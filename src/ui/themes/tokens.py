"""Studio design tokens and dynamic QSS generation."""

from __future__ import annotations

from functools import lru_cache

ACCENT_PRESETS = ["#ff5436", "#7a5ae0", "#1f9d6b", "#2f6fe0", "#e8911c"]

STUDIO_LIGHT = {
    "bg": "#fbf6f0",
    "titlebar": "#fffaf4",
    "titleText": "#241710",
    "surface": "#ffffff",
    "surface2": "#f6ede2",
    "surfaceHover": "#f0e4d6",
    "border": "#ece0d2",
    "borderStrong": "#ddccb8",
    "text": "#241710",
    "textMuted": "#7d6e5f",
    "textFaint": "#a99a8a",
    "accentText": "#ffffff",
    "success": "#1f9d57",
    "successSoft": "#e2f6ea",
    "danger": "#dc3a4b",
    "dangerSoft": "#fce9eb",
    "warn": "#e08a1e",
    "track": "#f0e4d6",
    "navActive": "#f6ede2",
    "scrollbar": "rgba(150,140,130,0.32)",
    "scrollbarHover": "rgba(150,140,130,0.5)",
}

STUDIO_DARK = {
    "bg": "#14100c",
    "titlebar": "#1c1612",
    "titleText": "#f5ebe0",
    "surface": "#221c17",
    "surface2": "#2a221c",
    "surfaceHover": "#332a23",
    "border": "#3d332b",
    "borderStrong": "#4d4036",
    "text": "#f5ebe0",
    "textMuted": "#b8a898",
    "textFaint": "#8a7a6a",
    "accentText": "#ffffff",
    "success": "#3ecf7a",
    "successSoft": "#1a3d28",
    "danger": "#f06070",
    "dangerSoft": "#3d1a20",
    "warn": "#f0a840",
    "track": "#332a23",
    "navActive": "#2a221c",
    "scrollbar": "rgba(150,140,130,0.25)",
    "scrollbarHover": "rgba(150,140,130,0.45)",
}

RADIUS = 20
RADIUS_SM = 13
PAD = 18
CONTROL_H = 38


def _darken_hex(hex_color: str, factor: float = 0.88) -> str:
    hex_color = hex_color.lstrip("#")
    r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    r = max(0, int(r * factor))
    g = max(0, int(g * factor))
    b = max(0, int(b * factor))
    return f"#{r:02x}{g:02x}{b:02x}"


def _soft_hex(hex_color: str, alpha: float = 0.15) -> str:
    hex_color = hex_color.lstrip("#")
    r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"


def _soft_text_hex(hex_color: str) -> str:
    return _darken_hex(hex_color, 0.75)


def resolve_tokens(mode: str, accent: str) -> dict[str, str]:
    base = STUDIO_DARK if mode == "dark" else STUDIO_LIGHT
    if accent not in ACCENT_PRESETS:
        accent = ACCENT_PRESETS[0]
    tokens = dict(base)
    tokens["accent"] = accent
    tokens["accentHover"] = _darken_hex(accent, 0.88)
    tokens["accentSoft"] = _soft_hex(accent, 0.18 if mode == "light" else 0.22)
    tokens["accentSoftText"] = _soft_text_hex(accent)
    tokens["selection"] = _soft_hex(accent, 0.28 if mode == "light" else 0.35)
    tokens["radius"] = str(RADIUS)
    tokens["radiusSm"] = str(RADIUS_SM)
    tokens["pad"] = str(PAD)
    tokens["controlH"] = str(CONTROL_H)
    return tokens


def build_stylesheet(mode: str, accent: str = "#ff5436") -> str:
    return _build_stylesheet_cached(mode, accent)


