"""Item 2: Probability of Backtest Overfitting (CSCV, Bailey-Borwein-Lopez de Prado-Zhu 2015).
Builds T x N daily-R matrices (harness2.run, R booked on exit day, 0 on weekdays w/o exits) for
  E_top  : 200 best family-E variants by IS totR (s1+s2 screens, IS n>=150)   -> the pool finalists came from
  E_rand : 200 random family-E variants (s1+s2, IS n>=150)                      -> representative of the search
  A_top  : family-A top-50 (top50_is_val.csv)
  A_mix  : A top-50 + 150 random MTF combos with IS n>=300
CSCV with S=16 on IS+VAL days (the data used for selection) and, for information, on all days.
Also: cross-sectional variance of IS daily Sharpe (for DSR with empirical V[SR])."""
import sys, time, numpy as np, pandas as pd, json, importlib.util
R = "/home/user/trading-bridge/research"
for p in (R, R + "/solution", R + "/families/A_indicators"):
    sys.path.insert(0, p)
import harness as H, harness2 as H2, hlib as L
def load(name, path):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp)
    sys.modules[name] = m; sp.loader.exec_module(m); return m
sys.path.insert(0, R + "/families/E_profit"); import common as EC
m1 = H.load_m1(); IDX = m1.index; START = IDX >= pd.Timestamp(H.PERIODS["IS"][0])
D0 = pd.read_parquet(f"{L.SCR}/daily.parquet"); days = D0.index
t0 = time.time()

def daily_of(tr):
    return H2.daily(tr).reindex(days).fillna(0.0).values

# ---------------- family E
e = pd.concat([pd.read_parquet(R + "/families/E_profit/s1_is.parquet"), pd.read_parquet(R + "/families/E_profit/s2_is.parquet")])
e = e[e.IS_n >= 150].drop_duplicates(["name", "slmode", "slk", "tpr", "trk", "mb", "filt"])
print("E pool", len(e), flush=True)
top = e.sort_values("IS_totR", ascending=False).head(200)
rnd = e.drop(top.index, errors="ignore").sample(200, random_state=0)
REG = EC.registry()
def e_col(r):
    trk = None if pd.isna(r.trk) else r.trk; tpr = None if pd.isna(r.tpr) else r.tpr
    d, s, tp, trl, mb = EC.build(r["name"], r.slmode, r.slk, tpr, trk, int(r.mb), r.filt, REG)
    return daily_of(H2.run(np.where(START, d, 0.0), s, tp, trl, mb))
mats = {}
for nm, df in (("E_top", top), ("E_rand", rnd)):
    cols = []
    for k, (_, r) in enumerate(df.iterrows()):
        cols.append(e_col(r))
        if k % 50 == 0: print(nm, k, round(time.time() - t0), flush=True)
    mats[nm] = np.column_stack(cols)
    np.save(f"{L.SCR}/pbo_{nm}.npy", mats[nm])
    EC._EC.clear()

# ---------------- family A
import validate_lib as V
a50 = pd.read_csv(R + "/families/A_indicators/top50_is_val.csv")
mtf = pd.read_parquet(R + "/families/A_indicators/mtf_is.parquet")
mtf = mtf[(mtf.n >= 300) & mtf.dist.isin(list(V.R.keys()))]
arnd = mtf.sample(150, random_state=0)
def a_col(combo, inv, dist):
    d = V.dirs_of(combo); d = (-d if inv else d).astype(np.float64); d[~START] = 0
    sl = np.asarray(V.R[dist], float)
    return daily_of(H2.run(d, sl, sl))
A_top = np.column_stack([a_col(r.combo, r.inv, r.dist) for _, r in a50.iterrows()])
print("A_top done", round(time.time() - t0), flush=True)
A_r = np.column_stack([a_col(r.combo, r.inv, r.dist) for _, r in arnd.iterrows()])
mats["A_top"] = A_top; mats["A_mix"] = np.column_stack([A_top, A_r])
np.save(f"{L.SCR}/pbo_A_mix.npy", mats["A_mix"])
print("A done", round(time.time() - t0), flush=True)

isv = np.asarray((pd.to_datetime(days) < pd.Timestamp("2025-01-01")))
is_ = np.asarray((pd.to_datetime(days) < pd.Timestamp("2023-07-01")))
out = {}
for nm, M in mats.items():
    keep = M.std(0) > 0; M = M[:, keep]
    res = {}
    for lab, mask in (("IS+VAL", isv), ("ALL", np.ones(len(days), bool))):
        pbo, lam, perf = L.cscv_pbo(M[mask], S=16)
        slope = np.polyfit(perf[:, 0], perf[:, 1], 1)[0]
        res[lab] = dict(PBO=round(pbo, 3), median_logit=round(float(np.median(lam)), 3),
                        mean_IS_best_SR_ann=round(perf[:, 0].mean() * np.sqrt(260), 2),
                        mean_OOS_SR_ann_of_IS_best=round(perf[:, 1].mean() * np.sqrt(260), 2),
                        P_OOS_SR_lt0=round((perf[:, 1] < 0).mean(), 3), slope_OOS_on_IS=round(slope, 3))
    sr_is = M[is_].mean(0) / M[is_].std(0, ddof=1)
    res["N"] = int(M.shape[1]); res["var_SR_IS_daily"] = float(np.var(sr_is, ddof=1))
    res["mean_SR_IS_ann"] = round(float(sr_is.mean() * np.sqrt(260)), 3)
    out[nm] = res; print(nm, res, flush=True)
json.dump(out, open("s2_pbo.json", "w"), indent=1)

# DSR with empirical cross-sectional V[SR] (random pools = representative of the search)
D0.index = pd.to_datetime(D0.index)
TR = {"A": 641368, "E": 11156}
dsr = {}
for c, fam, pool in (("A1", "A", "A_mix"), ("E1", "E", "E_rand"), ("E2", "E", "E_rand"), ("E3", "E", "E_rand")):
    x = L.sl_period(D0[c], "IS").values
    v = out[pool]["var_SR_IS_daily"]
    dsr[c] = dict(DSR_emp=round(float(L.dsr(x, TR[fam], v)), 4),
                  SR0_emp_ann=round(float(L.sr0_trials(TR[fam], v) * np.sqrt(260)), 2),
                  DSR_emp_N100=round(float(L.dsr(x, 100, v)), 4))
print("DSR empirical V[SR]:", dsr)
json.dump(dsr, open("s2_dsr_emp.json", "w"), indent=1)
print("total", round(time.time() - t0))
