"""Uncertainty and multiple-testing tools.

* stationary_bootstrap: Politis & Romano (1994) block bootstrap for serially
  dependent daily returns. Assumes stationarity within the sample; it does NOT
  capture regime changes outside the sample. Not a guarantee of future results.
* deflated_sharpe: Bailey & Lopez de Prado (2014). Probability that the true
  Sharpe > 0 after accounting for the number of trials and non-normality.
  Assumes the trials' Sharpe ratios are roughly independent draws; correlated
  trials make N an over-count (conservative).
* holm / benjamini_hochberg: family-wise / FDR corrections for per-hypothesis p-values.
"""
from __future__ import annotations

import numpy as np
from scipy import stats


def stationary_bootstrap_idx(n: int, mean_block: float, rng: np.random.Generator) -> np.ndarray:
    p = 1.0 / mean_block
    idx = np.empty(n, dtype=int)
    idx[0] = rng.integers(n)
    jumps = rng.random(n) < p
    starts = rng.integers(n, size=n)
    for i in range(1, n):
        idx[i] = starts[i] if jumps[i] else (idx[i - 1] + 1) % n
    return idx


def bootstrap_stats(x: np.ndarray, n_boot: int = 2000, mean_block: float = 5.0, seed: int = 0,
                    periods: float = 260.0) -> dict:
    x = np.asarray(x, float)
    x = x[np.isfinite(x)]
    rng = np.random.default_rng(seed)
    means, sharpes, totals = np.empty(n_boot), np.empty(n_boot), np.empty(n_boot)
    for b in range(n_boot):
        s = x[stationary_bootstrap_idx(len(x), mean_block, rng)]
        means[b] = s.mean()
        sd = s.std(ddof=1)
        sharpes[b] = s.mean() / sd * np.sqrt(periods) if sd > 0 else 0.0
        totals[b] = np.prod(1 + s) - 1
    q = lambda a: (float(np.quantile(a, 0.025)), float(np.quantile(a, 0.975)))
    return {"mean_ci95": q(means), "sharpe_ci95": q(sharpes), "total_ret_ci95": q(totals),
            "p_mean_le_0": float((means <= 0).mean()), "p_total_le_0": float((totals <= 0).mean()),
            "n": len(x), "mean_block": mean_block, "n_boot": n_boot, "seed": seed}


def sharpe_ratio(x: np.ndarray) -> float:
    x = np.asarray(x, float)
    sd = x.std(ddof=1)
    return float(x.mean() / sd) if sd > 0 else 0.0


def probabilistic_sharpe(x: np.ndarray, sr_benchmark: float = 0.0) -> float:
    """PSR: P(true per-period SR > benchmark) given sample skew/kurtosis."""
    x = np.asarray(x, float)
    n = len(x)
    sr = sharpe_ratio(x)
    g3 = stats.skew(x)
    g4 = stats.kurtosis(x, fisher=False)
    denom = np.sqrt(max(1e-12, 1 - g3 * sr + (g4 - 1) / 4 * sr ** 2))
    return float(stats.norm.cdf((sr - sr_benchmark) * np.sqrt(n - 1) / denom))


def expected_max_sharpe(n_trials: int, var_trial_sr: float) -> float:
    """Expected max of N per-period SR estimates under the null (true SR = 0)."""
    if n_trials <= 1:
        return 0.0
    g = 0.5772156649
    z1 = stats.norm.ppf(1 - 1.0 / n_trials)
    z2 = stats.norm.ppf(1 - 1.0 / (n_trials * np.e))
    return float(np.sqrt(var_trial_sr) * ((1 - g) * z1 + g * z2))


def deflated_sharpe(x: np.ndarray, n_trials: int, var_trial_sr: float | None = None) -> dict:
    """var_trial_sr=None -> null estimator variance 1/(T-1) (DECISIONS.md D-009): the dispersion of
    per-period SR estimates of N skill-less trials. Empirical cross-trial variance is NOT used by
    default because cost-driven negative strategies inflate it and make SR0 meaningless."""
    x = np.asarray(x, float)
    v = 1.0 / max(1, len(x) - 1) if var_trial_sr is None else var_trial_sr
    sr0 = expected_max_sharpe(n_trials, v)
    return {"sr": sharpe_ratio(x), "sr0": sr0, "n_trials": n_trials, "var_used": v,
            "dsr": probabilistic_sharpe(x, sr0)}


def holm(pvals: list[float]) -> list[float]:
    p = np.asarray(pvals, float)
    m = len(p)
    order = np.argsort(p)
    adj = np.empty(m)
    run = 0.0
    for k, i in enumerate(order):
        run = max(run, (m - k) * p[i])
        adj[i] = min(1.0, run)
    return adj.tolist()


def benjamini_hochberg(pvals: list[float]) -> list[float]:
    p = np.asarray(pvals, float)
    m = len(p)
    order = np.argsort(p)[::-1]
    adj = np.empty(m)
    run = 1.0
    for k, i in enumerate(order):
        rank = m - k
        run = min(run, p[i] * m / rank)
        adj[i] = run
    return adj.tolist()


def drop_trades_sim(net: np.ndarray, drop_frac: float, n_sim: int = 2000, seed: int = 0) -> dict:
    """Randomly remove a fraction of trades (missed fills/outages); additive P&L approximation."""
    rng = np.random.default_rng(seed)
    net = np.asarray(net, float)
    tot = np.empty(n_sim)
    for s in range(n_sim):
        keep = rng.random(len(net)) >= drop_frac
        tot[s] = net[keep].sum()
    return {"drop_frac": drop_frac, "p5": float(np.quantile(tot, 0.05)), "median": float(np.median(tot)),
            "p_le_0": float((tot <= 0).mean())}


def loss_clustering(daily_pnl: np.ndarray) -> dict:
    """Lag-1 autocorrelation of daily P&L and of loss indicator (clustering of losses)."""
    x = np.asarray(daily_pnl, float)
    if len(x) < 3:
        return {}
    lossy = (x < 0).astype(float)
    ac = lambda a: float(np.corrcoef(a[:-1], a[1:])[0, 1]) if a.std() > 0 else 0.0
    return {"ac1_pnl": ac(x), "ac1_loss_indicator": ac(lossy)}
