"""Strategy spec -> M1 dirs/SL arrays (causal, same alignment as harness.htf_to_m1), harness2 runs,
and a numba portfolio simulator with daily management (lock/stop/max trades/vol scaling).
Spec = dict(combo=..., inv=bool, sl=rule name, exit=EXITS key). combo is either
"SIG[(tf, name, inv)]" or "KIND[(..)|(..)|(..)]" with KIND in PROD, BOTH, MAJ, ALL, AGREE_else_fadeHTF."""
import sys, ast
import numpy as np, pandas as pd
from numba import njit
sys.path.insert(0, "/home/user/trading-bridge/research")
sys.path.insert(0, "/home/user/trading-bridge/research/families/A_indicators")
sys.path.insert(0, "/home/user/trading-bridge/research/families/F_portfolio")
import harness as H
import harness2 as H2
from signals import TFS, signals_for_tf
from engine import EXITS, Engine
WARM = "2018-01-01"
ORDER = list(TFS)
HOLD0 = pd.Timestamp(H2.PERIODS["HOLDOUT"][0])
m1 = H.load_m1()
_b, _s, _atr = {}, {}, {}


def bars(tf):
    if tf not in _b:
        _b[tf] = H.bars(TFS[tf])[lambda x: x.index >= WARM]
    return _b[tf]


def m1sig(key):
    tf, name, inv = key
    if tf not in _s:
        _s[tf] = signals_for_tf(bars(tf))
    v = H.htf_to_m1(pd.Series(_s[tf][name].astype(float), bars(tf).index), TFS[tf])
    v = np.nan_to_num(v, nan=0.0)
    return -v if inv else v


def sl_rule(name):
    k, tf = name.split("xATR_")
    if tf not in _atr:
        _atr[tf] = H.htf_to_m1(H.atr(bars(tf), 14), TFS[tf])
    return float(k) * _atr[tf]


def dirs_of(combo):
    kind, body = combo.split("[", 1)
    keys = [ast.literal_eval(x) for x in body[:-1].split("|")]
    A = [m1sig(k) for k in keys]
    if kind == "SIG":
        return A[0]
    if kind == "PROD":
        return A[0] * A[1]
    if kind == "BOTH":
        return np.where(A[0] == A[1], A[0], 0.0)
    ok = np.all([a != 0 for a in A], axis=0); s = A[0] + A[1] + A[2]
    if kind == "MAJ":
        return np.where(ok, np.sign(s), 0.0)
    if kind == "ALL":
        return np.where(np.abs(s) == 3, np.sign(s), 0.0)
    hi = max(range(3), key=lambda i: ORDER.index(keys[i][0]))
    return np.where(ok, np.where(np.abs(s) == 3, np.sign(s), -A[hi]), 0.0)


def build(spec, holdout=False):
    d = dirs_of(spec["combo"]).astype(np.float64)
    if spec["inv"]:
        d = -d
    d[m1.index < pd.Timestamp(H2.PERIODS["IS"][0])] = 0
    if not holdout:
        d[m1.index >= HOLD0] = 0          # selection phase: HOLDOUT invisible
    return d, sl_rule(spec["sl"])


def run_spec(spec, holdout=False):
    d, sl = build(spec, holdout)
    tpr, trr = EXITS[spec["exit"]]
    return H2.run(d, sl, sl * tpr if tpr > 0 else None, sl * trr if trr > 0 else None, 0)


def name_of(spec):
    return f"{spec['combo']}{'~inv' if spec['inv'] else ''} SL={spec['sl']} {spec['exit']}"


# ---------------- per-strategy chosen-side outcome table over a bar range ----------------
@njit(cache=True)
def _pick(d, lx, lR, sx, sR, i0):
    m = len(lx); X = np.full(m, -1, np.int32); RR = np.zeros(m, np.float32); S = np.zeros(m, np.int8)
    for k in range(m):
        s = d[i0 + k]
        if s > 0:
            X[k] = lx[k]; RR[k] = lR[k]; S[k] = 1
        elif s < 0:
            X[k] = sx[k]; RR[k] = sR[k]; S[k] = -1
    return X, RR, S


def outcome_table(E, spec, i0, i1, holdout=False):
    d, sl = build(spec, holdout)
    tpr, trr = EXITS[spec["exit"]]
    lx, lR, sx, sR = E.tables(sl, tpr, trr, i0, i1)
    X, RR, S = _pick(d, lx, lR, sx, sR, i0)
    return X, RR, S, sl[i0:i1].astype(np.float64)


