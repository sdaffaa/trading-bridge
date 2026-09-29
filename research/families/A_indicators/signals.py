"""Indicator signal library for family A. Every signal is +1/-1 (0 = undefined/warm-up)
computed on a tf's COMPLETED bars; the M1 alignment (tf_map) makes it causal."""
import numpy as np
import pandas as pd
from numba import njit

TFS = {"M5": "5min", "M15": "15min", "M30": "30min", "H1": "1h", "H4": "4h", "D1": "1D"}


def sgn(x):
    x = np.asarray(x, np.float64)
    out = np.sign(x)
    out[np.isnan(x)] = 0
    return out.astype(np.int8)


def ema(s, n): return s.ewm(span=n, adjust=False, min_periods=n).mean()
def sma(s, n): return s.rolling(n).mean()


def wma(s, n):
    w = np.arange(1, n + 1, dtype=float)
    return s.rolling(n).apply(lambda x: np.dot(x, w) / w.sum(), raw=True)


def wma_fast(s, n):
    # linear weighted MA via convolution
    v = s.values.astype(float); w = np.arange(1, n + 1, dtype=float); w /= w.sum()
    out = np.full(len(v), np.nan)
    if len(v) >= n:
        out[n - 1:] = np.convolve(v, w[::-1], mode="valid")
    return pd.Series(out, s.index)


def hma(s, n):
    h = max(int(n / 2), 1); r = max(int(np.sqrt(n)), 1)
    return wma_fast(2 * wma_fast(s, h) - wma_fast(s, n), r)


@njit(cache=True)
def _kama(c, n, fast, slow):
    out = np.full(len(c), np.nan)
    fsc = 2.0 / (fast + 1); ssc = 2.0 / (slow + 1)
    if len(c) <= n:
        return out
    out[n] = c[n]
    for i in range(n + 1, len(c)):
        ch = abs(c[i] - c[i - n]); vol = 0.0
        for k in range(i - n + 1, i + 1):
            vol += abs(c[k] - c[k - 1])
        er = ch / vol if vol > 0 else 0.0
        sc = (er * (fsc - ssc) + ssc) ** 2
        out[i] = out[i - 1] + sc * (c[i] - out[i - 1])
    return out


def kama(s, n): return pd.Series(_kama(s.values.astype(float), n, 2, 30), s.index)


def MA(kind, s, n):
    return {"EMA": ema, "SMA": sma, "HMA": hma, "KAMA": kama}[kind](s, n)


def atr_s(b, n=14):
    tr = pd.concat([b.high - b.low, (b.high - b.close.shift()).abs(), (b.low - b.close.shift()).abs()], axis=1).max(axis=1)
    return tr.rolling(n).mean()


@njit(cache=True)
def _supertrend(h, l, c, at, mult):
    n = len(c); d = np.zeros(n)
    ub = np.full(n, np.nan); lb = np.full(n, np.nan)
    for i in range(n):
        if np.isnan(at[i]):
            continue
        m = (h[i] + l[i]) / 2
        bu = m + mult * at[i]; bl = m - mult * at[i]
        if i > 0 and not np.isnan(ub[i - 1]):
            ub[i] = bu if (bu < ub[i - 1] or c[i - 1] > ub[i - 1]) else ub[i - 1]
            lb[i] = bl if (bl > lb[i - 1] or c[i - 1] < lb[i - 1]) else lb[i - 1]
            if d[i - 1] >= 0:
                d[i] = -1 if c[i] < lb[i] else 1
            else:
                d[i] = 1 if c[i] > ub[i] else -1
        else:
            ub[i] = bu; lb[i] = bl; d[i] = 1
    return d


@njit(cache=True)
def _psar(h, l, af0, afmax):
    n = len(h); d = np.zeros(n)
    if n < 3:
        return d
    up = True; sar = l[0]; ep = h[0]; af = af0
    for i in range(1, n):
        sar = sar + af * (ep - sar)
        if up:
            sar = min(sar, l[i - 1], l[i - 2] if i >= 2 else l[i - 1])
            if l[i] < sar:
                up = False; sar = ep; ep = l[i]; af = af0
            else:
                if h[i] > ep:
                    ep = h[i]; af = min(af + af0, afmax)
        else:
            sar = max(sar, h[i - 1], h[i - 2] if i >= 2 else h[i - 1])
            if h[i] > sar:
                up = True; sar = ep; ep = h[i]; af = af0
            else:
                if l[i] < ep:
                    ep = l[i]; af = min(af + af0, afmax)
        d[i] = 1 if up else -1
    return d


