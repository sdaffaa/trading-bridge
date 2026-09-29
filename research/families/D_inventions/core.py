"""Family D shared core: fast, harness-identical evaluation for search.

* Outcome tables: for a per-bar distance array, precompute for EVERY M1 bar the result
  of a long and a short 1:1 trade opened at that bar's open (via harness.trade_once,
  identical fill rules). A consecutive strategy is then a pointer walk: i -> exit+1.
* walk(): numba pointer walk given per-bar directions -> (entry, exit, side, r), which is
  exactly what harness._run produces (verified in verify_core.py).
* Periods come from harness.PERIODS (read at import).  Search helpers stop at VAL end so
  HOLDOUT is never looked at during selection.
"""
import sys, os
sys.path.insert(0, "/home/user/trading-bridge/research")
import numpy as np, pandas as pd
from numba import njit
import harness as H

M1 = H.load_m1()
O = M1.open.values.astype(np.float64); HI = M1.high.values.astype(np.float64)
LO = M1.low.values.astype(np.float64); C = M1.close.values.astype(np.float64)
T = M1.index
N = len(M1)


def idx_of(ts):
    return int(np.searchsorted(T.values, np.datetime64(pd.Timestamp(ts))))


P = {k: (idx_of(a), idx_of(b)) for k, (a, b) in H.PERIODS.items()}
IS0, IS1 = P["IS"]; VAL0, VAL1 = P["VAL"]; HO0, HO1 = P["HOLDOUT"]
WARM0 = idx_of("2020-01-01")   # only warm-up data before IS start is ever touched


@njit(cache=True)
def _tables(o, h, l, dist, spread, i0, i1):
    n = len(o)
    wl = np.zeros(n, np.int8); el = np.full(n, -1, np.int64)
    ws = np.zeros(n, np.int8); es = np.full(n, -1, np.int64)
    for i in range(i0, i1):
        d = dist[i]
        if not (d > 0):
            continue
        r, j = H.trade_once(o, h, l, i, 1.0, d, spread)
        wl[i] = r; el[i] = j
        r, j = H.trade_once(o, h, l, i, -1.0, d, spread)
        ws[i] = r; es[i] = j
    return wl, el, ws, es


def tables(dist, i0=WARM0, i1=None):
    """Outcome tables over [i0, i1). Default: warm-up..VAL end (no HOLDOUT)."""
    if i1 is None:
        i1 = VAL1
    return _tables(O, HI, LO, np.asarray(dist, np.float64), H.SPREAD, i0, i1)


@njit(cache=True)
def walk(dirs, wl, el, ws, es, i0, i1):
    """Consecutive pointer walk from bar i0 to i1 using precomputed tables."""
    m = i1 - i0
    ent = np.empty(m, np.int64); ex = np.empty(m, np.int64)
    res = np.empty(m, np.int8); side = np.empty(m, np.int8)
    k = 0; i = i0
    while i < i1:
        d = dirs[i]
        if d > 0:
            r = wl[i]; j = el[i]
        elif d < 0:
            r = ws[i]; j = es[i]
        else:
            i += 1; continue
        if r == 0:          # no distance here (warm-up/gap) or data ended
            if j < 0:
                i += 1; continue
            break
        ent[k] = i; ex[k] = j; res[k] = r; side[k] = 1 if d > 0 else -1
        k += 1; i = j + 1
    return ent[:k], ex[:k], res[:k], side[:k]


def to_df(ent, ex, res, side):
    return pd.DataFrame({"t": T[ent], "exit_t": T[ex], "side": side, "r": res})


@njit(cache=True)
def wr_split(ent, res, a0, a1, b0, b1):
    na = 0; wa = 0; nb = 0; wb = 0
    for k in range(len(ent)):
        e = ent[k]
        if e >= a0 and e < a1:
            na += 1; wa += res[k] > 0
        elif e >= b0 and e < b1:
            nb += 1; wb += res[k] > 0
    return na, (wa / na if na else 0.0), nb, (wb / nb if nb else 0.0)


def quick(dirs, tb, start=IS0, stop=VAL1):
    """IS and VAL (n, wr) for a direction array under tables tb (no HOLDOUT)."""
    ent, ex, res, side = walk(np.asarray(dirs, np.float64), *tb, start, stop)
    return wr_split(ent, res, IS0, IS1, VAL0, VAL1)


def full_run(dirs, dist):
    """Final, authoritative evaluation with the harness itself (all periods).
    Data before WARM0 gets dirs=0 so trading starts at 2020-01 (warm-up only)."""
    d = np.asarray(dirs, np.float64).copy(); d[:WARM0] = 0
    tr = H.run_consecutive(d, dist)
    return tr, H.stats(tr)


# ---------- common per-bar helpers (all causal: value at bar i uses bars < i) ----------
def htf(series, tf):
    return H.htf_to_m1(series, tf)


def atr_m1(tf="1h", n=14):
    return htf(H.atr(H.bars(tf), n), tf)
