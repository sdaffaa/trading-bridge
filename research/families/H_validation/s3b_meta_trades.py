"""Item 3b: meta-labelling on the EA's ACTUAL consecutive trades (primary = A1 trade sequence from harness2).
Skip = stay flat for that trade's lifetime (the primary sequence is unchanged, so P&L of the filtered EA =
sum of R of taken trades; identical to harness2 with waiting). Features = family-C 1h feature row of the last
completed H1 bar before entry + side + minutes since H1 close + outcome of the previous 1/3/10 EA trades
(known at entry since consecutive: previous trade exited on the previous bar).
Purged 6-fold CV inside IS (1-day embargo) -> threshold; final model on all IS trades -> VAL/HOLDOUT."""
import sys, numpy as np, pandas as pd, lightgbm as lgb, warnings, json
from scipy.stats import norm
from sklearn.metrics import roc_auc_score
warnings.filterwarnings("ignore")
sys.path.insert(0, "/home/user/trading-bridge/research")
import harness2 as H2, hlib as L
tr = pd.read_parquet(f"{L.SCR}/trades_A1.parquet").reset_index(drop=True)
X = pd.read_parquet("/tmp/claude-0/-home-user-trading-bridge/b109c4cd-e10b-5fab-96f6-d6f544632108/scratchpad/C_ml/feat_1h.parquet")
close_t = X.index + pd.Timedelta("1h")
k = close_t.searchsorted(tr.t, side="right") - 1          # last H1 bar CLOSED at or before entry
F = X.iloc[k].reset_index(drop=True).copy()
F["side"] = tr.side.values; F["mins_since"] = (tr.t.values - close_t[k].values) / np.timedelta64(1, "m")
w = (tr.R > 0).astype(float)
for n in (1, 3, 10): F[f"prev{n}"] = w.shift(1).rolling(n).mean().values
y = w.values.astype(int)
IS1 = pd.Timestamp("2023-07-01")
per = np.where(tr.t < IS1, "IS", np.where(tr.t < pd.Timestamp("2025-01-01"), "VAL", "HOLDOUT"))
P = dict(n_estimators=200, learning_rate=0.02, num_leaves=7, min_child_samples=60, subsample=0.7, subsample_freq=1,
         colsample_bytree=0.5, reg_lambda=10, n_jobs=2, verbose=-1, random_state=0)
isr = np.where(per == "IS")[0]; oof = np.full(len(y), np.nan)
for f in np.array_split(isr, 6):
    a, z = tr.t[f[0]], tr.exit_t[f].max()
    trn = isr[~np.isin(isr, f)]
    ov = (tr.exit_t.values[trn] >= a) & (tr.t.values[trn] <= z + pd.Timedelta("1D"))
    trn = trn[~ov]
    oof[f] = lgb.LGBMClassifier(**P).fit(F.iloc[trn], y[trn]).predict_proba(F.iloc[f])[:, 1]
fin = isr[tr.exit_t.values[isr] < IS1]
p = oof.copy(); o = per != "IS"; p[o] = lgb.LGBMClassifier(**P).fit(F.iloc[fin], y[fin]).predict_proba(F[o])[:, 1]
auc = {q: round(roc_auc_score(y[per == q], p[per == q]), 4) for q in ("IS", "VAL", "HOLDOUT")}
print("AUC", auc)
best = None
for th in (0.45, 0.48, 0.50, 0.52, 0.54, 0.56):
    m = (per == "IS") & (p > th); tot = tr.R[m].sum()
    print(f" IS-OOF th={th}: n={m.sum()} totR={tot:.1f}")
    if m.sum() >= 300 and (best is None or tot > best[1]): best = (th, tot)
th = best[0]
sz = np.clip(2 * norm.cdf((p - 0.5) / np.sqrt(p * (1 - p))) - 1, 0, None); sz = sz / sz[(per == "IS") & (p > 0.5)].mean()
rows = []
for name, R in (("EA all trades", tr.R.values), (f"meta p>{th}", np.where(p > th, tr.R, 0.0)),
                ("meta LdP bet size", np.where(p > 0.5, tr.R * sz, 0.0))):
    t2 = tr.assign(R=R)[R != 0]
    st = H2.stats(t2); print(H2.fmt(name, st))
    for q, v in st.items(): rows.append(dict(variant=name, period=q, **v))
pd.DataFrame(rows).to_csv("s3b_meta_trades.csv", index=False)
json.dump(dict(auc=auc, th=th), open("s3b_meta_trades.json", "w"))
