"""Stage 1: re-rank the family-A universe by EXPECTANCY (R), not win rate.
Universe: 792 single signals (6 TFs) x {normal, inverted}, then MTF combos (pair products, 3-TF majority,
3-TF unanimous-else-flat, agree-else-fade-HTF) built from the IS-best signals by R.
Exit grid: 7 SL rules x 5 exits (TP=1,1.5,2 x SL; trail=1xSL no TP; trail=1xSL + TP=3xSL).
Scores on IS and VAL with the exact fast engine (engine.py == harness2, verified in test_engine.py).
HOLDOUT tables are never built here."""
import sys, time, itertools
import numpy as np, pandas as pd
sys.path.insert(0, "/home/user/trading-bridge/research/families/F_portfolio")
sys.path.insert(0, "/home/user/trading-bridge/research/families/A_indicators")
from engine import Engine, EXITS, walk, walk_rel
from grid import build_signals, dist_rules
from signals import TFS
D = "/home/user/trading-bridge/research/families/F_portfolio/"
SLS = ["2xATR_M15", "1xATR_H1", "2xATR_H1", "3xATR_H1", "1xATR_H4", "2xATR_H4", "1xATR_D1"]
ORDER = list(TFS)


def score(n, s1, gw, gl, s2):
    m = s1 / max(n, 1); sd = np.sqrt(max(s2 / max(n, 1) - m * m, 1e-12))
    return n, s1, gw / gl if gl > 0 else np.inf, m / sd * np.sqrt(n)


if __name__ == "__main__":
    t0 = time.time()
    E = Engine(); sig, maps, atrs = build_signals(); R = dist_rules(atrs, E.m1)
    rngs = {p: E.rng(p) for p in ("IS", "VAL")}
    T = {}
    for sl in SLS:
        for ex, (tpr, trr) in EXITS.items():
            for p, (i0, i1) in rngs.items():
                T[(sl, ex, p)] = E.tables(R[sl], tpr, trr, i0, i1)
        print("tables", sl, f"{time.time()-t0:.0f}s", flush=True)
    rules = [(sl, ex) for sl in SLS for ex in EXITS]
    rows = []
    for (tf, name), s in sig.items():
        for inv in (False, True):
            for sl, ex in rules:
                r = [tf, name, inv, sl, ex]
                for p, (i0, i1) in rngs.items():
                    r += list(score(*walk(s, maps[tf], inv, *T[(sl, ex, p)], i0, i1)))
                rows.append(r)
    cols = ["tf", "sig", "inv", "sl", "exit"] + [f"{p}_{k}" for p in ("IS", "VAL") for k in ("n", "R", "PF", "sqn")]
    g = pd.DataFrame(rows, columns=cols); g.to_parquet(D + "s1_single.parquet")
    print("singles done", len(g), f"{time.time()-t0:.0f}s", flush=True)
    # MTF pool: per TF the 5 best (sig, inv) by IS sqn (n>=300), selected on IS only
    q = g[g.IS_n >= 300]
    best = q.groupby(["tf", "sig", "inv"]).IS_sqn.max().reset_index().sort_values("IS_sqn", ascending=False)
    pool = best.groupby("tf").head(5)
    print(pool.to_string(), flush=True)
    A = {}
    for p, (i0, i1) in rngs.items():
        for r in pool.itertuples():
            mp = maps[r.tf][i0:i1]
            v = sig[(r.tf, r.sig)][mp].astype(np.int8); v[mp < 0] = 0
            A[(p, (r.tf, r.sig, r.inv))] = -v if r.inv else v
    keys = [(r.tf, r.sig, r.inv) for r in pool.itertuples()]

    def gen(p):
        for a, b in itertools.combinations(keys, 2):
            if a[0] != b[0]:
                x, y = A[(p, a)], A[(p, b)]
                yield f"PROD[{a}|{b}]", (x * y).astype(np.int8)
                yield f"BOTH[{a}|{b}]", np.where(x == y, x, 0).astype(np.int8)
        for a, b, c in itertools.combinations(keys, 3):
            if len({a[0], b[0], c[0]}) < 3:
                continue
            x, y, z = A[(p, a)], A[(p, b)], A[(p, c)]
            s = x.astype(np.int16) + y + z; ok = (x != 0) & (y != 0) & (z != 0)
            yield f"MAJ[{a}|{b}|{c}]", np.where(ok, np.sign(s), 0).astype(np.int8)
            yield f"ALL[{a}|{b}|{c}]", np.where(np.abs(s) == 3, np.sign(s), 0).astype(np.int8)
            hi = max((a, b, c), key=lambda k: ORDER.index(k[0]))
            yield f"AGREE_else_fadeHTF[{a}|{b}|{c}]", np.where(ok, np.where(np.abs(s) == 3, np.sign(s), -A[(p, hi)]), 0).astype(np.int8)
    res = {}
    for p, (i0, i1) in rngs.items():
        cnt = 0
        for name, d in gen(p):
            cnt += 1
            for inv in (False, True):
                dd = -d if inv else d
                for sl, ex in rules:
                    res.setdefault((name, inv, sl, ex), []).extend(score(*walk_rel(dd, *T[(sl, ex, p)], i0, i1)))
            if cnt % 2000 == 0:
                print(p, cnt, f"{time.time()-t0:.0f}s", flush=True)
    m = pd.DataFrame([list(k) + v for k, v in res.items()],
                     columns=["combo", "inv", "sl", "exit"] + cols[5:])
    m.to_parquet(D + "s1_mtf.parquet")
    print("mtf done", len(m), f"{time.time()-t0:.0f}s")
