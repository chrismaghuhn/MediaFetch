"""Card panel frame."""

from __future__ import annotations

from PyQt6.QtWidgets import QFrame, QVBoxLayout


class Panel(QFrame):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("Panel")
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(18, 18, 18, 18)
        self._layout.setSpacing(12)

    @property
    def content_layout(self) -> QVBoxLayout:
        return self._layout
