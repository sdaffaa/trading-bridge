"""State-dependent inventions (numba loop around harness.trade_once, identical fills).

  1. barrier-momentum : next side = direction price actually travelled in the last trade
                        (the side whose barrier was hit)  -> trend at the barrier scale
  2. barrier-reversion: opposite of the above
  3. win-stay/lose-shift and its inverse (depends on own P&L state)
  4. streak rules      : after k same-direction barrier hits, fade (or follow)
Distances: m x ATR_H1 or p % of price.  IS/VAL only (dirs stop at VAL end)."""
import numpy as np, pandas as pd
from numba import njit
from core import *


from state_ideas_fns import run_state


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
