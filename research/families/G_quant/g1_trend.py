"""Family 1: time-series momentum (sign / risk-adjusted), blends, EWMAC (Carver)."""
import common as G, signals as S

G.baselines()
HZ = {"4h": 4, "8h": 8, "12h": 12, "1d": 23, "2d": 46, "3d": 69, "5d": 115, "10d": 230, "20d": 460,
      "40d": 920, "60d": 1380, "120d": 2760}
cache = {}
for k, h in HZ.items():
    cache[("sign", k)] = S.tsmom_sign(h); cache[("ra", k)] = S.tsmom_ra(h)
for m in ("LS", "LF"):
    for k in HZ:
        for t in ("sign", "ra"):
            G.evaluate(f"tsmom_{t}_{k}_{m}", "1_tsmom", S.to_pos(S.mode(cache[(t, k)], m)), dict(t=t, h=k, m=m))
GR = {"intra": ["4h", "8h", "12h", "1d", "2d", "3d", "5d"], "short": ["1d", "2d", "5d"], "med": ["10d", "20d", "40d"],
      "long": ["60d", "120d"], "daily_all": ["1d", "2d", "5d", "10d", "20d", "40d", "60d", "120d"], "all": list(HZ)}
for g, ks in GR.items():
    for t in ("sign", "ra"):
        f = S.blend([cache[(t, k)] for k in ks])
        for m in ("LS", "LF"):
            G.evaluate(f"tsmomblend_{t}_{g}_{m}", "1_tsmom", S.to_pos(S.mode(f, m)), dict(t=t, g=g, m=m))
FAST = [4, 8, 16, 32, 64, 128, 256, 512, 1024]
ew = {f: S.ewmac(f) for f in FAST}
for f in FAST:
    for m in ("LS", "LF"):
        G.evaluate(f"ewmac_{f}_{4*f}_{m}", "1_ewmac", S.to_pos(S.mode(ew[f], m)), dict(fast=f, m=m))
EG = {"fast": [4, 8, 16, 32], "slow": [128, 256, 512, 1024], "mid": [32, 64, 128, 256], "carver": [64, 128, 256, 512, 1024], "all": FAST}
for g, fs in EG.items():
    fb = S.blend([ew[f] for f in fs])
    for m in ("LS", "LF"):
        G.evaluate(f"ewmacblend_{g}_{m}", "1_ewmac", S.to_pos(S.mode(fb, m)), dict(g=g, m=m))
df = G.save("g1")
print(len(df), "configs")
G.show(df, n=25)
print("--- worst IS 5"); G.show(df.sort_values("IS_sr").head(5), n=5)
