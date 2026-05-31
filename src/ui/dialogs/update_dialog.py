"""Update notification dialog."""

from __future__ import annotations

import os
import subprocess
import webbrowser
from enum import Enum

from PyQt6.QtWidgets import QDialog, QDialogButtonBox, QLabel, QPushButton, QVBoxLayout

from core.updater import UpdateInfo, download_file
from ui.i18n.translator import tr
from utils.paths import app_data_dir


class UpdateDialogResult(Enum):
    DISMISS = "dismiss"
    REMIND_LATER = "remind_later"
    SKIP_VERSION = "skip_version"
    OPEN_RELEASE = "open_release"


class UpdateDialog(QDialog):
    def __init__(self, update: UpdateInfo, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle(tr("dialog.update.title"))
        self._update = update
        self._result = UpdateDialogResult.DISMISS
        self._build_ui()

    def exec(self) -> UpdateDialogResult:
        super().exec()
        return self._result

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        update = self._update

        layout.addWidget(
            QLabel(tr("dialog.update.message", version=update.latest, current=update.current))
        )

        if update.body:
            changelog = QLabel(update.body[:2000])
            changelog.setWordWrap(True)
            layout.addWidget(changelog)
        else:
            instructions = QLabel(tr("dialog.update.instructions"))
            instructions.setWordWrap(True)
            layout.addWidget(instructions)

        open_btn = QPushButton(tr("dialog.update.open_release"))
        open_btn.clicked.connect(self._open_release)
        layout.addWidget(open_btn)

        if update.installer_url:
            download_btn = QPushButton(tr("dialog.update.download_installer"))
            download_btn.clicked.connect(self._download_installer)
            layout.addWidget(download_btn)

        buttons = QDialogButtonBox()
        skip_btn = buttons.addButton(
            tr("dialog.update.skip_version"), QDialogButtonBox.ButtonRole.ActionRole
        )
        skip_btn.clicked.connect(self._skip_version)

        remind_btn = buttons.addButton(
            tr("dialog.update.remind_later"), QDialogButtonBox.ButtonRole.ActionRole
        )
        remind_btn.clicked.connect(self._remind_later)

        dismiss = buttons.addButton(tr("dialog.update.dismiss"), QDialogButtonBox.ButtonRole.RejectRole)
        dismiss.clicked.connect(self.reject)
        layout.addWidget(buttons)

    def _open_release(self) -> None:
        webbrowser.open(self._update.url)
        self._result = UpdateDialogResult.OPEN_RELEASE

    def _skip_version(self) -> None:
        self._result = UpdateDialogResult.SKIP_VERSION
        self.accept()

    def _remind_later(self) -> None:
        self._result = UpdateDialogResult.REMIND_LATER
        self.accept()

    def _download_installer(self) -> None:
        dest = app_data_dir() / "downloads" / f"MediaFetch-{self._update.latest}-Setup.exe"
        if download_file(
            self._update.installer_url,
            dest,
            expected_sha256=self._update.installer_sha256 or None,
        ):
            if os.name == "nt":
                os.startfile(dest.parent)  # noqa: S606
                subprocess.Popen([str(dest)], shell=True)  # noqa: S603
            self._result = UpdateDialogResult.OPEN_RELEASE
            self.accept()
