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
- [Git for Windows](https://git-scm.com/) (for cloning and pushing)
- FFmpeg and fonts (downloaded via setup scripts below)

## Quick start (development)

```powershell
cd Download-Tool
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
.\scripts\setup_dev.ps1
.\scripts\setup_fonts.ps1
python src\main.py
```

- `setup_dev.ps1` downloads FFmpeg to `resources\bin\` (required for YouTube video downloads)
- `setup_fonts.ps1` downloads Space Grotesk/Mono fonts to `resources\fonts\`

Without activating the venv:

```powershell
python -m pip install -r requirements-dev.txt
python src\main.py
```

## Running tests

```powershell
pytest
pytest --cov=src/core --cov=src/services --cov=src/utils --cov-report=term-missing --cov-fail-under=70
```

## Building a release

### Executable (one-file)

```powershell
python scripts\build.py
# or with FFmpeg download:
.\build\build_release.ps1
```

Output: `dist\MediaFetch.exe`


### Installer (Inno Setup)

Install [Inno Setup 6](https://jrsoftware.org/isinfo.php), then:

```powershell
.\build\build_release.ps1 -Installer
# or after building the exe:
.\scripts\build_installer.ps1
```

Output: `dist\MediaFetch-{version}-Setup.exe`

### Release workflow

1. Bump version in [`src/version.py`](src/version.py)
2. Run tests with coverage (see above)
3. Build exe and installer
4. Tag and push: `git tag v1.0.0 && git push origin v1.0.0`
5. GitHub Actions ([`.github/workflows/release.yml`](.github/workflows/release.yml)) uploads release assets

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
| One-file PyInstaller | Single `MediaFetch.exe` for end users |
| Inno Setup | Bilingual installer, registry entries, optional data retention on uninstall |
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
