"""Single queue item progress row — Studio layout."""

from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel, QProgressBar, QVBoxLayout

from core.platform import Platform
from models.download_item import DownloadItem, DownloadStatus
from ui.i18n.translator import tr
from ui.widgets.styled_button import styled_button
from ui.widgets.status_pill import StatusPill

PLATFORM_LABELS = {
    Platform.YOUTUBE: ("Y", "#ff0000"),
    Platform.INSTAGRAM: ("I", "#e1306c"),
    Platform.TIKTOK: ("T", "#010101"),
    Platform.UNKNOWN: ("?", "#888888"),
}


class ProgressRow(QFrame):
    def __init__(self, item: DownloadItem, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("QueueRow")
        self._item = item
        self._url = item.url
        self._build_ui()
        self.update_item(item)

    def _build_ui(self) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 11, 12, 11)
        layout.setSpacing(12)

        self._platform_badge = QLabel("?")
        self._platform_badge.setObjectName("PlatformBadge")
        self._platform_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._platform_badge)

        center = QVBoxLayout()
        center.setSpacing(4)
        self._title = QLabel()
        self._title.setWordWrap(False)
        font = self._title.font()
        font.setWeight(600)
        self._title.setFont(font)
        center.addWidget(self._title)

        progress_row = QHBoxLayout()
        progress_row.setSpacing(8)
        self._progress = QProgressBar()
        self._progress.setRange(0, 100)
        self._progress.setTextVisible(False)
        progress_row.addWidget(self._progress, stretch=1)

        self._percent = QLabel("0%")
        self._percent.setProperty("mono", "true")
        self._percent.setFixedWidth(40)
        progress_row.addWidget(self._percent)
        center.addLayout(progress_row)

        self._details = QLabel()
        self._details.setProperty("mono", "true")
        self._details.setProperty("class", "muted")
        center.addWidget(self._details)
        layout.addLayout(center, stretch=1)

        right = QVBoxLayout()
        right.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self._status_pill = StatusPill()
        right.addWidget(self._status_pill, alignment=Qt.AlignmentFlag.AlignRight)

        self._remove_btn = styled_button("×", variant="danger")
        self._remove_btn.setFixedSize(32, 32)
        right.addWidget(self._remove_btn, alignment=Qt.AlignmentFlag.AlignRight)
        layout.addLayout(right)

    @property
    def url(self) -> str:
        return self._url

    @property
    def remove_button(self):
        return self._remove_btn

    def refresh_theme(self, tokens: dict[str, str], *, accent_only: bool = False) -> None:
        self._status_pill.set_tokens(tokens)
        self._progress.style().unpolish(self._progress)
        self._progress.style().polish(self._progress)
        if accent_only:
            return
        if self._item:
            self.update_item(self._item)

    def _set_platform_badge(self, platform: Platform) -> None:
        letter, color = PLATFORM_LABELS.get(platform, PLATFORM_LABELS[Platform.UNKNOWN])
        self._platform_badge.setText(letter)
        self._platform_badge.setStyleSheet(
            f"background-color: {color}; color: white; border-radius: 8px;"
        )

    def update_item(self, item: DownloadItem) -> None:
        self._item = item
        title = item.title or item.url
        if len(title) > 60:
            title = title[:57] + "..."
        self._title.setText(title)
        self._set_platform_badge(item.platform)

        self._status_pill.set_status(item.status)
        self._progress.setValue(int(item.progress_percent))
        self._percent.setText(f"{int(item.progress_percent)}%")

        if item.status == DownloadStatus.COMPLETED:
            self._progress.setProperty("status", "completed")
        elif item.status == DownloadStatus.FAILED:
            self._progress.setProperty("status", "failed")
        else:
            self._progress.setProperty("status", "downloading")
        self._progress.style().unpolish(self._progress)
        self._progress.style().polish(self._progress)

        if item.status == DownloadStatus.FAILED and item.error_key:
            self._details.setText(tr(item.error_key))
            self._details.setProperty("class", "error")
        elif item.status == DownloadStatus.DOWNLOADING:
            speed = tr("queue.progress.speed", speed=item.speed) if item.speed else ""
            eta = tr("queue.progress.eta", eta=item.eta) if item.eta else ""
            parts = [p for p in [speed, eta] if p]
            self._details.setText(" · ".join(parts))
            self._details.setProperty("class", "muted")
        elif item.status == DownloadStatus.COMPLETED:
            self._details.setText("")
        else:
            self._details.setText("")
            self._details.setProperty("class", "muted")

        self._details.setVisible(bool(self._details.text()))
        self._progress.setVisible(
            item.status in (DownloadStatus.DOWNLOADING, DownloadStatus.COMPLETED, DownloadStatus.FAILED)
        )
        self._percent.setVisible(self._progress.isVisible())

    def retranslate(self) -> None:
        if self._item:
            self.update_item(self._item)
