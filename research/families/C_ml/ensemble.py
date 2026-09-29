"""Ensembles of saved out-of-fold probabilities (same TF/spec): mean of P(long wins) across models.
Each OOF prob is itself out-of-fold (IS) / walk-forward (VAL, HOLDOUT), so the average is too.
Also 'meta' = LightGBM stacker trained on the OOF probs + a few regime features, with the same
purged folds (stacker for IS blocks trained on other IS blocks only)."""
import glob, sys, numpy as np, pandas as pd, common as C, harness as H, ml_run as R

def load(TF, sn):
    P = {}
    for f in glob.glob(f"{C.CACHE}/oof_*_{TF}_{sn}.parquet"):
        nm = f.split("oof_")[1].split(f"_{TF}_")[0]
        P[nm] = pd.read_parquet(f).p
    return pd.DataFrame(P)

def emit(name, st):
    print(H.fmt(name, st), H.passes(st), flush=True)
    with open("/home/user/trading-bridge/research/families/C_ml/results_raw.tsv", "a") as f:
        f.write("\t".join([name] + [f"{p}:n={st[p].get('n')},wr={st[p].get('wr')}" for p in st] + [f"passes={H.passes(st)}"]) + "\n")

for TF in ("15min", "1h"):
    for s in ("atr:1:1h", "atr:2:1h", "atr:3:1h", "atr:2:15min", "atr:3:15min", "usd:5", "usd:10"):
        spec = R.parse(s); sn = C.spec_name(spec)
        P = load(TF, sn)
        if P.shape[1] < 3: continue
        b, X = C.build_dataset(TF)
        pm = P.mean(axis=1)
        side = pd.Series(np.nan, index=b.index); side.loc[pm.index] = np.where(pm >= .5, 1., -1.)
        emit(f"ens_mean[{'+'.join(sorted(P.columns))}]|{TF}|{sn}", C.evaluate(side.values, b, TF, spec)[0])
        # majority vote
        v = np.sign((P >= .5).astype(int).sum(axis=1) * 2 - P.notna().sum(axis=1)); v[v == 0] = 1
        side = pd.Series(np.nan, index=b.index); side.loc[v.index] = v.values
        emit(f"ens_vote[{P.shape[1]}]|{TF}|{sn}", C.evaluate(side.values, b, TF, spec)[0])
        # stacker
        L = C.labels(b, TF, spec).loc[P.index]
        Z = P.join(X[["atr_ratio", "hour", "ret24", "ema200", "datr_ratio"]])
        e = np.maximum(L.eL.values, L.eS.values); prob = pd.Series(np.nan, index=P.index)
        for bi, tr, te in C.folds(P.index, L.i.values, e):
            trm = tr & (L.yL.values != L.yS.values) & P.notna().all(axis=1).values
            m = R.make_model("lgb"); m.set_params(n_estimators=150, num_leaves=7, min_child_samples=500)
            m.fit(Z[trm], (L.yL.values[trm] > 0).astype(int)); prob[te] = m.predict_proba(Z[te])[:, 1]
        side = pd.Series(np.nan, index=b.index); side.loc[prob.index] = np.where(prob >= .5, 1., -1.)
        emit(f"ens_stack|{TF}|{sn}", C.evaluate(side.values, b, TF, spec)[0])
