"""MediaFetch entry point."""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure src is on path for both dev and frozen builds
_src = Path(__file__).resolve().parent
if str(_src) not in sys.path:
    sys.path.insert(0, str(_src))

from app import MediaFetchApp  # noqa: E402


def main() -> int:
    application = MediaFetchApp()
    return application.run()


if __name__ == "__main__":
    sys.exit(main())
