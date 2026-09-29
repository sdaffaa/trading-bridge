"""Round 2: label every M1 bar with the 1:1 outcome (long & short) and mine
conditions whose win rate holds in-sample AND out-of-sample."""
import sys, itertools
import numpy as np, pandas as pd
from numba import njit
sys.path.insert(0, ".")
from backtest import load, indicators, SPREAD

@njit
def label(o, h, l, dist, spread):
    n = len(o); L = np.zeros(n, np.int8); S = np.zeros(n, np.int8)
    for i in range(n):
        d = dist[i]
        if not (d > 0):
            continue
        e = o[i] + spread / 2; tp = e + d; sl = e - d
        for j in range(i, n):
            if l[j] - spread / 2 <= sl: L[i] = -1; break
            if h[j] - spread / 2 >= tp: L[i] = 1; break
        e = o[i] - spread / 2; tp = e - d; sl = e + d
        for j in range(i, n):
            if h[j] + spread / 2 >= sl: S[i] = -1; break
            if l[j] + spread / 2 <= tp: S[i] = 1; break
    return L, S

m1 = load(sys.argv[1]); f = indicators(m1)
m1c = m1.close.shift(1)
f["hour"] = m1.index.hour
f["dow"] = m1.index.dayofweek
f["rsi_b"] = pd.cut(f.rsi, [0, 20, 30, 40, 50, 60, 70, 80, 100], labels=False)
f["bbz_b"] = pd.cut(f.bb_z, [-9, -2.5, -2, -1, 0, 1, 2, 2.5, 9], labels=False)
f["trend"] = np.sign(f.ema_fast - f.ema_slow)
f["h1"] = f.h1_trend
f["mom_b"] = np.sign(f.mom)
f["atr_q"] = pd.qcut(f.atr, 4, labels=False)
# day range position: where is price in today's range so far (liquidity context)
day = m1.index.normalize()
dh = m1.high.groupby(day).cummax().shift(1); dl = m1.low.groupby(day).cummin().shift(1)
f["dpos"] = pd.cut((m1c - dl) / (dh - dl), [-1, .1, .3, .5, .7, .9, 2], labels=False)
split = int(len(m1) * 0.66)
feats = ["hour", "rsi_b", "bbz_b", "trend", "h1", "mom_b", "atr_q", "dpos", "dow"]
best = []
for k in (0.5, 1.0, 2.0, 3.0):
    L, S = label(m1.open.values, m1.high.values, m1.low.values, (k * f.atr).values, SPREAD)
    df = f[feats].copy(); df["L"] = L; df["S"] = S
    df["part"] = np.where(np.arange(len(df)) < split, "IS", "OOS")
    df = df[(df.L != 0) & df[feats].notna().all(axis=1)]
    base = ((df.L > 0).mean(), (df.S > 0).mean())
    print(f"k={k}: unconditional long wr={base[0]:.3f} short wr={base[1]:.3f}")
    for a, b in itertools.combinations(feats, 2):
        for side in ("L", "S"):
            g = df.groupby([a, b, "part"])[side].agg(lambda s: (s > 0).mean()).unstack("part")
            c = df.groupby([a, b, "part"])[side].size().unstack("part")
            # distinct days matters: bars are heavily overlapping, so require many days
            ok = g[(c.IS > 3000) & (c.OOS > 1500)]
            for idx, r in ok.iterrows():
                best.append((k, side, a, idx[0], b, idx[1], round(r.IS, 3), round(r.OOS, 3), int(c.loc[idx].IS), int(c.loc[idx].OOS)))
res = pd.DataFrame(best, columns=["k", "side", "f1", "v1", "f2", "v2", "wr_IS", "wr_OOS", "n_IS", "n_OOS"])
res["min_wr"] = res[["wr_IS", "wr_OOS"]].min(axis=1)
pd.set_option("display.width", 200)
print(res.sort_values("min_wr", ascending=False).head(30).to_string(index=False))
res.to_csv("/tmp/claude-0/-home-user-trading-bridge/b109c4cd-e10b-5fab-96f6-d6f544632108/scratchpad/mine.csv", index=False)
