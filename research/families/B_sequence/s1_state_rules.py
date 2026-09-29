"""Trade-state rules: win/loss keep/flip, follow/fade last-N exit majority, streak rules,
and a lookup table over the last N exit directions learned on IS (chain-based)."""
from common import *
from common import _wr_seg, _labels

@njit(cache=True)
def run_policy(o, h, l, dist, spread, pol, p1, p2, table, start):
    """pol 0: wl rule (p1: after win keep=1/flip=-1, p2 after loss keep/flip)
       pol 1: majority of last p1 exit dirs, p2=+1 follow / -1 fade
       pol 2: streak: s=len of current run of same exit dirs; if s<p1 follow*p2 else fade*p2
       pol 3: table over last p1 exit dirs (code in base 2), table[code] in {+1,-1}
    Returns ent, ex, res, side, and for pol 3 learning: state codes and alt outcomes."""
    n = len(o)
    ent = np.empty(n // 2, np.int64); ex = np.empty(n // 2, np.int64)
    res = np.empty(n // 2, np.int8); side = np.empty(n // 2, np.int8)
    codes = np.empty(n // 2, np.int64)
    hist = np.zeros(64, np.int8)   # ring of last exit dirs, hist[0] most recent
    nh = 0
    k = 0; i = start; d = 1; lastres = 1
    while i < n:
        ds = dist[i]
        if not (ds > 0):
            i += 1; continue
        code = -1
        if pol == 0:
            if nh > 0:
                d = d * (p1 if lastres > 0 else p2)
        elif pol == 1:
            if nh >= p1:
                s = 0
                for q in range(p1):
                    s += hist[q]
                d = (1 if s > 0 else -1) * p2
        elif pol == 2:
            if nh > 0:
                s = 1
                while s < nh and s < 60 and hist[s] == hist[0]:
                    s += 1
                d = hist[0] * p2 if s < p1 else -hist[0] * p2
        elif pol == 3:
            if nh >= p1:
                code = 0
                for q in range(p1):
                    code = code * 2 + (1 if hist[q] > 0 else 0)
                d = table[code]
        out, j = trade_once(o, h, l, i, d, ds, spread)
        if out == 0:
            break
        ent[k] = i; ex[k] = j; res[k] = out; side[k] = d; codes[k] = code
        k += 1
        lastres = out
        for q in range(63, 0, -1):
            hist[q] = hist[q - 1]
        hist[0] = d * out
        if nh < 64:
            nh += 1
        i = j + 1
    return ent[:k], ex[:k], res[:k], side[:k], codes[:k]


def seg(ent, res):
    out = {}
    for p, (a, b) in (("IS", (IS_START, IS_END)), ("VAL", (IS_END, VAL_END)), ("HOLDOUT", (VAL_END, HO_END))):
        n, w = _wr_seg(ent, res, a, b)
        out[p] = (n, 100.0 * w / n if n else 0.0)
    return out


if __name__ == "__main__":
    log = Log("res_s1_state.csv")
    SC = stop_configs()
    dummy = np.ones(2, np.int8)
    for sn, dist in SC.items():
        dist = np.nan_to_num(dist, nan=0.0)
        variants = []
        for a in (1, -1):
            for b in (1, -1):
                variants.append((f"wl_win{'keep' if a>0 else 'flip'}_loss{'keep' if b>0 else 'flip'}", 0, a, b))
        for nn in (1, 3, 5, 7, 9):
            for f in (1, -1):
                variants.append((f"maj{nn}_{'follow' if f>0 else 'fade'}", 1, nn, f))
        for S in (1, 2, 3, 4, 5, 6):
            for f in (1, -1):
                variants.append((f"streak<{S}_{'follow' if f>0 else 'fade'}", 2, S, f))
        for name, pol, p1, p2 in variants:
            ent, ex, res, side, _ = run_policy(O, H, L, dist, SPREAD, pol, p1, p2, dummy, 0)
            log.add("state", name, sn, seg(ent, res))
        # learned exit-dir pattern table: learn by running chain with random-ish base (follow last exit)
        # then for each IS entry, record long/short outcome at that bar
        for nn in (2, 3, 4, 5, 6, 8):
            # base chain: table all +1 over states -> collect codes; compute both-dir outcomes at entries
            rng = np.random.default_rng(nn)
            tab = rng.choice(np.array([-1, 1], np.int8), 2 ** nn).astype(np.int8)
            ent, ex, res, side, codes = run_policy(O, H, L, dist, SPREAD, 3, nn, 0, tab, 0)
            m = (ent >= IS_START) & (ent < IS_END) & (codes >= 0)
            lo, so = _labels(O, H, L, ent[m], dist, SPREAD, 20000)
            for minc in (100, 300):
                t, lwr, swr, cnt = learn_table(codes[m], lo, so, 2 ** nn, minc=minc)
                dflt = default_dir(lo, so)
                t = np.where(t == 0, dflt, t).astype(np.int8)
                ent2, ex2, res2, side2, _ = run_policy(O, H, L, dist, SPREAD, 3, nn, 0, t, 0)
                log.add("state", f"exitpat{nn}_table_min{minc}", sn, seg(ent2, res2))
        print(sn, "done", flush=True)
    log.save()
    df = pd.DataFrame(log.rows)
    df = df[df.is_n >= 300].sort_values("is_wr", ascending=False)
    print(len(log.rows), "variants"); print(df.head(20).to_string())
