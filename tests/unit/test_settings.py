"""Tests for settings persistence."""

from models.settings import AppSettings
from services.settings_service import SettingsService


def test_default_settings(settings_service):
    s = settings_service.settings
    assert s.language in ("de", "en")
    assert s.max_concurrent >= 1
    assert s.log_level == "INFO"


def test_update_and_persist(settings_service, tmp_app_data):
    settings_service.update(language="en", max_concurrent=3, log_level="DEBUG")
    reloaded = SettingsService()
    assert reloaded.settings.language == "en"
    assert reloaded.settings.max_concurrent == 3
    assert reloaded.settings.log_level == "DEBUG"


def test_from_dict_ignores_unknown_fields():
    data = AppSettings().to_dict()
    data["unknown_field"] = "x"
    settings = AppSettings.from_dict(data)
    assert not hasattr(settings, "unknown_field")


def test_update_skip_and_remind(settings_service):
    settings_service.update(skipped_version="2.0.0", remind_update_after="2099-01-01")
    s = settings_service.settings
    assert s.skipped_version == "2.0.0"
    assert s.remind_update_after == "2099-01-01"
