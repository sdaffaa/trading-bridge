"""Chart-context features shared by the ML studies (all use completed bars only)."""
import numpy as np, pandas as pd

def build(m1, TF):
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
    
    return b, atr, X
