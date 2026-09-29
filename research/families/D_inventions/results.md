# Family D: inventions, structure, and search-generated rules

Periods are the updated harness ones: IS 2020-07-01..2023-07-01 (selection), VAL 2023-07-01..2025-01-01, HOLDOUT 2025-01-01..2026-08-01.
Data before 2020-07 is used only for indicator warm-up. Trading starts 2020-01 for warm-up and is counted from IS start.
All numbers below come from the scripts in this folder, and each script's output is saved next to it (`*.out`, `*.csv`).

**Result: nothing passes `passes()`.** No candidate reached 60% on VAL. Only an overfit GA rule reached 60% on IS, and it fell to 53.7% on VAL and 49.8% on HOLDOUT, with fewer than 300 trades in each.

## Infrastructure
- `core.py` precomputes outcome tables. For every M1 bar it stores the result and exit bar of a long and a short 1:1 trade, using `harness.trade_once`, so the fill rules are identical. A consecutive strategy then becomes a pointer walk.
- `verify_core.py` checks this against the harness. On random directions the walk is **bit-identical** to `harness.run_consecutive` (19,609 trades). Evaluating one rule costs about 1 ms.
- `features_d.py` builds a causal library of 36 features. The value at bar i uses bars before i only, and higher-timeframe values come through `htf_to_m1`. The features cover:
  - returns at 5 horizons
  - day range position
  - previous-day high/low distance
  - round-number phase (10/50/100)
  - RSI at M15, H1 and H4
  - efficiency ratio, variance ratio at H1 and M5, M5 lag-1 autocorrelation, and an H1 Hurst estimate (rescaled range)
  - ATR regime
  - EMA distances at H1, H4 and D1
  - Asian range position and size
  - previous-day time-at-price POC, VAH and VAL
  - H1 fractal levels
  - TWAP distance

## Ideas tested (≈180,000 random rules + 3 GA runs + 375 hand-designed candidates)
1. **Asymmetry (`asym.py`).** This measures the unconditional first-passage P(win) for a long vs a short trade from every bar, by UTC hour, across 15 distance schemes ($1–13, 0.5–4×ATR_H1, 0.1–0.5% of price, and 0.25–0.5×ATR_D1).
   - Best single hour on IS: 54.0% long, at 22 UTC with 0.25% of price.
   - Picking the side per hour: at most 51.2% IS.
   - Picking the best (scheme, side) per hour on IS: 49.2% IS and 49.4% VAL.
   - Small stops are destroyed by the 0.30 spread: $1 → 35%.
   - During VAL, longs win more at every distance (for example 4×ATR_H1: 57.6% long vs 40.7% short). This is the 2023-24 bull drift, and it was **not** present in IS (49.2% vs 49.1%).
2. **Random rule search (`rule_search.py`).** 60k rules per run over 3 sets of distance schemes (180k rules). Each rule is either a VOTE of 1/3/5 threshold conditions or an IF (2–4 conditions) → side, ELSE a condition's sign. Thresholds are IS quantiles.
3. **Genetic evolution** on IS win rate, with elitism, tournament selection, crossover and mutation. Runs: 400×60 over all distance schemes, and 600×80 on each of two distance-scheme groups (2×ATR / 0.5% of price, and 1×ATR / 0.25% of price).
4. **Structure geometry (`structure.py`, 286 candidates).**
   - Levels: previous-day H/L, today's H/L so far, H1 fractals, Asian range, round $10 and $50, previous-day value-area edges, and the nearest level of any kind.
   - Four geometries: toward or away from the nearer level, and toward or away from the farther level, with distance equal to that level's distance.
   - Three distance floors: 0.5, 1 and 2×ATR.
   - Also tested: POC toward/away (distance to POC, or 1–2×ATR), value-area fade inside / continue outside, the Asian range size as the distance, and 0.1–0.8% of price with 7 direction rules.
5. **Regime switching (in `structure.py`).** In a trending regime the rule follows the trend, otherwise it fades. The regime filters were ER, VR (H1 and M5), Hurst, autocorrelation and ATR ratio, each with 2–3 thresholds. They were crossed with 4 trend signals and 2 distances.
6. **State inventions (`state_ideas.py`, 70 candidates).** These use a numba loop around `trade_once`. Variants:
   - barrier momentum or reversion: the next side is the direction price actually travelled last trade, or its opposite
   - win-stay/lose-shift and its inverse
   - follow for k streaks then fade, and the inverse
