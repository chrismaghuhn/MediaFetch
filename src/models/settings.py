"""Application settings model."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Literal

from utils.paths import default_download_dir, default_log_dir


ThemeMode = Literal["system", "dark", "light"]
Language = Literal["de", "en"]


@dataclass
class AppSettings:
    language: Language = "de"
    theme: ThemeMode = "system"
    download_dir: str = field(default_factory=lambda: str(default_download_dir()))
    max_concurrent: int = 2
    max_retries: int = 3
    default_quality: int = 1080
    include_subtitles: bool = False
    log_path: str = field(default_factory=lambda: str(default_log_dir() / "mediafetch.log"))
    restore_queue_on_startup: bool = True
    check_updates_on_startup: bool = True
    accent_color: str = "#ff5436"
    github_repo: str = "ChrismagHuhn/MediaFetch"
    log_level: str = "INFO"
    skipped_version: str = ""
    remind_update_after: str = ""

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> AppSettings:
        known = {f.name for f in cls.__dataclass_fields__.values()}  # type: ignore[attr-defined]
        filtered = {k: v for k, v in data.items() if k in known}
        return cls(**filtered)
