---
name: verified-market-charts
description: >-
  Build accurate, honestly-sourced trading charts for Liquidity State from REAL market data instead of
  guessing. Use this WHENEVER you are about to draw candles, a Volume Profile, or set VAH/POC/VAL/entry/SL
  for a chart, reel, or carousel — especially for XAUUSD/gold, GLD, GC futures, or any "أعد رسم الشارت / بيانات
  حقيقية / رسم توضيحي / شارت تعليمي / Volume Profile / POC / VAH / VAL / احسب الستوب". It decides the source
  mode (original chart → verified market data → educational simulation), fetches real OHLCV via the available
  MCP data tools, verifies every candle mathematically, builds a real Fixed-Range Volume Profile, and scans for
  a verifiable scenario — never inventing candles, prices, volume, or R. Always pair this with the actual
  drawing/animation (see ls-reel-engine) so the chart you render is provably real.
---

# Verified Market Charts

The point of this skill: a Liquidity State chart must never quietly fake the market. Viewers are intermediate
traders who will notice invented candles or an impossible Volume Profile. So we **prove** the data is real (or
clearly label it as a simulation) before drawing anything.

## 1. Pick the source mode (in strict priority order)

`CHART_SOURCE_MODE = A_ORIGINAL_CHART / B_VERIFIED_MARKET_DATA / C_EDUCATIONAL_SIMULATION`

1. **A — original chart**: a user screenshot / TradingView recording / exported CSV + the real trade values.
   Preserve every body, wick, price and event order exactly; you may only clean the UI and recolor.
2. **B — verified market data** (default when A is absent): fetch real historical OHLCV from a trusted source
   and rebuild. This is almost always achievable — **do not fall through to C just because A is missing.**
3. **C — educational simulation**: only when neither A nor B is possible. Generate a coherent, clearly-labeled
   synthetic scenario. Never attach a real date, provider, or exchange to it, and never show R as a real result.

Read `references/source-modes.md` for the full rules and the exact on-chart / caption disclosure strings for
each mode. The disclosure is mandatory — the viewer must always be able to tell real data from simulation.

## 2. Autonomous data fetch (do not ask the user for files)

Auto-pick the instrument from the topic, then fetch. Full playbook with tool names, symbols, and fallbacks is in
`references/data-sources.md`. The short version that works today:

- Gold Volume-Profile / VWAP / Volume lessons → **GLD daily** via Alpha Vantage `TIME_SERIES_DAILY` (real NYSE
  exchange volume, free). Intraday gold (`GC futures`, AV intraday) is often plan-gated — fall back to GLD daily
  and disclose it, rather than stalling.
- Verify what you fetched: save the raw rows to a CSV (`timestamp,open,high,low,close,volume`) so the chart is
  reproducible from a file.

## 3. Verify + build the scenario (one script)

`scripts/build_scenario.mjs` does the math so every run is consistent and auditable. It:
verifies OHLC integrity (High ≥ O,C,L and Low ≤ O,C on every row — aborts if any row is impossible), builds a
Fixed-Range Volume Profile from the real volume (POC = highest-volume price, VAH/VAL = the 70% value-area edges),
and scans for a real **break above VAH → failed acceptance → rotation to POC then VAL** sequence with the events
on distinct bars.

```bash
node scripts/build_scenario.mjs --csv data/gld_daily.csv --out data/scenario.json \
  --tick 0.5 --va 0.70 \
  --symbol "GLD (SPDR Gold Shares)" --source "Alpha Vantage" \
  --tf "يومي · 1D" --voltype "حجم بورصة حقيقي (NYSE Arca)"
```

It writes `scenario.json` (candles, vah/poc/val, exit/fail/entry/SL, target indices, profile bins, source
metadata) — the exact contract `ls-reel-engine`'s scene template consumes. If it prints `NO SCENARIO FOUND`,
pull a different/longer data window rather than bending the data to fit the script.

## 4. Volume Profile honesty (important)

If you only have OHLCV (not tick/trade data), a Volume Profile is an **estimate** — the volume is real but its
distribution *within* each bar is inferred. Label it **"Volume Profile تقديري"** on the chart. Never claim
price-level precision you don't have, and never derive Footprint/Delta/Absorption from candle shape alone.
Per-school data rules (SMC, ICT, Footprint, Volume Profile, VWAP, Volume) are in `references/school-data-rules.md`.

## 5. Pre-delivery checklist

- [ ] Source mode chosen and **disclosed** on-chart + in caption (real vs simulation is never hidden).
- [ ] Every OHLC row valid (script aborts otherwise); no duplicated/overlapping bars.
- [ ] POC = real max-volume level; VAH/VAL from the stated value-area %; Fixed-Range dates shown.
- [ ] Entry/SL/targets sit on real prices; SL derived (exit-high + a disclosed margin), R omitted unless real.
- [ ] The chart is reproducible from the saved CSV + `scenario.json`.
