"""'Feel' for the grid: in a consecutive 1:1 always-in system every trade is one +-dist 'brick'.
Decide the next side from the pattern of the last K bricks (the direction in which each previous
trade actually resolved). Policies: momentum (repeat last brick), reversal, and a learned lookup
table pattern->side fitted only on earlier data (IS: purged leave-one-block-out, VAL/HOLDOUT:
expanding). The path is generated with harness.trade_once, then dirs are replayed through
harness.run_consecutive to get the official numbers."""
import sys, numpy as np, pandas as pd
from numba import njit
import common as C, harness as H, ml_run as R

@njit(cache=True)
def walk(o, h, l, dist, start, policy_tab, K, mode, spread):
    # mode 0 momentum, 1 reversal, 2 table lookup by last-K brick pattern (bit code)
    n = len(o); dirs = np.full(n, np.nan); hist = np.zeros(64, np.int64); hn = 0
    ent = np.empty(n, np.int64); brick = np.empty(n, np.int8); k = 0
    i = start; code = 0
    while i < n:
        if not (dist[i] > 0):
            i += 1; continue
        if hn < K:
            d = 1
        elif mode == 0:
            d = 1 if (code & 1) else -1
        elif mode == 1:
            d = -1 if (code & 1) else 1
        else:
            d = policy_tab[i, code]
        out, j = H.trade_once(o, h, l, i, d, dist[i], spread)
        if out == 0: break
        br = d * out                       # direction the market resolved (+1 up, -1 down)
        for t in range(i, min(j + 1, n)): dirs[t] = d
        ent[k] = i; brick[k] = br; k += 1
        code = ((code << 1) | (1 if br > 0 else 0)) & ((1 << K) - 1); hn += 1
        i = j + 1
    return dirs, ent[:k], brick[:k]

def main(spec, K):
    m1 = H.load_m1(); o, h, l = m1.open.values, m1.high.values, m1.low.values
    dist = C.dist_m1(spec); st = m1.index.searchsorted(C.START)
    for mode, nm in ((0, "momentum"), (1, "reversal")):
        dirs, _, _ = walk(o, h, l, dist, st, np.zeros((1, 1), np.int64), K, mode, H.SPREAD)
        s = H.stats(H.run_consecutive(dirs, dist))
        print(H.fmt(f"renko_{nm}|{C.spec_name(spec)}", s), H.passes(s), flush=True)
    # learned table: brick sequence from the momentum walk is just the market's d-grid path
    _, ent, br = walk(o, h, l, dist, st, np.zeros((1, 1), np.int64), K, 0, H.SPREAD)
    t = m1.index[ent]; up = (br > 0).astype(int)
    codes = np.zeros(len(br), np.int64)
    for j in range(1, K + 1):
        codes += np.r_[np.zeros(j, np.int64), up[:-j]] << (j - 1)
    tab = np.ones((len(m1), 1 << K), np.int64)
    for bi, (a, z) in enumerate(C.BLOCKS):
        a, z = pd.Timestamp(a), pd.Timestamp(z)
        if a < C.IS_END:
            trm = (t >= C.START) & (t < C.IS_END) & ~((t >= a - pd.Timedelta("2D")) & (t < z + pd.Timedelta("5D")))
        else:
            trm = (t >= C.START) & (t < a - pd.Timedelta("2D"))
        trm &= np.arange(len(t)) >= K
        row = np.array([1 if up[trm & (codes == c)].mean() >= .5 else -1 if (trm & (codes == c)).any() else 1 for c in range(1 << K)])
        ia, iz = m1.index.searchsorted(a), m1.index.searchsorted(z)
        tab[ia:iz] = row
    dirs, _, _ = walk(o, h, l, dist, st, tab, K, 2, H.SPREAD)
    s = H.stats(H.run_consecutive(dirs, dist))
    name = f"renko_table_K{K}|{C.spec_name(spec)}"
    print(H.fmt(name, s), H.passes(s), flush=True)
    with open("/home/user/trading-bridge/research/families/C_ml/results_raw.tsv", "a") as f:
        f.write("\t".join([name] + [f"{p}:n={s[p].get('n')},wr={s[p].get('wr')}" for p in s] + [f"passes={H.passes(s)}"]) + "\n")

if __name__ == "__main__":
    for sp in sys.argv[1].split(";"):
        for K in (2, 4, 6):
            main(R.parse(sp), K)
