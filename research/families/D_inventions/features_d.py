"""Causal per-M1-bar feature library for family D (value at bar i uses bars < i only).
Builds a float32 matrix X (N x F) cached in the scratchpad."""
import os, numpy as np, pandas as pd
from numba import njit
from core import *

CACHE_X = "/tmp/claude-0/-home-user-trading-bridge/b109c4cd-e10b-5fab-96f6-d6f544632108/scratchpad/D_X.npy"
NAMES = ["hour", "dow", "ret5", "ret15", "ret60", "ret240", "ret1440", "dpos", "drange",
         "to_pdh", "to_pdl", "r10", "r50", "r100", "rsi_m15", "rsi_h1", "rsi_h4", "er_h1",
         "vr_h1", "ac1_m5", "vr_m5", "atr_ratio", "ema50_h1", "ema50_h4", "ema20_d1",
         "asia_pos", "asia_size", "to_poc", "to_vah", "to_val", "frac_hi", "frac_lo",
         "ret1", "to_twap", "ret5d", "hurst_h1"]


def rsi(c, n=14):
    d = c.diff(); up = d.clip(lower=0).ewm(alpha=1 / n).mean(); dn = (-d.clip(upper=0)).ewm(alpha=1 / n).mean()
    return 100 - 100 / (1 + up / dn)


@njit(cache=True)
def _day_state(o, h, l, c, day, hour):
    """For each bar i: today's high/low/TWAP so far (bars < i), today's Asian (00-07 UTC)
    high/low so far, previous-day high/low. Uses only bars < i."""
    n = len(o)
    dhi = np.full(n, np.nan); dlo = np.full(n, np.nan); tw = np.full(n, np.nan)
    ahi = np.full(n, np.nan); alo = np.full(n, np.nan)
    pdh = np.full(n, np.nan); pdl = np.full(n, np.nan)
    chi = -1e18; clo = 1e18; s = 0.0; cnt = 0; a_h = -1e18; a_l = 1e18
    phi = np.nan; plo = np.nan
    for i in range(n):
        if i > 0 and day[i] != day[i - 1]:
            phi = chi; plo = clo
            chi = -1e18; clo = 1e18; s = 0.0; cnt = 0; a_h = -1e18; a_l = 1e18
        if cnt > 0:
            dhi[i] = chi; dlo[i] = clo; tw[i] = s / cnt
        if a_h > -1e17:
            ahi[i] = a_h; alo[i] = a_l
        pdh[i] = phi; pdl[i] = plo
        # now include bar i for later bars
        chi = max(chi, h[i]); clo = min(clo, l[i]); s += c[i]; cnt += 1
        if hour[i] < 7:
            a_h = max(a_h, h[i]); a_l = min(a_l, l[i])
    return dhi, dlo, tw, ahi, alo, pdh, pdl


@njit(cache=True)
def _profile(c, day, binw):
    """Previous-day time-at-price profile from M1 closes: POC, VAH, VAL (70%).
    Value at bar i is from the previous completed UTC day."""
    n = len(c)
    poc = np.full(n, np.nan); vah = np.full(n, np.nan); val = np.full(n, np.nan)
    start = 0
    ppoc = np.nan; pvah = np.nan; pval = np.nan
    i = 0
    while i < n:
        j = i
        while j < n and day[j] == day[i]:
            j += 1
        for k in range(i, j):
            poc[k] = ppoc; vah[k] = pvah; val[k] = pval
        # build profile of day [i, j)
        bw = binw[i]
        lo = c[i]; hi = c[i]
        for k in range(i, j):
            lo = min(lo, c[k]); hi = max(hi, c[k])
        nb = int((hi - lo) / bw) + 1
        hist = np.zeros(nb)
        for k in range(i, j):
            hist[int((c[k] - lo) / bw)] += 1
        p = np.argmax(hist)
        tot = hist.sum(); acc = hist[p]; a = p; b = p
        while acc < 0.7 * tot:
            up = hist[b + 1] if b + 1 < nb else -1.0
            dn = hist[a - 1] if a - 1 >= 0 else -1.0
            if up >= dn:
                b += 1; acc += up
            else:
                a -= 1; acc += dn
        ppoc = lo + (p + 0.5) * bw; pvah = lo + (b + 1) * bw; pval = lo + a * bw
        i = j
    return poc, vah, val


