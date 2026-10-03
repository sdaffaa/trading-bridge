"""Technical analysis engine — candles + indicators + confluence structure.

Pulls recent OHLC(V) history (FMP: intraday + daily) and computes the picture the
agent's confluence methodology needs:
  - indicators: SMA20/50, EMA20, RSI(14), ATR(14), trend, momentum
  - SMC:  swing highs/lows (pivots) and market structure (HH/HL vs LH/LL)
  - ICT:  unfilled Fair Value Gaps (3-candle imbalances) + liquidity pools
  - Volume Profile: POC and Value Area (VAH/VAL) from a volume/price histogram
  - Footprint proxy: last-bar volume vs average (order-flow hint when volume exists)

Pure-Python (no numpy). Degrades gracefully: returns {"error": ...}.
"""
import requests

from . import config
from .logging_setup import jlog

_FMP_INTERVAL = {"1": "1min", "5": "5min", "15": "15min", "30": "30min",
                 "60": "1hour", "1H": "1hour", "240": "4hour", "4H": "4hour"}


def _bare(symbol: str) -> str:
    return symbol.split(":")[-1].strip().upper()


def get_candles(symbol: str, timeframe: str, limit: int = 200) -> dict:
    """Return {"candles": [{o,h,l,c,v}, ...]} oldest-first, or {"error": ...}."""
    if config.DATA_PROVIDER != "fmp":
        return {"error": "technical analysis needs AGENT_DATA_PROVIDER=fmp"}
    if not config.DATA_API_KEY:
        return {"error": "AGENT_DATA_API_KEY not set"}
    sym, tf = _bare(symbol), str(timeframe)
    try:
        if tf in _FMP_INTERVAL:
            url = f"https://financialmodelingprep.com/api/v3/historical-chart/{_FMP_INTERVAL[tf]}/{sym}"
            r = requests.get(url, params={"apikey": config.DATA_API_KEY},
                             timeout=config.DATA_TIMEOUT_S)
            r.raise_for_status()
            rows = r.json()[:limit]
        else:
            url = f"https://financialmodelingprep.com/api/v3/historical-price-full/{sym}"
            r = requests.get(url, params={"apikey": config.DATA_API_KEY, "timeseries": limit},
                             timeout=config.DATA_TIMEOUT_S)
            r.raise_for_status()
            rows = r.json().get("historical", [])
        candles = [{"o": x["open"], "h": x["high"], "l": x["low"], "c": x["close"],
                    "v": x.get("volume", 0) or 0}
                   for x in rows if all(k in x for k in ("open", "high", "low", "close"))]
        candles.reverse()
        return {"candles": candles}
    except requests.RequestException as e:
        jlog("technical_error", symbol=symbol, error=str(e))
        return {"error": f"candle fetch failed: {e}"}
    except (KeyError, ValueError, TypeError) as e:
        return {"error": f"unexpected data shape: {e}"}


# --- indicators -----------------------------------------------------------
def sma(vals, n):
    return sum(vals[-n:]) / n if len(vals) >= n else None


def ema(vals, n):
    if len(vals) < n:
        return None
    k = 2 / (n + 1)
    e = sum(vals[:n]) / n
    for v in vals[n:]:
        e = v * k + e * (1 - k)
    return e


def rsi(closes, n=14):
    if len(closes) < n + 1:
        return None
    g = l = 0.0
    for i in range(-n, 0):
        d = closes[i] - closes[i - 1]
        g += max(d, 0.0)
        l += max(-d, 0.0)
    if l == 0:
        return 100.0
    return 100 - 100 / (1 + (g / n) / (l / n))


def atr(candles, n=14):
    if len(candles) < n + 1:
        return None
    trs = [max(candles[i]["h"] - candles[i]["l"],
               abs(candles[i]["h"] - candles[i - 1]["c"]),
               abs(candles[i]["l"] - candles[i - 1]["c"]))
           for i in range(1, len(candles))]
    return sum(trs[-n:]) / n if len(trs) >= n else None


# --- SMC: swing pivots + market structure ---------------------------------
def swings(candles, span=2):
    """Fractal pivots: a swing high/low with `span` lower/higher bars each side."""
    highs, lows = [], []
    for i in range(span, len(candles) - span):
        h = candles[i]["h"]
        l = candles[i]["l"]
        if all(h > candles[i - k]["h"] and h > candles[i + k]["h"] for k in range(1, span + 1)):
            highs.append((i, h))
        if all(l < candles[i - k]["l"] and l < candles[i + k]["l"] for k in range(1, span + 1)):
            lows.append((i, l))
    return highs, lows


def structure(sh, sl):
    """HH/HL (bullish) vs LH/LL (bearish) from the last two swings each side."""
    if len(sh) >= 2 and len(sl) >= 2:
        hh = sh[-1][1] > sh[-2][1]
        hl = sl[-1][1] > sl[-2][1]
        if hh and hl:
            return "HH/HL (bullish)"
        if not hh and not hl:
            return "LH/LL (bearish)"
        return "mixed / transition"
    return "insufficient swings"


