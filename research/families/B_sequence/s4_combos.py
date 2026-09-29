"""Combine the best IS tables: pattern x calendar and pattern x pattern keys, with minimum-count
constraints (200/1000/3000 IS label samples per cell) to limit overfitting. Candidates chosen per
stop by IS win rate only (s2/s3 results)."""
from common import *
from s2_candle_patterns import pattern_codes, TFS
import pickle, re

SP = "/tmp/claude-0/-home-user-trading-bridge/b109c4cd-e10b-5fab-96f6-d6f544632108/scratchpad/"
LAB = pickle.load(open(SP + "labels_B.pkl", "rb"))
K = pickle.load(open(SP + "calkeys_B.pkl", "rb"))
SC = stop_configs()
p2 = pd.read_csv("res_s2_patterns.csv"); p3 = pd.read_csv("res_s3_calendar.csv")
p2 = p2[(p2.is_n >= 300) & ~p2.name.str.endswith("_inv")]; p3 = p3[p3.is_n >= 300]
p2["base"] = p2.name.str.replace(r"_min\d+$", "", regex=True); p3["base"] = p3.name.str.replace(r"_min\d+$", "", regex=True)
inv = {v: k for k, v in TFS.items()}
pc_cache = {}
def pkey(base):
    if base not in pc_cache:
        m = re.match(r"(\w+?)_(sign|tri[\d.]+)_N(\d+)", base)
        tf = inv[m.group(1)]; fl = None if m.group(2) == "sign" else float(m.group(2)[3:])
        pc_cache[base] = pattern_codes(tf, int(m.group(3)), fl)
    return pc_cache[base]

log = Log("res_s4_combos.csv")
for sn, dist in SC.items():
    idx, lo, so = LAB[sn]; dflt = default_dir(lo, so)
    tp = p2[p2.stop == sn].sort_values("is_wr", ascending=False).base.drop_duplicates().head(5).tolist()
    tc = p3[p3.stop == sn].sort_values("is_wr", ascending=False).base.drop_duplicates().head(5).tolist()
    pairs = [(a, b, "c") for a in tp for b in tc] + [(a, b, "p") for i, a in enumerate(tp) for b in tp[i + 1:]]
    for a, b, kind in pairs:
        ka, na = pkey(a)
        kb, nb = K[b] if kind == "c" else pkey(b)
        if na * nb > 200000:
            continue
        keys = np.where((ka >= 0) & (kb >= 0), ka * nb + kb, -1)
        for minc in (200, 1000, 3000):
            tab, *_ = learn_table(keys[idx], lo, so, na * nb, minc=minc)
            if (tab != 0).sum() == 0:
                continue
            log.add("combo", f"{a}X{b}_min{minc}", sn, quick(apply_table(keys, tab, dflt), dist))
    print(sn, len(log.rows), flush=True)
log.save()
df = pd.DataFrame(log.rows)
print(len(df), "variants")
print(df[df.is_n >= 300].sort_values("is_wr", ascending=False).head(20).to_string())
