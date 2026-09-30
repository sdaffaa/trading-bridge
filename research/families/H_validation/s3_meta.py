"""Item 3: meta-labelling (Lopez de Prado, AFML ch.3) on the current EA signal.
Primary model = family-A combo #1 direction (d, causal on every M1 bar).
Events = first M1 bar after each completed H1 bar (IS..HOLDOUT) where d != 0.
Triple barrier = the EA's own barriers: TP = SL = 3 x ATR(H1), no vertical barrier (harness2 logic, spread,
SL-first when both in one bar). Meta label y = 1 if the primary trade wins.
Secondary = LightGBM classifier on causal H1 features (family C feature set, 1h) + primary side.
Purged K-fold (6 contiguous folds inside IS, training rows whose [entry, exit] overlaps the test span are
purged, 1-day embargo after the test span). Threshold and sizing rule chosen on IS out-of-fold only.
Final model trained on ALL IS events (exit before IS end) and applied unchanged to VAL and HOLDOUT.
Evaluation: harness2.run (one position at a time, waiting allowed), dirs non-zero only at taken events."""
import sys, numpy as np, pandas as pd, lightgbm as lgb, json, warnings
from numba import njit
from scipy.stats import norm
warnings.filterwarnings("ignore")
R = "/home/user/trading-bridge/research"
sys.path.insert(0, R)
import harness as H, harness2 as H2, hlib as L

m1 = H.load_m1(); IDX = m1.index; N = len(m1)
o, h, l, c = (m1[k].values.astype(np.float64) for k in ("open", "high", "low", "close"))
d = np.load(f"{L.SCR}/A1_dirs.npy"); sl = np.load(f"{L.SCR}/A1_sl.npy")
X = pd.read_parquet("/tmp/claude-0/-home-user-trading-bridge/b109c4cd-e10b-5fab-96f6-d6f544632108/scratchpad/C_ml/feat_1h.parquet")
IS0, IS1 = pd.Timestamp("2020-07-01"), pd.Timestamp("2023-07-01")


@njit(cache=True)
def barrier(o, h, l, idx, dirs, sl, spread):
    n = len(o); m = len(idx); y = np.zeros(m); ex = np.full(m, n, np.int64)
    for k in range(m):
        i = idx[k]; dd = dirs[k]; s = sl[k]
        if dd > 0:
            e = o[i] + spread
            for j in range(i, n):
                if l[j] <= e - s: y[k] = -1; ex[k] = j; break
                if h[j] >= e + s: y[k] = 1; ex[k] = j; break
        else:
            e = o[i]
            for j in range(i, n):
                if h[j] + spread >= e + s: y[k] = -1; ex[k] = j; break
                if l[j] + spread <= e - s: y[k] = 1; ex[k] = j; break
    return y, ex


# ---- events
X = X[(X.index >= IS0 - pd.Timedelta("1h")) & (X.index < pd.Timestamp("2026-08-01"))]
idx = IDX.searchsorted(X.index + pd.Timedelta("1h"))
ok = idx < N; X = X[ok]; idx = idx[ok]
side = d[idx]; s_ = sl[idx]
keep = (side != 0) & (s_ > 0); X = X[keep]; idx = idx[keep]; side = side[keep]; s_ = s_[keep]
y, ex = barrier(o, h, l, idx.astype(np.int64), side, s_, H.SPREAD)
keep = y != 0; X = X[keep]; idx = idx[keep]; side = side[keep]; y = (y[keep] > 0).astype(int); ex = ex[keep]
X = X.copy(); X["side"] = side
t = IDX[idx]; te_ = IDX[np.minimum(ex, N - 1)]
per = np.where(t < IS1, "IS", np.where(t < pd.Timestamp("2025-01-01"), "VAL", "HOLDOUT"))
print("events", pd.Series(per).value_counts().to_dict(), "IS base win rate", round(y[per == "IS"].mean(), 4), flush=True)

P = dict(n_estimators=300, learning_rate=0.02, num_leaves=15, min_child_samples=300, subsample=0.7,
         subsample_freq=1, colsample_bytree=0.5, reg_lambda=10, n_jobs=2, verbose=-1, random_state=0)

