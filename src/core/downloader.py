"""yt-dlp download wrapper with progress hooks."""

from __future__ import annotations

import logging
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

from core.content_filter import build_match_filter
from core.format_selector import DownloadOptions, build_format_string
from core.path_builder import build_output_template
from core.platform import Platform
from core.validators import VideoInfo, map_error_to_key, parse_video_info
from utils.paths import ffmpeg_path, ytdlp_exe_path

logger = logging.getLogger(__name__)

ProgressCallback = Callable[[dict[str, Any]], None]


class Downloader:
    def __init__(self, download_dir: str) -> None:
        self._download_dir = download_dir
        self._use_subprocess = False
        self._ytdlp = None
        self._init_ytdlp()

    def _init_ytdlp(self) -> None:
        try:
            import yt_dlp  # noqa: F401

            self._use_subprocess = False
        except ImportError:
            if ytdlp_exe_path():
                self._use_subprocess = True
                logger.warning("yt-dlp Python module unavailable, using subprocess fallback")
            else:
                raise RuntimeError("yt-dlp is not available")

    def extract_info(self, url: str, download: bool = False) -> VideoInfo:
        if self._use_subprocess:
            return self._extract_info_subprocess(url)
        return self._extract_info_api(url, download=download)

    def _extract_info_api(self, url: str, download: bool = False) -> VideoInfo:
        import yt_dlp

        opts: dict[str, Any] = {
            "quiet": True,
            "no_warnings": True,
            "skip_download": not download,
        }
        ff = ffmpeg_path()
        if ff:
            opts["ffmpeg_location"] = str(ff.parent)

        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=download)
            if info is None:
                raise ValueError("Could not extract video information")
            if info.get("_type") == "playlist" and info.get("entries"):
                first = next(e for e in info["entries"] if e)
                return parse_video_info(url, first)
            return parse_video_info(url, info)

    def _extract_info_subprocess(self, url: str) -> VideoInfo:
        exe = ytdlp_exe_path()
        if not exe:
            raise RuntimeError("yt-dlp executable not found")

        cmd = [str(exe), "--dump-json", "--no-download", url]
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if result.returncode != 0:
            raise RuntimeError(result.stderr or result.stdout)

        import json

        info = json.loads(result.stdout.strip().split("\n")[0])
        return parse_video_info(url, info)

    def download(
        self,
        url: str,
        options: DownloadOptions,
        video_info: VideoInfo | None = None,
        on_progress: ProgressCallback | None = None,
    ) -> VideoInfo:
        if self._use_subprocess:
            return self._download_subprocess(url, options, on_progress)
        return self._download_api(url, options, video_info, on_progress)

    def _build_ydl_opts(
        self,
        options: DownloadOptions,
        video_info: VideoInfo | None,
        on_progress: ProgressCallback | None,
    ) -> dict[str, Any]:
        platform = video_info.platform if video_info else Platform.UNKNOWN
        uploader = video_info.uploader if video_info else "unknown"
        is_collection = video_info.is_playlist if video_info else False
        collection_name = video_info.collection_name if video_info else ""

        outtmpl = build_output_template(
            self._download_dir,
            platform,
            uploader,
            is_collection=is_collection,
            collection_name=collection_name,
        )

        ydl_opts: dict[str, Any] = {
            "format": build_format_string(options),
            "outtmpl": outtmpl,
            "quiet": True,
            "no_warnings": True,
            "retries": 3,
            "ignoreerrors": False,
        }

        ff = ffmpeg_path()
        if ff:
            ydl_opts["ffmpeg_location"] = str(ff.parent)

        match_filter = build_match_filter(options.content_filter)
        if match_filter:
            ydl_opts["match_filter"] = match_filter

        if options.include_subtitles:
            ydl_opts.update({
                "writesubtitles": True,
                "writeautomaticsub": True,
                "subtitleslangs": ["de", "en"],
                "embedsubtitles": True,
            })

        if options.audio_only:
            ydl_opts.update({
                "format": "bestaudio/best",
                "postprocessors": [{
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": options.audio_format,
                    "preferredquality": "192",
                }],
            })

        if on_progress:
            ydl_opts["progress_hooks"] = [on_progress]

        return ydl_opts

    def _download_api(
        self,
        url: str,
        options: DownloadOptions,
        video_info: VideoInfo | None,
        on_progress: ProgressCallback | None,
    ) -> VideoInfo:
        import yt_dlp

        ydl_opts = self._build_ydl_opts(options, video_info, on_progress)

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                if info is None:
                    raise ValueError("Download returned no info")
                if info.get("_type") == "playlist":
                    entries = [e for e in info.get("entries", []) if e]
                    if entries:
                        return parse_video_info(url, entries[-1])
                return parse_video_info(url, info)
        except Exception as exc:
            logger.exception("Download failed for %s", url)
            key = map_error_to_key(exc)
            raise RuntimeError(key) from exc

    def _download_subprocess(
        self,
        url: str,
        options: DownloadOptions,
        on_progress: ProgressCallback | None,
    ) -> VideoInfo:
        exe = ytdlp_exe_path()
        if not exe:
            raise RuntimeError("yt-dlp executable not found")

        info = self.extract_info(url)
        outtmpl = build_output_template(
            self._download_dir,
            info.platform,
            info.uploader,
            is_collection=info.is_playlist,
            collection_name=info.collection_name,
        )

        cmd = [
            str(exe),
            "-f", build_format_string(options),
            "-o", outtmpl,
            url,
        ]
        if options.audio_only:
            cmd.extend(["-x", "--audio-format", options.audio_format])

        ff = ffmpeg_path()
        if ff:
            cmd.extend(["--ffmpeg-location", str(ff.parent)])

        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if result.returncode != 0:
            raise RuntimeError(map_error_to_key(RuntimeError(result.stderr)))

        if on_progress:
            on_progress({"status": "finished", "downloaded_bytes": 0, "total_bytes": 0})

        return info
