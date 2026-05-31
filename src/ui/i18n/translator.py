"""Simple JSON-based translator."""

from __future__ import annotations

import json
import logging
from pathlib import Path

from utils.paths import i18n_dir

logger = logging.getLogger(__name__)


class Translator:
    _instance: Translator | None = None

    def __init__(self) -> None:
        self._language = "de"
        self._strings: dict[str, str] = {}
        self._load("de")

    @classmethod
    def instance(cls) -> Translator:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @property
    def language(self) -> str:
        return self._language

    def set_language(self, language: str) -> None:
        if language not in ("de", "en"):
            language = "de"
        self._language = language
        self._load(language)

    def _load(self, language: str) -> None:
        candidates = [
            i18n_dir() / f"{language}.json",
            Path(__file__).parent / f"{language}.json",
        ]
        for path in candidates:
            if path.is_file():
                try:
                    with path.open(encoding="utf-8") as fh:
                        self._strings = json.load(fh)
                    return
                except (json.JSONDecodeError, OSError) as exc:
                    logger.error("Failed to load translations from %s: %s", path, exc)
        logger.warning("No translation file found for '%s'", language)
        self._strings = {}

    def tr(self, key: str, **kwargs: str | int) -> str:
        text = self._strings.get(key, key)
        if kwargs:
            try:
                return text.format(**kwargs)
            except (KeyError, ValueError):
                return text
        return text


def tr(key: str, **kwargs: str | int) -> str:
    return Translator.instance().tr(key, **kwargs)
