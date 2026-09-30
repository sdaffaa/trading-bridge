"""Signal builders (all causal: value at bar t uses closes <= t). Return raw forecast Series on G.B index,
normalised so that mean |forecast| over IS ~= 1 (scalar fit on IS only), capped at +-2."""
import numpy as np, pandas as pd
import common as G

C, LR = G.C, G.LR
IS_MASK = (C.index >= G.PER["IS"][0]) & (C.index < G.PER["IS"][1])
D = 23  # bars per trading day


def scale_cap(f, cap=2.0):
    s = f[IS_MASK].abs().mean()
    return (f / s).clip(-cap, cap) if s > 0 else f


def sigma_1h(span=24 * 25):
    return LR.ewm(span=span, min_periods=D * 10).std()


def tsmom_sign(h):
    return np.sign(np.log(C).diff(h)).fillna(0.0)


def tsmom_ra(h):
    r = np.log(C).diff(h)
    return scale_cap(r / (sigma_1h() * np.sqrt(h))).fillna(0.0)


def ewmac(fast, slow=None):
    slow = slow or 4 * fast
    raw = (C.ewm(span=fast).mean() - C.ewm(span=slow).mean()) / (C * sigma_1h() * np.sqrt(D))
    return scale_cap(raw).fillna(0.0)


def blend(fs, cap=2.0):
    f = sum(fs) / len(fs)
    return scale_cap(f, cap)            # FDM: rescale blended forecast to mean|f|=1 on IS


def mode(f, m):
    return f.clip(lower=0) if m == "LF" else f


def to_pos(f, target=0.10, buf=0.10, hours=None):
    return G.buffer(G.vt(f, target), buf, target, hours)


# ---------------- Kalman local-linear-trend on vol-normalised price path ----------------
from numba import njit


@njit(cache=True)
def _kf_llt(y, q_level, q_slope, r):
    n = len(y)
    lv = y[0]; sl = 0.0
    P00, P01, P11 = 1.0, 0.0, 1.0
    out_s = np.zeros(n); out_sd = np.zeros(n)
    for t in range(n):
        # predict
        lv = lv + sl
        P00n = P00 + 2 * P01 + P11 + q_level
        P01n = P01 + P11
        P11n = P11 + q_slope
        # update
        S_ = P00n + r
        K0 = P00n / S_; K1 = P01n / S_
        e = y[t] - lv
        lv = lv + K0 * e; sl = sl + K1 * e
        P00 = (1 - K0) * P00n
        P01 = (1 - K0) * P01n
        P11 = P11n - K1 * P01n
        out_s[t] = sl; out_sd[t] = np.sqrt(max(P11, 1e-12))
    return out_s, out_sd


def norm_path():
    z = (LR / sigma_1h().shift(1)).clip(-10, 10).fillna(0.0)
    return z.cumsum()


def kalman(q_level, q_slope, r=1.0, kind="slope"):
    y = norm_path().values
    s, sd = _kf_llt(y, q_level, q_slope, r)
    s = pd.Series(s, index=C.index); sd = pd.Series(sd, index=C.index)
    if kind == "slope":
        return scale_cap(s)
    if kind == "tstat":
        return scale_cap(s / sd)
    raise ValueError


# ---------------- mean reversion ----------------
@njit(cache=True)
def _band(z, zin, zout, gate):
    n = len(z); out = np.zeros(n); cur = 0.0
    for i in range(n):
        zi = z[i]
        if np.isnan(zi):
            cur = 0.0
        elif cur == 0.0:
            if gate[i]:
                if zi > zin: cur = -1.0
                elif zi < -zin: cur = 1.0
        elif cur > 0 and zi > -zout: cur = 0.0
        elif cur < 0 and zi < zout: cur = 0.0
        out[i] = cur
    return out


def zscore_dev(L):
    lp = np.log(C)
    dev = lp - lp.ewm(span=L).mean()
    return dev / dev.rolling(max(L * 4, 48)).std()


def band(z, zin, zout, gate=None):
    g = np.ones(len(z), dtype=np.bool_) if gate is None else gate.reindex(z.index).fillna(False).values.astype(np.bool_)
    return pd.Series(_band(z.values, zin, zout, g), index=z.index)


def rolling_tests(W, step=23, L=48):
    """Every `step` bars, on the last W bars: variance ratio VR(4) of 1h log returns, Hurst (R/S via
    aggregated variance slope), ADF p-value and AR(1) half-life of the EMA(L)-deviation. Causal (ffill)."""
    from statsmodels.tsa.stattools import adfuller
    lp = np.log(C).values; r = LR.values
    dev = (np.log(C) - np.log(C).ewm(span=L).mean()).values
    idx = np.arange(W, len(C), step)
    vr = np.full(len(C), np.nan); hu = vr.copy(); adf = vr.copy(); hl = vr.copy()
    for i in idx:
        x = r[i - W + 1:i + 1]
        v1 = x.var()
        x4 = np.convolve(x, np.ones(4), "valid")
        vr[i] = x4.var() / (4 * v1) if v1 > 0 else np.nan
        # Hurst from aggregated variance: var(sum over k) ~ k^(2H)
        ks = np.array([1, 2, 4, 8, 16]); vs = []
        for k in ks:
            m = len(x) // k; vs.append(x[:m * k].reshape(m, k).sum(1).var())
        hu[i] = np.polyfit(np.log(ks), np.log(np.array(vs) + 1e-30), 1)[0] / 2
        d = dev[i - W + 1:i + 1]
        adf[i] = adfuller(d, maxlag=1, autolag=None, result_object=False)[1]
        b = np.polyfit(d[:-1], np.diff(d), 1)[0]
        hl[i] = -np.log(2) / np.log(1 + b) if -1 < b < 0 else np.inf
    f = lambda a: pd.Series(a, index=C.index).ffill()
    return f(vr), f(hu), f(adf), f(hl)


