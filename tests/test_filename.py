"""Tests for filename sanitization."""

import pytest

from utils.filename import build_filename, sanitize


def test_sanitize_removes_invalid_chars():
    assert sanitize('Test: "Video" <name>') == "Test_Video_name"


def test_sanitize_empty():
    assert sanitize("") == "unknown"


def test_build_filename():
    name = build_filename("Creator", "My Video", "20240101", "mp4")
    assert name == "Creator_My_Video_20240101.mp4"
