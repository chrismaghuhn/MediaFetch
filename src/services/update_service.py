"""App and yt-dlp update checking."""

from __future__ import annotations

import logging
from pathlib import Path

import requests

from ui.dialogs.update_dialog import UpdateDialog
from utils.paths import ytdlp_exe_path
from utils.version import is_newer_version, parse_version

logger = logging.getLogger(__name__)

APP_VERSION = "1.0.0"
GITHUB_API = "https://api.github.com/repos/{repo}/releases/latest"
YTDLP_RELEASE = "https://api.github.com/repos/yt-dlp/yt-dlp/releases/latest"


class UpdateService:
    def __init__(self, github_repo: str) -> None:
        self._github_repo = github_repo

    def check_app_update(self) -> dict | None:
        try:
            url = GITHUB_API.format(repo=self._github_repo)
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            tag = data.get("tag_name", "")
            latest = tag.lstrip("v")
            if is_newer_version(APP_VERSION, latest):
                return {
                    "current": APP_VERSION,
                    "latest": latest,
                    "url": data.get("html_url", ""),
                    "body": data.get("body", ""),
                }
        except requests.RequestException as exc:
            logger.warning("App update check failed: %s", exc)
        return None

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

            exe_response = requests.get(download_url, timeout=60)
            exe_response.raise_for_status()

            if target_dir is None:
                from utils.paths import exe_dir
                target_dir = exe_dir() / "bin"
            target_dir.mkdir(parents=True, exist_ok=True)
            dest = target_dir / "yt-dlp.exe"
            dest.write_bytes(exe_response.content)
            return True
        except (requests.RequestException, OSError) as exc:
            logger.error("Failed to download yt-dlp: %s", exc)
            return False

    def check_and_notify(self, parent) -> None:
        app_update = self.check_app_update()
        if app_update:
            dialog = UpdateDialog(
                app_update["current"],
                app_update["latest"],
                app_update["url"],
                parent=parent,
            )
            dialog.exec()
            return

        ytdlp_update = self.check_ytdlp_update()
        if ytdlp_update:
            from PyQt6.QtWidgets import QMessageBox
            from ui.i18n.translator import tr

            reply = QMessageBox.question(
                parent,
                tr("dialog.update.ytdlp"),
                f"yt-dlp {ytdlp_update['latest']} ({tr('dialog.update.message', version=ytdlp_update['latest'], current=ytdlp_update['current'])})",
            )
            if reply == QMessageBox.StandardButton.Yes:
                if self.download_ytdlp_exe():
                    QMessageBox.information(parent, tr("app.title"), "yt-dlp updated.")
                else:
                    QMessageBox.warning(parent, tr("app.title"), tr("error.generic"))
