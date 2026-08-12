# Liquidity State — chart & reel production skills

A composable suite for turning a trading idea into a provably-real, brand-styled educational chart or reel.
The three skills separate concerns so each can be reused and improved independently:

| Skill | Owns | Key outputs |
|---|---|---|
| **ls-methodology-module** | *Which* methodologies to use and how to layer them (max 3), hooks & CTAs per school | a layer plan (primary + optional structure/context/confirmation) |
| **verified-market-charts** | *What to draw* — real data, OHLC verification, Volume Profile, scenario scan, source disclosure | `scripts/build_scenario.mjs` → `data/scenario.json` (+ raw CSV) |
| **ls-reel-engine** | *How to animate & export* — deterministic 1080×1920 renderer, price axis, camera, timing, encode | `build_html → render_frames → encode` → MP4 (master + web) |

## Typical flow
1. `ls-methodology-module` → pick primary + layers for the piece (e.g. Volume Profile + ICT structure).
2. `verified-market-charts` → fetch real OHLCV (autonomously), verify, build the Volume Profile, scan for a
   valid scenario → `scenario.json`. Disclose the source mode (real data vs simulation) — never hide it.
3. `ls-reel-engine` → render the scene from `scenario.json` to a silent H.264 reel + hand off the audio cue sheet.

## Reference implementation
`/reel` in this repo is a worked example end-to-end: `data/gld_daily.csv` (real GLD daily from Alpha Vantage) →
`data/scenario.json` (verified break-above-VAH → fail → POC/VAL on gold) → the redesigned reel with a
TradingView-style price axis and live last-price tag. Reproduce it with the three skill scripts; see each skill's
`SKILL.md` for exact commands.

## Environment notes
- Rendering needs Node + Playwright + Chromium (preinstalled at `/opt/pw-browsers`).
- Encoding needs H.264: `ffmpeg` on PATH, or `pip install imageio-ffmpeg` (its static build has libx264).
- Fonts (IBM Plex Sans Arabic + Inter) are bundled in `ls-reel-engine/assets/fonts` and inlined at build time.
