# Chart Markup Method — الطريقة المعتمدة

The adopted way of marking up charts for Liquidity State: structure lines, order blocks,
and explanation lines. Derived from the reference method and rebuilt in the brand palette.

**Implementation:** `markup.js` (engine) + `brand.css` (`.ls-mk-*` layer) · **Example:** `markup-demo.html` → `markup-demo.png`

![Markup demo](markup-demo.png)

---

## The nine rules

1. **Hairlines only.** Annotation strokes are `1.4–1.6px`. Markup must never be visually heavier
   than the candles — it sits *over* the chart, it does not *become* the chart.
2. **Every line carries exactly one label, and the line breaks around it.** The label is set inside
   the gap, vertically centred on the line. This is the signature of the method: annotation reads
   as typography, not as a sticker floating above a line.
3. **Zones are outlined rectangles, not filled blocks.** Thin border, fill at 6–9% opacity. On wide
   bands the label is right-aligned inside the zone; on narrow zones it is centred.
4. **Structure is one thin zigzag** through the swing points — never a line per leg. Swings are
   tagged `(0) (1) (2) (3) (5)` in accent color, above highs and below lows.
5. **Diagonals are labelled along their own angle.** The label rotates with the line and sits just
   above it, placed in empty space (≈0.85 along the line).
6. **Two tones carry meaning, a third carries context.**
   - `primary` (navy `#15222E`) — settled structure: levels, zones, trendlines
   - `accent` (teal `#2C7F9E`) — the live read: structure zigzag, the zone in focus, projection
   - `muted` (grey `#8FA0A9`) — context you are not arguing about (untouched liquidity)
   - `danger` (red `#DC4B41`) — invalidation only. Never decorative.
7. **Terminology stays English, narration stays Arabic.** `BSL`, `Internal BSL`, `Sweep`, `CHoCH`,
   `BOS`, `OB`, `Liquidity`, `Trendline`, `Fibo Zone` on the chart; the headline, the accent line
   and the caption in Kuwaiti/Gulf Arabic around it.
8. **Leave bars empty on the right.** The projection needs somewhere to go — `barsRight: 6–8`.
9. **Eight annotations maximum per chart.** If a ninth is needed, the chart is carrying two ideas
   and should be split across two slides. Every line has a reason or it gets deleted.

---

## Vocabulary

| Primitive | Means | Call |
|---|---|---|
| Level line | A price that matters — liquidity, a break, a sweep | `level({price, label, from, to, tone, dashed})` |
| Zone | Order block, liquidity band, fib zone | `zone({from, to, top, bottom, label, tone, align})` |
| Structure | The swing path the market actually walked | `structure([{i, price}, …])` |
| Swing tag | Sequence of the legs — `(0) (1) (2)` | `swing({i, price, label, place})` |
| Fib rail | Retracement depth on an impulse leg | `fib({i, priceFrom, priceTo, levels, width})` |
| Trendline | The diagonal, labelled along itself | `trend({i1, p1, i2, p2, label, extend})` |
| Projection | Where the idea expects price to go | `structure([…], {tone:'accent', projection:true})` |
| Invalidation | Where the idea is wrong | `invalid({i, price})` |

Coordinates are always **(candle index, price)** — never pixels — so markup stays locked to the
data when the canvas size or price range changes.

---

## Reading order

Mark up in the order a viewer should read it, because that's the order it gets drawn and the
order it should be narrated in a reel:

```
1. External liquidity      → level  BSL
2. Zones                   → zone   Internal BSL, Small OB
3. The diagonal            → trend  Trendline
4. Structure + swing tags  → structure + swing
5. What happened, in order → level  Sweep → CHoCH → BOS
6. Depth + invalidation    → fib + invalid
7. Where it goes           → projection
```

---

## Rhythm — إيقاع الرسم

Markup is not pasted on, it is **drawn**, and the pace is part of the method. These numbers are
measured from the reference recording (30s clip; drawing runs 3.5s → 28.2s, 17 structural strokes),
not estimated.

| Quantity | Measured | Adopted |
|---|---|---|
| Stroke duration | median **0.7s** (p25 0.5 · p75 0.9 · range 0.2–1.2) | per-type table below |
| Rest between strokes | median **0.9s** | `rest: 0.9` |
| Inter-onset interval | median **1.6s** → one element every ~1.5s | emergent |
| Label fade-in after its stroke lands | median **0.7s** | `labelLag: 0.7`, `labelDur: 0.4` |
| Total drawing span | 24.7s for 17 elements | ~20s for 15 |

