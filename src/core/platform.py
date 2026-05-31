"""Platform detection from URLs."""

from __future__ import annotations

import re
from enum import Enum


class Platform(str, Enum):
    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    UNKNOWN = "unknown"

    @property
    def display_key(self) -> str:
        return f"platform.{self.value}"


_YOUTUBE = re.compile(
    r"(https?://)?(www\.)?(youtube\.com|youtu\.be)/",
    re.IGNORECASE,
)
_INSTAGRAM = re.compile(
    r"(https?://)?(www\.)?instagram\.com/",
    re.IGNORECASE,
)
_TIKTOK = re.compile(
    r"(https?://)?(www\.)?(tiktok\.com|vm\.tiktok\.com)/",
    re.IGNORECASE,
)


def detect_platform(url: str) -> Platform:
    url = url.strip()
    if _YOUTUBE.search(url):
        return Platform.YOUTUBE
    if _INSTAGRAM.search(url):
        return Platform.INSTAGRAM
    if _TIKTOK.search(url):
        return Platform.TIKTOK
    return Platform.UNKNOWN


def is_supported_url(url: str) -> bool:
    return detect_platform(url) != Platform.UNKNOWN
