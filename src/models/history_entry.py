"""Download history entry model."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class HistoryEntry:
    id: int | None
    video_id: str
    platform: str
    title: str
    uploader: str
    upload_date: str
    file_path: str
    status: str
    downloaded_at: str
    url: str
