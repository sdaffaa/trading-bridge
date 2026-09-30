# Family H: statistical validation, meta-labelling and risk sizing

Every number below comes from the scripts in this folder:
- `s0_build.py`: rebuilds the trades.
- `s1_significance.py`: significance tests.
- `s2_pbo.py`: PBO and DSR.
- `s3_meta.py` and `s3b_meta_trades.py`: meta-labelling.
- `s4_sizing.py`: position sizing.

`hlib.py` holds the statistics code. All numbers were run through harness2.run. Nothing was selected on HOLDOUT. Periods: IS 2020-07..2023-06, VAL 2023-07..2024-12, HOLDOUT 2025-01..2026-07. OOS = VAL+HOLDOUT.

## Candidates, rebuilt exactly
Every candidate reproduces the numbers in its family's results.
- **A1:** the current EA. Family-A combo #1, a 3-TF majority vote, SL = TP = 3xATR(H1), trades placed back to back. Benchmark: A1_long, which goes long on every bar with the same exits.
- **E1, E2, E3:** the family-E top 3. E2 is E1 plus a not-Asia session filter, so it is nearly a duplicate. Benchmarks: E*_long (long on every bar, same exits) and E*_Lsame (long at the same entry bars).
- **C1:** reg 1h tp1.5 both, theta=0. It is reproducible from the cached seed-0 walk-forward predictions. Benchmark: C1_long (long at every H1 decision bar, same exits).

## 1. Significance (`s1_significance.csv`, `s1_joint.json`)
Column notes:
- Daily series: R is booked on the exit day, and weekdays with no exit count as 0.
- t_NW: Newey-West t-stat of the daily mean.
- DSR: computed on IS, the selection sample. It uses the null variance V[SR] = 1/T and the raw trial counts. Trials are correlated, so the raw counts make DSR conservative.
- RC / SPA: stationary bootstrap, mean block 10 days, 5000 draws. The differential is the strategy's daily R minus its always-long benchmark's daily R.

| cand | t/trade IS / VAL / HO / OOS | t_NW daily OOS | IS SR (ann) | DSR (family N) | DSR (all ~1.47M) | SPA p vs long IS / VAL / HO / OOS | alpha-vs-gold t OOS (beta) |
|---|---|---|---|---|---|---|---|
| A1 | 2.67 / 2.02 / 1.44 / 2.46 | 2.48 | 1.64 | 0.026 (N=641,368) | 0.018 | 0.001 / 0.29 / 1.0 / 1.0 | 2.39 (0.04) |
| E1 | 2.18 / 0.24 / 2.10 / 1.64 | 1.70 | 1.25 | 0.029 (N=11,156) | 0.001 | 0.07 / 1.0 / 1.0 / 1.0 | 1.19 (0.30) |
| E2 | 2.10 / 0.26 / 2.08 / 1.62 | 1.79 | 1.21 | 0.023 | 0.001 | 0.09 / 1.0 / 1.0 / 1.0 | 1.32 (0.24) |
| E3 | 2.14 / 0.82 / 0.84 / 1.18 | 1.16 | 1.14 | 0.018 | 0.001 | 0.03 / 1.0 / 1.0 / 1.0 | 0.88 (0.15) |
| C1 | 0.78 / 0.54 / 2.00 / 1.76 | 1.51 | 0.46 | 0.018 (N=300) | 0.000 | 0.000 / 0.30 / 1.0 / 0.47 | 1.43 (0.03) |

- **Joint test, all 5 candidates vs always-long:**
  - SPA p is 0.00 on IS, 0.61 on VAL, 1.00 on HOLDOUT and 0.78 on OOS.
  - RC p is 0.00 on IS, 0.48 on VAL, 0.92 on HOLDOUT and 0.76 on OOS.
- **Joint test vs zero (any profit at all):** SPA p is 0.075 on VAL, 0.094 on HOLDOUT and 0.028 on OOS.
- **Expected maximum Sharpe of zero-skill trials:** 2.77 (annualised) for A's 641k trials, 2.25 for E and 1.68 for C. Every IS Sharpe is below its bar.
- **DSR with an empirical cross-sectional V[SR]:** it is about 0 for all candidates (`s2_dsr_emp.json`). That variance is dominated by variants that lose to costs, so the value is not informative.
- **A1 long/short split:**

  | period | long trades | long R | long t | short trades | short R | short t |
  |---|---|---|---|---|---|---|
  | IS | 493 | +41 | 1.85 | 459 | +41 | 1.92 |
  | VAL | 294 | +48 | 2.83 | 274 | 0 | 0.00 |
  | HOLDOUT | 250 | +44 | 2.82 | 215 | -13 | -0.89 |

  All of A1's out-of-sample profit comes from the long leg.
