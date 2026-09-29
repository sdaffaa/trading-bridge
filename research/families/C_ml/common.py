"""Family C (ML / 'trading by feel') shared pipeline.

Decision rows = completed bars of a decision timeframe TF (M5/M15/H1). The model's
direction for bar b (known at b's close) is forward-filled to every M1 bar until the next
TF bar closes (via harness.htf_to_m1), so at ANY M1 bar where a consecutive trade must
start, a direction exists. Labels: harness.trade_once both ways at the first M1 bar after
the TF bar close (identical fills to run_consecutive).

Folds (new scope: only data from 2020-07 onward is used for training):
  * IS  (2020-07..2023-07): 6 half-year blocks, leave-one-block-out CV inside IS only,
    purged (train labels whose trade overlaps the test block are removed) + 5-day embargo
    after the test block.
  * VAL / HOLDOUT: expanding walk-forward in half-year blocks: train on all rows from
    2020-07 whose trade EXITED before the block start, predict the block.
"""
import os, sys
import numpy as np, pandas as pd
from numba import njit
sys.path.insert(0, "/home/user/trading-bridge/research")
import harness as H

START = pd.Timestamp("2020-07-01")
WARM = pd.Timestamp("2019-01-01")          # feature warm-up only
CACHE = "/tmp/claude-0/-home-user-trading-bridge/b109c4cd-e10b-5fab-96f6-d6f544632108/scratchpad/C_ml"
os.makedirs(CACHE, exist_ok=True)

BLOCKS = [("2020-07-01", "2021-01-01"), ("2021-01-01", "2021-07-01"), ("2021-07-01", "2022-01-01"),
          ("2022-01-01", "2022-07-01"), ("2022-07-01", "2023-01-01"), ("2023-01-01", "2023-07-01"),
          ("2023-07-01", "2024-01-01"), ("2024-01-01", "2024-07-01"), ("2024-07-01", "2025-01-01"),
          ("2025-01-01", "2025-07-01"), ("2025-07-01", "2026-01-01"), ("2026-01-01", "2026-08-01")]
IS_END = pd.Timestamp("2023-07-01")


@njit(cache=True)
def label_both(o, h, l, idx, dist, spread):
    n = len(idx)
    yL = np.zeros(n, np.int8); yS = np.zeros(n, np.int8)
    eL = np.zeros(n, np.int64); eS = np.zeros(n, np.int64)
    for k in range(n):
        if not (dist[k] > 0):
            continue
        a, b = H.trade_once(o, h, l, idx[k], 1, dist[k], spread); yL[k] = a; eL[k] = b
        a, b = H.trade_once(o, h, l, idx[k], -1, dist[k], spread); yS[k] = a; eS[k] = b
    return yL, yS, eL, eS


def m1_arrays():
    m1 = H.load_m1()
    return m1, m1.open.values, m1.high.values, m1.low.values


def _align(src, src_tf, dst_close_times):
    """Values of src (indexed by bar open) known at each dst close time."""
    s = src.copy(); s.index = s.index + pd.Timedelta(src_tf)
    return s.reindex(dst_close_times, method="ffill")


