# Family A: exhaustive indicator / parameter grid (always-in-market, 1:1, XAUUSD)

Periods (the updated harness): IS 2020-07-01..2023-07-01 (selection only), VAL 2023-07-01..2025-01-01,
HOLDOUT 2025-01-01..2026-08-01. Data from 2018 is used only to warm up the indicators. Spread is 0.30. If SL and TP are both hit in the same bar, the trade counts as a loss.

## Method
- `core.py` has a fast engine. For each stop rule it computes, for every M1 bar, the long and short outcome and the exit bar. It uses segment-tree first-crossing searches and follows the same rules as `harness.trade_once`. Scoring a dirs array is then just a pointer chase over those tables. I checked it against `harness.run_consecutive`: IS n and win rate match exactly for all 100 validated configs.
- `signals.py` builds 132 signals on each of M5, M15, M30, H1, H4 and D1 (792 total). They cover:
  - price vs EMA/SMA/HMA/KAMA (lengths 5-200), MA slopes, and crosses of those four MA types
  - MACD in 3 settings: line, histogram and histogram slope
  - Donchian mid-position and breakout state, Supertrend x4, PSAR x3
  - Ichimoku: cloud, TK cross and kijun
  - DI (7/14/28), Heikin-Ashi colour, candle colour, linreg slope, Aroon
  - RSI (2-21) vs 50 and in 70/30 and 80/20 hold-zones
  - Stochastic (vs 50, K vs D, zone), Williams %R zone, CCI (sign and ±100 zone), z-score/Bollinger zones (1σ, 2σ), ROC (1-50)
  
  Each signal was also tested inverted, which covers both the contrarian and the momentum reading. Higher-timeframe values are aligned to M1 bars so they only use completed bars, with the same logic as `htf_to_m1`.
- There are 52 stop rules:
  - k x ATR14(tf) for k in {0.5,1,1.5,2,3,5}, on all 6 timeframes
  - fixed $ {1,2,3,5,8,12,20}
  - {0.05,0.075,0.1,0.15,0.2,0.3,0.5,0.75,1.0}% of the previous close
- Stage 1 (`grid.py`): 792 x 2 x 52 = **82,368 combos**. 72,837 of them have >= 300 IS trades.
- Stage 2 (`mtf.py`): multi-timeframe combos built from the 5 best IS signals per timeframe. With two ±1 signals, "agree, else follow the higher timeframe" is the same as trading the higher timeframe alone. So I tested:
  - products of pairs of signals
  - 3-timeframe majority votes
  - "all agree, else fade the highest timeframe"
  
  That is 5,375 combos x 2 (normal/inverted) x 52 stop rules = **559,000**, of which 494,428 have >= 300 IS trades.
- Stage 3 (`validate.py`): I took two pools and re-ran each config with the real `run_consecutive` + `stats`:
  - Pool A: the IS top 50 with n >= 300.
  - Pool B: the IS top 50 with n >= 700. Pool B exists because only about 700 IS trades are enough for VAL and HOLDOUT to reach 300. Only 1 of the 50 in pool A reached 300 trades in VAL.
  
  The final 10 were chosen by min(IS, VAL) win rate among configs with VAL n >= 300. Only those 10 were run on HOLDOUT.

## Multiple-testing picture (IS win rate, combos with >= 300 IS trades)
| set | combos | median | 99th pct | 99.9th pct | max |
|---|---|---|---|---|---|
| single indicators | 72,837 | 46.70 | 51.68 | 53.56 | 56.27 |
| MTF combos | 494,428 | 46.57 | 53.19 | 55.73 | 60.12 |
| all | 567,265 | 46.58 | 53.04 | 55.63 | **60.12** (n=326) |
| random coin-flip H1 signals (null, `null_random.py`) | 45,992 | 46.52 | 52.57 | 55.12 | 58.71 |

The largest IS win rates with n >= 700 trades were 54.2% (single indicators) and 55.1% (MTF). The random null reached 54.78%.
One combo cleared 60% on IS: 60.12% on n=326, a 3-timeframe majority with a 5xATR(H1) stop. It is out of reach of the 300-trade minimum in VAL, where it has ~170 trades.
The IS top 50 regressed to a mean VAL win rate of 48.2% for pool A and 49.1% for pool B.

## Final 10 (IS / VAL / HOLDOUT, real harness)
| # | combo | stop | IS n / wr | VAL n / wr | HOLDOUT n / wr |
|---|---|---|---|---|---|
| 1 | MAJ[H4 stoch5_KD, M5 px<HMA5 (inv), M15 MACD5_35_hslope (inv)] | 3xATR_H1 | 953 / 54.35 | 568 / 54.05 | 464 / 53.45 |
| 2 | MAJ[H4 stoch5_KD, D1 SMAcross5_10, M30 HMAcross20_100] | 3xATR_H1 | 944 / 54.13 | 555 / 51.53 | 467 / 52.89 |
| 3 | MAJ[D1 SMAcross5_10, H1 linreg50 (inv), M15 RSI14_zone80] | 1.5xATR_H4 | 1080 / 54.07 | 580 / 51.21 | 533 / 50.47 |
| 4 | MAJ[H1 px_vs_SMA200, M30 HMAcross50_200, M15 SMAcross50_200 (inv)] | 3xATR_H1 | 956 / 54.08 | 538 / 51.12 | 461 / 49.89 |
| 5 | MAJ[H4 stoch5_KD, H1 z200_zone1, M30 HMAcross20_100] | 3xATR_H1 | 945 / 54.07 | 555 / 50.81 | 469 / 53.09 |
| 6 | MAJ[D1 linreg10, H1 linreg50 (inv), M5 px_vs_HMA5 (inv)] | 5xATR_M15 | 856 / 54.21 | 469 / 50.75 | 529 / 49.53 |
| 7 | MAJ[M30 linreg100 (inv), D1 linreg10, M5 px_vs_HMA5 (inv)] | 5xATR_M15 | 856 / 54.21 | 469 / 50.75 | 529 / 49.53 |
| 8 | MAJ[H1 px_vs_SMA200, M30 linreg100 (inv), M15 RSI14_zone80] | 3xATR_H1 | 966 / 54.14 | 539 / 50.65 | 459 / 51.85 |
| 9 | MAJ[H4 stoch5_KD, H1 SMAcross10_50 (inv), D1 CCI14] | 1.5xATR_H4 | 1073 / 54.05 | 559 / 50.63 | 531 / 51.60 |
| 10 | MAJ[H4 stoch5_KD, M30 HMAcross20_100, M5 ichi_TK (inv)] | 3xATR_H1 | 921 / 54.07 | 517 / 50.29 | 471 / 53.08 |

Full rows are in `final10_holdout.csv` and `top50_is_val.csv`. The raw grids are `grid_is.parquet` and `mtf_is.parquet`.

## Verdict
**Nothing passes().** No combo reaches 60% on IS with enough trades for VAL and HOLDOUT to count.
The IS win-rate distribution is no better than random coin-flip signals under the same stop rules.
The best config's IS edge, about 54%, shrinks out of sample to 50-54%. That is roughly the 1:1 break-even after spread, with no sign of a 60% edge.
#1 held about 53-54% in all three periods (953 / 568 / 464 trades), but it is still far below 60%.
