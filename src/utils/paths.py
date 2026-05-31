"""Application path helpers."""

from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path


APP_NAME = "MediaFetch"


def is_frozen() -> bool:
    return getattr(sys, "frozen", False)


def exe_dir() -> Path:
    if is_frozen():
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent.parent


def resource_dir() -> Path:
    if is_frozen():
        return Path(getattr(sys, "_MEIPASS", exe_dir()))
    # Development: resources/ next to src/
    dev_resources = exe_dir() / "resources"
    if dev_resources.is_dir():
        return dev_resources
    return exe_dir()


def app_data_dir() -> Path:
    base = os.environ.get("APPDATA")
    if not base:
        base = str(Path.home() / "AppData" / "Roaming")
    path = Path(base) / APP_NAME
    path.mkdir(parents=True, exist_ok=True)
    return path


def default_download_dir() -> Path:
    home = Path.home()
    path = home / "Downloads" / APP_NAME
    path.mkdir(parents=True, exist_ok=True)
    return path


def default_log_dir() -> Path:
    path = app_data_dir() / "logs"
    path.mkdir(parents=True, exist_ok=True)
    return path


def settings_path() -> Path:
    return app_data_dir() / "settings.json"


def queue_path() -> Path:
    return app_data_dir() / "queue.json"


def history_db_path() -> Path:
    return app_data_dir() / "history.db"


def ffmpeg_path() -> Path | None:
    candidates = [
        exe_dir() / "bin" / "ffmpeg.exe",
        resource_dir() / "bin" / "ffmpeg.exe",
        exe_dir() / "ffmpeg.exe",
    ]
    for candidate in candidates:
        if candidate.is_file():
            return candidate

    on_path = shutil.which("ffmpeg")
    if on_path:
        return Path(on_path)
    return None


def ytdlp_exe_path() -> Path | None:
    candidates = [
        exe_dir() / "bin" / "yt-dlp.exe",
        resource_dir() / "bin" / "yt-dlp.exe",
    ]
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    return None


def i18n_dir() -> Path:
    candidates = [
        resource_dir() / "i18n",
        Path(__file__).resolve().parent.parent / "ui" / "i18n",
    ]
    for path in candidates:
        if path.is_dir():
            return path
    return candidates[-1]


def themes_dir() -> Path:
    candidates = [
        resource_dir() / "themes",
        Path(__file__).resolve().parent.parent / "ui" / "themes",
    ]
    for path in candidates:
        if path.is_dir():
            return path
    return candidates[-1]


def app_icon_path() -> Path | None:
    """Return the application icon (.ico preferred, .png fallback)."""
    candidates = [
        resource_dir() / "icons" / "mediafetch.ico",
        resource_dir() / "icons" / "mediafetch.png",
        exe_dir() / "resources" / "icons" / "mediafetch.ico",
        exe_dir() / "resources" / "icons" / "mediafetch.png",
    ]
    for path in candidates:
        if path.is_file():
            return path
    return None
