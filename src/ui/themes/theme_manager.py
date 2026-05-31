"""Theme management with Studio design tokens."""

from __future__ import annotations

import logging

from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtGui import QColor, QPalette
from PyQt6.QtWidgets import QApplication, QWidget

from models.settings import ThemeMode
from ui.themes.tokens import ACCENT_PRESETS, build_stylesheet, resolve_tokens

logger = logging.getLogger(__name__)


def repolish_widget_tree(widget: QWidget) -> None:
    widget.style().unpolish(widget)
    widget.style().polish(widget)
    for child in widget.children():
        if isinstance(child, QWidget):
            repolish_widget_tree(child)


def apply_palette(app: QApplication, tokens: dict[str, str]) -> None:
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(tokens["bg"]))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(tokens["text"]))
    palette.setColor(QPalette.ColorRole.Base, QColor(tokens["surface"]))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(tokens["surface2"]))
    palette.setColor(QPalette.ColorRole.Text, QColor(tokens["text"]))
    palette.setColor(QPalette.ColorRole.Button, QColor(tokens["surface"]))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(tokens["text"]))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(tokens["accent"]))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor(tokens["accentText"]))
    palette.setColor(QPalette.ColorRole.PlaceholderText, QColor(tokens["textFaint"]))
    app.setPalette(palette)


class ThemeManager(QObject):
    theme_changed = pyqtSignal(str, str, bool)  # effective_mode, accent, accent_only

    def __init__(self, app: QApplication) -> None:
        super().__init__()
        self._app = app
        self._mode: ThemeMode = "system"
        self._accent = ACCENT_PRESETS[0]
        self._effective_mode = "light"
        self._tokens: dict[str, str] = resolve_tokens("light", self._accent)
        self._root_widget: QWidget | None = None

    @property
    def mode(self) -> ThemeMode:
        return self._mode

    @property
    def accent(self) -> str:
        return self._accent

    @property
    def effective_mode(self) -> str:
        return self._effective_mode

    @property
    def tokens(self) -> dict[str, str]:
        return dict(self._tokens)

    def set_root_widget(self, widget: QWidget) -> None:
        self._root_widget = widget

    def apply(
        self,
        mode: ThemeMode,
        accent: str | None = None,
        *,
        preview: bool = False,
    ) -> None:
        prev_mode = self._effective_mode
        prev_accent = self._accent

        self._mode = mode
        if accent and accent in ACCENT_PRESETS:
            self._accent = accent

        new_effective = self._effective_mode_from_setting(mode)
        mode_changed = new_effective != prev_mode
        accent_changed = self._accent != prev_accent

        if preview and not mode_changed and not accent_changed:
            return

        self._effective_mode = new_effective
        self._tokens = resolve_tokens(self._effective_mode, self._accent)
        self._app.setStyleSheet(build_stylesheet(self._effective_mode, self._accent))
        apply_palette(self._app, self._tokens)

        if self._root_widget is not None:
            if preview:
                if mode_changed:
                    repolish_widget_tree(self._root_widget)
            elif mode_changed or accent_changed:
                repolish_widget_tree(self._root_widget)

        accent_only = accent_changed and not mode_changed
        self.theme_changed.emit(self._effective_mode, self._accent, accent_only)

    def _effective_mode_from_setting(self, mode: ThemeMode) -> str:
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
