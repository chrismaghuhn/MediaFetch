"""Download options dialog."""

from __future__ import annotations

from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QSpinBox,
    QVBoxLayout,
)

from core.format_selector import ContentFilter, DownloadOptions
from ui.i18n.translator import tr


class FormatDialog(QDialog):
    def __init__(self, parent=None, defaults: DownloadOptions | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle(tr("format.title"))
        self._defaults = defaults or DownloadOptions()
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        form = QFormLayout()

        self._quality = QSpinBox()
        self._quality.setRange(360, 4320)
        self._quality.setSingleStep(360)
        self._quality.setValue(self._defaults.quality)
        form.addRow(tr("format.quality"), self._quality)

        self._audio_only = QCheckBox(tr("format.audio_only"))
        self._audio_only.setChecked(self._defaults.audio_only)
        self._audio_only.toggled.connect(self._on_audio_toggled)
        form.addRow("", self._audio_only)

        self._audio_format = QComboBox()
        self._audio_format.addItems(["mp3", "m4a"])
        idx = self._audio_format.findText(self._defaults.audio_format)
        if idx >= 0:
            self._audio_format.setCurrentIndex(idx)
        form.addRow(tr("format.audio_format"), self._audio_format)

        self._subtitles = QCheckBox(tr("format.subtitles"))
        self._subtitles.setChecked(self._defaults.include_subtitles)
        form.addRow("", self._subtitles)

        self._content_filter = QComboBox()
        self._content_filter.addItem(tr("format.content.all"), ContentFilter.ALL)
        self._content_filter.addItem(tr("format.content.shorts"), ContentFilter.SHORTS)
        self._content_filter.addItem(tr("format.content.full"), ContentFilter.FULL)
        for i in range(self._content_filter.count()):
            if self._content_filter.itemData(i) == self._defaults.content_filter:
                self._content_filter.setCurrentIndex(i)
                break
        form.addRow(tr("format.content_filter"), self._content_filter)

        layout.addLayout(form)

        hint = QLabel(tr("error.content_filter"))
        hint.setProperty("class", "muted")
        hint.setWordWrap(True)
        layout.addWidget(hint)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self._on_audio_toggled(self._audio_only.isChecked())

    def _on_audio_toggled(self, checked: bool) -> None:
        self._quality.setEnabled(not checked)
        self._audio_format.setEnabled(checked)
        self._subtitles.setEnabled(not checked)

    def get_options(self) -> DownloadOptions:
        return DownloadOptions(
            quality=self._quality.value(),
            audio_only=self._audio_only.isChecked(),
            audio_format=self._audio_format.currentText(),  # type: ignore[arg-type]
            include_subtitles=self._subtitles.isChecked(),
            content_filter=self._content_filter.currentData(),
        )