# ---- purged K-fold OOF inside IS
isr = np.where(per == "IS")[0]
oof = np.full(len(y), np.nan)
folds = np.array_split(isr, 6)
emb = pd.Timedelta("1D")
for f in folds:
    a, z = t[f[0]], te_[f].max()
    trn = isr[~np.isin(isr, f)]
    # purge: drop training events whose [t, exit] overlaps [a, z + embargo]
    ov = (te_[trn] >= a) & (t[trn] <= z + emb)
    trn = trn[~ov & (te_[trn] < IS1)]
    m = lgb.LGBMClassifier(**P).fit(X.iloc[trn], y[trn])
    oof[f] = m.predict_proba(X.iloc[f])[:, 1]
print("IS OOF AUC", round(__import__("sklearn.metrics", fromlist=["x"]).roc_auc_score(y[isr], oof[isr]), 4), flush=True)

# ---- final model: all IS events that exited before IS end
fin = isr[te_[isr] < IS1]
mf = lgb.LGBMClassifier(**P).fit(X.iloc[fin], y[fin])
p = oof.copy(); oos = per != "IS"; p[oos] = mf.predict_proba(X[oos])[:, 1]
from sklearn.metrics import roc_auc_score
auc = {q: round(roc_auc_score(y[per == q], p[per == q]), 4) for q in ("IS", "VAL", "HOLDOUT")}
print("AUC (IS=OOF, VAL/HO=final model):", auc, flush=True)


def sim(take, size=None):
    dirs = np.zeros(N); dirs[idx[take]] = side[take]
    tr = H2.run(dirs, sl, sl)
    if size is not None:
        sz = np.zeros(N); sz[idx[take]] = size[take]
        tr["R"] = tr.R * sz[IDX.get_indexer(tr.t)]
    return tr


def bet_size(pp):
    z = (pp - 0.5) / np.sqrt(pp * (1 - pp))
    return np.clip(2 * norm.cdf(z) - 1, 0, None)


rows = []
def rep(name, tr):
    st = H2.stats(tr)
    for q, v in st.items():
        rows.append(dict(variant=name, period=q, **{k: v.get(k) for k in ("n", "totR", "R_trade", "wr", "PF", "green_days", "maxDD", "green_months")}))
    print(H2.fmt(name, st), flush=True)
    return st

rep("EA consecutive (original)", H2.run(d, sl, sl))
base = rep("primary @H1 events, take all", sim(np.ones(len(y), bool)))
# threshold chosen on IS OOF only (IS totR of the harness simulation restricted to IS)
best = None
for th in (0.50, 0.52, 0.54, 0.56, 0.58, 0.60):
    tk = (p > th) & (per == "IS")
    st = H2.stats(sim(tk), ("IS",))["IS"]
    print(f"  IS-OOF th={th}: n={st.get('n')} totR={st.get('totR')} R/t={st.get('R_trade')}", flush=True)
    if st.get("n", 0) >= 200 and (best is None or st["totR"] > best[1]): best = (th, st["totR"])
th = best[0]; print("chosen threshold (IS OOF):", th, flush=True)
rep(f"meta filter p>{th}", sim(p > th))
sz = bet_size(p); norm_ = sz[(per == "IS") & (p > 0.5)].mean()
rep("meta filter p>0.5 + LdP bet size (IS-normalised)", sim(p > 0.5, sz / norm_))
rep(f"meta filter p>{th} + LdP bet size", sim(p > th, sz / norm_))
df = pd.DataFrame(rows); df.to_csv("s3_meta.csv", index=False)
json.dump(dict(auc=auc, threshold=th, events=pd.Series(per).value_counts().to_dict()), open("s3_meta.json", "w"), indent=1)

# significance of the meta improvement (daily difference vs take-all, stationary bootstrap SPA)
days = pd.read_parquet(f"{L.SCR}/daily.parquet").index
dA = H2.daily(sim(np.ones(len(y), bool))).reindex(days).fillna(0); dM = H2.daily(sim(p > th)).reindex(days).fillna(0)
dA.index = pd.to_datetime(dA.index); dM.index = pd.to_datetime(dM.index)
for q in ("VAL", "HOLDOUT", "OOS"):
    diff = (L.sl_period(dM, q) - L.sl_period(dA, q)).values
    print(q, "meta - takeall daily mean", round(diff.mean(), 4), "NW t", round(L.hac_t(diff), 2), "SPA p", L.rc_spa(diff, 3000)[1])
