"""Family E (profit objective). Shared helpers: cached bars, causal entry-event builders,
generic exit grid, evaluation through harness2.run / harness2.stats (mandatory harness).
Conventions: every entry builder returns a float M1 array (+1/-1 at the M1 bar where the
order is sent = first M1 bar at/after the signalling TF bar's CLOSE, 0 elsewhere) or, in
'state' mode, the causal TF state on every M1 bar (re-entry allowed after exits)."""
import os, sys, numpy as np, pandas as pd
from numba import njit
R = "/home/user/trading-bridge/research"
sys.path.insert(0, R); sys.path.insert(0, R + "/families/A_indicators")
import harness2 as H
from signals import ema, sma, atr_s, _supertrend, rsi

M1 = H.load_m1(); N = len(M1); IDX = M1.index
O, HI, LO, C = (M1[k].values.astype(np.float64) for k in ("open", "high", "low", "close"))
TF = {"M15": "15min", "M30": "30min", "H1": "1h", "H4": "4h", "D1": "1D"}
SCR = "/tmp/claude-0/-home-user-trading-bridge/b109c4cd-e10b-5fab-96f6-d6f544632108/scratchpad/E"
os.makedirs(SCR, exist_ok=True)
_B = {}


def B(tf):
    if tf not in _B:
        p = f"{SCR}/bars_{tf}.parquet"
        if os.path.exists(p):
            _B[tf] = pd.read_parquet(p)
        else:
            _B[tf] = H.bars(TF[tf]); _B[tf].to_parquet(p)
    return _B[tf]


_A = {}


def ATRM1(tf, n=14):
    """ATR of the last COMPLETED tf bar, on every M1 bar (causal)."""
    if (tf, n) not in _A:
        _A[(tf, n)] = H.htf_to_m1(atr_s(B(tf), n), TF[tf])
    return _A[(tf, n)]


def state_m1(series, tf):
    x = H.htf_to_m1(pd.Series(np.asarray(series, float), B(tf).index), TF[tf])
    return np.nan_to_num(x)


def event_m1(ev, tf):
    """ev: array len(B(tf)) of +1/-1/0 decided at bar close -> M1 array at first M1 bar >= close."""
    b = B(tf); ev = np.asarray(ev, float)
    k = np.nonzero(ev)[0]
    pos = IDX.searchsorted(b.index[k] + pd.Timedelta(TF[tf]))
    out = np.zeros(N); ok = pos < N
    out[pos[ok]] = ev[k][ok]
    return out


def flips(state):
    s = np.asarray(state, float); prev = np.r_[0, s[:-1]]
    return np.where((s != prev) & (prev != 0) & (s != 0), s, 0.0)


# ---------------------------------------------------------------- trend entries
def st_donch(tf, n):
    b = B(tf); hh = b.high.rolling(n).max().shift(); ll = b.low.rolling(n).min().shift()
    brk = np.where(b.close > hh, 1.0, np.where(b.close < ll, -1.0, np.nan))
    return pd.Series(brk).ffill().fillna(0).values


def st_macross(tf, f, s):
    c = B(tf).close
    return np.nan_to_num(np.sign((ema(c, f) - ema(c, s)).values))


def st_super(tf, n, m):
    b = B(tf)
    d = _supertrend(b.high.values.astype(float), b.low.values.astype(float), b.close.values.astype(float),
                    atr_s(b, n).values, m)
    d[:n + 1] = 0
    return d


def trend_entry(kind, tf, p, mode):
    st = {"donch": lambda: st_donch(tf, *p), "ma": lambda: st_macross(tf, *p), "st": lambda: st_super(tf, *p)}[kind]()
    return event_m1(flips(st), tf) if mode == "event" else state_m1(st, tf)


# ---------------------------------------------------------------- pullback in trend
def pullback(ttf, etf, tdef, rn, thr):
    bt = B(ttf); c = bt.close
    if tdef == "ema50_200":
        tr = np.sign(ema(c, 50) - ema(c, 200)).values
    else:  # close vs EMA50 and EMA50 rising
        e = ema(c, 50); tr = np.where((c > e) & (e.diff() > 0), 1, np.where((c < e) & (e.diff() < 0), -1, 0))
    trm = state_m1(tr, ttf)
    r = rsi(B(etf).close, rn).values; rp = np.r_[np.nan, r[:-1]]
    ev = np.where((r < thr) & ~(rp < thr), 1.0, np.where((r > 100 - thr) & ~(rp > 100 - thr), -1.0, 0.0))
    e = event_m1(ev, etf)
    return np.where(e == trm, e, 0.0)


