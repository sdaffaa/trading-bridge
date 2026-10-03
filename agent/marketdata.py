"""Live market data — so scheduled analysis uses real prices, no browser.

Pluggable provider: "none" (default), "fmp" (Financial Modeling Prep), or
"generic" (any HTTPS JSON endpoint + a dot-path to the price). Degrades
gracefully: a data error is returned as data, never raised, so the agent can
still decide (conservatively) or escalate.
"""
import requests

from . import config
from .logging_setup import jlog


def _bare(symbol: str) -> str:
    """OANDA:XAUUSD -> XAUUSD ; BINANCE:BTCUSDT -> BTCUSDT."""
    return symbol.split(":")[-1].strip().upper()


def _dig(obj, path: str):
    cur = obj
    for part in path.split("."):
        if isinstance(cur, list):
            try:
                cur = cur[int(part)]
                continue
            except (ValueError, IndexError):
                return None
        if isinstance(cur, dict):
            cur = cur.get(part)
        else:
            return None
    return cur


def get_quote(symbol: str) -> dict:
    """Return {symbol, price, source} or {symbol, error}."""
    provider = config.DATA_PROVIDER
    try:
        if provider == "fmp":
            return _fmp(symbol)
        if provider == "generic":
            return _generic(symbol)
        return {"symbol": symbol, "error": "no data provider configured (AGENT_DATA_PROVIDER)"}
    except requests.RequestException as e:
        jlog("marketdata_error", symbol=symbol, provider=provider, error=str(e))
        return {"symbol": symbol, "error": f"data fetch failed: {e}"}


def _fmp(symbol: str) -> dict:
    if not config.DATA_API_KEY:
        return {"symbol": symbol, "error": "AGENT_DATA_API_KEY not set for fmp"}
    sym = _bare(symbol)
    url = f"https://financialmodelingprep.com/api/v3/quote/{sym}"
    r = requests.get(url, params={"apikey": config.DATA_API_KEY},
                     timeout=config.DATA_TIMEOUT_S)
    r.raise_for_status()
    data = r.json()
    if not data:
        return {"symbol": symbol, "error": f"no quote for {sym}"}
    q = data[0]
    return {"symbol": symbol, "price": q.get("price"),
            "day_low": q.get("dayLow"), "day_high": q.get("dayHigh"),
            "change_pct": q.get("changesPercentage"), "source": "fmp"}


def _generic(symbol: str) -> dict:
    if not config.DATA_URL_TEMPLATE:
        return {"symbol": symbol, "error": "AGENT_DATA_URL_TEMPLATE not set for generic"}
    url = config.DATA_URL_TEMPLATE.format(symbol=_bare(symbol), full=symbol)
    r = requests.get(url, timeout=config.DATA_TIMEOUT_S)
    r.raise_for_status()
    price = _dig(r.json(), config.DATA_PRICE_PATH)
    if price is None:
        return {"symbol": symbol, "error": f"price not found at path {config.DATA_PRICE_PATH}"}
    return {"symbol": symbol, "price": price, "source": "generic"}