@lru_cache(maxsize=32)
def _build_stylesheet_cached(mode: str, accent: str) -> str:
    t = resolve_tokens(mode, accent)
    return f"""
* {{
    font-family: "Space Grotesk", "Segoe UI", sans-serif;
    font-size: 14px;
}}

QMainWindow, QWidget {{
    background-color: {t["bg"]};
    color: {t["text"]};
}}

QScrollArea, QStackedWidget {{
    background-color: {t["bg"]};
    border: none;
}}

QWidget#Root {{
    background-color: {t["bg"]};
    color: {t["text"]};
}}

QWidget[mono="true"], QLabel[mono="true"], QPlainTextEdit, QTextEdit[mono="true"] {{
    font-family: "Space Mono", "Consolas", monospace;
}}

QFrame#Titlebar {{
    background-color: {t["titlebar"]};
    border-bottom: 1px solid {t["border"]};
    min-height: 52px;
    max-height: 52px;
}}

QFrame#Panel {{
    background-color: {t["surface"]};
    border: 1px solid {t["border"]};
    border-radius: {t["radius"]}px;
}}

QFrame#HeroPanel {{
    background-color: {t["surface"]};
    border: 1px solid {t["border"]};
    border-radius: {t["radius"]}px;
}}

QFrame#HeroHeader {{
    background-color: {t["surface2"]};
    border-top-left-radius: {t["radius"]}px;
    border-top-right-radius: {t["radius"]}px;
    border-bottom: 1px solid {t["border"]};
}}

QLabel#BrandName {{
    font-size: 15px;
    font-weight: 700;
    color: {t["titleText"]};
}}

QLabel#BrandBadge {{
    background-color: {t["accent"]};
    color: {t["accentText"]};
    border-radius: 8px;
    font-weight: 700;
    font-size: 13px;
}}

QLabel#PageTitle {{
    font-size: 22px;
    font-weight: 700;
    color: {t["text"]};
}}

QLabel#PageSubtitle, QLabel.muted {{
    color: {t["textMuted"]};
    font-size: 13px;
}}

QLabel.error {{
    color: {t["danger"]};
}}

QLabel.success {{
    color: {t["success"]};
}}

QLabel#SectionLabel {{
    font-size: 11px;
    font-weight: 700;
    color: {t["textFaint"]};
    text-transform: uppercase;
    letter-spacing: 1px;
}}

QPushButton {{
    min-height: {t["controlH"]}px;
    padding: 0 16px;
    border-radius: {t["radiusSm"]}px;
    font-weight: 600;
    border: none;
}}

QPushButton[variant="primary"] {{
    background-color: {t["accent"]};
    color: {t["accentText"]};
}}
QPushButton[variant="primary"]:hover {{
    background-color: {t["accentHover"]};
}}
QPushButton[variant="primary"]:disabled {{
    background-color: {t["border"]};
    color: {t["textFaint"]};
}}

QPushButton[variant="secondary"] {{
    background-color: {t["surface"]};
    color: {t["text"]};
    border: 1px solid {t["border"]};
}}
QPushButton[variant="secondary"]:hover {{
    background-color: {t["surfaceHover"]};
}}

QPushButton[variant="ghost"] {{
    background-color: transparent;
    color: {t["textMuted"]};
    border: none;
}}
QPushButton[variant="ghost"]:hover {{
    background-color: {t["surfaceHover"]};
    color: {t["text"]};
}}

QPushButton[variant="danger"] {{
    background-color: transparent;
    color: {t["danger"]};
    border: none;
    min-height: 32px;
    min-width: 32px;
    padding: 0;
}}
QPushButton[variant="danger"]:hover {{
    background-color: {t["dangerSoft"]};
}}

QPushButton[nav="true"] {{
    background-color: {t["surface"]};
    color: {t["textMuted"]};
    border: 1px solid {t["border"]};
    border-radius: 999px;
    min-height: 40px;
    padding: 0 18px;
}}
QPushButton[nav="true"]:hover {{
    background-color: {t["surfaceHover"]};
    color: {t["text"]};
}}
QPushButton[nav="true"][active="true"] {{
    background-color: {t["accent"]};
    color: {t["accentText"]};
    border-color: {t["accent"]};
}}

QPushButton[accentSwatch="true"] {{
    min-width: 36px;
    max-width: 36px;
    min-height: 36px;
    max-height: 36px;
    border-radius: 18px;
    border: 2px solid {t["border"]};
    padding: 0;
}}
QPushButton[accentSwatch="true"][selected="true"] {{
    border: 3px solid {t["text"]};
}}

QLineEdit, QSpinBox, QComboBox {{
    background-color: {t["surface"]};
    color: {t["text"]};
    border: 1px solid {t["border"]};
    border-radius: {t["radiusSm"]}px;
    padding: 8px 12px;
    min-height: {t["controlH"]}px;
    selection-background-color: {t["accentSoft"]};
}}
QLineEdit:focus, QSpinBox:focus, QComboBox:focus {{
    border-color: {t["accent"]};
}}

QPlainTextEdit, QTextEdit {{
    background-color: {t["bg"]};
    color: {t["text"]};
    border: 1px dashed {t["borderStrong"]};
    border-radius: {t["radiusSm"]}px;
    padding: 11px 13px;
    font-family: "Space Mono", "Consolas", monospace;
    font-size: 13px;
    selection-background-color: {t["accentSoft"]};
}}
QPlainTextEdit:focus, QTextEdit:focus {{
    border: 1px solid {t["accent"]};
}}

QComboBox::drop-down {{
    border: none;
    width: 24px;
}}
QComboBox QAbstractItemView {{
    background-color: {t["surface"]};
    color: {t["text"]};
    border: 1px solid {t["border"]};
    selection-background-color: {t["accentSoft"]};
}}

QTableWidget {{
    background-color: {t["surface"]};
    alternate-background-color: {t["bg"]};
    color: {t["text"]};
    border: none;
    gridline-color: {t["border"]};
}}
QHeaderView::section {{
    background-color: {t["surface2"]};
    color: {t["textMuted"]};
    font-size: 11px;
    font-weight: 700;
    padding: 10px 8px;
    border: none;
    border-bottom: 1px solid {t["border"]};
    border-right: 1px solid {t["border"]};
}}
QTableWidget::item {{
    padding: 8px;
    min-height: 40px;
}}
QTableWidget::item:selected {{
    background-color: {t["accentSoft"]};
    color: {t["text"]};
}}

QProgressBar {{
    background-color: {t["track"]};
    border: none;
    border-radius: 3px;
    max-height: 6px;
    min-height: 6px;
    text-align: center;
    color: transparent;
}}
QProgressBar::chunk {{
    background-color: {t["accent"]};
    border-radius: 3px;
}}

QProgressBar[status="completed"]::chunk {{
    background-color: {t["success"]};
}}
QProgressBar[status="failed"]::chunk {{
    background-color: {t["danger"]};
}}

QScrollArea {{
    border: none;
    background: transparent;
}}
QScrollBar:vertical {{
    background: transparent;
    width: 10px;
    margin: 4px 2px;
}}
QScrollBar::handle:vertical {{
    background: {t["scrollbar"]};
    border-radius: 5px;
    min-height: 30px;
}}
QScrollBar::handle:vertical:hover {{
    background: {t["scrollbarHover"]};
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}
QScrollBar:horizontal {{
    background: transparent;
    height: 10px;
}}
QScrollBar::handle:horizontal {{
    background: {t["scrollbar"]};
    border-radius: 5px;
    min-width: 30px;
}}

QCheckBox {{
    spacing: 8px;
    color: {t["text"]};
}}
QCheckBox::indicator {{
    width: 18px;
    height: 18px;
    border-radius: 4px;
    border: 1px solid {t["borderStrong"]};
    background: {t["surface"]};
}}
QCheckBox::indicator:checked {{
    background: {t["accent"]};
    border-color: {t["accent"]};
}}

QGroupBox {{
    border: 1px solid {t["border"]};
    border-radius: {t["radius"]}px;
    margin-top: 16px;
    padding-top: 20px;
    background: {t["surface"]};
    font-weight: 600;
    color: {t["text"]};
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    left: 16px;
    padding: 0 6px;
    color: {t["textFaint"]};
    font-size: 11px;
    font-weight: 700;
}}

QDialog {{
    background-color: {t["bg"]};
    color: {t["text"]};
}}

QMessageBox {{
    background-color: {t["surface"]};
}}

QFrame#QueueRow {{
    background: transparent;
    border-bottom: 1px solid {t["border"]};
}}

QLabel#PlatformBadge {{
    min-width: 32px;
    max-width: 32px;
    min-height: 32px;
    max-height: 32px;
    border-radius: 8px;
    font-weight: 700;
    font-size: 13px;
}}

QLabel#StatusPill {{
    border-radius: 999px;
    padding: 4px 10px;
    font-size: 12px;
    font-weight: 600;
}}

QStatusBar {{
    background: {t["titlebar"]};
    color: {t["textMuted"]};
    border-top: 1px solid {t["border"]};
}}
"""
