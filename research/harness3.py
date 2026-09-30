"""Quant harness: continuous / fractional positions (vol targeting, TSMOM, Kalman, OU, HMM...).

A strategy is a target position series `pos` in units of "fraction of equity notional"
(e.g. +1 = 100% long gold notional, -0.5 = 50% short), decided at the CLOSE of bar t of
timeframe `tf` and held over bar t+1 (so it is causal by construction if pos[t] only uses
data up to bar t). Costs: SPREAD (USD) per unit of notional traded, i.e. cost = |dpos| *
SPREAD / price. Daily P&L is in % of equity (simple, non-compounded per bar).

Periods are the same as harness.py (last 6 years):
IS 2020-07..2023-06 (select / fit), VAL 2023-07..2024-12, HOLDOUT 2025-01..2026-07.
Always compare against the buy-and-hold baseline over the same period (gold rallied 2024-26).
"""
import numpy as np
import pandas as pd
import harness as H

SPREAD = H.SPREAD
PERIODS = H.PERIODS
bars, load_m1 = H.bars, H.load_m1


def pnl(pos, b, spread=SPREAD):
    """pos: Series aligned to bars b (decision at bar close). Returns per-bar returns Series."""
    pos = pos.reindex(b.index).fillna(0.0)
    ret = b.close.pct_change().shift(-1)            # return earned over the NEXT bar
    cost = pos.diff().abs().fillna(pos.abs()) * spread / b.close
    r = (pos * ret - cost).fillna(0.0)
    r.index = b.index + (b.index[1] - b.index[0] if len(b) > 1 else pd.Timedelta(0))  # book at bar end
    return r


def daily(r):
    return r.groupby(r.index.date).sum()


def stats(r, periods=("IS", "VAL", "HOLDOUT"), annual_days=260):
    d = daily(r)
    out = {}
    for p in periods:
        a, b = PERIODS[p]
        x = d[(d.index >= pd.Timestamp(a).date()) & (d.index < pd.Timestamp(b).date())]
        x = x[x != 0] if (x != 0).any() else x
        if len(x) < 5:
            out[p] = dict(days=len(x)); continue
        eq = x.cumsum()
        sr = x.mean() / x.std() * np.sqrt(annual_days) if x.std() > 0 else 0.0
        out[p] = dict(days=len(x), ann_ret=round(x.mean() * annual_days * 100, 2),
                      ann_vol=round(x.std() * np.sqrt(annual_days) * 100, 2), sharpe=round(sr, 2),
                      maxDD=round((eq - eq.cummax()).min() * 100, 2), green_days=round((x > 0).mean() * 100, 1),
                      green_months=round((x.groupby(pd.to_datetime(x.index).to_period("M")).sum() > 0).mean() * 100, 1),
                      total=round(x.sum() * 100, 1))
    return out


def vol_target(pos, b, target_ann=0.10, lookback=20 * 24, bars_per_year=260 * 24, cap=3.0):
    """Scale a raw +-1 signal to a target annual volatility using trailing realised vol (causal)."""
    rv = b.close.pct_change().rolling(lookback).std() * np.sqrt(bars_per_year)
    lev = (target_ann / rv).clip(upper=cap)
    return (pos * lev).fillna(0.0)


def buy_hold(b, target_ann=None):
    pos = pd.Series(1.0, index=b.index)
    if target_ann:
        pos = vol_target(pos, b, target_ann)
    return pos


def fmt(name, st):
    s = f"{name:<38}"
    for p, v in st.items():
        s += f" | {p}: SR={v.get('sharpe','-')} ret={v.get('ann_ret','-')}% dd={v.get('maxDD','-')}% gd={v.get('green_days','-')}%"
    return s


if __name__ == "__main__":
    b = bars("1h")
    print(fmt("buy&hold 1x", stats(pnl(buy_hold(b), b))))
    print(fmt("buy&hold vol-target 10%", stats(pnl(buy_hold(b, 0.10), b))))
    m = np.sign(b.close - b.close.shift(24 * 20))
    print(fmt("TSMOM 20d sign, vt10%", stats(pnl(vol_target(m, b), b))))
