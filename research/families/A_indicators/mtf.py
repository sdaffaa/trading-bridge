"""Stage 2: multi-timeframe combinations, ranked on IS only.
Note: with two +/-1 signals a, b the only always-in-market rules are a, b, -a, -b, a*b, -a*b
("agree -> trade, disagree -> follow higher TF" is identical to just the higher TF), so we test
  * pair products a*b (and inverted) across different TFs,
  * 3-TF majority votes (and inverted),
  * 3-TF 'all agree -> that side, else follow the highest TF's opposite / lowest TF' variants.
Signal pool = per TF the 5 best (tf, sig, inv) by stage-1 IS win rate (n>=300)."""
import sys, time, itertools
import numpy as np, pandas as pd
sys.path.insert(0, "/home/user/trading-bridge/research/families/A_indicators")
from core import Engine, H, walk_rel
from grid import build_signals, dist_rules
from signals import TFS

OUT = "/home/user/trading-bridge/research/families/A_indicators/mtf_is.parquet"
ORDER = list(TFS)  # low -> high

if __name__ == "__main__":
    t0 = time.time()
    g = pd.read_parquet("/home/user/trading-bridge/research/families/A_indicators/grid_is.parquet")
    g = g[g.n >= 300]
    best = g.groupby(["tf", "sig", "inv"]).wr.max().reset_index().sort_values("wr", ascending=False)
    pool = best.groupby("tf").head(5)
    print(pool.to_string())
    E = Engine(); sig, maps, atrs = build_signals(); R = dist_rules(atrs, E.m1)
    i0, i1 = E.rng("IS")
    A = {}
    for r in pool.itertuples():
        v = sig[(r.tf, r.sig)][maps[r.tf][i0:i1]].astype(np.int8)
        v[maps[r.tf][i0:i1] < 0] = 0
        A[(r.tf, r.sig, r.inv)] = -v if r.inv else v
    keys = list(A)
    T = {}
    for dn, dist in R.items():
        lx, lw, sx, sw = E.tables(dist, i0, i1)
        T[dn] = (lx.astype(np.int32), lw, sx.astype(np.int32), sw)
    print("tables ready", f"{time.time()-t0:.0f}s", flush=True)

    def gen():
        for a, b in itertools.combinations(keys, 2):
            if a[0] != b[0]:
                yield f"PROD[{a}|{b}]", (A[a] * A[b]).astype(np.int8)
        for a, b, c in itertools.combinations(keys, 3):
            if len({a[0], b[0], c[0]}) < 3:
                continue
            s = A[a].astype(np.int16) + A[b] + A[c]
            ok = (A[a] != 0) & (A[b] != 0) & (A[c] != 0)
            yield f"MAJ[{a}|{b}|{c}]", np.where(ok, np.sign(s), 0).astype(np.int8)
            hi = max((a, b, c), key=lambda k: ORDER.index(k[0]))
            yield f"AGREE_else_fadeHTF[{a}|{b}|{c}]", np.where(ok, np.where(np.abs(s) == 3, np.sign(s), -A[hi]), 0).astype(np.int8)

    rows = []; cnt = 0
    for name, d in gen():
        cnt += 1
        for inv in (False, True):
            dd = -d if inv else d
            for dn, (lx, lw, sx, sw) in T.items():
                n, w = walk_rel(dd, lx, lw, sx, sw, i0, i1)
                rows.append((name, inv, dn, n, w))
        if cnt % 500 == 0:
            print(cnt, f"{time.time()-t0:.0f}s", flush=True)
    df = pd.DataFrame(rows, columns=["combo", "inv", "dist", "n", "w"])
    df["wr"] = 100 * df.w / df.n.clip(lower=1)
    df.to_parquet(OUT)
    print("done", cnt, "combos", len(df), "rows", f"{time.time()-t0:.0f}s")
