"""Replays the EA's default logic (H1 EMA20/50 direction, SL=TP=2xATR(H1),
re-enter immediately) on M1 bars for intrabar-accurate exits."""
import sys
import numpy as np, pandas as pd
sys.path.insert(0, ".")
from backtest import load, SPREAD

m1 = load(sys.argv[1])
h1 = m1.resample("1h").agg({"open": "first", "high": "max", "low": "min", "close": "last"}).dropna()
tr = pd.concat([h1.high - h1.low, (h1.high - h1.close.shift()).abs(), (h1.low - h1.close.shift()).abs()], axis=1).max(axis=1)
f = pd.DataFrame({"atr": tr.rolling(14).mean(),
                  "dir": np.sign(h1.close.ewm(span=20).mean() - h1.close.ewm(span=50).mean())}).shift(1)
f = f.reindex(m1.index, method="ffill")  # value of last completed H1 bar
o, h, l = m1.open.values, m1.high.values, m1.low.values
res, i, n = [], 0, len(m1)
while i < n:
    d, a = f.dir.values[i], f.atr.values[i]
    if not (np.isfinite(a) and d != 0): i += 1; continue
    e = o[i] + d * SPREAD / 2; dist = 2 * a; out = None
    for j in range(i, n):
        bid_lo, bid_hi = l[j], h[j]
        if d > 0: loss, win = bid_lo - 0 <= e - dist, bid_hi >= e + dist
        else:     loss, win = bid_hi + SPREAD >= e + dist, bid_lo + SPREAD <= e - dist
        if loss: out = -1; break
        if win: out = 1; break
    if out is None: break
    res.append((m1.index[i], out)); i = j + 1
s = pd.Series([r[1] for r in res], index=[r[0] for r in res])
daily = (s > 0).groupby(s.index.date).mean()
print(f"trades={len(s)}  win rate={(s>0).mean()*100:.1f}%  net={int(s.sum())}R  "
      f"trades/day={len(s)/daily.size:.1f}  days with 65-85%+ wins={(daily>=.65).mean()*100:.0f}%  "
      f"max losing streak={max(len(g) for g in ''.join('L' if x<0 else 'W' for x in s).split('W'))}")
