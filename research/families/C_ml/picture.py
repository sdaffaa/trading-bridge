"""'Chart picture' input: the last N candles of the decision TF, OHLC expressed relative to the
last close and scaled by ATR(14) of that TF (what a trader sees on screen), plus the hour."""
import os, numpy as np, pandas as pd, common as C, harness as H

def picture(TF, N=48):
    fn = f"{C.CACHE}/pic_{TF}_{N}.parquet"
    b, X = C.build_dataset(TF)
    if os.path.exists(fn):
        return b, pd.read_parquet(fn)
    a = H.atr(b, 14).values
    c = b.close.values
    cols = {}
    for k in range(N):
        for f in ("open", "high", "low", "close"):
            v = np.r_[np.full(k, np.nan), b[f].values[:len(b) - k]] if k else b[f].values
            cols[f"{f[0]}{k}"] = ((v - c) / a).astype(np.float32)
    P = pd.DataFrame(cols, index=b.index)
    P["hsin"] = X["hsin"].values; P["hcos"] = X["hcos"].values
    P = P.replace([np.inf, -np.inf], np.nan).clip(-30, 30)
    P.to_parquet(fn)
    return b, P
