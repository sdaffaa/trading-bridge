"""Diagnostics for the best profit candidate (lgb_reg 1h tp1.5 both th=0):
(1) side mix and ATR level of taken trades; (2) cost-filter baselines: random side / always-long /
always-short at H1 decision bars, only when ATR(H1) is above its IS-only quantile; (3) seed robustness."""
import numpy as np, pandas as pd, lightgbm as lgb, common as C, harness as H, harness2 as H2, profit as P
m1 = H.load_m1(); a1h = H.htf_to_m1(H.atr(H.bars("1h"), 14), "1h")
g = [x for x in P.GEOMS if x[0] == "tp1.5"][0]; sl, tp, tr, mb = P.geom_arrays(g, a1h)
b, L, Pr = P.oof("1h", g, "reg")
dirs = P.trade_dirs(b, "1h", L, Pr, 0.0, "both"); sig = dirs[L.i.values]
A = a1h[L.i.values]
print("model trades: long share", round((sig > 0).sum() / max((sig != 0).sum(), 1), 3),
      "| median ATR1h taken", round(np.nanmedian(A[sig != 0]), 2), "vs all", round(np.nanmedian(A), 2))
isA = A[(L.index < C.IS_END)]
rng = np.random.default_rng(3)
for q in (0.5, 0.75, 0.9):
    thr = np.nanquantile(isA, q)
    for nm in ("long", "short", "random"):
        d = np.zeros(len(m1)); m = A > thr
        v = np.ones(m.sum()) if nm == "long" else -np.ones(m.sum()) if nm == "short" else rng.choice([-1., 1.], m.sum())
        d[L.i.values[m]] = v
        print(H2.fmt(f"ATR>{q}q({thr:.2f}) {nm}", H2.stats(H2.run(d, sl, tp, tr, mb))), flush=True)
# seed robustness: refit with different seeds / colsample
b, X = C.build_dataset("1h"); D = X.loc[L.index]
for seed in (1, 2, 3):
    Q = pd.DataFrame(np.nan, index=L.index, columns=["pL", "pS"])
    for bi, trm, te in C.folds(L.index, L.i.values, L.e.values):
        for side, col in (("RL", "pL"), ("RS", "pS")):
            mdl = lgb.LGBMRegressor(n_estimators=250, learning_rate=0.03, num_leaves=15, min_child_samples=400,
                                    subsample=0.7, subsample_freq=1, colsample_bytree=0.6, reg_lambda=10,
                                    n_jobs=2, verbose=-1, objective="huber", alpha=1.0, random_state=seed)
            mdl.fit(D[trm], np.clip(L[side].values[trm], -1.5, 4)); Q.loc[te, col] = mdl.predict(D[te])
    d = P.trade_dirs(b, "1h", L, Q, 0.0, "both")
    st = H2.stats(H2.run(d, sl, tp, tr, mb))
    print(H2.fmt(f"seed{seed} reg 1h tp1.5 both th=0", st), "all>0" if H2.credible(st) else "", flush=True)