**Per-type stroke duration** (`LSChart.CADENCE.dur`):

| Element | Duration | Reveal |
|---|---|---|
| `level` | 0.5s | dash reveal, left → right |
| `trend` | 0.6s | dash reveal along the diagonal |
| `zone` | 1.0s | wipe open, left → right |
| `structure` | **2.2s** | dash reveal across the whole traverse |
| `projection` | 0.9s | dash reveal, dashed stroke |
| `fib` | 0.8s | rail draws, ticks and numbers fade at 50% |
| `swing` | 0.3s | fade |
| `invalid` | 0.35s | fade |

### The three rules of the rhythm

1. **Draw → rest → name.** A line lands, the chart sits still for ~0.9s, *then* its label fades in
   0.7s later. The pause is what makes it read as explanation instead of decoration. Never fade a
   label in with its own line.
2. **The structure zigzag is the long stroke.** At 2.2s it takes ~3× any other element — it is the
   spine of the read, and the eye needs to travel it. Everything else is a beat; this is a phrase.
3. **Swing tags land together, not queued.** After the zigzag settles they appear staggered ~0.18s
   apart, not spaced by the normal 0.9s rest — they are one gesture, not five elements.

Easing is `ease-out` (cubic) on every reveal: fast departure, soft arrival.

### Driving it

```js
const ch = LSChart({ …, anim: {} });     // {} adopts the cadence above
// …add markup in reading order — the timeline auto-sequences from call order…
ch.layout();

ch.play();          // live playback
ch.seek(7.5);       // deterministic state at t — used for frame capture
ch.duration();      // total timeline length in seconds
```

Override any timing per element with `{ at, dur }`, e.g. the staggered swing tags:

```js
swings.forEach(([i, price, label, place], k) =>
  ch.swing({ i, price, label, place, at: 9.8 + k * 0.18 }));
```

### Rendering to video

`capture-motion.py` drives the page over the Chrome DevTools Protocol, stepping `seek(t)` frame by
frame so the output is frame-accurate rather than dependent on wall-clock playback:

```bash
python3 assets/brand/capture-motion.py assets/brand/markup-motion.html out.mp4 30
```

Reference render: `markup-motion.html` → **`markup-motion.mp4`** (19.9s timeline, 1080×1350, 30fps).

---

## Usage

```html
<link rel="stylesheet" href="assets/brand/brand.css">
<div id="chart"></div>
<script src="assets/brand/markup.js"></script>
<script>
  const ch = LSChart({
    mount: '#chart', width: 960, height: 880, candles: myOHLC,
    padding: { top: 34, right: 120, bottom: 54, left: 14 }, barsRight: 7
  });

  ch.grid(4).drawCandles();
  ch.level({ price: 100, label: 'BSL', from: 4 });
  ch.zone({ from: 41, to: 62, top: 87, bottom: 83.5, label: 'Small OB', tone: 'accent', align: 'right' });
  ch.trend({ i1: 4, p1: 100, i2: 30, p2: 90, label: 'Trendline' });
  ch.structure([{ i: 4, price: 100 }, { i: 22, price: 77 }, { i: 30, price: 90 }]);
  ch.swing({ i: 22, price: 77, label: '(1)', place: 'below' });
  ch.level({ price: 70, label: 'BOS', from: 44, to: 60 });
  ch.invalid({ i: 60, price: 87.8 });

  ch.layout();   // REQUIRED last: measures labels, then breaks the lines around them
</script>
```

`ch.layout()` must be called after all markup is added — it measures each label and cuts the
gap in its line. Skip it and the labels sit on top of unbroken lines.

Render to PNG:

```bash
/opt/pw-browsers/chromium-1194/chrome-linux/chrome --headless --no-sandbox --disable-gpu \
  --hide-scrollbars --allow-file-access-from-files --window-size=1080,1350 \
  --virtual-time-budget=4000 --screenshot=out.png "file://$PWD/slide.html"
```

---

## Real charts

The demo uses a deterministic synthetic series and is labelled **مثال تخطيطي** on the slide.
Documented-trade content must use real TradingView data — read the chart with the
`tradingview-chart-reading` protocol first, then mark it up with this method. Never invent
candles for a صفقة موثقة.
