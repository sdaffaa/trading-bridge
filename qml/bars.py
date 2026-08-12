"""Normalization of incoming OHLC payloads into a canonical bar series."""

from dataclasses import dataclass


class BadPayload(ValueError):
    """Raised when an incoming payload cannot be read as a bar series."""


@dataclass(frozen=True)
class Bar:
    time: float
    open: float
    high: float
    low: float
    close: float


# TradingView and most feeds use one of these two key styles.
_KEYS = {
    "time": ("time", "t", "timestamp", "datetime"),
    "open": ("open", "o"),
    "high": ("high", "h"),
    "low": ("low", "l"),
    "close": ("close", "c"),
}


def _pick(raw, field, index):
    for key in _KEYS[field]:
        if key in raw:
            return raw[key]
    raise BadPayload("bar %d is missing '%s'" % (index, field))


def _as_float(value, field, index):
    try:
        return float(value)
    except (TypeError, ValueError):
        raise BadPayload(
            "bar %d has a non-numeric '%s' value: %r" % (index, field, value)
        )


def parse_bar(raw, index=0):
    """Build one Bar from a dict, tolerating either key style."""
    if not isinstance(raw, dict):
        raise BadPayload("bar %d is %s, expected an object" % (index, type(raw).__name__))

    values = {
        field: _as_float(_pick(raw, field, index), field, index) for field in _KEYS
    }
    bar = Bar(**values)

    if bar.high < bar.low:
        raise BadPayload("bar %d has high < low" % index)
    if not (bar.low <= bar.open <= bar.high and bar.low <= bar.close <= bar.high):
        raise BadPayload("bar %d has open/close outside its high/low range" % index)
    return bar


def parse_bars(payload):
    """Read a bar series from a bare list or from a {"bars": [...]} envelope.

    Bars are returned in ascending time order; a series that is not already
    sorted is sorted here so a feed that streams newest-first still works.
    """
    if isinstance(payload, dict):
        if "bars" not in payload:
            raise BadPayload("payload has no 'bars' key")
        raw_bars = payload["bars"]
    else:
        raw_bars = payload

    if not isinstance(raw_bars, list):
        raise BadPayload("'bars' is %s, expected a list" % type(raw_bars).__name__)
    if not raw_bars:
        raise BadPayload("'bars' is empty")

    bars = [parse_bar(raw, i) for i, raw in enumerate(raw_bars)]
    return sorted(bars, key=lambda b: b.time)
