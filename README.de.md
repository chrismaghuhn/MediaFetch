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
- [Git for Windows](https://git-scm.com/) (zum Klonen und Pushen)
- FFmpeg und Fonts (werden per Setup-Skripte geladen)

## Schnellstart (Entwicklung)

```powershell
cd Download-Tool
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
.\scripts\setup_dev.ps1
.\scripts\setup_fonts.ps1
python src\main.py
```

- `setup_dev.ps1` lädt FFmpeg nach `resources\bin\` (erforderlich für YouTube-Video-Downloads)
- `setup_fonts.ps1` lädt Space Grotesk/Mono nach `resources\fonts\`

Ohne aktivierte venv:

```powershell
python -m pip install -r requirements-dev.txt
python src\main.py
```

## Tests ausführen

```powershell
pytest
pytest --cov=src/core --cov=src/services --cov=src/utils --cov-report=term-missing --cov-fail-under=70
```

## Release bauen

### Executable (One-File)

```powershell
python scripts\build.py
# oder mit FFmpeg-Download:
.\build\build_release.ps1
```

Ausgabe: `dist\MediaFetch.exe`

Wenn `dist\` nicht gelöscht werden kann (exe noch geöffnet), MediaFetch schließen oder:

```powershell
python scripts\build.py --no-clean
```

### Installer (Inno Setup)

[Inno Setup 6](https://jrsoftware.org/isinfo.php) installieren, dann:

```powershell
.\build\build_release.ps1 -Installer
# oder nach dem exe-Build:
.\scripts\build_installer.ps1
```

Ausgabe: `dist\MediaFetch-{version}-Setup.exe`

### Release-Workflow

1. Version in [`src/version.py`](src/version.py) erhöhen
2. Tests mit Coverage ausführen (siehe oben)
3. exe und Installer bauen
4. Tag pushen: `git tag v1.0.0 && git push origin v1.0.0`
5. GitHub Actions ([`.github/workflows/release.yml`](.github/workflows/release.yml)) lädt Release-Assets hoch

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
| One-File PyInstaller | Eine `MediaFetch.exe` für Endnutzer |
| Inno Setup | Zweisprachiger Installer, Registry, optionale Datenbehalt-Abfrage |
| Manuelle App-Updates | Frozen exe kann sich nicht selbst ersetzen |

## Limitierungen

- Nur öffentliche Inhalte — kein Login oder Cookie-Import
- Instagram/TikTok-Extractors brechen bei Plattform-Änderungen; yt-dlp aktuell halten
- Inhaltsfilter (Shorts/Reels) hängen von yt-dlp-Extractor-Keys ab und können brechen
- Geo-Blocking und Rate-Limits können Fehler verursachen
- Internetverbindung erforderlich

## Auf GitHub veröffentlichen

Remote: `https://github.com/chrismaghuhn/MediaFetch.git`

**Nicht committen** (steht in [`.gitignore`](.gitignore)):

- `.venv/`, `.pytest_cache/`, `.coverage`
- `resources/bin/ffmpeg.exe`, `yt-dlp.exe` (~200 MB)
- `resources/fonts/*.ttf` (via `setup_fonts.ps1`)
- `dist/`, PyInstaller-Cache in `build/` (außer `*.spec`, `*.ps1`)
- `*.zip`, `*.db`, `*.log`, `*.Setup.exe`

Nach dem Klonen die Setup-Skripte aus [Schnellstart](#schnellstart-entwicklung) ausführen.

**Push / Sync:**

```powershell
git add .
git status    # ffmpeg.exe, dist/, .venv/, *.ttf dürfen NICHT erscheinen
git commit -m "Deine Nachricht"
git push -u origin main
```

Falls `git` nicht im PATH ist: `"C:\Program Files\Git\bin\git.exe"` verwenden.

Update-Checks nutzen `github_repo` in [`src/models/settings.py`](src/models/settings.py) (Standard: `ChrismagHuhn/MediaFetch`).

## Rechtliches

Siehe [DISCLAIMER.md](DISCLAIMER.md). Du trägst die alleinige Verantwortung dafür, dass deine Nutzung den geltenden Gesetzen und Plattform-Nutzungsbedingungen entspricht.

## Lizenz

MIT-Lizenz — siehe [LICENSE](LICENSE). PyQt6 wird unter LGPL verwendet; die Anwendung linkt Qt-Bibliotheken dynamisch.
