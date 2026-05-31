"""Main application window."""

from __future__ import annotations

import logging

from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import (
    QMainWindow,
    QMessageBox,
    QStatusBar,
    QTabWidget,
)

from core.downloader import Downloader
from core.duplicate_checker import DuplicateChecker
from core.format_selector import DownloadOptions
from core.queue_manager import QueueManager
from core.validators import validate_url
from models.download_item import DownloadItem
from services.history_service import HistoryService
from services.network_service import has_internet
from services.settings_service import SettingsService
from ui.dialogs.age_warning_dialog import AgeWarningDialog
from ui.dialogs.copyright_dialog import CopyrightDialog
from ui.dialogs.duplicate_dialog import DuplicateDialog
from ui.dialogs.format_dialog import FormatDialog
from ui.i18n.translator import tr
from ui.themes.theme_manager import ThemeManager
from ui.widgets.history_widget import HistoryWidget
from ui.widgets.queue_widget import QueueWidget
from ui.widgets.settings_widget import SettingsWidget
from ui.widgets.url_input_widget import UrlInputWidget

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    def __init__(
        self,
        settings_service: SettingsService,
        theme_manager: ThemeManager,
    ) -> None:
        super().__init__()
        self._settings_service = settings_service
        self._theme_manager = theme_manager
        self._history = HistoryService()
        self._duplicate_checker = DuplicateChecker(self._history)

        settings = settings_service.settings
        self._queue = QueueManager(
            download_dir=settings.download_dir,
            max_concurrent=settings.max_concurrent,
            max_retries=settings.max_retries,
            history_service=self._history,
        )

        self._build_ui()
        self._build_menu()
        self._connect_signals()
        self._restore_queue()
        self.retranslate_ui()

    def _build_ui(self) -> None:
        self.setMinimumSize(900, 650)

        self._tabs = QTabWidget()
        self.setCentralWidget(self._tabs)

        # Download tab
        from PyQt6.QtWidgets import QVBoxLayout, QWidget

        download_page = QWidget()
        download_layout = QVBoxLayout(download_page)

        self._url_input = UrlInputWidget()
        download_layout.addWidget(self._url_input)

        self._queue_widget = QueueWidget(self._queue)
        download_layout.addWidget(self._queue_widget)

        self._tabs.addTab(download_page, tr("queue.title"))

        self._history_widget = HistoryWidget(self._history)
        self._tabs.addTab(self._history_widget, tr("history.title"))

        self._settings_widget = SettingsWidget(
            self._settings_service,
            self._theme_manager,
            on_saved=self._on_settings_saved,
        )
        self._tabs.addTab(self._settings_widget, tr("settings.title"))

        self._status = QStatusBar()
        self.setStatusBar(self._status)
        self._status.showMessage(tr("app.ready"))

    def _build_menu(self) -> None:
        menubar = self.menuBar()

        file_menu = menubar.addMenu("")
        self._quit_action = QAction("", self)
        self._quit_action.triggered.connect(self.close)
        file_menu.addAction(self._quit_action)

        help_menu = menubar.addMenu("")
        self._update_action = QAction("", self)
        self._update_action.triggered.connect(self._check_updates_manual)
        help_menu.addAction(self._update_action)

        self._file_menu = file_menu
        self._help_menu = help_menu

    def _connect_signals(self) -> None:
        self._url_input.add_button.clicked.connect(self._on_add_urls)
        self._queue.validation_failed.connect(self._on_validation_failed)

    def _restore_queue(self) -> None:
        if self._settings_service.settings.restore_queue_on_startup:
            self._queue.load_queue()

    def _on_add_urls(self) -> None:
        if not has_internet():
            QMessageBox.warning(self, tr("app.title"), tr("error.network"))
            return

        urls = self._url_input.get_urls()
        if not urls:
            return

        for url in urls:
            valid, error_key = validate_url(url)
            if not valid:
                QMessageBox.warning(self, tr("app.title"), tr(error_key))
                return

        settings = self._settings_service.settings
        defaults = DownloadOptions(
            quality=settings.default_quality,
            include_subtitles=settings.include_subtitles,
        )

        dialog = FormatDialog(self, defaults=defaults)
        if dialog.exec() != FormatDialog.DialogCode.Accepted:
            return

        options = dialog.get_options()

        downloader = Downloader(settings.download_dir)
        validated_infos = []
        items: list[DownloadItem] = []

        for url in urls:
            try:
                info = downloader.extract_info(url)
                validated_infos.append(info)

                if info.age_limit >= 18:
                    age_dialog = AgeWarningDialog(info.age_limit, self)
                    if age_dialog.exec() != AgeWarningDialog.DialogCode.Accepted:
                        continue

                item = DownloadItem(url=url, options=options, video_info=info, title=info.title)
                items.append(item)
            except Exception as exc:
                logger.exception("Failed to validate %s", url)
                error_key = str(exc) if str(exc).startswith("error.") else "error.generic"
                if error_key == "error.copyright":
                    copyright_dialog = CopyrightDialog(self)
                    if copyright_dialog.exec() != CopyrightDialog.DialogCode.Accepted:
                        continue
                QMessageBox.warning(self, tr("app.title"), tr(error_key))

        duplicates = self._duplicate_checker.find_duplicates(validated_infos)
        if duplicates:
            dup_dialog = DuplicateDialog(duplicates, self)
            if dup_dialog.exec() == DuplicateDialog.DialogCode.Accepted:
                if dup_dialog.choice == DuplicateDialog.SKIP_ALL:
                    dup_ids = {m.video_info.video_id for m in duplicates}
                    items = [i for i in items if not i.video_info or i.video_info.video_id not in dup_ids]
                elif dup_dialog.choice == DuplicateDialog.REVIEW:
                    dup_ids = {m.video_info.video_id for m in duplicates}
                    items = [i for i in items if not i.video_info or i.video_info.video_id not in dup_ids]

        for item in items:
            self._queue.add_item(item)

        self._url_input.clear()
        self._queue.start()

    def _on_settings_saved(self) -> None:
        settings = self._settings_service.settings
        self._queue.set_download_dir(settings.download_dir)
        self._queue.set_limits(settings.max_concurrent, settings.max_retries)
        self.retranslate_ui()

    def _on_validation_failed(self, url: str, error_key: str) -> None:
        self._status.showMessage(tr(error_key))
        logger.warning("Validation failed for %s: %s", url, error_key)

    def _check_updates_manual(self) -> None:
        from services.update_service import UpdateService

        service = UpdateService(self._settings_service.settings.github_repo)
        service.check_and_notify(self)

    def retranslate_ui(self) -> None:
        self.setWindowTitle(tr("app.title"))
        self._file_menu.setTitle(tr("menu.file"))
        self._quit_action.setText(tr("menu.quit"))
        self._help_menu.setTitle(tr("menu.help"))
        self._update_action.setText(tr("menu.check_updates"))
        self._tabs.setTabText(0, tr("queue.title"))
        self._tabs.setTabText(1, tr("history.title"))
        self._tabs.setTabText(2, tr("settings.title"))
        self._status.showMessage(tr("app.ready"))
        self._queue_widget.retranslate()

    def closeEvent(self, event) -> None:
        self._queue.save_queue()
        if not self._settings_service.settings.restore_queue_on_startup:
            self._queue.clear_saved_queue()
        super().closeEvent(event)
