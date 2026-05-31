"""Tests for application path helpers."""

from pathlib import Path

import pytest

from utils import paths


def test_is_frozen_false():
    assert paths.is_frozen() is False


def test_app_data_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("APPDATA", str(tmp_path))
    data = paths.app_data_dir()
    assert data == tmp_path / "MediaFetch"
    assert data.is_dir()


def test_default_download_dir(monkeypatch, tmp_path):
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    dl = paths.default_download_dir()
    assert dl.name == "MediaFetch"
    assert dl.is_dir()


def test_i18n_dir_exists():
    d = paths.i18n_dir()
    assert d.is_dir()
    assert (d / "de.json").is_file()


def test_settings_and_queue_paths(tmp_app_data):
    assert paths.settings_path().name == "settings.json"
    assert paths.queue_path().name == "queue.json"
    assert paths.history_db_path().name == "history.db"
