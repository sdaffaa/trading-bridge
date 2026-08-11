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

### Bar replay — printing the candles forward

Measured from the reference recording (TradingView bar replay, XAUUSD M15, its toolbar showing 5×):

| Quantity | Measured | Adopted |
|---|---|---|
| Print rate | **4.71 candles/sec** (one bar every ~212ms) | `rate: 4.71` |
| Candle pitch | **14.0 px** | `barsVisible` sized to give 14px |
| Viewport step | **exactly one pitch per printed bar** | discrete, never interpolated |
| Resulting scroll | **66 px/sec** | emergent |

Two things matter more than the rate itself:

1. **The viewport jumps, it does not glide.** When a bar prints, the chart moves exactly one candle
   pitch and stops. Interpolating that pan turns a replay into a camera move — it reads as a
   different thing entirely, however correct the bar rate is.
2. **Perceived speed is pitch × rate, not rate alone.** Set `barsVisible` so the pitch is right;
   without it the pitch comes from the whole series, so a 120-bar series draws hair-thin candles
   and the replay feels half speed while printing at exactly the correct rate. This is the mistake
   worth knowing about — the number is right and the result still looks wrong.

```js
const ch = LSChart({ …, candles, barsVisible: 58, anim: {} });
ch.priceScale({ step: 20 }).drawCandles();
ch.replay({ rate: 4.71, window: 56 });   // window = bars on screen before it starts jumping
ch.layout();
```

Reference render: `replay-demo.html` → **`replay-demo.mp4`**. Verified against the source with the
same measurement pipeline: pitch 14.0px, one-pitch jumps, 64.5 px/s, 4.61 candles/sec.

### Entry model — replay that stops at each event

`entry-model-demo.html` → **`entry-model-demo.mp4`** walks one setup in the spec's order
(`Liquidity → Sweep → MSS → FVG → Entry → SL → TP`) while the chart replays at the measured rate.

The mechanism that makes it work is `holds`: the replay freezes on the bar that just printed while
that step's markup draws, then runs on.

```js
const holds = [
  { atBar: sweepI + 2, seconds: 3.6 },
  { atBar: mssI   + 2, seconds: 3.6 },
  …
];
ch.replay({ rate: 4.71, window: 56, start: 24, holds });
const T = holds.map(h => h.t);      // when each step begins — schedule markup against it
ch.level({ …, at: T[0] + 0.2 });
```

Without holds every event flashes past in 212ms and the markup lands on a chart that has already
moved somewhere else. `start` opens with bars already on screen instead of a long empty run-up.

**Every level is read back off the candles, never typed in** — the reference high, the sweep wick,
the last higher low, the gap bounds and the target low are all found by scanning the series, so
each drawing lands on a real wick and the chart reports zero violations. That is the zero rule
holding in code rather than in good intentions.

Two details worth copying:

- **MSS is a body close**, not a wick — `while (candles[mssI].c >= swingLo.p) mssI++`. Naming a
  wick-only penetration a break is exactly what the spec forbids.
- **The FVG chosen is the first one price actually returns into**, not the first one found. A
  displacement leaves several gaps; an untouched gap is not an entry, it is just a gap.

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

## The zero rule — the source chart is a locked layer

From the markup spec. The original chart is never edited; markup goes on a layer above it.
Absolutely forbidden:

1. Inventing a candle, price, time, high or low
2. Changing any candle's body, wick, order, width, colour or position
3. Redrawing, stretching, compressing or rotating the chart, changing the price/time scale, or
   cropping away context that matters
4. Calling a wick-only penetration a break — that is a sweep (`mode: 'close'` is what a confirmed
   break requires)
5. Running lines edge to edge for decoration
6. Putting text or an arrow over a decisive candle, or over a price that has to stay readable

**If a level cannot be read precisely, write "غير محسوم — يحتاج تأكيد" in the plan and do not draw
it.** Never guess a value. A markup that quietly invents a number is worse than one that admits a
gap, because the audience cannot tell the difference.

## Read before drawing

Identify in chronological order — not in the order that looks best: context (trend or range,
the highs and lows that matter, session boundaries if visible) → liquidity → the sweep (the candle
that pierced the level and came back) → confirmation → the return zone → the plan.

Then produce a **Markup Map** before touching the design:

| العنصر | نقطة البداية الدقيقة | نقطة النهاية الدقيقة | النص | الثقة |
|---|---|---|---|---|
| Liquidity line | ذيل القمة المرجعية | شمعة السحب | BSL Sweep | عالية / متوسطة / غير محسومة |

Do not start designing until every element has an unambiguous start and end.

