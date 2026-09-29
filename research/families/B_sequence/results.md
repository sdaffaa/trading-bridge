# Family B: sequence, state, calendar rules (XAUUSD, always in market, 1:1)

Periods (updated scope): IS 2020-07-01..2023-07-01 (selection + table learning only),
VAL 2023-07-01..2025-01-01, HOLDOUT 2025-01-01..2026-08-01. Spread 0.30, harness fill rules.
Stops (17): k x ATR14(M15/H1/D1), k in {0.5,1,2,3}; fixed USD {1,2,3,5,10}.
Tables are learned from IS-only long/short outcome labels at every 5th IS M1 bar; each cell needs
at least minc samples, otherwise the global IS default direction is used. The tables are then frozen.

| script | content | variants |
|---|---|---|
| s1_state_rules.py | win/loss keep/flip (4), majority of last N exits follow/fade, streak-length rules, learned exit-direction pattern table (N=2..8) | 646 |
| s2_candle_patterns.py | colour (N=1..8) and 3-state flat 0.1/0.3 ATR (N=1..6) patterns on M1/M5/M15/H1 (Markov order N), plus inverted tables | 5318 |
| s3_calendar.py | hour, dow, month, hour x dow, 15-min x dow, session open-to-now, vs day/week/month open, prev D/W/M dir, first-hour dir, London first hour, US 12:30-13:30 window, and crosses | 898 |
| s4_combos.py | top-5 patterns x top-5 calendar keys, and pattern x pattern, minc 200/1000/3000 | 247 |
| **total** | | **7109** |

Max IS win rate with at least 300 IS trades: **58.53%** (H1 colour pattern N=7, stop 1xATR(D1), n=434).
No variant reached 60% on IS. None reached 60% on VAL with at least 300 trades. **Nothing passes().**
Stops of 1xATR(D1) and larger produce fewer than 300 trades in VAL and HOLDOUT, so they cannot pass the trade-count rule.
Among variants with at least 300 VAL trades, the best IS win rate is 54.00% (H1_sign_N8, 3xATR(H1)), with 47.90% on VAL.

## Final top 10 by IS wr (s5_finalists.py, official run_consecutive/stats/passes)
| strategy | stop | IS n / wr | VAL n / wr | HOLDOUT n / wr |
|---|---|---|---|---|
| H1_sign_N7 | 1xATRD1 | 434 / 58.53 | 226 / 49.56 | 260 / 47.31 |
| H1_sign_N7 x sess_sign | 1xATRD1 | 440 / 57.73 | 222 / 50.90 | 266 / 56.02 |
| H1_tri0.1_N5 | 1xATRD1 | 433 / 57.51 | 227 / 50.66 | 250 / 52.80 |
| month x prevmonth | 1xATRD1 | 414 / 55.56 | 220 / 48.18 | 258 / 51.16 |
| H1_sign_N7 x dow | 1xATRD1 | 433 / 55.43 | 211 / 54.50 | 259 / 48.65 |
| H1_tri0.3_N6 | 1xATRD1 | 447 / 55.26 | 224 / 54.02 | 254 / 51.97 |
| M15_sign_N8 | 1xATRD1 | 436 / 55.05 | 224 / 45.98 | 249 / 51.00 |
| H1_tri0.1_N5 x sess_sign | 1xATRD1 | 429 / 55.01 | 225 / 51.56 | 262 / 52.29 |
| H1_tri0.1_N5 x H1_tri0.1_N6 | 1xATRD1 | 429 / 55.01 | 219 / 51.60 | 265 / 51.70 |
| H1_sign_N8 | 1xATRD1 | 426 / 54.23 | 221 / 50.68 | 244 / 48.36 |

Interpretation: the IS winners are all small-sample (about 430 trades) daily-ATR variants picked from
about 7000 tries. On VAL and HOLDOUT they drop back to about 46-56%. That is what selection noise looks
like, not a real edge. State rules (win/loss keep/flip, exit-majority, streaks) stay at about 50% or below after spread.
Raw per-variant results are in res_s1..s5_*.csv.