def base_feats(b, pre):
    c, h, l, o = b.close, b.high, b.low, b.open
    a = H.atr(b, 14)
    X = pd.DataFrame(index=b.index)
    for n in (1, 2, 3, 6, 12, 24, 48, 96):
        X[f"{pre}ret{n}"] = (c - c.shift(n)) / a
    for n in (9, 21, 50, 200):
        X[f"{pre}ema{n}"] = (c - c.ewm(span=n, adjust=False).mean()) / a
    d = c.diff()
    for n in (7, 14):
        up = d.clip(lower=0).ewm(alpha=1 / n).mean(); dn = (-d.clip(upper=0)).ewm(alpha=1 / n).mean()
        X[f"{pre}rsi{n}"] = 100 - 100 / (1 + up / dn)
    X[f"{pre}atr_ratio"] = a / a.rolling(200).mean()
    X[f"{pre}vol_ratio"] = d.rolling(6).std() / d.rolling(96).std()
    for k in range(3):   # candle anatomy of last 3 bars
        X[f"{pre}body{k}"] = ((c - o) / a).shift(k)
        X[f"{pre}uw{k}"] = ((h - np.maximum(o, c)) / a).shift(k)
        X[f"{pre}lw{k}"] = ((np.minimum(o, c) - l) / a).shift(k)
        X[f"{pre}rng{k}"] = ((h - l) / a).shift(k)
    for n in (12, 48, 200):
        hh, ll = h.rolling(n).max(), l.rolling(n).min()
        X[f"{pre}pos{n}"] = (c - ll) / (hh - ll)
        X[f"{pre}dhh{n}"] = (hh - c) / a
        X[f"{pre}dll{n}"] = (c - ll) / a
    # confirmed fractal swings (pivot of 5 bars known 2 bars later)
    ph = (h.shift(2) == h.rolling(5).max()); pl = (l.shift(2) == l.rolling(5).min())
    swh = h.shift(2).where(ph).ffill(); swl = l.shift(2).where(pl).ffill()
    X[f"{pre}dswh"] = (swh - c) / a; X[f"{pre}dswl"] = (c - swl) / a
    swh_prev = h.shift(2).where(ph).ffill().where(ph).ffill()  # placeholder same series
    # market structure: HH / HL counts over last 10 swing points (approx by last 20 bars)
    hi_seq = h.shift(2).where(ph); lo_seq = l.shift(2).where(pl)
    hh_flag = (hi_seq > hi_seq.ffill().shift(1)).astype(float).where(ph)
    hl_flag = (lo_seq > lo_seq.ffill().shift(1)).astype(float).where(pl)
    X[f"{pre}hh_cnt"] = hh_flag.fillna(0).rolling(30).sum() - (1 - hh_flag).fillna(0).rolling(30).sum()
    X[f"{pre}hl_cnt"] = hl_flag.fillna(0).rolling(30).sum() - (1 - hl_flag).fillna(0).rolling(30).sum()
    X[f"{pre}eff"] = (c - c.shift(24)).abs() / d.abs().rolling(24).sum()
    X[f"{pre}up_frac"] = (d > 0).astype(float).rolling(24).mean()
    return X, a


def build_dataset(TF):
    """Feature frame at decision-TF bar closes (index = bar open time), plus ATR series."""
    fn = f"{CACHE}/feat_{TF}.parquet"
    m1 = H.load_m1()
    m1w = m1[m1.index >= WARM]
    b = m1w.resample(TF).agg({"open": "first", "high": "max", "low": "min", "close": "last"}).dropna()
    if os.path.exists(fn):
        return b, pd.read_parquet(fn)
    X, a = base_feats(b, "")
    close_t = b.index + pd.Timedelta(TF)
    c = b.close
    for htf in ("15min", "1h", "4h"):
        if pd.Timedelta(htf) <= pd.Timedelta(TF):
            continue
        hb = m1w.resample(htf).agg({"open": "first", "high": "max", "low": "min", "close": "last"}).dropna()
        HX, ha = base_feats(hb, f"{htf}_")
        keep = [k for k in HX.columns if any(s in k for s in ("ret", "ema", "rsi14", "pos", "dsw", "hh_cnt", "hl_cnt", "atr_ratio", "body0", "eff"))]
        A = _align(HX[keep], htf, close_t); A.index = b.index
        X = X.join(A)
        hc = _align(hb.close, htf, close_t).values
        X[f"{htf}_since"] = (c.values - hc) / a.values
    # daily / weekly levels
    day = m1w.resample("1D").agg({"open": "first", "high": "max", "low": "min", "close": "last"}).dropna()
    wk = m1w.resample("W-SUN").agg({"open": "first", "high": "max", "low": "min", "close": "last"}).dropna()
    dA = H.atr(day, 14)
    pdh = _align(day.high, "1D", close_t).values; pdl = _align(day.low, "1D", close_t).values
    pdc = _align(day.close, "1D", close_t).values; datr = _align(dA, "1D", close_t).values
    s = pd.Series(np.ones(1)); 
    wk.index = wk.index - pd.Timedelta("6D")   # W-SUN label is week end; make it week start (Mon)
    pwh = _align(wk.high, "7D", close_t).values; pwl = _align(wk.low, "7D", close_t).values
    X["to_pdh"] = (pdh - c.values) / a.values; X["to_pdl"] = (c.values - pdl) / a.values
    X["from_pdc_d"] = (c.values - pdc) / datr
    X["pd_pos"] = (c.values - pdl) / (pdh - pdl)
    X["pw_pos"] = (c.values - pwl) / (pwh - pwl)
    X["to_pwh"] = (pwh - c.values) / datr; X["to_pwl"] = (c.values - pwl) / datr
    dkey = b.index.normalize()
    dh = b.high.groupby(dkey).cummax(); dl = b.low.groupby(dkey).cummin()
    dO = b.open.groupby(dkey).transform("first")
    X["dpos"] = (c - dl) / (dh - dl); X["drange_d"] = (dh - dl) / datr
    X["from_dopen"] = (c - dO) / a
    X["datr_ratio"] = datr / pd.Series(datr).rolling(20 * 24).mean().values
    X["r10"] = (c % 10) / 10; X["r50"] = (c % 50) / 50
    hr = close_t.hour + close_t.minute / 60
    X["hour"] = hr; X["dow"] = close_t.dayofweek
    X["hsin"] = np.sin(2 * np.pi * hr / 24); X["hcos"] = np.cos(2 * np.pi * hr / 24)
    X = X.replace([np.inf, -np.inf], np.nan).astype(np.float32)
    X.to_parquet(fn)
    return b, X


