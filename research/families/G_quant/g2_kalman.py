"""Family 2: Kalman local-level + slope (local linear trend) on the vol-normalised log-price path.
Grid over q_slope/r (speed) and q_level/r; plus q ratios fitted by MLE on IS (statsmodels)."""
import numpy as np, pandas as pd
import common as G, signals as S
import statsmodels.api as sm

rows = []
for ql in (0.0, 0.1, 1.0):
    for qs in (1e-7, 1e-6, 1e-5, 1e-4, 1e-3, 1e-2):
        for kind in ("slope", "tstat"):
            f = S.kalman(ql, qs, 1.0, kind)
            for m in ("LS", "LF"):
                G.evaluate(f"kf_{kind}_ql{ql}_qs{qs:g}_{m}", "2_kalman", S.to_pos(S.mode(f, m)), dict(ql=ql, qs=qs, kind=kind, m=m))
# MLE on IS, daily-sampled normalised path (UnobservedComponents local linear trend)
y = S.norm_path()
yd = y[S.IS_MASK].iloc[::23].values
mod = sm.tsa.UnobservedComponents(yd, level="local linear trend")
res = mod.fit(disp=False)
print(res.summary().tables[1])
s2i, s2l, s2s = res.params  # irregular, level, trend variances (per day)
# convert per-day variances to per-hour (random walk scaling /23; slope var /23^3)
r_h, ql_h, qs_h = s2i, s2l / 23, s2s / 23 ** 3
print("MLE per-hour ratios ql/r=%.3g qs/r=%.3g" % (ql_h / r_h, qs_h / r_h))
for kind in ("slope", "tstat"):
    f = S.kalman(ql_h / r_h, qs_h / r_h, 1.0, kind)
    for m in ("LS", "LF"):
        G.evaluate(f"kf_mle_{kind}_{m}", "2_kalman", S.to_pos(S.mode(f, m)), dict(ql=ql_h / r_h, qs=qs_h / r_h, kind=kind, m=m, mle=True))
df = G.save("g2"); print(len(df), "configs"); G.show(df, n=20)
