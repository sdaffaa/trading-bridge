"""FINAL: the only script that touches HOLDOUT. Evaluates the pre-selected top 10 (top10_selected.csv) and
baselines with harness3.stats (per period), plus Sharpe SE, t-stat of mean daily return, DSR."""
import json, numpy as np, pandas as pd
from scipy.stats import norm, skew, kurtosis
import common as G, build as Bd, harness3 as H3

top = pd.read_csv(f"{G.HERE}/top10_selected.csv")
tri = pd.read_csv(f"{G.HERE}/trial_sharpes.csv")
N_ALL, N_UNIQ = 630, 547
V_is = tri.sr_is_daily.var(); V_iv = tri.sr_isval_daily.var()


def seg(d, a, b):
    return d[(d.index >= pd.Timestamp(a)) & (d.index < pd.Timestamp(b))]


def sr_se(x):
    s = x.mean() / x.std(); g3 = skew(x); g4 = kurtosis(x, fisher=False); T = len(x)
    return s, np.sqrt((1 - g3 * s + (g4 - 1) / 4 * s * s) / (T - 1))


def dsr(x, V, N):
    s, se = sr_se(x)
    e = 0.5772156649
    sr0 = np.sqrt(V) * ((1 - e) * norm.ppf(1 - 1 / N) + e * norm.ppf(1 - 1 / (N * np.e)))
    return norm.cdf((s - sr0) / se), sr0


rows = []
series = {"B&H 1x": pd.Series(1.0, index=G.B.index), "B&H vt10": G.vt(pd.Series(1.0, index=G.B.index))}
for _, r in top.iterrows():
    series[r["name"]] = Bd.full_pos(r["name"], r["params"])
for nm, p in series.items():
    rb = H3.pnl(p, G.B)
    st = H3.stats(rb)
    d = G.daily_all(rb)
    row = dict(name=nm)
    for per in ("IS", "VAL", "HOLDOUT"):
        v = st[per]
        row.update({f"{per}_sr": v["sharpe"], f"{per}_ret": v["ann_ret"], f"{per}_dd": v["maxDD"], f"{per}_gd": v["green_days"], f"{per}_gm": v["green_months"]})
        x = seg(d, *G.H3.PERIODS[per]) if hasattr(G, "H3") else None
    ho = seg(d, "2025-01-01", "2026-08-01"); isv = seg(d, "2020-07-01", "2025-01-01"); iso = seg(d, "2020-07-01", "2023-07-01")
    s, se = sr_se(ho)
    row["HO_sr_all"] = round(s * np.sqrt(260), 2); row["HO_sr_se"] = round(se * np.sqrt(260), 2)
    row["HO_t"] = round(ho.mean() / ho.std() * np.sqrt(len(ho)), 2)
    s2, se2 = sr_se(isv); row["ISVAL_sr"] = round(s2 * np.sqrt(260), 2); row["ISVAL_sr_se"] = round(se2 * np.sqrt(260), 2)
    row["ISVAL_t"] = round(isv.mean() / isv.std() * np.sqrt(len(isv)), 2)
    row["DSR_IS_N547"] = round(dsr(iso, V_is, N_UNIQ)[0], 3)
    row["DSR_ISVAL_N547"] = round(dsr(isv, V_iv, N_UNIQ)[0], 3)
    row["PSR_HO_0"] = round(norm.cdf(s / se), 3)
    row["DSR_HO_N10"] = round(dsr(ho, tri.sr_isval_daily.var(), 10)[0], 3)
    rows.append(row)
out = pd.DataFrame(rows)
print("SR0 IS (N=547): %.3f ann; SR0 IS+VAL: %.3f ann" % (dsr(iso, V_is, N_UNIQ)[1] * np.sqrt(260), dsr(isv, V_iv, N_UNIQ)[1] * np.sqrt(260)))
out.to_csv(f"{G.HERE}/final_top10.csv", index=False)
pd.set_option("display.width", 250)
c1 = ["name"] + [f"{p}_{k}" for p in ("IS", "VAL", "HOLDOUT") for k in ("sr", "ret", "dd", "gd")]
print(out[c1].to_string(index=False))
print(out[["name", "HOLDOUT_gm", "HO_sr_all", "HO_sr_se", "HO_t", "ISVAL_sr", "ISVAL_sr_se", "ISVAL_t", "DSR_IS_N547", "DSR_ISVAL_N547", "PSR_HO_0", "DSR_HO_N10"]].to_string(index=False))
