"""Shared pytest fixtures."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
FIXTURES = Path(__file__).resolve().parent / "fixtures"

sys.path.insert(0, str(SRC))


@pytest.fixture
def tmp_download_dir(tmp_path, monkeypatch):
    download_dir = tmp_path / "downloads"
    download_dir.mkdir()
    monkeypatch.setattr("utils.paths.default_download_dir", lambda: download_dir)
    return download_dir


@pytest.fixture
def tmp_app_data(tmp_path, monkeypatch):
    app_data = tmp_path / "MediaFetch"
    app_data.mkdir()
    monkeypatch.setattr("utils.paths.app_data_dir", lambda: app_data)
    monkeypatch.setattr("utils.paths.settings_path", lambda: app_data / "settings.json")
    monkeypatch.setattr("utils.paths.queue_path", lambda: app_data / "queue.json")
    monkeypatch.setattr("utils.paths.history_db_path", lambda: app_data / "history.db")
    monkeypatch.setattr("utils.paths.default_log_dir", lambda: app_data / "logs")
    return app_data


@pytest.fixture
def settings_service(tmp_app_data):
    from services.settings_service import SettingsService

    return SettingsService()


@pytest.fixture
def sample_youtube_info():
    path = FIXTURES / "youtube_video.json"
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.fixture
def sample_urls():
    return {
        "youtube_video": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "youtube_playlist": "https://www.youtube.com/playlist?list=PLexample",
        "youtube_channel": "https://www.youtube.com/@example",
        "instagram_reel": "https://www.instagram.com/reel/ABC123/",
        "tiktok_video": "https://www.tiktok.com/@user/video/1234567890",
        "invalid": "https://example.com/not-a-video",
    }


@pytest.fixture
def mock_ytdlp_info(sample_youtube_info):
    return sample_youtube_info
