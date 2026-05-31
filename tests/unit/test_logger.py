"""Tests for logging utilities."""

import logging

from utils.logger import configure_logging, export_logs_zip, get_logger, sanitize_url_for_log


def test_get_logger_namespace():
    logger = get_logger("core")
    assert logger.name == "mediafetch.core"


def test_configure_logging(tmp_path):
    log_file = tmp_path / "mediafetch.log"
    configure_logging(log_file, level="DEBUG")
    logger = logging.getLogger("mediafetch.test")
    logger.info("hello")
    assert log_file.exists()
    assert "hello" in log_file.read_text(encoding="utf-8")


def test_export_logs_zip(tmp_path):
    log_dir = tmp_path / "logs"
    log_dir.mkdir()
    (log_dir / "mediafetch.log").write_text("line1\n", encoding="utf-8")
    archive = export_logs_zip(log_dir, tmp_path / "export")
    assert archive.suffix == ".zip"
    assert archive.exists()


def test_sanitize_url_for_log():
    long_url = "https://youtube.com/" + "a" * 100
    short = sanitize_url_for_log(long_url, max_len=40)
    assert len(short) <= 40
    assert short.endswith("...")
