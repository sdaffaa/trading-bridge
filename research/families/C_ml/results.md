# Family C - ML / "trading by feel"  (periods: IS 2020-07..2023-06, VAL 2023-07..2024-12, HOLDOUT 2025-01..2026-07)

## Part 1 - always-in-market 1:1 win-rate objective (stopped early when objective changed)

Pipeline (`common.py`, `ml_run.py`): decision rows = completed M5/M15/H1 bars; features = 84-132 causal
features (multi-TF returns/EMA distance/RSI, ATR regime, candle anatomy of last 3 bars, distance to
fractal swings, HH/HL counts, rolling range position, prev-day/prev-week levels, day range position,
round numbers, hour/dow). Label = harness.trade_once both ways at the first M1 bar after the bar close.
Prediction forward-filled to every M1 bar -> harness.run_consecutive (no skipping).
Folds: IS = 6 half-year blocks, leave-one-block-out inside IS only (purged + 5-day embargo);
VAL/HOLDOUT = expanding walk-forward per half-year from 2020-07 (train rows must have exited before the block).

Completed: LightGBM (1h & 15m x 11 stop specs), logistic regression (1h & 15m x 7 specs), ExtraTrees
(1h x 7, 15m x 5), Renko/brick-pattern "feel" (momentum, reversal, learned K=2/4/6 pattern table x 6 specs),
baselines (`baselines.txt`). Not run before the pivot: MLP, RF, chart-picture MLP (`picture.py`),
kNN analogs (`knn.py`), M1-level model (`m1_level.py`), 5m LightGBM, ensembles (`ensemble.py`).

Stop specs: k x ATR(M15/H1), k in {0.5,1,2,3}; fixed $2/$5/$10. Baselines (random side): 0.5xATR15 ~33%,
1xATR ~42-47%, 2-3xATR ~47-49% (spread + "both in bar = loss" rule). Always-long in the 2024-26 rally:
3xATR1h VAL 53.3% / HOLDOUT 55.6%.

Top configs ranked by min(IS,VAL,HOLDOUT) win rate, all with >=300 trades (66 configs):

| config | IS wr (n) OOF | VAL wr (n) | HOLDOUT wr (n) |
|---|---|---|---|
| renko_table_K6, 2xATR1h | 48.75 (2193) | 49.24 (1190) | 51.09 (1059) |
| lr 1h, 3xATR1h | 48.72 (940) | 53.10 (533) | 51.71 (468) |
| lr 1h, 2xATR1h | 48.65 (2185) | 49.71 (1221) | 50.35 (1011) |
| lgb 15m, $10 | 48.59 (2204) | 49.16 (1371) | 48.53 (13405) |
| renko_table_K4, 2xATR1h | 48.52 (2232) | 49.62 (1197) | 49.76 (1025) |
| lr 15m, $10 | 48.40 (2225) | 49.93 (1350) | 49.01 (13337) |
| lgb 1h, $10 | 48.34 (2193) | 48.59 (1348) | 48.79 (13366) |
| renko_table_K6, $10 | 50.14 (2218) | 49.45 (1361) | 48.20 (13414) |
| renko_table_K2, 3xATR1h | 48.16 (949) | 50.27 (565) | 55.56 (459) |
| lr 15m, 3xATR15 | 48.11 (2729) | 48.48 (1483) | 51.28 (1603) |

Nothing passes(). Max out-of-sample win rate with >=300 trades: IS 50.37%, VAL 53.10%, HOLDOUT 55.94%
(ExtraTrees 1h 3xATR1h - explained by long bias during the gold rally; always-long gives 55.6%).
Row-level (decision) accuracy never exceeded ~57% on HOLDOUT and ~49% on IS.
Conclusion: no ML model found a 1:1 directional edge anywhere near 60%; results equal the random/always-long baselines.