# ---------------------------------------------------------------- window range breaks
@njit(cache=True)
def _window_break(c, ws, we, hi, lo, both):
    """For each window [ws,we): first M1 bar j (ws<j<we) with close[j-1] beyond hi/lo -> dir at j.
    both=1 allows one long AND one short break per window."""
    out = np.zeros(len(c)); w = np.zeros(len(c))
    for k in range(len(ws)):
        s = ws[k]; e = we[k]; dl = False; ds = False
        if not (hi[k] > lo[k]):
            continue
        for j in range(s + 1, e):
            if not dl and c[j - 1] > hi[k]:
                out[j] = 1.0; w[j] = hi[k] - lo[k]; dl = True
                if both == 0: break
            elif not ds and c[j - 1] < lo[k]:
                out[j] = -1.0; w[j] = hi[k] - lo[k]; ds = True
                if both == 0: break
            if dl and ds: break
    return out, w


def session_break(r0, r1, t1, both=0):
    """Range = M1 bars in [r0,r1) UTC hours (fractional ok) each day; trade breaks in [r1,t1)."""
    m = M1; hrs = IDX.hour + IDX.minute / 60.0
    day = IDX.normalize()
    inr = (hrs >= r0) & (hrs < r1)
    g = pd.DataFrame({"h": HI[inr], "l": LO[inr]}, index=day[inr]).groupby(level=0).agg({"h": "max", "l": "min"})
    days = g.index
    ws = IDX.searchsorted(days + pd.Timedelta(hours=r1)); we = IDX.searchsorted(days + pd.Timedelta(hours=t1))
    return _window_break(C, ws.astype(np.int64), we.astype(np.int64), g.h.values, g.l.values, both)


def setup_break(tf, kind):
    """Volatility contraction on tf: setup bar = NR7 / NR4 / inside bar; trade the first close
    beyond its high/low during the NEXT tf bar (M1 closes)."""
    b = B(tf); rg = b.high - b.low
    if kind == "NR7": s = rg <= rg.rolling(7).min()
    elif kind == "NR4": s = rg <= rg.rolling(4).min()
    elif kind == "IB": s = (b.high < b.high.shift()) & (b.low > b.low.shift())
    elif kind == "NR7IB": s = (rg <= rg.rolling(7).min()) & (b.high < b.high.shift()) & (b.low > b.low.shift())
    k = np.nonzero(s.values)[0]; k = k[k + 1 < len(b)]
    ws = IDX.searchsorted(b.index[k + 1]); we = IDX.searchsorted(b.index[k + 1] + pd.Timedelta(TF[tf]))
    return _window_break(C, ws.astype(np.int64), we.astype(np.int64), b.high.values[k], b.low.values[k], 0)


def squeeze_break(tf, n=20, k=2.0, look=100, recent=5):
    b = B(tf); c = b.close; m = sma(c, n); sd = c.rolling(n).std(); up = m + k * sd; dn = m - k * sd
    bw = (up - dn) / m
    sq = (bw <= bw.rolling(look).min()).rolling(recent).max().shift().fillna(0) > 0
    cu = (c > up) & ~(c.shift() > up.shift()); cd = (c < dn) & ~(c.shift() < dn.shift())
    ev = np.where(sq & cu, 1.0, np.where(sq & cd, -1.0, 0.0))
    return event_m1(ev, tf)


# ---------------------------------------------------------------- mean reversion
def bb_fade(tf, n, k):
    c = B(tf).close; m = sma(c, n); sd = c.rolling(n).std()
    lo = c < m - k * sd; hi = c > m + k * sd
    ev = np.where(lo & ~lo.shift(fill_value=False), 1.0, np.where(hi & ~hi.shift(fill_value=False), -1.0, 0.0))
    return event_m1(ev, tf)


def rsi_fade(tf, n, thr):
    r = rsi(B(tf).close, n); rp = r.shift()
    ev = np.where((r < thr) & ~(rp < thr), 1.0, np.where((r > 100 - thr) & ~(rp > 100 - thr), -1.0, 0.0))
    return event_m1(ev, tf)


def daymean_fade(tf, kk):
    """Deviation of tf close from the running mean of today's tf closes (TWAP, VWAP proxy: no volume),
    in ATR_H1 units; fade the first cross beyond kk."""
    b = B(tf); c = b.close; d = b.index.normalize()
    tw = c.groupby(d).expanding().mean().reset_index(level=0, drop=True).reindex(b.index)
    a = atr_s(B("H1"), 14).reindex(b.index, method="ffill").shift()  # conservative lag
    z = (c - tw) / a
    lo = z < -kk; hi = z > kk
    ev = np.where(lo & ~lo.shift(fill_value=False), 1.0, np.where(hi & ~hi.shift(fill_value=False), -1.0, 0.0))
    return event_m1(ev, tf)


# ---------------------------------------------------------------- filters (causal M1 arrays)
_F = {}


