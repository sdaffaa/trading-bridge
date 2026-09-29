"""Stage 3: take IS top-50 (grid + MTF, n>=300 on IS), re-run each with the REAL harness
run_consecutive + stats on IS and VAL; pick final 10 by min(IS wr, VAL wr); only those are
evaluated on HOLDOUT."""
import sys, ast, json
import numpy as np, pandas as pd
sys.path.insert(0, "/home/user/trading-bridge/research/families/A_indicators")
from core import H
from grid import dist_rules, WARM
from signals import TFS, signals_for_tf

D = "/home/user/trading-bridge/research/families/A_indicators/"
ORDER = list(TFS)

m1 = H.load_m1()
cache_b, cache_s = {}, {}


def m1sig(key):
    tf, name, inv = key
    b = cache_b[tf]
    if tf not in cache_s:
        cache_s[tf] = signals_for_tf(b)
    v = H.htf_to_m1(pd.Series(cache_s[tf][name].astype(float), b.index), TFS[tf])
    v = np.nan_to_num(v, nan=0.0)
    return -v if inv else v


def dirs_of(combo):
    kind, body = combo.split("[", 1)
    keys = [ast.literal_eval(x) for x in body[:-1].split("|")]
    A = [m1sig(k) for k in keys]
    if kind == "SIG":
        return A[0]
    ok = np.all([a != 0 for a in A], axis=0)
    if kind == "PROD":
        return A[0] * A[1]
    s = A[0] + A[1] + A[2]
    if kind == "MAJ":
        return np.where(ok, np.sign(s), 0.0)
    hi = max(range(3), key=lambda i: ORDER.index(keys[i][0]))
    return np.where(ok, np.where(np.abs(s) == 3, np.sign(s), -A[hi]), 0.0)


atrs = {tf: H.atr(cache_b.setdefault(tf, H.bars(f)[lambda x: x.index >= WARM]), 14) for tf, f in TFS.items()}
R = dist_rules(atrs, m1)

