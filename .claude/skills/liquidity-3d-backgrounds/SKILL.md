---
name: liquidity-3d-backgrounds
description: A library of 10 reusable, brand-colored 3D (WebGL/Three.js) backgrounds for Liquidity State designs — carousels, reels, covers, thumbnails, story frames. Real 3D scenes (perspective grids, particle vortex, wireframe gem, candlestick field, nebula, tunnel, terrain, network, rings, wavefield) rendered to PNG, all in the brand dark-teal + teal-green palette. Use this whenever a design needs a premium 3D background instead of a flat gradient — pre-rendered PNGs are ready in assets/, or render any scene at any size with the generator. Triggers include: "خلفية ثلاثية الأبعاد", "خلفية 3D", "3D background", "خلفية للسلايد/الغلاف/الريل", "مشهد ثلاثي الأبعاد", or picking a background for a brand design.
---

# Liquidity State — 3D Backgrounds

Ten reusable WebGL backgrounds, all in the brand palette (bg `#0A171C`, teal-green
`#2ECC9A`, mint `#7BEBC8`, soft-red `#E15A5A`). Pre-rendered PNGs live in `assets/`;
the generator re-renders any scene at any size.

## The 10 scenes

| # | name | what it is | best for |
|---|---|---|---|
| 1 | `sun-grid` | synthwave sun + perspective grid floor | default hero, covers |
| 2 | `vortex` | particle spiral / portal | revenge-spiral, psychology, "دوامة" |
| 3 | `tunnel` | square wireframe tunnel receding | motion, momentum |
| 4 | `candles` | floating 3D bull/bear candlesticks | trading / documented-trade content |
| 5 | `gem` | wireframe icosahedron (the brand mark) + glow | on-brand hero, identity |
| 6 | `terrain` | synthwave wireframe mountains | cinematic covers |
| 7 | `wavefield` | dot-grid wave surface | calm / editorial |
| 8 | `network` | 3D node-and-edge graph | "شبكة السيولة" / liquidity network |
| 9 | `rings` | concentric glowing rings / ripples | sonar / liquidity pulse |
| 10 | `nebula` | glowing particle cloud | atmospheric, quotes |

## Use pre-rendered assets (fastest)

`assets/bg-01-sun-grid.png … bg-10-nebula.png` are 1080×1350 (4:5) @2x. Drop one
behind your slide content as a CSS background, then add a readability scrim over the
text side:

```css
.slide{background:#0A171C}
.bg3d{position:absolute;inset:0;background:url('bg-05-gem.png') center/cover no-repeat}
.scrim{position:absolute;inset:0;               /* darken the text side (right, RTL) */
  background:linear-gradient(270deg, rgba(8,18,22,.66) 0%, rgba(8,18,22,.30) 44%, transparent 72%)}
```
Keep the grain + vignette + brand chrome (gem logo, Cairo/Tajawal type) on top — see
`carousel-design-pro`.

## Render fresh (any scene / size / crop)

```bash
npm i playwright-core            # once; three is vendored (three.bundle.js)
node scripts/bg3d-scenes.js --scene gem --out bg.png --width 1080 --height 1350 --scale 2
node scripts/bg3d-scenes.js --all --outdir assets      # re-render all 10
```
Or from code:
```js
const { SCENES, renderScene } = require('./scripts/bg3d-scenes');
await renderScene('vortex', { out:'bg.png', width:1080, height:1920, scale:2 }); // reel size
```
Compositions are tuned for the 4:5 (0.8) aspect; other aspects still work but
re-check framing. Change the palette constants (`TEAL/MINT/RED/BG`) in `HEAD` to
retheme — keep them on brand.

## Files
- `scripts/bg3d-scenes.js` — the 10 scene defs + `renderScene()` + CLI.
- `scripts/three.bundle.js` — vendored Three.js (single-file ESM, no network needed).
- `assets/bg-01…bg-10.png` — ready-to-use 1080×1350 backgrounds.

## Notes
- Rendering needs a Chromium with WebGL; software swiftshader is fine (flags handled in the script). Auto-detects `$CHROMIUM_PATH` / `/opt/pw-browsers`.
- These are backgrounds — always lay a scrim/vignette between the 3D and the copy so text stays ≥ 4.5:1 contrast.
- Never let a scene introduce off-brand colors; the palette is teal-green / soft-red / dark-teal / silver only (warm amber only as a semantic accent for "greed").
