"""Check that core.walk over precomputed tables == harness.run_consecutive exactly."""
import time, numpy as np
from core import *

a = atr_m1("1h")
rng = np.random.default_rng(1)
dirs = rng.choice([-1.0, 1.0], N)
dirs[:WARM0] = 0
t = time.time(); tb = tables(a, WARM0, N); print("tables s", round(time.time() - t, 1))
t = time.time(); ent, ex, res, side = walk(dirs, *tb, WARM0, N); print("walk s", round(time.time() - t, 3))
mine = to_df(ent, ex, res, side)
ref = H.run_consecutive(dirs, a)
ref = ref[ref.t >= T[WARM0]].reset_index(drop=True)
print(len(mine), len(ref), (mine.values == ref.values).all() if len(mine) == len(ref) else "LEN MISMATCH")
print(H.fmt("random dir, 1xATR_H1", H.stats(mine)))
for nm, d in (("always long", np.ones(N)), ("always short", -np.ones(N))):
    e, x, r, s = walk(d, *tb, WARM0, N)
    print(H.fmt(nm + " 1xATR_H1", H.stats(to_df(e, x, r, s))))
dur = (ex - ent)
print("median bars/trade", np.median(dur), "mean", dur.mean())
