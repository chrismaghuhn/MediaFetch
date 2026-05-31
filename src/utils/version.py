"""Version comparison without external dependencies."""

from __future__ import annotations

import re


def parse_version(version_str: str) -> tuple[int, ...]:
    """Parse '1.2.3' or 'v1.2.3-beta' into a comparable tuple."""
    cleaned = version_str.strip().lstrip("vV")
    match = re.match(r"(\d+(?:\.\d+)*)", cleaned)
    if not match:
        return (0,)
    parts = match.group(1).split(".")
    return tuple(int(p) for p in parts)


def is_newer_version(current: str, latest: str) -> bool:
    return parse_version(latest) > parse_version(current)
