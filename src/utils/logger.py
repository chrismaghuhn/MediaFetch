"""Central logging configuration with named loggers."""

from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

MAX_BYTES = 5 * 1024 * 1024
BACKUP_COUNT = 5

LEVEL_MAP = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
}


def get_logger(name: str) -> logging.Logger:
    """Return a namespaced logger under mediafetch.*."""
    if not name.startswith("mediafetch."):
        name = f"mediafetch.{name}"
    return logging.getLogger(name)


def configure_logging(
    log_path: str | Path,
    level: str = "INFO",
    *,
    console: bool = True,
) -> None:
    """Configure root logging with rotating file handler and optional console output."""
    path = Path(log_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    log_level = LEVEL_MAP.get(level.upper(), logging.INFO)
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)

    for handler in root.handlers[:]:
        root.removeHandler(handler)

    formatter = logging.Formatter(LOG_FORMAT, datefmt=LOG_DATE_FORMAT)

    file_handler = RotatingFileHandler(
        path,
        maxBytes=MAX_BYTES,
        backupCount=BACKUP_COUNT,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)
    root.addHandler(file_handler)

    if console:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(logging.WARNING)
        root.addHandler(console_handler)

    root.setLevel(log_level)


def export_logs_zip(log_dir: Path, dest_zip: Path) -> Path:
    """Archive all log files in log_dir into dest_zip (without extension)."""
    import shutil

    log_dir = Path(log_dir)
    dest_zip = Path(dest_zip)
    if dest_zip.suffix.lower() == ".zip":
        dest_zip = dest_zip.with_suffix("")

    files = sorted(log_dir.glob("*.log*"))
    if not files:
        raise FileNotFoundError(f"No log files in {log_dir}")

    staging = dest_zip.parent / f"{dest_zip.name}_staging"
    staging.mkdir(parents=True, exist_ok=True)
    try:
        for f in files:
            shutil.copy2(f, staging / f.name)
        archive = shutil.make_archive(str(dest_zip), "zip", staging)
        return Path(archive)
    finally:
        shutil.rmtree(staging, ignore_errors=True)


def sanitize_url_for_log(url: str, max_len: int = 80) -> str:
    """Redact long URLs for logs — keep host and truncate path."""
    if len(url) <= max_len:
        return url
    return url[: max_len - 3] + "..."
