"""Asymmetry study: unconditional first-passage win probability of a long vs a short
1:1 trade started at each M1 bar, by UTC hour, for many distance schemes (IS & VAL).
Then consecutive strategies: side (and distance scheme) chosen per hour on IS."""
import numpy as np, pandas as pd
from core import *

a1 = atr_m1("1h"); ad = atr_m1("1D")
px = htf(M1.close.resample("1D").last().dropna(), "1D")
schemes = {f"${d}": np.full(N, float(d)) for d in (1, 2, 3, 5, 8, 13)}
schemes.update({f"{m}xATRh1": m * a1 for m in (0.5, 1, 2, 4)})
schemes.update({f"{p}%px": p / 100 * px for p in (0.1, 0.25, 0.5)})
schemes.update({f"{m}xATRd1": m * ad for m in (0.25, 0.5)})
hour = T.hour.values
rows = []; TB = {}
for nm, dist in schemes.items():
    tb = tables(dist); TB[nm] = tb
    wl, el, ws, es = tb
    for per, (i0, i1) in (("IS", (IS0, IS1)), ("VAL", (VAL0, VAL1))):
        sl = slice(i0, i1)
        v = wl[sl] != 0
        L = (wl[sl][v] > 0); S = (ws[sl][v] > 0); hh = hour[sl][v]
        d = pd.DataFrame({"h": hh, "L": L, "S": S}).groupby("h").mean()
        rows.append(dict(scheme=nm, per=per, pL=L.mean(), pS=S.mean(),
                         best_hour_L=d.L.max(), best_hour_S=d.S.max(),
                         hL=int(d.L.idxmax()), hS=int(d.S.idxmax())))
    print(nm, "done", flush=True)
R = pd.DataFrame(rows)
pd.set_option("display.width", 200)
print(R.round(3).to_string())

# per-hour side from IS, per scheme -> consecutive strategy
out = []
for nm, tb in TB.items():
    wl, el, ws, es = tb
    sl = slice(IS0, IS1); v = wl[sl] != 0
    d = pd.DataFrame({"h": hour[sl][v], "L": wl[sl][v] > 0, "S": ws[sl][v] > 0}).groupby("h").mean()
    side_h = np.where(d.L >= d.S, 1.0, -1.0)
    sideh = np.zeros(24); sideh[d.index.values] = side_h
    dirs = sideh[hour]
    na, wa, nb, wb = quick(dirs, tb)
    out.append((nm, na, round(wa * 100, 2), nb, round(wb * 100, 2)))
    print("hour-side", nm, na, round(wa * 100, 2), nb, round(wb * 100, 2), flush=True)

# per-hour best (scheme, side) chosen on IS -> combined tables
best = {}
for h in range(24):
    bestv = -1
    for nm, tb in TB.items():
        wl, el, ws, es = tb
        m = (hour[IS0:IS1] == h) & (wl[IS0:IS1] != 0)
        for s, w in ((1, wl), (-1, ws)):
            p = (w[IS0:IS1][m] > 0).mean()
            if p > bestv:
                bestv = p; best[h] = (nm, s, p)
print({h: (b[0], b[1], round(b[2], 3)) for h, b in best.items()})
wl = np.zeros(N, np.int8); el = np.full(N, -1, np.int32); ws = wl.copy(); es = el.copy(); dirs = np.zeros(N)
for h, (nm, s, p) in best.items():
    m = hour == h
    t = TB[nm]; wl[m] = t[0][m]; el[m] = t[1][m]; ws[m] = t[2][m]; es[m] = t[3][m]; dirs[m] = s
na, wa, nb, wb = quick(dirs, (wl, el, ws, es))
print("per-hour best scheme+side: IS", na, round(wa * 100, 2), "VAL", nb, round(wb * 100, 2))
