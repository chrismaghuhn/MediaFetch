"""Brand logo tile and app name."""

from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QWidget

from ui.i18n.translator import tr


class BrandWidget(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        self._badge = QLabel("MF")
        self._badge.setObjectName("BrandBadge")
        self._badge.setFixedSize(30, 30)
        self._badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._badge)

        self._name = QLabel(tr("app.title"))
        self._name.setObjectName("BrandName")
        layout.addWidget(self._name)

    def retranslate(self) -> None:
        self._name.setText(tr("app.title"))