## Educational slide geometry

`markup-slide.html` → `markup-slide.png` is the worked example (1080×1920).

- **Liquidity line** starts on the highest pixel of the reference high's wick (or the lowest of the
  low's) and stops at the sweep candle. The line's centre sits on the price exactly. Dashed.
- **Numbered anchors** (`anchor()`) ring the exact pixel and carry the step number — the ring is
  what proves the line starts *on* the wick rather than near it.
- **Stickers** (`sticker()`) never sit on a candle. They float in empty space and reach the price
  with one calm curve that stops ~16px short. One arrow per idea; if an element needs two, the
  explanation is too long.
- **FVG** uses the three-candle model only; the rectangle starts after the third candle completes
  and runs to first mitigation.
- **Price scale** (`priceScale()`) on the right — a level cannot be verified against a chart that
  does not show its own prices.

Visual sequence, in this order:
`Context → Liquidity → Sweep → Displacement → MSS/BOS → FVG/OB → Entry → SL → TP`

Weight them differently: the current element, the previous one, then secondary context. Not
everything at the same intensity.

## Delivery format

Deliver in this order:

1. **قراءة الشارت** — what the chart says, before any drawing
2. **Markup Map** — the table above
3. **النسخة النظيفة** — original chart + markup layer only
4. **نسخة تعليمية** — numbered
5. **تقرير تحقق** — state explicitly that candles, prices and scale are unchanged, and name any
   element left undrawn because it could not be read

Final check before export: every line touches the intended pixel · nothing is built on information
that is not visible · no text covers a decisive candle or the price scale · no more than two
educational colours plus the risk colour · events are chronologically ordered · the idea reads in
one second · the chart before and after is identical.

## Liquidity + Volume Profile

The spec's second master prompt. Its role is **Designer, not advisor**: map where liquidity sits and
where the market found acceptance or rejection — without inventing data or issuing a
recommendation.

### Audit the volume source before reading anything

Volume means different things depending on where the chart came from, and reading it wrong makes
every level downstream wrong:

| Source | What the numbers are | What you may not say |
|---|---|---|
| `XAUUSD` CFD / spot | **tick volume** — price update counts | never call it contracts traded |
| `GC1!` / COMEX futures | real exchange trade volume | — |
| unclear | classify as **Unknown** and say so | anything precise |

Never infer Bid/Ask or Up/Down split from tick volume. If the chart is Heikin Ashi or any
non-standard candle type it distorts both price and volume — ask for normal candles before
committing. Publish the audit as a table (symbol · volume type · profile type · bounds · session ·
timezone) with a confidence column, **before** any level.

### External vs internal liquidity

- **External** — PDH/PDL, PWH/PWL, session highs/lows (Asia / London / New York), major swing
  highs/lows, equal highs/lows. The level must be clear in context and at the edge of the working
  range. **Not every high is external liquidity.**
- **Internal** — short-term equal highs/lows, minor swing clusters, highs and lows inside the range.
  Use them as a possible path *through* the range, never as an automatic final target.

Equal highs need to be equal: past the stated tolerance they are not equal, and you need at least
two valid ones. A level already pierced by an earlier candle that then traded behind it is not
untouched.

### What makes a sweep a sweep

All four, or it is not one:

1. Price reached a level identified **beforehand**
2. It pierced or touched it per the stated rule
3. It returned inside the range, or closed with a proper rejection
4. It happened **after** the level formed — not before

If price broke through and kept accepting beyond, that is a breakout, not a sweep.

Then score the level out of five — clear session or higher-timeframe level · not already swept or
deeply tested · nearby equal highs/lows clustered · clean approach without repeated chop · a
confirmed response after arrival — and grade it A / B / C.

> **Do not use the response after the touch to argue the level was obvious before it.** Grade the
> level's quality *before* the touch separately from the confirmation *after* it. This is the single
> easiest way to produce analysis that looks rigorous and is actually hindsight.

### Acceptance vs rejection

Neither is a one-candle verdict. **Acceptance** wants a cluster of evidence: several closes
inside/behind the area, time spent there with new volume building, the POC migrating toward it, a
successful retest from the other side. **Rejection** wants a short test, a wick or displacement
away, and a close outside. A single wick is not institutional rejection.

### Choosing the profile

`Session` for one session · `FRVP` between two fixed points · `AVP` anchored to a clear event and
running to the last bar · `Composite` for merged sessions, stating why. **Do not use Visible Range
for final markup** — if changing the zoom changes the level, the level was never a level.

### The levels, and how each is drawn

