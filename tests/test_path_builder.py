"""Tests for path builder."""

from core.path_builder import build_output_template, platform_folder_name
from core.platform import Platform


def test_platform_folder_name():
    assert platform_folder_name(Platform.YOUTUBE) == "YouTube"


def test_build_output_template(tmp_path):
    template = build_output_template(tmp_path, Platform.YOUTUBE, "TestChannel")
    assert "YouTube" in template
    assert "TestChannel" in template
    assert "%(title)s" in template
