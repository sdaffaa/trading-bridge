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

## Part 2 - profit objective (harness2; waiting allowed, any exits)

`profit.py`: LightGBM predicts the R outcome of a long and of a short opened at the first M1 bar after
each H1 (or M15) bar close, per exit geometry (SL = a x ATR(H1); TP = 1/1.5/2/3 x SL; trailing 1xATR;
time exits 60/240 bars; 0.5xATR SL with 2R TP; all with a 1-day time cap). Two targets: Huber regression on R
("reg") and win-classifier converted to E[R] ("cls"). Trade only if max predicted E[R] > theta
(theta in {0,.05,.1,.2,.3}); modes "both" sides or "long only". Same purged folds as Part 1 (IS OOF = LOBO
inside IS, VAL/HOLDOUT = expanding walk-forward). Official numbers from harness2.run, dirs non-zero only at
decision bars. 245 result rows (`profit_raw.tsv`, logs `log_profit_*.txt`), ranked by IS only (`select_profit.py`).

Always-long, same exits, every H1 bar (the rally benchmark): tp1.5 IS -293.9R / VAL -18.5 / HO +65.3;
tp3 IS -219.9 / VAL +29.1 / HO +116.9; trail1 IS -398.7 / VAL -33.8 / HO +151.8. Always-short loses everywhere.

Top by IS out-of-fold total R (IS n>=200):

| config (TF, geometry, mode, theta) | IS totR, n, R/t, PF, green%, maxDD | VAL | HOLDOUT | all>0 |
|---|---|---|---|---|
| cls 1h tp3 both 0.1 (IS #1) | +56.6, 1695, .033, 1.05, 47.7, -40.8 | -29.7, 837, -.035, 0.95, 45.7, -49.9 | +102.3, 792, .129, 1.19, 48.8, -36.0 | no |
| cls 1h tp3 long 0.2 | +30.9, 775, .040, 1.06, 43.0, -35.1 | +24.8, 343, .072, 1.11, 43.8, -31.0 | +56.5, 387, .146, 1.22, 45.6, -30.0 | yes |
| cls 1h tp1.5 long 0.3 | +30.0, 315, .095, 1.17, 51.4, -12.5 | +9.5, 83, .115, 1.21, 53.3, -8.5 | +8.3, 105, .079, 1.14, 48.6, -10.7 | yes |
| reg 1h tp1.5 both 0.0 | +25.4, 697, .036, 1.06, 48.1, -30.4 | +10.0, 225, .044, 1.08, 52.4, -10.5 | +34.3, 189, .181, 1.35, 52.1, -7.0 | yes |
| cls 1h tp1.5 both 0.3 | +22.3, 635, .035, 1.06, 48.2, -21.0 | -21.0, 216, -.097, 0.85, 43.1, -26.0 | +34.8, 161, .216, 1.42, 54.2, -6.2 | no |

Robustness (`profit_null.py`, `profit_diag.py`):
* Random-entry null (same decision bars, same trade count and long/short mix per half-year): all candidates
  are at the 99.5-100th percentile in IS (the model avoids the IS losers), but out of sample:
  cls tp3 long -> VAL 22nd / HO 21st pct (i.e. no better than random long entries in the rally);
  cls tp1.5 long -> 68th / 52nd; cls tp3 both -> 68th / 91st; reg tp1.5 both -> 96.5th / 94th.
* reg 1h tp1.5 both th=0 re-trained with 3 other seeds: IS +4.4/+31.8/+25.9, VAL -1.5/-2.2/-0.8,
  HOLDOUT +32.3/+44.6/+34.9 -> VAL is ~0, the all-positive result of seed 0 is not robust.
* Cost/volatility filter alone (random side when ATR1h > IS quantile) does not explain it: IS -67..-7R.

Verdict: no robust edge. The IS-selected best config fails VAL. Long-only "credible" configs mostly carry
the 2023-26 rally and don't beat random long entries in VAL/HOLDOUT. The most interesting signal is
reg 1h tp1.5 (both sides): it beats the random null in all three periods, but its VAL result is about
zero across seeds, and it trades only ~0.3/day at ~0.04R/trade in IS.
