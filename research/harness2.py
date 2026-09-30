"""Profit harness (objective = account profit at the end of each day).

Constraints removed: no 1:1 requirement, waiting between trades allowed (dir 0 = stay flat),
any SL/TP geometry, optional trailing stop and time exit. Still enforced:
  * causal signals (value at M1 bar i uses only bars < i; use harness.htf_to_m1),
  * realistic fills on BID M1 bars: buy at ask = bid + SPREAD, sell at bid; long exits on bid,
    short exits on ask; if SL and TP are both inside one M1 bar -> SL first (conservative),
  * one position at a time per strategy,
  * results in R = P&L / initial SL distance (1R = the amount risked per trade).
Periods (last 6 years): IS 2020-07..2023-06 (select), VAL 2023-07..2024-12, HOLDOUT 2025-01..2026-07.
A strategy is CREDIBLE only if total R > 0 in IS, VAL and HOLDOUT, and it was selected on IS
(optionally IS+VAL) only.
"""
import numpy as np
import pandas as pd
from numba import njit
import harness as H

SPREAD = H.SPREAD
PERIODS = H.PERIODS
load_m1, bars, htf_to_m1, atr = H.load_m1, H.bars, H.htf_to_m1, H.atr


@njit(cache=True)
def _run(o, h, l, c, dirs, sld, tpd, trail, maxbars, spread, reenter_same_bar):
    """dirs: +1/-1/0 per bar. sld: SL distance. tpd: TP distance (<=0 or nan = no TP).
    trail: trailing-stop distance (<=0 = none; trails from best price, never loosens).
    maxbars: time exit after N M1 bars (<=0 = none), exit at that bar's close."""
    n = len(o)
    ent = np.empty(n, np.int64); ex = np.empty(n, np.int64)
    rr = np.empty(n, np.float64); side = np.empty(n, np.int8)
    k = 0; i = 0
    while i < n:
        d = dirs[i]; sl = sld[i]
        if d == 0 or np.isnan(d) or not (sl > 0):
            i += 1
            continue
        tp = tpd[i]; tr = trail[i]; mb = maxbars
        if d > 0:
            e = o[i] + spread; stop = e - sl; best = e
        else:
            e = o[i]; stop = e + sl; best = e
        j = i; exitp = np.nan
        while j < n:
            if d > 0:
                if l[j] <= stop:
                    exitp = stop; break
                if tp > 0 and h[j] >= e + tp:
                    exitp = e + tp; break
                if tr > 0:
                    if h[j] > best: best = h[j]
                    ns = best - tr
                    if ns > stop: stop = ns
            else:
                if h[j] + spread >= stop:
                    exitp = stop; break
                if tp > 0 and l[j] + spread <= e - tp:
                    exitp = e - tp; break
                if tr > 0:
                    if l[j] + spread < best: best = l[j] + spread
                    ns = best + tr
                    if ns < stop: stop = ns
            if mb > 0 and j - i + 1 >= mb:
                exitp = c[j] if d > 0 else c[j] + spread
                break
            j += 1
        if j >= n:
            break
        ent[k] = i; ex[k] = j; side[k] = 1 if d > 0 else -1
        rr[k] = ((exitp - e) if d > 0 else (e - exitp)) / sl
        k += 1
        i = j + 1
    return ent[:k], ex[:k], rr[:k], side[:k]


def run(dirs, sl, tp=None, trail=None, maxbars=0, spread=SPREAD):
    m1 = load_m1(); n = len(m1)
    f = lambda x: np.full(n, -1.0) if x is None else (np.full(n, float(x)) if np.isscalar(x) else np.asarray(x, np.float64))
    ent, ex, rr, side = _run(m1.open.values, m1.high.values, m1.low.values, m1.close.values,
                             np.asarray(dirs, np.float64), f(sl), f(tp), f(trail), int(maxbars), spread, False)
    return pd.DataFrame({"t": m1.index[ent], "exit_t": m1.index[ex], "side": side, "R": rr})


def daily(tr):
    """Daily P&L in R, booked on exit date (what the account shows at end of day)."""
    return tr.groupby(tr.exit_t.dt.date).R.sum().round(9)  # round away float noise (+1R-1R != 1e-14)


def stats(tr, periods=("IS", "VAL", "HOLDOUT")):
    out = {}
    dd_all = daily(tr)
    for p in periods:
        a, b = PERIODS[p]
        x = tr[(tr.exit_t >= a) & (tr.exit_t < b)]
        if len(x) == 0:
            out[p] = dict(n=0, totR=0.0); continue
        day = dd_all[(dd_all.index >= pd.Timestamp(a).date()) & (dd_all.index < pd.Timestamp(b).date())]
        eq = day.cumsum()
        wins, losses = x.R[x.R > 0].sum(), -x.R[x.R < 0].sum()
        out[p] = dict(n=len(x), totR=round(x.R.sum(), 1), R_trade=round(x.R.mean(), 3),
                      wr=round((x.R > 0).mean() * 100, 1), PF=round(wins / losses, 2) if losses > 0 else np.inf,
                      green_days=round((day > 0).mean() * 100, 1), R_day=round(day.mean(), 3),
                      maxDD=round((eq - eq.cummax()).min(), 1),
                      green_months=round((day.groupby(pd.to_datetime(day.index).to_period("M")).sum() > 0).mean() * 100, 1))
    return out


def credible(st):
    return all(st[p].get("totR", 0) > 0 for p in ("IS", "VAL", "HOLDOUT"))


def fmt(name, st):
    s = f"{name:<40}"
    for p, v in st.items():
        s += (f" | {p}: n={v.get('n',0)} R={v.get('totR','-')} R/t={v.get('R_trade','-')} PF={v.get('PF','-')}"
              f" gd={v.get('green_days','-')}% dd={v.get('maxDD','-')}")
    return s
