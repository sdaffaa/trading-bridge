"""Feature-based ML (LightGBM / ExtraTrees / RF / logistic / MLP) with purged folds.
usage: python ml_run.py TF model spec1;spec2...   spec: atr:k:tf | usd:v
Writes OOF side predictions to cache + a line per config to results_raw.tsv"""
import sys, time, warnings
import numpy as np, pandas as pd
warnings.filterwarnings("ignore")
import common as C, harness as H

def make_model(name, seed=0):
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler
    if name == "lgb":
        import lightgbm as lgb
        return lgb.LGBMClassifier(n_estimators=300, learning_rate=0.03, num_leaves=31, min_child_samples=300,
                                  subsample=0.7, subsample_freq=1, colsample_bytree=0.6, reg_lambda=5,
                                  n_jobs=2, verbose=-1, random_state=seed)
    if name == "et":
        from sklearn.ensemble import ExtraTreesClassifier
        return ExtraTreesClassifier(n_estimators=200, min_samples_leaf=200, max_features=0.3, n_jobs=2, random_state=seed)
    if name == "rf":
        from sklearn.ensemble import RandomForestClassifier
        return RandomForestClassifier(n_estimators=150, min_samples_leaf=300, max_features=0.2, max_samples=0.5, n_jobs=2, random_state=seed)
    if name == "lr":
        from sklearn.linear_model import LogisticRegression
        return make_pipeline(StandardScaler(), LogisticRegression(C=0.05, max_iter=500))
    if name == "mlp":
        from sklearn.neural_network import MLPClassifier
        return make_pipeline(StandardScaler(), MLPClassifier((64, 32), alpha=1e-3, batch_size=512, learning_rate_init=1e-3,
                                                             max_iter=30, early_stopping=True, n_iter_no_change=4, random_state=seed))
    raise ValueError(name)

MAXTRAIN = {"lgb": 200000, "et": 150000, "rf": 150000, "lr": 10**9, "mlp": 200000}

def parse(s):
    p = s.split(":")
    return ("usd", float(p[1])) if p[0] == "usd" else ("atr", float(p[1]), p[2])

def run(TF, model, spec, Xextra=None, tag=""):
    b, X = C.build_dataset(TF)
    if Xextra is not None:
        X = Xextra
    L = C.labels(b, TF, spec)
    D = X.loc[L.index]
    e = np.maximum(L.eL.values, L.eS.values)
    prob = pd.Series(np.nan, index=L.index)
    rng = np.random.default_rng(0)
    for bi, tr, te in C.folds(L.index, L.i.values, e):
        trm = tr & (L.yL.values != L.yS.values)
        ii = np.flatnonzero(trm)
        if len(ii) > MAXTRAIN[model]:
            ii = np.sort(rng.choice(ii, MAXTRAIN[model], replace=False))
        Xt = D.iloc[ii]; yt = (L.yL.values[ii] > 0).astype(int)
        med = Xt.median()
        m = make_model(model)
        if model == "lgb":
            m.fit(Xt, yt); p = m.predict_proba(D[te])[:, 1]
        else:
            m.fit(Xt.fillna(med).values, yt); p = m.predict_proba(D[te].fillna(med).values)[:, 1]
        prob[te] = p
    side = np.where(prob.values >= 0.5, 1.0, -1.0); side[np.isnan(prob.values)] = np.nan
    # decision-level accuracy on test rows
    ok = ~np.isnan(side)
    win = np.where(side > 0, L.yL.values > 0, L.yS.values > 0)
    full_side = pd.Series(np.nan, index=b.index); full_side.loc[L.index] = side
    full_side = full_side.ffill(limit=1)  # rows dropped only at data end
    st, trades = C.evaluate(full_side.values, b, TF, spec)
    name = f"{model}{tag}|{TF}|{C.spec_name(spec)}"
    acc = {p: round(win[ok & (L.index >= a) & (L.index < z)].mean() * 100, 2) for p, (a, z) in H.PERIODS.items()}
    print(H.fmt(name, st), "| rowacc", acc, "| passes", H.passes(st), flush=True)
    with open("/home/user/trading-bridge/research/families/C_ml/results_raw.tsv", "a") as f:
        f.write("\t".join([name] + [f"{p}:n={st[p].get('n')},wr={st[p].get('wr')}" for p in st] +
                          [f"rowacc={acc}", f"passes={H.passes(st)}"]) + "\n")
    prob.to_frame("p").to_parquet(f"{C.CACHE}/oof_{name.replace('|','_')}.parquet")
    return st, prob

if __name__ == "__main__":
    TF, model = sys.argv[1], sys.argv[2]
    for s in sys.argv[3].split(";"):
        t = time.time(); run(TF, model, parse(s)); print("  time", round(time.time() - t), flush=True)
