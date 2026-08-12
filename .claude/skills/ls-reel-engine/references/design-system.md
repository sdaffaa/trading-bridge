# Reel design system

## Palette (locked)
- Navy hook bg: `#04121C` (radial to `#0a2230`). Content bg: warm off-white `#F6F1E9→#EAE0D2`.
- Chart card: `#0E1E24→#12262E`, border `#21414c`, radius 30, padding 34.
- Candles on the dark card: **bull cyan `#2FC6C6`**, **bear steel `#90A7AF`** (bears are NOT red/green — those
  are reserved). Red `#DF7573` = stop only. Teal/green `#57C7A6` = targets only. Amber `#E0A458` = POC.
- Level lines: VAH/VAL cyan, POC amber. Grid `#173039`. Price axis rule `#20404a`, ticks `#3a5a64`, labels `#8fa8b0`.
- Text on chart: near-white `#EAF2F3`; on off-white: `#12333f`. Muted labels `#728b95`.

## Typography
- Arabic: **IBM Plex Sans Arabic** (family `Plex` in the bundle). Latin numerals/tickers: Inter (`InterLS`).
- Hook title ~96px; teaching beat ~64px; CTA main ~82px, sub ~44px. Two lines max, 4–7 words per shot.
- Price-axis labels ~17px; level chips ~19px. Keep one big idea per screen.

## Layout & safe zones
- Canvas 1080×1920. Keep key content out of the **top 250px** and **bottom 320px** (platform UI). Logo top-center,
  quiet. Full educational disclaimer goes in the caption, not stacked on the video.
- Chart card ~ x64,y600,952×980. Inside the card SVG (884×912): header 96px, plot below, right price-axis gutter
  ~48px, Volume Profile ~118px just left of the axis, candles fill the rest.

## Per-tool chart sizing (when adapting the template to other schools)
- SMC/ICT: candle panel ≥470px tall; ≤3 structure labels at once; shrink the HTF panel to 280–320px when stepping
  down to LTF.
- Footprint: make it the largest element (panel 720–820px); Bid×Ask numerals ≥34px; zoom absorption/imbalance to
  115–130%; never resize/alter a real number.
- Volume Profile: histogram 18–25% of width; VAH/POC/VAL clear (lines 4–6px); show the range start/end; don't
  cover the candles.
- VWAP: line 5–6px, bands 3–4px and quieter than candles; label type + anchor.
- Volume: candles 68–74% height, histogram 22–28%; tie each bar to its candle by spotlight, not a long arrow.

## Focus rule
One primary chart on screen at a time; primary tool 65–75% of the analysis area, support 25–35%; ≤3 labels at once;
hide a card once its job is done. No persistent grid-of-all-conditions.
