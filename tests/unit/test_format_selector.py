"""Tests for format selector."""

from core.format_selector import ContentFilter, DownloadOptions, build_format_string


def test_build_format_string_video():
    opts = DownloadOptions(quality=720)
    fmt = build_format_string(opts)
    assert "720" in fmt


def test_build_format_string_audio():
    opts = DownloadOptions(audio_only=True)
    assert build_format_string(opts) == "bestaudio/best"


def test_content_filter_enum():
    assert ContentFilter.SHORTS.value == "shorts"