def dist_series(b, TF, spec):
    """Stop distance known at decision-bar close. spec: ('atr', k, atr_tf) or ('usd', v)."""
    close_t = b.index + pd.Timedelta(TF)
    if spec[0] == "usd":
        return np.full(len(b), float(spec[1]))
    k, atf = spec[1], spec[2]
    m1 = H.load_m1(); m1w = m1[m1.index >= WARM]
    ab = m1w.resample(atf).agg({"open": "first", "high": "max", "low": "min", "close": "last"}).dropna()
    return k * _align(H.atr(ab, 14), atf, close_t).values


def dist_m1(spec):
    m1 = H.load_m1()
    if spec[0] == "usd":
        return np.full(len(m1), float(spec[1]))
    return spec[1] * H.htf_to_m1(H.atr(H.bars(spec[2]), 14), spec[2])


def spec_name(spec):
    return f"{spec[1]}usd" if spec[0] == "usd" else f"{spec[1]}xATR{spec[2]}"


def labels(b, TF, spec):
    fn = f"{CACHE}/lab_{TF}_{spec_name(spec)}.parquet"
    if os.path.exists(fn):
        return pd.read_parquet(fn)
    m1, o, h, l = m1_arrays()
    idx = m1.index.searchsorted(b.index + pd.Timedelta(TF))
    dist = dist_series(b, TF, spec)
    ok = idx < len(m1)
    idx2 = np.where(ok, idx, 0)
    yL, yS, eL, eS = label_both(o, h, l, idx2.astype(np.int64), np.where(ok, dist, np.nan), H.SPREAD)
    L = pd.DataFrame({"i": idx2, "yL": yL, "yS": yS, "eL": eL, "eS": eS, "dist": dist}, index=b.index)
    L = L[ok & (L.yL != 0) & (L.yS != 0)]
    L.to_parquet(fn)
    return L


def folds(index, i_arr, e_arr, strict=False):
    """Yield (block_id, train_mask, test_mask). e_arr = max exit M1 idx of each row."""
    m1 = H.load_m1()
    t = index
    for bi, (a, z) in enumerate(BLOCKS):
        a, z = pd.Timestamp(a), pd.Timestamp(z)
        te = (t >= a) & (t < z)
        if te.sum() == 0:
            continue
        ia = m1.index.searchsorted(a); iz = m1.index.searchsorted(z)
        if a < IS_END and not strict:   # LOBO-CV inside IS
            ins = (t >= START) & (t < IS_END)
            before = ins & (t < a) & (e_arr < ia)
            after = ins & (t >= z + pd.Timedelta("5D"))
            tr = before | after
        else:            # expanding walk-forward
            tr = (t >= START) & (e_arr < ia)
        if tr.sum() < 1000:
            continue
        yield bi, tr, te


def evaluate(pred_side, b, TF, spec):
    """pred_side: +1/-1 per decision-TF bar (NaN allowed outside data). Returns harness stats."""
    s = pd.Series(pred_side, index=b.index)
    dirs = H.htf_to_m1(s, TF)
    m1 = H.load_m1()
    dirs = np.where(m1.index >= START, dirs, np.nan)
    tr = H.run_consecutive(dirs, dist_m1(spec))
    return H.stats(tr), tr
