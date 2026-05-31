"""Output path and folder structure builder."""

from __future__ import annotations

from pathlib import Path

from core.platform import Platform
from utils.filename import sanitize


def platform_folder_name(platform: Platform) -> str:
    mapping = {
        Platform.YOUTUBE: "YouTube",
        Platform.INSTAGRAM: "Instagram",
        Platform.TIKTOK: "TikTok",
    }
    return mapping.get(platform, "Other")


def build_output_template(
    download_dir: str | Path,
    platform: Platform,
    uploader: str,
    *,
    is_collection: bool = False,
    collection_name: str = "",
) -> str:
    """Return yt-dlp outtmpl string for organized folder structure."""
    base = Path(download_dir) / platform_folder_name(platform)

    if is_collection and collection_name:
        folder = base / sanitize(collection_name)
    else:
        folder = base / sanitize(uploader or "unknown")

    folder.mkdir(parents=True, exist_ok=True)

    # yt-dlp template variables
    return str(folder / "%(uploader)s_%(title)s_%(upload_date)s.%(ext)s")
