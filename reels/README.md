# Liquidity State — Branded Reel Kit

Educational trading Reels (1080×1920) in the **Liquidity State** brand identity,
built to match the swipe-style animated-chart format (à la @vaultfxtrading) but
fully re-skinned to the brand:

- Dark-teal gradient canvas (`#0E1E24 → #12262E`) — never white, never pure black
- Teal-green bullish `#2ECC9A` / soft-red bearish `#E15A5A` candles
- White faceted **gem** watermark + `LIQUIDITY STATE` wordmark
- Arabic **Tajawal** hook text (correct RTL shaping, rendered in-browser)
- Animated lesson beats: swing High/Low → liquidity sweep → Order Block + FVG entry
- Gold accent `#E9C46A` for FVG / key terms

Everything is a pure function of time `t`, so renders are 100% deterministic.

## Files

| File | Purpose |
|---|---|
| `template.html` | The whole reel. Edit the `CONFIG` block to make a new video. |
| `render.mjs` | Drives Chromium frame-by-frame → PNG sequence in `out/frames`. |
| `fonts/` | Tajawal TTFs (loaded locally for identical render). |
| `out/` | Rendered frames + final MP4 (git-ignored except the sample). |

## Make a new video

1. Copy `template.html` → `my-topic.html`.
2. Edit only the **`CONFIG`** block near the top:
   - `candles`: array of `[open, high, low, close]` telling your lesson.
   - `swingHigh` / `swingLow` / `sweepIdx` / `obIdx` / `fvgBand`: where the annotations land.
   - `beats`: the timed Arabic hook lines. Use `<em>` (teal), `<b>` (gold),
     `<span class='sub'>` (grey subtitle). English only for technical terms
     (Order Block, FVG, POC…), per brand voice.
   - `duration` / `fps`.
3. Render + encode:

```bash
cd reels
node render.mjs my-topic.html out/frames
FF=$(python3 -c "import imageio_ffmpeg as f;print(f.get_ffmpeg_exe())")   # or system ffmpeg
"$FF" -y -framerate 30 -i out/frames/f%04d.png \
  -c:v libx264 -pix_fmt yuv420p -profile:v high -crf 18 -movflags +faststart \
  out/my-topic.mp4
```

## Preview locally

Open `template.html` in any browser — it auto-plays on a loop (live preview).
The render path calls `window.__setT(seconds)` for deterministic frames.

## Real chart data

`market-clarity.html` uses **real COMEX Gold (GC=F ≈ XAUUSD, 1H) candles** pulled
from a live market feed, not illustrative data. The annotations are computed from
that real series: the volume profile POC/VAH/VAL, the HH/HL swings + BOS break,
and the balance range + real Fair Value Gap.

Because this environment's network policy blocks outbound market-data hosts, the
data was fetched via the Higgsfield sandbox (which has open internet), then the
selected windows + detected structures were dropped into the `SCENES` config. To
refresh with a newer window, re-run the fetch/analysis and replace the candle
arrays. Any real OHLC source works (TradingView CSV export, a screenshot I read,
or a broker export) — the template only needs `[open,high,low,close]` arrays.

## Notes

- **Logo:** the gem is a clean SVG placeholder matching the brand spec
  (white faceted gem). To use the real logo, replace the two inline
  `<svg class="gem">…</svg>` blocks with your `<img src="logo.png">`.
- **Audio:** rendered silent by design. Add your licensed track + voiceover in
  your editor, or wire it through the `arabic-voiceover` / `reels-design-pipeline`
  skills. Master to **-14 LUFS** for Instagram.
- **Safe zones:** hook text sits above the bottom ~300px; top ~200px kept clear —
  clears IG Reels UI.
- Rendering ~600 frames takes a few minutes; frames are screenshot via the
  pre-installed Chromium headless-shell.
