"""Stage 1: screen every entry x exit combination on IS ONLY (dirs masked to IS)."""
import time, pandas as pd, numpy as np
from common import *
import common as CM
E = registry(); rows = []; t0 = time.time()
print("entries", len(E), flush=True)
for i, (name, (fam, fn, atf, grp)) in enumerate(E.items()):
    d0, w = fn(); CM._EC[name] = (d0, w)
    for slmode, slk, tpr, trk, mb in exit_grid(grp, w is not None):
        d, sl, tp, tr, mb = build(name, slmode, slk, tpr, trk, mb, E=E)
        st, _ = evaluate(d, sl, tp, tr, mb, ("IS",))
        rows.append(dict(name=name, fam=fam, slmode=slmode, slk=slk, tpr=tpr, trk=trk, mb=mb, filt="none", **flat(st)))
    del CM._EC[name]
    if i % 20 == 0: print(i, name, len(rows), round(time.time() - t0), flush=True)
df = pd.DataFrame(rows); df.to_parquet("s1_is.parquet")
print("variants", len(df))
q = df[(df.IS_n >= 150) & (df.IS_PF > 1.1)].sort_values("IS_totR", ascending=False)
pd.set_option("display.width", 250); pd.set_option("display.max_columns", 30)
print("qualified", len(q))
print(q.head(40)[["name", "slmode", "slk", "tpr", "trk", "mb", "IS_n", "IS_totR", "IS_R_trade", "IS_PF", "IS_green_days", "IS_R_day", "IS_maxDD"]].to_string())
print(q.groupby("fam").IS_totR.agg(["count", "max"]))
print(df.groupby("fam").IS_totR.agg(["count", "median", "max"]))
