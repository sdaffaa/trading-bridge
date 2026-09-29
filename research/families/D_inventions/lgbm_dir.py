"""Search-generated rule via ML: LightGBM predicts P(long wins) and P(short wins) for a
1:1 trade at each bar (distance scheme fixed), trained on IS bars only; direction =
side with higher predicted win prob. Evaluated consecutively on IS (in-sample!) and VAL."""
import numpy as np, lightgbm as lgb
from core import *
from features_d import build, NAMES

X = build()
a1 = atr_m1("1h"); px = htf(M1.close.resample("1D").last().dropna(), "1D")
for nm, dist in (("2xATRh1", 2 * a1), ("0.5%px", 0.005 * px), ("1xATRh1", a1)):
    tb = tables(dist)
    wl, el, ws, es = tb
    # training rows: IS bars, subsampled, label must not leak past IS end
    idx = np.arange(IS0, IS1, 5)
    idx = idx[(wl[idx] != 0) & (np.maximum(el[idx], es[idx]) < IS1)]
    Xt = np.asarray(X[idx], np.float32)
    p = dict(objective="binary", learning_rate=0.03, num_leaves=15, min_data_in_leaf=2000,
             feature_fraction=0.7, bagging_fraction=0.7, bagging_freq=1, verbose=-1, num_threads=1)
    mL = lgb.train(p, lgb.Dataset(Xt, (wl[idx] > 0).astype(int)), 300)
    mS = lgb.train(p, lgb.Dataset(Xt, (ws[idx] > 0).astype(int)), 300)
    rows = np.arange(IS0, VAL1)
    Xa = np.asarray(X[IS0:VAL1], np.float32)
    pl = mL.predict(Xa); ps = mS.predict(Xa)
    dirs = np.zeros(N); dirs[IS0:VAL1] = np.where(pl >= ps, 1.0, -1.0)
    na, wa, nb, wb = quick(dirs, tb)
    print(f"LGBM dir {nm}: IS(in-sample) n={na} wr={wa*100:.2f} | VAL n={nb} wr={wb*100:.2f}", flush=True)
    # confidence-only variant is not allowed (must always trade) -> also report calibration
    edge = np.maximum(pl, ps)
    for q in (0.5, 0.9, 0.99):
        th = np.quantile(edge[: IS1 - IS0], q)
        m = edge[IS1 - IS0 + (VAL0 - IS1):] >= th
        vv = np.arange(VAL0, VAL1)[m]
        w = np.where(pl[vv - IS0] >= ps[vv - IS0], wl[vv], ws[vv]) > 0
        print(f"   VAL bars with pred-edge >= IS q{q}: {m.sum()} bars, actual win rate {w.mean()*100:.2f} (not a tradable subset: always-in rule)")
