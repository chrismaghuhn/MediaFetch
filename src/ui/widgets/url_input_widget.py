"""URL input widget."""

from __future__ import annotations

from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from ui.i18n.translator import tr


class UrlInputWidget(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(tr("url.label")))

        self._input = QTextEdit()
        self._input.setPlaceholderText(tr("url.placeholder"))
        self._input.setMaximumHeight(100)
        layout.addWidget(self._input)

        row = QHBoxLayout()
        self._add_btn = QPushButton(tr("url.add"))
        row.addStretch()
        row.addWidget(self._add_btn)
        layout.addLayout(row)

    @property
    def add_button(self) -> QPushButton:
        return self._add_btn

    def get_urls(self) -> list[str]:
        text = self._input.toPlainText()
        return [line.strip() for line in text.splitlines() if line.strip()]

    def clear(self) -> None:
        self._input.clear()
