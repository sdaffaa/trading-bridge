# The canvas model — hovering, selecting a candle, reading exact values

TradingView draws candles, axes, and drawings on `<canvas>`. There is **no DOM
per candle**. So the whole game of "select and read precisely" is:

> Move the pointer over the canvas → read ground truth back from the two DOM
> read-outs (legend + Data Window) → adjust → confirm.

Trying to compute "price → pixel Y" from the DOM does not work: the price axis
labels are painted on canvas too. Don't attempt pixel-to-price math. Use the
techniques below instead — they are how a human actually does it.

## The two read-outs (ground truth)

1. **Series legend** (`[data-name="legend-source-item"]`, top-left): shows
   `O H L C` + change of the bar under the crosshair. Fast, approximate to read.
2. **Data Window** (`[data-name="data-window"]` in the right widget bar): shows
   precise `Open / High / Low / Close / Volume` **and the date/time** of the
   hovered bar. This is the authority for *which* candle you're on and *what* its
   values are. Open it once at the start of a selection task.

Both update on `mousemove` over the chart. After every pointer move, **read them
back** — that read-back is what turns "roughly there" into "exactly there".

## Getting the chart region

Send mouse events relative to the chart pane's bounding box:

```
box = chart_locator.bounding_box()   # {x, y, width, height}
# a point inside the chart:
px = box["x"] + fx * box["width"]     # fx, fy in 0..1
py = box["y"] + fy * box["height"]
```

Keep away from the very edges (axes and toolbars live there). Use `fx` in
`0.05..0.92` and `fy` in `0.10..0.85`.

## Hover a specific candle (select by read-back, not by pixel)

The time axis maps left→right = older→newer. To land on a target bar, **search
X while reading the Data Window's date**, like sliding the crosshair:

1. Open the Data Window.
2. Start at the right edge (newest) and move left, or binary-search:
   - Move pointer to `fx`, read the Data Window date.
   - If the shown date is **after** your target, move left; if **before**, move
     right. Halve the step each time.
   - Stop when the date equals your target bar (or you're within one bar and the
     step is a single candle width).
3. Read `O/H/L/C/V` from the Data Window for that bar.

This converges in ~6–10 moves for any visible bar. If the target isn't on
screen, scroll time first (`Ctrl+←/→`, wheel, or `Alt+R` to jump to latest), or
use **Bar Replay** (`#header-toolbar-replay`) to step candle-by-candle — replay
is the deterministic way to land on an exact historical bar with zero aiming.

`scripts/tv_agent.py` implements this as `hover_bar_by_time(target)` and
`read_ohlc()`.

## Place an EXACT price level (type it, don't aim it)

Mouse-aiming a horizontal line to a precise price is impossible on a canvas.
Do it the human-precise way:

1. `Alt+H` (horizontal line tool) → click anywhere on the canvas to drop it.
2. Double-click the line (or right-click → Settings) to open its settings dialog.
3. The **Price** field is a real DOM `<input>` — clear it, type the exact price,
   press `Enter`.
4. Read it back from the settings/legend to confirm.

For levels that must sit on a candle's high/low/open/close, enable **Magnet
mode** (`[data-name="magnet"]`) first so the tool snaps to OHLC as you draw —
then you don't even need to type.

## Reading works, writing pixels doesn't — summary

| Goal | Right way | Wrong way (don't) |
|---|---|---|
| Which candle am I on | Read Data Window date after hover | Count pixels from the edge |
| Exact O/H/L/C/V of a bar | Read Data Window while hovering it | OCR the canvas |
| Put a line at price X | Draw line → type price in settings input | Aim the mouse at a Y pixel |
| Snap a line to a candle's high | Magnet mode + draw | Eyeball the wick |
| Land on a historical bar | Bar Replay step, or read-back search | Guess the X coordinate |

## Confirm & capture

After any change, screenshot the **chart region only** (crop to the chart
bounding box), not the whole page — it's cleaner evidence and smaller.
`scripts/tv_agent.py screenshot_chart(path)` does the crop for you.
