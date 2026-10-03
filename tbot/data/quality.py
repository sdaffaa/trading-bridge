"""Data-quality report for 1m bid/ask bars. Produces a JSON-serialisable dict.

Expected gold CFD/spot session (assumption to verify against the broker):
Sunday 18:00 NY -> Friday 17:00 NY, with a daily break 17:00-18:00 NY.
"""
from __future__ import annotations

import hashlib
from pathlib import Path

import numpy as np
import pandas as pd

from tbot.data.bars import BAR_COLS, trading_day, validate_bars


def sha256_file(path: str | Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_frame(df: pd.DataFrame) -> str:
    return hashlib.sha256(pd.util.hash_pandas_object(df, index=True).values.tobytes()).hexdigest()


def expected_open(index: pd.DatetimeIndex) -> np.ndarray:
    ny = index.tz_convert("America/New_York")
    wd, hr = ny.weekday, ny.hour
    closed = (hr == 17) | (wd == 5) | ((wd == 4) & (hr >= 17)) | ((wd == 6) & (hr < 18))
    return ~np.asarray(closed)


def quality_report(df: pd.DataFrame, spike_k: float = 15.0, stale_run: int = 30) -> dict:
    rep: dict = {"rows": int(len(df))}
    if df.empty:
        rep["verdict"] = "EMPTY"
        return rep
    rep["start"], rep["end"] = str(df.index[0]), str(df.index[-1])
    rep["sha256"] = sha256_frame(df[BAR_COLS])
    rep["structural_errors"] = validate_bars(df)
    rep["duplicates"] = int(df.index.duplicated().sum())
    # coverage vs expected session minutes
    full = pd.date_range(df.index[0].floor("D"), df.index[-1].ceil("D"), freq="1min", tz="UTC")
    exp = full[expected_open(full)]
    have = df.index.intersection(exp)
    rep["expected_minutes"] = int(len(exp))
    rep["coverage"] = float(len(have) / len(exp)) if len(exp) else np.nan
    rep["bars_outside_expected_session"] = int((~expected_open(df.index)).sum())
    # DST sanity: the daily break must sit at 17:00 NY in both summer and winter
    ny = df.index.tz_convert("America/New_York")
    summer = (ny.month >= 6) & (ny.month <= 8)
    winter = (ny.month == 12) | (ny.month <= 2)
    rep["share_bars_in_17h_NY_summer"] = float((ny.hour[summer] == 17).mean()) if summer.any() else None
    rep["share_bars_in_17h_NY_winter"] = float((ny.hour[winter] == 17).mean()) if winter.any() else None
    # gaps inside expected session
    dt = pd.Series(df.index[1:] - df.index[:-1], index=df.index[1:])
    big = dt[dt > pd.Timedelta(minutes=5)]
    inside = big[[expected_open(pd.DatetimeIndex([t - d / 2]))[0] for t, d in big.items()]] if len(big) else big
    rep["gaps_gt5m_in_session"] = int(len(inside))
    rep["largest_gaps"] = [(str(t), str(d)) for t, d in inside.sort_values(ascending=False).head(10).items()]
    # per-day bar counts (holidays / partial days)
    days = pd.Series(trading_day(df.index)).value_counts()
    rep["days"] = int(len(days))
    rep["short_days_lt_1000_bars"] = int((days < 1000).sum())
    # spreads
    sp = (df["ask_c"] - df["bid_c"])
    rep["spread"] = {q: float(sp.quantile(q)) for q in (0.01, 0.5, 0.9, 0.99)}
    rep["spread_nonpositive"] = int((sp <= 0).sum())
    hr = df.index.hour
    rep["median_spread_by_utc_hour"] = {int(h): float(v) for h, v in sp.groupby(hr).median().items()}
    rep["median_spread_by_year"] = {int(y): float(v) for y, v in sp.groupby(df.index.year).median().items()}
    # spikes: 1m mid return vs rolling robust scale
    m = (df["bid_c"] + df["ask_c"]) / 2
    r = np.log(m).diff()
    mad = r.abs().rolling(1440, min_periods=200).median()
    spikes = r.abs() > spike_k * mad / 0.6745
    rep["spikes"] = int(spikes.sum())
    rep["spike_examples"] = [str(t) for t in r[spikes].abs().sort_values(ascending=False).head(10).index]
    # stale quotes: long runs of identical mid
    same = (m.diff() == 0).astype(int)
    runs = same.groupby((same == 0).cumsum()).cumsum()
    rep["stale_runs_ge_%d" % stale_run] = int((runs == stale_run).sum())
    if "ticks" in df:
        rep["ticks_note"] = "tick COUNT from the feed; not centralised volume"
        rep["zero_tick_bars"] = int((df["ticks"] == 0).sum())
    bad = bool(rep["structural_errors"]) or rep["duplicates"] > 0 or rep["spread_nonpositive"] > 0
    rep["verdict"] = "FAIL" if bad else ("WARN" if rep["coverage"] < 0.97 or rep["spikes"] > 0 else "PASS")
    return rep
