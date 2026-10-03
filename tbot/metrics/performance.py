"""Daily-equity and trade metrics (spec §8 of the brief).

Daily performance is measured on full liquidation equity (open positions marked at
bid for longs / ask for shorts) at the trading-day cutoff 17:00 America/New_York,
after all costs. Deposits/withdrawals: pass `flows` (per day, + = deposit) and
returns are computed time-weighted so flows never count as profit.
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def daily_returns(daily: pd.DataFrame, initial: float, flows: pd.Series | None = None) -> pd.Series:
    eq = daily["equity_end"]
    prev = eq.shift(1).fillna(initial)
    f = flows.reindex(eq.index).fillna(0.0) if flows is not None else 0.0
    return (eq - f) / prev - 1.0


def max_drawdown(equity: pd.Series) -> tuple[float, pd.Timestamp | None, pd.Timestamp | None, pd.Timestamp | None]:
    """Max drawdown fraction, peak time, trough time, recovery time (None if unrecovered)."""
    if equity.empty:
        return 0.0, None, None, None
    v = equity.to_numpy()
    peak = np.maximum.accumulate(v)
    dd = (peak - v) / peak
    j = int(np.argmax(dd))
    if dd[j] <= 0:
        return 0.0, None, None, None
    i = int(np.argmax(v[: j + 1] == peak[j]))
    rec = np.nonzero(v[j:] >= peak[j])[0]
    rec_t = equity.index[j + rec[0]] if len(rec) else None
    return float(dd[j]), equity.index[i], equity.index[j], rec_t


def longest_streak(mask: np.ndarray) -> int:
    best = cur = 0
    for m in mask:
        cur = cur + 1 if m else 0
        best = max(best, cur)
    return best


def summarize(res, initial: float, periods_per_year: float = 260.0) -> dict:
    """res: BacktestResult. Returns a flat dict of metrics (all after costs)."""
    tr, daily = res.trades, res.daily
    r = daily_returns(daily, initial)
    final = float(daily["equity_end"].iloc[-1]) if len(daily) else initial
    n_days = len(daily)
    active = daily["active"].to_numpy() if n_days else np.array([], bool)
    pnl = daily["pnl"].to_numpy() if n_days else np.array([])
    years = n_days / periods_per_year if n_days else np.nan
    out = {
        "initial": initial, "final_equity": final, "net_profit": final - initial,
        "cum_return": final / initial - 1,
        "cagr": (final / initial) ** (1 / years) - 1 if years and years > 0 and final > 0 else np.nan,
        "market_days": n_days, "active_days": int(active.sum()), "no_trade_days": int(n_days - active.sum()),
        "mean_daily_ret": float(r.mean()) if n_days else np.nan,
        "median_daily_ret": float(r.median()) if n_days else np.nan,
        "std_daily_ret": float(r.std(ddof=1)) if n_days > 1 else np.nan,
        "pct_profitable_days_all": float((pnl > 0).mean()) if n_days else np.nan,
        "pct_profitable_days_active": float((pnl[active] > 0).mean()) if active.any() else np.nan,
        "pct_losing_days_active": float((pnl[active] < 0).mean()) if active.any() else np.nan,
        "worst_day": float(r.min()) if n_days else np.nan,
        "best_day": float(r.max()) if n_days else np.nan,
    }
    if n_days:
        eqd = daily["equity_end"]
        wk = eqd.resample("W-FRI").last().dropna()
        mo = eqd.resample("ME").last().dropna()
        out["worst_week"] = float((wk / wk.shift(1).fillna(initial) - 1).min())
        out["worst_month"] = float((mo / mo.shift(1).fillna(initial) - 1).min())
        out["longest_losing_day_streak"] = longest_streak(pnl < 0)
        sd = r.std(ddof=1)
        out["sharpe_daily_ann"] = float(r.mean() / sd * np.sqrt(periods_per_year)) if sd > 0 else np.nan
        dn = r[r < 0].std(ddof=1)
        out["sortino_ann"] = float(r.mean() / dn * np.sqrt(periods_per_year)) if dn and dn > 0 else np.nan
    dd, pk, tr_t, rec = max_drawdown(res.equity)
    out.update({"max_dd": dd, "dd_peak": str(pk), "dd_trough": str(tr_t), "dd_recovered": str(rec),
                "dd_recovery_days": (rec - pk).days if rec is not None and pk is not None else None})
    out["exposure"] = res.exposure_bars / res.n_bars if res.n_bars else 0.0
    out["max_margin_used"] = res.max_margin_used
    out["n_ambiguous_bars"] = res.n_ambiguous
    out["n_trades"] = int(len(tr))
    if len(tr):
        net = tr["net"].to_numpy()
        wins, losses = net[net > 0], net[net < 0]
        out.update({
            "win_rate": float((net > 0).mean()),
            "expectancy": float(net.mean()),
            "expectancy_R": float((net / tr["planned_risk"].replace(0, np.nan)).mean()),
            "profit_factor": float(wins.sum() / -losses.sum()) if len(losses) else np.inf,
            "avg_win": float(wins.mean()) if len(wins) else 0.0,
            "avg_loss": float(losses.mean()) if len(losses) else 0.0,
            "longest_losing_trade_streak": longest_streak(net < 0),
            "total_commission": float(tr["commission"].sum()),
            "total_swap": float(tr["swap"].sum()),
            "total_slippage_cost": float(tr["slippage_cost"].sum()),
            "total_spread_cost": float(tr["spread_cost"].sum()),
            "gross_pnl": float(tr["gross"].sum()),
            "trades_per_active_day": len(tr) / max(1, int(active.sum())),
            "ambiguous_exits": int(tr["ambiguous"].sum()),
        })
        srt = np.sort(net)[::-1]
        for q in (0.01, 0.05):
            k = max(1, int(np.ceil(q * len(srt))))
            out[f"net_ex_top{int(q*100)}pct_trades"] = float(srt[k:].sum())
        if n_days:
            best = np.sort(pnl)[::-1]
            k = max(1, int(np.ceil(0.05 * n_days)))
            out["net_ex_top5pct_days"] = float(best[k:].sum())
        out["exit_reasons"] = tr["exit_reason"].value_counts().to_dict()
    out["decisions"] = dict(res.decisions)
    out["risk_events"] = len(res.risk_events)
    return out
