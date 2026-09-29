"""Stage 4: daily management for the 3 carried-forward portfolios, parameters chosen on IS ONLY
(objective = IS daily Sharpe; ties are irrelevant), then checked on VAL. HOLDOUT masked.
Knobs: lock_up (stop new entries after day P&L >= +X R), lock_dn (after <= -Y R), eqmode (0 = realized P&L,
1 = equity incl. floating at M1 close and flatten everything when hit), max entries/day (portfolio),
vol scaling w = clip((median ATR_D1 over 250 d / ATR_D1)^a, 0.5, 1.5) applied to risk at entry."""
import sys, json, itertools, time
import numpy as np, pandas as pd
sys.path.insert(0, "/home/user/trading-bridge/research/families/F_portfolio")
import common as C
import harness as H
import harness2 as H2
from engine import Engine
D = "/home/user/trading-bridge/research/families/F_portfolio/"
pd.set_option("display.width", 250)
E = Engine(); m1 = E.m1
i0 = E.rng("IS")[0]; i1 = E.rng("VAL")[1]            # IS start .. HOLDOUT start (excluded)
iv = E.rng("VAL")[0] - i0
day = pd.factorize(m1.index[i0:i1].date)[0].astype(np.int64)
dates = m1.index[i0:i1]
ports = json.load(open(D + "s3_ports.json")); chosen = json.load(open(D + "s3_chosen.json"))
pool = pd.read_csv(D + "s2_pool.csv").set_index("name")
a = H.atr(C.bars("D1"), 14); med = a.rolling(250).median()
ratio = np.nan_to_num(H.htf_to_m1(med / a, "1D")[i0:i1], nan=1.0)
W = {va: np.clip(ratio ** va, 0.5, 1.5) for va in (0.0, 0.5, 1.0)}


def dstats(oe, ox, rr, lo, hi):
    m = (ox >= lo) & (ox < hi)
    d = pd.Series(rr[m], index=dates[ox[m]].date).groupby(level=0).sum()
    eq = d.cumsum()
    sh = d.mean() / d.std() * np.sqrt(252) if len(d) > 2 and d.std() > 0 else -9
    mo = d.groupby(pd.to_datetime(d.index).to_period("M")).sum()
    return dict(totR=round(d.sum(), 1), R_day=round(d.mean(), 3), gd=round((d > 0).mean() * 100, 1),
                dd=round((eq - eq.cummax()).min(), 1), gm=round((mo > 0).mean() * 100, 1), sh=round(sh, 2), n=int(m.sum()))


out = {}
for pn in chosen:
    t0 = time.time()
    specs = [json.loads(pool.loc[n, "spec"]) for n in ports[pn]]
    tabs = [C.outcome_table(E, s, i0, i1) for s in specs]
    X = np.stack([t[0] for t in tabs]); RR = np.stack([t[1] for t in tabs]); S = np.stack([t[2] for t in tabs]); SL = np.stack([t[3] for t in tabs])
    # sanity: unmanaged sim == sum of real harness2 runs
    oe, ox, rr, st = C.psim(X, RR, S, SL, E.o, E.c, day, i0, 0.0, 0.0, 0, 0, C.H2.SPREAD, W[0.0])
    ref = sum(C.run_spec(s).pipe(lambda t: t[(t.t >= H2.PERIODS["IS"][0]) & (t.t < H2.PERIODS["HOLDOUT"][0])].R.sum()) for s in specs)
    print(pn, "psim unmanaged totR", round(rr.sum(), 2), "harness2 sum", round(ref, 2), f"{time.time()-t0:.0f}s", flush=True)
    rows = []
    for up, dn, mt, em, va in itertools.product((0, 1, 2, 3, 5), (0, 1, 2, 3), (0, 2, 4, 8), (0, 1), (0.0, 0.5, 1.0)):
        if em == 1 and up == 0 and dn == 0:
            continue
        oe, ox, rr, st = C.psim(X, RR, S, SL, E.o, E.c, day, i0, float(up), float(dn), mt, em, C.H2.SPREAD, W[va])
        s_is = dstats(oe, ox, rr, 0, iv); s_v = dstats(oe, ox, rr, iv, i1 - i0)
        rows.append(dict(lock_up=up, lock_dn=dn, maxtr=mt, eqmode=em, volexp=va,
                         **{f"IS_{k}": v for k, v in s_is.items()}, **{f"VAL_{k}": v for k, v in s_v.items()}))
    r = pd.DataFrame(rows)
    base = r[(r.lock_up == 0) & (r.lock_dn == 0) & (r.maxtr == 0) & (r.volexp == 0)].iloc[0]
    best = r.sort_values("IS_sh", ascending=False)
    print(f"\n{pn} unmanaged:\n{base.to_frame().T.to_string(index=False)}")
    print(f"{pn} top-8 by IS Sharpe:\n{best.head(8).to_string(index=False)}")
    for knob in ("lock_up", "lock_dn", "maxtr", "eqmode", "volexp"):
        print(f"  mean IS/VAL Sharpe by {knob}:", r.groupby(knob)[["IS_sh", "VAL_sh"]].mean().round(2).to_dict("index"))
    r.to_csv(D + f"s4_{pn}.csv", index=False)
    out[pn] = best.iloc[0][["lock_up", "lock_dn", "maxtr", "eqmode", "volexp"]].to_dict()
json.dump(out, open(D + "s4_mgmt.json", "w"), indent=1)
print(out)
