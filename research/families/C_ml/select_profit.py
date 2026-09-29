"""Rank profit configs by IS (out-of-fold) total R only; report VAL/HOLDOUT untouched."""
import numpy as np, sys
from numpy import inf, nan
rows = {}
for line in open("/home/user/trading-bridge/research/families/C_ml/profit_raw.tsv"):
    name, st = line.rstrip("\n").split("\t"); rows[name] = eval(st, {"np": np, "inf": inf, "nan": nan})
minn = int(sys.argv[1]) if len(sys.argv) > 1 else 200
def f(v): return f"n={v['n']} R={v['totR']} R/t={v['R_trade']} PF={v['PF']} gd={v['green_days']}% dd={v['maxDD']}"
cand = [(k, v) for k, v in rows.items() if not k.startswith("ALWAYS") and v["IS"]["n"] >= minn]
cand.sort(key=lambda kv: -kv[1]["IS"]["totR"])
print(f"{len(rows)} rows, {len(cand)} model configs with IS n>={minn}")
for k, v in cand[:10]:
    cred = all(v[p]["totR"] > 0 for p in ("IS", "VAL", "HOLDOUT"))
    g = "|".join(k.split("|")[1:3])
    bl = rows.get(f"ALWAYS_LONG|{g}")
    print(f"{k}\n   IS {f(v['IS'])}\n   VAL {f(v['VAL'])}\n   HO {f(v['HOLDOUT'])}\n   all>0={cred}  | always-long same exits: IS {bl['IS']['totR']} VAL {bl['VAL']['totR']} HO {bl['HOLDOUT']['totR']}")
print("credible (all 3 >0) count:", sum(all(v[p]['totR'] > 0 for p in ('IS','VAL','HOLDOUT')) for k, v in cand), "of", len(cand))
