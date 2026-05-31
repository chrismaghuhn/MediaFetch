"""Styled push button with variant property."""

from __future__ import annotations

from PyQt6.QtWidgets import QPushButton


def styled_button(text: str = "", variant: str = "secondary") -> QPushButton:
    btn = QPushButton(text)
    btn.setProperty("variant", variant)
    btn.style().unpolish(btn)
    btn.style().polish(btn)
    return btn


def nav_button(text: str = "", active: bool = False) -> QPushButton:
    btn = QPushButton(text)
    btn.setProperty("nav", "true")
    btn.setProperty("active", "true" if active else "false")
    btn.setCheckable(True)
    btn.setChecked(active)
    btn.style().unpolish(btn)
    btn.style().polish(btn)
    return btn
