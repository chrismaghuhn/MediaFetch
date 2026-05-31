"""Font loading for Studio theme."""

from __future__ import annotations

import logging
from pathlib import Path

from PyQt6.QtGui import QFontDatabase

from utils.paths import resource_dir

logger = logging.getLogger(__name__)

FONT_FILES = [
    "SpaceGrotesk-Regular.ttf",
    "SpaceGrotesk-Medium.ttf",
    "SpaceGrotesk-SemiBold.ttf",
    "SpaceGrotesk-Bold.ttf",
    "SpaceMono-Regular.ttf",
    "SpaceMono-Bold.ttf",
]


def fonts_dir() -> Path:
    candidates = [
        resource_dir() / "fonts",
        Path(__file__).resolve().parent.parent.parent / "resources" / "fonts",
    ]
    for path in candidates:
        if path.is_dir():
            return path
    return candidates[-1]


def load_application_fonts() -> None:
    directory = fonts_dir()
    if not directory.is_dir():
        logger.warning("Fonts directory not found: %s", directory)
        return

    loaded = 0
    for name in FONT_FILES:
        path = directory / name
        if path.is_file():
            fid = QFontDatabase.addApplicationFont(str(path))
            if fid >= 0:
                loaded += 1
            else:
                logger.warning("Failed to load font: %s", path)

    if loaded:
        logger.info("Loaded %d font files from %s", loaded, directory)
    else:
        logger.warning("No Space Grotesk/Mono fonts loaded — using system fallback")
