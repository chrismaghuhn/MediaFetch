"""Download history widget — Studio panel layout."""

from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QHeaderView,
    QLineEdit,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from services.history_service import HistoryService
from ui.i18n.translator import tr
from ui.widgets.page_head import PageHead
from ui.widgets.panel import Panel
from ui.widgets.styled_button import styled_button


class HistoryWidget(QWidget):
    def __init__(self, history_service: HistoryService, parent=None) -> None:
        super().__init__(parent)
        self._history = history_service
        self._build_ui()
        self.refresh()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        panel = Panel()
        self._head = PageHead(tr("history.title"), tr("history.subtitle"))
        panel.content_layout.addWidget(self._head)

        filters = QHBoxLayout()
        filters.setSpacing(8)
        self._search = QLineEdit()
        self._search.setPlaceholderText(tr("history.search"))
        self._search.setMaximumWidth(320)
        filters.addWidget(self._search)

        self._platform_filter = QComboBox()
        self._platform_filter.addItem(tr("history.filter.all"), "all")
        self._platform_filter.addItem(tr("platform.youtube"), "youtube")
        self._platform_filter.addItem(tr("platform.instagram"), "instagram")
        self._platform_filter.addItem(tr("platform.tiktok"), "tiktok")
        filters.addWidget(self._platform_filter)

        self._status_filter = QComboBox()
        self._status_filter.addItem(tr("history.filter.all"), "all")
        self._status_filter.addItem(tr("history.status.success"), "success")
        self._status_filter.addItem(tr("history.status.failed"), "failed")
        filters.addWidget(self._status_filter)

        self._refresh_btn = styled_button(tr("history.search"), variant="secondary")
        self._refresh_btn.clicked.connect(self.refresh)
        filters.addWidget(self._refresh_btn)
        filters.addStretch()
        panel.content_layout.addLayout(filters)

        self._table = QTableWidget(0, 6)
        self._table.setHorizontalHeaderLabels([
            tr("history.col.date"),
            tr("history.col.platform"),
            tr("history.col.title"),
            tr("history.col.uploader"),
            tr("history.col.status"),
            tr("history.col.path"),
        ])
        self._table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self._table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)
        self._table.setAlternatingRowColors(True)
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.verticalHeader().setVisible(False)
        self._table.setShowGrid(False)
        panel.content_layout.addWidget(self._table)

        layout.addWidget(panel)

    def refresh(self) -> None:
        entries = self._history.search(
            query=self._search.text(),
            platform=self._platform_filter.currentData(),
            status=self._status_filter.currentData(),
        )
        self._table.setRowCount(0)
        for entry in entries:
            row = self._table.rowCount()
            self._table.insertRow(row)
            self._table.setRowHeight(row, 48)
            status_text = (
                tr(f"history.status.{entry.status}")
                if entry.status in ("success", "failed")
                else entry.status
            )
            platform_text = (
                tr(f"platform.{entry.platform}") if entry.platform else entry.platform
            )
            values = [
                entry.downloaded_at[:19] if entry.downloaded_at else "",
                platform_text,
                entry.title,
                entry.uploader,
                status_text,
                entry.file_path,
            ]
            for col, value in enumerate(values):
                item = QTableWidgetItem(value)
                item.setToolTip(value)
                if col in (0, 5):
                    item.setData(Qt.ItemDataRole.UserRole, "mono")
                self._table.setItem(row, col, item)

        if self._table.rowCount() == 0:
            self._table.setRowCount(1)
            self._table.setRowHeight(0, 48)
            empty = QTableWidgetItem(tr("history.empty"))
            empty.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self._table.setItem(0, 0, empty)
            self._table.setSpan(0, 0, 1, 6)

    def retranslate(self) -> None:
        self._head.set_title(tr("history.title"))
        self._head.set_subtitle(tr("history.subtitle"))
        self._search.setPlaceholderText(tr("history.search"))
        self._refresh_btn.setText(tr("history.search"))
        self._retranslate_filter_combo(
            self._platform_filter,
            [
                ("history.filter.all", "all"),
                ("platform.youtube", "youtube"),
                ("platform.instagram", "instagram"),
                ("platform.tiktok", "tiktok"),
            ],
        )
        self._retranslate_filter_combo(
            self._status_filter,
            [
                ("history.filter.all", "all"),
                ("history.status.success", "success"),
                ("history.status.failed", "failed"),
            ],
        )
        self._table.setHorizontalHeaderLabels([
            tr("history.col.date"),
            tr("history.col.platform"),
            tr("history.col.title"),
            tr("history.col.uploader"),
            tr("history.col.status"),
            tr("history.col.path"),
        ])
        self.refresh()

    def _retranslate_filter_combo(
        self,
        combo: QComboBox,
        items: list[tuple[str, str]],
    ) -> None:
        current = combo.currentData()
        combo.blockSignals(True)
        combo.clear()
        for label_key, data in items:
            combo.addItem(tr(label_key), data)
        if current is not None:
            for i in range(combo.count()):
                if combo.itemData(i) == current:
                    combo.setCurrentIndex(i)
                    break
        combo.blockSignals(False)