| Level | Meaning | Drawn as |
|---|---|---|
| POC / VPOC | the row holding the most volume | **one precise line** on the actual price row |
| Value Area | the stated percentage, usually 70% | shaded band between VAH and VAL |
| VAH / VAL | its edges | thin dashed edges, labelled |
| HVN | a clear peak — dense trading, prior acceptance | **a band the thickness of the rows forming it** |
| LVN | a clear valley between two higher nodes | a band; do **not** assume it gets crossed |
| Shelf / Ledge | where a cluster ends against a void | the edge at the actual transition |

A node is a region of acceptance, not a price — drawn as a line it claims precision the profile does
not have. While a profile is still forming, mark it **developing** and say so.

```js
const vp = ch.volumeProfile({ from, to, valueArea: 0.70, showVA: true, nodes: true });
vp.pocPrice; vp.vah; vp.val; vp.hvn; vp.lvn;
```

### Confluence, and the language rule

Rank **at most three** zones. For each: the liquidity present, the volume level, the rejection
scenario, the acceptance scenario, and what invalidates the read. Write scenarios conditionally:

```
IF sweep + close back inside value + displacement, THEN the rejection scenario becomes valid.
IF several closes outside value + new volume building, THEN acceptance becomes more likely.
```

**Forbidden outright:** «شراء مؤكد» · «بيع مؤكد» · «هدف مضمون» · «نجاح مضمون». This is a map, not a
signal.

### Delivery for this prompt

`Data Audit → Liquidity Map → Volume Profile Map → Confluence Map (top 3) → Markup Plan → Quality
Report`. The quality report states explicitly: no invented levels · volume type named · profile and
session bounds fixed · candles and prices unchanged · no guaranteed-profit language · undecided
elements left undrawn.

## Accuracy

Drawing it in the right style is half of it; drawing it in the right *place* is the other half.
Every line and box must be anchored to the candle that created it and must stop at the candle that
broke it — past that point it is asserting a level held while price was already through it.

### Auto-termination

The engine can apply the rule while drawing, so endpoints never have to be maintained by hand:

```js
const ch = LSChart({ …, autoTerminate: true });

ch.zone({ from: 41, top: 87, bottom: 83.5, label: 'Small OB' });   // ends itself
ch.level({ price: 77.21, label: 'Sweep', from: 22 });              // ends itself
ch.level({ price: 62, label: 'Liquidity', from: 30, to: 'edge' }); // untapped target, opts out
```

| `to` | Behaviour |
|---|---|
| a number | used verbatim — you are asserting the endpoint yourself |
| `'auto'` | terminate at the break, whatever `autoTerminate` is set to |
| `'edge'` | run to the right edge — for targets and untapped liquidity |
| omitted | terminates at the break when `autoTerminate` is on, otherwise runs to the edge |

A drawing that is **never broken runs to the right edge**, because it is still live — an
unmitigated order block or an untested level genuinely does extend forward.

### Snapping to the candle

`snapToCandle: true` also enforces the geometry: a level lands on the nearer wick tip of its anchor
candle, and a box expands to wrap that candle whole. A line drawn mid-candle marks a price the
candle merely passed through, and a box cropped to the body hides the wick that did the sweeping.

Snapping edits your numbers, so it never does it silently — every change lands in
`ch.corrections` with the old value, the new one, and why. Targets opt out entirely:

```js
ch.level({ price: 62, label: 'Liquidity', from: 30, target: true, dashed: true });
```

A target has no anchor candle and cannot be broken, so it is exempt from snapping and termination
alike — it only has to stay untouched. Mark it and the engine leaves it alone; forget to, and it
gets snapped onto whatever candle happens to sit at its anchor bar.

Anchors are checked too, but not silently corrected: a level starting on a candle that never
traded at its price is a judgement call about which candle you meant, so the engine records it and
leaves it to you. Read `ch.violations` after `layout()` — the demo prints them to the console and
into the page title, which is enough to catch one before a render ships.

### Checking without drawing

`LSChart.audit(candles, drawings)` applies the same rules with no rendering, and the skill's
standalone checker does the same from the command line:

```bash
python3 .claude/skills/chart-drawing-accuracy/scripts/verify_drawing.py spec.json
```

Two implementations of one rule set drift, so `tools/check-rules-parity.js` runs both over the same
spec and fails on any disagreement:

```bash
node assets/brand/tools/check-rules-parity.js
```

## Real charts

The demo uses a deterministic synthetic series and is labelled **مثال تخطيطي** on the slide.
Documented-trade content must use real TradingView data — read the chart with the
`tradingview-chart-reading` protocol first, then mark it up with this method. Never invent
candles for a صفقة موثقة.