def build():
    if os.path.exists(CACHE_X):
        return np.load(CACHE_X, mmap_mode="r")
    F = len(NAMES)
    X = np.full((N, F), np.nan, np.float32)
    c1 = np.r_[np.nan, C[:-1]]
    a1 = atr_m1("1h"); ad = atr_m1("1D")
    hour = T.hour.values; day = (T.values.astype("datetime64[D]")).astype(np.int64)
    X[:, 0] = hour + T.minute.values / 60; X[:, 1] = T.dayofweek.values
    cs = pd.Series(C)
    for j, k in enumerate((5, 15, 60, 240, 1440)):
        X[:, 2 + j] = (c1 - cs.shift(1 + k).values) / a1
    dhi, dlo, tw, ahi, alo, pdh, pdl = _day_state(O, HI, LO, C, day, hour)
    X[:, 7] = (c1 - dlo) / (dhi - dlo); X[:, 8] = (dhi - dlo) / a1
    X[:, 9] = (pdh - c1) / a1; X[:, 10] = (c1 - pdl) / a1
    X[:, 11] = (c1 % 10) / 10; X[:, 12] = (c1 % 50) / 50; X[:, 13] = (c1 % 100) / 100
    b15, bh, b4, bd, b5 = H.bars("15min"), H.bars("1h"), H.bars("4h"), H.bars("1D"), H.bars("5min")
    X[:, 14] = htf(rsi(b15.close), "15min"); X[:, 15] = htf(rsi(bh.close), "1h"); X[:, 16] = htf(rsi(b4.close), "4h")
    ch = bh.close; rh = ch.diff()
    X[:, 17] = htf((ch - ch.shift(20)).abs() / rh.abs().rolling(20).sum(), "1h")
    X[:, 18] = htf(ch.diff(4).rolling(120).var() / (4 * rh.rolling(120).var()), "1h")
    r5 = b5.close.diff()
    X[:, 19] = htf(r5.rolling(288).corr(r5.shift(1)), "5min")
    X[:, 20] = htf(b5.close.diff(6).rolling(288).var() / (6 * r5.rolling(288).var()), "5min")
    ah = H.atr(bh); X[:, 21] = htf(ah / ah.rolling(240).mean(), "1h")
    X[:, 22] = htf((ch - ch.ewm(span=50).mean()) / ah, "1h")
    a4 = H.atr(b4); X[:, 23] = htf((b4.close - b4.close.ewm(span=50).mean()) / a4, "4h")
    adb = H.atr(bd); X[:, 24] = htf((bd.close - bd.close.ewm(span=20).mean()) / adb, "1D")
    X[:, 25] = (c1 - alo) / (ahi - alo); X[:, 26] = (ahi - alo) / ad
    binw = np.maximum(0.0002 * C, 0.1)
    poc, vah, val = _profile(C, day, binw)
    X[:, 27] = (c1 - poc) / a1; X[:, 28] = (c1 - vah) / a1; X[:, 29] = (c1 - val) / a1
    hh, ll = bh.high, bh.low
    fh = hh.where(hh == hh.rolling(5, center=True).max()).shift(2).ffill()   # known 2 bars later
    fl = ll.where(ll == ll.rolling(5, center=True).min()).shift(2).ffill()
    X[:, 30] = (htf(fh, "1h") - c1) / a1; X[:, 31] = (c1 - htf(fl, "1h")) / a1
    X[:, 32] = np.r_[np.nan, (C - O)[:-1]] / a1
    X[:, 33] = (c1 - tw) / a1
    X[:, 34] = htf((bd.close - bd.close.shift(5)) / adb, "1D")
    # Hurst proxy on H1: log(R/S)/log(n) over 128 bars of returns
    def rs(x):
        y = np.cumsum(x - x.mean()); s = x.std()
        return np.log((y.max() - y.min()) / s) / np.log(len(x)) if s > 0 else np.nan
    hr = rh.iloc[-60000:] if len(rh) > 60000 else rh
    X[:, 35] = htf(rh.rolling(128).apply(rs, raw=True), "1h")
    X[~np.isfinite(X)] = np.nan
    np.save(CACHE_X, X)
    return np.load(CACHE_X, mmap_mode="r")


if __name__ == "__main__":
    import time; t = time.time()
    X = build(); print(X.shape, round(time.time() - t, 1), "s")
    sl = slice(IS0, IS1)
    for j, nm in enumerate(NAMES):
        x = X[sl, j]
        print(f"{nm:10s} nan={np.isnan(x).mean():.3f} q05={np.nanquantile(x,.05):.3f} q50={np.nanquantile(x,.5):.3f} q95={np.nanquantile(x,.95):.3f}")