@njit(cache=True)
def _zone_hold(x, hi, lo):
    """+1 once x>hi, -1 once x<lo, hold previous state otherwise (momentum form)."""
    n = len(x); d = np.zeros(n); st = 0.0
    for i in range(n):
        if np.isnan(x[i]):
            d[i] = 0; continue
        if x[i] > hi:
            st = 1.0
        elif x[i] < lo:
            st = -1.0
        d[i] = st
    return d


def zone(x, hi, lo): return _zone_hold(np.asarray(x, np.float64), hi, lo).astype(np.int8)


@njit(cache=True)
def _aroon(h, l, n):
    m = len(h); au = np.full(m, np.nan); ad = np.full(m, np.nan)
    for i in range(n, m):
        bh = i - n; bl = i - n
        for k in range(i - n, i + 1):
            if h[k] >= h[bh]: bh = k
            if l[k] <= l[bl]: bl = k
        au[i] = bh; ad[i] = bl
    return au, ad


@njit(cache=True)
def _meandev(x, n):
    m = len(x); out = np.full(m, np.nan)
    for i in range(n - 1, m):
        mu = 0.0
        for k in range(i - n + 1, i + 1): mu += x[k]
        mu /= n; s = 0.0
        for k in range(i - n + 1, i + 1): s += abs(x[k] - mu)
        out[i] = s / n
    return out


def rsi(c, n):
    d = c.diff(); up = d.clip(lower=0); dn = (-d).clip(lower=0)
    au = up.ewm(alpha=1 / n, adjust=False, min_periods=n).mean()
    ad = dn.ewm(alpha=1 / n, adjust=False, min_periods=n).mean()
    return 100 - 100 / (1 + au / ad)


def linreg_slope(c, n):
    x = np.arange(n, dtype=float); x -= x.mean(); den = (x ** 2).sum()
    v = c.values.astype(float); out = np.full(len(v), np.nan)
    if len(v) >= n:
        out[n - 1:] = np.convolve(v, (x / den)[::-1], mode="valid")
    return out


