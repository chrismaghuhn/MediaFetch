"""Tests for platform detection."""

import pytest

from core.platform import Platform, detect_platform, is_supported_url


@pytest.mark.parametrize("url,expected", [
    ("https://www.youtube.com/watch?v=abc", Platform.YOUTUBE),
    ("https://youtu.be/abc", Platform.YOUTUBE),
    ("https://www.instagram.com/reel/abc/", Platform.INSTAGRAM),
    ("https://www.tiktok.com/@user/video/123", Platform.TIKTOK),
    ("https://example.com/video", Platform.UNKNOWN),
])
def test_detect_platform(url, expected):
    assert detect_platform(url) == expected


def test_is_supported_url():
    assert is_supported_url("https://youtube.com/watch?v=x")
    assert not is_supported_url("https://example.com")
