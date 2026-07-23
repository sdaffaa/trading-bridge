"""Pure-Python technical indicators computed from OHLC candles.

Deliberately dependency-free (no numpy/pandas) so the app stays lightweight.
compute() produces a compact market snapshot that grounds the AI recommendation
and also feeds the rule-based fallback.
"""


def _closes(candles):
    return [c["c"] for c in candles]


def ema(values, period):
    """Exponential moving average of the last value in `values`."""
    if len(values) < period:
        return None
    k = 2 / (period + 1)
    # seed with SMA of the first `period` values
    e = sum(values[:period]) / period
    for v in values[period:]:
        e = v * k + e * (1 - k)
    return e


def rsi(values, period=14):
    """Wilder's RSI on the last `period` window."""
    if len(values) <= period:
        return None
    gains, losses = 0.0, 0.0
    for i in range(1, period + 1):
        diff = values[i] - values[i - 1]
        if diff >= 0:
            gains += diff
        else:
            losses -= diff
    avg_gain = gains / period
    avg_loss = losses / period
    for i in range(period + 1, len(values)):
        diff = values[i] - values[i - 1]
        gain = diff if diff > 0 else 0.0
        loss = -diff if diff < 0 else 0.0
        avg_gain = (avg_gain * (period - 1) + gain) / period
        avg_loss = (avg_loss * (period - 1) + loss) / period
    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


def atr(candles, period=14):
    """Average True Range — used to size stops/targets."""
    if len(candles) <= period:
        return None
    trs = []
    for i in range(1, len(candles)):
        h = candles[i]["h"]
        l = candles[i]["l"]
        prev_close = candles[i - 1]["c"]
        tr = max(h - l, abs(h - prev_close), abs(l - prev_close))
        trs.append(tr)
    # Wilder smoothing
    a = sum(trs[:period]) / period
    for tr in trs[period:]:
        a = (a * (period - 1) + tr) / period
    return a


def compute(candles):
    """Return a dict snapshot of the market state."""
    closes = _closes(candles)
    price = closes[-1]

    ema20 = ema(closes, 20)
    ema50 = ema(closes, 50)
    ema200 = ema(closes, 200) if len(closes) >= 200 else None
    rsi14 = rsi(closes[-100:] if len(closes) > 100 else closes, 14)
    atr14 = atr(candles, 14)

    # recent swing range (last 20 bars)
    recent = candles[-20:]
    recent_high = max(c["h"] for c in recent)
    recent_low = min(c["l"] for c in recent)

    # trend classification from EMA stack + price
    trend = "neutral"
    if ema20 and ema50:
        if price > ema20 > ema50:
            trend = "up"
        elif price < ema20 < ema50:
            trend = "down"

    # short-term momentum: % change over last 10 bars
    if len(closes) >= 11:
        momentum = (closes[-1] - closes[-11]) / closes[-11] * 100
    else:
        momentum = 0.0

    return {
        "price": round(price, 6),
        "ema20": _r(ema20),
        "ema50": _r(ema50),
        "ema200": _r(ema200),
        "rsi14": _r(rsi14, 2),
        "atr14": _r(atr14),
        "recent_high": round(recent_high, 6),
        "recent_low": round(recent_low, 6),
        "trend": trend,
        "momentum_pct": round(momentum, 2),
    }


def _r(x, digits=6):
    return round(x, digits) if x is not None else None
