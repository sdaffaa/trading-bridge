"""Stage 5 (FINAL, run once): HOLDOUT for the pre-registered finalists.
Singles = top-5 of s2_pool by the s2 score (IS+VAL). Portfolios = the 3 carried forward in s3 with the
IS-chosen daily management from s4 (which was: none). Nothing here feeds back into selection.
Also: drawdown / risk-of-ruin in % of account for risk per trade 0.25/0.5/1 %."""
import sys, json
import numpy as np, pandas as pd
sys.path.insert(0, "/home/user/trading-bridge/research/families/F_portfolio")
import common as C
import harness2 as H2
D = "/home/user/trading-bridge/research/families/F_portfolio/"
pd.set_option("display.width", 250); pd.set_option("display.max_colwidth", 200)
pool = pd.read_csv(D + "s2_pool.csv").set_index("name")
ports = json.load(open(D + "s3_ports.json")); chosen = json.load(open(D + "s3_chosen.json"))
mgmt = json.load(open(D + "s4_mgmt.json"))
assert all(v == {"lock_up": 0.0, "lock_dn": 0.0, "maxtr": 0.0, "eqmode": 0.0, "volexp": 0.0} for v in mgmt.values())
singles = list(pool.index[:5])
need = list(dict.fromkeys(singles + [n for p in chosen for n in ports[p]]))
TR, DAY = {}, {}
for n in need:
    tr = C.run_spec(json.loads(pool.loc[n, "spec"]), holdout=True)
    TR[n] = tr; DAY[n] = H2.daily(tr)
rng = np.random.default_rng(7)
PR = ("IS", "VAL", "HOLDOUT")


def risk_block(day, label):
    """day: daily R (days with exits). Compounded equity at r% risk per 1R."""
    out = []
    ivd = day[day.index < pd.Timestamp(H2.PERIODS["HOLDOUT"][0]).date()].values
    for r in (0.25, 0.5, 1.0):
        row = dict(item=label, risk=r)
        for p in PR:
            a, b = H2.PERIODS[p]
            x = day[(day.index >= pd.Timestamp(a).date()) & (day.index < pd.Timestamp(b).date())].values
            eq = np.cumprod(1 + r / 100 * x); row[f"{p}_ret%"] = round((eq[-1] - 1) * 100, 1)
            row[f"{p}_maxDD%"] = round(((eq / np.maximum.accumulate(np.r_[1.0, eq])[1:]) - 1).min() * 100, 1)
        # block bootstrap of IS+VAL daily R, 1-year paths (250 trading days w/ exits), block 20
        nb = 10000; L = 250; B = 20; dd = np.empty(nb)
        for k in range(nb):
            st = rng.integers(0, len(ivd) - B, L // B + 1)
            path = np.concatenate([ivd[s:s + B] for s in st])[:L]
            eq = np.cumprod(1 + r / 100 * path); dd[k] = ((eq / np.maximum.accumulate(np.r_[1.0, eq])[1:]) - 1).min()
        row["boot_medDD%"] = round(np.median(dd) * 100, 1); row["boot_p95DD%"] = round(np.percentile(dd, 5) * 100, 1)
        for th in (10, 20, 30, 50):
            row[f"P(DD>{th}%)"] = round((dd <= -th / 100).mean() * 100, 2)
        out.append(row)
    return out


rows, risk = [], []
def add(label, day, tr=None, members=None):
    st = C.day_stats(day)
    r = dict(item=label)
    for p in PR:
        s = st[p]
        r.update({f"{p}_totR": s["totR"], f"{p}_Rday": s["R_day"], f"{p}_gd%": s["green_days"],
                  f"{p}_gm%": s["green_months"], f"{p}_ddR": s["maxDD"], f"{p}_dd%@0.5": round(s["maxDD"] * 0.5, 1)})
    if tr is not None:
        hs = H2.stats(tr)
        for p in PR:
            r[f"{p}_n"] = hs[p]["n"]; r[f"{p}_PF"] = hs[p]["PF"]
        h = tr[tr.exit_t >= H2.PERIODS["HOLDOUT"][0]]
        r["HO_long_R"] = round(h.R[h.side > 0].sum(), 1); r["HO_short_R"] = round(h.R[h.side < 0].sum(), 1)
    r["credible"] = all(st[p]["totR"] > 0 for p in PR)
    rows.append(r); risk.extend(risk_block(day, label))

for i, n in enumerate(singles):
    add(f"S{i+1}", DAY[n], TR[n])
for p in chosen:
    day = pd.concat([DAY[n] for n in ports[p]], axis=1).fillna(0).sum(axis=1).sort_index()   # concat of object (date) indexes is unsorted
    tr = pd.concat([TR[n] for n in ports[p]])
    add(f"P_{p}", day, tr)

res = pd.DataFrame(rows); rk = pd.DataFrame(risk)
print(res.T.to_string()); print(); print(rk.to_string(index=False))
res.to_csv(D + "s5_final.csv", index=False); rk.to_csv(D + "s5_risk.csv", index=False)
print("\nlegend:"); [print(f"S{i+1} = {n}") for i, n in enumerate(singles)]
for p in chosen:
    print(f"P_{p}:"); [print("   ", n) for n in ports[p]]
