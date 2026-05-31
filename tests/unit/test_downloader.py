"""Tests for yt-dlp downloader wrapper."""

from unittest.mock import MagicMock, patch

import pytest

from core.downloader import Downloader
from core.format_selector import DownloadOptions
from core.validators import parse_video_info


@pytest.fixture
def downloader(tmp_download_dir):
    with patch.object(Downloader, "_init_ytdlp"):
        dl = Downloader(str(tmp_download_dir))
        dl._use_subprocess = False
        return dl


def test_extract_info_api(downloader, mock_ytdlp_info, sample_urls):
    mock_ydl = MagicMock()
    mock_ydl.extract_info.return_value = mock_ytdlp_info

    with patch("yt_dlp.YoutubeDL") as ydl_cls:
        ydl_cls.return_value.__enter__.return_value = mock_ydl
        info = downloader._extract_info_api(sample_urls["youtube_video"])

    assert info.title == "Test Video Title"
    assert info.video_id == "dQw4w9WgXcQ"


def test_download_api_maps_errors(downloader, sample_urls):
    with patch("yt_dlp.YoutubeDL") as ydl_cls:
        ydl_cls.return_value.__enter__.return_value.extract_info.side_effect = Exception("network timeout")
        with pytest.raises(RuntimeError, match="error.network"):
            downloader._download_api(sample_urls["youtube_video"], DownloadOptions(), None, None)


def test_build_ydl_opts_includes_format(downloader):
    from core.platform import Platform
    from core.validators import VideoInfo

    video = VideoInfo(
        video_id="1",
        platform=Platform.YOUTUBE,
        title="T",
        uploader="U",
        upload_date="",
        url="https://youtube.com/watch?v=1",
    )
    opts = downloader._build_ydl_opts(DownloadOptions(quality=720), video, None)
    assert "format" in opts
    assert "outtmpl" in opts


def test_parse_video_info_from_fixture(mock_ytdlp_info, sample_urls):
    info = parse_video_info(sample_urls["youtube_video"], mock_ytdlp_info)
    assert info.uploader == "TestChannel"
