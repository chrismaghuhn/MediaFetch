#!/usr/bin/env python3
"""Reproducible MediaFetch release build."""

from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
BUILD = ROOT / "build"
DIST = ROOT / "dist"
SPEC = BUILD / "mediafetch.spec"


def read_version() -> tuple[str, int]:
    text = (SRC / "version.py").read_text(encoding="utf-8")
    version_match = re.search(r'__version__\s*=\s*"([^"]+)"', text)
    build_match = re.search(r"__build__\s*=\s*(\d+)", text)
    version = version_match.group(1) if version_match else "0.0.0"
    build_num = int(build_match.group(1)) if build_match else 0
    return version, build_num


def write_version_info(version: str) -> Path:
    """Generate Windows VERSIONINFO file for PyInstaller."""
    parts = (version.split(".") + ["0", "0", "0"])[:4]
    file_version = ".".join(parts)
    numeric = ",".join(parts)

    content = f"""# UTF-8
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=({numeric}),
    prodvers=({numeric}),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo([
      StringTable('040904B0', [
        StringStruct('CompanyName', 'MediaFetch'),
        StringStruct('FileDescription', 'MediaFetch Video Downloader'),
        StringStruct('FileVersion', '{file_version}'),
        StringStruct('InternalName', 'MediaFetch'),
        StringStruct('OriginalFilename', 'MediaFetch.exe'),
        StringStruct('ProductName', 'MediaFetch'),
        StringStruct('ProductVersion', '{file_version}'),
      ])
    ]),
    VarFileInfo([VarStruct('Translation', [1033, 1200])])
  ]
)
"""
    path = BUILD / "version_info.txt"
    path.write_text(content, encoding="utf-8")
    return path


def _safe_rmtree(path: Path) -> None:
    """Remove a directory tree; warn instead of failing if files are locked (Windows)."""
    if not path.exists():
        return
    try:
        shutil.rmtree(path)
    except PermissionError:
        print(
            f"Warning: could not remove '{path}' — a file is still in use "
            "(close MediaFetch.exe if it is running). Continuing build…",
            file=sys.stderr,
        )
    except OSError as exc:
        print(f"Warning: could not remove '{path}': {exc}", file=sys.stderr)


def clean() -> None:
    _safe_rmtree(ROOT / "build" / "mediafetch")
    _safe_rmtree(DIST)


def run_pyinstaller(version_info: Path) -> None:
    env = {**os.environ, "MEDIAFETCH_VERSION_INFO": str(version_info)}
    cmd = [sys.executable, "-m", "PyInstaller", str(SPEC), "--noconfirm", "--clean"]
    subprocess.run(cmd, cwd=ROOT, check=True, env=env)


def sign_exe(exe: Path, cert_path: str) -> None:
    """Optional code signing with signtool (requires Windows SDK)."""
    subprocess.run(
        ["signtool", "sign", "/fd", "SHA256", "/f", cert_path, str(exe)],
        check=True,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Build MediaFetch executable")
    parser.add_argument("--no-clean", action="store_true", help="Skip dist/ cleanup")
    parser.add_argument("--sign", metavar="CERT", help="Path to code signing certificate")
    args = parser.parse_args()

    version, _ = read_version()
    print(f"Building MediaFetch {version}")

    if not args.no_clean:
        clean()

    version_info = write_version_info(version)
    run_pyinstaller(version_info)

    exe = DIST / "MediaFetch.exe"
    if not exe.is_file():
        # onedir fallback name
        alt = DIST / "MediaFetch" / "MediaFetch.exe"
        if alt.is_file():
            exe = alt
        else:
            print("ERROR: MediaFetch.exe not found in dist/", file=sys.stderr)
            return 1

    print(f"Build output: {exe}")

    if args.sign:
        sign_exe(exe, args.sign)
        print("Executable signed.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
