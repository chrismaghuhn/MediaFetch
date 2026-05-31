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
APP_DIR = DIST / "MediaFetch"
SPEC = BUILD / "mediafetch.spec"
EXTERNAL_BINARIES = ("ffmpeg.exe", "yt-dlp.exe")
APP_ICON = ROOT / "resources" / "icons" / "mediafetch.ico"
APP_ICON_PNG = ROOT / "resources" / "icons" / "mediafetch.png"


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


def find_app_exe() -> Path:
    """Return the onedir launcher (dist/MediaFetch/MediaFetch.exe)."""
    exe = APP_DIR / "MediaFetch.exe"
    if exe.is_file():
        return exe
    legacy = DIST / "MediaFetch.exe"
    if legacy.is_file():
        return legacy
    raise FileNotFoundError("MediaFetch.exe not found under dist/")


def copy_external_binaries(app_dir: Path) -> None:
    """Place FFmpeg and yt-dlp beside the frozen exe for stable exe_dir()/bin/ paths."""
    src_dir = ROOT / "resources" / "bin"
    dest_dir = app_dir / "bin"
    dest_dir.mkdir(parents=True, exist_ok=True)
    copied = 0
    for name in EXTERNAL_BINARIES:
        src = src_dir / name
        if src.is_file():
            shutil.copy2(src, dest_dir / name)
            copied += 1
    if copied:
        print(f"Copied {copied} binary helper(s) to {dest_dir}")
    else:
        print(
            "Warning: no ffmpeg.exe or yt-dlp.exe in resources/bin — "
            "run scripts/setup_dev.ps1 or build/build_release.ps1 first.",
            file=sys.stderr,
        )


def ensure_app_icon() -> None:
    if APP_ICON.is_file():
        return
    if APP_ICON_PNG.is_file():
        print("mediafetch.ico missing — generating from mediafetch.png...")
        subprocess.run([sys.executable, str(ROOT / "scripts" / "generate_icon.py")], check=True)
        return
    print(
        "Warning: no app icon at resources/icons/mediafetch.ico — "
        "PyInstaller and Inno Setup will build without a custom icon.",
        file=sys.stderr,
    )
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

    ensure_app_icon()
    version_info = write_version_info(version)
    run_pyinstaller(version_info)

    try:
        exe = find_app_exe()
    except FileNotFoundError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    copy_external_binaries(exe.parent)
    print(f"Build output: {exe.parent}")
    print(f"Launcher:     {exe}")

    if args.sign:
        sign_exe(exe, args.sign)
        print("Executable signed.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
