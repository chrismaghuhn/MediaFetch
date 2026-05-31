"""Integration test for queue download flow with mocked yt-dlp."""

from unittest.mock import MagicMock, patch

import pytest

from core.downloader import Downloader
from core.queue_manager import QueueManager
from core.validators import VideoInfo
from core.platform import Platform
from models.download_item import DownloadItem, DownloadStatus


@pytest.mark.integration
def test_queue_validate_and_complete_flow(qapp, tmp_download_dir, tmp_app_data, mock_ytdlp_info, sample_urls):
    url = sample_urls["youtube_video"]
    video = VideoInfo(
        video_id=mock_ytdlp_info["id"],
        platform=Platform.YOUTUBE,
        title=mock_ytdlp_info["title"],
        uploader=mock_ytdlp_info["uploader"],
        upload_date=mock_ytdlp_info["upload_date"],
        url=url,
    )

    queue = QueueManager(download_dir=str(tmp_download_dir), max_concurrent=1, max_retries=1)

    with patch.object(Downloader, "extract_info", return_value=video):
        item = DownloadItem(url=url)
        queue.add_item(item)
        info = queue.validate_item(item)
        assert info is not None
        assert item.status == DownloadStatus.PENDING

    queue._on_completed(url, video)
    assert queue.items[0].status == DownloadStatus.COMPLETED
    assert queue.items[0].progress_percent == 100.0


@pytest.mark.integration
def test_downloader_extract_to_parse_pipeline(mock_ytdlp_info, sample_urls, tmp_download_dir):
    with patch.object(Downloader, "_init_ytdlp"):
        dl = Downloader(str(tmp_download_dir))
        dl._use_subprocess = False

        mock_ydl = MagicMock()
        mock_ydl.extract_info.return_value = mock_ytdlp_info

        with patch("yt_dlp.YoutubeDL") as ydl_cls:
            ydl_cls.return_value.__enter__.return_value = mock_ydl
            info = dl._extract_info_api(sample_urls["youtube_video"])

        assert info.platform == Platform.YOUTUBE
        assert info.title == "Test Video Title"
