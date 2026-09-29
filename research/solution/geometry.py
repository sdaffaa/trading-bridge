"""Solution search: keep the most stable family-A signal (consecutive trades, no waiting)
and vary the TP:SL geometry. Reports win rate AND expectancy (R per trade), because
win rate alone can be raised for free by shrinking TP."""
import sys
import numpy as np, pandas as pd
from numba import njit
sys.path.insert(0, "/home/user/trading-bridge/research")
sys.path.insert(0, "/home/user/trading-bridge/research/families/A_indicators")
import harness as H
from signals import TFS
import validate_lib as V   # thin copy of validate.py helpers (no side effects)

@njit(cache=True)
def run(o, h, l, dirs, sld, tpr, spread):
    n = len(o); ent = np.empty(n, np.int64); res = np.empty(n, np.int8); k = 0; i = 0
    while i < n:
        d = dirs[i]; sl = sld[i]
        if not (sl > 0) or d == 0 or np.isnan(d): i += 1; continue
        tp = sl * tpr; out = 0; j = i
        if d > 0:
            e = o[i] + spread
            for j in range(i, n):
                if l[j] <= e - sl: out = -1; break
                if h[j] >= e + tp: out = 1; break
        else:
            e = o[i]
            for j in range(i, n):
                if h[j] + spread >= e + sl: out = -1; break
                if l[j] + spread <= e - tp: out = 1; break
        if out == 0: break
        ent[k] = i; res[k] = out; k += 1; i = j + 1
    return ent[:k], res[:k]

m1 = H.load_m1()
combos = pd.read_csv("/home/user/trading-bridge/research/families/A_indicators/final10_holdout.csv")
o, h, l = m1.open.values, m1.high.values, m1.low.values
rows = []
for rank, r in enumerate(combos.itertuples(), 1):
    d = V.dirs_of(r.combo); d = -d if r.inv else d
    d = d.copy(); d[m1.index < pd.Timestamp(H.PERIODS["IS"][0])] = 0
    sl = V.R[r.dist]
    for tpr in (1.0, 0.9, 0.8, 0.7, 0.6, 0.5):
        ent, res = run(o, h, l, d.astype(np.float64), sl, tpr, H.SPREAD)
        t = m1.index[ent]
        row = dict(rank=rank, dist=r.dist, tp_to_sl=tpr)
        for p, (a, b) in H.PERIODS.items():
            x = res[(t >= a) & (t < b)]; w = (x > 0)
            dd = pd.Series(w, index=t[(t >= a) & (t < b)]).groupby(lambda z: z.date()).mean()
            row[f"{p}_n"] = len(x); row[f"{p}_wr"] = round(w.mean() * 100, 1)
            row[f"{p}_R/trade"] = round((w * tpr - (~w)).mean(), 3)
            row[f"{p}_days>=60"] = round((dd >= .6).mean() * 100, 0)
        rows.append(row); print(row, flush=True)
pd.DataFrame(rows).to_csv("/home/user/trading-bridge/research/solution/geometry.csv", index=False)
