"""Part 2 - profit objective (harness2). ML predicts the R outcome of a long and of a short opened
at the first M1 bar after a decision-bar close, for a given exit geometry (SL = a x ATR(H1),
TP = r x SL or none, trailing stop, time exit). Trade only when max predicted E[R] > theta,
side = argmax. theta and config are selected on IS out-of-fold results only.
Folds as in common.py (IS: purged leave-one-half-year-out inside IS; VAL/HOLDOUT: expanding WF).
Official numbers from harness2.run with dirs non-zero only at decision bars."""
import sys, os, time, warnings, itertools, numpy as np, pandas as pd, lightgbm as lgb
from numba import njit
warnings.filterwarnings("ignore")
import common as C, harness as H, harness2 as H2

@njit(cache=True)
def one(o, h, l, c, i, d, sl, tp, tr, mb, spread):
    """Exact copy of harness2._run's single-trade logic. Returns (R, exit_bar)."""
    n = len(o)
    if d > 0:
        e = o[i] + spread; stop = e - sl; best = e
    else:
        e = o[i]; stop = e + sl; best = e
    j = i; exitp = np.nan
    while j < n:
        if d > 0:
            if l[j] <= stop:
                exitp = stop; break
            if tp > 0 and h[j] >= e + tp:
                exitp = e + tp; break
            if tr > 0:
                if h[j] > best: best = h[j]
                ns = best - tr
                if ns > stop: stop = ns
        else:
            if h[j] + spread >= stop:
                exitp = stop; break
            if tp > 0 and l[j] + spread <= e - tp:
                exitp = e - tp; break
            if tr > 0:
                if l[j] + spread < best: best = l[j] + spread
                ns = best + tr
                if ns < stop: stop = ns
        if mb > 0 and j - i + 1 >= mb:
            exitp = c[j] if d > 0 else c[j] + spread
            break
        j += 1
    if j >= n:
        return np.nan, n
    return ((exitp - e) if d > 0 else (e - exitp)) / sl, j

@njit(cache=True)
def lab(o, h, l, c, idx, sl, tp, tr, mb, spread):
    n = len(idx); RL = np.full(n, np.nan); RS = np.full(n, np.nan); E = np.zeros(n, np.int64)
    for k in range(n):
        if not (sl[k] > 0): continue
        a, j1 = one(o, h, l, c, idx[k], 1, sl[k], tp[k], tr[k], mb, spread)
        b, j2 = one(o, h, l, c, idx[k], -1, sl[k], tp[k], tr[k], mb, spread)
        RL[k] = a; RS[k] = b; E[k] = max(j1, j2)
    return RL, RS, E

# geometry: (name, sl_mult of ATR1h, tp_mult of SL (0=none), trail_mult of ATR1h (0=none), maxbars)
GEOMS = [("tp1", 1, 1, 0, 1440), ("tp1.5", 1, 1.5, 0, 1440), ("tp2", 1, 2, 0, 1440), ("tp3", 1, 3, 0, 1440),
         ("trail1", 1, 0, 1, 1440), ("trail1_sl2", 2, 0, 1, 1440), ("time60", 1, 0, 0, 60), ("time240", 1.5, 0, 0, 240),
         ("tp2_sl0.5", 0.5, 2, 0, 480)]

def geom_arrays(g, a1h):
    _, s, r, t, mb = g
    sl = s * a1h
    return sl, (r * sl if r > 0 else np.full_like(sl, -1.0)), (t * a1h if t > 0 else np.full_like(sl, -1.0)), mb

def dataset(TF, g):
    fn = f"{C.CACHE}/plab_{TF}_{g[0]}.parquet"
    b, X = C.build_dataset(TF)
    if os.path.exists(fn):
        return b, X, pd.read_parquet(fn)
    m1 = H.load_m1(); o, h, l, c = (m1[k].values for k in ("open", "high", "low", "close"))
    sel = b.index >= C.START - pd.Timedelta("1D")
    bi = b.index[sel]
    idx = m1.index.searchsorted(bi + pd.Timedelta(TF)); ok = idx < len(m1)
    a1h = C.dist_series(b, TF, ("atr", 1, "1h"))[sel]
    sl, tp, tr, mb = geom_arrays(g, a1h)
    RL, RS, E = lab(o, h, l, c, np.where(ok, idx, 0).astype(np.int64), np.where(ok, sl, np.nan), tp, tr, mb, H.SPREAD)
    L = pd.DataFrame({"i": idx, "RL": RL, "RS": RS, "e": E}, index=bi)[ok]
    L = L.dropna(); L.to_parquet(fn)
    return b, X, L

