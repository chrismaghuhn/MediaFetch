"""Tests for core updater module."""

from unittest.mock import MagicMock

import pytest

from core import updater
from models.settings import AppSettings


def test_check_latest_newer_version():
    session = MagicMock()
    session.get.return_value.json.return_value = {
        "tag_name": "v2.0.0",
        "html_url": "https://github.com/org/repo/releases/tag/v2.0.0",
        "body": "Changelog",
        "assets": [{"name": "MediaFetch-2.0.0-Setup.exe", "browser_download_url": "https://x/setup.exe"}],
    }
    session.get.return_value.raise_for_status = MagicMock()

    info = updater.check_latest("org/repo", "1.0.0", session=session)
    assert info is not None
    assert info.latest == "2.0.0"
    assert info.installer_url.endswith("setup.exe")


def test_check_latest_no_update():
    session = MagicMock()
    session.get.return_value.json.return_value = {"tag_name": "v1.0.0", "html_url": "", "body": "", "assets": []}
    session.get.return_value.raise_for_status = MagicMock()

    assert updater.check_latest("org/repo", "1.0.0", session=session) is None


def test_should_notify_skipped_version():
    update = updater.UpdateInfo("1.0.0", "2.0.0", "url", "body")
    settings = AppSettings(skipped_version="2.0.0")
    assert updater.should_notify(update, settings) is False


def test_should_notify_remind_later():
    update = updater.UpdateInfo("1.0.0", "2.0.0", "url", "body")
    settings = AppSettings(remind_update_after="2099-12-31")
    assert updater.should_notify(update, settings) is False


def test_parse_release_assets_sha_from_body():
    data = {
        "assets": [{"name": "MediaFetch-1.1.0-Setup.exe", "browser_download_url": "https://x/setup.exe"}],
        "body": "SHA256: abc123def\nOther notes",
    }
    url, sha = updater.parse_release_assets(data)
    assert url == "https://x/setup.exe"
    assert sha == "abc123def"


def test_download_file_verifies_sha256(tmp_path):
    content = b"test-installer"
    import hashlib

    sha = hashlib.sha256(content).hexdigest()

    session = MagicMock()
    response = MagicMock()
    response.headers = {"Content-Length": str(len(content))}
    response.iter_content = lambda chunk_size: [content]
    response.raise_for_status = MagicMock()
    session.get.return_value.__enter__ = MagicMock(return_value=response)
    session.get.return_value.__exit__ = MagicMock(return_value=False)

    dest = tmp_path / "setup.exe"
    assert updater.download_file("http://example.com/setup.exe", dest, expected_sha256=sha, session=session)
    assert dest.read_bytes() == content


def test_download_file_sha_mismatch(tmp_path):
    session = MagicMock()
    response = MagicMock()
    response.headers = {}
    response.iter_content = lambda chunk_size: [b"bad"]
    response.raise_for_status = MagicMock()
    session.get.return_value.__enter__ = MagicMock(return_value=response)
    session.get.return_value.__exit__ = MagicMock(return_value=False)

    dest = tmp_path / "setup.exe"
    assert not updater.download_file("http://x", dest, expected_sha256="00" * 32, session=session)
    assert not dest.exists()
