---
name: liquidity-carousel-system
description: The end-to-end design system for building Liquidity State Instagram carousels as 1080×1350 PNGs — premium Cairo (display) + Tajawal (body) Arabic typography, the brand dark-teal theme, glassmorphism cards, 3D-background layering, and ready slide components (hook cover, stat, two-cards, numbered steps, quote, CTA, real chart). Use this whenever building or restyling a carousel / multi-slide post for @liquidity.state. Pairs with liquidity-3d-backgrounds (backgrounds), realistic-trading-chart (chart slides), liquidity-state-brand (voice/colors), content-writing-engine (script), and carousel-design-pro (save-optimized architecture). Triggers: "صمم كاروسيل", "سلايدات", "بوست متعدد الصور", "carousel", "restyle the carousel", any @liquidity.state multi-slide design.
---

# Liquidity State — Carousel Design System

One module (`scripts/carousel-kit.js`) that produces on-brand carousel slides:
Cairo/Tajawal typography, dark-teal theme, glass cards, 3D-background layering,
grain + vignette + readability scrim, and ready components. Deterministic,
self-contained (fonts vendored), renders to 1080×1350 (4:5) PNG.

## Quick start

```js
const K = require('./scripts/carousel-kit');
const BG = '/abs/path/to/.claude/skills/liquidity-3d-backgrounds/assets';

const slides = [
  K.slide({ num:'١', total:'٥', bg:`${BG}/bg-02-vortex.png`, kt:'سيكولوجيا', ke:'PSYCHOLOGY',
    main: K.H(`تبيع <span style="color:${K.RED}">بخوف</span>.<br>تشتري <span style="color:${K.AMBER}">بطمع</span>.`, 96)
        + K.P(`السوق ما فجّر حسابك — <b>نفسيتك</b> إهي اللي تخلّيك تعكس الصح.`),
    foot:'اسحب لتعرف 👇' }),
  K.slide({ num:'٢', total:'٥', bg:`${BG}/bg-03-tunnel.png`, kt:'الوجع', ke:'THE TRAP',
    main: K.H(`الخسارة ما تعورك…<br><span style="color:${K.RED}">الإهانة</span> تعورك.`,80) + K.STAT('90%','يحطّون الستوب بنفس المكان الواضح.') }),
  // …value slides…
  K.slide({ num:'٥', total:'٥', bg:`${BG}/bg-05-gem.png`, kt:'الخلاصة', ke:'TAKEAWAY',
    main: K.QUOTE(`لا تحط استوبك وين يحطّه <span style="color:${K.RED}">الكل</span>.`) + K.CTA('احفظ الدرس','سيولة'), last:true }),
];
await K.renderSlides(slides, 'out', { scale:2 });   // -> out/01.png … out/0n.png
```

## Components (all return inner HTML for `main`)

| fn | slide role |
|---|---|
| `H(html, size)` | headline (Cairo Black; put accent words in `<span style="color:…">`) |
| `P(html, size)` | body paragraph (Tajawal) |
| `CARD(html)` | glass panel |
| `STAT(num, label)` | big number + label (e.g. `STAT('1%', '…')`) |
| `STEPS([...], start)` | numbered framework (Arabic-Indic ١٢٣…); `start` offsets numbering |
| `TWO({c,h,b},{c,h,b})` | two contrast glass cards |
| `QUOTE(html)` | large quote (the screenshot/share slide) |
| `CTA(title, keyword)` | save + ManyChat keyword card |
| `CHART(markers)` | real chart card (needs `realistic-trading-chart` skill); pass markers `[{i,at,dir,color,label}]` or omit for auto sweep annotation |

Palette exports: `K.GREEN K.MINT K.RED K.AMBER K.GREY`. Red/amber are **semantic**
(fear/greed) — everything else stays brand teal-green. `slide()` accepts `acc`
to retint the kicker/accents per carousel.

## Rules baked in

- **Typography:** Cairo 900 headlines, Tajawal 500 body — one big hook per slide.
- **Backgrounds:** pass a PNG from `liquidity-3d-backgrounds/assets` (one per carousel for cohesion, or per-slide themed). The scrim darkens the text side (right, RTL) so copy stays ≥ 4.5:1.
- **Logo + colors:** brand gem + dark-teal + teal-green are always on; never introduce off-brand colors.
- **Voice/dialect:** follow `liquidity-state-brand` (نقول: إهي / تعورك / صكّر …). Content architecture (hook→value→quote→CTA, one keyword) follows `carousel-design-pro`.

## Files
- `scripts/carousel-kit.js` — theme + components + `slide()` + `renderSlides()`.
- `fonts/` — Cairo (400/700/900) + Tajawal (400/700/800) Arabic woff2, base64-inlined at build.

Rendering needs `playwright-core` + a Chromium (auto-detected). Chart slides need the sibling `realistic-trading-chart` skill.
