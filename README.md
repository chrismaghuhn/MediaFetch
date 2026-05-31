# MediaFetch

[Deutsch](README.de.md) | [English](README.md)

Desktop video downloader for **YouTube**, **Instagram**, and **TikTok**. Windows-only, built with Python and PyQt6.

## Features

- Download single videos, playlists, channels, and profiles
- Quality selection, audio-only (MP3/M4A), optional subtitles
- Batch queue with concurrent downloads and retry handling
- Real-time progress (percent, speed, ETA)
- Organized folder structure by platform and creator
- Download history with search and filters
- Dark/light theme and German/English UI
- Duplicate detection with user confirmation
- Age-restriction and copyright warnings
- Update notifications for app and yt-dlp

## Requirements (development)

- Windows 10/11
- Python 3.10+ (get it from [python.org](https://www.python.org/downloads/) or the Microsoft Store)
- FFmpeg (bundled automatically for releases)

## Quick start (development)

```powershell
cd Download-Tool
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pip install pyinstaller pytest
.\scripts\setup_dev.ps1
python src\main.py
```

`setup_dev.ps1` downloads FFmpeg into `resources\bin\` — required for YouTube video downloads.

Without activating the venv:

```powershell
python -m pip install -r requirements.txt
python src\main.py
```

## Building a release

```powershell
.\build\build_release.ps1
```

Output: `dist\MediaFetch\MediaFetch.exe` and `dist\MediaFetch-win64.zip`

## Usage

1. Paste one or more video URLs (one per line)
2. Click **Add to queue** and choose format options
3. Downloads start automatically; progress appears in the queue tab
4. View completed downloads in the **History** tab
5. Configure folder, concurrency, and theme in **Settings**

### Example URLs

```
https://www.youtube.com/watch?v=dQw4w9WgXcQ
https://www.instagram.com/reel/EXAMPLE/
https://www.tiktok.com/@user/video/1234567890
```

## Architecture

```
src/
├── core/       # Download engine, queue, validation (GUI-free)
├── models/     # Data classes
├── services/   # Settings, history, logging, updates
├── workers/    # QThread download workers
├── ui/         # PyQt6 widgets and dialogs
└── utils/      # Paths, filenames, version helpers
```

- **yt-dlp** is the sole download engine (Python API with subprocess fallback)
- **SQLite** for searchable download history
- **JSON** for settings and queue persistence
- **QThread** per active download (not QThreadPool)

## Technical decisions

| Choice | Reason |
|--------|--------|
| PyQt6 | Modern API, HiDPI, LGPL-compatible dynamic linking via PyInstaller |
| yt-dlp | Unified support for all target platforms, actively maintained |
| `--onedir` PyInstaller | Reliable bundling of FFmpeg and yt-dlp binaries |
| Manual app updates | Frozen exe cannot replace itself while running |

## Limitations

- Public content only — no login or cookie import
- Instagram/TikTok extractors break when platforms change; keep yt-dlp updated
- Content filters (Shorts/Reels) depend on yt-dlp extractor keys and may break
- Geo-blocking and rate limits can cause failures
- Internet connection required


## Legal

See [DISCLAIMER.md](DISCLAIMER.md). You are solely responsible for ensuring your use complies with applicable laws and platform terms of service.

## License

MIT License — see [LICENSE](LICENSE). PyQt6 is used under LGPL; the application dynamically links Qt libraries.
