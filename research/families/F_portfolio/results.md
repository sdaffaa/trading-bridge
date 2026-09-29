# Family F: expectancy re-rank, portfolios and daily management (objective: profit at the end of each day)

Harness: `harness2.run` (bid M1 bars, spread 0.30, SL-first when SL and TP fall in the same bar, one position per strategy).
Periods: IS 2020-07..2023-06 is used for selection. VAL 2023-07..2024-12 is also used for selection, as a filter. HOLDOUT 2025-01..2026-07 was run once, in `s5_final.py`.
While selecting, HOLDOUT is masked: the dirs arrays are set to 0 from 2025-01-01 (`common.build(holdout=False)`), so no HOLDOUT trade existed until s5.

## Pipeline (scripts, in order)
| script | what it does |
|---|---|
| `engine.py`, `test_engine.py` | A fast outcome-table engine that reproduces harness2 exactly. On random dirs it matches harness2 for all 5 exits: same n, same total R. |
| `s1_rank.py` | Re-ranks the family-A universe by R. It covers 792 signals x 2 (normal and inverted), plus 8,250 MTF combos (PROD, BOTH, MAJ, ALL, AGREE_else_fadeHTF). The MTF pool is the 5 best signals per timeframe by IS SQN. There are 7 SL rules (2xATR_M15, 1/2/3xATR_H1, 1/2xATR_H4, 1xATR_D1) and 5 exits: TP = 1, 1.5 or 2 x SL; trail = 1xSL with no TP; trail = 1xSL plus TP = 3xSL. In total 632,940 configs, 582,304 of them with IS n >= 300. |
| `s2_select.py` | Takes the IS top 400 by SQN. It keeps configs with VAL R > 0 and VAL PF >= 1.05, which leaves 69. It ranks them by min(IS SQN, VAL SQN scaled to IS length) and re-runs them in the real harness2. |
| `s3_portfolio.py` | Builds 9 portfolios: 3 methods x sizes 3, 5 and 10. **A** takes candidates in score order with a correlation cap of 0.5. **B** is greedy on IS Sharpe with a cap of 0.3. **C** is greedy on IS+VAL Sharpe with a cap of 0.3. The 3 with the best min(IS, VAL) Sharpe go forward. |
| `s4_manage.py` | Grid of daily management on IS only (479 settings per portfolio): daily lock +{1,2,3,5}R, daily stop -{1,2,3}R, realized mode vs equity mode (the equity mode flattens), max entries per day {2,4,8}, and vol scaling with exponent {0.5,1}. `psim` matches the harness2 sum within 0.5%; the gap comes from trades that cross the period edge. |
| `s5_final.py` | HOLDOUT, plus drawdown % and risk of ruin at 0.25, 0.5 and 1 % risk. |

## Key findings
1. **Ranking by expectancy has no out-of-sample power at the top.** Mean VAL SQN by IS-SQN vingtile rises from -4.4 in the worst vingtile to -0.40 in the middle, then falls to -0.64 in the best 5%. The IS top 400 had a mean VAL SQN of -0.69, and only 28% of them had VAL R > 0. The IS/VAL correlation of 0.72 comes only from costs, since small stops lose to the spread.
2. **The survivors failed on HOLDOUT.** None of the 5 best single strategies is credible. HOLDOUT PF was 0.76-0.93, and every one of them lost only on shorts; longs were positive in the 2025-26 gold rally. Their edge was mostly short-term mean reversion (inverted HMA/MACD-slope signals), and a strong trend broke it.
3. **Diversification raises green days and green months in-sample, but it cannot create an edge.** In IS, green days went from 46-49% for single strategies to 50-56% for portfolios, and green months from 64-78% to 83-89%. On HOLDOUT the portfolios had 38-45% green days, and 2 of the 3 lost money.
4. **Daily management hurt on IS for all 3 portfolios.** The IS optimum was *no* lock, *no* stop and *no* trade cap. Mean IS Sharpe was lower with every lock value, and the equity-mode flatten was worst. The one exception, vol scaling (exponent 0.5-1), added about +1-4% R at the same Sharpe, which is not meaningful. So the IS rule "no management" was carried forward.
5. **Bootstrap risk estimates from IS+VAL were badly optimistic.** For example, P_C5 at 0.5% risk had a bootstrap 1-year p95 drawdown of -9.0%, but its realized HOLDOUT drawdown was -36.5%.

## Final table (all from s5_final.py; R/day and green days% use only days with at least 1 closed trade, like harness2.daily)
| id | IS totR / R/day / gd% / gm% / ddR | VAL totR / R/day / gd% / gm% / ddR | HOLDOUT totR / R/day / gd% / gm% / ddR (dd%@0.5%) | credible |
|---|---|---|---|---|
| S1 | 82.4 / .208 / 47.5 / 75 / -9.7 | 43.2 / .214 / 46.5 / 67 / -9.1 | -29.1 / -.137 / 36.8 / 42 / -41.2 (-18.8%) | no |
| S2 | 77.6 / .191 / 48.9 / 78 / -9.0 | 40.2 / .195 / 46.1 / 67 / -13.6 | -12.0 / -.054 / 42.1 / 47 / -25.0 (-12.0%) | no |
| S3 | 72.9 / .216 / 48.2 / 67 / -9.7 | 30.3 / .185 / 47.0 / 67 / -10.2 | -11.4 / -.059 / 36.8 / 26 / -35.2 (-16.2%) | no |
| S4 | 64.5 / .188 / 45.9 / 64 / -11.2 | 25.9 / .157 / 43.0 / 67 / -7.6 | -18.4 / -.093 / 36.0 / 37 / -32.5 (-15.1%) | no |
| S5 | 70.1 / .172 / 48.3 / 72 / -9.8 | 28.3 / .132 / 43.5 / 67 / -21.8 | -8.0 / -.042 / 41.1 / 42 / -21.3 (-10.2%) | no |
| P_A10 | 809 / 1.10 / 52.0 / 86 / -30.0 | 309 / .846 / 52.1 / 83 / -32.7 | +7.6 / .020 / 45.1 / 37 / -92.6 (-38.4%) | yes (PF 1.01 = break-even) |
| P_C5 | 366 / .551 / 56.2 / 89 / -13.9 | 148 / .440 / 53.0 / 83 / -13.9 | -67.5 / -.194 / 41.4 / 32 / -88.2 (-36.5%) | no |
| P_A3 | 233 / .415 / 49.9 / 83 / -13.2 | 114 / .385 / 46.8 / 72 / -12.6 | -52.5 / -.161 / 38.0 / 37 / -75.9 (-32.1%) | no |

Definitions of S1-S5 and the portfolio members are in `s5.log` (legend) and `s2_pool.csv` (JSON spec). The dd% numbers use compounded daily equity; see `s5_risk.csv` for 0.25, 0.5 and 1 %.
VAL numbers are not out-of-sample: VAL was a selection filter.

## Verdict
Nothing here is deployable. The only "credible" item, P_A10, earns +7.6R over 19 months with a 92R drawdown, which is noise.
Family-A #1 (+32R HOLDOUT at TP=SL) had its HOLDOUT result published before this work, so it cannot be re-selected as a clean candidate here.
