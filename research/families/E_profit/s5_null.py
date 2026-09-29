"""Selection-bias null (IS only): random-direction entries at random H1/M30 closes, run through the
same 'trend' exit grid; how large does the best qualifying IS totR get by chance?"""
import numpy as np, pandas as pd
from common import *
rng = np.random.default_rng(7); best = []; allq = []
for seed in range(60):
    tf = ("H1", "M30")[seed % 2]; nb = len(B(tf)); p = 0.03 if tf == "H1" else 0.015
    ev = np.where(rng.random(nb) < p, rng.choice([-1.0, 1.0], nb), 0.0)
    d = event_m1(ev, tf); a = ATRM1(tf); bs = -1e9
    for slmode, slk, tpr, trk, mb in exit_grid("trend", False):
        sl, tp, tr = exits(a, slk, tpr, trk)
        st, _ = evaluate(d, sl, tp, tr, mb, ("IS",))
        s = st["IS"]
        if s["n"] >= 150 and s["PF"] > 1.1: allq.append(s["totR"]); bs = max(bs, s["totR"])
    best.append(bs)
best = np.array(best); best = best[best > -1e9]
print("random-entry sets:", 60, "x", len(exit_grid("trend", False)), "exits =", 60 * len(exit_grid("trend", False)), "variants")
print("qualifying variants:", len(allq), "max IS totR:", max(allq) if allq else None,
      "95th pct of qualifying:", np.percentile(allq, 95) if allq else None)
print("per-set best (sets with any qualifier):", len(best), np.round(np.sort(best)[::-1][:10], 1))
