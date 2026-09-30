"""Family 5a: intraday seasonality statistics on IS only (2020-07..2023-06).
Hypotheses: 23 NY hours, 4 sessions, 5 weekdays, overnight vs COMEX-day, 4 London-fix windows.
t-stats use HAC (Newey-West, 5 lags) on the per-period log returns; BH-FDR across all hypotheses."""
import numpy as np, pandas as pd
import statsmodels.api as sm
from statsmodels.stats.multitest import multipletests
import common as G, harness3 as H3

a, b = G.PER["IS"]


def tt(x):
    x = pd.Series(x).dropna()
    m = sm.OLS(x.values, np.ones(len(x))).fit(cov_type="HAC", cov_kwds={"maxlags": 5})
    return x.mean(), m.tvalues[0], m.pvalues[0], len(x)


rows = []
r = G.LR[(G.C.index >= a) & (G.C.index < b)]
h = G.NY_HOUR.reindex(r.index)
for hr in sorted(h.unique()):
    rows.append(("hour", f"NY{hr:02d}", *tt(r[h == hr])))
sess = {"Asia 18-02": list(range(18, 24)) + [0, 1], "London 02-08": list(range(2, 8)),
        "NY-AM 08-12": list(range(8, 12)), "NY-PM 12-17": list(range(12, 17))}
td = G.TDAY.reindex(r.index)
for s, hs in sess.items():
    x = r[h.isin(hs)].groupby(td[h.isin(hs)].values).sum()
    rows.append(("session", s, *tt(x)))
dr = r.groupby(td.values).sum(); dr.index = pd.to_datetime(dr.index)
for wd in range(5):
    rows.append(("weekday", ["Mon", "Tue", "Wed", "Thu", "Fri"][wd], *tt(dr[dr.index.weekday == wd])))
day = h.isin(range(8, 14))
for nm, msk in (("COMEX-day 08-14", day), ("overnight 14-08", ~day)):
    x = r[msk].groupby(td[msk].values).sum(); rows.append(("on/id", nm, *tt(x)))
# London fixes on 30m bars (HistData clock = NY local + 5h in IS)
b30 = H3.bars("30min"); b30 = b30[(b30.index >= a - pd.Timedelta(days=3)) & (b30.index < b)]
ny = pd.DatetimeIndex(b30.index - pd.Timedelta(hours=5)).tz_localize("America/New_York", ambiguous="NaT", nonexistent="NaT")
ldn = ny.tz_convert("Europe/London")
lr30 = np.log(b30.close).diff()
lmin = pd.Series(ldn.hour * 60 + ldn.minute, index=b30.index)
dkey = pd.Series(ldn.normalize().tz_localize(None), index=b30.index)
for fix, fm in (("AM 10:30", 630), ("PM 15:00", 900)):
    for w, lo, hi in (("pre60", fm - 60, fm), ("post60", fm, fm + 60)):
        msk = (lmin >= lo) & (lmin < hi) & (b30.index >= a)
        x = lr30[msk].groupby(dkey[msk].values).sum(); rows.append(("fix", f"{fix} {w}", *tt(x)))
df = pd.DataFrame(rows, columns=["group", "effect", "mean", "t", "p", "n"])
df["mean_bp"] = (df["mean"] * 1e4).round(2)
for q in (0.05, 0.10):
    df[f"BH{int(q*100)}"] = multipletests(df.p, alpha=q, method="fdr_bh")[0]
df = df.drop(columns="mean"); df["t"] = df.t.round(2); df["p"] = df.p.round(4)
df.to_csv(f"{G.HERE}/g5_season_stats.csv", index=False)
print(df.sort_values("p").to_string(index=False))
print("hypotheses:", len(df), "significant BH10:", int(df.BH10.sum()), "BH5:", int(df.BH5.sum()))
