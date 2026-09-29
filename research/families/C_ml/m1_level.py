"""Decision at the exact M1 bar (the bar right after a previous exit): features = last completed
M5-bar feature set (multi-TF, levels, time) + M1 micro-structure (last M1 returns / candles scaled
by the stop distance, position in current M5/M15 bar). Trained on a random 1-in-SUB sample of M1
bars (labels = trade_once both ways at that bar), predicted at every M1 bar -> run_consecutive.
usage: python m1_level.py spec1;spec2 [SUB]"""
import sys, time, warnings, numpy as np, pandas as pd, lightgbm as lgb
warnings.filterwarnings("ignore")
import common as C, harness as H, ml_run as R

m1 = H.load_m1()
st0 = m1.index.searchsorted(C.START - pd.Timedelta("10D"))
M = m1.iloc[st0:]
b5, X5 = C.build_dataset("5min")
keep = [c for c in X5.columns]
# align M5 features to M1 (value of last completed M5 bar)
A = X5.copy(); A.index = A.index + pd.Timedelta("5min")
F = A.reindex(M.index, method="ffill").astype(np.float32)
o, h, l, c = (M[k].values for k in ("open", "high", "low", "close"))
a5 = H.htf_to_m1(H.atr(H.bars("5min"), 14), "5min")[st0:]
def sh(x, k): return np.r_[np.full(k, np.nan), x[:-k]]
for k in (1, 2, 3, 5, 10, 20, 30, 60):
    F[f"m1ret{k}"] = ((sh(c, 1) - sh(c, k + 1)) / a5).astype(np.float32)
for k in (1, 2, 3):
    F[f"m1body{k}"] = ((sh(c, k) - sh(o, k)) / a5).astype(np.float32)
    F[f"m1uw{k}"] = ((sh(h, k) - np.maximum(sh(o, k), sh(c, k))) / a5).astype(np.float32)
    F[f"m1lw{k}"] = ((np.minimum(sh(o, k), sh(c, k)) - sh(l, k)) / a5).astype(np.float32)
F["m1gap"] = ((o - sh(c, 1)) / a5).astype(np.float32)          # current bar open is known at entry
F["min5"] = (M.index.minute % 5).astype(np.float32); F["min15"] = (M.index.minute % 15).astype(np.float32)
F["m1since5"] = ((o - H.htf_to_m1(H.bars("5min").close, "5min")[st0:]) / a5).astype(np.float32)
hh = pd.Series(h).rolling(30).max().shift(1).values; ll = pd.Series(l).rolling(30).min().shift(1).values
F["m1pos30"] = ((o - ll) / (hh - ll)).astype(np.float32)
F = F.replace([np.inf, -np.inf], np.nan)
feats = list(F.columns)
print("features", F.shape, flush=True)

def run(spec, SUB=5):
    dist = C.dist_m1(spec)[st0:]
    fu = np.arange(len(M)); rng = np.random.default_rng(1)
    samp = np.sort(rng.choice(fu, len(M) // SUB, replace=False))
    samp = samp[M.index[samp] >= C.START]
    yL, yS, eL, eS = C.label_both(m1.open.values, m1.high.values, m1.low.values, (samp + st0).astype(np.int64), dist[samp], H.SPREAD)
    okr = (yL != 0) & (yS != 0)
    samp, yL, yS, eL, eS = samp[okr], yL[okr], yS[okr], eL[okr], eS[okr]
    idx = M.index[samp]; e = np.maximum(eL, eS)
    pr_all = np.full(len(M), np.nan)
    Xs = F.values[samp]
    for bi, tr, te in C.folds(idx, samp + st0, e):
        trm = tr & (yL != yS)
        m = R.make_model("lgb"); m.set_params(n_estimators=300, min_child_samples=1000)
        m.fit(Xs[trm], (yL[trm] > 0).astype(int))
        a, z = pd.Timestamp(C.BLOCKS[bi][0]), pd.Timestamp(C.BLOCKS[bi][1])
        rows = np.flatnonzero((M.index >= a) & (M.index < z))
        pr_all[rows] = m.predict_proba(F.values[rows])[:, 1]
    dirs = np.full(len(m1), np.nan); dirs[st0:] = np.where(np.isnan(pr_all), np.nan, np.where(pr_all >= .5, 1., -1.))
    dirs[:m1.index.searchsorted(C.START)] = np.nan
    st = H.stats(H.run_consecutive(dirs, C.dist_m1(spec)))
    name = f"lgb_M1level|1min|{C.spec_name(spec)}"
    print(H.fmt(name, st), "| passes", H.passes(st), flush=True)
    with open("/home/user/trading-bridge/research/families/C_ml/results_raw.tsv", "a") as f:
        f.write("\t".join([name] + [f"{p}:n={st[p].get('n')},wr={st[p].get('wr')}" for p in st] + [f"passes={H.passes(st)}"]) + "\n")
    np.save(f"{C.CACHE}/m1prob_{C.spec_name(spec)}.npy", pr_all)

if __name__ == "__main__":
    SUB = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    for s in sys.argv[1].split(";"):
        t = time.time(); run(R.parse(s), SUB); print("  time", round(time.time() - t), flush=True)
