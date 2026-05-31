"""Tests for download queue management."""

from unittest.mock import MagicMock, patch

import pytest

from core.queue_manager import QueueManager
from core.validators import VideoInfo
from core.platform import Platform
from models.download_item import DownloadItem, DownloadStatus


@pytest.fixture
def queue_manager(qapp, tmp_download_dir, tmp_app_data):
    return QueueManager(
        download_dir=str(tmp_download_dir),
        max_concurrent=2,
        max_retries=2,
    )


def test_add_and_remove_item(queue_manager, sample_urls):
    item = DownloadItem(url=sample_urls["youtube_video"])
    queue_manager.add_item(item)
    assert len(queue_manager.items) == 1

    queue_manager.remove_item(item.url)
    assert len(queue_manager.items) == 0


def test_add_invalid_url_emits_validation_failed(queue_manager, qtbot):
    signals = []
    queue_manager.validation_failed.connect(lambda url, key: signals.append((url, key)))

    item = DownloadItem(url="https://invalid.example.com")
    queue_manager.add_item(item)

    assert len(queue_manager.items) == 0
    assert signals == [("https://invalid.example.com", "url.invalid")]


def test_save_and_load_queue(queue_manager, tmp_app_data, sample_urls):
    item = DownloadItem(url=sample_urls["youtube_video"], title="Saved")
    queue_manager.add_item(item)
    queue_manager.save_queue()

    q2 = QueueManager(download_dir=str(tmp_app_data / "dl"))
    q2.load_queue()
    assert len(q2.items) == 1
    assert q2.items[0].url == sample_urls["youtube_video"]


def test_retry_on_failure(queue_manager, sample_urls, mocker):
    mocker.patch.object(queue_manager, "_fill_slots")
    item = DownloadItem(url=sample_urls["youtube_video"])
    queue_manager.add_item(item)
    queue_manager._on_failed(item.url, "error.network")

    found = queue_manager.items[0]
    assert found.retry_count == 1
    assert found.status == DownloadStatus.PENDING


def test_failed_after_max_retries(queue_manager, sample_urls, mocker):
    mocker.patch.object(queue_manager, "_fill_slots")
    item = DownloadItem(url=sample_urls["youtube_video"], retry_count=2)
    queue_manager.add_item(item)
    queue_manager._on_failed(item.url, "error.network")

    found = queue_manager.items[0]
    assert found.status == DownloadStatus.FAILED
    assert found.error_key == "error.network"


def test_completed_adds_history(queue_manager, sample_urls):
    item = DownloadItem(url=sample_urls["youtube_video"])
    queue_manager.add_item(item)

    result = VideoInfo(
        video_id="abc",
        platform=Platform.YOUTUBE,
        title="Done",
        uploader="U",
        upload_date="20240101",
        url=sample_urls["youtube_video"],
    )
    queue_manager._on_completed(item.url, result)

    assert queue_manager.items[0].status == DownloadStatus.COMPLETED


def test_clear_queue(queue_manager, sample_urls):
    queue_manager.add_item(DownloadItem(url=sample_urls["youtube_video"]))
    queue_manager.add_item(DownloadItem(url=sample_urls["instagram_reel"]))
    queue_manager.clear()
    assert len(queue_manager.items) == 0
