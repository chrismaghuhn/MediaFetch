# MediaFetch Studio Design

Design variant extracted from the HTML prototype (`MediaFetch (standalone).html`).

## Variant: Studio

- **Navigation:** Pill tabs in 52px titlebar (Downloads / History / Settings)
- **URL input:** Hero panel with header strip, dashed mono textarea, paste + add actions
- **Queue:** Horizontal rows with platform badge, thin 6px progress bar, status pill
- **Palette (light):** Background `#fbf6f0`, surface `#ffffff`, accent default `#ff5436`
- **Palette (dark):** Background `#14100c`, surface `#221c17`
- **Typography:** Space Grotesk (UI), Space Mono (URLs, stats, paths)

## Accent presets

| Hex | Name |
|-----|------|
| `#ff5436` | Orange (default) |
| `#7a5ae0` | Purple |
| `#1f9d6b` | Green |
| `#2f6fe0` | Blue |
| `#e8911c` | Amber |

Selectable in **Settings → Accent color**.

## Theme tokens

Generated dynamically in [`src/ui/themes/tokens.py`](../src/ui/themes/tokens.py) via `build_stylesheet(mode, accent)`.

Key tokens: `bg`, `surface`, `surface2`, `border`, `text`, `textMuted`, `accent`, `track`, `success`, `danger`.

## Fonts setup

```powershell
.\scripts\setup_fonts.ps1
```

Downloads Space Grotesk and Space Mono TTF files into `resources/fonts/`.

## Implementation notes

- Qt has no CSS `box-shadow`; panels use border-only styling
- QSS uses `[variant="primary"]`, `[nav="true"]`, `#Panel`, `#HeroPanel` selectors
- Old static `dark.qss` / `light.qss` are superseded by token-based generation

## Limitations vs HTML prototype

- No Tweaks panel (density/corners) — compact + soft corners are hardcoded
- No WebView — native PyQt6 widgets only
- Window controls in titlebar are simplified (update + close, not min/max)
