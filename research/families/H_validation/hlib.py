"""Shared statistics for family H (validation): bootstrap, HAC t, PSR/DSR, stationary bootstrap,
White RC / Hansen SPA, CSCV-PBO. All pure numpy/scipy."""
import numpy as np, pandas as pd
from scipy import stats as ss

SCR = "/tmp/claude-0/-home-user-trading-bridge/b109c4cd-e10b-5fab-96f6-d6f544632108/scratchpad/H"
PER = {"IS": ("2020-07-01", "2023-07-01"), "VAL": ("2023-07-01", "2025-01-01"),
       "HOLDOUT": ("2025-01-01", "2026-08-01"), "OOS": ("2023-07-01", "2026-08-01")}


def sl_period(x, p, col=None):
    a, b = PER[p]
    if isinstance(x.index, pd.DatetimeIndex) or col is None:
        idx = pd.to_datetime(x.index)
        return x[(idx >= a) & (idx < b)]
    t = x[col]
    return x[(t >= a) & (t < b)]


def tstat(x):
    x = np.asarray(x, float); n = len(x)
    return x.mean() / (x.std(ddof=1) / np.sqrt(n)) if n > 2 and x.std() > 0 else np.nan


def hac_t(x, lags=None):
    """Newey-West t-stat of the mean."""
    x = np.asarray(x, float); n = len(x); u = x - x.mean()
    L = lags if lags is not None else int(np.floor(4 * (n / 100) ** (2 / 9)))
    s = u @ u / n
    for l in range(1, L + 1):
        s += 2 * (1 - l / (L + 1)) * (u[l:] @ u[:-l]) / n
    return x.mean() / np.sqrt(s / n) if s > 0 else np.nan


def boot_ci(x, B=10000, seed=0, block=None):
    """95% CI of the mean. block=None -> iid; else stationary bootstrap with mean block length."""
    x = np.asarray(x, float); n = len(x); rng = np.random.default_rng(seed)
    if block is None:
        m = x[rng.integers(0, n, (B, n))].mean(1)
    else:
        m = x[stationary_idx(n, B, block, rng)].mean(1)
    return np.percentile(m, [2.5, 97.5])


def stationary_idx(n, B, block, rng):
    """Politis-Romano stationary bootstrap index matrix (B x n)."""
    p = 1.0 / block
    idx = np.empty((B, n), np.int64)
    idx[:, 0] = rng.integers(0, n, B)
    new = rng.random((B, n)) < p
    rnd = rng.integers(0, n, (B, n))
    for t in range(1, n):
        idx[:, t] = np.where(new[:, t], rnd[:, t], (idx[:, t - 1] + 1) % n)
    return idx


def psr(x, sr0=0.0):
    """Probabilistic Sharpe ratio (per-observation SR units)."""
    x = np.asarray(x, float); n = len(x)
    sr = x.mean() / x.std(ddof=1)
    g3 = ss.skew(x); g4 = ss.kurtosis(x, fisher=False)
    den = np.sqrt(max(1 - g3 * sr + (g4 - 1) / 4 * sr ** 2, 1e-12))
    return ss.norm.cdf((sr - sr0) * np.sqrt(n - 1) / den)


def sr0_trials(N, var_sr):
    """Expected maximum SR among N trials with zero true SR (Bailey & Lopez de Prado 2014)."""
    if N <= 1: return 0.0
    g = 0.5772156649
    return np.sqrt(var_sr) * ((1 - g) * ss.norm.ppf(1 - 1 / N) + g * ss.norm.ppf(1 - 1 / (N * np.e)))


def dsr(x, N, var_sr=None):
    x = np.asarray(x, float)
    v = var_sr if var_sr is not None else 1.0 / (len(x) - 1)
    return psr(x, sr0_trials(N, v))


def rc_spa(D, B=5000, block=10, seed=0):
    """D: T x K matrix of loss differentials (strategy - benchmark, higher is better).
    Returns White RC p-value (non-studentized) and Hansen SPA_c p-value (studentized, consistent)."""
    D = np.asarray(D, float)
    if D.ndim == 1: D = D[:, None]
    T, K = D.shape; rng = np.random.default_rng(seed)
    dbar = D.mean(0)
    idx = stationary_idx(T, B, block, rng)
    Mb = np.stack([D[idx[:, :], k].mean(1) for k in range(K)], 1)       # B x K bootstrap means
    om = np.sqrt(T) * Mb.std(0)                                          # bootstrap sd of sqrt(T)*mean
    om = np.where(om > 0, om, 1e-12)
    # White RC
    Vrc = np.sqrt(T) * dbar.max()
    Vrc_b = (np.sqrt(T) * (Mb - dbar)).max(1)
    p_rc = (Vrc_b >= Vrc).mean()
    # Hansen SPA (consistent recentering)
    tstat_ = np.sqrt(T) * dbar / om
    Vspa = max(tstat_.max(), 0)
    mu_c = np.where(tstat_ <= -np.sqrt(2 * np.log(np.log(T))), dbar, 0.0)   # Hansen (2005) consistent recentring
    Z = np.sqrt(T) * (Mb - dbar + mu_c) / om
    Vspa_b = np.maximum(Z.max(1), 0)
    p_spa = (Vspa_b >= Vspa).mean()
    return p_rc, p_spa


def cscv_pbo(M, S=16):
    """Bailey et al. CSCV. M: T x N matrix of returns (one column per trial). Returns PBO,
    logits, and (IS-best SR, OOS SR) pairs. Metric = Sharpe."""
    from itertools import combinations
    M = np.asarray(M, float); T, N = M.shape
    T2 = T - T % S; M = M[:T2]
    blocks = np.array_split(np.arange(T2), S)
    lam = []; perf = []
    for c in combinations(range(S), S // 2):
        tr = np.concatenate([blocks[i] for i in c]); te = np.concatenate([blocks[i] for i in range(S) if i not in c])
        def sr(X):
            s = X.std(0, ddof=1); return np.where(s > 0, X.mean(0) / np.where(s > 0, s, 1), -np.inf)
        a = sr(M[tr]); b = sr(M[te])
        n_star = int(np.argmax(a))
        rank = ss.rankdata(b)[n_star] / (N + 1)
        lam.append(np.log(rank / (1 - rank))); perf.append((a[n_star], b[n_star]))
    lam = np.array(lam)
    return (lam <= 0).mean(), lam, np.array(perf)
