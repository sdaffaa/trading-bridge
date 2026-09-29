"""EA default logic (H1 EMA20/50 direction, SL=TP=k x ATR(H1), always in market) on 2014-2026 M1."""
import sys
import numpy as np, pandas as pd
sys.path.insert(0, ".")
from load_multi import load_multi
from ict_setups_sim import sim
m1 = load_multi()
h1 = m1.resample("1h").agg({"open": "first", "high": "max", "low": "min", "close": "last"}).dropna()
tr = pd.concat([h1.high - h1.low, (h1.high - h1.close.shift()).abs(), (h1.low - h1.close.shift()).abs()], axis=1).max(axis=1)
atr = tr.rolling(14).mean().shift(1).reindex(m1.index, method="ffill").values
dirn = np.sign(h1.close.ewm(span=20).mean() - h1.close.ewm(span=50).mean()).shift(1).reindex(m1.index, method="ffill").values
o, h, l = m1.open.values, m1.high.values, m1.low.values
for k in (1.0, 2.0, 3.0):
    res, ts, i, n = [], [], 1000, len(m1)
    while i < n:
        if not (np.isfinite(atr[i]) and dirn[i] != 0): i += 1; continue
        out, e = sim(o, h, l, np.array([i]), np.array([dirn[i]]), np.array([k * atr[i]]), 0.30)
        if out[0] == 0: break
        res.append(out[0]); ts.append(m1.index[i]); i = e[0] + 1
    s = pd.Series(res, index=ts); dd = (s > 0).groupby(s.index.date).mean(); yw = (s > 0).groupby(s.index.year).mean()
    print(f"k={k}: trades={len(s)} wr={(s>0).mean()*100:.1f}% net={int(s.sum())}R days>=60%={(dd>=.6).mean()*100:.0f}% "
          f"yearly={ {y: round(v*100) for y, v in yw.items()} }")
