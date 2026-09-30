"""Shared helpers for family G (quant). Uses harness3 (pnl, stats, vol_target) on 1h bars.
HOLDOUT discipline: registry stores daily returns only up to 2024-12-31; HOLDOUT is evaluated
only in final.py for the final top 10.
"""
import os, sys, json
import numpy as np, pandas as pd
from numba import njit
sys.path.insert(0, "/home/user/trading-bridge/research")
import harness3 as H3

HERE = os.path.dirname(os.path.abspath(__file__))
TF = "1h"
B = H3.bars(TF)
C = B.close
LR = np.log(C).diff().fillna(0.0)
VAL_END = pd.Timestamp("2025-01-01")

# --- clock: HistData (<=2025) is NY-local+5h; Tickstory (2026) is true UTC. Build NY-local time.
_idx = B.index
_ny = pd.Series(_idx - pd.Timedelta(hours=5), index=_idx)
_m26 = _idx >= pd.Timestamp("2026-01-01")
_ny[_m26] = _idx[_m26].tz_localize("UTC").tz_convert("America/New_York").tz_localize(None)
NY = pd.DatetimeIndex(_ny.values)          # New-York local wall clock of bar open
NY_HOUR = pd.Series(NY.hour, index=_idx)
# trading day (NY 17:00 roll): bars from 17:00 NY belong to next day
TDAY = pd.Series((NY + pd.Timedelta(hours=7)).normalize(), index=_idx)

HPD = 23  # ~1h bars per trading day


def ann_vol_lev(target=0.10, lookback=20 * 24):
    rv = C.pct_change().rolling(lookback).std() * np.sqrt(260 * 24)
    return (target / rv).clip(upper=3.0)


def vt(sig, target=0.10):
    return H3.vol_target(sig, B, target)


@njit(cache=True)
def _buffer(tgt, buf, allow):
    n = len(tgt); out = np.zeros(n); cur = 0.0
    for i in range(n):
        t = tgt[i]
        if np.isnan(t):
            t = 0.0
        if allow[i] and (abs(t - cur) > buf[i] or (t == 0.0 and cur != 0.0)):
            cur = t
        out[i] = cur
    return out


def buffer(pos, frac=0.10, target=0.10, hours=None):
    """Carver-style buffer: trade only when |target-current| > frac * (vol-target leverage), or target is exactly 0 (go flat).
    hours: optional iterable of NY hours (bar open) at which rebalancing is allowed."""
    lev = ann_vol_lev(target).reindex(pos.index).fillna(0).values
    allow = np.ones(len(pos), dtype=np.bool_) if hours is None else NY_HOUR.reindex(pos.index).isin(list(hours)).values
    return pd.Series(_buffer(pos.values.astype(np.float64), frac * lev, allow), index=pos.index)


def daily_all(r):
    """daily returns (NY trading day), incl. zero days, on B&H calendar."""
    d = r.groupby(TDAY.reindex(r.index - pd.Timedelta(TF)).values).sum() if False else r.groupby(r.index.date).sum()
    d.index = pd.to_datetime(d.index)
    return d.reindex(CAL).fillna(0.0)


def _cal():
    r = H3.pnl(pd.Series(1.0, index=B.index), B)
    d = r.groupby(r.index.date).sum(); d.index = pd.to_datetime(d.index)
    return d[d != 0].index
CAL = _cal()

PER = {k: (pd.Timestamp(a), pd.Timestamp(b)) for k, (a, b) in H3.PERIODS.items()}


def sr(x):
    return float(x.mean() / x.std() * np.sqrt(260)) if x.std() > 0 else 0.0


def pstats(d, p):
    a, b = PER[p]; x = d[(d.index >= a) & (d.index < b)]
    eq = x.cumsum()
    return dict(sr=round(sr(x), 3), ret=round(x.mean() * 260 * 100, 2), dd=round((eq - eq.cummax()).min() * 100, 2),
                gd=round((x > 0).mean() * 100, 1), expo=round((x != 0).mean() * 100, 1))


REG = []           # list of dict rows
DAILY = {}         # name -> daily returns up to VAL_END


def evaluate(name, fam, pos, params=None, keep=True):
    pos = pos.reindex(B.index).fillna(0.0)
    pos = pos.where(pos.index < VAL_END, 0.0)          # HOLDOUT masked during research
    r = H3.pnl(pos, B)
    d = daily_all(r)
    d = d[d.index < VAL_END]
    row = dict(name=name, fam=fam, params=json.dumps(params or {}))
    for p in ("IS", "VAL"):
        for k, v in pstats(d, p).items():
            row[f"{p}_{k}"] = v
    row["turn"] = round(float(pos.diff().abs().sum() / (len(pos) / (260 * 24))), 1)   # notional traded / yr
    if keep:
        REG.append(row); DAILY[name] = d
    return row


def save(tag):
    df = pd.DataFrame(REG)
    df.to_csv(f"{HERE}/reg_{tag}.csv", index=False)
    pd.DataFrame(DAILY).to_parquet(f"{HERE}/daily_{tag}.parquet")
    return df


def show(df, by="IS_sr", n=15, cols=None):
    cols = cols or ["name", "IS_sr", "IS_ret", "IS_dd", "IS_gd", "VAL_sr", "VAL_ret", "VAL_dd", "VAL_gd", "turn"]
    print(df.sort_values(by, ascending=False)[cols].head(n).to_string(index=False))


def baselines():
    out = {}
    for nm, pos in (("B&H 1x", pd.Series(1.0, index=B.index)), ("B&H vt10", vt(pd.Series(1.0, index=B.index)))):
        out[nm] = evaluate(nm, "base", pos, keep=False)
    return out
