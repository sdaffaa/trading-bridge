"""Null benchmark: random coin-flip H1 signals through the same 52 stop rules (IS only)."""
import sys; sys.path.insert(0, "/home/user/trading-bridge/research/families/A_indicators")
import numpy as np, pandas as pd
from core import Engine, H, walk, tf_map
from grid import build_signals, dist_rules, WARM
E = Engine(); i0, i1 = E.rng("IS")
atrs = {tf: H.atr(H.bars(f)[lambda x: x.index >= WARM], 14) for tf, f in __import__("signals").TFS.items()}
R = dist_rules(atrs, E.m1)
b = H.bars("1h"); b = b[b.index >= WARM]; mp = tf_map("1h", b.index)
rng = np.random.default_rng(7); S = [rng.choice(np.array([-1, 1], np.int8), len(b)) for _ in range(1000)]
rows = []
for dn, d in R.items():
    T = E.tables(d, i0, i1)
    for k, s in enumerate(S):
        n, w = walk(s, mp, False, *T, i0, i1); rows.append((k, dn, n, w))
df = pd.DataFrame(rows, columns=["k", "dist", "n", "w"]); df["wr"] = 100 * df.w / df.n.clip(lower=1)
q = df[df.n >= 300]
print("random null: combos", len(q), "pcts50/90/99/99.9", q.wr.quantile([.5, .9, .99, .999]).round(2).tolist(), "max", round(q.wr.max(), 2))
print("n>=700 max", round(df[df.n >= 700].wr.max(), 2))
