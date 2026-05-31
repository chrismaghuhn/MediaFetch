# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for MediaFetch."""

import sys
from pathlib import Path

block_cipher = None
root = Path(SPECPATH).parent.parent
src = root / "src"

a = Analysis(
    [str(src / "main.py")],
    pathex=[str(src)],
    binaries=[],
    datas=[
        (str(src / "ui" / "themes" / "dark.qss"), "themes"),
        (str(src / "ui" / "themes" / "light.qss"), "themes"),
        (str(src / "ui" / "i18n" / "de.json"), "i18n"),
        (str(src / "ui" / "i18n" / "en.json"), "i18n"),
    ],
    hiddenimports=[
        "yt_dlp",
        "yt_dlp.extractor",
        "yt_dlp.postprocessor",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        "PyQt6.QtWebEngineWidgets",
        "PyQt6.QtWebEngineCore",
        "PyQt6.QtNetwork",
        "PyQt6.QtMultimedia",
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# Bundle ffmpeg and yt-dlp if present
bin_dir = root / "resources" / "bin"
for binary in ("ffmpeg.exe", "yt-dlp.exe"):
    path = bin_dir / binary
    if path.is_file():
        a.binaries.append((str(path), "bin", binary))

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="MediaFetch",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(root / "resources" / "icons" / "mediafetch.ico") if (root / "resources" / "icons" / "mediafetch.ico").is_file() else None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="MediaFetch",
)