# ---------------- daily (NY 17:00 roll) helpers & regime models ----------------
def daily_close():
    return C.groupby(G.TDAY.values).last()


def daily_to_bars(s):
    """value computed at close of trading day d -> applied to all 1h bars of trading day d+1 (causal)."""
    s = s.copy(); s.index = pd.to_datetime(s.index)
    days = pd.DatetimeIndex(sorted(set(G.TDAY.values)))
    s = s.reindex(days).ffill().shift(1)
    return pd.Series(s.reindex(G.TDAY.values).values, index=C.index)


def daily_feats():
    dc = daily_close(); dr = np.log(dc).diff()
    rv = LR.pow(2).groupby(G.TDAY.values).sum().pow(0.5)
    X = pd.DataFrame({"r": dr, "lrv": np.log(rv.replace(0, np.nan))}).dropna()
    X = X[X.index >= "2015-01-01"]
    return X


def _forward_filter(model, X):
    """causal filtered state probabilities P(s_t | x_1..t) using a fitted hmmlearn GaussianHMM."""
    from scipy.stats import multivariate_normal
    K = model.n_components
    ll = np.column_stack([multivariate_normal(model.means_[k], model.covars_[k], allow_singular=True).logpdf(X) for k in range(K)])
    A = model.transmat_; a = model.startprob_.copy(); out = np.zeros((len(X), K))
    for t in range(len(X)):
        if t > 0:
            a = out[t - 1] @ A
        l = ll[t] - ll[t].max(); p = a * np.exp(l); out[t] = p / p.sum()
    return out


def hmm_expanding(K=2, feats=("r", "lrv"), refit="QS", start="2019-01-01", seed=0):
    """Expanding-window GaussianHMM refit each quarter on data < refit date; filtered probs for the next quarter.
    States are relabelled by ascending mean realised vol (state 0 = calmest). Returns DataFrame of
    probs + expected next-day return (in daily units), indexed by trading day."""
    from hmmlearn.hmm import GaussianHMM
    X = daily_feats()[list(feats)]
    dates = pd.date_range(start, X.index[-1] + pd.Timedelta(days=92), freq=refit)
    rows = []
    for i in range(len(dates) - 1):
        tr = X[X.index < dates[i]]
        m = GaussianHMM(K, covariance_type="full", n_iter=200, random_state=seed).fit(tr.values)
        vcol = list(feats).index("lrv") if "lrv" in feats else 0
        order = np.argsort(m.means_[:, vcol] if "lrv" in feats else np.sqrt(m.covars_[:, 0, 0]))
        P = _forward_filter(m, X[X.index < dates[i + 1]].values)
        seg = (X.index >= dates[i]) & (X.index < dates[i + 1])
        P = P[seg[:len(P)]][:, order]
        mu = m.means_[order, list(feats).index("r")] if "r" in feats else np.zeros(K)
        A = m.transmat_[np.ix_(order, order)]
        er = (P @ A) @ mu
        for d, p, e in zip(X.index[seg], P, er):
            rows.append(dict(day=d, er=e, **{f"p{k}": p[k] for k in range(K)}))
    return pd.DataFrame(rows).set_index("day")


def garch_vol(fit_end=None):
    """GARCH(1,1) with Student-t on daily % returns, fitted on IS (2020-07..2023-06) only; fixed params
    run over all data -> one-step-ahead annualised vol forecast for next day (indexed by the day it is known)."""
    from arch import arch_model
    dr = np.log(daily_close()).diff().dropna() * 100
    dr = dr[dr.index >= "2015-01-01"]
    fit = dr[(dr.index >= G.PER["IS"][0]) & (dr.index < G.PER["IS"][1])]
    am = arch_model(fit, mean="Constant", vol="GARCH", p=1, q=1, dist="t").fit(disp="off")
    mu, om, al, be = am.params["mu"], am.params["omega"], am.params["alpha[1]"], am.params["beta[1]"]
    e = (dr - mu).values; h = np.zeros(len(e)); h[0] = e[:250].var()
    for t in range(1, len(e)):
        h[t] = om + al * e[t - 1] ** 2 + be * h[t - 1]
    hn = om + al * e ** 2 + be * h        # forecast for next day, known at close of day t
    return pd.Series(np.sqrt(hn * 260) / 100, index=dr.index), am.params
