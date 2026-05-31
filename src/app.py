"""Application bootstrap."""

from __future__ import annotations

import sys

from PyQt6.QtWidgets import QApplication

from services.log_service import setup_logging
from services.settings_service import SettingsService
from ui.i18n.translator import Translator
from ui.main_window import MainWindow
from ui.themes.theme_manager import ThemeManager


class MediaFetchApp:
    def __init__(self) -> None:
        self.qt_app = QApplication(sys.argv)
        self.qt_app.setApplicationName("MediaFetch")
        self.qt_app.setOrganizationName("MediaFetch")

        self.settings_service = SettingsService()
        settings = self.settings_service.settings

        setup_logging(settings.log_path)

        translator = Translator.instance()
        translator.set_language(settings.language)

        self.theme_manager = ThemeManager(self.qt_app)
        self.theme_manager.apply(settings.theme)

        self.main_window = MainWindow(
            settings_service=self.settings_service,
            theme_manager=self.theme_manager,
        )

        if settings.check_updates_on_startup:
            from services.update_service import UpdateService
            UpdateService(settings.github_repo).check_and_notify(self.main_window)

    def run(self) -> int:
        self.main_window.show()
        return self.qt_app.exec()
