# TradingView keyboard shortcuts — the human-fast command set

Keyboard is the single biggest speed win on TradingView, and it is more robust
than locating buttons because it doesn't depend on markup. **Focus the chart
first** (click once anywhere on the chart canvas) so keystrokes go to the chart,
not to a text field. In Playwright: `page.locator(<chart>).click()` then
`page.keyboard.press(...)`.

## Symbol

| Action | How | Notes |
|---|---|---|
| Open symbol search | Just **start typing** the symbol while the chart is focused (e.g. type `X`, `A`, `U`…) | A search box pops up automatically. This is faster than clicking `#header-toolbar-symbol-search`. |
| Confirm symbol | Type the full ticker → **`Enter`** | Takes the top match. Type an exchange prefix (`OANDA:XAUUSD`, `BINANCE:BTCUSDT`) to disambiguate. |
| Cancel | **`Esc`** | Closes the search without changing symbol. |

## Interval / timeframe

Press a **digit while the chart is focused** to open the interval quick-input,
then type the resolution and `Enter`:

| Type then Enter | Result |
|---|---|
| `1` | 1 minute |
| `5` | 5 minutes |
| `15` | 15 minutes |
| `60` | 1 hour (60 min) |
| `240` | 4 hours |
| `1D` or `D` | 1 day |
| `1W` or `W` | 1 week |
| `1M` | 1 month |
| `10S` | 10 seconds (needs a plan that supports seconds) |

So "switch to 4H" = focus chart → press `2` `4` `0` → `Enter`, or type `4H`
`Enter`. Confirm by reading the interval label in the header
(`#header-toolbar-intervals`).

## Drawing tools (default binds)

| Shortcut | Tool |
|---|---|
| `Alt+T` | Trend line |
| `Alt+H` | Horizontal line |
| `Alt+V` | Vertical line |
| `Alt+C` | Cross line |
| `Alt+F` | Fib retracement |
| `Esc` | Deselect tool → return to crosshair |
| `Delete` / `Backspace` | Remove the selected drawing |
| `Ctrl+Z` / `Ctrl+Y` | Undo / Redo |
| `Ctrl+Alt+H` | Hide/show all drawings |

After picking a tool with a shortcut, you draw with the mouse on the canvas
(see `canvas-and-reading.md`). To place a **price-exact** horizontal line, draw
it roughly then open its settings and type the price — don't try to hit the
pixel (see the same reference).

## View / navigation

| Shortcut | Action |
|---|---|
| `Alt+R` | Reset chart view (auto scale + scroll to latest) |
| `+` / `-` | Zoom in / out |
| `Ctrl+←` / `Ctrl+→` | Nudge scroll left/right in time |
| Mouse wheel over chart | Zoom time axis at cursor |
| Wheel over price axis | Rescale price only |
| `Alt+I` | Invert the price scale |

## Panels & dialogs

| Shortcut | Action |
|---|---|
| `/` | Focus/open symbol search (alternative to just typing) |
| `Ctrl+S` | Save chart layout |
| `Esc` | Close the top-most dialog / cancel current tool |

## Replay (bar-by-bar playback — great for deterministic "select this bar")

Open replay via `#header-toolbar-replay`. Once in replay you can step bars with
the on-canvas controls. Replay is the most reliable way to land on an exact
historical bar because the chart advances one candle at a time — no pixel aiming.

## Practical macros (chain these)

- **Go to symbol + timeframe fast:** focus chart → type `OANDA:XAUUSD` `Enter`
  → wait legend → press `2` `4` `0` `Enter` → confirm header shows `4h`.
- **Clean slate:** `Ctrl+Alt+H` to hide drawings, `Alt+R` to reset view.
- **Drop and price a level:** `Alt+H` → click on canvas → double-click the line
  → type exact price in the settings input → `Enter`.
