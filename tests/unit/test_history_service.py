"""Tests for history service."""

from services.history_service import HistoryService


def test_add_and_search(tmp_app_data):
    history = HistoryService()
    history.add_entry(
        video_id="vid1",
        platform="youtube",
        title="Test",
        uploader="User",
        upload_date="20240101",
        file_path="/tmp/v.mp4",
        status="success",
        url="https://youtube.com/watch?v=vid1",
    )
    results = history.search(query="Test")
    assert len(results) >= 1
    assert results[0].title == "Test"


def test_search_by_platform(tmp_app_data):
    history = HistoryService()
    history.add_entry(
        video_id="v2",
        platform="tiktok",
        title="TikTok Vid",
        uploader="u",
        upload_date="",
        file_path="",
        status="success",
        url="https://tiktok.com/x",
    )
    results = history.search(platform="tiktok")
    assert all(e.platform == "tiktok" for e in results)
