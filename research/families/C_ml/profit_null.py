"""Null test for candidate profit configs: random entries at the same decision bars, same number of
signals and same long/short mix per half-year block, same exits. Reports the model's percentile."""
import numpy as np, pandas as pd, common as C, harness as H, harness2 as H2, profit as P

CANDS = [("1h", "tp3", "cls", "long", 0.2), ("1h", "tp1.5", "cls", "long", 0.3), ("1h", "tp1.5", "reg", "both", 0.0),
         ("1h", "tp3", "cls", "both", 0.1)]
m1 = H.load_m1()
a1h = H.htf_to_m1(H.atr(H.bars("1h"), 14), "1h")
rng = np.random.default_rng(7)
for TF, gn, tgt, mode, th in CANDS:
    g = [x for x in P.GEOMS if x[0] == gn][0]
    b, L, Pr = P.oof(TF, g, tgt)
    sl, tp, tr, mb = P.geom_arrays(g, a1h)
    dirs = P.trade_dirs(b, TF, L, Pr, th, mode)
    st = H2.stats(H2.run(dirs, sl, tp, tr, mb))
    trd = H2.run(dirs, sl, tp, tr, mb)
    blk = trd.groupby(pd.cut(trd.t, pd.to_datetime([a for a, _ in C.BLOCKS] + ["2026-08-01"]), right=False)).R.sum().round(1)
    print(H2.fmt(f"{tgt}|{TF}|{gn}|{mode}|th={th}", st))
    print("   R per half-year block:", list(blk.values))
    # null
    sig = dirs[L.i.values]; ts = L.index
    null = {p: [] for p in H.PERIODS}
    for r in range(200):
        nd = np.zeros(len(m1))
        for a, z in C.BLOCKS:
            msk = np.flatnonzero((ts >= a) & (ts < z))
            s = sig[msk]; k = int((s != 0).sum()); nl = int((s > 0).sum())
            if k == 0: continue
            pick = rng.choice(msk, k, replace=False)
            side = np.r_[np.ones(nl), -np.ones(k - nl)]; rng.shuffle(side)
            nd[L.i.values[pick]] = side
        s2 = H2.stats(H2.run(nd, sl, tp, tr, mb))
        for p in null: null[p].append(s2[p]["totR"])
    print("   percentile of model totR vs random-entry null (same count & side mix):",
          {p: round((np.array(null[p]) < st[p]["totR"]).mean() * 100, 1) for p in null},
          " null median:", {p: round(float(np.median(null[p])), 1) for p in null}, flush=True)
