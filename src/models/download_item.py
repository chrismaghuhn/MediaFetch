"""Download queue item model."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from core.format_selector import DownloadOptions
from core.platform import Platform
from core.validators import VideoInfo


class DownloadStatus(str, Enum):
    PENDING = "pending"
    VALIDATING = "validating"
    DOWNLOADING = "downloading"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class DownloadItem:
    url: str
    status: DownloadStatus = DownloadStatus.PENDING
    options: DownloadOptions = field(default_factory=DownloadOptions)
    video_info: VideoInfo | None = None
    platform: Platform = Platform.UNKNOWN
    title: str = ""
    progress_percent: float = 0.0
    speed: str = ""
    eta: str = ""
    error_key: str = ""
    retry_count: int = 0
    file_path: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "url": self.url,
            "status": self.status.value,
            "options": {
                "quality": self.options.quality,
                "audio_only": self.options.audio_only,
                "audio_format": self.options.audio_format,
                "include_subtitles": self.options.include_subtitles,
                "content_filter": self.options.content_filter.value,
            },
            "title": self.title,
            "progress_percent": self.progress_percent,
            "error_key": self.error_key,
            "retry_count": self.retry_count,
            "file_path": self.file_path,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> DownloadItem:
        from core.format_selector import ContentFilter

        opts_data = data.get("options", {})
        options = DownloadOptions(
            quality=opts_data.get("quality", 1080),
            audio_only=opts_data.get("audio_only", False),
            audio_format=opts_data.get("audio_format", "mp3"),
            include_subtitles=opts_data.get("include_subtitles", False),
            content_filter=ContentFilter(opts_data.get("content_filter", "all")),
        )
        status = DownloadStatus(data.get("status", "pending"))
        return cls(
            url=data["url"],
            status=status,
            options=options,
            title=data.get("title", ""),
            progress_percent=data.get("progress_percent", 0.0),
            error_key=data.get("error_key", ""),
            retry_count=data.get("retry_count", 0),
            file_path=data.get("file_path", ""),
        )
