"""Round 6: 'trading by feel' as a learned model. LightGBM reads chart context
and predicts P(1:1 winner) for long and short; trade only when confident.
Walk-forward: retrain every week on all past data, predict the next week only."""
import sys, warnings
import numpy as np, pandas as pd, lightgbm as lgb
sys.path.insert(0, ".")
from backtest import load, SPREAD
from ict_setups_sim import sim
warnings.filterwarnings("ignore")

m1 = load(sys.argv[1])
TF = "5min"
b = m1.resample(TF).agg({"open": "first", "high": "max", "low": "min", "close": "last"}).dropna()
c, h, l, o = b.close, b.high, b.low, b.open
tr = pd.concat([h - l, (h - c.shift()).abs(), (l - c.shift()).abs()], axis=1).max(axis=1)
atr = tr.rolling(14).mean()
X = pd.DataFrame(index=b.index)
for n in (1, 3, 6, 12, 24, 48, 96, 288):
    X[f"ret{n}"] = (c - c.shift(n)) / atr
for n in (20, 50, 200):
    X[f"ema{n}"] = (c - c.ewm(span=n).mean()) / atr
d = c.diff()
for n in (7, 14, 28):
    up = d.clip(lower=0).ewm(alpha=1/n).mean(); dn = (-d.clip(upper=0)).ewm(alpha=1/n).mean()
    X[f"rsi{n}"] = 100 - 100 / (1 + up / dn)
X["atr_ratio"] = atr / atr.rolling(288).mean()
X["range_now"] = (h - l) / atr
X["upwick"] = (h - np.maximum(o, c)) / atr
X["dnwick"] = (np.minimum(o, c) - l) / atr
X["body"] = (c - o) / atr
for n in (12, 48, 288):
    hh, ll = h.rolling(n).max(), l.rolling(n).min()
    X[f"pos{n}"] = (c - ll) / (hh - ll)
    X[f"dhh{n}"] = (hh - c) / atr
    X[f"dll{n}"] = (c - ll) / atr
day = b.index.normalize()
dh = h.groupby(day).cummax(); dl = l.groupby(day).cummin()
X["dpos"] = (c - dl) / (dh - dl); X["drange"] = (dh - dl) / atr
dO = o.groupby(day).transform("first"); X["from_open"] = (c - dO) / atr
pdh = h.groupby(day).max().shift(1).reindex(day).values; pdl = l.groupby(day).min().shift(1).reindex(day).values
X["to_pdh"] = (pdh - c) / atr; X["to_pdl"] = (c - pdl) / atr
X["r25"] = (c % 25) / 25; X["r10"] = (c % 10) / 10
X["hour"] = b.index.hour + b.index.minute / 60; X["dow"] = b.index.dayofweek
X["std_ratio"] = c.diff().rolling(12).std() / c.diff().rolling(96).std()
X["efficiency"] = (c - c.shift(24)).abs() / c.diff().abs().rolling(24).sum()
X = X.replace([np.inf, -np.inf], np.nan)

# labels: exact 1:1 outcome of a market entry at the next M1 bar
pos = m1.index.searchsorted(b.index + pd.Timedelta(TF))
valid = (pos < len(m1)) & atr.notna().values
o1, h1, l1 = m1.open.values, m1.high.values, m1.low.values

def run(K):
    idx = pos[valid]; dist = (K * atr.values)[valid]
    yL, eL = sim(o1, h1, l1, idx, np.ones(len(idx)), dist, SPREAD)
    yS, eS = sim(o1, h1, l1, idx, -np.ones(len(idx)), dist, SPREAD)
    D = X[valid].copy(); D["yL"] = yL; D["yS"] = yS; D["eL"] = eL; D["eS"] = eS; D["i"] = idx
    D = D[(D.yL != 0) & (D.yS != 0)]
    weeks = D.index.to_period("W")
    uw = weeks.unique()
    preds = []
    feats = [f for f in X.columns]
    for w in uw[3:]:
        test = D[weeks == w]
        # purge: drop training rows whose trade was still open when the test week starts
        tr_ = D[(weeks < w) & (np.maximum(D.eL, D.eS) < test.i.min())]
        P = test[["yL", "yS", "eL", "eS", "i"]].copy()
        for side in ("yL", "yS"):
            m = lgb.LGBMClassifier(n_estimators=300, learning_rate=0.03, num_leaves=15,
                                   min_child_samples=200, subsample=0.8, subsample_freq=1,
                                   colsample_bytree=0.7, verbose=-1)
            m.fit(tr_[feats], (tr_[side] > 0).astype(int))
            P["p" + side[1]] = m.predict_proba(test[feats])[:, 1]
        preds.append(P)
    P = pd.concat(preds)
    print(f"\n=== SL=TP={K}xATR(M5)  out-of-sample weeks={len(uw)-3}  bars={len(P)} base long wr={(P.yL>0).mean():.3f} short wr={(P.yS>0).mean():.3f}")
    for thr in (0.5, 0.55, 0.6, 0.65, 0.7):
        # one position at a time, take the more confident side if above threshold
        busy, res, ts = -1, [], []
        for t_, r in P.iterrows():
            if r.i <= busy: continue
            side = "L" if r.pL >= r.pS else "S"
            if max(r.pL, r.pS) < thr: continue
            res.append(r["y" + side]); ts.append(t_); busy = r["e" + side]
        if not res: print(f"thr={thr}: no trades"); continue
        s = pd.Series(res, index=ts); daily = (s > 0).groupby(s.index.date).agg(["mean", "size"])
        print(f"thr={thr}: trades={len(s)} winrate={(s>0).mean()*100:.1f}% net={int(s.sum())}R "
              f"trades/day={daily['size'].mean():.1f} days>=60%={(daily['mean']>=.6).mean()*100:.0f}% "
              f"worst day={daily['mean'].min()*100:.0f}%")
    return P

for K in (1.0, 2.0, 3.0):
    run(K)
