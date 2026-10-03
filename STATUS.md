# STATUS — 2026-10-03

## Phase
Phase 1 (scoping + infrastructure) **done**. Phase 2 (real data + research) **BLOCKED**: no market data reachable and no account information yet.

## Done (verified by runs)
- Bid/ask 1m engine with spread, commission, swap (triple day), slippage, latency, rejection, partial fills, order expiry, margin/stop-out, conservative intrabar policy. Same per-bar core for the backtest and the paper runner.
- Independent risk engine: risk-based sizing (rounds down, rejects below min lot), position/risk/trades/day/margin/spread limits incl. pending orders, daily loss halt, permanent drawdown halt, kill switch, cancel + retried flatten.
- Paper runner: state persistence/restart, duplicate-order protection, stale-bar suppression, reconciliation, live mode refused without approval.
- H1–H5 pre-registered (N=62 trials) with frozen splits, budget and acceptance criteria (before any real data).
- Walk-forward pipeline with block bootstrap, deflated Sharpe, Holm, stress/neighbour/concentration tests.
- Tests: **58 passed** (`reports/pytest_last.txt`), including look-ahead truncation test with negative control, research/paper parity with restart, 16 regression tests from the independent review (each verified to fail on the pre-fix code).
- Independent review: 12 + 3 defects found and fixed (`reports/REVIEW_1.md`), including a critical one (intraday exits were not firing).
- Method controls (SYNTHETIC, code evidence only): null random walk → all 5 REJECT (`reports/synthetic_dryrun/`); injected edge → only H5 long (3,8) detected, verdict CANDIDATE_PENDING_USER_LIMITS (`reports/synthetic_edge/`). Even with that strong injected edge, only **62%** of days were profitable: a frequent-daily-profit goal does not follow from a real edge.

## Blockers
1. **Data**: egress policy denies `datafeed.dukascopy.com` and `huggingface.co` (403 at proxy). Fix: owner adds these domains to the environment's allowed domains (free). The HF connector cannot stream 40–650 MB files (max 80 KB per read through model context).
2. **Account facts missing** (PROJECT_SPEC §1): broker, account type, platform, capital/currency, risk limits, sessions/overnight policy, budget/constraints.
3. **Broker instrument spec** missing → no sizing approval; feasibility only illustrative (`reports/feasibility_template.txt`).
4. `configs/acceptance.json` user_limits are null → no strategy can reach ACCEPT.

## Next step (in order, once unblocked)
1. `python3 scripts/fetch_dukascopy.py --start 2015-01-01 --end 2026-10-01` → QA report → verify price divisor and DST/session structure.
2. Fill `configs/instrument_<broker>.json` (verified) and `user_limits`; run feasibility on real stop distances.
3. `python3 scripts/run_research.py --data data/processed/XAUUSD --spec ...` (WF only; hold-out stays locked).
4. Independent review of results → freeze → single hold-out → paper trading plan.

## Experiments
EXPERIMENTS.csv rows before commit d2df1b8 are superseded (D-014). No real-data experiment has been run.
