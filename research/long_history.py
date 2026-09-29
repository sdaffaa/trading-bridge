"""Round 3: the same always-in-market 1:1 engine on 25 years of daily gold
(2000-2025) and on H1 (Apr-Oct 2025). Both-hit-same-bar = loss."""
import sys
import numpy as np, pandas as pd

def load(p):
    df = pd.read_csv(p); df.columns = [c.lower() for c in df.columns]
    t = df.columns[0]; df[t] = pd.to_datetime(df[t], utc=True); df = df.set_index(t)
    df = df[["open", "high", "low", "close"]].astype(float)
    return df[(df.high > df.low)]

def feats(b):
    tr = pd.concat([b.high - b.low, (b.high - b.close.shift()).abs(), (b.low - b.close.shift()).abs()], axis=1).max(axis=1)
    f = pd.DataFrame(index=b.index)
    f["atr"] = tr.rolling(14).mean()
    f["tr_ema"] = np.sign(b.close.ewm(span=20).mean() - b.close.ewm(span=50).mean())
    f["tr_200"] = np.sign(b.close - b.close.ewm(span=200).mean())
    f["mom"] = np.sign(b.close - b.close.shift(20))
    d = b.close.diff(); up = d.clip(lower=0).ewm(alpha=1/14).mean(); dn = (-d.clip(upper=0)).ewm(alpha=1/14).mean()
    f["rev"] = np.where(100 - 100/(1 + up/dn) < 50, 1, -1)
    f["always_long"] = 1
    f["always_short"] = -1
    return f.shift(1)  # decided on completed bars only

def run(b, f, col, k, spread):
    o, h, l = b.open.values, b.high.values, b.low.values
    sig, atr = f[col].values, f.atr.values
    res, i, n = [], 210, len(b)
    while i < n:
        d = sig[i]
        if not np.isfinite(atr[i]) or d == 0 or not np.isfinite(d):
            i += 1; continue
        dist = k * atr[i]; e = o[i] + d * spread / 2
        out = None
        for j in range(i, n):
            lo, hi = l[j] - spread / 2 if d > 0 else l[j] + spread / 2, h[j] - spread / 2 if d > 0 else h[j] + spread / 2
            win = hi >= e + dist if d > 0 else lo <= e - dist
            loss = lo <= e - dist if d > 0 else hi >= e + dist
            if loss: out = -1; break
            if win: out = 1; break
        if out is None: break
        res.append((b.index[i], out)); i = j + 1
    return res

for path, spread in ((sys.argv[1], 0.3), (sys.argv[2], 0.3)):
    b = load(path); f = feats(b)
    print(f"\n### {path.split('/')[-1]}  bars={len(b)}  {b.index[0].date()} -> {b.index[-1].date()}")
    rows = []
    for col in ["always_long", "always_short", "tr_ema", "tr_200", "mom", "rev"]:
        for k in (0.5, 1, 2):
            r = run(b, f, col, k, spread)
            if not r: continue
            s = pd.Series([x[1] for x in r], index=[x[0] for x in r])
            yearly = (s > 0).groupby(s.index.year).mean()
            rows.append(dict(strategy=col, atr_mult=k, trades=len(s), winrate=round((s > 0).mean()*100, 1),
                             net_R=int(s.sum()), worst_year=round(yearly.min()*100, 1), best_year=round(yearly.max()*100, 1)))
    print(pd.DataFrame(rows).sort_values("winrate", ascending=False).to_string(index=False))
