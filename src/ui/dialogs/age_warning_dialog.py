"""Age restriction warning dialog."""

from __future__ import annotations

from PyQt6.QtWidgets import QDialog, QDialogButtonBox, QLabel, QVBoxLayout

from ui.i18n.translator import tr


class AgeWarningDialog(QDialog):
    def __init__(self, age_limit: int, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle(tr("dialog.age.title"))
        layout = QVBoxLayout(self)

        label = QLabel(tr("dialog.age.message", age=age_limit))
        label.setWordWrap(True)
        layout.addWidget(label)

        buttons = QDialogButtonBox()
        confirm = buttons.addButton(tr("dialog.age.confirm"), QDialogButtonBox.ButtonRole.AcceptRole)
        cancel = buttons.addButton(tr("dialog.age.cancel"), QDialogButtonBox.ButtonRole.RejectRole)
        confirm.clicked.connect(self.accept)
        cancel.clicked.connect(self.reject)
        layout.addWidget(buttons)
