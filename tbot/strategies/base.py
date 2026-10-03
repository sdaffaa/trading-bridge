"""Strategy interface + causal feature helpers.

Contract: `signals(bars)` returns a DataFrame aligned to bars.index with columns
  entry  int   +1 long / -1 short / 0 none   (decision at this bar's CLOSE)
  stop   float protective stop price (required when entry != 0)
  target float take-profit price or NaN
  exit   int   1 = close open positions at next bar open
  tag    str
Row i may use only bars[:i+1]. Enforced by tests/test_leakage.py (truncation test).
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from tbot.data.bars import mid, trading_day


class Strategy:
    name = "base"
    param_grid: dict = {}
    ordinal: tuple = ()      # params whose grid order is meaningful (used for neighbourhood robustness)

    def __init__(self, **params):
        self.params = params

    def signals(self, bars: pd.DataFrame) -> pd.DataFrame:
        raise NotImplementedError

    @classmethod
    def grid(cls) -> list[dict]:
        keys = list(cls.param_grid)
        out = [{}]
        for k in keys:
            out = [dict(o, **{k: v}) for o in out for v in cls.param_grid[k]]
        return out

    @classmethod
    def neighbors(cls, params: dict) -> list[dict]:
        """Parameter perturbations for robustness: adjacent grid values of ORDINAL params only.
        Categorical params (e.g. stop_mode, trade side) are not perturbed (D-010)."""
        out = []
        for k in cls.ordinal:
            vals = cls.param_grid[k]
            i = vals.index(params[k])
            for j in (i - 1, i + 1):
                if 0 <= j < len(vals):
                    out.append(dict(params, **{k: vals[j]}))
        return out

    def label(self) -> str:
        return self.name + "(" + ",".join(f"{k}={v}" for k, v in sorted(self.params.items())) + ")"


def empty_signals(index) -> pd.DataFrame:
    n = len(index)
    return pd.DataFrame({"entry": np.zeros(n, int), "stop": np.full(n, np.nan), "target": np.full(n, np.nan),
                         "exit": np.zeros(n, int), "tag": np.full(n, "", dtype=object)}, index=index)


def local_clock(index: pd.DatetimeIndex, tz: str) -> tuple[np.ndarray, np.ndarray]:
    """(minutes since local midnight of bar OPEN, minutes of bar CLOSE) — DST aware."""
    loc = index.tz_convert(tz)
    m = (loc.hour * 60 + loc.minute).to_numpy()
    return m, m + 1  # 1-minute bars


def daily_context(bars: pd.DataFrame, lookback: int = 20) -> pd.DataFrame:
    """Per-bar features derived ONLY from completed previous trading days."""
    mp = mid(bars)
    day = pd.Series(trading_day(bars.index), index=bars.index)
    g = mp.groupby(day.values)
    d = pd.DataFrame({"o": g["o"].first(), "h": g["h"].max(), "l": g["l"].min(), "c": g["c"].last()})
    d["ret"] = np.log(d["c"] / d["c"].shift(1))
    d["vol"] = d["ret"].rolling(lookback, min_periods=lookback).std().shift(1)
    d["atr"] = (d["h"] - d["l"]).rolling(14, min_periods=14).mean().shift(1)
    d["prev_close"] = d["c"].shift(1)
    return d[["vol", "atr", "prev_close"]].reindex(day.values).set_index(bars.index)


def first_true_per_day(mask: np.ndarray, day: np.ndarray) -> np.ndarray:
    """Keep only the first True of each trading day."""
    out = np.zeros_like(mask, dtype=bool)
    s = pd.Series(mask)
    cs = s.groupby(day).cumsum().to_numpy()
    out[(cs == 1) & mask] = True
    return out
