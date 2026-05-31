"""Update notification dialog."""

from __future__ import annotations

import webbrowser

from PyQt6.QtWidgets import QDialog, QDialogButtonBox, QLabel, QPushButton, QVBoxLayout

from ui.i18n.translator import tr


class UpdateDialog(QDialog):
    def __init__(
        self,
        current_version: str,
        latest_version: str,
        release_url: str,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle(tr("dialog.update.title"))
        self._release_url = release_url
        self._build_ui(current_version, latest_version)

    def _build_ui(self, current: str, latest: str) -> None:
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel(tr("dialog.update.message", version=latest, current=current)))
        instructions = QLabel(tr("dialog.update.instructions"))
        instructions.setWordWrap(True)
        layout.addWidget(instructions)

        open_btn = QPushButton(tr("dialog.update.open_release"))
        open_btn.clicked.connect(self._open_release)
        layout.addWidget(open_btn)

        buttons = QDialogButtonBox()
        dismiss = buttons.addButton(tr("dialog.update.dismiss"), QDialogButtonBox.ButtonRole.RejectRole)
        dismiss.clicked.connect(self.reject)
        layout.addWidget(buttons)

    def _open_release(self) -> None:
        webbrowser.open(self._release_url)
