"""Item 1: significance of each candidate. Per-trade R: mean, t, iid-bootstrap 95% CI.
Daily P&L (R, booked on exit day, 0 on weekdays without exits): mean, Newey-West t, stationary-bootstrap CI,
annualised Sharpe, PSR(0), DSR with each family's trial count (on IS = the selection sample) and with the
all-families total. RC / SPA vs the always-long benchmark with the same exits (stationary bootstrap),
per candidate and jointly. Alpha vs gold's daily return (HAC t of intercept)."""
import numpy as np, pandas as pd, json
import hlib as L

D = pd.read_parquet(f"{L.SCR}/daily.parquet"); D.index = pd.to_datetime(D.index)
TR = {k: pd.read_parquet(f"{L.SCR}/trades_{k}.parquet") for k in D.columns}
TRIALS = {"A": 641368, "B": 7109, "D": 180000, "E": 11156, "F": 632940, "C": 300}
ALL = sum(TRIALS.values())
CANDS = {"A1": ("A", "A1_long"), "E1": ("E", "E1_long"), "E2": ("E", "E2_long"), "E3": ("E", "E3_long"),
         "C1": ("C", "C1_long")}
# gold daily return (close-to-close, %), same calendar
import sys; sys.path.insert(0, "/home/user/trading-bridge/research")
import harness as H
cl = H.load_m1().close.resample("1D").last().dropna()
gret = cl.pct_change().reindex(D.index).fillna(0.0) * 100

rows = []
for c, (fam, bench) in CANDS.items():
    for p in ("IS", "VAL", "HOLDOUT", "OOS"):
        t = L.sl_period(TR[c], p, "exit_t").R.values
        tb = L.sl_period(TR[bench], p, "exit_t").R.values
        d = L.sl_period(D[c], p).values; db = L.sl_period(D[bench], p).values; g = L.sl_period(gret, p).values
        ci_t = L.boot_ci(t, seed=1); ci_d = L.boot_ci(d, block=10, seed=2)
        sr = d.mean() / d.std(ddof=1)
        # alpha vs gold daily return, HAC t on intercept
        X = np.c_[np.ones_like(g), g]; beta = np.linalg.lstsq(X, d, rcond=None)[0]; res = d - X @ beta
        a_t = L.hac_t(beta[0] + res)
        r = dict(cand=c, period=p, n_tr=len(t), R_tr=round(t.mean(), 3), t_tr=round(L.tstat(t), 2),
                 ci_tr=f"[{ci_t[0]:.3f},{ci_t[1]:.3f}]", days=len(d), R_day=round(d.mean(), 3),
                 t_day_NW=round(L.hac_t(d), 2), ci_day=f"[{ci_d[0]:.3f},{ci_d[1]:.3f}]",
                 SR_ann=round(sr * np.sqrt(260), 2), PSR0=round(L.psr(d), 3),
                 bench_R_day=round(db.mean(), 3), bench_SR_ann=round(db.mean() / db.std(ddof=1) * np.sqrt(260), 2),
                 alpha_gold=round(beta[0], 3), beta_gold=round(beta[1], 3), t_alpha=round(a_t, 2))
        if p == "IS":
            r["DSR_fam"] = round(L.dsr(d, TRIALS[fam]), 4); r["DSR_all"] = round(L.dsr(d, ALL), 4)
            r["SR0_fam_ann"] = round(L.sr0_trials(TRIALS[fam], 1 / (len(d) - 1)) * np.sqrt(260), 2)
        prc, pspa = L.rc_spa(d - db, B=5000, block=10, seed=3)
        r["p_RC_vs_long"] = round(prc, 4); r["p_SPA_vs_long"] = round(pspa, 4)
        if c.startswith("E"):
            dl = L.sl_period(D[c + "_Lsame"], p).values
            r["p_SPA_vs_Lsame"] = round(L.rc_spa(d - dl, B=5000, block=10, seed=4)[1], 4)
        rows.append(r); print(r, flush=True)
df = pd.DataFrame(rows)
df.to_csv("s1_significance.csv", index=False)
# joint RC / SPA across all 5 candidates (each vs its own always-long benchmark)
joint = {}
for p in ("IS", "VAL", "HOLDOUT", "OOS"):
    M = np.column_stack([L.sl_period(D[c] - D[b], p).values for c, (_, b) in CANDS.items()])
    joint[p] = L.rc_spa(M, B=5000, block=10, seed=5)
    # also vs zero (absolute skill, not beyond the rally)
    M0 = np.column_stack([L.sl_period(D[c], p).values for c in CANDS])
    joint[p + "_vs0"] = L.rc_spa(M0, B=5000, block=10, seed=6)
print("JOINT (p_RC, p_SPA):", joint)
json.dump({k: [float(x) for x in v] for k, v in joint.items()}, open("s1_joint.json", "w"), indent=1)
pd.set_option("display.width", 300); pd.set_option("display.max_columns", 40)
print(df.to_string(index=False))