# --- ICT: Fair Value Gaps (3-candle imbalance) ----------------------------
def fair_value_gaps(candles, price, lookback=40, max_out=3):
    """Unfilled FVGs in the recent window. Bullish: gap up (c[i-1].h < c[i+1].l);
    Bearish: gap down (c[i-1].l > c[i+1].h). Unfilled if price hasn't traded back."""
    out = []
    start = max(1, len(candles) - lookback)
    for i in range(start, len(candles) - 1):
        up_lo, up_hi = candles[i - 1]["h"], candles[i + 1]["l"]
        dn_hi, dn_lo = candles[i - 1]["l"], candles[i + 1]["h"]
        if up_hi > up_lo and price >= up_lo:                 # bullish FVG, not fully filled
            out.append({"type": "bullish", "low": round(up_lo, 5), "high": round(up_hi, 5)})
        elif dn_hi > dn_lo and price <= dn_hi:               # bearish FVG, not fully filled
            out.append({"type": "bearish", "low": round(dn_lo, 5), "high": round(dn_hi, 5)})
    return out[-max_out:]


# --- Volume Profile: POC + Value Area -------------------------------------
def volume_profile(candles, bins=24):
    """POC and 70% value area from a typical-price histogram weighted by volume
    (falls back to bar count when volume is absent)."""
    prices = [(c["h"] + c["l"] + c["c"]) / 3 for c in candles]
    lo, hi = min(c["l"] for c in candles), max(c["h"] for c in candles)
    if hi <= lo:
        return None
    width = (hi - lo) / bins
    hist = [0.0] * bins
    use_vol = any(c["v"] for c in candles)
    for c, p in zip(candles, prices):
        b = min(bins - 1, int((p - lo) / width))
        hist[b] += (c["v"] if use_vol else 1)
    poc_bin = max(range(bins), key=lambda b: hist[b])
    poc = lo + (poc_bin + 0.5) * width
    total = sum(hist)
    target = total * 0.70
    lo_b = hi_b = poc_bin
    acc = hist[poc_bin]
    while acc < target and (lo_b > 0 or hi_b < bins - 1):
        left = hist[lo_b - 1] if lo_b > 0 else -1
        right = hist[hi_b + 1] if hi_b < bins - 1 else -1
        if right >= left:
            hi_b += 1
            acc += hist[hi_b]
        else:
            lo_b -= 1
            acc += hist[lo_b]
    return {"poc": round(poc, 5), "vah": round(lo + (hi_b + 1) * width, 5),
            "val": round(lo + lo_b * width, 5), "source": "volume" if use_vol else "bars"}


def _r(x, d=5):
    return round(x, d) if isinstance(x, (int, float)) else None


def analyze(symbol: str, timeframe: str) -> dict:
    data = get_candles(symbol, timeframe)
    if "error" in data:
        return data
    candles = data["candles"]
    if len(candles) < 30:
        return {"error": f"not enough candles ({len(candles)}) for analysis"}

    closes = [c["c"] for c in candles]
    price = closes[-1]
    s20, s50, e20 = sma(closes, 20), sma(closes, 50), ema(closes, 20)
    r14, a14 = rsi(closes, 14), atr(candles, 14)
    sh, sl = swings(candles)
    struct = structure(sh, sl)

    if s20 and s50:
        trend = "uptrend" if price > s20 > s50 else "downtrend" if price < s20 < s50 else "ranging"
    else:
        trend = "unknown"
    momentum = "neutral"
    if r14 is not None:
        momentum = ("overbought" if r14 >= 70 else "oversold" if r14 <= 30 else
                    "bullish" if r14 >= 55 else "bearish" if r14 <= 45 else "neutral")

    vols = [c["v"] for c in candles]
    avgv = sma(vols, 20)
    vol_state = None
    if avgv:
        ratio = vols[-1] / avgv if avgv else None
        vol_state = ("expanding" if ratio and ratio > 1.5 else
                     "contracting" if ratio and ratio < 0.6 else "average") if any(vols) else "no_volume_data"

    return {
        "symbol": symbol, "timeframe": timeframe, "price": _r(price), "bars": len(candles),
        # indicators
        "trend": trend, "momentum": momentum,
        "sma20": _r(s20), "sma50": _r(s50), "ema20": _r(e20),
        "rsi14": _r(r14, 1), "atr14": _r(a14),
        # SMC
        "market_structure": struct,
        "swing_highs": [_r(h) for _, h in sh[-3:]],
        "swing_lows": [_r(l) for _, l in sl[-3:]],
        "liquidity_above": _r(max((h for _, h in sh), default=max(c["h"] for c in candles))),
        "liquidity_below": _r(min((l for _, l in sl), default=min(c["l"] for c in candles))),
        # ICT
        "fair_value_gaps": fair_value_gaps(candles, price),
        # Volume Profile
        "volume_profile": volume_profile(candles),
        # Footprint proxy
        "volume_state": vol_state,
        "source": "fmp",
    }
