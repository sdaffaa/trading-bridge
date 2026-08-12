# Timing, beats & camera (VP stop-placement reel, 23.5s)

The runtime is intentionally short (skip-rate discipline). Every beat is 4–7 words, ≤2 lines.

| Time (s) | Beat text | On-chart action |
|---|---|---|
| 0.00–0.70 | «أقرب ظل يضرب ستوبك.» | navy hook, close-up of a swept wick + stop line (full text from frame 1, no slow fade) |
| 0.70–1.80 | «وين مكانه المنطقي؟» | push-in |
| 1.80–3.30 | «فوق بطلان الفكرة… مو فوق أي ظل.» | crossfade navy → warm off-white, chart card in |
| 3.30–4.70 | «المثال داخل رينج واضح.» | reveal range candles; Fixed Range bracket + price axis appear |
| 4.70–6.40 | «VAH فوق · POC وسط · VAL تحت» | draw VAH→POC→VAL sequentially, with real prices |
| 6.40–8.20 | «السعر خرج فوق VAH» | reveal breakout candle; zoom-in #1; mark قمة الخروج |
| 8.20–10.20 | «ثم رجع داخل منطقة القيمة» | reveal fail candle; frame it |
| 10.20–11.70 | «هذا فشل قبول… مو اختراق.» | dim the rest 15%, keep exit+fail bright |
| 11.70–13.60 | «الدخول بعد تأكيد الرجوع» | entry label at the real price |
| 13.60–15.70 | «الستوب فوق قمة الخروج» | SL band above the exit high + disclosed margin |
| 15.70–18.20 | «الهدف الأول POC… ثم VAL» | zoom-out #3; reveal rotation candles; activate each target card as price reaches it |
| 18.20–20.00 | «السياق يحدد الستوب، مو أقرب ظل.» | dim chart; 3-point summary |
| 20.00–23.50 | CTA «اكتب "ستوب" وخذ قائمة الفحص» | keyword CTA + save/share reasons + handle |

## Camera — exactly three analysis moves (+ the hook push-in)
1. Zoom into the breakout (exit) area.  2. Zoom into the return/entry area (framing exit-high SL + entry).
3. Zoom-out to reveal the rotation to the targets.
Rules: smooth ease in/out, transitions 4–8 frames, no glitch/shake/large arrows. Draw every line **after** its
event, never before. Logo and titles stay fixed outside camera motion; text never covers candles/VAH/POC/VAL.
Auto-scale stays calm; keep zoom between ~100% and ~114%.

## Reveal & markup timing
Candles reveal left→right by mask (opacity ramp ~0.22s); never fabricate intrabar motion. Each markup element has
a time+price+condition anchor and appears only once its condition holds. Target cards activate individually when
price reaches that level — not all at once.
