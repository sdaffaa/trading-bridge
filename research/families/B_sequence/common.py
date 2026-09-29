"""Shared helpers for family B (sequence / state / calendar rules)."""
import sys, os, time
sys.path.insert(0, "/home/user/trading-bridge/research")
import numpy as np, pandas as pd
from numba import njit
from harness import (load_m1, bars, htf_to_m1, atr, run_consecutive, trade_once, stats, fmt,
                     passes, SPREAD, PERIODS, _run)

M1 = load_m1()
N = len(M1)
O = M1.open.values; H = M1.high.values; L = M1.low.values; C = M1.close.values
IDX = M1.index
IS_END = int(np.searchsorted(IDX.values, np.datetime64("2020-01-01")))
VAL_END = int(np.searchsorted(IDX.values, np.datetime64("2023-01-01")))


def stop_configs():
    """name -> dist array aligned to M1 (causal)."""
    out = {}
    for tf, lab in (("15min", "M15"), ("1h", "H1"), ("1D", "D1")):
        a = htf_to_m1(atr(bars(tf)), tf)
        for k in (0.5, 1, 2, 3):
            out[f"{k}xATR{lab}"] = k * a
    for u in (1, 2, 3, 5, 10):
        out[f"fix{u}"] = np.full(N, float(u))
    return out


@njit(cache=True)
def _labels(o, h, l, idx, dist, spread, maxscan):
    """long/short outcome (+1/-1, 0 unknown) for trades opened at bars idx."""
    m = len(idx); lo = np.zeros(m, np.int8); so = np.zeros(m, np.int8)
    n = len(o)
    for k in range(m):
        i = idx[k]; d = dist[i]
        if not (d > 0):
            continue
        e = o[i] + spread
        for j in range(i, min(n, i + maxscan)):
            if l[j] <= e - d:
                lo[k] = -1; break
            if h[j] >= e + d:
                lo[k] = 1; break
        e = o[i]
        for j in range(i, min(n, i + maxscan)):
            if h[j] + spread >= e + d:
                so[k] = -1; break
            if l[j] + spread <= e - d:
                so[k] = 1; break
    return lo, so


def labels(dist, step=5, end=None, maxscan=20000):
    end = IS_END if end is None else end
    idx = np.arange(0, end, step, dtype=np.int64)
    lo, so = _labels(O, H, L, idx, dist, SPREAD, maxscan)
    return idx, lo, so


def learn_table(keys_at_idx, lo, so, nkeys, minc=300, margin=0.0):
    """Per key: +1 if long wins more often, -1 if short, 0 if too few samples / no margin.
    keys < 0 are ignored. Returns table (int8), long_wr, short_wr, counts."""
    ok = (keys_at_idx >= 0) & (lo != 0) & (so != 0)
    k = keys_at_idx[ok]
    cnt = np.bincount(k, minlength=nkeys).astype(float)
    lw = np.bincount(k, weights=(lo[ok] > 0), minlength=nkeys)
    sw = np.bincount(k, weights=(so[ok] > 0), minlength=nkeys)
    with np.errstate(invalid="ignore", divide="ignore"):
        lwr = lw / cnt; swr = sw / cnt
    tab = np.where(lwr >= swr, 1, -1).astype(np.int8)
    tab[(cnt < minc) | (np.abs(lwr - swr) < margin)] = 0
    return tab, lwr, swr, cnt


def default_dir(lo, so):
    return 1 if (lo > 0).mean() >= (so > 0).mean() else -1


def apply_table(keys, tab, default):
    d = np.full(N, float(default))
    ok = keys >= 0
    t = tab[keys[ok]].astype(float)
    t[t == 0] = default
    d[ok] = t
    return d


@njit(cache=True)
def _wr_seg(ent, res, a, b):
    n = 0; w = 0
    for k in range(len(ent)):
        if ent[k] >= a and ent[k] < b:
            n += 1
            if res[k] > 0:
                w += 1
    return n, w


def quick(dirs, dist):
    """Fast IS/VAL/HOLDOUT (n, wr%) using harness _run (identical rules)."""
    ent, ex, res, side = _run(O, H, L, np.asarray(dirs, np.float64), np.asarray(dist, np.float64), SPREAD, 0)
    out = {}
    for p, (a, b) in (("IS", (0, IS_END)), ("VAL", (IS_END, VAL_END)), ("HOLDOUT", (VAL_END, N))):
        n, w = _wr_seg(ent, res, a, b)
        out[p] = (n, 100.0 * w / n if n else 0.0)
    return out


def to_df(ent, ex, res, side):
    return pd.DataFrame({"t": IDX[ent], "exit_t": IDX[ex], "side": side, "r": res})


class Log:
    def __init__(self, path):
        self.path = path; self.rows = []
    def add(self, family, name, stop, q):
        self.rows.append(dict(family=family, name=name, stop=stop,
                              is_n=q["IS"][0], is_wr=round(q["IS"][1], 2),
                              val_n=q["VAL"][0], val_wr=round(q["VAL"][1], 2)))
    def save(self):
        pd.DataFrame(self.rows).to_csv(self.path, index=False)
