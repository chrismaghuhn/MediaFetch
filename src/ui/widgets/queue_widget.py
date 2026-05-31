"""Download queue widget."""

from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from core.queue_manager import QueueManager
from models.download_item import DownloadItem
from ui.i18n.translator import tr
from ui.widgets.progress_row import ProgressRow


class QueueWidget(QWidget):
    def __init__(self, queue_manager: QueueManager, parent=None) -> None:
        super().__init__(parent)
        self._queue = queue_manager
        self._rows: dict[str, ProgressRow] = {}
        self._build_ui()
        self._connect_signals()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)

        header = QHBoxLayout()
        header.addWidget(QLabel(tr("queue.title")))
        header.addStretch()

        self._start_btn = QPushButton(tr("queue.start"))
        self._pause_btn = QPushButton(tr("queue.pause"))
        self._pause_btn.setProperty("class", "secondary")
        self._clear_btn = QPushButton(tr("queue.clear"))
        self._clear_btn.setProperty("class", "secondary")

        header.addWidget(self._start_btn)
        header.addWidget(self._pause_btn)
        header.addWidget(self._clear_btn)
        layout.addLayout(header)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        self._container = QWidget()
        self._list_layout = QVBoxLayout(self._container)
        self._list_layout.addStretch()
        scroll.setWidget(self._container)
        layout.addWidget(scroll)

        self._empty_label = QLabel(tr("queue.empty"))
        self._empty_label.setProperty("class", "muted")
        self._empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._empty_label)

    def _connect_signals(self) -> None:
        self._queue.item_added.connect(self._on_item_added)
        self._queue.item_updated.connect(self._on_item_updated)
        self._queue.item_removed.connect(self._on_item_removed)
        self._queue.queue_cleared.connect(self._on_cleared)
        self._start_btn.clicked.connect(self._queue.start)
        self._pause_btn.clicked.connect(self._queue.pause)
        self._clear_btn.clicked.connect(self._queue.clear)

    def _on_item_added(self, item: DownloadItem) -> None:
        row = ProgressRow(item)
        row.remove_button.clicked.connect(lambda: self._queue.remove_item(item.url))
        self._rows[item.url] = row
        self._list_layout.insertWidget(self._list_layout.count() - 1, row)
        self._update_empty_state()

    def _on_item_updated(self, item: DownloadItem) -> None:
        row = self._rows.get(item.url)
        if row:
            row.update_item(item)

    def _on_item_removed(self, url: str) -> None:
        row = self._rows.pop(url, None)
        if row:
            row.deleteLater()
        self._update_empty_state()

    def _on_cleared(self) -> None:
        for row in self._rows.values():
            row.deleteLater()
        self._rows.clear()
        self._update_empty_state()

    def _update_empty_state(self) -> None:
        self._empty_label.setVisible(len(self._rows) == 0)

    def retranslate(self) -> None:
        self._start_btn.setText(tr("queue.start"))
        self._pause_btn.setText(tr("queue.pause"))
        self._clear_btn.setText(tr("queue.clear"))
        self._empty_label.setText(tr("queue.empty"))
