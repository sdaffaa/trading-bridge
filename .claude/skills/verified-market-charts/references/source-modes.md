# Source modes A / B / C — rules and disclosure

## A — Original chart
Use when a real screenshot / TradingView recording / exported CSV + real trade values are available.
- Preserve all bodies, wicks, prices; do not redraw any candle differently; do not change event timing/order.
- Cleaning the UI and recoloring to brand is allowed; the markup must match what actually happened.
- Disclosure: none required beyond "لغرض تعليمي" if a trade is shown.

## B — Verified market data (default)
Rebuild from trusted historical OHLCV.
- Import real OHLC; draw each candle from O/H/L/C. Keep session gaps, holidays, weekends. Do not smooth or add
  intermediate candles. Do not alter data to get a prettier scenario — if a window doesn't contain the model,
  fetch another window.
- Multi-timeframe must come from the same source/timestamp (aggregate up; never hand-draw a different chart).
- Volume: exchange volume for centralized markets; Tick Volume only where that's all that exists (Forex/CFD) —
  and say so. XAUUSD spot/CFD has no single consolidated volume; disclose the provider and that it's tick volume.
- **On-chart disclosure (required):** `إعادة رسم من بيانات سوق تاريخية — [المصدر] — [التاريخ]`
- If VP is bar-based (OHLCV only, not tick): add `Volume Profile تقديري`.

## C — Educational simulation (last resort)
Only when A and B are both impossible.
- Generate coherent OHLC (see `references/school-data-rules.md` §simulation). Natural, non-geometric motion.
- **Never**: write "صفقة حقيقية"; claim prices are historical; attach a real provider/exchange/date; invent
  volume/Delta and call it real; show a real profit/backtest result.
- **On-chart disclosure (required):** `محاكاة تعليمية لحركة السوق` (and for order flow: `محاكاة تعليمية لبيانات Order Flow`).
- **Caption disclosure (required):** `الشارت توضيحي وليس تسجيلًا لصفقة حقيقية.`

## Final classification line (put one on the chart)
- Verified data:  `جارت تعليمي مبني على بيانات سوق تاريخية — المصدر: [المصدر]`
- Full simulation: `محاكاة تعليمية واقعية — ليست توصية تداول`
Never hide the difference between the two from the viewer.
