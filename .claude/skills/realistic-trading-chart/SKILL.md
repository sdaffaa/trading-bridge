---
name: realistic-trading-chart
description: Render realistic, TradingView-style candlestick charts as SVG/PNG for Liquidity State carousels, reels, covers, and lesson slides — real-looking price action (dozens of OHLC candles, thin wicks), a right-side price axis, price grid, volume bars, last-price tag, and a dashed liquidity line, all in the brand palette. Use this INSTEAD of hand-drawing a few blocky candles whenever a slide, cover, thumbnail, or video frame needs a chart that looks like a genuine trading terminal — especially for liquidity-sweep / stop-hunt, order-block, BOS/CHoCH, FVG, or documented-trade visuals. Triggers include: "الجارت طالع طفولي/مو حقيقي", "خلي الشارت حقيقي", "شارت مثل TradingView", "candles واقعية", "أضف شارت للسلايد/الغلاف/الريل", or any brand chart visual. Engineered scenarios (liquidity_sweep_bullish, etc.) place the pattern deliberately so the teaching point is unmistakable.
---

# Realistic Trading Chart Engine

A dependency of `carousel-design-pro` and `reels-design-pipeline`. Produces brand-styled
candlestick charts that read as a **real trading terminal**, not a cartoon. Deterministic
(seeded), no network, no external chart library.

## Why this exists

Hand-drawing 6–10 fat candles looks childish and kills credibility on a trading account.
Real charts have **density** (50–70 candles), thin wicks, a price axis, a grid, volume,
and a coherent price story. This engine generates all of that and lets you **engineer the
pattern** (equal lows → sweep → reversal) so the lesson is obvious while the chart still
looks authentic.

## Files

- `scripts/chart-engine.js` — the engine. Exports `chartSVG(opts)` and `buildSeries(opts)`. No deps.
- `scripts/render-chart.js` — CLI that rasterizes a chart to PNG (needs `playwright-core` + Chromium).
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
