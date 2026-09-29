"""Objective = account profit at the end of each day. For the most stable signal
(family A #1) and several TP:SL ratios, measure daily P&L in R (1R = amount risked
per trade, spread included): % green days, mean day, worst day, max drawdown.
Optional daily lock variants (stop for the day after +X R or -Y R) are reported
separately because they pause trading."""
import sys
import numpy as np, pandas as pd
sys.path.insert(0, "/home/user/trading-bridge/research")
sys.path.insert(0, "/home/user/trading-bridge/research/solution")
sys.path.insert(0, "/home/user/trading-bridge/research/families/A_indicators")
import harness as H
import validate_lib as V
from geometry import run

m1 = H.load_m1(); o, h, l = m1.open.values, m1.high.values, m1.low.values
c = pd.read_csv("/home/user/trading-bridge/research/families/A_indicators/final10_holdout.csv").iloc[0]
d = V.dirs_of(c.combo); d = (-d if c.inv else d).astype(np.float64)
d[m1.index < pd.Timestamp(H.PERIODS["IS"][0])] = 0
sl = V.R[c.dist]

def summarize(pnl_by_day, label, rows):
    for p, (a, b) in H.PERIODS.items():
        x = pnl_by_day[(pnl_by_day.index >= pd.Timestamp(a).date()) & (pnl_by_day.index < pd.Timestamp(b).date())]
        eq = x.cumsum(); dd = (eq - eq.cummax()).min()
        rows.append(dict(setup=label, period=p, days=len(x), green_days=round((x > 0).mean() * 100, 1),
                         mean_day_R=round(x.mean(), 3), total_R=round(x.sum(), 1),
                         worst_day_R=round(x.min(), 1), best_day_R=round(x.max(), 1), maxDD_R=round(dd, 1),
                         green_weeks=round((x.groupby(pd.to_datetime(x.index).to_period("W")).sum() > 0).mean() * 100, 1)))

rows = []
for tpr in (1.0, 0.8, 0.6, 0.5):
    ent, res = run(o, h, l, d, sl, tpr, H.SPREAD)
    t = m1.index[ent]
    r = np.where(res > 0, tpr, -1.0)
    day = pd.Series(r, index=t).groupby(t.date).sum()
    summarize(day, f"TP={tpr}xSL", rows)
    # daily lock variants (these pause after the lock is hit)
    s = pd.Series(r, index=t)
    for up, dn in ((2, -3), (1, -2), (3, -3)):
        def lock(x):
            cs = x.cumsum().values
            hit = np.where((cs >= up) | (cs <= dn))[0]
            return cs[hit[0]] if len(hit) else cs[-1]
        summarize(s.groupby(t.date).apply(lock), f"TP={tpr}xSL lock+{up}/{dn}R", rows)
df = pd.DataFrame(rows)
df.to_csv("/home/user/trading-bridge/research/solution/daily.csv", index=False)
pd.set_option("display.width", 250)
print(df.to_string(index=False))
