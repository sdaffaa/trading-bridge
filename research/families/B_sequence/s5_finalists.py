"""Final top 10 (by IS win rate, IS n>=300, deduplicated) re-run through the OFFICIAL harness
run_consecutive() + stats() + passes(), including HOLDOUT (touched only here)."""
from common import *
from s2_candle_patterns import pattern_codes, TFS
import pickle, re

SP = "/tmp/claude-0/-home-user-trading-bridge/b109c4cd-e10b-5fab-96f6-d6f544632108/scratchpad/"
LAB = pickle.load(open(SP + "labels_B.pkl", "rb")); K = pickle.load(open(SP + "calkeys_B.pkl", "rb"))
SC = stop_configs(); inv = {v: k for k, v in TFS.items()}
d = pd.concat([pd.read_csv(f) for f in ["res_s1_state.csv", "res_s2_patterns.csv", "res_s3_calendar.csv", "res_s4_combos.csv"]])
e = d[d.is_n >= 300].sort_values("is_wr", ascending=False).drop_duplicates(["stop", "is_n", "is_wr", "val_n", "val_wr"]).head(10)

def key(part):
    m = re.match(r"^(M1|M5|M15|H1)_(sign|tri[\d.]+)_N(\d+)$", part)
    if m:
        return pattern_codes(inv[m.group(1)], int(m.group(3)), None if m.group(2) == "sign" else float(m.group(2)[3:]))
    return K[part]

rows = []
for _, r in e.iterrows():
    base, minc = re.match(r"(.*)_min(\d+)$", r["name"]).groups()
    parts = base.split("X") if r.family == "combo" else [base]
    # combo names join with 'X' but calendar keys may contain 'X' too: rebuild greedily
    if r.family == "combo":
        m = re.match(r"^((?:M1|M5|M15|H1)_(?:sign|tri[\d.]+)_N\d+)X(.*)$", base); parts = [m.group(1), m.group(2)]
    ka, na = key(parts[0]); keys = ka
    if len(parts) == 2:
        kb, nb = key(parts[1]); keys = np.where((ka >= 0) & (kb >= 0), ka * nb + kb, -1); na = na * nb
    idx, lo, so = LAB[r.stop]
    tab, *_ = learn_table(keys[idx], lo, so, na, minc=int(minc))
    dirs = apply_table(keys, tab, default_dir(lo, so))
    st = stats(run_consecutive(dirs, SC[r.stop]))
    print(fmt(f"{r['name']}@{r.stop}", st), "PASS" if passes(st) else "fail", flush=True)
    rows.append(dict(name=r["name"], stop=r.stop, **{f"{p}_{k}": st[p].get(k) for p in st for k in ("n", "wr")}, passes=passes(st)))
pd.DataFrame(rows).to_csv("res_s5_finalists.csv", index=False)
