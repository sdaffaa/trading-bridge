---
name: chart-realism
description: >-
  Enforce the Liquidity State "Universal Chart Realism" standard on ANY chart you draw or animate — candle
  morphology vs local volatility, directional-oscillation states (ER/Overlap/Pause/Pullback), reversal & Doji
  ratios, anti-robotic-pattern checks (Motif/Similarity/Lag), MTF aggregation, markup sizing, and a required
  pre-export QA report with hard reject gates. Use this WHENEVER you build, redesign, or review a chart for a
  carousel/reel/PDF/image, or the user says "واقعية الشارت / الشموع تبين مصطنعة / أعد تصميم الشارت / تدقيق
  الجارت / QA / معايير الجارت / master prompt". It complements verified-market-charts (which proves the DATA is
  real) by proving the DRAWING is realistic and auditable — run its QA script before every export.
---

# Universal Chart Realism (v1.0)

Governing idea: **«الجارت المقنع لا يبدو مثاليًا — بل يبدو قابلًا للتحقق.»** A chart earns trust by being
checkable, not pretty. Full standard (tables, thresholds, Arabic wording, references) is in
`references/universal-chart-realism-AR.md`; the original PDF sits beside it. Read that reference when you need a
specific threshold — this page is the operating procedure.

## The one rule people get wrong
Real data is never bent to fit the aesthetic ranges. The numeric bands (ER, body/range %, reversal %, motif
share…) are **design + test controls for educational simulation**, and **diagnostics only** for real or
reconstructed data. So: never edit a real candle because a ratio sits outside a band — report the ratio instead.
Conversely, for simulated data those bands are enforceable and a breach means regenerate.

## Procedure

1. **Declare the variables before drawing** — `SYMBOL/MARKET`, `DATA_SOURCE` + `SOURCE_MODE (Real/Reconstructed/
   Simulated)`, `TIMEFRAMES`, `SESSION/TZ`, `METHOD/MODEL`, `OUTPUT`, `LEVELS` (from the source only),
   `DISCLOSURE`. If a field isn't available, **don't invent it** — either declare a simulation or drop the element
   that needs it. (Data sourcing itself belongs to `verified-market-charts`.)
2. **Respect the school's data gate** — ICT/SMC need OHLC+Time; Volume needs a named volume; VWAP needs
   price+volume and a session/anchor; Volume Profile needs volume-at-price and a stated range; Footprint needs
   tick Bid×Ask. Missing data → explain the concept visually and label it as a non-order-flow teaching model.
   One primary school + one context + one confirmation, never all of them.
3. **Size the drawing to the output** — carousel: **28–48 candles, body 10–16px, wick 2–3px**; reel 1080px:
   32–44 candles, body 12–16px, wick ~3px. Markup explains evidence and must not cover bodies/wicks; lines start
   at the intended candle/price and end at the last logical extension, not the canvas edge; label each zone with
   its origin and timeframe; show symbol/TF/time/timezone/source when real.
4. **Run QA before export** and paste the report into the delivery notes:
   ```bash
   node scripts/chart_qa.mjs --scenario data/scenario.json --mode Reconstructed --json out/qa.json
   ```
   It computes candle stats, morphology vs rolling-median range, ER/Overlap/PullbackDepth/PauseRate, reversal /
   Doji / Inside / Outside / longest same-colour streak, Body-Range-Shape similarity, Motif share & repeat,
   Lag1/Lag3 direction match and body correlation, plus trade chronology and R — then applies the gates.
5. **Honour the gates.** Critical failures (invalid OHLC, broken chronology / future leak, unsupported data
   source, stop not above the invalidation high) mean **do not export** — fix the input. High-severity failures
   (periodic motif, ER>0.85 with no pause) mean regenerate when the data is simulated. Items marked `تشخيصي`
   are informational for real data — report them, don't "fix" the market.

## Delivery
State plainly what is real and what is simulated, keep the disclosure visible on any chart frame, and attach the
QA summary. The final visual + numeric check after export is part of the standard, not optional.
