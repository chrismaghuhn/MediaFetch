"""Tests for network service."""

from unittest.mock import patch

from services.network_service import has_internet


def test_has_internet_true():
    with patch("socket.create_connection"):
        assert has_internet() is True


def test_has_internet_false():
    with patch("socket.create_connection", side_effect=OSError("offline")):
        assert has_internet() is False
