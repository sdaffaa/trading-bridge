---
name: realistic-trading-chart
description: Render realistic, TradingView-style candlestick charts as SVG/PNG for Liquidity State carousels, reels, covers, and lesson slides — from REAL fetched market data (Yahoo/Binance/Stooq, no API key) or from a deterministic engineered scenario. Real-looking price action (dozens of OHLC candles, thin wicks), a right-side price axis, price grid, volume bars, last-price tag, and an auto-detected dashed liquidity line + sweep marker, all in the brand palette. Use this INSTEAD of hand-drawing a few blocky candles whenever a slide, cover, thumbnail, or video frame needs a chart that looks like a genuine trading terminal — especially for liquidity-sweep / stop-hunt, order-block, BOS/CHoCH, FVG, or documented-trade visuals. Triggers include: "اسحب الجارت", "اسحب داتا/شموع الذهب الحقيقية", "شارت مثل TradingView", "الجارت طالع طفولي/مو حقيقي", "candles واقعية", "أضف شارت للسلايد/الغلاف/الريل", or any brand chart visual. Real fetch needs open network egress; engineered scenarios need none.
---

# Realistic Trading Chart Engine

A dependency of `carousel-design-pro` and `reels-design-pipeline`. Produces brand-styled
candlestick charts that read as a **real trading terminal**, not a cartoon. Two data modes:
**(A) real fetched OHLC** from free key-less providers, or **(B) a deterministic engineered
scenario** (seeded, no network). Same renderer for both.

## Real market data (mode A) — "اسحب الجارت"

```bash
npm i playwright-core                       # once
# fetch REAL XAUUSD candles and render a brand chart card straight to PNG:
node scripts/render-real-chart.js --symbol XAUUSD --interval 15m --window 70 \
     --title "XAU/USD" --out xau-example.png --scale 2
```

Or fetch the raw candles yourself and feed them to the renderer:

```js
const { fetchOHLC } = require('./scripts/fetch-ohlc');
const { chartSVG }  = require('./scripts/chart-engine');
const { candles, source } = await fetchOHLC({ symbol:'XAUUSD', interval:'15m', limit:120 });
const { svg, meta } = chartSVG({ candles, annotate:true });   // sweep auto-detected
// meta = { pool, last, sweepIndex } — the liquidity line + "سحب السيولة" marker are drawn for you
```

- **Providers** (first success wins, no API key): Yahoo Finance (`GC=F`/`XAUUSD=X`, forex, indices, crypto) → Binance (`PAXGUSDT` ≈ gold, crypto) → Stooq (daily CSV). Symbol map in `fetch-ohlc.js` (`XAUUSD`, `EURUSD`, `BTCUSD`, `US100`, …).
- **Intervals**: `1m,5m,15m,30m,1h,4h,1d` (Stooq falls back to daily).
- **Auto sweep detection**: `detectSweep()` finds equal-lows (the pool) that a later bar wicks below then closes back above, and annotates it. Override by slicing `candles` to the window you want.
- ⚠️ **Network**: real fetch needs outbound access to those hosts. In an egress-filtered sandbox every host returns 403 — run mode A where the network is open (local Claude Code, CI with internet). In a locked sandbox, use mode B or paste a screenshot.

## Engineered scenario (mode B) — no network

## Why this exists

Hand-drawing 6–10 fat candles looks childish and kills credibility on a trading account.
Real charts have **density** (50–70 candles), thin wicks, a price axis, a grid, volume,
and a coherent price story. This engine generates all of that and lets you **engineer the
pattern** (equal lows → sweep → reversal) so the lesson is obvious while the chart still
looks authentic.

## Files

- `scripts/chart-engine.js` — the renderer + generator. Exports `chartSVG(opts)`, `buildSeries(opts)`, `prepReal(candles)`, `detectSweep(candles)`. No deps.
- `scripts/fetch-ohlc.js` — pull REAL OHLC from Yahoo/Binance/Stooq (no API key). Exports `fetchOHLC({symbol,interval,limit})`.
- `scripts/render-real-chart.js` — CLI: fetch real data → auto-detect sweep → render brand chart card PNG.
- `scripts/render-chart.js` — CLI that rasterizes an engineered chart to PNG (needs `playwright-core` + Chromium).
- `fonts/` — Tajawal Arabic woff2 (400/700/800/900) for Arabic annotations, base64-inlined at render time.

