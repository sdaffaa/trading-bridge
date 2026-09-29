# Family E: profit objective (harness2.run / harness2.stats)

Scripts, in run order:
- `common.py`: builders and evaluation.
- `s1_screen.py`: 215 entries x exit grid, IS only.
- `s2_filters.py`: filters and time exits on the best bases, IS only.
- `s3_validate.py`: IS rank to VAL.
- `s4_holdout.py`: final 10, run once.
- `s5_null.py`: random-entry null.

Every dirs array is masked to the period being evaluated, so selection never sees VAL or HOLDOUT.

## Scope
- **Trend entries:** Donchian 10/20/55 (flip, state and fresh-breakout modes), EMA 10x50, 20x100 and 50x200, Supertrend(10,3) and (10,2). Timeframes M15, M30, H1, H4, D1.
- **Trend exits:** SL of 1, 1.5, 2 or 3 x ATR14(TF). TP at 1.5, 2, 3 or 5 x SL, each with and without a chandelier trail of 1 x SL. Also trail-only (no TP) at 0.5, 1 or 1.5 x SL.
- **Pullback entries:** trend on H1, H4 or D1 (EMA50>EMA200, or close>EMA50 with EMA50 rising), combined with an RSI2 (10/5) or RSI14 (30/40) dip on M15, H1 or H4.
- **Session breakouts:** 8 range and window definitions (Asia to London, first London hour, NY 13:30, and others). SL is 0.5 or 1 x the range, or 1 or 2 x ATR_H1. TP is 1 to 5 x SL, with a trail option. Time exit 0 or 360 bars.
- **Volatility contraction:** NR7, NR4, inside bar and NR7+IB on H1, H4 and D1, plus Bollinger squeezes on M30 to D1.
- **Mean reversion:** Bollinger fade at 2, 2.5 and 3 sd, RSI2 and RSI14 extremes, and a daily-TWAP (VWAP proxy) deviation fade. TP at 0.5 to 2 x SL, time exits 0, 240 or 1440 bars.
- **Filters:** sessions (7-17, 12-17, not Asia), ADX (H1, H4, D1), ATR regime (high or low vs its 500-bar median), D1 EMA50 and EMA200 trend, H4 EMA50 trend, and combinations. Time exits of 60 to 7200 M1 bars.
- **Totals:** 11,156 distinct variants were tested on IS. 666 met n>=150 and PF>1.1. The top 50 (at most 3 per entry) went to VAL and 28 had VAL>0. The final 10 are the best by IS rank with VAL>0, at most 2 per entry, with identical-trade duplicates removed.

## Final 10 (totR / R per trade / PF / green-days% / maxDD / trades)
| # | spec | IS | VAL | HOLDOUT | credible |
|---|---|---|---|---|---|
| 1 | pb D1 EMA50-slope trend + H1 RSI14<40, SL1.5ATR_H1, TP5R | 91/0.32/1.42/24.6/-19/281 | 7/0.04/1.05/20.0/-26/161 | 60/0.50/1.67/27.8/-15/120 | yes |
| 2 | same as #1 + not-Asia filter (6-21 UTC) | 85/0.32/1.41/24.3/-21/263 | 7/0.05/1.06/19.1/-16/143 | 55/0.55/1.73/27.7/-13/101 | yes |
| 3 | Donchian20 M30 state, SL3ATR_M30, TP5R | 84/0.34/1.44/32.1/-11/246 | 24/0.16/1.20/29.0/-18/150 | 27/0.15/1.18/28.9/-28/183 | yes |
| 4 | pb H1 EMA50-slope + M15 RSI2<10, SL3ATR_M15, TP5R, H1 vol-high | 72/0.27/1.34/25.0/-17/270 | 14/0.08/1.10/20.7/-27/166 | 85/0.71/2.00/35.4/-11/119 | yes |
| 5 | as #4 but D1 EMA50 direction filter instead of vol | 70/0.18/1.23/23.2/-22/380 | 32/0.15/1.18/24.0/-24/220 | 82/0.41/1.54/30.3/-20/200 | yes |
| 6 | EMA50x200 M30 state, SL3ATR, TP3R, H1 vol-high | 69/0.25/1.36/39.0/-14/279 | 28/0.16/1.22/37.1/-14/176 | 37/0.18/1.25/39.1/-24/207 | yes |
| 7 | Supertrend(10,3) H1 state, SL3ATR, TP1.5R, time exit 7200 | 68/0.11/1.19/53.8/-16/642 | 14/0.04/1.07/50.2/-28/359 | 48/0.16/1.30/53.0/-9/305 | yes |
| 8 | EMA10x50 M30 state, SL3ATR, TP5R | 64/0.24/1.30/30.5/-22/266 | 44/0.28/1.35/32.4/-19/160 | 13/0.07/1.09/28.0/-25/185 | yes |
| 9 | Donchian20 H1 state, SL2ATR, TP5R, H4 EMA50 direction | 64/0.18/1.23/29.0/-30/350 | 76/0.34/1.44/32.5/-17/224 | 36/0.19/1.24/28.6/-25/186 | yes |
| 10 | Donchian10 M30 fresh breakout, SL2ATR, TP5R, 12-17 UTC | 64/0.18/1.22/24.6/-31/362 | 66/0.31/1.40/25.9/-29/210 | 19/0.08/1.10/22.1/-30/233 | yes |

## Long/short split and always-long baselines (totR IS / VAL / HOLDOUT, same exits)
Two baselines are shown. L_same goes long at the same entry bars as the strategy. L_every goes long on every bar and re-enters after each exit.

| # | strategy | long only | short only | L_same | L_every |
|---|---|---|---|---|---|
| 1 | 91/7/60 | 47/24/64 | 36/-17/-2 | 30/44/60 | 0/77/118 |
| 3 | 84/24/27 | 21/61/73 | -14/-55/-42 | 6/58/89 | 6/58/89 |
| 4 | 72/14/85 | 32/52/61 | 6/-33/-20 | 24/61/65 | 8/63/78 |
| 5 | 70/32/82 | 39/57/75 | 28/-26/5 | 21/82/85 | 8/63/78 |
| 9 | 64/76/36 | 34/55/59 | -18/8/-22 | 27/47/66 | 9/63/80 |

(The other rows are in `final10_holdout.csv`.)

## Selection-bias null (`s5_null.py`)
- Random-direction entries at random H1/M30 closes were run through the same 44-exit trend grid, 2,640 variants in all.
- Their best qualifying IS totR was 99, which is higher than our best of 91 from 11k variants.
- 6.5% of the null variants qualified, against 6.0% of the real variants.
- Taking the best-IS variant per random set, 14 of 34 were credible. Their median VAL was -1 and median HOLDOUT +11.

## Conclusion
- All 10 finalists are credible (R>0 in IS, VAL and HOLDOUT), but none beats always-long with the same exits over VAL+HOLDOUT. Strategy vs L_every, VAL+HOLDOUT totR: #5 114 vs 141, #9 112 vs 143, #1 67 vs 195.
- Their IS advantage is not distinguishable from random entries.
- Out of sample, the short legs lose and the long legs roughly match the always-long baseline.
- The profit in 2023-2026 comes from gold's rally, captured by wide-SL, 3-5R-target, long-biased exits.
- The one repeatable ingredient is the exit geometry: wide ATR stop (2-3x), TP 3-5R, no tight trail.
