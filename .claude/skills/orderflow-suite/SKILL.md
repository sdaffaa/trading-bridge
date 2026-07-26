---
name: orderflow-suite
description: Build, extend, and maintain the all-in-one TradingView order-flow indicator in this repo (orderflow_suite.pine). Use whenever the user asks to add, change, or debug order-flow / footprint / delta / CVD / imbalance / absorption / volume-profile / DOM / key-level features in the Pine indicator, or mentions مؤشر الاوردر فلو، الفوت برنت، الفوليوم بروفايل، مستويات اليوم والسابق، DOM. Owns the design invariants (honest LTF approximation, force_overlay drawing, object-count budgets, no-repaint rules) so extensions stay compiling and consistent.
---

# Order Flow Suite — Builder Skill

The deliverable is a single Pine Script **v6** indicator: `orderflow_suite.pine`.
It reconstructs order flow on TradingView (which has **no real bid/ask tape**) from a
lower-timeframe volume feed and renders footprint, delta/CVD, imbalances, patterns,
volume profile, today/yesterday key levels, and a DOM-style liquidity ladder.

## Non-negotiable design invariants

1. **Honesty.** TradingView has no order book. Every bid/ask figure is an *approximation*
   from `request.security_lower_tf()` classified by close-in-range. Keep the notice at the
   top of the file and in docs. Never present it as true tape.
2. **Pane architecture.** `indicator(overlay=false)`. CVD + dashboard tables live in the
   pane. **Every price-chart drawing (`label.new`/`box.new`/`line.new`) MUST pass
   `force_overlay=true`**, and `plotshape` markers too. Forgetting this is the #1 bug —
   objects silently render in the CVD pane at price y-values.
3. **No repaint.** Approximated delta and profiles update only on `barstate.isconfirmed`.
   Daily levels use `request.security(..., "1D", high[1], lookahead=barmerge.lookahead_on)`
   (the `[1]` makes lookahead safe). Developing profile excludes the live forming bar.
4. **Object-count budgets.** Pane limits: 500 boxes / 500 labels / 500 lines.
   - Footprint numbers are heavy → gate to `last_bar_index - bar_index < fpBars`.
   - Volume-profile histogram + level lines redraw only on `barstate.islast`
     (delete-then-recreate via `var array<...>` registers).
   - Bin size is derived from the previous day's range so bin count ≈ `profRows`,
     bounded on any instrument.
5. **Pine v6 gotchas that break compiles here** (all already respected — keep them):
   - No function definitions inside `if`/loops — all UDFs (`f_fmt`, `f_classify`,
     `f_profile`, `f_lvlDraw`, `f_row`) are global.
   - No multi-var declarations on one line (`var float a=na, b=na` is illegal → one per line).
   - No comma-separated statements (`a.clear(), b.clear()` → separate lines).
   - `line.style_*` constants are **strings**, not ints (type params accordingly).
   - `for i = 0 to n-1` auto-decrements when `n==0` → always guard loops with size > 0.
   - Arrays/maps are reference types; pushing to an array *parameter* mutates the caller's.

## Module map (what lives where in the file)

| Section | Produces |
|---|---|
| LTF engine + `f_classify` | per-bar buy/sell split, `barDelta`, `barVol`, `volRatio` |
| CVD block | session/day/week-anchored `cvd` + signal MA + delta candle coloring |
| Pattern detectors | `absBull/absBear`, `exhUp/exhDn`, `trapTop/trapBot`, `bull/bearDiv` (scores → booleans) |
| Footprint block (`doFp`) | per-price Bid×Ask **box grid** (bid left / ask right of the candle, drawn with `xloc.bar_time` to split the bar width), heatmap cell shading, diagonal imbalances, stacked-zone boxes, bar POC, unfinished auction |
| Iceberg block | one-sided aggression absorbed at a rejected extreme → `iceSell`/`iceBuy`, persistent level lines removed when broken, 🧊 markers |
| VP / key-levels block | day maps `dTot/dAsk/dBid`, `f_profile` → POC/VAH/VAL, current + previous-day lines, naked POCs |
| DOM ladder | `dAsk/dBid` near price → block-bar table (`position.middle_left`) |
| Plots / markers / tables / alerts | CVD pane plot, `plotshape` signals, info table, `alertcondition`s |

## When extending

- **New pattern** → add a boolean score detector next to the others, a `plotshape(...,
  force_overlay=true)` marker, an info-table read, and an `alertcondition`. Gate it behind
  a confluence check (context + score threshold + CVD agreement) — high-quality-only means
  the gate rejects most candidates.
- **New drawn level/zone** → register objects in a `var array`, delete-then-redraw on the
  relevant barstate, and always `force_overlay=true`.
- **Touching the profile** → keep bin sizing derived from a stable reference (prev-day
  range / ATR), never from the still-developing current range.
- After any change, re-scan for the invariants above (especially `force_overlay` on every
  new `*.new`, and function definitions not nested in blocks) before declaring it done.
  There is no local Pine compiler — TradingView's editor is the only validator, so the
  manual invariant pass is the safety net.

## Domain skills to load alongside

- `footprint-orderflow` — delta/imbalance/absorption/exhaustion/trap definitions and the
  confluence-gate philosophy for signals.
- `volume-profile-mastery` — POC/VA math, profile shapes, nPOC magnets, 80% rule, the
  acceptance-vs-rejection read that the levels are meant to support.
