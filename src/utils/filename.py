"""Safe filename generation."""

from __future__ import annotations

import re
import unicodedata


_INVALID_CHARS = re.compile(r'[<>:"/\\|?*\x00-\x1f]')
_WHITESPACE = re.compile(r"\s+")


def sanitize(text: str, max_length: int = 120) -> str:
    if not text:
        return "unknown"
    normalized = unicodedata.normalize("NFKD", text)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    cleaned = _INVALID_CHARS.sub("", ascii_text)
    cleaned = _WHITESPACE.sub("_", cleaned.strip())
    cleaned = cleaned.strip("._")
    if not cleaned:
        cleaned = "unknown"
    return cleaned[:max_length]


def build_filename(uploader: str, title: str, upload_date: str, ext: str) -> str:
    parts = [sanitize(uploader), sanitize(title)]
    if upload_date:
        parts.append(sanitize(upload_date))
    name = "_".join(p for p in parts if p)
    ext = ext.lstrip(".")
    return f"{name}.{ext}"
