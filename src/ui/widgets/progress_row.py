"""Single queue item progress row."""

from __future__ import annotations

from PyQt6.QtWidgets import QHBoxLayout, QLabel, QProgressBar, QPushButton, QVBoxLayout, QWidget

from models.download_item import DownloadItem, DownloadStatus
from ui.i18n.translator import tr


class ProgressRow(QWidget):
    def __init__(self, item: DownloadItem, parent=None) -> None:
        super().__init__(parent)
        self._item = item
        self._url = item.url
        self._build_ui()
        self.update_item(item)

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)

        top = QHBoxLayout()
        self._title = QLabel()
        self._title.setWordWrap(True)
        top.addWidget(self._title, stretch=1)

        self._remove_btn = QPushButton(tr("queue.remove"))
        self._remove_btn.setProperty("class", "secondary")
        top.addWidget(self._remove_btn)
        layout.addLayout(top)

        self._status = QLabel()
        self._status.setProperty("class", "muted")
        layout.addWidget(self._status)

        self._progress = QProgressBar()
        self._progress.setRange(0, 100)
        layout.addWidget(self._progress)

        self._details = QLabel()
        self._details.setProperty("class", "muted")
        layout.addWidget(self._details)

    @property
    def url(self) -> str:
        return self._url

    @property
    def remove_button(self) -> QPushButton:
        return self._remove_btn

    def update_item(self, item: DownloadItem) -> None:
        self._item = item
        title = item.title or item.url
        self._title.setText(title)

        status_key = f"queue.status.{item.status.value}"
        self._status.setText(tr(status_key))

        self._progress.setValue(int(item.progress_percent))

        if item.status == DownloadStatus.FAILED and item.error_key:
            self._details.setText(tr(item.error_key))
            self._details.setProperty("class", "error")
        elif item.status == DownloadStatus.DOWNLOADING:
            speed = tr("queue.progress.speed", speed=item.speed) if item.speed else ""
            eta = tr("queue.progress.eta", eta=item.eta) if item.eta else ""
            parts = [p for p in [speed, eta] if p]
            self._details.setText(" · ".join(parts))
            self._details.setProperty("class", "muted")
        else:
            self._details.setText("")
            self._details.setProperty("class", "muted")

        self._details.style().unpolish(self._details)
        self._details.style().polish(self._details)
