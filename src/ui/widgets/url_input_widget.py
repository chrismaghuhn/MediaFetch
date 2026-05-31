"""Hero-style URL input panel."""

from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QClipboard, QGuiApplication
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPlainTextEdit,
    QVBoxLayout,
    QWidget,
)

from ui.i18n.translator import tr
from ui.widgets.styled_button import styled_button


class UrlInputWidget(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._build_ui()
        self._input.textChanged.connect(self._update_count)

    def _build_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        panel = QFrame()
        panel.setObjectName("HeroPanel")
        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(0, 0, 0, 0)
        panel_layout.setSpacing(0)

        header = QFrame()
        header.setObjectName("HeroHeader")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(18, 16, 18, 16)
        header_layout.setSpacing(12)

        icon = QLabel("↓")
        icon.setObjectName("BrandBadge")
        icon.setFixedSize(38, 38)
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(icon)

        text_col = QVBoxLayout()
        text_col.setSpacing(2)
        self._hero_title = QLabel(tr("url.hero.title"))
        self._hero_title.setObjectName("PageTitle")
        text_col.addWidget(self._hero_title)
        self._hero_tagline = QLabel(tr("url.hero.tagline"))
        self._hero_tagline.setObjectName("PageSubtitle")
        text_col.addWidget(self._hero_tagline)
        header_layout.addLayout(text_col, stretch=1)
        panel_layout.addWidget(header)

        body = QWidget()
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(18, 16, 18, 16)
        body_layout.setSpacing(12)

        self._input = QPlainTextEdit()
        self._input.setPlaceholderText(tr("url.placeholder"))
        self._input.setMaximumHeight(90)
        self._input.setTabChangesFocus(True)
        body_layout.addWidget(self._input)

        footer = QHBoxLayout()
        self._count_label = QLabel(tr("url.count", count=0))
        self._count_label.setProperty("mono", "true")
        self._count_label.setProperty("class", "muted")
        footer.addWidget(self._count_label)
        footer.addStretch()

        self._paste_btn = styled_button(tr("url.paste"), variant="ghost")
        self._paste_btn.clicked.connect(self._paste_clipboard)
        footer.addWidget(self._paste_btn)

        self._add_btn = styled_button(tr("url.add"), variant="primary")
        footer.addWidget(self._add_btn)
        body_layout.addLayout(footer)
        panel_layout.addWidget(body)

        outer.addWidget(panel)

    def _update_count(self) -> None:
        count = len(self.get_urls())
        self._count_label.setText(tr("url.count", count=count))

    def _paste_clipboard(self) -> None:
        clipboard = QGuiApplication.clipboard()
        if clipboard:
            text = clipboard.text()
            if text:
                current = self._input.toPlainText()
                if current and not current.endswith("\n"):
                    current += "\n"
                self._input.setPlainText(current + text.strip())

    @property
    def add_button(self):
        return self._add_btn

    def get_urls(self) -> list[str]:
        text = self._input.toPlainText()
        return [line.strip() for line in text.splitlines() if line.strip()]

    def clear(self) -> None:
        self._input.clear()

    def retranslate(self) -> None:
        self._hero_title.setText(tr("url.hero.title"))
        self._hero_tagline.setText(tr("url.hero.tagline"))
        self._input.setPlaceholderText(tr("url.placeholder"))
        self._paste_btn.setText(tr("url.paste"))
        self._add_btn.setText(tr("url.add"))
        self._update_count()
