#!/usr/bin/env python3
"""Regenerate resources/icons/mediafetch.ico from mediafetch.png."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PNG = ROOT / "resources" / "icons" / "mediafetch.png"
ICO = ROOT / "resources" / "icons" / "mediafetch.ico"


def main() -> int:
    try:
        from PIL import Image
    except ImportError:
        print("Install Pillow first: python -m pip install pillow")
        return 1

    if not PNG.is_file():
        print(f"Missing source icon: {PNG}")
        return 1

    img = Image.open(PNG).convert("RGBA")
    img.save(ICO, format="ICO", sizes=[(size, size) for size in (16, 32, 48, 64, 128, 256)])
    print(f"Wrote {ICO}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
