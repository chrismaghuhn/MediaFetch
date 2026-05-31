"""Tests for version comparison and package version."""

from utils.version import is_newer_version, parse_version
from version import __version__


def test_parse_version():
    assert parse_version("1.2.3") == (1, 2, 3)
    assert parse_version("v2.0") == (2, 0)


def test_is_newer_version():
    assert is_newer_version("1.0.0", "1.1.0")
    assert not is_newer_version("2.0.0", "1.9.9")


def test_package_version_semver():
    parts = parse_version(__version__)
    assert len(parts) >= 2
