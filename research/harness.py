"""Shared, strict evaluation harness for the always-in-market 1:1 gold study.

Rules enforced here (identical for every strategy family):
  * Data: XAUUSD M1 BID bars, 2014-01 .. 2026-07 (UTC). Buy fills at ask (bid + SPREAD),
    sell fills at bid; long exits on bid, short exits on ask (bid + SPREAD).
  * One position at a time, SL distance == TP distance (1:1), set at entry.
  * CONSECUTIVE: the next trade opens at the open of the very next M1 bar after the
    previous trade's exit bar. No waiting, no skipping: the strategy MUST give a
    direction (+1/-1) at every bar where a trade can start.
  * If SL and TP are both reachable inside one M1 bar -> LOSS (conservative).
  * Samples: SELECT on IS = 2020-07..2023-06, VALIDATE on VAL = 2023-07..2024-12,
    and only finalists touch HOLDOUT = 2025-01..2026-07 (last 6 years only). A strategy counts as a success
    only if it reaches >= 60% win rate on IS, VAL and HOLDOUT with >= 300 trades each.

Signals must be causal: the value at M1 bar i may use only information from bars < i
(e.g. a completed higher-timeframe bar). Use `htf_to_m1` to align higher-TF values.
"""
import os
import numpy as np
import pandas as pd
from numba import njit

SPREAD = 0.30
CACHE = "/tmp/claude-0/-home-user-trading-bridge/b109c4cd-e10b-5fab-96f6-d6f544632108/scratchpad/moredata/xau_m1_2014_2026.parquet"
# Focus: last 6 years only (user request). Earlier data may be used for indicator warm-up only.
PERIODS = {"IS": ("2020-07-01", "2023-07-01"), "VAL": ("2023-07-01", "2025-01-01"),
           "HOLDOUT": ("2025-01-01", "2026-08-01")}

_M1 = None


def load_m1():
    """M1 BID bars, UTC index, columns open/high/low/close."""
    global _M1
    if _M1 is None:
        if not os.path.exists(CACHE):
            import sys
            sys.path.insert(0, os.path.dirname(__file__))
            from load_multi import load_multi
            load_multi()
        _M1 = pd.read_parquet(CACHE)
    return _M1


def bars(tf):
    """Resampled OHLC bars (label = bar open time)."""
    m1 = load_m1()
    return m1.resample(tf).agg({"open": "first", "high": "max", "low": "min", "close": "last"}).dropna()


def htf_to_m1(series, tf):
    """Align a higher-TF series (indexed by bar open time) to M1 so that each M1 bar
    sees only the value of the last COMPLETED higher-TF bar."""
    m1 = load_m1()
    s = series.copy()
    s.index = s.index + pd.Timedelta(tf)          # value becomes known at bar close
    return s.reindex(m1.index, method="ffill").values


def atr(b, n=14):
    tr = pd.concat([b.high - b.low, (b.high - b.close.shift()).abs(),
                    (b.low - b.close.shift()).abs()], axis=1).max(axis=1)
    return tr.rolling(n).mean()


@njit(cache=True)
def trade_once(o, h, l, i, d, dist, spread):
    """Simulate one 1:1 trade opened at the open of bar i. Returns (outcome, exit_bar):
    outcome +1 win, -1 loss, 0 = data ended."""
    n = len(o)
    if d > 0:
        e = o[i] + spread
        for j in range(i, n):
            if l[j] <= e - dist:
                return -1, j
            if h[j] >= e + dist:
                return 1, j
    else:
        e = o[i]
        for j in range(i, n):
            if h[j] + spread >= e + dist:
                return -1, j
            if l[j] + spread <= e - dist:
                return 1, j
    return 0, n


@njit(cache=True)
def _run(o, h, l, dirs, dists, spread, start):
    n = len(o)
    ent = np.empty(n, np.int64); ex = np.empty(n, np.int64)
    res = np.empty(n, np.int8); side = np.empty(n, np.int8)
    k = 0
    i = start
    while i < n:
        d = dirs[i]; dist = dists[i]
        if not (dist > 0) or d == 0 or np.isnan(d):
            i += 1          # only allowed during indicator warm-up / data gaps
            continue
        out, j = trade_once(o, h, l, i, d, dist, spread)
        if out == 0:
            break
        ent[k] = i; ex[k] = j; res[k] = out; side[k] = 1 if d > 0 else -1
        k += 1
        i = j + 1           # consecutive: next bar after exit
    return ent[:k], ex[:k], res[:k], side[:k]


def run_consecutive(dirs, dists, spread=SPREAD):
    """dirs, dists: float arrays aligned with load_m1() rows. Returns a trades DataFrame."""
    m1 = load_m1()
    dirs = np.asarray(dirs, np.float64); dists = np.asarray(dists, np.float64)
    ent, ex, res, side = _run(m1.open.values, m1.high.values, m1.low.values, dirs, dists, spread, 0)
    return pd.DataFrame({"t": m1.index[ent], "exit_t": m1.index[ex], "side": side, "r": res})


def stats(tr, periods=("IS", "VAL", "HOLDOUT")):
    """Win-rate stats per period, plus share of days >= 60% and worst day."""
    out = {}
    for p in periods:
        a, b = PERIODS[p]
        x = tr[(tr.t >= a) & (tr.t < b)]
        if len(x) == 0:
            out[p] = dict(n=0); continue
        w = x.r > 0
        daily = w.groupby(x.t.dt.date).mean()
        out[p] = dict(n=len(x), wr=round(w.mean() * 100, 2), netR=int(x.r.sum()),
                      per_day=round(len(x) / max(daily.size, 1), 1),
                      days_ge60=round((daily >= .6).mean() * 100, 1),
                      worst_year=round(w.groupby(x.t.dt.year).mean().min() * 100, 1))
    return out


def fmt(name, st):
    s = f"{name:<45}"
    for p, v in st.items():
        s += f" | {p}: n={v.get('n',0)} wr={v.get('wr','-')}% net={v.get('netR','-')}R d60={v.get('days_ge60','-')}%"
    return s


def passes(st):
    return all(st[p].get("n", 0) >= 300 and st[p].get("wr", 0) >= 60 for p in ("IS", "VAL", "HOLDOUT"))


if __name__ == "__main__":
    m1 = load_m1()
    n = len(m1)
    rng = np.random.default_rng(0)
    a = atr(bars("1h")); dist = 2 * htf_to_m1(a, "1h")
    for name, d in (("always_long", np.ones(n)), ("always_short", -np.ones(n)),
                    ("random", rng.choice([-1.0, 1.0], n))):
        print(fmt(name, stats(run_consecutive(d, dist))))
