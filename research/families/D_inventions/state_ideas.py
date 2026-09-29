"""State-dependent inventions (numba loop around harness.trade_once, identical fills).

  1. barrier-momentum : next side = direction price actually travelled in the last trade
                        (the side whose barrier was hit)  -> trend at the barrier scale
  2. barrier-reversion: opposite of the above
  3. win-stay/lose-shift and its inverse (depends on own P&L state)
  4. streak rules      : after k same-direction barrier hits, fade (or follow)
  5. adaptive distance : distance = median |barrier-hit| duration-scaled... (dist = k * last
                         trade's realised range per minute * sqrt(target minutes))
Distances: m x ATR_H1 or p % of price.  IS/VAL only (dirs stop at VAL end)."""
import numpy as np, pandas as pd
from numba import njit
from core import *


@njit(cache=True)
def run_state(o, h, l, dist, spread, i0, i1, mode, k):
    n = len(o)
    ent = np.empty(n // 2, np.int64); ex = np.empty(n // 2, np.int64)
    res = np.empty(n // 2, np.int8); side = np.empty(n // 2, np.int8)
    m = 0; i = i0; last_move = 1.0; last_side = 1.0; last_res = 1; streak = 0
    while i < i1:
        d = dist[i]
        if not (d > 0):
            i += 1; continue
        if mode == 0:   s = last_move                      # barrier momentum
        elif mode == 1: s = -last_move                     # barrier reversion
        elif mode == 2: s = last_side if last_res > 0 else -last_side   # win-stay lose-shift
        elif mode == 3: s = -last_side if last_res > 0 else last_side   # win-shift lose-stay
        elif mode == 4: s = -last_move if streak >= k else last_move    # follow, fade after k
        else:           s = last_move if streak >= k else -last_move    # fade, follow after k
        r, j = H.trade_once(o, h, l, i, s, d, spread)
        if r == 0:
            break
        ent[m] = i; ex[m] = j; res[m] = r; side[m] = 1 if s > 0 else -1; m += 1
        mv = s if r > 0 else -s
        streak = streak + 1 if mv == last_move else 1
        last_move = mv; last_side = s; last_res = r
        i = j + 1
    return ent[:m], ex[:m], res[:m], side[:m]


a1 = atr_m1("1h")
px = htf(M1.close.resample("1D").last().dropna(), "1D")
DIST = {f"{m}xATRh1": m * a1 for m in (0.5, 1, 2, 4)}
DIST.update({f"{p}%px": p / 100 * px for p in (0.1, 0.25, 0.5)})
MODES = {0: "barrier-momentum", 1: "barrier-reversion", 2: "win-stay/lose-shift", 3: "win-shift/lose-stay",
         4: "follow, fade after k", 5: "fade, follow after k"}
rows = []
for dn, dist in DIST.items():
    for mode, mn in MODES.items():
        for k in ((2, 3, 4) if mode >= 4 else (0,)):
            e, x, r, s = run_state(O, HI, LO, np.asarray(dist, np.float64), H.SPREAD, WARM0, VAL1, mode, k)
            st = H.stats(to_df(e, x, r, s), ("IS", "VAL"))
            name = f"{mn}{'' if mode < 4 else f' k={k}'} | {dn}"
            rows.append(dict(name=name, nIS=st["IS"]["n"], wrIS=st["IS"]["wr"], nVAL=st["VAL"]["n"], wrVAL=st["VAL"]["wr"]))
            print(f"{name:<45} IS n={st['IS']['n']:>6} wr={st['IS']['wr']:6.2f} | VAL n={st['VAL']['n']:>6} wr={st['VAL']['wr']:6.2f}", flush=True)
df = pd.DataFrame(rows); df.to_csv("state_results.csv", index=False)
print(df.sort_values("wrIS", ascending=False).head(10).to_string())
