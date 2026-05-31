"""Settings persistence service."""

from __future__ import annotations

import json
import logging

from models.settings import AppSettings
from utils.paths import settings_path

logger = logging.getLogger(__name__)


class SettingsService:
    def __init__(self) -> None:
        self._settings = AppSettings()
        self.load()

    @property
    def settings(self) -> AppSettings:
        return self._settings

    def load(self) -> AppSettings:
        path = settings_path()
        if not path.is_file():
            self._settings = AppSettings()
            self.save()
            return self._settings
        try:
            with path.open(encoding="utf-8") as fh:
                data = json.load(fh)
            self._settings = AppSettings.from_dict(data)
        except (json.JSONDecodeError, OSError, TypeError) as exc:
            logger.warning("Could not load settings, using defaults: %s", exc)
            self._settings = AppSettings()
        return self._settings

    def save(self) -> None:
        path = settings_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as fh:
            json.dump(self._settings.to_dict(), fh, indent=2, ensure_ascii=False)

    def update(self, **kwargs) -> AppSettings:
        for key, value in kwargs.items():
            if hasattr(self._settings, key):
                setattr(self._settings, key, value)
        self.save()
        return self._settings
