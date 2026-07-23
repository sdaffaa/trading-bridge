"""Free market data via the public Yahoo Finance chart endpoint.

No API key required. Covers gold/metals, forex, crypto and indices with a
single source, which is why it's used here instead of a keyed provider.

get_candles() returns a normalized list of OHLC candles (oldest -> newest)
plus the latest price.
"""

import requests

_BASE = "https://query1.finance.yahoo.com/v8/finance/chart/"

# Yahoo rejects requests without a browser-like User-Agent.
_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/122.0 Safari/537.36"
    )
}


class MarketDataError(Exception):
    pass


def get_candles(yahoo_symbol, interval="1h", range_="1mo", timeout=12):
    """Fetch OHLC candles for a Yahoo symbol.

    Returns a dict: {"price": float, "candles": [{o,h,l,c,v,t}, ...]}
    Candles are ordered oldest -> newest, with null bars dropped.
    """
    url = _BASE + yahoo_symbol
    params = {"interval": interval, "range": range_, "includePrePost": "false"}
    try:
        resp = requests.get(url, params=params, headers=_HEADERS, timeout=timeout)
    except requests.RequestException as exc:
        raise MarketDataError("تعذّر الاتصال بمزوّد البيانات: " + str(exc))

    if resp.status_code != 200:
        raise MarketDataError("رد غير متوقع من مزوّد البيانات: HTTP " + str(resp.status_code))

    try:
        data = resp.json()
        result = data["chart"]["result"][0]
        timestamps = result.get("timestamp") or []
        quote = result["indicators"]["quote"][0]
        opens = quote.get("open", [])
        highs = quote.get("high", [])
        lows = quote.get("low", [])
        closes = quote.get("close", [])
        volumes = quote.get("volume", [])
        meta = result.get("meta", {})
    except (KeyError, IndexError, TypeError, ValueError) as exc:
        raise MarketDataError("بيانات غير صالحة من المزوّد: " + str(exc))

    candles = []
    for i in range(len(timestamps)):
        o, h, l, c = (
            _at(opens, i),
            _at(highs, i),
            _at(lows, i),
            _at(closes, i),
        )
        if None in (o, h, l, c):
            continue
        candles.append({
            "t": timestamps[i],
            "o": float(o),
            "h": float(h),
            "l": float(l),
            "c": float(c),
            "v": float(_at(volumes, i) or 0),
        })

    if len(candles) < 30:
        raise MarketDataError("عدد الشموع غير كافٍ للتحليل.")

    price = meta.get("regularMarketPrice") or candles[-1]["c"]
    return {"price": float(price), "candles": candles}


def _at(seq, i):
    try:
        return seq[i]
    except (IndexError, TypeError):
        return None