def adx_tf(tf, n=14):
    b = B(tf); h, l, c = b.high, b.low, b.close
    upm = h.diff(); dnm = -l.diff()
    pdm = np.where((upm > dnm) & (upm > 0), upm, 0.0); ndm = np.where((dnm > upm) & (dnm > 0), dnm, 0.0)
    tr = pd.concat([h - l, (h - c.shift()).abs(), (l - c.shift()).abs()], axis=1).max(axis=1)
    a = tr.ewm(alpha=1 / n, adjust=False, min_periods=n).mean()
    pdi = pd.Series(pdm, b.index).ewm(alpha=1 / n, adjust=False, min_periods=n).mean() / a
    ndi = pd.Series(ndm, b.index).ewm(alpha=1 / n, adjust=False, min_periods=n).mean() / a
    dx = 100 * (pdi - ndi).abs() / (pdi + ndi)
    return dx.ewm(alpha=1 / n, adjust=False, min_periods=n).mean()


def filt(name):
    """Returns (allowed_mask, dir_constraint or None)."""
    if name in _F: return _F[name]
    hrs = IDX.hour.values
    if name == "none": r = (np.ones(N, bool), None)
    elif name == "sess7_17": r = ((hrs >= 7) & (hrs < 17), None)
    elif name == "sess12_17": r = ((hrs >= 12) & (hrs < 17), None)
    elif name == "notasia": r = ((hrs >= 6) & (hrs < 21), None)
    elif name.startswith("adx"):  # adxH1_25
        tf, th = name[3:].split("_"); a = state_m1(adx_tf(tf).values, tf); r = (a > float(th), None)
    elif name.startswith("volhi") or name.startswith("vollo"):  # volhiH1: ATR14 > its 500-bar median
        tf = name[5:]; a = atr_s(B(tf), 14); x = state_m1((a / a.rolling(500).median()).values, tf)
        r = ((x > 1) if name.startswith("volhi") else ((x > 0) & (x <= 1)), None)
    elif name.startswith("dtrend"):  # dtrend50: D1 close vs EMA50 D1 -> direction constraint
        n_ = int(name[6:]); c = B("D1").close; r = (np.ones(N, bool), state_m1(np.sign(c - ema(c, n_)).values, "D1"))
    elif name.startswith("h4trend"):
        n_ = int(name[7:]); c = B("H4").close; r = (np.ones(N, bool), state_m1(np.sign(c - ema(c, n_)).values, "H4"))
    _F[name] = r
    return r


def apply_filter(dirs, name):
    m, dc = filt(name)
    d = np.where(m, dirs, 0.0)
    if dc is not None: d = np.where(d == dc, d, 0.0)
    return d


# ---------------------------------------------------------------- evaluation
PMASK = {p: (IDX >= pd.Timestamp(a)) & (IDX < pd.Timestamp(b)) for p, (a, b) in H.PERIODS.items()}


def exits(atr, slk, tpr, trk, width=None):
    """sl = slk*ATR (or slk*width when width given, floored at 0.25*ATR); tp = tpr*sl; trail = trk*sl."""
    base = atr if width is None else np.maximum(width, 0.25 * atr)
    sl = slk * base
    tp = None if tpr is None else tpr * sl
    tr = None if trk is None else trk * sl
    return sl, tp, tr


def evaluate(dirs, sl, tp=None, trail=None, maxbars=0, periods=("IS",), side=0):
    d = np.asarray(dirs, float)
    if side: d = np.where(d == side, d, 0.0)
    m = np.zeros(N, bool)
    for p in periods: m |= PMASK[p]
    d = np.where(m, d, 0.0)
    tr = H.run(d, sl, tp, trail, maxbars)
    return H.stats(tr, periods), tr


def flat(st, prefix=""):
    o = {}
    for p, v in st.items():
        for k, x in v.items(): o[f"{p}_{k}"] = x
    return o


def st_donch_fresh(tf, n):
    b = B(tf); hh = b.high.rolling(n).max().shift(); ll = b.low.rolling(n).min().shift()
    up = b.close > hh; dn = b.close < ll
    ev = np.where(up & ~up.shift(fill_value=False), 1.0, np.where(dn & ~dn.shift(fill_value=False), -1.0, 0.0))
    return event_m1(ev, tf)


