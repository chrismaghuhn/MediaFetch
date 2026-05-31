"""Tests for content filter helpers."""

from core.content_filter import build_match_filter
from core.format_selector import ContentFilter


def test_build_match_filter_all():
    assert build_match_filter(ContentFilter.ALL) is None


def test_build_match_filter_shorts():
    expr = build_match_filter(ContentFilter.SHORTS)
    assert expr is not None
    assert "YoutubeShorts" in expr


def test_build_match_filter_full():
    expr = build_match_filter(ContentFilter.FULL)
    assert expr is not None
    assert "YoutubeShorts" in expr
