"""Tests for duplicate checker."""

from core.duplicate_checker import DuplicateChecker
from core.platform import Platform
from core.validators import VideoInfo
from services.history_service import HistoryService


def test_find_duplicates(tmp_path):
    db_path = tmp_path / "test.db"
    history = HistoryService(db_path)
    history.add_entry(
        video_id="abc123",
        platform="youtube",
        title="Test Video",
        uploader="Creator",
        upload_date="20240101",
        file_path="/downloads/test.mp4",
        status="success",
        url="https://youtube.com/watch?v=abc123",
    )

    checker = DuplicateChecker(history)
    info = VideoInfo(
        video_id="abc123",
        platform=Platform.YOUTUBE,
        title="Test Video",
        uploader="Creator",
        upload_date="20240101",
        url="https://youtube.com/watch?v=abc123",
    )

    matches = checker.find_duplicates([info])
    assert len(matches) == 1
    assert matches[0].file_path == "/downloads/test.mp4"

    other = VideoInfo(
        video_id="xyz999",
        platform=Platform.YOUTUBE,
        title="Other",
        uploader="Creator",
        upload_date="20240101",
        url="https://youtube.com/watch?v=xyz999",
    )
    assert len(checker.find_duplicates([other])) == 0
