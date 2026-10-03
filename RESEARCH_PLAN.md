# RESEARCH_PLAN — pre-registered (frozen 2026-10-03, before any real market data was loaded)

Goal under test: can a rules-based XAUUSD intraday bot produce **positive net expectancy after realistic costs, out of sample**, with frequent (not guaranteed) profitable days and bounded drawdown? A guaranteed daily profit is not a testable or achievable goal and is not targeted.

## 1. Data and splits (configs/research.json)
- 1-minute bid/ask bars from Dukascopy ticks (planned, blocked by network policy).
- Development/training start 2015-01-01. Walk-forward test windows 2019-01-01 → 2024-07-01 in 6-month folds, rolling 36-month training, 1-day embargo.
- **Final hold-out 2024-07-01 → 2026-07-01**, opened once after freezing code + params + criteria (FREEZE.json). Data after 2026-07-01 is reserved as an extra out-of-sample check.
- Known risk: 2024–2026 is a strong gold bull regime; hold-out may differ structurally from training. Reported, not hidden.

## 2. Hypotheses (code: `tbot/strategies/hypotheses.py`)
Common: signals on mid, execution on bid/ask, one position at a time, all intraday hypotheses flat by 16:30 NY (no overnight/weekend exposure), stops always set.

| ID | Why an edge might exist | Suits | Fails when | Rules | Grid (trials) | Cost risk | Rejected if |
|---|---|---|---|---|---|---|---|
| H1 NY opening-range breakout | COMEX open (08:20 NY) + US data at 08:30 concentrate information and order flow; breakouts of the first range may continue | trend/news days | choppy, low-vol days; false breaks | range = high/low of [08:20, 08:20+R); first 1m close beyond range before 11:30 NY; stop = opposite side or mid; target RR or time exit 16:30 NY | R∈{10,30,60} × stop∈{opp,mid} × RR∈{1,2,none} = 18 | tight ranges → spread is a large share of risk | any frozen gate fails OOS |
| H2 London breakout of Asian range | Asian session is thin; London open brings liquidity and repricing; range break may mark the day's direction | London trend days | range already wide; Asia news days | range 00:00–07:00 London; entry 07:00–10:00 London on close beyond range ± buffer×width; stop opp/mid; RR or time exit | buffer∈{0,0.1} × stop × RR = 12 | moderate | same |
| H3 Intraday momentum | Documented intraday momentum (early-session return predicts late-session return) in futures; hedging/flow persistence | trending macro days | reversal days, low vol | sign of return from previous close to 10:00 or 12:00 NY, only if |r| > k×20d vol; stop m×ATR14(daily); exit 16:30 NY | decision∈{10:00,12:00} × k∈{0,.25,.5} × m∈{.5,1} = 12 | low turnover (≤1/day) | same |
| H4 Asian-session mean reversion | Thin Asian liquidity → temporary dislocations revert | quiet nights | news shocks, trend nights | z of close vs L-bar mean beyond ±Z in 19:00–02:00 NY; target = mean; stop = s×rolling sd; exit at window end or after 60 bars | L∈{30,60} × Z∈{2,2.5,3} × s∈{2,3} = 12 | **high**: wider Asian spreads vs small targets | same |
| H5 Time-of-day drift | Session seasonality in gold returns (Asia vs London/NY fix flows) | stable seasonal regimes | regime shifts | enter at window start+5 min, exit at window end (NY hours), stop 1×ATR14 | windows {(18,3),(3,8),(8,12),(12,16)} × side{long,short} = 8 | low | same |

Total pre-registered trials **N = 62**. Robustness-only runs (stress, neighbours) are not selection trials.

## 3. Procedure
1. Data QA (`tbot/data/quality.py`) → `reports/data_quality.json`. FAIL stops the project.
2. For each hypothesis: run every grid point over dev+WF span; walk-forward selection by train-window daily Sharpe (≥30 train trades); stitch OOS test windows.
3. Statistics on stitched OOS daily returns: stationary block bootstrap (mean block 5 days), deflated Sharpe with N=62 and null variance 1/T, Holm correction across the 5 hypothesis p-values.
4. Robustness (only for candidates passing the core gates): spread ×1.5 + slippage ×2; +1 bar latency; 5% rejections; intrabar-best bound; ordinal-parameter neighbours (H5: window ±1h); removal of top 5% trades; random 10% trade drop; year concentration.
5. Freeze → single hold-out evaluation → decision. Then paper trading (§5).
6. Additions (extra filters, ML) only as separate pre-registered variants compared against the simpler parent; each adds to N.

## 4. Budget
- Trials: **150 configurations max** for selection (62 used by H1–H5). New hypotheses require a written rationale here before running.
- Compute: local container only (~2 s per simulated year per configuration). No paid compute.
- Data: free sources only. Purchases need explicit approval.
- Stop rule: if all hypotheses are REJECTED or INCONCLUSIVE after the trial budget, deliver the negative result. No open-ended search.

## 5. Paper-trading plan (pre-registered)
Minimum 8 weeks AND ≥ 60 trades (whichever is later). Continue only if: realised mean spread+slippage ≤ 1.5× backtest assumption; fill/reject behaviour within assumptions; P&L within the 5–95% band of bootstrap paths from the OOS distribution; no risk-control violation. Stop immediately on any risk-engine malfunction, reconciliation mismatch, or drawdown beyond the OOS 95th percentile.

## 6. Validation of the method itself (done, SYNTHETIC — code evidence only)
- Null control: random-walk data → all 5 hypotheses REJECT (`reports/synthetic_dryrun/`).
- Positive control: random walk + injected +0.004/min drift 03:00–08:00 NY → H5 long (3,8) is the only selected config and reaches CANDIDATE (`reports/synthetic_edge/`).
