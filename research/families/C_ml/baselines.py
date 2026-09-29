"""Reference win rates under the new periods: always long / short / random / momentum of last M1 bar."""
import numpy as np, pandas as pd, common as C, harness as H
m1 = H.load_m1(); n = len(m1)
rng = np.random.default_rng(0)
SPECS = [("atr", .5, "15min"), ("atr", 1, "15min"), ("atr", 2, "15min"), ("atr", 3, "15min"),
         ("atr", .5, "1h"), ("atr", 1, "1h"), ("atr", 2, "1h"), ("atr", 3, "1h"), ("usd", 2), ("usd", 5), ("usd", 10)]
pre = np.r_[np.nan, np.sign(m1.close.values[:-1] - m1.open.values[:-1])]; pre[pre == 0] = 1
for sp in SPECS:
    dist = C.dist_m1(sp)
    for nm, d in (("long", np.ones(n)), ("short", -np.ones(n)), ("random", rng.choice([-1., 1.], n)), ("lastM1bar", pre), ("revM1bar", -pre)):
        d = np.where(m1.index >= C.START, d, np.nan)
        print(H.fmt(f"{nm}|{C.spec_name(sp)}", H.stats(H.run_consecutive(d, dist))), flush=True)
