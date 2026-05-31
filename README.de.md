# MediaFetch

[Deutsch](README.de.md) | [English](README.md)

Desktop-Video-Downloader für **YouTube**, **Instagram** und **TikTok**. Nur für Windows, gebaut mit Python und PyQt6.

## Funktionen

- Einzelne Videos, Playlists, Kanäle und Profile herunterladen
- Qualitätsauswahl, nur Audio (MP3/M4A), optionale Untertitel
- Batch-Warteschlange mit parallelen Downloads und Wiederholungsversuchen
- Echtzeit-Fortschritt (Prozent, Geschwindigkeit, ETA)
- Organisierte Ordnerstruktur nach Plattform und Creator
- Download-Chronik mit Suche und Filtern
- Dark/Light-Theme und zweisprachige UI (Deutsch/Englisch)
- Duplikat-Erkennung mit Nutzerbestätigung
- Warnungen bei Altersfreigabe und Urheberrecht
- Update-Benachrichtigungen für App und yt-dlp

## Voraussetzungen (Entwicklung)

- Windows 10/11
- Python 3.10+ ([python.org](https://www.python.org/downloads/) oder Microsoft Store)
- FFmpeg (wird für Releases automatisch gebündelt)

## Schnellstart (Entwicklung)

Unter Windows ist `pip` oft nicht im PATH. Stattdessen `python -m pip` verwenden:

```powershell
cd Download-Tool
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pip install pyinstaller pytest
.\scripts\setup_dev.ps1
python src\main.py
```

`setup_dev.ps1` lädt FFmpeg nach `resources\bin\` — erforderlich für YouTube-Video-Downloads.

Ohne aktivierte venv:

```powershell
python -m pip install -r requirements.txt
python src\main.py
```

## Release bauen

```powershell
.\build\build_release.ps1
```

Ausgabe: `dist\MediaFetch\MediaFetch.exe` und `dist\MediaFetch-win64.zip`

## Nutzung

1. Eine oder mehrere Video-URLs einfügen (eine pro Zeile)
2. **Zur Warteschlange hinzufügen** klicken und Format wählen
3. Downloads starten automatisch; Fortschritt erscheint in der Warteschlange
4. Abgeschlossene Downloads im Tab **Chronik** ansehen
5. Ordner, Parallelität und Theme unter **Einstellungen** konfigurieren

### Beispiel-URLs

```
https://www.youtube.com/watch?v=dQw4w9WgXcQ
https://www.instagram.com/reel/EXAMPLE/
https://www.tiktok.com/@user/video/1234567890
```

## Architektur

```
src/
├── core/       # Download-Engine, Queue, Validierung (GUI-frei)
├── models/     # Datenklassen
├── services/   # Settings, Chronik, Logging, Updates
├── workers/    # QThread-Download-Worker
├── ui/         # PyQt6-Widgets und Dialoge
└── utils/      # Pfade, Dateinamen, Version
```

- **yt-dlp** als einzige Download-Engine (Python-API mit Subprocess-Fallback)
- **SQLite** für durchsuchbare Download-Chronik
- **JSON** für Einstellungen und Queue-Persistenz
- **QThread** pro aktivem Download (kein QThreadPool)

## Technische Entscheidungen

| Wahl | Grund |
|------|-------|
| PyQt6 | Moderne API, HiDPI, LGPL-konformes dynamisches Linking via PyInstaller |
| yt-dlp | Einheitliche Unterstützung aller Zielplattformen, aktiv gepflegt |
| `--onedir` PyInstaller | Zuverlässiges Bündeln von FFmpeg und yt-dlp |
| Manuelle App-Updates | Frozen exe kann sich nicht selbst ersetzen |

## Limitierungen

- Nur öffentliche Inhalte — kein Login oder Cookie-Import
- Instagram/TikTok-Extractors brechen bei Plattform-Änderungen; yt-dlp aktuell halten
- Inhaltsfilter (Shorts/Reels) hängen von yt-dlp-Extractor-Keys ab und können brechen
- Geo-Blocking und Rate-Limits können Fehler verursachen
- Internetverbindung erforderlich

## Repository veröffentlichen

Vor dem ersten Release den Platzhalter `your-org/MediaFetch` in `src/models/settings.py` (oder in den App-Einstellungen) durch dein echtes Repository ersetzen, z. B. `dein-username/MediaFetch`. Sonst liefert der Update-Check einen 404-Fehler.

Diese Dateien gehören **nicht** ins Repository (stehen bereits in `.gitignore`):

- `.venv/`, `.pytest_cache/`
- `resources/bin/ffmpeg.exe`, `yt-dlp.exe` (~200 MB, werden per Skript geladen)
- `dist/`, PyInstaller-Zwischendateien in `build/`
- `*.zip`, `*.db`, `*.log`

Erster Push:

```powershell
git init
git add .
git status          # prüfen: keine .venv, kein ffmpeg.exe
git commit -m "Initial commit: MediaFetch desktop app"
git branch -M main
git remote add origin https://github.com/DEIN-USER/MediaFetch.git
git push -u origin main
```

Falls `git` in der Konsole nicht gefunden wird: [Git for Windows](https://git-scm.com/) installieren oder [GitHub Desktop](https://desktop.github.com/) nutzen.

## Rechtliches

Siehe [DISCLAIMER.md](DISCLAIMER.md). Du trägst die alleinige Verantwortung dafür, dass deine Nutzung den geltenden Gesetzen und Plattform-Nutzungsbedingungen entspricht.

## Lizenz

MIT-Lizenz — siehe [LICENSE](LICENSE). PyQt6 wird unter LGPL verwendet; die Anwendung linkt Qt-Bibliotheken dynamisch.
