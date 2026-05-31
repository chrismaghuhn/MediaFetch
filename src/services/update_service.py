"""App and yt-dlp update checking."""

from __future__ import annotations

import logging
from pathlib import Path

import requests

from core import updater
from models.settings import AppSettings
from services.settings_service import SettingsService
from ui.dialogs.update_dialog import UpdateDialog, UpdateDialogResult
from utils.paths import ytdlp_exe_path
from utils.version import is_newer_version
from version import __version__

logger = logging.getLogger(__name__)

YTDLP_RELEASE = "https://api.github.com/repos/yt-dlp/yt-dlp/releases/latest"


class UpdateService:
    def __init__(self, github_repo: str, settings: AppSettings | None = None) -> None:
        self._github_repo = github_repo
        self._settings = settings

    def check_app_update(self) -> updater.UpdateInfo | None:
        return updater.check_latest(self._github_repo, __version__)

    def check_ytdlp_update(self) -> dict | None:
        try:
            response = requests.get(YTDLP_RELEASE, timeout=10)
            response.raise_for_status()
            data = response.json()
            tag = data.get("tag_name", "").lstrip("v")

            current = self._current_ytdlp_version()
            if current and is_newer_version(current, tag):
                return {"current": current, "latest": tag, "url": data.get("html_url", "")}

            if not current and tag:
                return {"current": "unknown", "latest": tag, "url": data.get("html_url", "")}
        except requests.RequestException as exc:
            logger.warning("yt-dlp update check failed: %s", exc)
        return None

    def _current_ytdlp_version(self) -> str | None:
        try:
            import yt_dlp

            return yt_dlp.version.__version__
        except (ImportError, AttributeError):
            pass

        exe = ytdlp_exe_path()
        if exe:
            import subprocess

            result = subprocess.run([str(exe), "--version"], capture_output=True, text=True, check=False)
            if result.returncode == 0:
                return result.stdout.strip()
        return None

    def download_ytdlp_exe(self, target_dir: Path | None = None) -> bool:
        """Download latest yt-dlp.exe to bin folder."""
        try:
            response = requests.get(YTDLP_RELEASE, timeout=10)
            response.raise_for_status()
            data = response.json()

            download_url = None
            for asset in data.get("assets", []):
                if asset.get("name") == "yt-dlp.exe":
                    download_url = asset.get("browser_download_url")
                    break

            if not download_url:
                logger.error("yt-dlp.exe not found in release assets")
                return False

            if target_dir is None:
                from utils.paths import exe_dir

                target_dir = exe_dir() / "bin"
            dest = target_dir / "yt-dlp.exe"
            return updater.download_file(download_url, dest)
        except requests.RequestException as exc:
            logger.error("Failed to download yt-dlp: %s", exc)
            return False

    def download_installer(self, update: updater.UpdateInfo, dest: Path) -> bool:
        if not update.installer_url:
            return False
        return updater.download_file(
            update.installer_url,
            dest,
            expected_sha256=update.installer_sha256 or None,
        )

    def check_and_notify(
        self,
        parent,
        settings: AppSettings | None = None,
        settings_service: SettingsService | None = None,
    ) -> None:
        settings = settings or self._settings
        app_update = self.check_app_update()
        if app_update:
            if settings and not updater.should_notify(app_update, settings):
                return

            dialog = UpdateDialog(app_update, parent=parent)
            result = dialog.exec()

            if settings:
                if result == UpdateDialogResult.SKIP_VERSION:
                    settings.skipped_version = app_update.latest
                elif result == UpdateDialogResult.REMIND_LATER:
                    settings.remind_update_after = updater.remind_later_days(7)
                if settings_service:
                    settings_service.save()
            return

        ytdlp_update = self.check_ytdlp_update()
        if ytdlp_update:
            from PyQt6.QtWidgets import QMessageBox

            from ui.i18n.translator import tr

            reply = QMessageBox.question(
                parent,
                tr("dialog.update.ytdlp"),
                tr(
                    "dialog.update.message",
                    version=ytdlp_update["latest"],
                    current=ytdlp_update["current"],
                ),
            )
            if reply == QMessageBox.StandardButton.Yes:
                if self.download_ytdlp_exe():
                    QMessageBox.information(parent, tr("app.title"), tr("dialog.update.ytdlp_done"))
                else:
                    QMessageBox.warning(parent, tr("app.title"), tr("error.generic"))
