"""Family 3: mean reversion. (a) OU-style z-score of log price vs EMA(L), band entry/exit, optional
stationarity gates (VR<1, Hurst<0.5, ADF p<0.10, OU half-life < L) on rolling windows;
(b) intraday reversion to the running NY-day mean (TWAP proxy, no volume in data), flat at day end."""
import numpy as np, pandas as pd, time
import common as G, signals as S

t0 = time.time()
tests = {}
for W in (120, 480):
    tests[W] = S.rolling_tests(W, 23, 48)
    print("tests W", W, round(time.time() - t0), "s", flush=True)
for L in (12, 24, 48, 120, 240):
    z = S.zscore_dev(L)
    for zin in (1.5, 2.0, 2.5):
        for zout in (0.0, 0.5):
            gates = {"none": None}
            for W, (vr, hu, adf, hl) in tests.items():
                gates[f"vr{W}"] = vr < 1.0
                gates[f"hurst{W}"] = hu < 0.5
                gates[f"adf{W}"] = adf < 0.10
                gates[f"hl{W}"] = hl < L
            for gn, g in gates.items():
                if gn != "none" and not (zout == 0.0):
                    continue      # gates only with zout=0 to limit the grid
                raw = S.band(z, zin, zout, g)
                for m in ("LS", "LF"):
                    G.evaluate(f"ou_L{L}_z{zin}_{zout}_{gn}_{m}", "3_mr", S.to_pos(S.mode(raw, m)), dict(L=L, zin=zin, zout=zout, gate=gn, m=m))
# (b) intraday reversion to running NY-day mean
C = G.C
day = G.TDAY
cum = C.groupby(day.values).cumsum(); cnt = C.groupby(day.values).cumcount() + 1
tw = cum / cnt
sig_p = C * S.sigma_1h()
zd = ((C - tw) / (sig_p * np.sqrt(cnt.clip(lower=1)))).where(cnt >= 3)
endday = G.NY_HOUR.isin([16])   # flat from NY 16:00 bar (close at 17:00)
for zin in (0.5, 1.0, 1.5, 2.0):
    for zout in (0.0, 0.5):
        raw = S.band(zd, zin, zout).where(~endday, 0.0)
        for m in ("LS", "LF"):
            G.evaluate(f"twap_z{zin}_{zout}_{m}", "3_mr", S.to_pos(S.mode(raw, m)), dict(zin=zin, zout=zout, m=m))
df = G.save("g3"); print(len(df), "configs", round(time.time() - t0), "s"); G.show(df, n=20)
