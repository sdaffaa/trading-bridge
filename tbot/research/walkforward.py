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
        tr_end = t0 - pd.Timedelta(days=embargo_days)
        tr_start = max(pd.Timestamp(first_train), t0 - pd.DateOffset(months=train_months)) if train_months \
            else pd.Timestamp(first_train)
        out.append(Fold(str(tr_start.date()), str(tr_end.date()), str(t0.date()), str(t1.date())))
        t0 = t1
    return out


def score(daily: pd.DataFrame, trades: pd.DataFrame, start, end, min_trades: int) -> float:
    d = daily.loc[start:end]
    if trades.empty:
        return -np.inf
    tt = trades[(trades["entry_time"] >= pd.Timestamp(start, tz="UTC")) &
                (trades["entry_time"] < pd.Timestamp(end, tz="UTC"))]
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


def walk_forward(grid_results, folds: list[Fold], min_trades: int = 30):
    rows, oos = [], []
    for f in folds:
        scores = [score(d, t, f.train_start, f.train_end, min_trades) for (_, d, t, _) in grid_results]
        k = int(np.argmax(scores))
        params, d, t, _ = grid_results[k]
        test = d.loc[f.test_start:f.test_end]
        test = test[test.index < pd.Timestamp(f.test_end)]
        oos.append(test[["ret", "pnl", "active"]].assign(fold=f.test_start, params=str(params)))
        tt = t[(t["entry_time"] >= pd.Timestamp(f.test_start, tz="UTC")) &
               (t["entry_time"] < pd.Timestamp(f.test_end, tz="UTC"))] if not t.empty else t
        rows.append({"test_start": f.test_start, "test_end": f.test_end, "chosen": str(params),
                     "train_score": scores[k], "test_days": len(test), "test_trades": len(tt),
                     "test_ret": float((1 + test["ret"]).prod() - 1) if len(test) else np.nan,
                     "test_R": float((tt["net"] / tt["planned_risk"]).sum()) if len(tt) else 0.0})
    return pd.DataFrame(rows), (pd.concat(oos) if oos else pd.DataFrame())
