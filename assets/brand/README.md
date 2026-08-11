# Liquidity State — Brand Identity Assets

Canonical brand identity for **@liquidity.state**: logo, approved color palette, typography,
and ready-to-use design tokens.

```
assets/brand/
├── colors.json            ← design tokens (source of truth for color + type)
├── brand.css              ← CSS variables + slide/chart/markup primitives
├── MARKUP.md              ← the approved chart markup method (read before marking up a chart)
├── markup.js              ← markup engine: levels, zones, structure, fib, projection + motion
├── markup-demo.html/.png  ← worked example of the full markup vocabulary
├── markup-motion.html/.mp4 ← the same markup drawn at the approved rhythm
├── FORMAT-REEL-SPLIT.md   ← split-screen reel format (face + chart + karaoke captions)
├── reel-split-demo.html/.mp4 ← the split-screen reel template
├── FORMAT-CAROUSEL.md     ← carousel page architecture + the footprint method
├── footprint.js           ← footprint ladders: ladder / heat / inside / bars
├── carousel-demo.html     ← the 7-page carousel template — copy it, swap the content
├── carousel/              ← its render, 7 × 1080×1350
├── capture-slides.py      ← renders each page to PNG; fails if a drawing broke a rule
├── captions.js            ← karaoke caption track (0.6s cadence)
├── tools/check-rules-parity.js ← proves the JS and Python drawing rules agree
├── capture-motion.py      ← frame-accurate CDP renderer (motion page → MP4)
├── palette-swatches.html  ← swatch sheet source
├── palette-swatches.png   ← swatch sheet render (1080×1350)
├── fonts/                 ← vendored Tajawal (OFL) for reproducible renders
└── logo/                  ← logo lockups + gem mark (SVG + PNG)
```

---

## 1. Logo

| File | Use |
|---|---|
| `logo/liquidity-state-logo-light.svg` / `.png` | Primary lockup on light / cream backgrounds |
| `logo/liquidity-state-logo-dark.svg` / `.png` | Primary lockup on the dark-teal background |
| `logo/liquidity-state-mark.svg` / `.png` | Gem mark only, transparent — watermark, profile icon, favicon |

SVGs are the source of truth. PNGs are exported at 2400 px wide (mark at 1200 px).

**Mark:** faceted silver / steel gem. Keep it small — bottom-corner or top-corner watermark, never dominating.
**Clear space:** at least the height of the gem on all sides. **Minimum mark size:** 40 px.
Do not recolor the gem, stretch the lockup, or place the light lockup on busy / low-contrast photos.

---

## 2. Approved palette — light (cream) theme

This is the **approved primary design theme**, taken from the carousel design system
(slide "الإشارة التي تعاكسك"). Use it for carousels, charts and static posts.

| Role | Hex | Usage |
|---|---|---|
| Background — base | `#F2EDE4` | Slide canvas (warm cream) |
| Background — gradient start | `#F5F0E7` | Top-left of canvas gradient |
| Background — gradient end | `#EDE6DA` | Bottom-right of canvas gradient |
| Surface | `#E9F2F6` | Badge / callout box fill |
| Surface border | `#9EC4D5` | Badge / callout box + counter border |
| Text primary | `#15222E` | Headlines, sub-headlines, key stat lines |
| Text secondary | `#8FA0A9` | Body and closing explanation lines |
| Text accent | `#2C7F9E` | Highlight sentence, section labels |
| Watermark | `#8FA3AC` | Corner `LIQUIDITY STATE` wordmark |
| Candle — bullish | `#34809B` | Up candle body + wick (teal) |
| Candle — bearish | `#15222E` | Down candle body + wick (deep navy) |
| Structure | `#15222E` | Level lines, equal-lows, markers, circles |
| Gridline | `#DFD8CC` | Horizontal chart grid |
| Invalidation | `#DC4B41` | Stop / rejection mark (✗) — **reserved, never decorative** |

### Alternate — dark theme (reels / video overlays)

Background `#0E1E24`→`#12262E`, surface `#1B3A45`, text `#FFFFFF` / `#9FB4BC`,
bullish `#2ECC9A`, bearish `#E15A5A`. Activate with `data-ls-theme="dark"`.

### Metallic (logo mark only)

Silver/steel gradient: `#FFFFFF` → `#E6ECEF` → `#CDD6DA` → `#A9B4BA` → `#7E8A90`, edges `#BFC9CE`.

![Palette swatches](palette-swatches.png)

