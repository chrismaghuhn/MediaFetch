"""Tests for update service facade."""

from unittest.mock import MagicMock, patch

from core.updater import UpdateInfo
from services.update_service import UpdateService


def test_check_app_update_delegates():
    service = UpdateService("org/repo")
    info = UpdateInfo("1.0.0", "2.0.0", "url", "body")
    with patch("services.update_service.updater.check_latest", return_value=info) as mock_check:
        result = service.check_app_update()
    mock_check.assert_called_once()
    assert result.latest == "2.0.0"


def test_check_ytdlp_update_newer():
    service = UpdateService("org/repo")
    with patch.object(service, "_current_ytdlp_version", return_value="2024.01.01"):
        with patch("requests.get") as mock_get:
            mock_get.return_value.json.return_value = {
                "tag_name": "2025.01.01",
                "html_url": "https://github.com/yt-dlp/yt-dlp/releases",
            }
            mock_get.return_value.raise_for_status = MagicMock()
            result = service.check_ytdlp_update()
    assert result is not None
    assert result["latest"] == "2025.01.01"


def test_download_ytdlp_exe_success(tmp_path):
    service = UpdateService("org/repo")
    with patch("requests.get") as mock_get:
        release = MagicMock()
        release.json.return_value = {
            "assets": [{"name": "yt-dlp.exe", "browser_download_url": "http://x/yt-dlp.exe"}],
        }
        release.raise_for_status = MagicMock()
        exe = MagicMock()
        exe.content = b"binary"
        exe.raise_for_status = MagicMock()
        mock_get.side_effect = [release, exe]
        assert service.download_ytdlp_exe(tmp_path) is True
        assert (tmp_path / "yt-dlp.exe").exists()
