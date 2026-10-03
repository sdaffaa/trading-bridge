# RUNBOOK — operation, monitoring, stopping (paper trading; live is NOT enabled)

## Start (paper)
`LiveRunner(strategy, spec, risk_cfg, exec_cfg, balance, state_dir="state/<name>", buffer_bars=...)`
and call `on_bar(t, bar)` for every CLOSED 1-minute bid/ask bar (UTC open time). A broker/data
adapter that delivers closed bars is still to be written once the platform is known.
Buffer sizes: H1/H2 ≥ 1500 bars, H4 ≥ 200, H3/H5 ≥ 30 trading days (43 200 bars).

## Restart after crash / disconnect
`LiveRunner.resume(strategy, "state/<name>")` restores positions, pending orders, risk state and the
set of used order ids (no duplicates). Bars with time ≤ last processed bar are ignored. Then call
`reconcile(broker_positions)`: any mismatch → kill switch + flatten + log `RECONCILE_MISMATCH`.

## Monitoring (state/<name>/events.jsonl)
Watch for: `RECONCILE_MISMATCH`, `rejected`, `expired`, `partial`, `stale_bar_signal_suppressed`,
`daily_halt`/`dd_halt` events, spread at fills vs backtest assumption, slippage per fill.

## Stopping
| Action | Effect | How |
|---|---|---|
| Kill switch | blocks new orders AND closes all positions at next bar open; permanent | create file `state/<name>/KILL` |
| Daily loss limit | per config: `flatten` (block + close) or `block_new`; resets next trading day (17:00 NY) | automatic |
| Max drawdown | permanent halt (flatten/block per config) | automatic; reset only by a human after review |
| Resume after kill/DD halt | requires review, new state dir or explicit state edit, logged in DECISIONS.md | manual |
Closing is a market order: the fill price is not guaranteed (gaps, slippage).

## Live trading
Disabled. Requires: accepted strategy, completed paper phase (RESEARCH_PLAN §5), a verified
instrument spec, a broker adapter, `live_approved=true` in config AND `TBOT_LIVE_APPROVED=1`,
and the owner's explicit written approval. Credentials only via environment variables.
