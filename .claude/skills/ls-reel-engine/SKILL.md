---
name: ls-reel-engine
description: >-
  Produce a premium, silent, vertical (1080×1920) educational trading reel for Liquidity State — animated
  brand-styled candlesticks, a TradingView-like price axis + Volume Profile, sequenced markup (VAH/POC/VAL,
  entry/SL/targets), three disciplined camera moves, Arabic beats, and a keyword CTA — rendered deterministically
  to an H.264 MP4. Use this WHENEVER the task is to build/redesign/render a trading reel, short, or animated chart
  video, convert a scenario or carousel into a reel, or the user says "ريل / صمم الريل / أعد تصميم الفيديو /
  انتج الفيديو / موشن شارت / stop reel / VWAP reel / Volume Profile reel". It renders from a verified `scenario.json`
  (see verified-market-charts) so the motion is always tied to real, disclosed data; pair the two skills.
---

# Liquidity State — Reel Engine

A reel is rendered **deterministically**: one browser scene exposes `window.buildStage(t)` that computes every
element's state for a timestamp `t` (candle reveal masks, sequential markup, camera transform). We screenshot 705
frames (30fps × 23.5s) then encode. Deterministic = no jitter, exact timing, reproducible.

## Pipeline (4 steps)

```bash
# 0. get a verified scenario first (verified-market-charts) -> data/scenario.json
# 1. assemble self-contained HTML (inline fonts + data + scene template)
node scripts/build_html.mjs --data data/scenario.json \
  --scene scripts/scene.template.js --fonts assets/fonts --out index.html
# 2. capture frames (needs Playwright + Chromium; Chromium is preinstalled at /opt/pw-browsers)
node scripts/render_frames.mjs --html index.html --out frames --fps 30 --dur 23.5
# 3. encode spec-master (~16 Mbps CBR) + web copy (small, for chat)
bash scripts/encode.sh frames out/liquidity-state-reel 30
```

Output spec (locked): **1080×1920 · 9:16 · 30fps CFR · H.264 High · yuv420p · Rec.709 · ~16 Mbps · MP4 faststart
· silent · no watermark.** The reel is silent by design — hand the editor the SFX cue sheet
(`references/audio-cues.md`) instead of synthesizing library music.

## The scene template & its data contract

`scripts/scene.template.js` is the VP stop-placement reel (Volume Profile primary + ICT structure). It reads
`window.__DATA` (the `scenario.json` from `build_scenario.mjs`). Key fields it consumes:
`candles[]{o,h,l,c,v}`, `vah/poc/val`, `rangeI0/rangeI1` (Fixed Range), `exitIdx/exitHigh`, `failIdx`,
`entryIdx/entryPrice`, `slPrice/slMargin`, `pocTargetIdx/valTargetIdx`, `profile[]{p,v}`, and the source
metadata (`symbol/source/tf/volType/firstDate/lastDate/valueAreaPct`) shown in the header disclosure.

To retheme or change the lesson, edit the template — it is plain browser JS (no build step) using helpers
`lerp/smooth/seg/fade`, a `cam(t)` keyframed camera, `chartSVG(t)` (candles + axis + profile + markup), a text
timeline `T`, and `buildStage(t)`. Chart geometry, the price axis, and the live last-price tag are all in
`chartSVG`. Keep every price/label change tied to `__DATA` so the render stays provably real.

## What the engine already gets right (don't regress)
- **RTL-safe SVG text**: Latin chips force `direction="ltr"`; Arabic uses `direction="rtl" unicode-bidi="plaintext"`
  with `text-anchor="middle"`. SVG `<text>` otherwise inherits the page's RTL and runs off-canvas.
- **Screen-pinned price axis & level chips**: drawn outside the camera `<g>` at `cm.ty + cm.s*yP(price)` so they
  stay readable (like a real price axis) when the camera zooms — never inside the transformed group.
- **Exact 1080×1920**: capture at deviceScaleFactor 1 (native). If you supersample at 2× for text crispness,
  downscale with Lanczos before encoding — deliverables must be exactly 1080×1920.

Timing, beats and camera rules: `references/timing-and-camera.md`. Colors, type, safe zones, per-tool chart
sizing: `references/design-system.md`. Audio hand-off: `references/audio-cues.md`.

## QA before delivery
Verify container (`ffmpeg -i`): 1080×1920, 30fps, h264 High, yuv420p, faststart (moov before mdat). Extract a few
frames from the *encoded* file and check: Arabic connected (no tofu/reversal), no clipped text, markup not covering
candles, price axis + last-price tag correct, source disclosure present. The 16 Mbps master often exceeds a 30 MB
chat limit — deliver the CRF-14 `_web.mp4` in chat and keep the master in the repo.
