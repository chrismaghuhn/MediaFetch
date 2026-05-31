"""Copyright / geo-block warning dialog."""

from __future__ import annotations

from PyQt6.QtWidgets import QDialog, QDialogButtonBox, QLabel, QVBoxLayout

from ui.i18n.translator import tr


class CopyrightDialog(QDialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle(tr("dialog.copyright.title"))
        layout = QVBoxLayout(self)

        label = QLabel(tr("dialog.copyright.message"))
        label.setWordWrap(True)
        layout.addWidget(label)

        buttons = QDialogButtonBox()
        confirm = buttons.addButton(tr("dialog.copyright.confirm"), QDialogButtonBox.ButtonRole.AcceptRole)
        cancel = buttons.addButton(tr("dialog.copyright.cancel"), QDialogButtonBox.ButtonRole.RejectRole)
        confirm.clicked.connect(self.accept)
        cancel.clicked.connect(self.reject)
        layout.addWidget(buttons)
