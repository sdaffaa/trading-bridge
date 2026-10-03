# Moving like a human — pacing, pathing, and anti-fragile waits

"Fast like a human" is not "instant". Instant, teleporting clicks (a) skip the
frames TradingView needs to open menus and render tooltips, so they silently
miss, and (b) read as a bot. Human-fast = **no wasted motion + the minimum
settle time each widget needs + read-back instead of blind sleeps.**

## Mouse: glide, don't teleport

Menus, tooltips, and the crosshair legend only respond to real `mousemove`
events. Move the pointer in several small steps with slight jitter along the
path, not one jump:

- ~12–25 intermediate steps over a short curve.
- A few pixels of random jitter per step.
- ~4–10 ms between steps.

`tv_agent.human_move(x, y)` implements this. Straight teleports (`mouse.move`
in one shot) will make hover-dependent UI (legend updates, tooltips, submenus)
fail intermittently.

## Click: hover → settle → click

1. `human_move` to the target.
2. Pause ~80–150 ms (let the hover state / menu render).
3. Click.
4. If it opens a menu/dialog, wait for that element to be **visible** before the
   next action — not a fixed timer.

`tv_agent.human_click(locator)` encodes this.

## Typing: per-character, not paste

Type symbols and indicator names character-by-character with ~30–90 ms between
keys, then `Enter`. Pasting a whole string sometimes doesn't trigger
TradingView's search filtering. `page.type(sel, text, delay=...)` or
`tv_agent.human_type`.

## Waits: poll the read-back, never a fixed sleep

Fixed `sleep(3)` is both slow (usually too long) and fragile (sometimes too
short). Instead, **poll a ground-truth read-out until it changes**:

- After changing symbol/interval: poll the legend/header until it shows the new
  value (or the OHLC updates).
- After opening a dialog: wait for the dialog element to be visible.
- After a drawing edit: re-read the value you set.

`tv_agent.wait_until(fn, timeout)` polls a predicate. The only legitimate fixed
pause is the tiny hover-settle (~100 ms), which is about rendering, not data.

## Chart-ready gate

Don't act on `load` or even `networkidle` — TradingView keeps painting. Gate on
a real signal:

```
wait until [data-name="legend-source-item"] exists AND shows a numeric OHLC
```

`tv_agent.wait_chart_ready()` does exactly this. Everything else waits behind it.

## Tuned defaults (used by tv_agent.py)

| Thing | Value | Why |
|---|---|---|
| Mouse steps | 12–25 | Smooth enough to fire hover, cheap enough to stay fast |
| Per-step delay | 4–10 ms | Real motion without dragging |
| Hover-settle before click | 80–150 ms | One+ frame for menus to render |
| Per-key typing delay | 30–90 ms | Triggers search filtering reliably |
| Read-back poll interval | 60–120 ms | Catches the update fast without busy-spinning |
| Read-back timeout | 8–12 s | TradingView data can lag on slow networks |

These are deliberately *tight but not zero*. Loosen only the read-back timeout
on slow links; keep the motion timings.