def oof(TF, g, target="reg"):
    fn = f"{C.CACHE}/poof_{TF}_{g[0]}_{target}.parquet"
    b, X, L = dataset(TF, g)
    if os.path.exists(fn):
        return b, L, pd.read_parquet(fn)
    D = X.loc[L.index]
    P = pd.DataFrame(np.nan, index=L.index, columns=["pL", "pS"])
    for bi, tr, te in C.folds(L.index, L.i.values, L.e.values):
        for side, col in (("RL", "pL"), ("RS", "pS")):
            y = L[side].values[tr]
            if target == "reg":
                m = lgb.LGBMRegressor(n_estimators=250, learning_rate=0.03, num_leaves=15, min_child_samples=400,
                                      subsample=0.7, subsample_freq=1, colsample_bytree=0.6, reg_lambda=10,
                                      n_jobs=2, verbose=-1, objective="huber", alpha=1.0)
                m.fit(D[tr], np.clip(y, -1.5, 4)); P.loc[te, col] = m.predict(D[te])
            else:   # classify win (R>0) -> E[R] = p*avgwin - (1-p)*avgloss from training fold
                m = lgb.LGBMClassifier(n_estimators=250, learning_rate=0.03, num_leaves=15, min_child_samples=400,
                                       subsample=0.7, subsample_freq=1, colsample_bytree=0.6, reg_lambda=10, n_jobs=2, verbose=-1)
                m.fit(D[tr], (y > 0).astype(int)); p = m.predict_proba(D[te])[:, 1]
                aw, al = y[y > 0].mean(), -y[y <= 0].mean()
                P.loc[te, col] = p * aw - (1 - p) * al
    P.to_parquet(fn)
    return b, L, P

def trade_dirs(b, TF, L, P, theta, mode="both"):
    m1 = H.load_m1()
    pL, pS = P.pL.values, P.pS.values
    if mode == "long": pS = np.full_like(pS, -9)
    if mode == "short": pL = np.full_like(pL, -9)
    d = np.where((pL >= pS) & (pL > theta), 1.0, np.where((pS > pL) & (pS > theta), -1.0, 0.0))
    d[np.isnan(pL)] = 0
    dirs = np.zeros(len(m1)); dirs[L.i.values] = d
    return dirs

def evaluate(TF, g, dirs):
    b, X = C.build_dataset(TF)
    a1h = H.htf_to_m1(H.atr(H.bars("1h"), 14), "1h")
    sl, tp, tr, mb = geom_arrays(g, a1h)
    return H2.stats(H2.run(dirs, sl, tp, tr, mb))

def is_oof_R(L, P, theta, mode="both"):
    """Fast approximate IS objective on label rows (ignores the one-position overlap) - used only
    to pre-screen theta; final numbers always from harness2."""
    pL, pS = P.pL.values, P.pS.values
    if mode == "long": pS = np.full_like(pS, -9)
    if mode == "short": pL = np.full_like(pL, -9)
    d = np.where((pL >= pS) & (pL > theta), 1, np.where((pS > pL) & (pS > theta), -1, 0))
    return d

if __name__ == "__main__":
    TFs = sys.argv[1].split(",") if len(sys.argv) > 1 else ["1h", "15min"]
    target = sys.argv[2] if len(sys.argv) > 2 else "reg"
    out = open("/home/user/trading-bridge/research/families/C_ml/profit_raw.tsv", "a")
    for TF in TFs:
        for g in GEOMS:
            t0 = time.time()
            b, L, P = oof(TF, g, target)
            m1 = H.load_m1()
            # baselines with identical exits and decision times
            for nm, dv in (("ALWAYS_LONG", 1.0), ("ALWAYS_SHORT", -1.0)):
                dirs = np.zeros(len(m1)); dirs[L.i.values] = dv
                st = evaluate(TF, g, dirs)
                print(H2.fmt(f"{nm}|{TF}|{g[0]}", st), flush=True)
                out.write(f"{nm}|{TF}|{g[0]}\t{st}\n")
            for mode in ("both", "long"):
                for theta in (0.0, 0.05, 0.1, 0.2, 0.3):
                    dirs = trade_dirs(b, TF, L, P, theta, mode)
                    if (dirs != 0).sum() < 50: continue
                    st = evaluate(TF, g, dirs)
                    nm = f"lgb_{target}|{TF}|{g[0]}|{mode}|th={theta}"
                    print(H2.fmt(nm, st), "CRED" if H2.credible(st) else "", flush=True)
                    out.write(f"{nm}\t{st}\n"); out.flush()
            print("  time", round(time.time() - t0), flush=True)
