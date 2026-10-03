"""Walk-forward selection over a pre-registered parameter grid.

Procedure (frozen in RESEARCH_PLAN.md):
 1. Each grid point is backtested ONCE over [dev_start, wf_end] with the full engine
    (fractional sizing => window returns are ~scale-invariant; approximation noted).
 2. For each fold: score every grid point on its TRAIN window (data strictly before
    the test window, separated by an embargo), pick the best, record its TEST-window
    daily returns. Strategies are flat by 16:30 NY each day (H1-H4) or hold < 1 day
    (H5), so with a >=1 trading-day embargo no trade spans the boundary.
 3. Stitch test windows -> out-of-sample series. Every grid point counts as a trial.
"""
from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass

import numpy as np
import pandas as pd

from tbot.engine.backtest import run_backtest
from tbot.metrics.performance import summarize


@dataclass
class Fold:
    train_start: str
    train_end: str
    test_start: str
    test_end: str


def make_folds(first_train: str, wf_start: str, wf_end: str, test_months: int = 6,
               train_months: int | None = 36, embargo_days: int = 1) -> list[Fold]:
    out = []
    t0 = pd.Timestamp(wf_start)
    end = pd.Timestamp(wf_end)
    while t0 < end:
        t1 = min(t0 + pd.DateOffset(months=test_months), end)
        # train window is inclusive of tr_end: leave `embargo_days` full days unused before t0
        tr_end = t0 - pd.Timedelta(days=embargo_days + 1)
        tr_start = max(pd.Timestamp(first_train), t0 - pd.DateOffset(months=train_months)) if train_months \
            else pd.Timestamp(first_train)
        out.append(Fold(str(tr_start.date()), str(tr_end.date()), str(t0.date()), str(t1.date())))
        t0 = t1
    return out


def in_days(trades: pd.DataFrame, start, end_excl) -> pd.DataFrame:
    """Trades whose ENTRY trading day (17:00 NY cutoff) is in [start, end_excl)."""
    if trades.empty:
        return trades
    return trades[(trades["entry_day"] >= pd.Timestamp(start)) & (trades["entry_day"] < pd.Timestamp(end_excl))]


def score(daily: pd.DataFrame, trades: pd.DataFrame, start, end, min_trades: int) -> float:
    """Train score on [start, end] inclusive (daily labels and trade entry days alike)."""
    d = daily.loc[start:end]
    if trades.empty:
        return -np.inf
    tt = in_days(trades, start, pd.Timestamp(end) + pd.Timedelta(days=1))
    if len(tt) < min_trades or len(d) < 20:
        return -np.inf
    r = d["ret"]
    sd = r.std(ddof=1)
    return float(r.mean() / sd) if sd > 0 else -np.inf


def _run_one(args):
    cls, params, bars, spec, rcfg, ecfg, bal = args
    sig = cls(**params).signals(bars)
    res = run_backtest(bars, sig, spec, rcfg, ecfg, bal)
    return params, res.daily, res.trades, summarize(res, bal)


def run_grid(cls, bars, spec, rcfg, ecfg, bal, workers: int = 4):
    jobs = [(cls, p, bars, spec, rcfg, ecfg, bal) for p in cls.grid()]
    if workers > 1:
        with ProcessPoolExecutor(workers) as ex:
            return list(ex.map(_run_one, jobs))
    return [_run_one(j) for j in jobs]


ABSTAIN = "ABSTAIN"


def walk_forward(grid_results, folds: list[Fold], min_trades: int = 30, fixed_choice: list | None = None):
    """fixed_choice: per-fold chosen param strings from a previous (base) run — used to evaluate
    stress scenarios on the SAME selections instead of re-optimising under stress."""
    rows, oos = [], []
    by = {str(p): (d, t) for p, d, t, _ in grid_results}
    ref_daily = grid_results[0][1]
    for i, f in enumerate(folds):
        if fixed_choice is None:
            scores = [score(d, t, f.train_start, f.train_end, min_trades) for (_, d, t, _) in grid_results]
            k = int(np.argmax(scores))
            chosen = str(grid_results[k][0]) if np.isfinite(scores[k]) else ABSTAIN
            sc = scores[k]
        else:
            chosen, sc = fixed_choice[i], np.nan
        if chosen == ABSTAIN:   # no grid point qualified: stay flat (review defect 7)
            test = ref_daily.loc[f.test_start:f.test_end]
            test = test[test.index < pd.Timestamp(f.test_end)].copy()
            test[["ret", "pnl"]] = 0.0
            test["active"] = False
            tt = pd.DataFrame()
        else:
            d, t = by[chosen]
            test = d.loc[f.test_start:f.test_end]
            test = test[test.index < pd.Timestamp(f.test_end)]
            tt = in_days(t, f.test_start, f.test_end)
        oos.append(test[["ret", "pnl", "active"]].assign(fold=f.test_start, params=chosen))
        rows.append({"test_start": f.test_start, "test_end": f.test_end, "chosen": chosen,
                     "train_score": sc, "test_days": len(test), "test_trades": len(tt),
                     "test_ret": float((1 + test["ret"]).prod() - 1) if len(test) else np.nan,
                     "test_R": float((tt["net"] / tt["planned_risk"]).sum()) if len(tt) else 0.0})
    return pd.DataFrame(rows), (pd.concat(oos) if oos else pd.DataFrame())
