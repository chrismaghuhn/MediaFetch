"""URL validation and metadata extraction."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from core.platform import Platform, detect_platform, is_supported_url

logger = logging.getLogger(__name__)


@dataclass
class VideoInfo:
    video_id: str
    platform: Platform
    title: str
    uploader: str
    upload_date: str
    url: str
    age_limit: int = 0
    is_playlist: bool = False
    collection_name: str = ""
    raw: dict | None = None


def map_error_to_key(exc: Exception) -> str:
    message = str(exc).lower()
    if "private" in message or "sign in" in message or "login" in message:
        return "error.private"
    if "geo" in message or "not available in your country" in message:
        return "error.geo_blocked"
    if "copyright" in message or "blocked" in message:
        return "error.copyright"
    if "network" in message or "urlopen error" in message or "timed out" in message:
        return "error.network"
    if "unavailable" in message or "video unavailable" in message:
        return "error.unavailable"
    if "ffmpeg" in message:
        return "error.ffmpeg"
    return "error.generic"


def _platform_from_extractor(extractor: str) -> Platform:
    extractor_lower = extractor.lower()
    if "youtube" in extractor_lower:
        return Platform.YOUTUBE
    if "instagram" in extractor_lower:
        return Platform.INSTAGRAM
    if "tiktok" in extractor_lower:
        return Platform.TIKTOK
    return Platform.UNKNOWN


def parse_video_info(url: str, info: dict[str, Any]) -> VideoInfo:
    extractor = info.get("extractor_key") or info.get("extractor") or ""
    platform = detect_platform(url)
    if platform == Platform.UNKNOWN:
        platform = _platform_from_extractor(str(extractor))

    entry_type = info.get("_type", "video")
    is_playlist = entry_type in ("playlist", "multi_video")
    collection_name = info.get("playlist_title") or info.get("channel") or info.get("uploader") or ""

    return VideoInfo(
        video_id=str(info.get("id", "")),
        platform=platform,
        title=str(info.get("title", "Unknown")),
        uploader=str(info.get("uploader") or info.get("channel") or "unknown"),
        upload_date=str(info.get("upload_date") or ""),
        url=url,
        age_limit=int(info.get("age_limit") or 0),
        is_playlist=is_playlist,
        collection_name=str(collection_name),
        raw=info,
    )


def validate_url(url: str) -> tuple[bool, str]:
    url = url.strip()
    if not url:
        return False, "url.invalid"
    if not is_supported_url(url):
        return False, "url.invalid"
    return True, ""
