"""Fast exact re-implementation of harness2._run for grid scoring.
For an exit rule (SL dist, TP dist, trail dist per bar) precompute, for every M1 bar i in [i0,i1),
the exit bar and R of a long and of a short opened at bar i's open (identical rules to harness2).
Fixed SL/TP uses segment-tree first-crossing search; trailing uses a direct loop.
Scoring a dirs array is then a pointer chase. Finalists are ALWAYS re-run with harness2.run."""
import sys
import numpy as np, pandas as pd
from numba import njit
sys.path.insert(0, "/home/user/trading-bridge/research")
sys.path.insert(0, "/home/user/trading-bridge/research/families/A_indicators")
import harness2 as H2
from core import build_tree, first_ge, first_le

SPREAD = H2.SPREAD


@njit(cache=True)
def tables_fixed(o, th, tl, P, sld, tpr, spread, i0, i1):
    m = i1 - i0
    lx = np.full(m, -1, np.int32); sx = np.full(m, -1, np.int32)
    lR = np.zeros(m, np.float32); sR = np.zeros(m, np.float32)
    for k in range(m):
        i = i0 + k; sl = sld[i]
        if not (sl > 0):
            continue
        tp = sl * tpr
        e = o[i] + spread
        jl = first_le(tl, P, i, e - sl); jw = first_ge(th, P, i, e + tp)
        if jl >= 0 and (jw < 0 or jl <= jw):
            lx[k] = jl; lR[k] = -1.0
        elif jw >= 0:
            lx[k] = jw; lR[k] = tpr
        e = o[i]
        jl = first_ge(th, P, i, e + sl - spread); jw = first_le(tl, P, i, e - tp - spread)
        if jl >= 0 and (jw < 0 or jl <= jw):
            sx[k] = jl; sR[k] = -1.0
        elif jw >= 0:
            sx[k] = jw; sR[k] = tpr
    return lx, lR, sx, sR


@njit(cache=True)
def one(o, h, l, c, i, d, sl, tp, tr, spread):
    n = len(o)
    if d > 0:
        e = o[i] + spread; stop = e - sl; best = e
    else:
        e = o[i]; stop = e + sl; best = e
    j = i
    while j < n:
        if d > 0:
            if l[j] <= stop:
                return j, (stop - e) / sl
            if tp > 0 and h[j] >= e + tp:
                return j, tp / sl
            if tr > 0:
                if h[j] > best: best = h[j]
                ns = best - tr
                if ns > stop: stop = ns
        else:
            if h[j] + spread >= stop:
                return j, (e - stop) / sl
            if tp > 0 and l[j] + spread <= e - tp:
                return j, tp / sl
            if tr > 0:
                if l[j] + spread < best: best = l[j] + spread
                ns = best + tr
                if ns < stop: stop = ns
        j += 1
    return -1, 0.0


@njit(cache=True)
def tables_trail(o, h, l, c, sld, tpr, trr, spread, i0, i1):
    m = i1 - i0
    lx = np.full(m, -1, np.int32); sx = np.full(m, -1, np.int32)
    lR = np.zeros(m, np.float32); sR = np.zeros(m, np.float32)
    for k in range(m):
        i = i0 + k; sl = sld[i]
        if not (sl > 0):
            continue
        tp = sl * tpr if tpr > 0 else -1.0
        j, r = one(o, h, l, c, i, 1, sl, tp, sl * trr, spread); lx[k] = j; lR[k] = r
        j, r = one(o, h, l, c, i, -1, sl, tp, sl * trr, spread); sx[k] = j; sR[k] = r
    return lx, lR, sx, sR


@njit(cache=True)
def walk(sig, mp, inv, lx, lR, sx, sR, i0, i1):
    """sig at native TF (int8), mp M1->tf index. Returns n, sumR, gross win, gross loss, sumsq."""
    i = i0; n = 0; s1 = 0.0; gw = 0.0; gl = 0.0; s2 = 0.0
    while i < i1:
        k = mp[i]
        s = sig[k] if k >= 0 else 0
        if s == 0:
            i += 1; continue
        if inv: s = -s
        r = i - i0
        if s > 0:
            j = lx[r]; x = lR[r]
        else:
            j = sx[r]; x = sR[r]
        if j < 0:
            i += 1; continue
        n += 1; s1 += x; s2 += x * x
        if x > 0: gw += x
        else: gl -= x
        i = j + 1
    return n, s1, gw, gl, s2


@njit(cache=True)
def walk_rel(dirs, lx, lR, sx, sR, i0, i1):
    i = i0; n = 0; s1 = 0.0; gw = 0.0; gl = 0.0; s2 = 0.0
    while i < i1:
        r = i - i0; s = dirs[r]
        if s == 0:
            i += 1; continue
        if s > 0:
            j = lx[r]; x = lR[r]
        else:
            j = sx[r]; x = sR[r]
        if j < 0:
            i += 1; continue
        n += 1; s1 += x; s2 += x * x
        if x > 0: gw += x
        else: gl -= x
        i = j + 1
    return n, s1, gw, gl, s2


class Engine:
    def __init__(self):
        m1 = H2.load_m1(); self.m1 = m1; self.idx = m1.index
        self.o = m1.open.values.astype(np.float64); self.h = m1.high.values.astype(np.float64)
        self.l = m1.low.values.astype(np.float64); self.c = m1.close.values.astype(np.float64)
        P = 1
        while P < len(m1): P *= 2
        self.P = P
        self.th = build_tree(self.h, P, True); self.tl = build_tree(self.l, P, False)

    def rng(self, period):
        a, b = H2.PERIODS[period]
        return int(self.idx.searchsorted(pd.Timestamp(a))), int(self.idx.searchsorted(pd.Timestamp(b)))

    def tables(self, sld, tpr, trr, i0, i1):
        if trr > 0:
            return tables_trail(self.o, self.h, self.l, self.c, sld, tpr, trr, SPREAD, i0, i1)
        return tables_fixed(self.o, self.th, self.tl, self.P, sld, tpr, SPREAD, i0, i1)


EXITS = {"TP1": (1.0, 0.0), "TP1.5": (1.5, 0.0), "TP2": (2.0, 0.0), "TR1": (-1.0, 1.0), "TR1_TP3": (3.0, 1.0)}


def run_h2(dirs, sl, exit_name):
    """Real harness2 run for an exit spec name."""
    tpr, trr = EXITS[exit_name]
    tp = sl * tpr if tpr > 0 else None
    tr = sl * trr if trr > 0 else None
    return H2.run(dirs, sl, tp, tr, 0)
