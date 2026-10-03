# Independent review #1 — engine, risk, strategies, research pipeline (2026-10-03)

Reviewer: separate agent, read-only, adversarial, with its own reproduction scripts.
Verdict at review time: **FAIL — not yet computationally trustworthy.**
Confirmed correct at the time: balance accounting (sum of trade net = final equity − initial = sum of daily P&L, incl. swap, partial fills, rejects, latency), bid/ask sides, slippage sign, gap-through stop fills, intrabar-worst policy, causality of daily features, PSR / expected-max-SR / Holm / BH / stationary-bootstrap formulas.

| # | Severity | Defect | Fix | Regression test |
|---|---|---|---|---|
| 1 | CRITICAL | 16:30 NY exit of H1–H3 fired at 18:00 NY (evening bars belong to the same trading day) → positions held overnight/weekends | exit mask bounded to [16:30, 17:00] NY, persistent | `test_d1_*` |
| 2 | HIGH | H5 entry/exit required an exact minute bar; missing bar → multi-day hold | entry window + persistent exit outside holding window | `test_d2_*` |
| 3 | HIGH | rejected/expired closes never retried | persistent exit flags; flatten re-issued every bar while a halt is active | `test_d3_*` |
| 4 | HIGH | kill switch did not cancel pending entries; late fills never flattened | `_cancel_entries` + flatten after fills | `test_d4_*` |
| 5 | HIGH | reconcile mismatch never flattened | flatten driven by `RiskEngine.must_flatten` state, not a one-shot trigger | `test_d5_*` |
| 6 | HIGH | limits ignored pending orders (latency ≥ 1 bypassed max positions/risk/trades) | pending entries counted in `size_order` | `test_d6_*` |
| 7 | MEDIUM | WF picked grid[0] when no grid point qualified | ABSTAIN (flat) for that fold | `test_d7_*` |
| 8 | MEDIUM | zero effective embargo; trades filtered by UTC time vs daily labels by trading day | real 1-day gap; `entry_day` (trading day) used everywhere | `test_d8_*` |
| 9 | LOW-MED | Sortino used std of losses | downside deviation | `test_d9_*` |
| 10 | LOW | research slice by UTC timestamps | slice by trading day | `test_d10_*` |
| 11 | LOW | peak equity updated from bar lows | peak on close equity, limits on worst | `test_d11_*` |
| 12 | LOW | Holm family depended on `--only` | family fixed to the 5 pre-registered hypotheses (missing p=1) | code |

Plausible concerns addressed: stress tests now evaluate the parameters selected in the base walk-forward (no re-optimisation under stress); live runner refuses a buffer smaller than `strategy.min_buffer`; order creation time = bar close (expiry tolerance exact).

Open / documented limitations:
- Grid paths run once over the whole span; dollar `net_profit`/PF mix equity scales across folds (R-based expectancy does not). Minimum-lot granularity breaks scale invariance at small capital — results will be reported in R and % as primary.
- Paper fills after an outage use the next bar's historical open; wall-clock expiry to be added with the real data adapter.
- TP fills at the limit even on gap-through (conservative); triple swap day configurable (some brokers triple metals on Friday); daily equity excludes the exit commission of open positions; bootstrap "p" is P(bootstrap mean ≤ 0), a percentile approximation.

All synthetic experiments logged before commit "Fix independent-review defects 1-12" (EXPERIMENTS.csv rows of phase `pipeline-test-synthetic*` with the earlier commits) are **superseded** — they were produced by the defective code.

Re-verification: see REVIEW_1 addendum below (pending).