# ---------------------------------------------------------------- entry registry
def registry():
    """name -> (family, builder() -> (dirs, width_or_None), atr_tf, exit_group)"""
    E = {}
    for tf in TF:
        for n in (10, 20, 55):
            E[f"donch{n}_{tf}_flip"] = ("trend", lambda tf=tf, n=n: (trend_entry("donch", tf, (n,), "event"), None), tf, "trend")
            E[f"donch{n}_{tf}_state"] = ("trend", lambda tf=tf, n=n: (trend_entry("donch", tf, (n,), "state"), None), tf, "trend")
            E[f"donch{n}_{tf}_fresh"] = ("trend", lambda tf=tf, n=n: (st_donch_fresh(tf, n), None), tf, "trend")
        for f, s in ((10, 50), (20, 100), (50, 200)):
            for md in ("event", "state"):
                E[f"ema{f}x{s}_{tf}_{md}"] = ("trend", lambda tf=tf, f=f, s=s, md=md: (trend_entry("ma", tf, (f, s), md), None), tf, "trend")
        for n, m in ((10, 3.0), (10, 2.0)):
            for md in ("event", "state"):
                E[f"st{n}_{m}_{tf}_{md}"] = ("trend", lambda tf=tf, n=n, m=m, md=md: (trend_entry("st", tf, (n, m), md), None), tf, "trend")
    for ttf, etf in (("H1", "M15"), ("H4", "M15"), ("H4", "H1"), ("D1", "H1"), ("D1", "M15"), ("D1", "H4")):
        for td in ("ema50_200", "ema50slope"):
            for rn, th in ((2, 10), (2, 5), (14, 30), (14, 40)):
                E[f"pb_{ttf}{td}_{etf}rsi{rn}_{th}"] = ("pullback", lambda a=ttf, e=etf, td=td, rn=rn, th=th: (pullback(a, e, td, rn, th), None), etf, "trend")
    for r0, r1, t1 in ((0, 7, 12), (0, 7, 16), (0, 7, 20), (0, 8, 13), (7, 8, 12), (12, 13.5, 17), (13, 14.5, 20), (0, 13, 17)):
        for both in (0, 1):
            E[f"sess_{r0}-{r1}_to{t1}_b{both}"] = ("session", lambda r0=r0, r1=r1, t1=t1, both=both: session_break(r0, r1, t1, both), "H1", "session")
    for tf in ("H1", "H4", "D1"):
        for k in ("NR7", "NR4", "IB", "NR7IB"):
            E[f"vcb_{k}_{tf}"] = ("vcb", lambda tf=tf, k=k: setup_break(tf, k), tf, "session")
    for tf in ("M30", "H1", "H4", "D1"):
        for look in (50, 100):
            E[f"sqz{look}_{tf}"] = ("vcb", lambda tf=tf, look=look: (squeeze_break(tf, 20, 2.0, look), None), tf, "trend")
    for tf in ("M15", "M30", "H1", "H4"):
        for n, k in ((20, 2.0), (20, 2.5), (20, 3.0)):
            E[f"bbfade{n}_{k}_{tf}"] = ("meanrev", lambda tf=tf, n=n, k=k: (bb_fade(tf, n, k), None), tf, "mr")
        for n, th in ((2, 5), (2, 10), (14, 25), (14, 20)):
            E[f"rsifade{n}_{th}_{tf}"] = ("meanrev", lambda tf=tf, n=n, th=th: (rsi_fade(tf, n, th), None), tf, "mr")
    for tf in ("M15", "M30"):
        for kk in (1.5, 2.0, 3.0, 4.0):
            E[f"daymean{kk}_{tf}"] = ("meanrev", lambda tf=tf, kk=kk: (daymean_fade(tf, kk), None), tf, "mr")
    return E


def exit_grid(group, has_width):
    """list of (slmode, slk, tpr, trk, maxbars)."""
    G = []
    if group == "trend":
        for slk in (1.0, 1.5, 2.0, 3.0):
            for tpr in (1.5, 2.0, 3.0, 5.0):
                for trk in (None, 1.0):
                    G.append(("atr", slk, tpr, trk, 0))
            for trk in (1.0, 0.5, 1.5):
                G.append(("atr", slk, None, trk, 0))
    elif group == "session":
        sls = [("atr", 1.0), ("atr", 2.0)] + ([("w", 0.5), ("w", 1.0)] if has_width else [])
        for m, slk in sls:
            for mb in (0, 360):
                for tpr in (1.0, 1.5, 2.0, 3.0, 5.0):
                    G.append((m, slk, tpr, None, mb))
                G.append((m, slk, None, 1.0, mb)); G.append((m, slk, 3.0, 1.0, mb))
    elif group == "mr":
        for slk in (1.0, 1.5, 2.0, 3.0):
            for tpr in (0.5, 1.0, 1.5, 2.0):
                for mb in (0, 240, 1440):
                    G.append(("atr", slk, tpr, None, mb))
    return G


_EC = {}


def build(name, slmode, slk, tpr, trk, mb, filt_name="none", E=None):
    E = E or registry()
    fam, fn, atf, grp = E[name]
    if name not in _EC: _EC[name] = fn()
    d, w = _EC[name]
    a = ATRM1(atf)
    sl, tp, tr = exits(a, slk, tpr, trk, w if slmode == "w" else None)
    if filt_name != "none":
        for f in filt_name.split("+"): d = apply_filter(d, f)
    return d, sl, tp, tr, mb
