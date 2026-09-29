"""Fast engine for family A grid search.

For a given per-bar SL=TP distance array, precompute for EVERY M1 bar the outcome and exit
bar of a long and of a short trade opened at that bar's open (same rules as
harness.trade_once, found with segment-tree first-crossing searches). Evaluating any
dirs array is then a pointer chase (microseconds). Finalists are always re-run with the
real harness.run_consecutive + stats().
"""
import sys, os
import numpy as np
import pandas as pd
from numba import njit

sys.path.insert(0, "/home/user/trading-bridge/research")
import harness as H

SPREAD = H.SPREAD


@njit(cache=True)
def build_tree(a, P, ismax):
    t = np.empty(2 * P, np.float64)
    fill = -1e18 if ismax else 1e18
    for k in range(P):
        t[P + k] = a[k] if k < len(a) else fill
    for p in range(P - 1, 0, -1):
        if ismax:
            t[p] = max(t[2 * p], t[2 * p + 1])
        else:
            t[p] = min(t[2 * p], t[2 * p + 1])
    return t


@njit(cache=True)
def first_ge(t, P, i, x):
    pos = i + P
    while True:
        if t[pos] >= x:
            break
        while pos & 1:
            pos >>= 1
        if pos == 0:
            return -1
        pos += 1
    while pos < P:
        pos = 2 * pos
        if t[pos] < x:
            pos += 1
    return pos - P


@njit(cache=True)
def first_le(t, P, i, x):
    pos = i + P
    while True:
        if t[pos] <= x:
            break
        while pos & 1:
            pos >>= 1
        if pos == 0:
            return -1
        pos += 1
    while pos < P:
        pos = 2 * pos
        if t[pos] > x:
            pos += 1
    return pos - P


@njit(cache=True)
def outcome_tables(o, th, tl, P, dist, spread, i0, i1):
    """For bars i0..i1-1: long/short exit bar and win flag. exit=-1 -> data ended."""
    m = i1 - i0
    lx = np.full(m, -1, np.int64); lw = np.zeros(m, np.int8)
    sx = np.full(m, -1, np.int64); sw = np.zeros(m, np.int8)
    for k in range(m):
        i = i0 + k
        d = dist[i]
        if not (d > 0):
            continue
        # long
        e = o[i] + spread
        jl = first_le(tl, P, i, e - d)
        jw = first_ge(th, P, i, e + d)
        if jl >= 0 and (jw < 0 or jl <= jw):
            lx[k] = jl; lw[k] = 0
        elif jw >= 0:
            lx[k] = jw; lw[k] = 1
        # short
        e = o[i]
        jl = first_ge(th, P, i, e + d - spread)
        jw = first_le(tl, P, i, e - d - spread)
        if jl >= 0 and (jw < 0 or jl <= jw):
            sx[k] = jl; sw[k] = 0
        elif jw >= 0:
            sx[k] = jw; sw[k] = 1
    return lx, lw, sx, sw


@njit(cache=True)
def walk(sig, mp, inv, lx, lw, sx, sw, i0, i1):
    """sig: int8 at native TF (0 = undefined); mp: M1 -> tf index (-1 none).
    Trades entered in [i0, i1). Returns (n, wins)."""
    i = i0; n = 0; w = 0
    while i < i1:
        k = mp[i]
        s = sig[k] if k >= 0 else 0
        if s == 0:
            i += 1; continue
        if inv:
            s = -s
        r = i - i0
        if s > 0:
            j = lx[r]; win = lw[r]
        else:
            j = sx[r]; win = sw[r]
        if j < 0:
            i += 1  # dist undefined here (warm-up) or data ended
            continue
        n += 1; w += win
        i = j + 1
    return n, w


@njit(cache=True)
def walk_m1(dirs, lx, lw, sx, sw, i0, i1):
    i = i0; n = 0; w = 0
    while i < i1:
        s = dirs[i]
        if s == 0:
            i += 1; continue
        r = i - i0
        if s > 0:
            j = lx[r]; win = lw[r]
        else:
            j = sx[r]; win = sw[r]
        if j < 0:
            i += 1; continue
        n += 1; w += win
        i = j + 1
    return n, w


class Engine:
    def __init__(self):
        m1 = H.load_m1()
        self.m1 = m1
        self.o = m1.open.values.astype(np.float64)
        h = m1.high.values.astype(np.float64); l = m1.low.values.astype(np.float64)
        n = len(m1); P = 1
        while P < n:
            P *= 2
        self.P = P
        self.th = build_tree(h, P, True)
        self.tl = build_tree(l, P, False)
        self.idx = m1.index

    def rng(self, period):
        a, b = H.PERIODS[period]
        return int(self.idx.searchsorted(pd.Timestamp(a))), int(self.idx.searchsorted(pd.Timestamp(b)))

    def tables(self, dist, i0, i1):
        # extend end so trades entered before i1 can exit later
        return outcome_tables(self.o, self.th, self.tl, self.P, dist, SPREAD, i0, i1)


def tf_map(tf, bars_index):
    """M1 row -> index of last COMPLETED tf bar (same semantics as harness.htf_to_m1)."""
    m1 = H.load_m1()
    close_t = bars_index + pd.Timedelta(tf)
    return (np.searchsorted(close_t.values, m1.index.values, side="right") - 1).astype(np.int64)


@njit(cache=True)
def walk_rel(dirs, lx, lw, sx, sw, i0, i1):
    """dirs indexed relative to i0 (dirs[i-i0])."""
    i = i0; n = 0; w = 0
    while i < i1:
        r = i - i0
        s = dirs[r]
        if s == 0:
            i += 1; continue
        if s > 0:
            j = lx[r]; win = lw[r]
        else:
            j = sx[r]; win = sw[r]
        if j < 0:
            i += 1; continue
        n += 1; w += win
        i = j + 1
    return n, w
