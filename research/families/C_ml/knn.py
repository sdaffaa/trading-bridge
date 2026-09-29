"""Analog / nearest-neighbour: 'this chart looks like past charts'. Shape vector = last N closes,
highs, lows relative to last close / ATR, PCA-compressed (PCA fit on the training fold only).
Direction = majority outcome (long-wins vs short-wins) of the k nearest historical situations.
strict=1: only data strictly before each test block (pure past analogs; IS then starts 2021)."""
import sys, time, numpy as np, pandas as pd, common as C, harness as H
from sklearn.decomposition import PCA
from sklearn.neighbors import KNeighborsClassifier
import picture as P

def run(TF, spec, N=32, k=200, ncomp=12, strict=False):
    b, Pic = P.picture(TF, 48)
    cols = [f"{f}{j}" for j in range(N) for f in ("c", "h", "l")]
    L = C.labels(b, TF, spec)
    D = Pic.loc[L.index, cols].fillna(0).values
    e = np.maximum(L.eL.values, L.eS.values)
    prob = pd.Series(np.nan, index=L.index)
    rng = np.random.default_rng(0)
    for bi, tr, te in C.folds(L.index, L.i.values, e, strict=strict):
        ii = np.flatnonzero(tr & (L.yL.values != L.yS.values))
        if len(ii) > 120000: ii = np.sort(rng.choice(ii, 120000, replace=False))
        pca = PCA(ncomp, random_state=0).fit(D[ii])
        m = KNeighborsClassifier(k, n_jobs=2).fit(pca.transform(D[ii]), (L.yL.values[ii] > 0).astype(int))
        prob[te] = m.predict_proba(pca.transform(D[te]))[:, 1]
    side = np.where(prob.values >= .5, 1., -1.); side[np.isnan(prob.values)] = np.nan
    full = pd.Series(np.nan, index=b.index); full.loc[L.index] = side
    st, _ = C.evaluate(full.values, b, TF, spec)
    name = f"knn{k}_N{N}{'_strict' if strict else ''}|{TF}|{C.spec_name(spec)}"
    print(H.fmt(name, st), "| passes", H.passes(st), flush=True)
    with open("/home/user/trading-bridge/research/families/C_ml/results_raw.tsv", "a") as f:
        f.write("\t".join([name] + [f"{p}:n={st[p].get('n')},wr={st[p].get('wr')}" for p in st] + [f"passes={H.passes(st)}"]) + "\n")
    prob.to_frame("p").to_parquet(f"{C.CACHE}/oof_{name.replace('|','_')}.parquet")

if __name__ == "__main__":
    import ml_run as R
    TF = sys.argv[1]; k = int(sys.argv[2]); N = int(sys.argv[3]); strict = len(sys.argv) > 5 and sys.argv[5] == "1"
    for s in sys.argv[4].split(";"):
        t = time.time(); run(TF, R.parse(s), N=N, k=k, strict=strict); print("  time", round(time.time() - t), flush=True)
