"""Stage 2: (a) out-of-sample decay of the IS ranking (by IS SQN) on VAL, (b) pick single-strategy
finalists on IS+VAL, (c) re-run them with the REAL harness2 (HOLDOUT masked -> invisible),
(d) build the candidate pool for portfolios and save daily R series (IS+VAL only).
Selection rule (fixed before looking): universe = IS n>=300; candidates = IS top-400 by IS SQN;
keep VAL R>0 and VAL PF>=1.05; rank by min(IS_sqn, VAL_sqn*sqrt(IS_n/VAL_n)) (VAL sqn scaled to IS length)."""
import sys, json
import numpy as np, pandas as pd
sys.path.insert(0, "/home/user/trading-bridge/research/families/F_portfolio")
import common as C
import harness2 as H2
D = "/home/user/trading-bridge/research/families/F_portfolio/"
pd.set_option("display.width", 250); pd.set_option("display.max_colwidth", 110)

s = pd.read_parquet(D + "s1_single.parquet")
s["combo"] = [f"SIG[{(a, b, c)}]" for a, b, c in zip(s.tf, s.sig, s.inv)]; s["inv"] = False
m = pd.read_parquet(D + "s1_mtf.parquet")
u = pd.concat([s[m.columns], m], ignore_index=True)
u = u[u.IS_n >= 300].copy()
print("universe (IS n>=300):", len(u), "of", len(s) + len(m))
u["kind"] = u.combo.str.split("[").str[0]
u["dec"] = pd.qcut(u.IS_sqn.rank(method="first"), 20, labels=False)
print("\nVAL behaviour by IS-SQN vingtile (19 = best 5%):")
print(u.groupby("dec")[["IS_sqn", "VAL_sqn", "VAL_R"]].mean().round(2).T.to_string())
top = u.nlargest(400, "IS_sqn")
print("\nIS top-400: mean IS sqn %.2f, mean VAL sqn %.2f, share VAL R>0 %.1f%%, mean VAL R %.1f" %
      (top.IS_sqn.mean(), top.VAL_sqn.mean(), 100 * (top.VAL_R > 0).mean(), top.VAL_R.mean()))
print("IS top-400 by kind:", top.kind.value_counts().to_dict())
c = top[(top.VAL_R > 0) & (top.VAL_PF >= 1.05)].copy()
c["score"] = np.minimum(c.IS_sqn, c.VAL_sqn * np.sqrt(c.IS_n / c.VAL_n))
c = c.sort_values("score", ascending=False)
print("\ncandidates passing VAL filter:", len(c))
print(c.head(40).round(2).to_string())
c.to_csv(D + "s2_candidates.csv", index=False)

# real-harness re-run (HOLDOUT masked) + daily series for the pool
rows, daily = [], {}
for r in c.itertuples():
    spec = dict(combo=r.combo, inv=bool(r.inv), sl=r.sl, exit=r.exit)
    tr = C.run_spec(spec, holdout=False)
    st = H2.stats(tr, ("IS", "VAL"))
    nm = C.name_of(spec)
    daily[nm] = H2.daily(tr)
    rows.append(dict(name=nm, spec=json.dumps(spec), score=r.score,
                     **{f"{p}_{k}": st[p][k] for p in ("IS", "VAL") for k in ("n", "totR", "PF", "green_days", "R_day", "maxDD", "green_months")},
                     long_share=round((tr.side > 0).mean(), 2)))
f = pd.DataFrame(rows); f.to_csv(D + "s2_pool.csv", index=False)
pd.DataFrame(daily).fillna(0.0).to_parquet(D + "s2_pool_daily.parquet")
print("\nreal-harness2 check (IS/VAL):")
print(f.drop(columns=["spec"]).head(40).to_string())
