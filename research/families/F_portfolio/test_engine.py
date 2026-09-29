"""Check engine tables+walk == harness2.run on IS for random dirs and every exit spec."""
import sys, time
import numpy as np, pandas as pd
sys.path.insert(0, "/home/user/trading-bridge/research/families/F_portfolio")
from engine import *
import harness as H
E = Engine(); i0, i1 = E.rng("IS"); n = len(E.m1)
sl = 2 * H.htf_to_m1(H.atr(H.bars("1h")), "1h")
rng = np.random.default_rng(3)
d = rng.choice([-1., 0., 1.], n, p=[.45, .1, .45]); d[:i0] = 0; d[i1:] = 0
for ex in EXITS:
    t = time.time(); lx, lR, sx, sR = E.tables(sl, *EXITS[ex], i0, i1); tt = time.time() - t
    nn, s1, gw, gl, s2 = walk_rel(d[i0:i1].astype(np.int8), lx, lR, sx, sR, i0, i1)
    tr = run_h2(d, sl, ex); tr = tr[tr.t < H.PERIODS["IS"][1]]
    print(ex, f"tables {tt:.1f}s", "engine", nn, round(s1, 2), "| harness2", len(tr), round(tr.R.sum(), 2))
