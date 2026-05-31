"""Page header with title, subtitle, and action buttons."""

from __future__ import annotations

from PyQt6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget


class PageHead(QWidget):
    def __init__(
        self,
        title: str,
        subtitle: str = "",
        parent=None,
    ) -> None:
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 8)

        text_col = QVBoxLayout()
        text_col.setSpacing(2)
        self._title = QLabel(title)
        self._title.setObjectName("PageTitle")
        text_col.addWidget(self._title)
        self._subtitle = QLabel(subtitle)
        self._subtitle.setObjectName("PageSubtitle")
        self._subtitle.setVisible(bool(subtitle))
        text_col.addWidget(self._subtitle)
        layout.addLayout(text_col, stretch=1)

        self._actions = QHBoxLayout()
        self._actions.setSpacing(8)
        layout.addLayout(self._actions)

    @property
    def actions_layout(self) -> QHBoxLayout:
        return self._actions

    def set_title(self, title: str) -> None:
        self._title.setText(title)

    def set_subtitle(self, subtitle: str) -> None:
        self._subtitle.setText(subtitle)
        self._subtitle.setVisible(bool(subtitle))
