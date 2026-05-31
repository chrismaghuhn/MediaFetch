"""Logging service — thin wrapper around utils.logger for backward compatibility."""

from __future__ import annotations

from pathlib import Path

from utils.logger import configure_logging, export_logs_zip

__all__ = ["setup_logging", "export_logs_zip"]


def setup_logging(log_path: str | Path, level: str = "INFO") -> None:
    configure_logging(log_path, level=level)
