"""Synthetic bid/ask bars — FOR CODE TESTS ONLY. Never evidence of profitability."""
from __future__ import annotations

import numpy as np
import pandas as pd


def make_bars(prices_mid, start="2024-01-02 14:00", spread=0.2, freq="1min") -> pd.DataFrame:
    """Bars where o=h=l=c=mid unless a (o,h,l,c) tuple is given per bar."""
    rows = []
    for p in prices_mid:
        o, h, l, c = p if isinstance(p, (tuple, list)) else (p, p, p, p)
        rows.append((o, h, l, c))
    a = np.array(rows, float)
    idx = pd.date_range(start, periods=len(a), freq=freq, tz="UTC")
    hs = spread / 2
    return pd.DataFrame({"bid_o": a[:, 0] - hs, "bid_h": a[:, 1] - hs, "bid_l": a[:, 2] - hs, "bid_c": a[:, 3] - hs,
                         "ask_o": a[:, 0] + hs, "ask_h": a[:, 1] + hs, "ask_l": a[:, 2] + hs, "ask_c": a[:, 3] + hs,
                         "ticks": 10}, index=idx)


def random_walk_bars(days=30, seed=0, start="2024-01-01", vol_per_min=0.15, spread=0.25, price=2000.0,
                     drift=None):
    """Gold-like 23h/5d session (closed 17:00-18:00 NY daily and over the weekend).
    drift=(ny_hour_from, ny_hour_to, per_minute) injects a KNOWN edge (positive-control tests)."""
    rng = np.random.default_rng(seed)
    idx = pd.date_range(start, periods=days * 1440, freq="1min", tz="UTC")
    ny = idx.tz_convert("America/New_York")
    wd, hr = ny.weekday, ny.hour
    open_ = ~((hr == 17) | (wd == 5) | ((wd == 4) & (hr >= 17)) | ((wd == 6) & (hr < 18)))
    idx = idx[open_]
    n = len(idx)
    steps = rng.standard_t(4, size=n) * vol_per_min / np.sqrt(2)
    if drift is not None:
        h0, h1, mu = drift
        hh = idx.tz_convert("America/New_York").hour
        steps = steps + np.where((hh >= h0) & (hh < h1), mu, 0.0)
    c = price + np.cumsum(steps)
    o = np.r_[price, c[:-1]]
    wig = np.abs(rng.normal(0, vol_per_min, size=(n, 2)))
    h = np.maximum(o, c) + wig[:, 0]
    l = np.minimum(o, c) - wig[:, 1]
    sp = spread * (1 + 0.5 * rng.random(n))
    hs = sp / 2
    return pd.DataFrame({"bid_o": o - hs, "bid_h": h - hs, "bid_l": l - hs, "bid_c": c - hs,
                         "ask_o": o + hs, "ask_h": h + hs, "ask_l": l + hs, "ask_c": c + hs,
                         "ticks": rng.integers(1, 50, n)}, index=idx)
