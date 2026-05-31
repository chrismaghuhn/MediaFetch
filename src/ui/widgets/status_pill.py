"""Status badge for queue/history rows."""

from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel

from models.download_item import DownloadStatus
from ui.i18n.translator import tr


class StatusPill(QLabel):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("StatusPill")
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._status = DownloadStatus.PENDING
        self._tokens: dict[str, str] = {}

    def set_tokens(self, tokens: dict[str, str]) -> None:
        self._tokens = tokens
        if self._status:
            self.set_status(self._status)

    def set_status(self, status: DownloadStatus) -> None:
        self._status = status
        key = f"queue.status.{status.value}"
        self.setText(tr(key))
        bg, fg = self._colors_for_status(status)
        self.setStyleSheet(
            f"background-color: {bg}; color: {fg}; border-radius: 999px; "
            f"padding: 4px 10px; font-size: 12px; font-weight: 600;"
        )

    def _colors_for_status(self, status: DownloadStatus) -> tuple[str, str]:
        t = self._tokens
        if status in (DownloadStatus.DOWNLOADING, DownloadStatus.VALIDATING):
            return t.get("accentSoft", "#ffe7e0"), t.get("accentSoftText", "#d63d22")
        if status == DownloadStatus.COMPLETED:
            return t.get("successSoft", "#e2f6ea"), t.get("success", "#1f9d57")
        if status == DownloadStatus.FAILED:
            return t.get("dangerSoft", "#fce9eb"), t.get("danger", "#dc3a4b")
        if status == DownloadStatus.SKIPPED:
            return t.get("surface2", "#f6ede2"), t.get("textFaint", "#a99a8a")
        return t.get("surface2", "#f6ede2"), t.get("textMuted", "#7d6e5f")