---

## 3. Typography

- **Arabic — Tajawal** (vendored in `fonts/`, OFL licensed).
  Bold 700 for headlines / sub-headlines / accent lines, Medium 500 for body, Regular 400 for captions.
- **Latin wordmark — Cormorant Garamond** (fallback Trajan Pro / Times New Roman), uppercase,
  letter-spacing `0.28em`. Used for the logo and the corner watermark. Italic for slide counters (`2/3`).
- **Technical terms & numbers** — Tajawal, Western digits (`XAUUSD`, `2.6R`, `Order Flow`, `FVG`, `POC`).

Type scale at a 1080×1350 canvas: headline 64 / sub-headline 40 / accent 34 / body 30 / caption 24 / watermark 22.

> **Arabic rendering:** always apply the `arabic-video-text` skill before rasterizing Arabic.
> Browsers and libass shape correctly from raw text; PIL, node-canvas and ffmpeg `drawtext` need
> reshaping + bidi first. The swatch sheet is rendered through Chromium for this reason.

---

## 4. Using the tokens

```html
<link rel="stylesheet" href="assets/brand/brand.css">

<div class="ls-slide">                     <!-- 1080×1350, cream gradient, RTL, Tajawal -->
  <div class="ls-badge">مثال تخطيطي</div>
  <h1 class="ls-headline">الإشارة التي تعاكسك</h1>
  <p class="ls-accent">هني الإشارة اللي تعاكسك — ولذلك رفضتها</p>
  <p class="ls-body">الفتيل تحت القاع يسحب السيولة، والإغلاق فوقه يلغي الكسر.</p>
</div>
```

Chart primitives: `.ls-candle-up`, `.ls-candle-down`, `.ls-level`, `.ls-grid`, `.ls-invalid`.
UI primitives: `.ls-badge`, `.ls-counter`, `.ls-pager` (`i.on` = active), `.ls-watermark`.

Render a slide to PNG:

```bash
/opt/pw-browsers/chromium-1194/chrome-linux/chrome --headless --no-sandbox --disable-gpu \
  --hide-scrollbars --allow-file-access-from-files --window-size=1080,1350 \
  --screenshot=out.png "file://$PWD/slide.html"
```

---

## 5. Chart markup

Structure lines, order blocks and explanation lines follow one approved method — hairlines with
labels set inside a break in the line, outlined zones, a single structure zigzag with swing tags,
and diagonals labelled along their own angle.

Markup is also **drawn, not pasted** — the pace is part of the method: a stroke lands, the chart
rests ~0.9s, then the label fades in. `MARKUP.md` §Rhythm carries the measured cadence.

Pass `autoTerminate: true` and every level and box ends itself at the candle that broke it; the
`chart-drawing-accuracy` skill checks the same rules standalone.

**Read `MARKUP.md` before marking up any chart.** Engine: `markup.js`. Worked examples:
`markup-demo.html` → `markup-demo.png` (static), `markup-motion.html` → `markup-motion.mp4` (animated).

![Markup demo](markup-demo.png)

---

## 6. Reel formats

| Format | Spec | Template |
|---|---|---|
| Static markup slide / slow-draw reel | `MARKUP.md` | `markup-demo.html`, `markup-motion.html` |
| Split-screen: face + chart + captions | `FORMAT-REEL-SPLIT.md` | `reel-split-demo.html` |
| Full-frame chart + footprint (faceless) | `reel-footprint.md` | `reel-footprint.html` |
| Documented trade, sweep → target | `reel-trade.md` | `reel-trade.html` |
| Range + volume profile, value-edge entry | `reel-value.md` | `reel-value.html` |
| Trend continuation from an order block (cream) | `reel-orderblock.md` | `reel-orderblock.html` |

The footprint reel is the worked example of the whole system on one clock: bar replay, markup,
a footprint that builds price by price, and captions all driven by the same `seek(t)`. Runtime
(20.6s) comes from the account's measured average watch, and its recording sheet — the 11-beat
script with per-beat timings and the skip-risk score — is in
[`reel-footprint.md`](reel-footprint.md). **It ships without a voiceover; record the lines on
their timings before posting.** Its last frame is pixel-identical to frame 0, so it loops seamlessly.

`reel-trade.html` is part two of the same series: one short from liquidity sweep to target, in
five steps, at 32s (a documented trade is allowed 25–35s because the result is the payoff).
Every price on screen — entry, stop, target, and the resulting **+1.93R** — is read back off the
candles rather than typed, and the result stays hidden until the target is actually reached.
Each of the five drawings ends on the candle that ended it, so the accuracy rule is what tells
the story. See [`reel-trade.md`](reel-trade.md).