def signals_for_tf(b):
    """Return dict name -> int8 array (len(b)); +1 long, -1 short, 0 undefined.
    All in the 'normal' (trend/momentum) form; the grid also tests each inverted."""
    c, h, l, o = b.close, b.high, b.low, b.open
    S = {}
    L = [5, 10, 20, 50, 100, 200]
    mas = {}
    for k in ("EMA", "SMA", "HMA", "KAMA"):
        for n in L:
            mas[(k, n)] = MA(k, c, n)
            S[f"px_vs_{k}{n}"] = sgn(c - mas[(k, n)])
        S[f"{k}_slope20"] = sgn(mas[(k, 20)].diff())
    for k in ("EMA", "SMA", "HMA", "KAMA"):
        for f, s in ((5, 20), (10, 50), (20, 100), (50, 200), (5, 10)):
            S[f"{k}cross{f}_{s}"] = sgn(mas[(k, f)] - mas[(k, s)])
    for f, s, g in ((12, 26, 9), (5, 35, 5), (3, 10, 16)):
        m = ema(c, f) - ema(c, s); sg = ema(m, g); hi = m - sg
        S[f"MACD{f}_{s}_line"] = sgn(m)
        S[f"MACD{f}_{s}_hist"] = sgn(hi)
        S[f"MACD{f}_{s}_hslope"] = sgn(hi.diff())
    for n in (10, 20, 55, 100):
        hh = h.rolling(n).max(); ll = l.rolling(n).min()
        S[f"donch{n}_pos"] = sgn(c - (hh + ll) / 2)
        # breakout state: last close above prior n-high -> +1, below prior n-low -> -1
        brk = np.where(c > hh.shift(), 1.0, np.where(c < ll.shift(), -1.0, np.nan))
        st = pd.Series(brk, b.index).ffill().values
        S[f"donch{n}_brk"] = sgn(st)
    for n, m in ((10, 3), (10, 2), (20, 3), (7, 1.5)):
        at = atr_s(b, n).values
        S[f"supertrend{n}_{m}"] = _supertrend(h.values.astype(float), l.values.astype(float), c.values.astype(float), at, m).astype(np.int8)
    for a0, am in ((0.02, 0.2), (0.01, 0.1), (0.04, 0.4)):
        S[f"psar{a0}"] = _psar(h.values.astype(float), l.values.astype(float), a0, am).astype(np.int8)
    tenkan = (h.rolling(9).max() + l.rolling(9).min()) / 2
    kijun = (h.rolling(26).max() + l.rolling(26).min()) / 2
    sa = ((tenkan + kijun) / 2).shift(26); sb = ((h.rolling(52).max() + l.rolling(52).min()) / 2).shift(26)
    top = np.maximum(sa, sb); bot = np.minimum(sa, sb)
    cloud = np.where(c > top, 1.0, np.where(c < bot, -1.0, np.sign(c - kijun)))
    cloud[np.isnan(top.values)] = np.nan
    S["ichi_cloud"] = sgn(cloud)
    S["ichi_TK"] = sgn(tenkan - kijun)
    S["ichi_px_kijun"] = sgn(c - kijun)
    for n in (7, 14, 28):
        upm = h.diff(); dnm = -l.diff()
        pdm = np.where((upm > dnm) & (upm > 0), upm, 0.0); ndm = np.where((dnm > upm) & (dnm > 0), dnm, 0.0)
        tr = pd.concat([h - l, (h - c.shift()).abs(), (l - c.shift()).abs()], axis=1).max(axis=1)
        atrw = tr.ewm(alpha=1 / n, adjust=False, min_periods=n).mean()
        pdi = pd.Series(pdm, b.index).ewm(alpha=1 / n, adjust=False, min_periods=n).mean() / atrw
        ndi = pd.Series(ndm, b.index).ewm(alpha=1 / n, adjust=False, min_periods=n).mean() / atrw
        S[f"DI{n}"] = sgn(pdi - ndi)
    hac = (o + h + l + c) / 4
    hao = np.empty(len(b)); hao[0] = (o.iloc[0] + c.iloc[0]) / 2
    hv = hac.values
    for i in range(1, len(b)):
        hao[i] = (hao[i - 1] + hv[i - 1]) / 2
    S["HA_colour"] = sgn(hv - hao)
    S["HA_colour_2of3"] = sgn(pd.Series(np.sign(hv - hao), b.index).rolling(3).sum())
    S["candle_colour"] = sgn(c - o)
    for n in (10, 20, 50, 100):
        S[f"linreg{n}"] = sgn(linreg_slope(c, n))
    for n in (14, 25, 50):
        au, ad = _aroon(h.values.astype(float), l.values.astype(float), n)
        S[f"aroon{n}"] = sgn(au - ad)  # later index of high => more recent high => up
    # oscillators: momentum form = sign(osc - mid); contrarian = inverted in grid
    for n in (2, 3, 5, 7, 14, 21):
        r = rsi(c, n)
        S[f"RSI{n}_50"] = sgn(r - 50)
        if n in (2, 5, 14):
            S[f"RSI{n}_zone70"] = zone(r.values, 70, 30)
            S[f"RSI{n}_zone80"] = zone(r.values, 80, 20)
    for n in (5, 14, 50):
        hh = h.rolling(n).max(); ll = l.rolling(n).min()
        k = 100 * (c - ll) / (hh - ll); d = k.rolling(3).mean()
        S[f"stoch{n}_50"] = sgn(d - 50)
        S[f"stoch{n}_KD"] = sgn(k - d)
        S[f"stoch{n}_zone"] = zone(d.values, 80, 20)
        S[f"WR{n}_zone"] = zone(k.values, 90, 10)  # Williams %R -10/-90 equivalent
    for n in (14, 20, 50):
        tp = (h + l + c) / 3; ma = tp.rolling(n).mean()
        md = pd.Series(_meandev(tp.values.astype(float), n), b.index)
        cci = (tp - ma) / (0.015 * md)
        S[f"CCI{n}"] = sgn(cci)
        S[f"CCI{n}_zone"] = zone(cci.values, 100, -100)
    for n in (20, 50, 100, 200):
        z = (c - c.rolling(n).mean()) / c.rolling(n).std()
        S[f"z{n}_zone1"] = zone(z.values, 1, -1)
        S[f"z{n}_zone2"] = zone(z.values, 2, -2)
    for n in (1, 3, 5, 10, 20, 50):
        S[f"ROC{n}"] = sgn(c.diff(n))
    return S
