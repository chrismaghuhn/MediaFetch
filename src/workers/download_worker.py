"""QThread worker for a single download."""

from __future__ import annotations

import logging
from typing import Any

from PyQt6.QtCore import QThread, pyqtSignal

from core.downloader import Downloader
from core.format_selector import DownloadOptions
from core.validators import VideoInfo
from models.download_item import DownloadItem

logger = logging.getLogger(__name__)


class DownloadWorker(QThread):
    progress = pyqtSignal(str, float, str, str)  # url, percent, speed, eta
    completed = pyqtSignal(str, object)  # url, VideoInfo
    failed = pyqtSignal(str, str)  # url, error_key

    def __init__(
        self,
        item: DownloadItem,
        download_dir: str,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self._item = item
        self._download_dir = download_dir
        self._video_info: VideoInfo | None = item.video_info

    @property
    def url(self) -> str:
        return self._item.url

    def run(self) -> None:
        downloader = Downloader(self._download_dir)

        def on_progress(d: dict[str, Any]) -> None:
            status = d.get("status")
            if status == "downloading":
                total = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
                downloaded = d.get("downloaded_bytes") or 0
                percent = (downloaded / total * 100) if total else 0.0
                speed = d.get("_speed_str") or self._format_speed(d.get("speed"))
                eta = d.get("_eta_str") or self._format_eta(d.get("eta"))
                self.progress.emit(self._item.url, percent, speed, eta)
            elif status == "finished":
                self.progress.emit(self._item.url, 100.0, "", "")

        try:
            if not self._video_info:
                self._video_info = downloader.extract_info(self._item.url)

            result = downloader.download(
                self._item.url,
                self._item.options,
                video_info=self._video_info,
                on_progress=on_progress,
            )
            self.completed.emit(self._item.url, result)
        except Exception as exc:
            logger.exception("Worker failed for %s", self._item.url)
            error_key = str(exc) if str(exc).startswith("error.") else "error.generic"
            self.failed.emit(self._item.url, error_key)

    @staticmethod
    def _format_speed(speed: float | None) -> str:
        if not speed:
            return ""
        if speed > 1_000_000:
            return f"{speed / 1_000_000:.1f} MB"
        if speed > 1_000:
            return f"{speed / 1_000:.1f} KB"
        return f"{speed:.0f} B"

    @staticmethod
    def _format_eta(eta: int | None) -> str:
        if eta is None or eta < 0:
            return ""
        minutes, seconds = divmod(int(eta), 60)
        if minutes >= 60:
            hours, minutes = divmod(minutes, 60)
            return f"{hours}:{minutes:02d}:{seconds:02d}"
        return f"{minutes}:{seconds:02d}"
