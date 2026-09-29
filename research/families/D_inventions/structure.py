"""Structure-geometry, volume-profile, regime-switching and %-of-price ideas.
Every candidate = (dirs, dist) per M1 bar, evaluated with the harness itself on IS/VAL
(run_sel zeroes everything after VAL end -> HOLDOUT never touched here)."""
import time, pickle, numpy as np, pandas as pd
from core import *
from features_d import build, NAMES

X = build()
col = {n: np.asarray(X[:, j], np.float64) for j, n in enumerate(NAMES)}
a1 = atr_m1("1h"); ad = atr_m1("1D")
c1 = np.r_[np.nan, C[:-1]]
px = htf(M1.close.resample("1D").last().dropna(), "1D")
res = []


def rec(name, dirs, dist):
    t = time.time()
    dirs = np.nan_to_num(np.asarray(dirs, np.float64)); dist = np.asarray(dist, np.float64)
    tr, st = run_sel(dirs, dist)
    s = st["IS"]; v = st["VAL"]
    res.append(dict(name=name, nIS=s.get("n", 0), wrIS=s.get("wr", 0), nVAL=v.get("n", 0), wrVAL=v.get("wr", 0)))
    print(f"{name:<60} IS n={s.get('n',0):>6} wr={s.get('wr',0):6.2f} | VAL n={v.get('n',0):>6} wr={v.get('wr',0):6.2f}  ({time.time()-t:.1f}s)", flush=True)


# ---- level distances (price units, >0), all from bars < i ----
lev_up = {"pdh": col["to_pdh"] * a1, "dayhi": None, "frac": col["frac_hi"] * a1,
          "asia": None, "vah": -col["to_vah"] * a1}
lev_dn = {"pdl": col["to_pdl"] * a1, "daylo": None, "frac": col["frac_lo"] * a1,
          "asia": None, "val": col["to_val"] * a1}
# day hi/lo from dpos, drange: dhi - c1 = (1-dpos)*drange*a1
dr = col["drange"] * a1
up_day = (1 - col["dpos"]) * dr; dn_day = col["dpos"] * dr
asz = col["asia_size"] * ad
up_as = (1 - col["asia_pos"]) * asz; dn_as = col["asia_pos"] * asz
r10u = (1 - col["r10"]) * 10; r10d = col["r10"] * 10
r50u = (1 - col["r50"]) * 50; r50d = col["r50"] * 50
poc = col["to_poc"] * a1       # c1 - poc
LEVELS = {
    "prevday": (col["to_pdh"] * a1, col["to_pdl"] * a1),
    "dayHL": (up_day, dn_day),
    "fractalH1": (col["frac_hi"] * a1, col["frac_lo"] * a1),
    "asia": (up_as, dn_as),
    "round10": (r10u, r10d),
    "round50": (r50u, r50d),
    "valueArea": (-col["to_vah"] * a1, col["to_val"] * a1),
}
# nearest level of any kind that is strictly on each side
U = np.full(N, np.inf); D = np.full(N, np.inf)
for k, (u, d) in LEVELS.items():
    u = np.where(u > 0, u, np.inf); d = np.where(d > 0, d, np.inf)
    U = np.minimum(U, np.nan_to_num(u, nan=np.inf)); D = np.minimum(D, np.nan_to_num(d, nan=np.inf))
LEVELS["anyLevel"] = (U, D)

for lname, (u, d) in LEVELS.items():
    u = np.where(u > 0, u, np.nan); d = np.where(d > 0, d, np.nan)
    upnear = u < d
    near = np.where(upnear, u, d); far = np.where(upnear, d, u)
    for floor in (0.5, 1.0, 2.0):          # distance floor in ATR_H1 (spread protection)
        fl = floor * a1
        dn_ = np.fmax(np.nan_to_num(near, nan=0), fl)
        df_ = np.fmax(np.nan_to_num(far, nan=0), fl)
        tow = np.where(upnear, 1.0, -1.0)
        rec(f"{lname} toward-nearer dist=near(floor{floor}ATR)", tow, dn_)
        rec(f"{lname} away-from-nearer dist=near(floor{floor}ATR)", -tow, dn_)
        rec(f"{lname} toward-farther dist=far(floor{floor}ATR)", -tow, df_)
        rec(f"{lname} away-from-farther dist=far(floor{floor}ATR)", tow, df_)

