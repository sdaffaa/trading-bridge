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

g = pd.read_parquet(D + "grid_is.parquet")
g["combo"] = g.apply(lambda r: f"SIG[{(r.tf, r.sig, False)}]", axis=1)
m = pd.read_parquet(D + "mtf_is.parquet")
allr = pd.concat([g[["combo", "inv", "dist", "n", "w", "wr"]], m], ignore_index=True)
q = allr[allr.n >= 300]
# pool A: the IS top-50 with >=300 IS trades (as specified).
# pool B: IS top-50 among combos with >=700 IS trades (IS = 3y, VAL = 1.5y, HOLDOUT = 1.6y, so
# ~700 IS trades are needed for VAL/HOLDOUT to reach 300 at all; pool A is dominated by wide stops).
topA = q.sort_values("wr", ascending=False).head(50).assign(pool="A")
topB = q[q.n >= 700].sort_values("wr", ascending=False).head(50).assign(pool="B")
top = pd.concat([topA, topB]).drop_duplicates(["combo", "inv", "dist"]).reset_index(drop=True)

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

rows = []
for r in top.itertuples():
    d = dirs_of(r.combo)
    if r.inv:
        d = -d
    d = d.copy(); d[m1.index < pd.Timestamp(H.PERIODS["IS"][0])] = 0  # no trades before IS
    tr = H.run_consecutive(d, R[r.dist])
    st = H.stats(tr, ("IS", "VAL"))
    rows.append(dict(pool=r.pool, combo=r.combo, inv=r.inv, dist=r.dist, fastIS_wr=round(r.wr, 2), fastIS_n=r.n,
                     IS_n=st["IS"]["n"], IS_wr=st["IS"]["wr"], VAL_n=st["VAL"].get("n", 0), VAL_wr=st["VAL"].get("wr", np.nan)))
    print(rows[-1], flush=True)
v = pd.DataFrame(rows)
v["minwr"] = v[["IS_wr", "VAL_wr"]].min(axis=1)
v.to_csv(D + "top50_is_val.csv", index=False)

fin = v[v.VAL_n >= 300].sort_values("minwr", ascending=False).head(10)
print(len(fin), "finalists with VAL n>=300", flush=True)
out = []
for r in fin.itertuples():
    d = dirs_of(r.combo)
    if r.inv:
        d = -d
    d = d.copy(); d[m1.index < pd.Timestamp(H.PERIODS["IS"][0])] = 0
    st = H.stats(H.run_consecutive(d, R[r.dist]))
    print(H.fmt(f"{r.combo} inv={r.inv} {r.dist}"[:45], st), "PASSES" if H.passes(st) else "", flush=True)
    out.append(dict(combo=r.combo, inv=r.inv, dist=r.dist, **{f"{p}_{k}": st[p].get(k) for p in st for k in ("n", "wr")},
                    passes=H.passes(st)))
pd.DataFrame(out).to_csv(D + "final10_holdout.csv", index=False)
