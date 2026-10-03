# CLAUDE.md — trading-bridge (XAUUSD intraday R&D)

Read STATUS.md first; continue from the last documented step. Do not redo research without a reason.

## Hard rules
- Every number in a report must come from a logged run (EXPERIMENTS.csv / reports/). Label results: SYNTHETIC (code tests), BACKTEST, PAPER, LIVE.
- No look-ahead: strategy row i uses bars[:i+1] only; `tests/test_leakage_metrics.py` must pass for every strategy.
- Never change configs/acceptance.json after seeing results. Changes need a DECISIONS.md entry *before* the next evaluation.
- Hold-out (configs/research.json `holdout_*`) is opened once, only via FREEZE.json + `tbot.research.registry.assert_can_open_holdout`.
- No martingale, no unbounded grids, no widening stops to hide losses, no raising risk to hit a daily target, no forced trades.
- No live trading, no purchases, no paid compute without the owner's explicit approval. No secrets in the repo (use env vars).
- Instrument specs with `verified: false` may not be used for sizing claims or profitability statements.

## Commands
```
pip install -r requirements-research.txt
python3 -m pytest -q                                   # all correctness tests (~2.5 min)
python3 scripts/run_research.py --synthetic             # pipeline null control (must REJECT all)
python3 scripts/run_research.py --synthetic --synthetic-edge --only H5_tod_drift   # positive control (must detect)
python3 scripts/fetch_dukascopy.py --start 2015-01-01 --end 2026-07-01   # needs network access to datafeed.dukascopy.com
python3 scripts/run_research.py --data data/processed/XAUUSD --spec configs/instrument_<broker>.json
python3 scripts/feasibility.py --spec <spec> --capital <C> --risk <r> --stops 2 5 10 --spread 0.4
```

## Layout
tbot/{data,engine,risk,strategies,metrics,research,live} · tests/ · configs/ · scripts/ · reports/
Shared per-bar logic: `tbot/engine/backtest.py::TradingCore.step` (backtest AND paper runner).
