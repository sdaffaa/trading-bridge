"""Stage 2 (IS only): WHEN-to-trade filters and time exits applied to the best stage-1 bases."""
import time, pandas as pd, numpy as np
from common import *
import common as CM
E = registry()
s1 = pd.read_parquet("s1_is.parquet")
q = s1[(s1.IS_n >= 150) & (s1.IS_PF > 1.1)].sort_values("IS_totR", ascending=False)
best = q.drop_duplicates("name")                      # best exit per entry
bases = pd.concat([best.head(40), best.groupby("fam").head(8)]).drop_duplicates("name")
# also best 3 exits of the top 10 entries
bases = pd.concat([bases, q[q.name.isin(best.head(10).name)].groupby("name").head(3)]).drop_duplicates(
    ["name", "slmode", "slk", "tpr", "trk", "mb"])
print("bases", len(bases), flush=True)
FILTERS = ["sess7_17", "sess12_17", "notasia", "adxH1_20", "adxH1_25", "adxH4_25", "adxD1_20", "volhiH1", "volloH1",
           "volhiD1", "volloD1", "dtrend50", "dtrend200", "h4trend50", "dtrend50+sess7_17", "dtrend50+adxH4_25",
           "volhiH1+sess7_17", "dtrend200+notasia"]
rows = []; t0 = time.time()
for k, r in enumerate(bases.itertuples()):
    tpr = None if pd.isna(r.tpr) else r.tpr; trk = None if pd.isna(r.trk) else r.trk
    for f in FILTERS:
        d, sl, tp, tr, mb = build(r.name, r.slmode, r.slk, tpr, trk, r.mb, f, E)
        st, _ = evaluate(d, sl, tp, tr, mb, ("IS",))
        rows.append(dict(name=r.name, fam=r.fam, slmode=r.slmode, slk=r.slk, tpr=tpr, trk=trk, mb=r.mb, filt=f, **flat(st)))
    for mb2 in (60, 240, 480, 1440, 2880, 7200):
        d, sl, tp, tr, _ = build(r.name, r.slmode, r.slk, tpr, trk, r.mb, "none", E)
        st, _ = evaluate(d, sl, tp, tr, mb2, ("IS",))
        rows.append(dict(name=r.name, fam=r.fam, slmode=r.slmode, slk=r.slk, tpr=tpr, trk=trk, mb=mb2, filt="none", **flat(st)))
    if k % 10 == 0: print(k, r.name, round(time.time() - t0), flush=True)
df = pd.DataFrame(rows); df.to_parquet("s2_is.parquet"); print("variants", len(df))
pd.set_option("display.width", 250)
q2 = df[(df.IS_n >= 150) & (df.IS_PF > 1.1)].sort_values("IS_totR", ascending=False)
print(q2.head(40)[["name", "slmode", "slk", "tpr", "trk", "mb", "filt", "IS_n", "IS_totR", "IS_R_trade", "IS_PF", "IS_green_days", "IS_R_day", "IS_maxDD"]].to_string())
