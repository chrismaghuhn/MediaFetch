# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for MediaFetch — one-dir, windowed, PyQt6.

FFmpeg and yt-dlp are copied to {app}/bin/ by scripts/build.py after PyInstaller
runs so paths.resolve via exe_dir()/bin/ stays stable (one-file temp dirs do not).
"""

import os
import sys
from pathlib import Path

block_cipher = None
# SPECPATH is the directory containing this spec file (build/)
root = Path(SPECPATH).parent
src = root / "src"

# PyQt6: collect runtime libs + plugin data (avoid full QML/WebEngine tree)
try:
    from PyInstaller.utils.hooks import collect_data_files, collect_dynamic_libs

    pyqt6_binaries = collect_dynamic_libs("PyQt6")
    pyqt6_datas = collect_data_files(
        "PyQt6",
        subdir="Qt6/plugins",
        includes=["platforms/*.dll", "styles/*.dll", "imageformats/*.dll"],
    )
    pyqt6_hidden = ["PyQt6.sip"]
except Exception:
    pyqt6_datas, pyqt6_binaries, pyqt6_hidden = [], [], []

version_info = os.environ.get("MEDIAFETCH_VERSION_INFO")
if version_info and not Path(version_info).is_file():
    version_info = None

a = Analysis(
    [str(src / "main.py")],
    pathex=[str(src)],
    binaries=list(pyqt6_binaries),
    datas=[
        (str(src / "ui" / "i18n" / "de.json"), "i18n"),
        (str(src / "ui" / "i18n" / "en.json"), "i18n"),
        (str(root / "resources" / "fonts"), "fonts"),
        (str(root / "resources" / "icons" / "mediafetch.ico"), "icons"),
        (str(root / "resources" / "icons" / "mediafetch.png"), "icons"),
        *pyqt6_datas,
    ],
    hiddenimports=[
        "yt_dlp",
        "yt_dlp.extractor",
        "yt_dlp.postprocessor",
        "PyQt6.QtCore",
        "PyQt6.QtGui",
        "PyQt6.QtWidgets",
        "PyQt6.sip",
        *pyqt6_hidden,
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        "PyQt6.QtWebEngineWidgets",
        "PyQt6.QtWebEngineCore",
        "PyQt6.QtMultimedia",
        "matplotlib",
        "numpy",
        "pandas",
        "PIL",
        "tkinter",
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

icon_path = root / "resources" / "icons" / "mediafetch.ico"
icon = str(icon_path) if icon_path.is_file() else None

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
    icon=icon,
    version=version_info,
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
