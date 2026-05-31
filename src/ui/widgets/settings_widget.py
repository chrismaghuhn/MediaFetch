"""Settings panel widget."""

from __future__ import annotations

from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from collections.abc import Callable

from models.settings import AppSettings
from services.settings_service import SettingsService
from ui.i18n.translator import Translator, tr
from ui.themes.theme_manager import ThemeManager


class SettingsWidget(QWidget):
    def __init__(
        self,
        settings_service: SettingsService,
        theme_manager: ThemeManager,
        on_saved: Callable[[], None] | None = None,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self._settings_service = settings_service
        self._theme_manager = theme_manager
        self._on_saved = on_saved
        self._build_ui()
        self._load_settings()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        group = QGroupBox(tr("settings.title"))
        form = QFormLayout(group)

        self._language = QComboBox()
        self._language.addItem("Deutsch", "de")
        self._language.addItem("English", "en")
        form.addRow(tr("settings.language"), self._language)

        self._theme = QComboBox()
        self._theme.addItem(tr("settings.theme.system"), "system")
        self._theme.addItem(tr("settings.theme.dark"), "dark")
        self._theme.addItem(tr("settings.theme.light"), "light")
        form.addRow(tr("settings.theme"), self._theme)

        download_row = QHBoxLayout()
        self._download_dir = QLineEdit()
        browse = QPushButton(tr("settings.browse"))
        browse.setProperty("class", "secondary")
        browse.clicked.connect(self._browse_download_dir)
        download_row.addWidget(self._download_dir)
        download_row.addWidget(browse)
        form.addRow(tr("settings.download_dir"), download_row)

        self._max_concurrent = QSpinBox()
        self._max_concurrent.setRange(1, 10)
        form.addRow(tr("settings.max_concurrent"), self._max_concurrent)

        self._max_retries = QSpinBox()
        self._max_retries.setRange(0, 10)
        form.addRow(tr("settings.max_retries"), self._max_retries)

        self._default_quality = QSpinBox()
        self._default_quality.setRange(360, 4320)
        self._default_quality.setSingleStep(360)
        form.addRow(tr("settings.default_quality"), self._default_quality)

        self._include_subtitles = QCheckBox(tr("settings.include_subtitles"))
        form.addRow("", self._include_subtitles)

        log_row = QHBoxLayout()
        self._log_path = QLineEdit()
        log_browse = QPushButton(tr("settings.browse"))
        log_browse.setProperty("class", "secondary")
        log_browse.clicked.connect(self._browse_log_path)
        log_row.addWidget(self._log_path)
        log_row.addWidget(log_browse)
        form.addRow(tr("settings.log_path"), log_row)

        self._restore_queue = QCheckBox(tr("settings.restore_queue"))
        form.addRow("", self._restore_queue)

        self._check_updates = QCheckBox(tr("settings.check_updates"))
        form.addRow("", self._check_updates)

        layout.addWidget(group)

        save_btn = QPushButton(tr("settings.save"))
        save_btn.clicked.connect(self._save)
        layout.addWidget(save_btn)
        layout.addStretch()

    def _load_settings(self) -> None:
        s = self._settings_service.settings
        for i in range(self._language.count()):
            if self._language.itemData(i) == s.language:
                self._language.setCurrentIndex(i)
                break
        for i in range(self._theme.count()):
            if self._theme.itemData(i) == s.theme:
                self._theme.setCurrentIndex(i)
                break
        self._download_dir.setText(s.download_dir)
        self._max_concurrent.setValue(s.max_concurrent)
        self._max_retries.setValue(s.max_retries)
        self._default_quality.setValue(s.default_quality)
        self._include_subtitles.setChecked(s.include_subtitles)
        self._log_path.setText(s.log_path)
        self._restore_queue.setChecked(s.restore_queue_on_startup)
        self._check_updates.setChecked(s.check_updates_on_startup)

    def _browse_download_dir(self) -> None:
        path = QFileDialog.getExistingDirectory(self, tr("settings.download_dir"))
        if path:
            self._download_dir.setText(path)

    def _browse_log_path(self) -> None:
        path, _ = QFileDialog.getSaveFileName(self, tr("settings.log_path"))
        if path:
            self._log_path.setText(path)

    def _save(self) -> None:
        language = self._language.currentData()
        theme = self._theme.currentData()

        self._settings_service.update(
            language=language,
            theme=theme,
            download_dir=self._download_dir.text(),
            max_concurrent=self._max_concurrent.value(),
            max_retries=self._max_retries.value(),
            default_quality=self._default_quality.value(),
            include_subtitles=self._include_subtitles.isChecked(),
            log_path=self._log_path.text(),
            restore_queue_on_startup=self._restore_queue.isChecked(),
            check_updates_on_startup=self._check_updates.isChecked(),
        )

        Translator.instance().set_language(language)
        self._theme_manager.apply(theme)
        if self._on_saved:
            self._on_saved()

    def retranslate(self) -> None:
        pass
