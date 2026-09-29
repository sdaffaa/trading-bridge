"""Stage 1: exhaustive single-indicator grid, ranked on IS only.
signals (6 TFs x ~132) x {normal, inverted} x 52 stop-distance rules."""
import sys, time
import numpy as np, pandas as pd
sys.path.insert(0, "/home/user/trading-bridge/research/families/A_indicators")
from core import Engine, H, walk, tf_map
from signals import TFS, signals_for_tf

OUT = "/home/user/trading-bridge/research/families/A_indicators/grid_is.parquet"
WARM = "2018-01-01"


def build_signals():
    sig, maps, atrs = {}, {}, {}
    for tf, f in TFS.items():
        b = H.bars(f); b = b[b.index >= WARM]
        maps[tf] = tf_map(f, b.index)
        atrs[tf] = H.atr(b, 14)
        for k, v in signals_for_tf(b).items():
            sig[(tf, k)] = v
    return sig, maps, atrs


def dist_rules(atrs, m1):
    R = {}
    for tf, f in TFS.items():
        a = H.htf_to_m1(atrs[tf], f)
        for k in (0.5, 1, 1.5, 2, 3, 5):
            R[f"{k}xATR_{tf}"] = k * a
    n = len(m1)
    for usd in (1, 2, 3, 5, 8, 12, 20):
        R[f"${usd}"] = np.full(n, float(usd))
    pc = np.r_[np.nan, m1.close.values[:-1]]
    for p in (0.05, 0.075, 0.1, 0.15, 0.2, 0.3, 0.5, 0.75, 1.0):
        R[f"{p}%px"] = pc * p / 100
    return R


if __name__ == "__main__":
    t0 = time.time()
    E = Engine()
    sig, maps, atrs = build_signals()
    R = dist_rules(atrs, E.m1)
    i0, i1 = E.rng("IS")
    print(f"{len(sig)} signals, {len(R)} dist rules, setup {time.time()-t0:.0f}s", flush=True)
    rows = []
    for dn, dist in R.items():
        t = time.time()
        lx, lw, sx, sw = E.tables(dist, i0, i1)
        for (tf, name), s in sig.items():
            mp = maps[tf]
            for inv in (False, True):
                n, w = walk(s, mp, inv, lx, lw, sx, sw, i0, i1)
                rows.append((tf, name, inv, dn, n, w))
        print(f"{dn:<14} {time.time()-t:.1f}s", flush=True)
    df = pd.DataFrame(rows, columns=["tf", "sig", "inv", "dist", "n", "w"])
    df["wr"] = 100 * df.w / df.n.clip(lower=1)
    df.to_parquet(OUT)
    print("done", len(df), f"{time.time()-t0:.0f}s")