@njit(cache=True)
def psim(X, RR, S, SL, o, c, day, i0, lock_up, lock_dn, maxtr, eqmode, spread, wts):
    """X,RR,S,SL: (K, m) chosen-side tables relative to i0. day: (m,) int day id.
    lock_up/lock_dn (R, >0; <=0 disables): once the day's P&L reaches +lock_up or -lock_dn no new entries
    that day; eqmode=1 uses equity (realized + floating at bar close) and also closes open trades at that close.
    maxtr: max entries per day across the portfolio (<=0 none). wts: (m,) risk weight applied at entry.
    Returns per-trade arrays (entry k, exit k, R*w, strat)."""
    K, m = X.shape
    busy = np.full(K, -1, np.int64); pr = np.zeros(K); pw = np.ones(K)
    pe = np.zeros(K); ps = np.zeros(K, np.int8); pent = np.zeros(K, np.int64)
    oe = np.empty(m * 2, np.int64); ox = np.empty(m * 2, np.int64); orr = np.empty(m * 2); ost = np.empty(m * 2, np.int32)
    nt = 0; cur = -1; dayR = 0.0; ntr = 0; locked = False
    for k in range(m):
        if day[k] != cur:
            cur = day[k]; dayR = 0.0; ntr = 0; locked = False
        # entries at open of bar k
        if not locked:
            for q in range(K):
                if busy[q] >= 0:
                    continue
                if S[q, k] == 0 or X[q, k] < 0:
                    continue
                if maxtr > 0 and ntr >= maxtr:
                    break
                busy[q] = X[q, k]
                pr[q] = RR[q, k]; pw[q] = wts[k]; ps[q] = S[q, k]; pent[q] = k
                pe[q] = o[i0 + k] + (spread if S[q, k] > 0 else 0.0)
                ntr += 1
        # exits during bar k (X holds ABSOLUTE bar index)
        for q in range(K):
            if busy[q] >= 0 and busy[q] == i0 + k:
                r = pr[q] * pw[q]; dayR += r
                oe[nt] = pent[q]; ox[nt] = k; orr[nt] = r; ost[nt] = q; nt += 1
                busy[q] = -1
        if locked:
            continue
        eq = dayR
        if eqmode == 1:
            for q in range(K):
                if busy[q] >= 0:
                    if ps[q] > 0:
                        eq += pw[q] * (c[i0 + k] - pe[q]) / SL[q, pent[q]]
                    else:
                        eq += pw[q] * (pe[q] - c[i0 + k] - spread) / SL[q, pent[q]]
        if (lock_up > 0 and eq >= lock_up) or (lock_dn > 0 and eq <= -lock_dn):
            locked = True
            if eqmode == 1:
                for q in range(K):
                    if busy[q] >= 0:
                        if ps[q] > 0:
                            r = pw[q] * (c[i0 + k] - pe[q]) / SL[q, pent[q]]
                        else:
                            r = pw[q] * (pe[q] - c[i0 + k] - spread) / SL[q, pent[q]]
                        dayR += r
                        oe[nt] = pent[q]; ox[nt] = k; orr[nt] = r; ost[nt] = q; nt += 1
                        busy[q] = -1
    return oe[:nt], ox[:nt], orr[:nt], ost[:nt]


def day_stats(day, periods=("IS", "VAL", "HOLDOUT")):
    """day: pd.Series of daily R indexed by date (only days with >=1 closed trade)."""
    out = {}
    for p in periods:
        a, b = H2.PERIODS[p]
        x = day[(day.index >= pd.Timestamp(a).date()) & (day.index < pd.Timestamp(b).date())]
        if len(x) == 0:
            out[p] = dict(totR=0.0); continue
        eq = x.cumsum(); mo = x.groupby(pd.to_datetime(x.index).to_period("M")).sum()
        out[p] = dict(days=len(x), totR=round(x.sum(), 1), R_day=round(x.mean(), 3),
                      green_days=round((x > 0).mean() * 100, 1), red_days=round((x < 0).mean() * 100, 1),
                      maxDD=round((eq - eq.cummax()).min(), 1), worst_day=round(x.min(), 1),
                      green_months=round((mo > 0).mean() * 100, 1),
                      sharpe_d=round(x.mean() / x.std() * np.sqrt(252), 2) if x.std() > 0 else 0.0)
    return out
