"""Stage 3: portfolios of weakly-correlated candidates (pool = s2 candidates, which passed IS-rank + VAL filter).
Each strategy trades one position at a time, 1R risk per trade, portfolio daily R = sum of strategy daily R.
Methods (HOLDOUT masked):
  A  score order (s2 score), accept if IS daily corr < 0.5 with every member
  B  greedy: add the member that maximises IS daily Sharpe of the sum, corr < 0.3
  C  greedy on IS+VAL daily Sharpe, corr < 0.3
sizes 3, 5, 10. The 3 portfolios carried forward = best 3 by min(IS Sharpe, VAL Sharpe) (VAL is OOS for A/B)."""
import sys, json
import numpy as np, pandas as pd
sys.path.insert(0, "/home/user/trading-bridge/research/families/F_portfolio")
import common as C
import harness2 as H2
D = "/home/user/trading-bridge/research/families/F_portfolio/"
pd.set_option("display.width", 250)
pool = pd.read_csv(D + "s2_pool.csv")
dl = pd.read_parquet(D + "s2_pool_daily.parquet")
dl.index = pd.to_datetime(dl.index).date
bdays = pd.bdate_range(H2.PERIODS["IS"][0], H2.PERIODS["HOLDOUT"][0], inclusive="left").date
dl = dl.reindex(sorted(set(bdays) | set(dl.index))).fillna(0.0)     # zero on no-exit days (for corr/Sharpe)
isd = dl[(dl.index < pd.Timestamp(H2.PERIODS["VAL"][0]).date())]
ivd = dl
names = list(pool.name)
corr = isd[names].corr()


def sharpe(x): return x.mean() / x.std() * np.sqrt(252) if x.std() > 0 else -9


def greedy(k, data, cmax):
    sel = [names[0]]
    while len(sel) < k:
        best, bv = None, -1e9
        for n in names:
            if n in sel or any(corr.loc[n, s] >= cmax for s in sel):
                continue
            v = sharpe(data[sel + [n]].sum(axis=1))
            if v > bv:
                best, bv = n, v
        if best is None:
            break
        sel.append(best)
    return sel


def score_order(k, cmax):
    sel = []
    for n in names:
        if all(corr.loc[n, s] < cmax for s in sel):
            sel.append(n)
        if len(sel) == k:
            break
    return sel


ports = {}
for k in (3, 5, 10):
    ports[f"A{k}"] = score_order(k, 0.5)
    ports[f"B{k}"] = greedy(k, isd, 0.3)
    ports[f"C{k}"] = greedy(k, ivd, 0.3)
rows = []
for pn, mem in ports.items():
    day = dl[mem].sum(axis=1); day = day[day != 0]
    st = C.day_stats(day, ("IS", "VAL"))
    c = corr.loc[mem, mem].values; mc = c[np.triu_indices(len(mem), 1)].mean() if len(mem) > 1 else np.nan
    rows.append(dict(port=pn, k=len(mem), mean_corr=round(mc, 3),
                     **{f"{p}_{kk}": st[p][kk] for p in ("IS", "VAL") for kk in ("totR", "R_day", "green_days", "maxDD", "green_months", "sharpe_d")}))
r = pd.DataFrame(rows); r["minSh"] = r[["IS_sharpe_d", "VAL_sharpe_d"]].min(axis=1)
print(r.to_string(index=False))
# single strategies for reference (days with exits only, like harness2.daily)
chosen = r.sort_values("minSh", ascending=False).head(3).port.tolist()
print("\ncarried forward:", chosen)
for pn in chosen:
    print(pn, *ports[pn], sep="\n   ")
json.dump({pn: ports[pn] for pn in ports}, open(D + "s3_ports.json", "w"), indent=1)
json.dump(chosen, open(D + "s3_chosen.json", "w"))
r.to_csv(D + "s3_ports.csv", index=False)
