"""SQLite-backed download history."""

from __future__ import annotations

import logging
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from models.history_entry import HistoryEntry
from utils.paths import history_db_path

logger = logging.getLogger(__name__)

_SCHEMA = """
CREATE TABLE IF NOT EXISTS downloads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    video_id TEXT NOT NULL,
    platform TEXT NOT NULL,
    title TEXT,
    uploader TEXT,
    upload_date TEXT,
    file_path TEXT,
    status TEXT,
    downloaded_at TEXT,
    url TEXT,
    UNIQUE(platform, video_id)
);
CREATE INDEX IF NOT EXISTS idx_platform ON downloads(platform);
CREATE INDEX IF NOT EXISTS idx_date ON downloads(downloaded_at);
CREATE INDEX IF NOT EXISTS idx_status ON downloads(status);
"""


class HistoryService:
    def __init__(self, db_path: Path | None = None) -> None:
        self._db_path = db_path or history_db_path()
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.executescript(_SCHEMA)

    def add_entry(
        self,
        video_id: str,
        platform: str,
        title: str,
        uploader: str,
        upload_date: str,
        file_path: str,
        status: str,
        url: str,
    ) -> None:
        now = datetime.now(timezone.utc).isoformat()
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO downloads
                    (video_id, platform, title, uploader, upload_date,
                     file_path, status, downloaded_at, url)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(platform, video_id) DO UPDATE SET
                    title=excluded.title,
                    file_path=excluded.file_path,
                    status=excluded.status,
                    downloaded_at=excluded.downloaded_at,
                    url=excluded.url
                """,
                (video_id, platform, title, uploader, upload_date,
                 file_path, status, now, url),
            )

    def find_duplicate(self, platform: str, video_id: str) -> HistoryEntry | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM downloads WHERE platform=? AND video_id=? AND status='success'",
                (platform, video_id),
            ).fetchone()
        if row:
            return self._row_to_entry(row)
        return None

    def search(
        self,
        query: str = "",
        platform: str = "",
        status: str = "",
        date_from: str = "",
        date_to: str = "",
        limit: int = 500,
    ) -> list[HistoryEntry]:
        sql = "SELECT * FROM downloads WHERE 1=1"
        params: list[str | int] = []

        if query:
            sql += " AND (title LIKE ? OR uploader LIKE ? OR url LIKE ?)"
            like = f"%{query}%"
            params.extend([like, like, like])

        if platform and platform != "all":
            sql += " AND platform=?"
            params.append(platform)

        if status and status != "all":
            sql += " AND status=?"
            params.append(status)

        if date_from:
            sql += " AND downloaded_at >= ?"
            params.append(date_from)

        if date_to:
            sql += " AND downloaded_at <= ?"
            params.append(date_to)

        sql += " ORDER BY downloaded_at DESC LIMIT ?"
        params.append(limit)

        with self._connect() as conn:
            rows = conn.execute(sql, params).fetchall()
        return [self._row_to_entry(row) for row in rows]

    @staticmethod
    def _row_to_entry(row: sqlite3.Row) -> HistoryEntry:
        return HistoryEntry(
            id=row["id"],
            video_id=row["video_id"],
            platform=row["platform"],
            title=row["title"] or "",
            uploader=row["uploader"] or "",
            upload_date=row["upload_date"] or "",
            file_path=row["file_path"] or "",
            status=row["status"] or "",
            downloaded_at=row["downloaded_at"] or "",
            url=row["url"] or "",
        )