# ---- volume profile: toward / away from previous-day POC ----
for floor in (0.5, 1.0, 2.0):
    dpoc = np.fmax(np.abs(poc), floor * a1)
    tow = np.where(poc > 0, -1.0, 1.0)
    rec(f"POC toward dist=|c-POC|(floor{floor}ATR)", tow, dpoc)
    rec(f"POC away dist=|c-POC|(floor{floor}ATR)", -tow, dpoc)
    for m in (1, 2):
        rec(f"POC toward dist={m}xATR (floor{floor})", tow, np.full(N, 1.0) * m * a1)
        rec(f"POC away dist={m}xATR", -tow, m * a1)
    inside = (col["to_vah"] < 0) & (col["to_val"] > 0)
    # inside VA: fade toward POC; outside: breakout continuation
    dd = np.where(inside, tow, -tow)
    rec(f"VA inside->toward POC, outside->continue dist={floor}xATR", dd, floor * a1)

# ---- Asian range size as distance, breakout side ----
for m in (0.5, 1.0, 1.5):
    dist = np.fmax(m * asz, 0.5 * a1)
    side = np.where(col["asia_pos"] > 0.5, 1.0, -1.0)
    rec(f"Asia size x{m}, side = above-mid long", side, dist)
    rec(f"Asia size x{m}, side = above-mid short", -side, dist)

# ---- stop as % of price with simple direction rules ----
for p in (0.1, 0.2, 0.3, 0.5, 0.8):
    dist = p / 100 * px
    for dn, dd in (("mom60", np.sign(col["ret60"])), ("mom1440", np.sign(col["ret1440"])),
                   ("ema50h4", np.sign(col["ema50_h4"])), ("ema20d1", np.sign(col["ema20_d1"])),
                   ("rev60", -np.sign(col["ret60"])), ("rev_twap", -np.sign(col["to_twap"])),
                   ("long", np.ones(N))):
        dd = np.where(dd == 0, 1.0, dd)
        rec(f"{p}% of price, dir={dn}", dd, dist)

# ---- regime switching: trend-follow in trending regime, fade in mean-reverting ----
REG = {"er_h1": (col["er_h1"], [0.2, 0.3, 0.4]), "vr_h1": (col["vr_h1"], [0.9, 1.0, 1.1]),
       "hurst_h1": (col["hurst_h1"], [0.5, 0.55]), "ac1_m5": (col["ac1_m5"], [-0.05, 0.0, 0.05]),
       "vr_m5": (col["vr_m5"], [0.9, 1.0]), "atr_ratio": (col["atr_ratio"], [0.9, 1.1, 1.3])}
for rn, (x, ths) in REG.items():
    for th in ths:
        trend = x > th
        for sig in ("ret60", "ret240", "ema50_h1", "to_twap"):
            s = np.sign(col[sig]); s = np.where(s == 0, 1.0, s)
            dd = np.where(trend, s, -s)
            for m in (1.0, 2.0):
                rec(f"regime {rn}>{th}: trend({sig}) else fade, {m}xATR", dd, m * a1)
res_df = pd.DataFrame(res)
res_df.to_csv("structure_results.csv", index=False)
print("\nTop 15 by IS wr (n>=300):")
print(res_df[res_df.nIS >= 300].sort_values("wrIS", ascending=False).head(15).to_string())
print("\nTop 15 by VAL wr (n>=300) [info only]:")
print(res_df[res_df.nVAL >= 300].sort_values("wrVAL", ascending=False).head(15).to_string())
print("candidates:", len(res_df))
