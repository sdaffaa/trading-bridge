---
name: tradingview-browse-select
description: >-
  Drive the TradingView web app (tradingview.com/chart) like a fast, precise
  human trader — navigate, browse, and SELECT anything on the chart with a
  browser agent (Playwright/Chromium). Use whenever the task is to control,
  automate, scrape, or interact with the TradingView UI itself: switch symbol,
  change timeframe/interval, add or configure indicators, open the watchlist,
  draw tools on the chart canvas, read exact OHLC/price values, hover a specific
  candle, take chart screenshots, or move the mouse/keyboard on the chart. Works
  even in Arabic (شغّل تريدنق فيو، تصفّح الشارت، اختر رمز، غيّر الفريم، حدّد شمعة،
  ارسم خط، اقرأ الأسعار، أتمتة تريدنق فيو، وكيل يتصفح تريدنق فيو). This skill owns
  UI automation of the platform; it does NOT do market analysis (use the trading
  methodology skills for that).
---

# TradingView Browse & Select — human-speed, human-precise agent control

## What this skill is for

Making a browser agent operate the **tradingview.com/chart** web app the way an
experienced trader does: fast, deliberate, and accurate. The hard part of
TradingView automation is that **the chart is a `<canvas>`** — candles, prices,
and drawings are painted pixels with no DOM. Everything *around* the chart
(header toolbar, symbol search, dialogs, watchlist, data window, drawing
toolbar) **is** real DOM. This skill teaches the split:

- **Chrome (DOM) → keyboard + stable anchors.** Symbol, interval, indicators,
  dialogs, panels. Fast and reliable.
- **Chart body (canvas) → mouse geometry + read-back.** Hover, draw, and select
  by moving the pointer over the canvas and *reading the values back* from DOM
  read-outs (the legend and the Data Window), never by guessing pixels.

The golden rule: **act, then read back to confirm.** A human glances at the
legend after every move. Your agent must too — this is what makes it *precise*
instead of merely fast.

## Prerequisites (one time)

Chromium is pre-installed at `/opt/pw-browsers/chromium`. Install the Python
Playwright client (the browser binary is already there — do **not** run
`playwright install`):

```bash
pip install playwright
```

Everything below is wrapped in `scripts/tv_agent.py`. Prefer calling that module
over hand-writing Playwright — it already encodes the human-pacing, the
read-back confirmation loop, and self-healing selector discovery.

## The 6-step operating loop

Follow this loop for any TradingView task. Each step maps to a helper in
`scripts/tv_agent.py` and to a section of the reference files.

1. **Launch with a persistent profile** so login/session survives runs. Use a
   real (non-headless) window when a login is needed; headless is fine once the
   profile is warm. → `TVAgent(profile_dir=...)`.
2. **Wait for the chart to be live**, not just for `load`. TradingView keeps
   painting after `networkidle`. Wait until the legend shows an OHLC value.
   → `agent.wait_chart_ready()`.
3. **Browse via keyboard first.** Symbol, interval, and tools are far faster and
   more robust by keyboard than by hunting buttons. See
   `reference/keyboard-shortcuts.md`. → `set_symbol`, `set_interval`.
4. **Select on the canvas by read-back, not by pixel.** To land on a specific
   candle, move the pointer across the chart and read the legend/Data Window
   date until it matches your target — a short search, exactly like a human
   sliding the crosshair. → `hover_bar_by_time`, `read_ohlc`.
5. **For exact price levels, don't aim pixels — type the number.** Drop a
   horizontal line, open its settings, and set the price in the DOM input. This
   is pixel-perfect where mouse-aiming never is. → `hline_at_price`.
6. **Confirm and capture.** Re-read the value you changed; screenshot the chart
   region (not the whole page) as evidence. → `screenshot_chart`.

## Move like a human (why speed ≠ haste)

"Fast like a human" does **not** mean instant teleport-clicks — those trip
TradingView's UI (menus need a frame to open, the canvas debounces hover) and
look like a bot. Human-fast means *no wasted motion, with the minimum settle
time each widget needs*:

- **Glide the mouse in small steps with slight jitter**, don't jump. Menus and
  tooltips only appear on genuine `mousemove`. `tv_agent.human_move` does this.
- **Hover, brief pause (~80–150 ms), then click.** Give menus a frame to render
  before the next action.
- **Prefer keyboard for anything with a shortcut** — it's both faster and more
  reliable than locating a button (see the shortcuts reference).
- **Type into search like a person** (per-character with tiny delays), then
  `Enter` to take the top hit, rather than pasting.
- **Never sleep on a fixed timer to "wait for data".** Poll the read-back
  (legend/Data Window) until it changes. This is faster *and* correct.

Full rationale and tuned timings: `reference/human-behavior.md`.

## Selecting & reading — the part that must be exact

The chart is canvas, so **do not scrape candles from the DOM — there are none.**
Two DOM read-outs give you ground truth:

- **The series legend** (top-left of the chart): shows `O H L C` and change for
  the bar under the crosshair. Updates on hover. Good for a quick read.
- **The Data Window** (right widget bar): shows precise `Open/High/Low/Close/
  Volume` and the **date/time** of the hovered bar. This is your source of truth
  for "which candle am I on" and "what is its exact value".

To **select a specific candle**: open the Data Window, then binary-search the
pointer's X across the chart, reading the Data Window's date each step, until it
equals your target bar. To **place an exact price level**: use a horizontal line
and set the price via its settings dialog input. Details, selectors, and the
coordinate model: `reference/canvas-and-reading.md`.

## Stable anchors + self-healing

TradingView ships obfuscated CSS class names but keeps **stable `id` and
`data-name` hooks** on the important controls (e.g. `#header-toolbar-symbol-search`,
`#header-toolbar-intervals`, `#header-toolbar-indicators`). Prefer those; treat
class names as disposable. When an anchor goes missing after a TradingView
update, **don't guess** — dump the live hooks and re-map:

```bash
python scripts/tv_agent.py discover   # prints every #header-toolbar-* id and [data-name] on the page
```

The catalogue of anchors and keyboard shortcuts lives in
`reference/selectors.md` and `reference/keyboard-shortcuts.md`. The discovery
command is the recovery path whenever reality disagrees with the catalogue.

## Reference files (read on demand — don't inline)

- `reference/keyboard-shortcuts.md` — the human-fast command set: symbol,
  interval, drawing tools, view, replay. Keyboard-first is the whole speed story.
- `reference/selectors.md` — stable `id`/`data-name` anchors for the header,
  dialogs, panels, and drawing toolbar, with fallbacks and the discovery routine.
- `reference/canvas-and-reading.md` — the canvas model: hover geometry, reading
  OHLC from the legend and Data Window, selecting a candle by read-back, and
  placing exact price levels.
- `reference/human-behavior.md` — pacing, mouse pathing, and anti-fragile waits
  (poll read-back, never fixed sleeps).

## Guardrails

- **Respect TradingView's ToS and rate limits.** This is for legitimate,
  low-volume, human-paced interaction (your own charts, screenshots, reading
  levels) — not scraping farms or hammering the site. Keep pacing human.
- **Never hard-code credentials.** Use a persistent profile dir and log in once
  interactively, or read secrets from env vars — never commit them.
- This skill does **UI control only**. For what a setup *means*, hand off to the
  analysis skills (ICT/SMC/volume-profile/footprint/chart-reading).
