"""Download queue orchestration with QThread workers."""

from __future__ import annotations

import json
import logging
from pathlib import Path

from PyQt6.QtCore import QObject, pyqtSignal

from core.downloader import Downloader
from core.validators import VideoInfo, validate_url
from models.download_item import DownloadItem, DownloadStatus
from services.history_service import HistoryService
from utils.paths import queue_path
from workers.download_worker import DownloadWorker

logger = logging.getLogger(__name__)


class QueueManager(QObject):
    item_added = pyqtSignal(object)
    item_updated = pyqtSignal(object)
    item_removed = pyqtSignal(str)
    queue_cleared = pyqtSignal()
    validation_failed = pyqtSignal(str, str)  # url, error_key

    def __init__(
        self,
        download_dir: str,
        max_concurrent: int = 2,
        max_retries: int = 3,
        history_service: HistoryService | None = None,
    ) -> None:
        super().__init__()
        self._download_dir = download_dir
        self._max_concurrent = max_concurrent
        self._max_retries = max_retries
        self._history = history_service or HistoryService()
        self._items: list[DownloadItem] = []
        self._active_workers: dict[str, DownloadWorker] = {}
        self._paused = False
        self._downloader = Downloader(download_dir)

    @property
    def items(self) -> list[DownloadItem]:
        return list(self._items)

    def set_limits(self, max_concurrent: int, max_retries: int) -> None:
        self._max_concurrent = max_concurrent
        self._max_retries = max_retries

    def set_download_dir(self, download_dir: str) -> None:
        self._download_dir = download_dir
        self._downloader = Downloader(download_dir)

    def add_item(self, item: DownloadItem) -> None:
        valid, error_key = validate_url(item.url)
        if not valid:
            self.validation_failed.emit(item.url, error_key)
            return
        self._items.append(item)
        self.item_added.emit(item)
        self.save_queue()

    def add_items(self, items: list[DownloadItem]) -> None:
        for item in items:
            self.add_item(item)

    def remove_item(self, url: str) -> None:
        worker = self._active_workers.pop(url, None)
        if worker and worker.isRunning():
            worker.terminate()
            worker.wait(3000)

        self._items = [i for i in self._items if i.url != url]
        self.item_removed.emit(url)
        self.save_queue()

    def clear(self) -> None:
        for url in list(self._active_workers):
            worker = self._active_workers.pop(url)
            if worker.isRunning():
                worker.terminate()
                worker.wait(3000)
        self._items.clear()
        self.queue_cleared.emit()
        self.save_queue()

    def validate_item(self, item: DownloadItem) -> VideoInfo | None:
        item.status = DownloadStatus.VALIDATING
        self.item_updated.emit(item)
        try:
            info = self._downloader.extract_info(item.url)
            item.video_info = info
            item.title = info.title
            item.platform = info.platform
            item.status = DownloadStatus.PENDING
            self.item_updated.emit(item)
            return info
        except Exception as exc:
            logger.exception("Validation failed for %s", item.url)
            item.status = DownloadStatus.FAILED
            item.error_key = str(exc) if str(exc).startswith("error.") else "error.generic"
            self.item_updated.emit(item)
            self.validation_failed.emit(item.url, item.error_key)
            return None

    def start(self) -> None:
        self._paused = False
        self._fill_slots()

    def pause(self) -> None:
        self._paused = True

    def _fill_slots(self) -> None:
        if self._paused:
            return

        active_count = len(self._active_workers)
        if active_count >= self._max_concurrent:
            return

        pending = [
            i for i in self._items
            if i.status in (DownloadStatus.PENDING, DownloadStatus.VALIDATING)
            and i.url not in self._active_workers
        ]

        slots = self._max_concurrent - active_count
        for item in pending[:slots]:
            if item.status == DownloadStatus.PENDING and not item.video_info:
                info = self.validate_item(item)
                if not info:
                    continue

            self._start_worker(item)

    def _start_worker(self, item: DownloadItem) -> None:
        item.status = DownloadStatus.DOWNLOADING
        self.item_updated.emit(item)

        worker = DownloadWorker(item, self._download_dir)
        worker.progress.connect(self._on_progress)
        worker.completed.connect(self._on_completed)
        worker.failed.connect(self._on_failed)
        worker.finished.connect(lambda: self._cleanup_worker(item.url))

        self._active_workers[item.url] = worker
        worker.start()

    def _cleanup_worker(self, url: str) -> None:
        self._active_workers.pop(url, None)
        self._fill_slots()

    def _on_progress(self, url: str, percent: float, speed: str, eta: str) -> None:
        item = self._find_item(url)
        if not item:
            return
        item.progress_percent = percent
        item.speed = speed
        item.eta = eta
        self.item_updated.emit(item)

    def _on_completed(self, url: str, result: VideoInfo) -> None:
        item = self._find_item(url)
        if not item:
            return

        item.status = DownloadStatus.COMPLETED
        item.progress_percent = 100.0
        item.title = result.title
        self.item_updated.emit(item)

        self._history.add_entry(
            video_id=result.video_id,
            platform=result.platform.value,
            title=result.title,
            uploader=result.uploader,
            upload_date=result.upload_date,
            file_path=item.file_path,
            status="success",
            url=url,
        )
        self.save_queue()
        self._fill_slots()

    def _on_failed(self, url: str, error_key: str) -> None:
        item = self._find_item(url)
        if not item:
            return

        item.retry_count += 1
        if item.retry_count <= self._max_retries:
            logger.info("Retrying %s (attempt %d)", url, item.retry_count)
            item.status = DownloadStatus.PENDING
            self.item_updated.emit(item)
            self._fill_slots()
            return

        item.status = DownloadStatus.FAILED
        item.error_key = error_key
        self.item_updated.emit(item)

        if item.video_info:
            self._history.add_entry(
                video_id=item.video_info.video_id,
                platform=item.video_info.platform.value,
                title=item.video_info.title,
                uploader=item.video_info.uploader,
                upload_date=item.video_info.upload_date,
                file_path="",
                status="failed",
                url=url,
            )
        self.save_queue()
        self._fill_slots()

    def _find_item(self, url: str) -> DownloadItem | None:
        for item in self._items:
            if item.url == url:
                return item
        return None

    def save_queue(self) -> None:
        path = queue_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        serializable = [i.to_dict() for i in self._items if i.status != DownloadStatus.COMPLETED]
        with path.open("w", encoding="utf-8") as fh:
            json.dump(serializable, fh, indent=2, ensure_ascii=False)

    def load_queue(self) -> None:
        path = queue_path()
        if not path.is_file():
            return
        try:
            with path.open(encoding="utf-8") as fh:
                data = json.load(fh)
            for entry in data:
                item = DownloadItem.from_dict(entry)
                if item.status not in (DownloadStatus.COMPLETED, DownloadStatus.DOWNLOADING):
                    item.status = DownloadStatus.PENDING
                self._items.append(item)
                self.item_added.emit(item)
        except (json.JSONDecodeError, OSError, KeyError) as exc:
            logger.warning("Could not load queue: %s", exc)

    def clear_saved_queue(self) -> None:
        path = queue_path()
        if path.is_file():
            path.unlink()
