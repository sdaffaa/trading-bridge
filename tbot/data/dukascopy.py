"""Dukascopy historical tick data (free, bid+ask per tick).

URL: https://datafeed.dukascopy.com/datafeed/{SYM}/{YYYY}/{MM-1:02d}/{DD:02d}/{HH:02d}h_ticks.bi5
File: LZMA-compressed records of 20 bytes, big-endian: uint32 ms-offset-from-hour,
uint32 ask, uint32 bid, float32 ask_volume, float32 bid_volume. Prices are integers
divided by POINT[symbol] (XAUUSD: 1000 — to be verified against an independent
price level before use, see DATA_MANIFEST.json `checks`). Hour folders are UTC.
Dukascopy is NOT the user's execution broker: its spreads/quotes are a proxy and
must be compared with the broker's live spreads during paper trading.
Requires network access to datafeed.dukascopy.com (currently blocked, see STATUS.md).
"""
from __future__ import annotations

import lzma
import struct
import time
from pathlib import Path

import numpy as np
import pandas as pd

POINT = {"XAUUSD": 1000.0, "XAGUSD": 1000.0, "EURUSD": 100000.0}
URL = "https://datafeed.dukascopy.com/datafeed/{sym}/{y:04d}/{m:02d}/{d:02d}/{h:02d}h_ticks.bi5"
REC = struct.Struct(">3I2f")


def decode_bi5(raw: bytes, hour_start: pd.Timestamp, point: float) -> pd.DataFrame:
    if not raw:
        return pd.DataFrame(columns=["ask", "bid", "ask_vol", "bid_vol"])
    data = lzma.decompress(raw)
    n = len(data) // REC.size
    arr = np.frombuffer(data[: n * REC.size], dtype=np.dtype([("ms", ">u4"), ("ask", ">u4"), ("bid", ">u4"),
                                                              ("av", ">f4"), ("bv", ">f4")]))
    idx = hour_start + pd.to_timedelta(arr["ms"].astype(np.int64), unit="ms")
    return pd.DataFrame({"ask": arr["ask"] / point, "bid": arr["bid"] / point,
                         "ask_vol": arr["av"].astype(float), "bid_vol": arr["bv"].astype(float)}, index=idx)


def encode_bi5(ticks: pd.DataFrame, hour_start: pd.Timestamp, point: float) -> bytes:
    """Inverse of decode_bi5 — used only by unit tests."""
    buf = b"".join(REC.pack(int((t - hour_start) / pd.Timedelta(milliseconds=1)), int(round(r.ask * point)),
                            int(round(r.bid * point)), r.ask_vol, r.bid_vol) for t, r in ticks.iterrows())
    return lzma.compress(buf, format=lzma.FORMAT_ALONE)


def fetch_hour(sym: str, hour: pd.Timestamp, cache_dir: Path, session=None, retries: int = 4) -> bytes:
    import requests
    cache = cache_dir / sym / f"{hour:%Y/%m/%d/%H}h_ticks.bi5"
    if cache.exists():
        return cache.read_bytes()
    url = URL.format(sym=sym, y=hour.year, m=hour.month - 1, d=hour.day, h=hour.hour)
    s = session or requests.Session()
    for k in range(retries):
        try:
            r = s.get(url, timeout=30)
            if r.status_code == 404:
                raw = b""
            else:
                r.raise_for_status()
                raw = r.content
            cache.parent.mkdir(parents=True, exist_ok=True)
            cache.write_bytes(raw)
            return raw
        except Exception:
            if k == retries - 1:
                raise
            time.sleep(2 ** (k + 1))
    return b""


def ticks_to_bars(ticks: pd.DataFrame, rule: str = "1min") -> pd.DataFrame:
    """Bid/ask OHLC from ticks. Includes tick count and max spread within the bar."""
    if ticks.empty:
        return pd.DataFrame()
    g = ticks.resample(rule, label="left", closed="left")
    bid, ask = g["bid"].ohlc(), g["ask"].ohlc()
    out = pd.concat([bid.add_prefix("bid_").rename(columns=lambda c: c.replace("open", "o").replace("high", "h")
                                                   .replace("low", "l").replace("close", "c")),
                     ask.add_prefix("ask_").rename(columns=lambda c: c.replace("open", "o").replace("high", "h")
                                                   .replace("low", "l").replace("close", "c"))], axis=1)
    out["ticks"] = g["bid"].count()
    out["max_spread"] = (ticks["ask"] - ticks["bid"]).resample(rule, label="left", closed="left").max()
    return out.dropna(subset=["bid_c"])


def download_range(sym: str, start: str, end: str, cache_dir: Path, out_dir: Path) -> list[Path]:
    """Download [start, end) by month, write one parquet of 1m bid/ask bars per month."""
    import requests
    s = requests.Session()
    point = POINT[sym]
    outs = []
    for m0 in pd.date_range(pd.Timestamp(start).replace(day=1), end, freq="MS", tz="UTC"):
        m1 = m0 + pd.offsets.MonthBegin(1)
        path = out_dir / sym / f"{m0:%Y-%m}.parquet"
        if path.exists():
            outs.append(path)
            continue
        frames = []
        for h in pd.date_range(m0, m1, freq="h", inclusive="left"):
            if h.weekday() == 5:   # Saturday: market closed
                continue
            raw = fetch_hour(sym, h, cache_dir, s)
            t = decode_bi5(raw, h, point)
            if len(t):
                frames.append(ticks_to_bars(t))
        if frames:
            path.parent.mkdir(parents=True, exist_ok=True)
            pd.concat(frames).to_parquet(path)
            outs.append(path)
    return outs
