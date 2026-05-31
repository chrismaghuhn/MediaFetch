"""Tests for URL validation and metadata parsing."""

import pytest

from core.platform import Platform
from core.validators import map_error_to_key, parse_video_info, validate_url


@pytest.mark.parametrize(
    "url,valid",
    [
        ("https://www.youtube.com/watch?v=abc123", True),
        ("https://youtu.be/abc123", True),
        ("https://www.youtube.com/playlist?list=PLxyz", True),
        ("https://www.youtube.com/@channelname", True),
        ("https://www.instagram.com/reel/ABC/", True),
        ("https://www.instagram.com/p/ABC/", True),
        ("https://www.tiktok.com/@user/video/123", True),
        ("https://vm.tiktok.com/abc/", True),
        ("", False),
        ("https://example.com/video", False),
        ("not-a-url", False),
    ],
)
def test_validate_url(url, valid):
    ok, key = validate_url(url)
    assert ok is valid
    if not valid:
        assert key == "url.invalid"


def test_parse_video_info(mock_ytdlp_info, sample_urls):
    info = parse_video_info(sample_urls["youtube_video"], mock_ytdlp_info)
    assert info.video_id == "dQw4w9WgXcQ"
    assert info.platform == Platform.YOUTUBE
    assert info.title == "Test Video Title"
    assert info.uploader == "TestChannel"


def test_parse_video_info_playlist(sample_urls):
    raw = {
        "id": "PL123",
        "title": "My Playlist",
        "uploader": "Creator",
        "_type": "playlist",
        "playlist_title": "My Playlist",
    }
    info = parse_video_info(sample_urls["youtube_playlist"], raw)
    assert info.is_playlist is True
    assert info.collection_name == "My Playlist"


@pytest.mark.parametrize(
    "message,expected",
    [
        ("Video private sign in required", "error.private"),
        ("Geo restricted not available in your country", "error.geo_blocked"),
        ("copyright blocked", "error.copyright"),
        ("network urlopen error timed out", "error.network"),
        ("video unavailable", "error.unavailable"),
        ("ffmpeg not found", "error.ffmpeg"),
        ("something else", "error.generic"),
    ],
)
def test_map_error_to_key(message, expected):
    assert map_error_to_key(Exception(message)) == expected
