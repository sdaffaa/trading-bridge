"""Candle-sequence lookup tables (2-state colour and 3-state up/flat/down vs ATR) of the last N
completed bars on M1/M5/M15/H1 = Markov chains of order N. Direction per pattern learned on IS
(from all-bar long/short outcome labels), frozen, applied to VAL/HOLDOUT."""
from common import *
import pickle

TFS = {"1min": "M1", "5min": "M5", "15min": "M15", "1h": "H1"}


def pattern_codes(tf, nb, flat=None):
    b = bars(tf) if tf != "1min" else M1
    body = (b.close - b.open).values
    if flat is None:
        s = (body > 0).astype(np.int64); base = 2
    else:
        a = atr(b).values
        s = np.where(body > flat * a, 2, np.where(body < -flat * a, 0, 1)).astype(np.int64)
        s[np.isnan(a)] = -10 ** 9
        base = 3
    code = np.zeros(len(b), np.int64)
    for q in range(nb):
        code = code * base + np.roll(s, q)
    code[:nb + 20] = -1; code[code < 0] = -1
    ser = pd.Series(code.astype(float), index=b.index)
    if tf == "1min":   # value for bar i known after bar i closes -> shift by one
        v = np.r_[-1.0, ser.values[:-1]]
    else:
        v = htf_to_m1(ser, tf)
    v = np.nan_to_num(v, nan=-1).astype(np.int64)
    return v, base ** nb


if __name__ == "__main__":
    SC = stop_configs()
    LAB = {sn: labels(np.nan_to_num(d, nan=0.0), step=5) for sn, d in SC.items()}
    pickle.dump(LAB, open("/tmp/claude-0/-home-user-trading-bridge/b109c4cd-e10b-5fab-96f6-d6f544632108/scratchpad/labels_B.pkl", "wb"))
    print("labels done", flush=True)
    log = Log("res_s2_patterns.csv")
    specs = []
    for tf in TFS:
        for nb in range(1, 9):
            specs.append((tf, nb, None))
        for fl in (0.1, 0.3):
            for nb in range(1, 7):
                specs.append((tf, nb, fl))
    for tf, nb, fl in specs:
        keys, nk = pattern_codes(tf, nb, fl)
        pname = f"{TFS[tf]}_{'sign' if fl is None else 'tri'+str(fl)}_N{nb}"
        for sn, dist in SC.items():
            idx, lo, so = LAB[sn]
            dflt = default_dir(lo, so)
            for minc in (200, 1000):
                tab, lwr, swr, cnt = learn_table(keys[idx], lo, so, nk, minc=minc)
                if (tab != 0).sum() == 0:
                    continue
                for inv in (1, -1):   # -1 = fade the learned table (sanity / mean-rev check)
                    d = apply_table(keys, (tab * inv).astype(np.int8), dflt)
                    log.add("pattern", f"{pname}_min{minc}{'_inv' if inv<0 else ''}", sn, quick(d, dist))
        print(pname, flush=True)
    log.save()
    df = pd.DataFrame(log.rows)
    print(len(df), "variants")
    print(df[df.is_n >= 300].sort_values("is_wr", ascending=False).head(25).to_string())
