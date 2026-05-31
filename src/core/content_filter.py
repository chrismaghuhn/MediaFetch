"""Content type filters — fragile, depends on yt-dlp extractors."""

from __future__ import annotations

import logging

from core.format_selector import ContentFilter

logger = logging.getLogger(__name__)


def build_match_filter(content_filter: ContentFilter) -> str | None:
    """Build yt-dlp match_filter expression.

    YouTube Shorts via extractor_key is preferred over duration heuristics.
    This may break when yt-dlp changes extractor behavior.
    """
    if content_filter == ContentFilter.ALL:
        return None

    if content_filter == ContentFilter.SHORTS:
        return "extractor_key = 'YoutubeShorts' | extractor_key = 'InstagramReel'"

    if content_filter == ContentFilter.FULL:
        return "extractor_key != 'YoutubeShorts' & extractor_key != 'InstagramReel'"

    return None
