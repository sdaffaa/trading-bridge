# DECISIONS

| ID | Date | Decision | Reason |
|---|---|---|---|
| D-001 | 2026-10-03 | Work on branch `claude/trading-bot-research`; keep the existing webhook bridge untouched. | Separate R&D from the existing alert tool. |
| D-002 | 2026-10-03 | Instrument focus XAUUSD (assumed, pending owner confirmation). | Only instrument present in the repo (bridge + reel data). Re-evaluate when the owner answers. |
| D-003 | 2026-10-03 | Primary data = Dukascopy ticks → 1m bid/ask bars; HF/Kaggle MT feed = cross-check only. | Need real bid/ask and known UTC timing; the HF file has a single price, unknown TZ and an unknown broker. |
| D-004 | 2026-10-03 | Instrument specs carry `verified`; unverified specs are for code tests/relative comparisons only. | Brief: no sizing/profit claims on undocumented assumptions. |
| D-005 | 2026-10-03 | Bar-level engine on 1m bid/ask, decision at close → next-open fill; ambiguous SL/TP → SL; 'best' only as a bound. | 1m bars cannot order intrabar events; conservative default with sensitivity bound (brief §5). Tick-level resolution can be added once ticks are available. |
| D-006 | 2026-10-03 | Pre-register H1–H5, grids (N=62), splits, budget (150), acceptance thresholds before loading any real data. | Prevent selection bias / moving goalposts. |
| D-007 | 2026-10-03 | One shared `TradingCore.step` for backtest and paper runner; parity test incl. restart. | Brief §10: research and execution versions must match and differences be explained. |
| D-008 | 2026-10-03 | Share of profitable days is reported, not an acceptance gate. | Optimising it encourages negative-skew designs that conflict with capital protection. |
| D-009 | 2026-10-03 | Deflated Sharpe uses null estimator variance 1/(T−1), not empirical cross-trial SR variance. | Found with the synthetic positive control (before real data): cost-driven negative strategies inflated the cross-trial variance to 0.063 → SR0 = 0.57/day (≈9 annualised), rejecting an unambiguous injected edge. 1/(T−1) is the dispersion of SR estimates of skill-less trials, which is what the deflation should remove. Empirical variance is still reported. |
| D-010 | 2026-10-03 | Neighbourhood robustness perturbs only ordinal params (grid adjacency); H5 uses window boundaries ±1h; categorical params (stop mode, side) are not perturbed. | Synthetic positive control showed the old rule treated disjoint windows / opposite side as "neighbours", which is not a parameter-stability test. Fixed before real data. |
| D-011 | 2026-10-03 | Leakage test cuts the data right after firing rows (+ random cuts) instead of random cuts only. | A one-bar look-ahead negative control passed the random-cut version; the new version detects it. |
| D-012 | 2026-10-03 | Do not fetch market data through other GitHub repos or by streaming large files through the HF connector. | Session scope rules restrict GitHub to this repo; streaming tens of MB through model context is impractical and unverifiable. Owner asked to allow `datafeed.dukascopy.com` instead. |
