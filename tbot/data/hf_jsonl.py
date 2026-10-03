"""Loader for the Hugging Face mirror `ZombitX64/xauusd-gold-price-historical-data-2004-2025`
(re-upload of a Kaggle dataset). Single price series (likely BID of an unknown MT
broker), timestamps in UNKNOWN broker server time, `Volume` = tick count.
Status: SECONDARY / cross-check only. Any bars built from it carry a SYNTHETIC spread.
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from tbot.data.bars import from_mid_with_spread


def load_jsonl(path: str | Path, server_tz_offset_hours: float | str) -> pd.DataFrame:
    """server_tz_offset_hours: fixed offset (e.g. 2) or 'EET_NY' meaning the common MT
    convention GMT+2 winter / GMT+3 summer aligned to New York DST (assumption to test)."""
    rows = [json.loads(l) for l in Path(path).read_text().splitlines() if l.strip()]
    df = pd.DataFrame(rows)
    t = pd.to_datetime(df["Date"], format="%Y.%m.%d %H:%M")
    if server_tz_offset_hours == "EET_NY":
        # server time = NY time + 7h  (17:00 NY == 00:00 server)
        loc = (t - pd.Timedelta(hours=7)).dt.tz_localize("America/New_York", ambiguous="NaT",
                                                          nonexistent="NaT")
        idx = loc.dt.tz_convert("UTC")
    else:
        idx = (t - pd.Timedelta(hours=float(server_tz_offset_hours))).dt.tz_localize("UTC")
    out = pd.DataFrame({"o": df["Open"].values, "h": df["High"].values, "l": df["Low"].values,
                        "c": df["Close"].values, "ticks": df["Volume"].values}, index=pd.DatetimeIndex(idx))
    out = out[out.index.notna()]
    return out[~out.index.duplicated(keep="first")].sort_index()


def to_bidask(df: pd.DataFrame, spread: float) -> pd.DataFrame:
    """Treat the series as BID and add a constant synthetic spread (assumption, flagged)."""
    mid = df.copy()
    for f in "ohlc":
        mid[f] = df[f] + spread / 2
    return from_mid_with_spread(mid, spread)