## Usage A — embed the SVG in a slide (preferred for carousels)

```js
const { chartSVG } = require('./scripts/chart-engine');
const { svg, meta } = chartSVG({
  width: 1040, height: 520,       // match your card's inner aspect (~2:1 reads best)
  seed: 7,                        // change the seed to reshuffle the noise, keep the structure
  annotate: true,                 // draw the liquidity line label + "سحب السيولة" marker
  bull: '#2ECC9A', bear: '#E15A5A', grid: '#22434E', text: '#8BA3AB',
  bg: 'transparent',              // let the slide card background show through
});
// drop `svg` inside your slide HTML card, then screenshot the slide with Playwright.
// `meta` = { pool, last, sweepIndex } if you need to place extra callouts.
```

Put the SVG inside a "chart widget" card with a header bar (`XAU/USD` · `M15` · `▲ 0.61%`
· `لغرض تعليمي`) to complete the terminal look. See §Recipe.

## Usage B — standalone PNG (thumbnails, quick frames)

```bash
npm i playwright-core           # once
node scripts/render-chart.js --out chart.png --seed 7 --annotate --width 1040 --height 520 --scale 2
```

Chromium is auto-detected via `$CHROMIUM_PATH`, playwright's default, or `/opt/pw-browsers/chromium-*`.

## Options (chartSVG)

| Option | Default | Notes |
|---|---|---|
| `width` / `height` | 1000 / 620 | viewBox; pick to match the card aspect (2:1 is a clean strip) |
| `seed` | 7 | deterministic RNG; vary to reshuffle wick/volume noise |
| `base` | 2348.0 | anchor price (XAUUSD-ish); axis auto-scales around the series |
| `n` | 64 | candle count; keep 55–70 for a realistic density |
| `annotate` | false | dashed liquidity line label + sweep marker/pill (Arabic) |
| `bull`/`bear`/`grid`/`text` | brand | colors — keep the brand teal-green/soft-red |
| `bg` | transparent | set to `#12262E` for a standalone image |

## Scenario (current)

`liquidity_sweep_bullish` — the default crafted structure:
push up → rollover → **equal-lows consolidation at the pool** → **liquidity sweep**
(one bar wicks below the pool and closes back above — trapping stops) → **impulse rally**.
`buildSeries` marks the sweep bar (`sweepIndex`) and places the pool at the equal lows so
the dashed liquidity line sits exactly where retail stops rest. To add scenarios
(bearish sweep, order block, BOS→retest, FVG fill), add a branch to `buildSeries`' close-path
and expose it via an opts flag — keep the "anchors + noise" method so it stays realistic.

## Recipe — the terminal-look card

1. Card: `background:linear-gradient(180deg,#12272F,#0E2027)`, `1px #2ECC9A22` border, 24px radius.
2. Header row: `XAU/USD` (bold white) · `M15` pill · `▲ 0.61%` (green) · `لغرض تعليمي` (grey, at inline-end).
3. Chart box ~2:1; call `chartSVG({annotate:true})`; svg fills 100% width/height.
4. Rasterize the whole slide at deviceScaleFactor 2 (see `carousel-design-pro` pipeline), then downscale.

## QA (must pass)

- [ ] 55–70 candles, thin wicks (≤2px), small gaps — not fat blocks
- [ ] Right price axis with 4–6 labeled levels + a grid
- [ ] Volume row present; sweep/impulse bars visibly heavier
- [ ] Dashed liquidity line sits **at the equal lows**; the sweep bar clearly pierces below it then closes back above
- [ ] Last-price tag on the axis; colors are brand teal-green/soft-red only
- [ ] Arabic annotations shaped/connected correctly (Tajawal) and `لغرض تعليمي` present

Never paste foreign-colored TradingView screenshots into brand content — regenerate with this engine.
