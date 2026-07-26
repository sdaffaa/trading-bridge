"""Market-hours awareness — don't burn analysis when the market is closed.

Crypto trades 24/7. Forex/metals (XAUUSD, EURUSD, ...) run from Sunday ~21:00
UTC to Friday ~21:00 UTC. This is a pragmatic approximation (no holiday
calendar); good enough to stop the scheduler from firing all weekend.
"""
from datetime import datetime, timezone

_CRYPTO_HINTS = ("BTC", "ETH", "USDT", "USDC", "BNB", "SOL", "XRP", "DOGE", "ADA")

# Forex week (UTC): opens Sun 21:00, closes Fri 21:00.
_OPEN_WEEKDAY, _OPEN_HOUR = 6, 21      # Sunday 21:00
_CLOSE_WEEKDAY, _CLOSE_HOUR = 4, 21    # Friday 21:00


def asset_class(symbol: str) -> str:
    s = symbol.split(":")[-1].upper()
    if any(h in s for h in _CRYPTO_HINTS):
        return "crypto"
    return "forex"


def is_open(symbol: str, now: datetime = None) -> bool:
    if asset_class(symbol) == "crypto":
        return True
    now = now or datetime.now(timezone.utc)
    wd, hr = now.weekday(), now.hour        # Mon=0 .. Sun=6
    if wd == 5:                              # Saturday: closed all day
        return False
    if wd == 6:                              # Sunday: open only from 21:00
        return hr >= _OPEN_HOUR
    if wd == 4:                              # Friday: closed from 21:00
        return hr < _CLOSE_HOUR
    return True                             # Mon-Thu: open
