# Family G: quant methods on XAUUSD (harness3, 1h bars, 10% vol target, spread 0.30 USD)

All numbers below come from the scripts in this folder: `g1_trend.py`, `g2_kalman.py`, `g3_meanrev.py`, `g4_regime.py`, `g5_season_stats.py`, `g5b_season_strats.py`, `g6_combo.py`, `select_top10.py`, `final.py` and `check_alpha.py`. Their logs are the matching `*.log` files.

## Protocol
- **Periods:** IS 2020-07..2023-06, VAL 2023-07..2024-12, HOLDOUT 2025-01..2026-06. The data ends on 2026-07-01.
- **HOLDOUT masking:** during research, `common.evaluate` sets positions to zero from 2025-01-01 and keeps daily returns only up to 2024-12-31. Only `final.py` and `check_alpha.py` touch HOLDOUT, and only for the 10 pre-selected configs.
- **Fitting:** every scalar, weight and model parameter is fitted on IS only. The exception is the HMM, which is refit each quarter on an expanding window using only past data; its filtered probabilities come from a forward-only pass, with no smoothing.
- **Sizing:** position = forecast (mean |f| = 1 on IS, capped at ±2) × `harness3.vol_target` leverage. That leverage is 10% annual vol on trailing 480 1h bars, capped at 3.
- **Buffer (Carver):** trade only when |target − current| > 0.10 × leverage, or go flat at once when the target is 0.
- **Clock:** HistData timestamps are NY local time + 5h; Tickstory data (2026) is UTC. `common.NY` maps both to New York wall-clock time. The London-fix windows use real Europe/London times.
- **Trial count:** 630 strategy configs, of which 547 give unique return streams (Kalman "tstat" equals "slope" at steady state). There were also 39 seasonality hypothesis tests.
- **Selection rule, fixed before HOLDOUT:** keep configs with IS SR > 0 and VAL SR > 0 (183 of them). Rank by IS SR. Drop any config whose IS+VAL daily-return correlation with an already chosen one is above 0.95. Keep 10.

## Findings by family (IS / VAL Sharpe, zero-days included)
1. **TSMOM / EWMAC** (100 configs).
   - Long/short trend is weak on IS: the best is ewmac 128/512 LS at 0.14 / 0.37.
   - Intraday horizons (4h-12h) lose badly after costs: tsmom_sign_4h_LS is −3.2 / −2.6, with turnover of 2000× notional per year.
   - Long-flat versions work better: tsmom_ra_10d_LF 0.58 / 1.17, ewmac128_LF 0.48 / 1.00. Most of that is long-gold beta: VAL alpha against vol-targeted B&H is about 0.
2. **Kalman local linear trend** (76 configs).
   - MLE on IS (statsmodels UnobservedComponents) puts the slope variance at about 0. The vol-normalised gold path is a pure random walk with no trend component.
   - The best grid point (q_level = 1, q_slope = 1e-5, LF) scores 0.53 / 1.13. It is highly correlated (0.94) with EWMAC.
3. **Mean reversion** (316 configs). Median IS SR −0.50, median VAL SR −0.66.
   - Stationarity gates (ADF, VR, Hurst, half-life) do not rescue it.
   - The best IS config, OU L240 z2.5 with a Hurst gate (LF), is 0.66 IS and −0.71 VAL.
   - TWAP/daily-mean reversion loses in both periods (−0.1 to −1.5). Intraday moves away from the day mean tend to continue.
4. **Regimes** (115 configs).
   - GARCH(1,1)-t fitted on IS: α = 0.053, β = 0.757.
   - GARCH sizing and filters change trend Sharpe by less than 0.05.
   - HMM "cut/flip in the high-vol state" overlays leave IS/VAL almost unchanged. They are the best HOLDOUT performers, with HAC alpha t of about 2-3 against vol-targeted B&H.
   - Markov-switching fitted on IS does not help on IS.
5. **Seasonality.** Of 39 hypotheses (hour of day, session, weekday, overnight vs day, London AM/PM fix windows), **0 pass BH-FDR at q = 0.10**.
   - The strongest raw effect is the Asia session, +3.4 bp/day with p = 0.008. That is about the size of one round-trip spread, so long-Asia loses after costs (−0.50 IS).
   - Nothing moved forward on statistical grounds.
   - Intraday momentum (the mirror of the failed TWAP reversion, z 1.5) scored 0.60 / 1.12 and was kept as a flagged diagnostic. It failed in HOLDOUT at −0.74.
6. **Combinations** (15 configs). Weights come from the IS covariance, positions are netted, and each combo is rescaled to 10% IS vol.
   - The best IS numbers of the study are ivar over 7 components (1.08 IS) and ERC trend3 + intraday (1.59 VAL). Diversification comes from the OU and intraday legs, which are uncorrelated with trend.

## Final (final.py; harness3.stats Sharpe, which excludes zero days; SR_all includes them)
See `final_top10.csv`, `top10_alpha.csv`.

- **Beat vol-targeted B&H on Sharpe in VAL and HOLDOUT:** none, whether measured with harness SR or SR_all.
- **Beat it on annual return in both periods:** 6 configs. They carry more exposure, with beta about 0.6-1.3.
- **DSR, IS sample, N = 547:** SR0 = 1.62 annualised, and every candidate is at or below 0.17. On IS+VAL, SR0 = 1.95 and every candidate is at or below 0.03.
- **Verdict:** nothing is significant after deflation. HOLDOUT gains are mostly long-gold beta during the 2025-26 rally. The exception is the HMM high-vol cut overlays, which show HOLDOUT alpha with t of about 2-3. That is suggestive, but it comes from a single out-of-sample episode.
