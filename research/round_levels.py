"""Round-number rejection, both directions, non-overlapping (one position at a time)."""
import sys
import numpy as np, pandas as pd
sys.path.insert(0, ".")
from backtest import load, SPREAD
from ict_setups_sim import sim

m1 = load(sys.argv[1])
m5 = m1.resample("5min").agg({"open": "first", "high": "max", "low": "min", "close": "last"}).dropna()
atr = (m5.high - m5.low).rolling(14).mean()
thirds = np.array_split(m1.close.values, 3)
print("price drift per third:", [f"{s[0]:.0f}->{s[-1]:.0f}" for s in thirds])
pos = m1.index
o, h, l = m1.open.values, m1.high.values, m1.low.values
for step in (10, 25, 50):
  for mult in (1.0, 2.0, 3.0):
    sig = []
    for ts, r in m5.iterrows():
        a = atr.get(ts)
        if not np.isfinite(a): continue
        up = np.floor(r.high / step) * step          # level pierced from below, rejected
        dn = np.ceil(r.low / step) * step            # level pierced from above, rejected
        i = pos.searchsorted(ts + pd.Timedelta("5min"))
        if i >= len(m1): continue
        if r.open < up <= r.high and r.close < up: sig.append((i, -1, mult * a))
        elif r.open > dn >= r.low and r.close > dn: sig.append((i, 1, mult * a))
    idx = np.array([s[0] for s in sig]); d = np.array([s[1] for s in sig], float); di = np.array([s[2] for s in sig])
    out, endj = sim(o, h, l, idx, d, di, SPREAD)
    # one position at a time
    keep, busy = [], -1
    for k in range(len(idx)):
        if idx[k] > busy and out[k] != 0: keep.append(k); busy = endj[k]
    keep = np.array(keep)
    res = pd.DataFrame({"t": m1.index[idx[keep]], "d": d[keep], "r": out[keep]})
    res["third"] = pd.qcut(np.arange(len(res)), 3, labels=["T1", "T2", "T3"])
    g = res.groupby(["third", "d"], observed=True).r.agg(lambda s: f"{(s>0).mean()*100:.0f}%/{len(s)}").unstack()
    daily = (res.r > 0).groupby(res.t.dt.date).mean()
    print(f"step={step} sl={mult}xATR5: all={((res.r>0).mean()*100):.1f}% n={len(res)} net={res.r.sum()}R  days>=60%: {(daily>=.6).mean()*100:.0f}%  | by third/side:",
          g.to_dict())
