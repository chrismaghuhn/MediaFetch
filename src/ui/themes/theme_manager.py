"""Theme management with system/dark/light modes."""

from __future__ import annotations

import logging

from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtWidgets import QApplication

from models.settings import ThemeMode
from utils.paths import themes_dir

logger = logging.getLogger(__name__)


class ThemeManager(QObject):
    theme_changed = pyqtSignal(str)

    def __init__(self, app: QApplication) -> None:
        super().__init__()
        self._app = app
        self._mode: ThemeMode = "system"

    @property
    def mode(self) -> ThemeMode:
        return self._mode

    def apply(self, mode: ThemeMode) -> None:
        self._mode = mode
        effective = self._effective_mode(mode)
        self._load_stylesheet(effective)
        self.theme_changed.emit(effective)

    def _effective_mode(self, mode: ThemeMode) -> str:
        if mode == "system":
            hints = self._app.styleHints()
            scheme = hints.colorScheme()
            scheme_name = scheme.name() if callable(scheme.name) else scheme.name
            if isinstance(scheme_name, str) and scheme_name.lower() == "dark":
                return "dark"
            palette = self._app.palette()
            window = palette.color(QPalette.ColorRole.Window)
            return "dark" if window.lightness() < 128 else "light"
        return mode

    def _load_stylesheet(self, effective: str) -> None:
        candidates = [
            themes_dir() / f"{effective}.qss",
        ]
        from pathlib import Path

        candidates.append(Path(__file__).parent / f"{effective}.qss")

        for path in candidates:
            if path.is_file():
                try:
                    stylesheet = path.read_text(encoding="utf-8")
                    self._app.setStyleSheet(stylesheet)
                    return
                except OSError as exc:
                    logger.error("Failed to load theme %s: %s", path, exc)

        logger.warning("No stylesheet found for theme '%s'", effective)
        self._app.setStyleSheet("")
