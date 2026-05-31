"""Settings panel widget — Studio layout with accent picker."""

from __future__ import annotations

from collections.abc import Callable

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from services.settings_service import SettingsService
from ui.i18n.translator import Translator, tr
from ui.themes.theme_manager import ThemeManager
from ui.themes.tokens import ACCENT_PRESETS
from ui.widgets.page_head import PageHead
from ui.widgets.panel import Panel
from ui.widgets.styled_button import styled_button

PREVIEW_DEBOUNCE_MS = 150


def _retranslate_combo(combo: QComboBox, items: list[tuple[str, str]]) -> None:
    current = combo.currentData()
    combo.blockSignals(True)
    combo.clear()
    for label_key, data in items:
        combo.addItem(tr(label_key), data)
    if current is not None:
        for i in range(combo.count()):
            if combo.itemData(i) == current:
                combo.setCurrentIndex(i)
                break
    combo.blockSignals(False)


class SettingsWidget(QWidget):
    def __init__(
        self,
        settings_service: SettingsService,
        theme_manager: ThemeManager,
        on_saved: Callable[[], None] | None = None,
        on_retranslate: Callable[[], None] | None = None,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self._settings_service = settings_service
        self._theme_manager = theme_manager
        self._on_saved = on_saved
        self._on_retranslate = on_retranslate
        self._accent = ACCENT_PRESETS[0]
        self._accent_buttons: list[QPushButton] = []
        self._preview_timer = QTimer(self)
        self._preview_timer.setSingleShot(True)
        self._preview_timer.setInterval(PREVIEW_DEBOUNCE_MS)
        self._preview_timer.timeout.connect(self._apply_preview_theme)
        self._build_ui()
        self._load_settings()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        panel = Panel()
        self._head = PageHead(tr("settings.title"), tr("settings.subtitle"))
        panel.content_layout.addWidget(self._head)

        form = QFormLayout()
        form.setSpacing(12)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)

        self._language = QComboBox()
        self._language.addItem("Deutsch", "de")
        self._language.addItem("English", "en")
        self._label_language = QLabel(tr("settings.language"))
        form.addRow(self._label_language, self._language)
        self._language.currentIndexChanged.connect(self._apply_language_preview)

        self._theme = QComboBox()
        self._theme.addItem(tr("settings.theme.system"), "system")
        self._theme.addItem(tr("settings.theme.dark"), "dark")
        self._theme.addItem(tr("settings.theme.light"), "light")
        self._label_theme = QLabel(tr("settings.theme"))
        form.addRow(self._label_theme, self._theme)
        self._theme.currentIndexChanged.connect(self._schedule_preview_theme)

        accent_row = QHBoxLayout()
        accent_row.setSpacing(8)
        for color in ACCENT_PRESETS:
            btn = QPushButton()
            btn.setProperty("accentSwatch", "true")
            btn.setProperty("accentColor", color)
            btn.setProperty("selected", "false")
            btn.setStyleSheet(f"background-color: {color};")
            btn.clicked.connect(lambda checked, c=color: self._select_accent(c))
            self._accent_buttons.append(btn)
            accent_row.addWidget(btn)
        accent_row.addStretch()
        self._accent_widget = QWidget()
        self._accent_widget.setLayout(accent_row)
        self._label_accent = QLabel(tr("settings.accent_color"))
        form.addRow(self._label_accent, self._accent_widget)

        download_row = QHBoxLayout()
        self._download_dir = QLineEdit()
        self._download_browse_btn = styled_button(tr("settings.browse"), variant="secondary")
        self._download_browse_btn.clicked.connect(self._browse_download_dir)
        download_row.addWidget(self._download_dir)
        download_row.addWidget(self._download_browse_btn)
        download_wrap = QWidget()
        download_wrap.setLayout(download_row)
        self._label_download_dir = QLabel(tr("settings.download_dir"))
        form.addRow(self._label_download_dir, download_wrap)

        self._max_concurrent = QSpinBox()
        self._max_concurrent.setRange(1, 10)
        self._label_max_concurrent = QLabel(tr("settings.max_concurrent"))
        form.addRow(self._label_max_concurrent, self._max_concurrent)

        self._max_retries = QSpinBox()
        self._max_retries.setRange(0, 10)
        self._label_max_retries = QLabel(tr("settings.max_retries"))
        form.addRow(self._label_max_retries, self._max_retries)

        self._default_quality = QSpinBox()
        self._default_quality.setRange(360, 4320)
        self._default_quality.setSingleStep(360)
        self._label_default_quality = QLabel(tr("settings.default_quality"))
        form.addRow(self._label_default_quality, self._default_quality)

        self._include_subtitles = QCheckBox(tr("settings.include_subtitles"))
        form.addRow("", self._include_subtitles)

        log_row = QHBoxLayout()
        self._log_path = QLineEdit()
        self._log_browse_btn = styled_button(tr("settings.browse"), variant="secondary")
        self._log_browse_btn.clicked.connect(self._browse_log_path)
        log_row.addWidget(self._log_path)
        log_row.addWidget(self._log_browse_btn)
        log_wrap = QWidget()
        log_wrap.setLayout(log_row)
        self._label_log_path = QLabel(tr("settings.log_path"))
        form.addRow(self._label_log_path, log_wrap)

        self._log_level = QComboBox()
        for level in ("DEBUG", "INFO", "WARNING", "ERROR"):
            self._log_level.addItem(level, level)
        self._label_log_level = QLabel(tr("settings.log_level"))
        form.addRow(self._label_log_level, self._log_level)

        log_actions = QHBoxLayout()
        self._open_logs_btn = styled_button(tr("settings.open_logs"), variant="secondary")
        self._open_logs_btn.clicked.connect(self._open_logs_folder)
        self._export_logs_btn = styled_button(tr("settings.export_logs"), variant="secondary")
        self._export_logs_btn.clicked.connect(self._export_logs)
        log_actions.addWidget(self._open_logs_btn)
        log_actions.addWidget(self._export_logs_btn)
        log_actions.addStretch()
        log_actions_wrap = QWidget()
        log_actions_wrap.setLayout(log_actions)
        form.addRow("", log_actions_wrap)

        self._restore_queue = QCheckBox(tr("settings.restore_queue"))
        form.addRow("", self._restore_queue)

        self._check_updates = QCheckBox(tr("settings.check_updates"))
        form.addRow("", self._check_updates)

        panel.content_layout.addLayout(form)

        self._save_btn = styled_button(tr("settings.save"), variant="primary")
        self._save_btn.clicked.connect(self._save)
        panel.content_layout.addWidget(self._save_btn)

        layout.addWidget(panel)
        layout.addStretch()

    def _select_accent(self, color: str, *, schedule_preview: bool = True) -> None:
        self._accent = color
        for btn in self._accent_buttons:
            selected = btn.property("accentColor") == color
            btn.setProperty("selected", "true" if selected else "false")
        self._repolish_accent_swatches()
        if schedule_preview:
            self._schedule_preview_theme()

    def _repolish_accent_swatches(self) -> None:
        for btn in self._accent_buttons:
            btn.style().unpolish(btn)
            btn.style().polish(btn)

    def _schedule_preview_theme(self) -> None:
        self._preview_timer.start()

    def _apply_preview_theme(self) -> None:
        theme = self._theme.currentData()
        if theme:
            self._theme_manager.apply(theme, accent=self._accent, preview=True)

    def _apply_language_preview(self) -> None:
        language = self._language.currentData()
        if not language or language == Translator.instance().language:
            return
        Translator.instance().set_language(language)
        if self._on_retranslate:
            self._on_retranslate()

    def _load_settings(self) -> None:
        s = self._settings_service.settings
        self._language.blockSignals(True)
        self._theme.blockSignals(True)
        for i in range(self._language.count()):
            if self._language.itemData(i) == s.language:
                self._language.setCurrentIndex(i)
                break
        for i in range(self._theme.count()):
            if self._theme.itemData(i) == s.theme:
                self._theme.setCurrentIndex(i)
                break
        self._accent = s.accent_color if s.accent_color in ACCENT_PRESETS else ACCENT_PRESETS[0]
        self._select_accent(self._accent, schedule_preview=False)
        self._download_dir.setText(s.download_dir)
        self._max_concurrent.setValue(s.max_concurrent)
        self._max_retries.setValue(s.max_retries)
        self._default_quality.setValue(s.default_quality)
        self._include_subtitles.setChecked(s.include_subtitles)
        self._log_path.setText(s.log_path)
        for i in range(self._log_level.count()):
            if self._log_level.itemData(i) == s.log_level:
                self._log_level.setCurrentIndex(i)
                break
        self._restore_queue.setChecked(s.restore_queue_on_startup)
        self._check_updates.setChecked(s.check_updates_on_startup)
        self._language.blockSignals(False)
        self._theme.blockSignals(False)

    def _browse_download_dir(self) -> None:
        path = QFileDialog.getExistingDirectory(self, tr("settings.download_dir"))
        if path:
            self._download_dir.setText(path)

    def _browse_log_path(self) -> None:
        path, _ = QFileDialog.getSaveFileName(self, tr("settings.log_path"))
        if path:
            self._log_path.setText(path)

    def _open_logs_folder(self) -> None:
        import os
        from pathlib import Path

        log_dir = Path(self._log_path.text()).parent
        log_dir.mkdir(parents=True, exist_ok=True)
        os.startfile(log_dir)  # noqa: S606

    def _export_logs(self) -> None:
        from pathlib import Path

        from PyQt6.QtWidgets import QMessageBox

        from services.log_service import export_logs_zip

        log_dir = Path(self._log_path.text()).parent
        dest = log_dir / "mediafetch-logs-export"
        try:
            archive = export_logs_zip(log_dir, dest)
            QMessageBox.information(
                self,
                tr("app.title"),
                tr("settings.log_export_done", path=str(archive)),
            )
        except OSError:
            QMessageBox.warning(self, tr("app.title"), tr("settings.log_export_failed"))

    def _save(self) -> None:
        language = self._language.currentData()
        theme = self._theme.currentData()

        self._settings_service.update(
            language=language,
            theme=theme,
            accent_color=self._accent,
            download_dir=self._download_dir.text(),
            max_concurrent=self._max_concurrent.value(),
            max_retries=self._max_retries.value(),
            default_quality=self._default_quality.value(),
            include_subtitles=self._include_subtitles.isChecked(),
            log_path=self._log_path.text(),
            log_level=self._log_level.currentData(),
            restore_queue_on_startup=self._restore_queue.isChecked(),
            check_updates_on_startup=self._check_updates.isChecked(),
        )

        Translator.instance().set_language(language)
        self._preview_timer.stop()
        self._theme_manager.apply(theme, accent=self._accent, preview=False)
        from services.log_service import setup_logging

        setup_logging(self._log_path.text(), level=self._log_level.currentData())
        if self._on_saved:
            self._on_saved()

    def retranslate(self) -> None:
        self._head.set_title(tr("settings.title"))
        self._head.set_subtitle(tr("settings.subtitle"))
        self._label_language.setText(tr("settings.language"))
        self._label_theme.setText(tr("settings.theme"))
        _retranslate_combo(
            self._theme,
            [
                ("settings.theme.system", "system"),
                ("settings.theme.dark", "dark"),
                ("settings.theme.light", "light"),
            ],
        )
        self._label_accent.setText(tr("settings.accent_color"))
        self._label_download_dir.setText(tr("settings.download_dir"))
        self._download_browse_btn.setText(tr("settings.browse"))
        self._label_max_concurrent.setText(tr("settings.max_concurrent"))
        self._label_max_retries.setText(tr("settings.max_retries"))
        self._label_default_quality.setText(tr("settings.default_quality"))
        self._include_subtitles.setText(tr("settings.include_subtitles"))
        self._label_log_path.setText(tr("settings.log_path"))
        self._log_browse_btn.setText(tr("settings.browse"))
        self._label_log_level.setText(tr("settings.log_level"))
        self._open_logs_btn.setText(tr("settings.open_logs"))
        self._export_logs_btn.setText(tr("settings.export_logs"))
        self._restore_queue.setText(tr("settings.restore_queue"))
        self._check_updates.setText(tr("settings.check_updates"))
        self._save_btn.setText(tr("settings.save"))
