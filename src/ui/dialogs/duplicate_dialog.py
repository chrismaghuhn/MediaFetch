"""Duplicate download confirmation dialog."""

from __future__ import annotations

from PyQt6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QLabel,
    QListWidget,
    QVBoxLayout,
)

from core.duplicate_checker import DuplicateMatch
from ui.i18n.translator import tr


class DuplicateDialog(QDialog):
    SKIP_ALL = 1
    DOWNLOAD_ALL = 2
    REVIEW = 3

    def __init__(self, duplicates: list[DuplicateMatch], parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle(tr("dialog.duplicate.title"))
        self._duplicates = duplicates
        self._choice = self.REVIEW
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel(tr("dialog.duplicate.message")))

        list_widget = QListWidget()
        for match in self._duplicates:
            info = match.video_info
            list_widget.addItem(f"{info.title} — {match.file_path}")
        layout.addWidget(list_widget)

        buttons = QDialogButtonBox()
        skip_btn = buttons.addButton(tr("dialog.duplicate.skip_all"), QDialogButtonBox.ButtonRole.NoRole)
        download_btn = buttons.addButton(tr("dialog.duplicate.download_all"), QDialogButtonBox.ButtonRole.YesRole)
        review_btn = buttons.addButton(tr("dialog.duplicate.review"), QDialogButtonBox.ButtonRole.AcceptRole)

        skip_btn.clicked.connect(lambda: self._finish(self.SKIP_ALL))
        download_btn.clicked.connect(lambda: self._finish(self.DOWNLOAD_ALL))
        review_btn.clicked.connect(lambda: self._finish(self.REVIEW))
        layout.addWidget(buttons)

    def _finish(self, choice: int) -> None:
        self._choice = choice
        self.accept()

    @property
    def choice(self) -> int:
        return self._choice
