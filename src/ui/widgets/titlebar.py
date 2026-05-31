"""Application titlebar with brand, pill navigation, and actions."""

from __future__ import annotations

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QPushButton, QWidget

from ui.i18n.translator import tr
from ui.widgets.brand_widget import BrandWidget
from ui.widgets.styled_button import nav_button, styled_button


class Titlebar(QFrame):
    tab_changed = pyqtSignal(int)
    updates_requested = pyqtSignal()
    quit_requested = pyqtSignal()

    TAB_QUEUE = 0
    TAB_HISTORY = 1
    TAB_SETTINGS = 2

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("Titlebar")
        self._nav_buttons: list[QPushButton] = []
        self._active_tab = 0
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(18, 6, 18, 6)
        layout.setSpacing(16)

        self._brand = BrandWidget()
        layout.addWidget(self._brand)

        nav_container = QWidget()
        nav_layout = QHBoxLayout(nav_container)
        nav_layout.setContentsMargins(0, 0, 0, 0)
        nav_layout.setSpacing(6)

        for idx, key in enumerate(("nav.queue", "nav.history", "nav.settings")):
            btn = nav_button(tr(key), active=(idx == 0))
            btn.clicked.connect(lambda checked, i=idx: self.set_active_tab(i))
            self._nav_buttons.append(btn)
            nav_layout.addWidget(btn)

        layout.addStretch()
        layout.addWidget(nav_container)
        layout.addStretch()

        self._update_btn = styled_button("?", variant="ghost")
        self._update_btn.setToolTip(tr("menu.check_updates"))
        self._update_btn.clicked.connect(self.updates_requested.emit)
        layout.addWidget(self._update_btn)

        self._quit_btn = styled_button("×", variant="ghost")
        self._quit_btn.setToolTip(tr("menu.quit"))
        self._quit_btn.clicked.connect(self.quit_requested.emit)
        layout.addWidget(self._quit_btn)

    def set_active_tab(self, index: int) -> None:
        self._active_tab = index
        for i, btn in enumerate(self._nav_buttons):
            active = i == index
            btn.setProperty("active", "true" if active else "false")
            btn.setChecked(active)
            btn.style().unpolish(btn)
            btn.style().polish(btn)
        self.tab_changed.emit(index)

    def retranslate(self) -> None:
        self._brand.retranslate()
        keys = ("nav.queue", "nav.history", "nav.settings")
        for btn, key in zip(self._nav_buttons, keys):
            btn.setText(tr(key))
        self._update_btn.setToolTip(tr("menu.check_updates"))
        self._quit_btn.setToolTip(tr("menu.quit"))
