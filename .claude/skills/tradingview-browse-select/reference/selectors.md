# Stable anchors on tradingview.com/chart + self-healing

TradingView obfuscates CSS **class** names (they look like `button-merBkM5y`)
and rotates them between builds. **Never** anchor on those. It keeps stable
`id` and `data-name` attributes on the controls that matter. Prefer, in order:

1. `#header-toolbar-*` ids on the top toolbar.
2. `[data-name="..."]` attributes.
3. `[aria-label="..."]` / visible text (locale-dependent — beware non-English).
4. Geometry on the canvas (last resort, for the chart body only).

If an anchor is missing after a TradingView update, run the discovery routine
(bottom of this file) and re-map — don't guess a class name.

## Header toolbar (top of chart)

| Control | Anchor |
|---|---|
| Symbol search button | `#header-toolbar-symbol-search` |
| Compare / add symbol | `#header-toolbar-compare` |
| Interval / timeframe menu | `#header-toolbar-intervals` |
| Chart style (candles/bars/line) | `#header-toolbar-chart-styles` |
| Indicators dialog | `#header-toolbar-indicators` |
| Templates | `#header-toolbar-indicator-templates` |
| Alerts | `#header-toolbar-alerts` |
| Bar replay | `#header-toolbar-replay` |
| Undo / Redo | `#header-toolbar-undo` |
| Chart settings (gear) | `#header-toolbar-properties` |
| Screenshot / share camera | `#header-toolbar-screenshot` |
| Save layout | `#header-toolbar-save-load` |
| Fullscreen | `#header-toolbar-fullscreen` |

The current interval and symbol text render **inside** these buttons — read them
back to confirm a change landed (e.g. `#header-toolbar-intervals` shows `4h`).

## Symbol search dialog

| Element | Anchor / strategy |
|---|---|
| Dialog container | `[data-dialog-name="symbol-search"]` (fallback: any `[role="dialog"]` visible after opening search) |
| Search input | `input[data-role="search"]` inside the dialog (fallback: the dialog's only focused `input`) |
| Result row | rows carry `data-symbol-full` / `data-symbol-short`; the simplest reliable pick is **type full ticker → `Enter`** to take the top hit |

## Indicators dialog

| Element | Anchor / strategy |
|---|---|
| Dialog | `[data-dialog-name="indicators"]` (fallback: visible `[role="dialog"]` after clicking `#header-toolbar-indicators`) |
| Search field | the dialog's focused `input` (type the indicator name) |
| Add an indicator | type name → click the first result row / press `Enter` → `Esc` to close the dialog |

## Right widget bar (panels)

| Panel | Anchor |
|---|---|
| Watchlist | `[data-name="base"]` |
| Data Window (exact OHLCV at crosshair — **source of truth**) | `[data-name="data-window"]` |
| Object tree | `[data-name="object_tree"]` |
| Alerts panel | `[data-name="alerts"]` |

Click `[data-name="data-window"]` to toggle the Data Window open before reading
candle values (see `canvas-and-reading.md`).

## Series legend (top-left overlay on the chart)

| Element | Anchor / strategy |
|---|---|
| Legend item (one per series) | `[data-name="legend-source-item"]` |
| O/H/L/C values | text spans inside the legend item — read `.textContent` and parse; they update on hover |

The legend is the quick read; the Data Window is the precise read.

## Left drawing toolbar

| Element | Anchor / strategy |
|---|---|
| Toolbar container | `[data-name="drawing-toolbar"]` |
| Magnet mode (snap to OHLC) | `[data-name="magnet"]` — enable it before drawing so lines snap to candle prices |
| Individual tools | prefer the **keyboard shortcuts** (`Alt+T/H/V/F`) over locating buttons |

## The chart canvas (the body)

The candles live on `<canvas>` inside the center layout area. For sending mouse
events, target the chart pane region and use its bounding box:

- Center area: `.layout__area--center` (fallback: the largest `<canvas>` on the
  page by bounding-box area).
- You do not read pixels off the canvas — you move the pointer over it and read
  the legend/Data Window back. See `canvas-and-reading.md`.

## Self-healing discovery routine

When an anchor disagrees with reality, dump what's actually on the page instead
of guessing:

```bash
python scripts/tv_agent.py discover
```

It prints, from the live page:
- every element id starting with `header-toolbar-`,
- every distinct `[data-name]` value,
- every visible `[data-dialog-name]` and `[role="dialog"]`.

Re-map the table above from that output. In ad-hoc Playwright you can do the
same with:

```js
[...document.querySelectorAll('[id^="header-toolbar-"]')].map(e => e.id)
[...new Set([...document.querySelectorAll('[data-name]')].map(e => e.dataset.name))]
```
