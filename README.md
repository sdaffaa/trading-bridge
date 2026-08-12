# trading-bridge

TradingView → QML detection → Telegram.

The bridge detects **QML (Quasimodo Level)** setups mechanically and forwards the level,
entry, stop, target and R:R. Claude is optional narration on top of an already-structured
setup, not the thing doing the analysis — so alerts are deterministic, reproducible and
unit-testable.

## The pattern

Quasimodo is a head-and-shoulders variant whose right shoulder returns to the **left
shoulder's** extreme. That extreme is the QML — the "Key Level" traders wait for after a
change of character (CHoCH).

**Bullish**, over a strictly alternating swing sequence:

| Swing | Meaning | Condition |
|-------|---------|-----------|
| `L1`  | left shoulder low | **QML sits here** |
| `H1`  | high after L1 | the level whose break is the CHoCH |
| `L2`  | head low | `L2 < L1` |
| `H2`  | high after L2 | `H2 > H1` → **CHoCH** |

Price then retraces into `L1`. Entry at the QML, stop below the sweep of it, target `H2` —
the swing high before price hit the Key Level, i.e. external range liquidity (EQH).

**Bearish** is the exact mirror: `H1 → L1 → H2 → L2` with `H2 > H1` and `L2 < L1`, QML at
`H1`, target `L2` (EQL).

A setup is **INVALIDATED** if price closes through the head before the retrace, or if the
retrace has not arrived within `max_bars_to_retrace` bars.

### Statuses

| Status | Meaning |
|--------|---------|
| `FORMING` | CHoCH has broken but the right shoulder is not a confirmed pivot yet — watch the level |
| `ARMED` | confirmed, waiting for price to retrace into the QML |
| `TRIGGERED` | price reached the QML |
| `INVALIDATED` | head broken, or the retrace never arrived |

## Layout

```
qml/swings.py     fractal pivots, collapsed so highs and lows strictly alternate
qml/detector.py   the pattern engine — find_setups() / latest_setup()
qml/bars.py       payload normalization into a canonical bar series
qml/format.py     Telegram message rendering
tv_claude_bridge.py   Flask webhook
pine/qml_quasimodo.pine   the same rules as a TradingView v6 indicator
```

## Running

```bash
pip install -r requirements.txt
cp .env.example .env      # set WEBHOOK_SECRET at minimum
export $(grep -v '^#' .env | xargs)
python tv_claude_bridge.py
```

`GET /health` → `{"status": "ok"}`, no secret required.

## Webhook contract

`POST /webhook` requires the shared secret, as either the `X-Webhook-Secret` header or a
`secret` field in the body. Two payload shapes are accepted.

**A bar series** — detection runs here:

```json
{
  "symbol": "XAUUSD",
  "tf": "15",
  "secret": "...",
  "bars": [{"t": 1712345678, "o": 2301.4, "h": 2303.0, "l": 2300.1, "c": 2302.7}]
}
```

Both `t/o/h/l/c` and `time/open/high/low/close` key styles work, and bars are sorted by
time, so a newest-first feed is fine.

**A detected setup** — as fired by the Pine indicator:

```json
{
  "symbol": "XAUUSD", "tf": "15", "secret": "...",
  "direction": "BULLISH", "status": "TRIGGERED",
  "qml": 2300.5, "choch": 2312.0, "head": 2288.0,
  "entry": 2300.5, "sl": 2296.9, "tp": 2325.0
}
```

Responses: `200` with the setup (or `"setup": null` if none), `400` on a malformed body,
`401` on a bad secret, `503` if `WEBHOOK_SECRET` is unset on the server.

## TradingView indicator

Paste `pine/qml_quasimodo.pine` into the Pine editor, add it to the chart, and set the
shared secret in its inputs. Create an alert on **"Any alert() function call"** with the
message box left empty and the webhook URL pointing at `/webhook` — the indicator builds
the JSON body itself.

The indicator and the Python engine share the same rules, with one deliberate difference:
the Python engine takes the lowest low over the next `sweep_lookahead` bars when placing the
stop (it has the whole series), while the indicator can only use the triggering bar's
extreme, since it fires live.

## Tests

```bash
python -m pytest -q
```

Synthetic bar series cover both directions, the no-CHoCH case, expiry, head-break
invalidation, the forming state, swing collapsing, payload parsing and every webhook
status code. No network or credentials required.
