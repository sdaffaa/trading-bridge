"""Stage 4: final 10 (chosen in s3 from IS rank + VAL>0) run ONCE on all periods incl. HOLDOUT,
with long-only / short-only splits and two always-long baselines using the SAME exits:
  L_same  = long at the same entry bars (direction ignored),
  L_every = long on every M1 bar (re-enter at the next bar after each exit)."""
import pandas as pd, numpy as np
from common import *
E = registry()
fin = pd.read_csv("final10_spec.csv")
rows = []
for k, r in enumerate(fin.itertuples()):
    tpr = None if pd.isna(r.tpr) else r.tpr; trk = None if pd.isna(r.trk) else r.trk
    d, sl, tp, tr, mb = build(r.name, r.slmode, r.slk, tpr, trk, r.mb, r.filt, E)
    P = ("IS", "VAL", "HOLDOUT")
    tag = f"{r.name}|sl{r.slk}{r.slmode}|tp{tpr}|tr{trk}|mb{r.mb}|{r.filt}"
    for var, dd, side in (("strategy", d, 0), ("long_only", d, 1), ("short_only", d, -1),
                          ("L_same", np.abs(d), 0), ("L_every", np.ones(N), 0)):
        st, trd = evaluate(dd, sl, tp, tr, mb, P, side)
        rows.append(dict(rank=k + 1, spec=tag, var=var, credible=H.credible(st), **flat(st)))
        print(k + 1, var, H.fmt(tag[:40], st), flush=True)
out = pd.DataFrame(rows); out.to_csv("final10_holdout.csv", index=False)
