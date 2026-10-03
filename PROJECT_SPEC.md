# PROJECT_SPEC — account, market and execution

Status legend: **[CONFIRMED]** documented by the owner/broker · **[ASSUMED]** working assumption, must be confirmed · **[MISSING]** unknown, blocks dependent work.

## 1. Account (all [MISSING] — requested from the owner, see STATUS.md)
| Item | Value | Status |
|---|---|---|
| Broker / legal entity | — | MISSING |
| Account type (ECN/raw vs standard, hedging vs netting) | — | MISSING |
| Platform / API (MT5, cTrader, FIX, REST) | — | MISSING |
| Capital and account currency | — | MISSING |
| Max risk per trade / daily loss / total drawdown | — | MISSING |
| Allowed sessions; overnight / weekend holding | — | MISSING |
| Research budget (data, compute) | 0 (no purchases authorised) | CONFIRMED by brief |

Existing repo context (not treated as current account facts): a TradingView→Claude→Telegram webhook (`tv_claude_bridge.py`) for XAUUSD alerts, and reel material using an MT broker feed in UTC+3 server time. This suggests XAUUSD on an MT-style broker, **[ASSUMED]**, to be confirmed.

## 2. Instrument (XAUUSD) — must come from the broker's symbol specification
Template with typical retail values: `configs/instrument_xauusd_TEMPLATE.json` (`verified: false`).
Required fields: contract size, tick size/value, volume min/step/max, leverage/margin rate, stops level, freeze level, commission, swap long/short and triple-swap day, trading sessions and holidays, server time zone.
Until a verified spec exists: no position sizing is approved and no profitability statement is made.

Feasibility rule (implemented in `scripts/feasibility.py`, risk engine identical): volume = floor_to_step(risk_budget / ((stop distance + cost allowance) × contract_size + 2 × commission)). If the result is below the minimum volume the trade is **rejected**, never rounded up.
Illustrative (template spec, 100 oz/lot, 0.01 min lot, 0.40 cost allowance, 0.5% risk): minimum capital for one 0.01-lot trade = 480 / 1080 / 2080 / 4080 (account ccy) for stops of 2 / 5 / 10 / 20 $/oz (`reports/feasibility_template.txt`). UNVERIFIED.

## 3. Data
Primary (planned): Dukascopy tick bid/ask → 1-minute bid/ask bars (free). **Blocked**: network policy denies `datafeed.dukascopy.com`.
Secondary: HF mirror of a Kaggle MT feed (single price series, unknown server TZ, tick-count volume, ends 2025-10-01). Cross-check only; reading it through the HF connector passes the content through the model context (impractical above a few MB). Direct download blocked (`huggingface.co`).
Execution-broker data: not available until the broker is known. Dukascopy spreads are a **proxy** for the user's broker; paper trading must measure the real spread/slippage.
Volume: only tick counts exist; never treated as centralised volume. No order-flow data is fabricated.

## 4. Execution model (backtest = paper)
See docstring of `tbot/engine/sim.py`. Summary: next-bar-open market fills at ask/bid + adverse slippage; stop = stop-market (gap → fill at open); TP = limit (no positive slippage); ambiguous SL/TP within a bar → SL (`intrabar=worst`), `best` only as a sensitivity bound; orders older than 5 min at execution are cancelled; random rejection and partial-fill caps available; swap per rollover (17:00 NY), triple on the configured weekday; margin check on entry and stop-out at 50% margin level.

## 5. Risk controls (`tbot/risk/engine.py`, independent from strategies)
| Control | Behaviour |
|---|---|
| Risk per trade | sizing by stop distance + cost allowance; floor to step; reject below min |
| Max open positions / total open risk | reject new entries |
| Spread filter | reject if spread at decision > `max_spread` |
| Max trades per day | reject |
| Margin usage cap | reject |
| Daily loss limit (vs day-start equity, intrabar worst mark) | `flatten`: block new + close all at next open; or `block_new` — resets next trading day |
| Max drawdown (vs peak equity) | permanent halt (flatten or block) until manual reset |
| Kill switch (`state/KILL` file) or reconciliation mismatch | permanent halt + flatten |
| Stale bar (> 3 min late) | no new decision on that bar |
| Duplicate orders | deterministic client ids; broker rejects repeats (persisted across restarts) |
A stop-loss is not a guaranteed price; daily limits can be exceeded by gaps. This is measured (worst day) and reported.

## 6. Operating stages
1. Code tests + historical replay → 2. paper trading (SimBroker on live bars, then broker demo) → 3. compare execution vs assumptions → 4. **limited live only after explicit owner approval** → 5. gradual scale-up on evidence. The live adapter is not implemented; `LiveRunner(mode="live")` refuses to start without approval.
