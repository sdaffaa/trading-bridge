"""Round 7: 12.5 years of M1 gold (2014 - mid 2026). Yearly walk-forward:
train LightGBM on every year before Y, trade year Y (never seen). 1:1, one
position at a time, spread 0.30. Reports per-year and per-day statistics."""
import sys, warnings
import numpy as np, pandas as pd, lightgbm as lgb
sys.path.insert(0, ".")
from load_multi import load_multi
from features import build
from ict_setups_sim import sim
warnings.filterwarnings("ignore")
SPREAD = 0.30
TF = sys.argv[1] if len(sys.argv) > 1 else "15min"
m1 = load_multi()
b, atr, X = build(m1, TF)
feats = list(X.columns)
pos = m1.index.searchsorted(b.index + pd.Timedelta(TF))
valid = (pos < len(m1)) & atr.notna().values & (atr.values > 0)
o1, h1, l1 = m1.open.values, m1.high.values, m1.low.values
for K in [float(k) for k in (sys.argv[2].split(",") if len(sys.argv) > 2 else ["1", "2"])]:
    idx = pos[valid]; dist = (K * atr.values)[valid]
    yL, eL = sim(o1, h1, l1, idx, np.ones(len(idx)), dist, SPREAD)
    yS, eS = sim(o1, h1, l1, idx, -np.ones(len(idx)), dist, SPREAD)
    D = X[valid].copy(); D["yL"], D["yS"], D["eL"], D["eS"], D["i"] = yL, yS, eL, eS, idx
    D = D[(D.yL != 0) & (D.yS != 0)]
    yr = D.index.year
    preds = []
    for Y in range(2017, 2027):
        te = D[yr == Y]
        if te.empty: continue
        trn = D[(yr < Y) & (np.maximum(D.eL, D.eS) < te.i.min())]
        P = te[["yL", "yS", "eL", "eS", "i"]].copy()
        for side in ("yL", "yS"):
            m = lgb.LGBMClassifier(n_estimators=400, learning_rate=0.03, num_leaves=31, min_child_samples=500,
                                   subsample=0.8, subsample_freq=1, colsample_bytree=0.7, verbose=-1)
            m.fit(trn[feats], (trn[side] > 0).astype(int))
            P["p" + side[1]] = m.predict_proba(te[feats])[:, 1]
        preds.append(P)
    P = pd.concat(preds)
    print(f"\n=== TF={TF} SL=TP={K}xATR  unseen 2017-2026 bars={len(P)}  base L={(P.yL>0).mean():.3f} S={(P.yS>0).mean():.3f}")
    for thr in (0.5, 0.55, 0.6, 0.65, 0.7, 0.75):
        busy, res, ts = -1, [], []
        pl, ps, yl, ys, el, es, ii = (P[c].values for c in ("pL", "pS", "yL", "yS", "eL", "eS", "i"))
        for k in range(len(P)):
            if ii[k] <= busy: continue
            best = max(pl[k], ps[k])
            if best < thr: continue
            if pl[k] >= ps[k]: res.append(yl[k]); busy = el[k]
            else: res.append(ys[k]); busy = es[k]
            ts.append(P.index[k])
        if len(res) < 30: print(f"thr={thr}: {len(res)} trades"); continue
        s = pd.Series(res, index=ts); dd = (s > 0).groupby(s.index.date).agg(["mean", "size"])
        yw = (s > 0).groupby(s.index.year).mean()
        print(f"thr={thr}: trades={len(s)} wr={(s>0).mean()*100:.1f}% net={int(s.sum())}R/day={dd['size'].mean():.1f} "
              f"days>=60%={(dd['mean']>=.6).mean()*100:.0f}% | yearly wr min/max={yw.min()*100:.0f}/{yw.max()*100:.0f}%")
