"""Format and quality selection for yt-dlp."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Literal


class ContentFilter(str, Enum):
    ALL = "all"
    SHORTS = "shorts"
    FULL = "full"


AudioFormat = Literal["mp3", "m4a"]


@dataclass
class DownloadOptions:
    quality: int = 1080
    audio_only: bool = False
    audio_format: AudioFormat = "mp3"
    include_subtitles: bool = False
    content_filter: ContentFilter = ContentFilter.ALL


def build_format_string(options: DownloadOptions) -> str:
    if options.audio_only:
        return "bestaudio/best"

    height = options.quality
    return (
        f"bestvideo[height<={height}]+bestaudio/best[height<={height}]/best"
    )
