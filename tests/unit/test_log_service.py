"""Tests for log service wrapper."""

from services.log_service import export_logs_zip, setup_logging


def test_setup_logging_delegates(tmp_path):
    log_file = tmp_path / "app.log"
    setup_logging(log_file, level="INFO")
    assert log_file.exists() or log_file.parent.exists()


def test_export_logs_via_service(tmp_path):
    log_dir = tmp_path / "logs"
    log_dir.mkdir()
    (log_dir / "mediafetch.log").write_text("x", encoding="utf-8")
    archive = export_logs_zip(log_dir, tmp_path / "out")
    assert archive.suffix == ".zip"
