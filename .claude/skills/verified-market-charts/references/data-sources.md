# Data-source playbook (autonomous — never ask the user for files)

Auto-pick the instrument from the content topic, then fetch via the available MCP data tools (load schemas with
ToolSearch, e.g. `select:mcp__Alpha_Vantage_MCP_Server__TIME_SERIES_DAILY`).

## Instrument selection by topic
| Topic | Preferred instrument / timeframe |
|---|---|
| ICT / SMC / liquidity / structure | XAUUSD M5–M15 (or GLD daily if intraday gated) |
| Volume Profile / Footprint / Order Flow | GC futures (COMEX, centralized volume) → **fallback GLD daily** |
| VWAP / Volume | GC futures default → **fallback GLD daily** |
| Psychology / loss anatomy | whichever market shows the behavior most clearly |
| Precise entry detail | M1–M5 | Structure/liquidity | M15 |

## What actually works on the current keys (verified 2026-08)
- **Alpha Vantage `TIME_SERIES_DAILY` (symbol GLD)** → real daily OHLCV **with real NYSE exchange volume**, free.
  This is the reliable Mode-B source for gold Volume-Profile/VWAP/Volume lessons. Returns `timestamp,open,high,low,close,volume`.
- **Gated on the current keys** (don't stall on these — fall back and disclose): FMP `commodity`/`chart`
  (Starter+ plan), Alpha Vantage intraday `TIME_SERIES_INTRADAY` / `FX_INTRADAY` (premium/rate-limited).
- GC futures COMEX intraday (ideal for true volume/footprint) needs a paid feed; if unavailable, use GLD and
  disclose that it's the gold ETF with real exchange volume rather than faking futures data.

## Fetch → save → build
1. Fetch (csv datatype), e.g. `TIME_SERIES_DAILY(symbol="GLD", outputsize="compact"|"full", datatype="csv")`.
2. Save raw rows verbatim to `data/<symbol>_<tf>.csv` with header `timestamp,open,high,low,close,volume`.
   (Saving to a file makes the chart reproducible and lets `build_scenario.mjs` process it.)
3. Run `build_scenario.mjs` (see SKILL.md) → `scenario.json`.

## Honesty
- Disclose the exact source + dates on the chart (`references/source-modes.md`).
- ETF proxy (GLD) is fine for a real-volume VP lesson **as long as it's disclosed**; don't label GLD data as GC
  futures. Don't put XAUUSD on data that isn't XAUUSD.
