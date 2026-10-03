# ACCEPTANCE_CRITERIA (frozen 2026-10-03; machine copy: configs/acceptance.json)

Thresholds were set before any real data was seen. They are project choices justified below, **not universal standards**. Changing them after results are visible is forbidden; any change requires a DECISIONS.md entry made before the next evaluation and downgrades existing evidence to development data.

Possible outcomes: **ACCEPT** (all gates pass incl. hold-out) · **REJECT** (any hard gate fails) · **INCONCLUSIVE** (insufficient sample) · **PENDING** (owner risk limits not yet given → cannot be accepted).

## A. Data
- QA verdict ≠ FAIL; coverage of expected session minutes ≥ 97% in research span.
- Real bid/ask spreads required (synthetic spreads not allowed for acceptance).

## B. Code
- `python3 -m pytest` passes at the frozen commit (incl. leakage truncation test with negative control, parity test, accounting tests).

## C. Out-of-sample walk-forward (base costs)
| Gate | Threshold | Why |
|---|---|---|
| OOS trades | ≥ 200, else INCONCLUSIVE | below this the CI on expectancy is too wide to separate a small edge from costs |
| Net profit | > 0 | |
| Profit factor | ≥ 1.15 | margin over cost-model error |
| Expectancy | ≥ 0.05 R / trade | edge must exceed plausible cost under-estimation (~0.05 R) |
| Bootstrap P(mean daily return ≤ 0) | ≤ 0.05 | serial dependence via block bootstrap |
| Deflated Sharpe (N = all trials) | ≥ 0.95 | multiple-testing / selection bias |
| Holm-adjusted p across hypotheses | ≤ 0.05 | family-wise error over H1–H5 |
| Positive WF folds | ≥ 60% | stability over time |
| OOS max drawdown | ≤ 0.75 × owner's max-drawdown limit | headroom: future DD is typically worse than backtest |

## D. Robustness
- Net > 0 under: spread ×1.5 + slippage ×2; +1 bar latency; 5% random rejections.
- ≥ 60% of ordinal-parameter neighbours net-positive in the WF period.
- Net ≥ 0 after removing the best 5% of trades; 5th percentile of net > 0 when 10% of trades are randomly dropped.
- No calendar year > 50% of net profit; ≥ 50% of years positive.

## E. Hold-out (opened once)
- ≥ 100 trades for a decision (else INCONCLUSIVE); net > 0; PF ≥ 1.0; max DD within owner limit.

## F. Reproducibility
- Re-running from a clean checkout with the logged commit, data hash, config hash and seed reproduces the metrics.

## Not acceptance criteria (deliberately)
- **Share of profitable days.** Reported (all market days and active days), but not a gate: optimising it pushes toward small targets/wide stops (negative skew), which conflicts with capital protection. Any such trade-off is shown numerically.
- **Win rate or historical profit alone.**

## Paper → live (owner approval required in any case)
See RESEARCH_PLAN.md §5.
