"""Family 5b: seasonality strategies. NO effect passed BH-FDR on IS (g5_season_stats), so by protocol none
moves forward. The nominally strongest (Asia session long, p=0.008 unadjusted) and the intraday-momentum
mirror of the failed TWAP-reversion (family 3b) are evaluated as DIAGNOSTICS only (counted as trials)."""
import numpy as np, pandas as pd
import common as G, signals as S


def scale_is(pos, target=0.10):
    """constant rescale so IS realised daily vol == target (part-time strategies)."""
    import harness3 as H3
    d = G.daily_all(H3.pnl(pos, G.B)); a, b = G.PER["IS"]
    v = d[(d.index >= a) & (d.index < b)].std() * np.sqrt(260)
    return pos * (target / v) if v > 0 else pos


lev = G.ann_vol_lev()
h = G.NY_HOUR
asia = h.isin(list(range(18, 24)) + [0, 1]).astype(float)
G.evaluate("season_asia_long", "5_season", scale_is((asia * lev).fillna(0)), dict(hours="18-01 NY", side="long"))
G.evaluate("season_asia_long_ny18only", "5_season", scale_is(((h == 18).astype(float) * lev).fillna(0)), dict(hours="18", side="long"))
# intraday momentum: follow deviation from running NY-day mean (mirror of 3b), flat from NY16
C = G.C
day = G.TDAY
cum = C.groupby(day.values).cumsum(); cnt = C.groupby(day.values).cumcount() + 1
zd = ((C - cum / cnt) / (C * S.sigma_1h() * np.sqrt(cnt.clip(lower=1)))).where(cnt >= 3)
endday = G.NY_HOUR.isin([16])
for zin in (0.5, 1.0, 1.5):
    raw = -S.band(zd, zin, 0.0).where(~endday, 0.0)
    for m in ("LS", "LF"):
        G.evaluate(f"twapmom_z{zin}_{m}", "5_season", S.to_pos(S.mode(raw, m)), dict(zin=zin, m=m))
df = G.save("g5"); print(len(df), "configs"); G.show(df, n=20)
