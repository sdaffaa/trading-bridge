---
name: chart-drawing-accuracy
description: Verify that every line, level, and box drawn on a candlestick chart is geometrically honest — anchored to the candle that actually created it, and terminated at the candle that broke or penetrated it. Use this skill whenever a chart is being marked up, reviewed, or produced for content: drawing support/resistance, order blocks, supply/demand zones, liquidity levels, BOS/CHoCH lines, fair value gaps, or trendlines; before publishing any chart image, carousel slide, or reel; when reviewing someone's chart or a screenshot for correctness; or when a level "looks wrong" or extends past where price already traded through it. Also trigger on Arabic requests about drawing accuracy — دقة الرسم، الخط يمتد بعد الكسر، وين ينتهي الخط، الرسم غلط، راجع الشارت، البوكس بعده مكسور، تأكد من الرسم، الأوردر بلوك متى ينتهي.
---

# Chart Drawing Accuracy — دقة الرسم على الشارت

A level is a claim about price. Drawn past the candle that broke it, the claim is simply
false — the picture says "this held" while the candles behind it say it did not. Most bad
trading charts are not wrong about the *idea*; they are wrong about **where the drawing stops**.

This skill enforces two rules and gives you a script that checks them against real candle data.

![before and after](before-after.png)

*Left: the same chart before checking — the liquidity band runs to the edge past the candle that
re-entered it, and three levels are anchored to bars that never traded at their price. Right: after.*

## The two rules

**1. A drawing starts on the candle that created it.**
A resistance line is the high of a specific candle. An order block is the range of a specific
candle. If the anchor bar never traded at that price, the drawing is decoration floating in
space — and every conclusion drawn from it is unearned.

**2. A drawing ends on the candle that broke it.**
Once price trades through a level or back into a zone, that drawing's life is over. Extending
it further asserts it was still acting as a level while price was already on the other side.

Everything else here is the detail of applying those two rules honestly.

## Before you check anything: price has to leave first

A level is born touching price. The bar right after a swing high is usually still at that high —
that is not a break, that is price not having left yet.

**Nothing counts as a break until price has departed the drawing at least once.** Find the first
bar that is clear of the level or zone, and only start looking for the break after that. Skip this
and every drawing appears "broken" one bar after it is created, which is why naive checks produce
nonsense.

If price never departs at all, the anchor is wrong — the drawing is sitting inside the range price
is still trading in, so it has no origin to speak of.

## What counts as a break

Different drawings die differently, and the mode should match what the drawing claims:

| Mode | Breaks when | Use for |
|---|---|---|
| `touch` (default) | a wick reaches the level / any overlap with the zone | liquidity levels, order blocks, supply & demand — price *reaching* them is the event |
| `close` | a candle closes beyond the level | BOS / CHoCH and anything where you argued a *confirmed* break |
| `fill` | a candle fully traverses the zone | gaps and FVGs that need complete fill to be done |

Pick deliberately. Claiming a structural break on a wick, then drawing it as though it were
confirmed by a close, is the most common way charts overstate their case.

## The one legitimate exception: targets

A level marking price that **has not happened yet** — untapped liquidity, a take-profit, a
projected target — has no anchor candle and cannot be broken. It is exempt from both rules.

But it has to earn the exemption: it must actually be untouched. The moment price trades there it
stops being a target and becomes a level, and the full rules apply. Mark these `kind: "target"`
and draw them dashed so the chart itself distinguishes "this happened" from "this might".

Projections (expected path) are the same idea in two dimensions: they are the only drawing allowed
to extend past the last bar, and they should not sit on top of real candles.

## Running the check

`scripts/verify_drawing.py` takes candles plus the drawings and reports each one. Build the spec
from whatever you have — the chart JSON, the markup calls, or values read off a screenshot:

```json
{
  "candles": [{"o":95,"h":96.4,"l":94.1,"c":96.0}, "…index 0 is oldest"],
  "drawings": [
    {"id":"BSL",      "kind":"level",  "price":100, "from":4},
    {"id":"Small OB", "kind":"zone",   "top":87, "bottom":83.5, "from":41, "to":62},
    {"id":"BOS",      "kind":"level",  "price":70, "from":50, "mode":"close"},
    {"id":"TP",       "kind":"target", "price":62, "from":30},
    {"id":"path",     "kind":"projection", "from":61, "to":68}
  ]
}
```

A runnable example ships with the skill — `examples/demo-spec.json` is a real chart with seven
violations in it:

```bash
python3 scripts/verify_drawing.py examples/demo-spec.json
```

```bash
python3 scripts/verify_drawing.py spec.json                      # report
python3 scripts/verify_drawing.py spec.json --fix out.json       # correct the endpoints
python3 scripts/verify_drawing.py spec.json --fix out.json --snap  # also fix bad anchors
```

Exit code is 0 when every drawing is accurate and 1 when anything is off, so it drops straight
into a pre-publish check.

Findings read like this:

```
[LONG] Small OB   ends at bar 62 but bar 42 already broke it (touch); it is drawn 20 bars too long  → to: 42
[ANCH] BOS        bar 44 never reaches 70, so the line starts from a candle that did not make that level
[ok  ] BSL        never broken; runs to the last bar
```

**`--snap` moves the price, not the bar.** When a level is anchored to a candle that never reached
it, the fix a trader makes by hand is to pull the level onto that candle's high or low — the level
*is* that extreme. Sliding the line to some other bar instead would silently change which candle
you are talking about.

Run `--fix` twice: snapping an anchor changes where the break lands, so the endpoint correction
needs a second pass to settle. Two passes is enough; if it has not converged by then the drawing
is genuinely ambiguous and needs a human decision, not another pass.

## Fixing what it finds

Findings are not all equally serious, and the order matters:

1. **`ANCH` first.** A wrong anchor invalidates the break analysis downstream — there is no point
   correcting an endpoint on a line that starts in the wrong place.
2. **`LONG`** — the headline error. Pull the endpoint back to the breaking bar.
3. **`SHRT`** — the line stops before price actually broke it, which understates a level that was
   still working. Less visually offensive, equally untrue.
4. **`FLOAT`** — a line running to the edge that price never returned to. Either it is a target
   (mark it as one) or it should not be on the chart.
5. **`BAD`** — indices outside the series, inverted boxes, zero-height zones. Structural bugs.

## Reading levels off a screenshot

When the source is an image rather than data, extract the candles with the
`tradingview-chart-reading` protocol first, then build the spec from what you read. Do not eyeball
whether a line stops in the right place — the whole failure mode this skill addresses is that
wrong drawings *look* fine. If you cannot get candle values, say the check could not be run rather
than implying the chart was verified.

## Charts produced with the LSChart engine

For charts drawn with `assets/brand/markup.js`, the drawings map directly onto the spec:
`level({price, from, to})` → `kind: "level"`, `zone({top, bottom, from, to})` → `kind: "zone"`,
`structure(…, {projection: true})` → `kind: "projection"`. Dump the candle array and the markup
calls into a spec, verify, then feed the corrected `to` values back into the calls.

Verify **before** rendering. A chart that has already been rendered, captioned, and cut into a reel
is expensive to correct, and a wrong level that ships is worse than one that never gets drawn —
it teaches the audience something false and it is exactly what a knowledgeable viewer screenshots.