`reel-value.html` is part three, and a different model on a different chart: a range measured
with a volume profile, an excursion above the VAH that fails to earn acceptance, entry on the
close back inside value, stop above the excursion high, and two targets — POC then VAL. Its
distinguishing claim is that the excursion clears the **value area** edge while staying inside
the range's own extremes, so a range-breakout trader never sees the setup at all. POC/VAH/VAL
come out of `volumeProfile()` and everything else is derived from them. See
[`reel-value.md`](reel-value.md).

> The profile is a **time-at-price approximation built from candle ranges**, not tick or
> exchange volume — stated on the page itself as well as here. Pass `volumes` to
> `volumeProfile()` on a feed that has real volume and the values become real.

`reel-orderblock.html` is part four, the first **continuation** (the others are reversals), the
first long, and the first reel in the **cream identity**. Entry is the top of the order block,
stop its low, target the high of the impulse — +2.15R. It is also the first page built on the
`.ls-vr` components below, so it renders cream by simply not asking for the dark theme. See
[`reel-orderblock.md`](reel-orderblock.md).

### `.ls-vr` — the vertical reel components

The first three reels hard-coded their dark surfaces. `brand.css` now carries the reel chrome
as theme-driven components — `.ls-vr`, `-chart`, `-beat`, `-scrim`, `-tile`, `-grid`, `-stat`,
`-rule`, `-caps`, `-disc` — so the same markup renders in either identity by setting or
omitting `data-ls-theme="cover"`. A page supplies only its vertical rhythm. New reels should
use these; the first three are left as they shipped.

![Footprint reel](reel-footprint-poster.png)
![Trade reel](reel-trade-poster.png)
![Value reel](reel-value-poster.png)
![Order block reel](reel-orderblock-poster.png)

The split-screen format runs **two clocks**: captions change every ~0.6s while the chart changes
every ~3.5s — roughly six captions per chart beat. Uses the `terminal` dark theme.

![Split reel](reel-split-poster.png)

---

## 7. Carousel + footprint

The carousel format is documented in full — page architecture, type scale, component set, the
footprint method, and a page-by-page recipe — in **[`FORMAT-CAROUSEL.md`](FORMAT-CAROUSEL.md)**.
`carousel-demo.html` is the working template: seven pages at 1080×1350, copy it and swap the
content.

Every page is the same seven bands in the same order — counter · crest · headline · sub ·
content · conclusion · (cta) — and the furniture is stamped in by script rather than re-typed
per page. Page 1 is the only dark page (`data-ls-theme="cover"`); the rest are the cream
identity.

`footprint.js` renders order flow in four variants: `ladder` (the hero panel), `heat` (bid |
candle | ask), `inside` (the grid laid over the candle body) and `bars` (proportional bid /
price / ask). One rule governs all of them:

> **The ladder is always LTR — bid left, ask right**, even on an RTL page. It is a market
> convention, not text. Arabic labels sit outside the ladder and stay RTL.

Render and check a deck with:

```bash
python3 capture-slides.py carousel-demo.html carousel/
# violations: 0   corrections: 0
```

It exits non-zero if any chart on any page broke its own accuracy rules, so a deck can't be
shipped looking finished while a level runs past the candle that killed it.

![Carousel cover](carousel/slide1.png)

---

## 8. Rules

- Never pure black (`#000000`) or pure white (`#FFFFFF`) backgrounds. Never neon.
- Max 2 font sizes per slide besides labels; one big hook line per screen.
- Charts are always brand-styled — never raw TradingView screenshots with default colors.
- Red `#DC4B41` is reserved for invalidation / stop only.
- Every educational post carries a comment keyword CTA.

---

## Notes

- The logo SVGs are a faithful **vector recreation** of the supplied reference artwork, built to the
  brand palette — very close, but not a pixel-for-pixel copy. If you have the original master file
  (PNG/AI/vector), drop it into `logo/` as `liquidity-state-logo-original.*` to keep it as the
  archival source.
- The hex values in `colors.json` are **visually matched** from the approved carousel design.
  If you have the original design source (HTML/Figma/PSD), share it and the values can be made exact.
- Full brand system beyond visuals (voice, pillars, formats, audience): see the
  `liquidity-state-brand` skill.
