"""Bid/Ask bar container and trading-day calendar.

Canonical bar format (1-minute unless stated): DataFrame indexed by bar OPEN time,
tz-aware UTC, columns bid_o,bid_h,bid_l,bid_c,ask_o,ask_h,ask_l,ask_c and optional
`ticks` (tick COUNT from the feed — not centralised market volume).
A bar's information is available only at its close (open + timeframe).
"""
from __future__ import annotations

import numpy as np
import pandas as pd

BAR_COLS = ["bid_o", "bid_h", "bid_l", "bid_c", "ask_o", "ask_h", "ask_l", "ask_c"]
DAY_CUTOFF_TZ = "America/New_York"
DAY_CUTOFF_HOUR = 17  # FX/metals rollover: trading day ends 17:00 New York (DST aware)


def trading_day(index: pd.DatetimeIndex) -> np.ndarray:
    """Trading day label for each bar. Bars at/after 17:00 NY belong to the next day."""
    ny = index.tz_convert(DAY_CUTOFF_TZ)
    shifted = ny + pd.Timedelta(hours=24 - DAY_CUTOFF_HOUR)
    return np.asarray(shifted.date)


def mid(df: pd.DataFrame) -> pd.DataFrame:
    out = pd.DataFrame(index=df.index)
    for f in "ohlc":
        out[f] = (df[f"bid_{f}"] + df[f"ask_{f}"]) / 2
    return out


def from_mid_with_spread(df: pd.DataFrame, spread: pd.Series | float) -> pd.DataFrame:
    """Build bid/ask bars from mid OHLC and a spread model (flag: SYNTHETIC SPREAD)."""
    out = pd.DataFrame(index=df.index)
    half = (spread if np.isscalar(spread) else spread.reindex(df.index).values) / 2
    for f in "ohlc":
        out[f"bid_{f}"] = df[f] - half
        out[f"ask_{f}"] = df[f] + half
    if "ticks" in df:
        out["ticks"] = df["ticks"]
    out.attrs["synthetic_spread"] = True
    return out


def stress_spread(df: pd.DataFrame, mult: float) -> pd.DataFrame:
    """Scale the bid/ask spread around mid by `mult` (cost stress test)."""
    if mult == 1.0:
        return df
    out = df.copy()
    for f in "ohlc":
        m = (df[f"bid_{f}"] + df[f"ask_{f}"]) / 2
        h = (df[f"ask_{f}"] - df[f"bid_{f}"]) / 2 * mult
        out[f"bid_{f}"], out[f"ask_{f}"] = m - h, m + h
    return out


def add_spread(df: pd.DataFrame, extra: float) -> pd.DataFrame:
    """Widen every quote by a constant (broker mark-up over the data source)."""
    if extra == 0:
        return df
    out = df.copy()
    for f in "ohlc":
        out[f"bid_{f}"] -= extra / 2
        out[f"ask_{f}"] += extra / 2
    return out


def validate_bars(df: pd.DataFrame) -> list[str]:
    errs = []
    missing = [c for c in BAR_COLS if c not in df]
    if missing:
        return [f"missing columns {missing}"]
    if df.index.tz is None or str(df.index.tz) != "UTC":
        errs.append("index must be tz-aware UTC")
    if not df.index.is_monotonic_increasing or df.index.has_duplicates:
        errs.append("index not strictly increasing")
    for side in ("bid", "ask"):
        o, h, l, c = (df[f"{side}_{f}"] for f in "ohlc")
        if ((h < np.maximum(o, c) - 1e-9) | (l > np.minimum(o, c) + 1e-9)).any():
            errs.append(f"{side} OHLC inconsistent")
    if (df["ask_c"] < df["bid_c"] - 1e-9).any() or (df["ask_o"] < df["bid_o"] - 1e-9).any():
        errs.append("negative spread")
    if df[BAR_COLS].isna().any().any():
        errs.append("NaN prices")
    return errs


def resample(df: pd.DataFrame, rule: str) -> pd.DataFrame:
    """Aggregate bid/ask bars (label = bar open, left-closed)."""
    agg = {}
    for side in ("bid", "ask"):
        agg.update({f"{side}_o": "first", f"{side}_h": "max", f"{side}_l": "min", f"{side}_c": "last"})
    if "ticks" in df:
        agg["ticks"] = "sum"
    out = df.resample(rule, label="left", closed="left").agg(agg)
    return out.dropna(subset=["bid_c"])
