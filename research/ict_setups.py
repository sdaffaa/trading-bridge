"""Round 4: discretionary-style ICT/SMC setups coded as rules, 1:1, on M1.
Each setup waits for its own trigger (selective), SL placed at structure,
TP = same distance. Split IS (first 2/3) vs OOS (last 1/3)."""
import sys
import numpy as np, pandas as pd
sys.path.insert(0, ".")
from backtest import load, SPREAD

from ict_setups_sim import sim

if len(sys.argv) > 1 and sys.argv[1] == 'multi':
    from load_multi import load_multi
    m1 = load_multi(); SPREAD = 0.30
else:
    m1 = load(sys.argv[1])
t = m1.index
m5 = m1.resample("5min").agg({"open": "first", "high": "max", "low": "min", "close": "last"}).dropna()
tr = (m5.high - m5.low).rolling(14).mean()
pos = pd.Series(np.arange(len(m1)), index=t)

def at(ts):  # M1 index of first bar after an M5 bar closes
    k = pos.index.searchsorted(ts + pd.Timedelta("5min"))
    return k if k < len(m1) else None

signals = {}
def add(name, ts, d, dist):
    i = at(ts)
    if i is not None and dist > 0: signals.setdefault(name, []).append((i, d, dist))

days = m5.groupby(m5.index.normalize())
prev = None
for day, g in days:
    asia = g.between_time("00:00", "06:55")
    if len(asia) < 30: prev = g; continue
    ah, al = asia.high.max(), asia.low.min()
    # 1) Asian range sweep & reclaim during London (07-10 UTC)
    lon = g.between_time("07:00", "10:00")
    done = False
    for ts, r in lon.iterrows():
        if done: break
        if r.high > ah and r.close < ah:
            add("asia_sweep_rev", ts, -1, max(r.high - r.close + 0.3, 1.0)); done = True
        elif r.low < al and r.close > al:
            add("asia_sweep_rev", ts, 1, max(r.close - r.low + 0.3, 1.0)); done = True
    # 2) Asian range breakout continuation (London)
    for ts, r in lon.iterrows():
        if r.close > ah: add("asia_breakout", ts, 1, (ah - al) / 2); break
        if r.close < al: add("asia_breakout", ts, -1, (ah - al) / 2); break
    # 3) previous-day high/low sweep & reclaim (any time)
    if prev is not None:
        ph, pl = prev.high.max(), prev.low.min()
        for ts, r in g.iterrows():
            if r.high > ph and r.close < ph: add("pdh_pdl_sweep", ts, -1, max(r.high - r.close + 0.3, 1.0)); break
            if r.low < pl and r.close > pl: add("pdh_pdl_sweep", ts, 1, max(r.close - r.low + 0.3, 1.0)); break
    # 4) NY opening-range (13:30-14:00 UTC) breakout
    orng = g.between_time("13:30", "13:55")
    if len(orng) >= 5:
        oh, ol = orng.high.max(), orng.low.min()
        for ts, r in g.between_time("14:00", "17:00").iterrows():
            if r.close > oh: add("ny_orb", ts, 1, oh - ol); break
            if r.close < ol: add("ny_orb", ts, -1, oh - ol); break
    prev = g

# 5) FVG after displacement, trade retest in the displacement direction (M5)
H, L, C, O = m5.high.values, m5.low.values, m5.close.values, m5.open.values
atr5 = tr.values
fvgs = []
for k in range(2, len(m5)):
    if not np.isfinite(atr5[k]): continue
    body = abs(C[k-1] - O[k-1])
    if L[k] > H[k-2] and body > 1.5 * atr5[k]: fvgs.append((k, 1, H[k-2], L[k]))
    if H[k] < L[k-2] and body > 1.5 * atr5[k]: fvgs.append((k, -1, H[k], L[k-2]))
for k, d, lo, hi in fvgs:
    for q in range(k + 1, min(k + 24, len(m5))):   # retest within 2h
        if d > 0 and L[q] <= hi:
            add("fvg_retest", m5.index[q], 1, max(hi - lo + (hi - L[q]), 1.0)); break
        if d < 0 and H[q] >= lo:
            add("fvg_retest", m5.index[q], -1, max(hi - lo + (H[q] - lo), 1.0)); break
    # same, but in the London/NY killzones only (silver-bullet style)
o, h, l = m1.open.values, m1.high.values, m1.low.values
split = m1.index.searchsorted(pd.Timestamp("2020-01-01")) if len(m1) > 1e6 else int(len(m1) * 0.66)
rows = []
for name, sig in signals.items():
    sig = sorted(sig)
    for mult in (0.5, 1.0, 1.5):
        idx = np.array([s[0] for s in sig]); dirs = np.array([s[1] for s in sig], np.float64)
        dists = np.array([s[2] for s in sig]) * mult
        out, _ = sim(o, h, l, idx, dirs, dists, SPREAD)
        for part, msk in (("IS", idx < split), ("OOS", idx >= split)):
            r = out[msk]; r = r[r != 0]
            if len(r): rows.append(dict(setup=name, sl_mult=mult, sample=part, trades=len(r),
                                         winrate=round((r > 0).mean() * 100, 1), net_R=int(r.sum())))
pd.set_option("display.width", 200)
df = pd.DataFrame(rows).pivot_table(index=["setup", "sl_mult"], columns="sample", values=["trades", "winrate", "net_R"])
print(df.to_string())
