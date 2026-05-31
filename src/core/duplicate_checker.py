"""Duplicate download detection."""

from __future__ import annotations

from dataclasses import dataclass

from core.validators import VideoInfo
from services.history_service import HistoryService


@dataclass
class DuplicateMatch:
    video_info: VideoInfo
    file_path: str


class DuplicateChecker:
    def __init__(self, history_service: HistoryService) -> None:
        self._history = history_service

    def find_duplicates(self, videos: list[VideoInfo]) -> list[DuplicateMatch]:
        matches: list[DuplicateMatch] = []
        for info in videos:
            entry = self._history.find_duplicate(
                info.platform.value,
                info.video_id,
            )
            if entry:
                matches.append(DuplicateMatch(video_info=info, file_path=entry.file_path))
        return matches
