"""Network connectivity check."""

from __future__ import annotations

import socket


def has_internet(timeout: float = 3.0) -> bool:
    try:
        socket.create_connection(("1.1.1.1", 53), timeout=timeout)
        return True
    except OSError:
        return False
