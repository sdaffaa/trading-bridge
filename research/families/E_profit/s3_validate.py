"""Stage 3: rank all IS-screened variants (n>=150, PF>1.1) by IS totR; take the top 50
(max 3 per entry) to VAL; final 10 = best IS rank with VAL totR>0 (max 2 per entry)."""
import pandas as pd, numpy as np
from common import *
E = registry()
df = pd.concat([pd.read_parquet("s1_is.parquet"), pd.read_parquet("s2_is.parquet")], ignore_index=True)
df = df.drop_duplicates(["name", "slmode", "slk", "tpr", "trk", "mb", "filt"])
print("total variants tested (IS):", len(df))
q = df[(df.IS_n >= 150) & (df.IS_PF > 1.1)].sort_values(["IS_totR", "IS_maxDD"], ascending=[False, False])
print("qualified:", len(q))
cand = q.groupby("name").head(3).head(50)
rows = []
for r in cand.itertuples():
    tpr = None if pd.isna(r.tpr) else r.tpr; trk = None if pd.isna(r.trk) else r.trk
    d, sl, tp, tr, mb = build(r.name, r.slmode, r.slk, tpr, trk, r.mb, r.filt, E)
    st, _ = evaluate(d, sl, tp, tr, mb, ("IS", "VAL"))
    rows.append(dict(name=r.name, fam=r.fam, slmode=r.slmode, slk=r.slk, tpr=tpr, trk=trk, mb=r.mb, filt=r.filt, **flat(st)))
v = pd.DataFrame(rows); v.to_csv("s3_is_val.csv", index=False)
pd.set_option("display.width", 250)
cols = ["name", "slk", "tpr", "trk", "mb", "filt", "IS_n", "IS_totR", "IS_PF", "IS_maxDD", "VAL_n", "VAL_totR", "VAL_R_trade", "VAL_PF", "VAL_maxDD"]
print(v[cols].to_string())
print("VAL>0:", (v.VAL_totR > 0).sum(), "of", len(v))
fin = v[v.VAL_totR > 0].drop_duplicates(["name", "IS_n", "IS_totR", "VAL_n", "VAL_totR"]).groupby("name").head(2).head(10)  # identical-trade duplicates removed
fin.to_csv("final10_spec.csv", index=False)
print(fin[cols].to_string())
