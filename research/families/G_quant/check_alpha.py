"""Sanity: full (unmasked) rebuild reproduces registry IS/VAL; and alpha/beta of each top-10 vs vol-targeted B&H
(daily OLS, HAC t) per period — how much is just long-gold exposure."""
import numpy as np, pandas as pd, statsmodels.api as sm
import common as G, build as Bd, harness3 as H3
top = pd.read_csv(f"{G.HERE}/top10_selected.csv")
bh = G.daily_all(H3.pnl(G.vt(pd.Series(1.0, index=G.B.index)), G.B))
rows = []
for _, r in top.iterrows():
    d = G.daily_all(H3.pnl(Bd.full_pos(r["name"], r["params"]), G.B))
    row = dict(name=r["name"], reg_IS=r.IS_sr, rebuilt_IS=G.pstats(d, "IS")["sr"], reg_VAL=r.VAL_sr, rebuilt_VAL=G.pstats(d, "VAL")["sr"])
    for p in ("IS", "VAL", "HOLDOUT"):
        a, b = G.PER[p]; m = (d.index >= a) & (d.index < b)
        f = sm.OLS(d[m].values, sm.add_constant(bh[m].values)).fit(cov_type="HAC", cov_kwds={"maxlags": 5})
        row[f"{p}_beta"] = round(f.params[1], 2); row[f"{p}_alpha_ann%"] = round(f.params[0] * 260 * 100, 1); row[f"{p}_alpha_t"] = round(f.tvalues[0], 2)
    rows.append(row)
out = pd.DataFrame(rows); out.to_csv(f"{G.HERE}/top10_alpha.csv", index=False)
pd.set_option("display.width", 250); print(out.to_string(index=False))