- **Harness bug:** harness2.stats `green_days` counts a +1R/-1R day as green, because floating-point noise leaves an R-sum of about 1e-14. For A1 the true green share of exit days is 44.5 / 47.9 / 44.0%. harness2 reports 55.9 / 56.8 / 51.6%. E is not affected, and C only slightly.

## 2. PBO, CSCV with S=16 (`s2_pbo.json`)
The PBO below is computed on IS+VAL days. The matrices are daily R.

| trial matrix | N | PBO | mean OOS SR of the IS-best (ann) | P(OOS SR<0) |
|---|---|---|---|---|
| E top-200 by IS totR (the pool the finalists came from) | 200 | **0.88** | 0.04 | 0.42 |
| E random 200 | 200 | 0.25 | -0.49 | 0.79 |
| A top-50 IS/VAL list (100 rows) | 100 | **0.55** | 0.85 | 0.14 |
| A top list + 150 random MTF combos | 250 | 0.03 | 0.85 | 0.14 |

- The competitive pools overfit: E's is plainly overfit and A's is a coin flip.
- The low PBO values for the random pools only mean that variants which lose to costs keep losing.
- The regression slope of OOS SR on IS SR is between -0.7 and -1.1 for every pool.

## 3. Meta-labelling (`s3_meta.csv`, `s3b_meta_trades.csv`)
- **Method:** the triple barrier is the EA's own SL/TP. The secondary model is LightGBM on 1h causal features, with purged 6-fold CV inside IS and a 1-day embargo. The final model was fit on IS only.
- **(a) Events at every H1 close where A1 has a direction:**
  - AUC is 0.495 on IS out-of-fold, 0.510 on VAL and 0.522 on HOLDOUT.
  - The IS out-of-fold threshold picked was 0.50.
  - Filtered R: IS 18 / VAL 12 / HOLDOUT 19. Taking every event gives IS 65 / VAL 24 / HOLDOUT 22.
  - Filtered minus take-all, daily: NW t is -0.72 on VAL and -0.25 on HOLDOUT.
  - Adding bet sizing gives VAL 27 / HOLDOUT 20, with a deeper drawdown.
- **(b) Take/skip on the EA's actual trade sequence:**
  - AUC is 0.534 on IS out-of-fold, 0.480 on VAL and 0.477 on HOLDOUT.
  - The chosen filter (p>0.45) gives 49 / 31 R on VAL / HOLDOUT. The unfiltered EA gives 48 / 31.
  - Bet sizing gives 18 / 0.6 R on VAL / HOLDOUT.
- **Verdict:** meta-labelling does not improve VAL or HOLDOUT.

## 4. Sizing for A1 (`s4_sizing.csv`)
- **Method:** equity compounds per trade.
  - VT: risk × clip(σ_IS / σ_20d, 0.5, 2).
  - Kelly: estimated on IS. f* = 8.8% per trade; the lower bound of the 95% CI gives 2.2%.
- **Results by period:**

  | scheme | CAGR IS / VAL / HO | maxDD % IS / VAL / HO |
  |---|---|---|
  | FF 0.25% | 7.0 / 8.2 / 5.2 | -4.2 / -3.5 / -3.0 |
  | FF 0.5% | 14.2 / 16.8 / 10.5 | -8.3 / -6.8 / -5.9 |
  | FF 1% | 29.5 / 35.0 / 21.2 | -16.0 / -13.4 / -11.6 |
  | VT 0.5% | 13.7 / 17.4 / 14.6 | -8.6 / -6.2 / -6.4 |
  | VT 1% | 28.0 / 36.6 / 30.2 | -16.8 / -12.1 / -12.6 |
  | ¼-Kelly (2.2%) | 69 / 84 / 46 | -33 / -28 / -24 |
  | ½-Kelly (4.4%) | 145 / 182 / 84 | -57 / -50 / -47 |

- **Green days, FF:** 44 / 48 / 42% of exit days, which is 28 / 35 / 28% of weekdays. VT scores higher because flat days split into a win and a loss of different sizes, so the gain is partly an artifact.
- **Months:** 61-67% are green. The bootstrap probability of a losing month is 33-42%.
- **Always-long twin at FF 0.5%:** CAGR -5.0 / 12.2 / 18.6% (IS / VAL / HO).
- **Recommendation:** cap risk at 0.25-0.5% per trade and use VT, not Kelly. The DSR is about 0.03 and the Kelly estimate is dominated by estimation error.

## Verdict
- No candidate shows statistically significant skill beyond the gold rally once multiple testing is accounted for:
  - Every DSR is ≤ 0.03.
  - No candidate beats always-long with the same exits out of sample (SPA p ≥ 0.47).
  - PBO is 0.55 for A's pool and 0.88 for E's pool.
  - A1's OOS profit is all from the long leg.
- A1 is the most robust candidate: it is positive in all periods, OOS t = 2.46, and alpha-vs-gold t = 2.39 OOS.
- That evidence is not enough to claim an edge, because A1 was drawn from 641k trials and its short leg fails out of sample.