7. **LightGBM (`lgbm_dir.py`).** A model predicts P(long wins) and P(short wins) and always takes the higher one. It was trained on IS only.

Best IS win rate per idea family, with the VAL result for the same candidate:

| Family | Best IS wr | VAL wr |
|---|---|---|
| Structure | 51.2% | 52.2% |
| Regime switching | 50.3% | 48.1% |
| State | 53.3% | 49.8% (n = 283) |
| Asymmetry | 49.2% | 49.4% |
| LightGBM, 2×ATR | 64.8% (in-sample) | 47.6% |
| LightGBM, 0.5% of price | 64.3% (in-sample) | 48.0% |
| LightGBM, 1×ATR | 56.8% (in-sample) | 46.3% |

## IS → VAL decay (overfitting curve)
Random search over all distance schemes, 60k rules ranked by IS win rate:

| IS rank | mean IS wr | mean VAL wr |
|---|---|---|
| 1–10 | 55.07 | 53.79 |
| 11–100 | 54.00 | 52.05 |
| 101–1000 | 52.44 | 51.43 |
| 1001–10000 | 49.78 | 49.48 |
| rest | 47.34 | 47.61 |

- Spearman correlation between IS and VAL win rate is 0.47 over all rules but **0.13 within the top 1000**. The remaining correlation is mostly "bigger distance = less spread drag" plus a long bias.
- The top rules are all 4×ATR_H1, which gives about 290 VAL trades, below the 300 minimum.
- GA (`ga_curve.csv`): best IS 55.5→57.6→59.2→60.3% at generations 0/10/20/30. VAL for that best rule went 55.0→56.4→54.7→53.7%. More evolution increased IS and decreased VAL.
- GA on 2×ATR / 0.5% of price: IS 51.5→54.0%, VAL 45.2→47.0%, which is below the 50% coin flip.
- GA on 1×ATR / 0.25% of price: IS 49.3%, VAL 48.2%.
- For the two smaller distance groups, the top-1000 IS/VAL Spearman is 0.006 and 0.051, meaning no transfer.

## Final top 10 → HOLDOUT (`finalize.py`, harness `run_consecutive` + `stats`)
Selection was by IS, taking the best IS candidate from each idea family. Nothing was confirmed on VAL; HOLDOUT was run once only for this report.

| candidate | IS n / wr | VAL n / wr | HOLDOUT n / wr | passes |
|---|---|---|---|---|
| GA (all distances) #1, 4×ATR_H1 | 538 / 60.41 | 285 / 53.68 | 243 / 49.79 | no |
| Random-search best-IS, 4×ATR_H1 | 529 / 55.58 | 291 / 54.98 | 242 / 56.61 | no |
| State: follow barrier, fade after 4, 4×ATR | 522 / 53.26 | 283 / 49.82 | 238 / 56.30 | no |
| GA (2×ATR / 0.5%) #1, 0.5% of price | 2558 / 53.83 | 1045 / 46.99 | 3228 / 47.58 | no |
| State: barrier momentum, 4×ATR | 501 / 52.30 | 271 / 54.98 | 251 / 52.99 | no |
| Structure: previous-day level, toward farther | 447 / 51.23 | 364 / 52.20 | 317 / 52.68 | no |
| Volume profile: away from POC, distance = \|c−POC\| | 437 / 50.80 | 262 / 53.44 | 274 / 55.84 | no |
| Structure: value-area edge, toward farther | 687 / 50.51 | 425 / 51.29 | 484 / 55.79 | no |
| GA (1×ATR / 0.25%) #1 | 9784 / 49.30 | 3975 / 48.23 | 11835 / 48.42 | no |
| Asymmetry: per-hour (scheme, side) chosen on IS | 1580 / 49.24 | 985 / 49.44 | 2543 / 48.76 | no |

## Conclusion
- For an always-in-market 1:1 barrier trade on XAUUSD M1 with a 0.30 spread and the "both hit in one bar = loss" rule, the unconditional win probability is below 50%. It is about 46% at 1×ATR_H1 and about 49% at 4×ATR_H1.
- No structural, regime, profile, state or searched rule moved out-of-sample win rate above about 55%.
- The 55–56% seen in VAL and HOLDOUT for large-distance rules matches gold's 2023-26 up-drift that long-biased rules capture. It is not a stable edge: those same rules sit at or below 50% in other windows or with other thresholds.
- IS scores of 60% and above appear only through selection (GA, LightGBM), and they decay to 47–54% on VAL.
