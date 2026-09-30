"""Pre-declared selection (no HOLDOUT data used): pool = every strategy config in reg_g*.csv.
Rule: IS_sr > 0 and VAL_sr > 0; rank by IS_sr (Sharpe incl. flat days); skip a config whose IS+VAL daily
returns correlate > 0.95 with an already selected one; keep 10."""
import glob, pandas as pd, numpy as np
import common as G

reg = pd.concat([pd.read_csv(f) for f in sorted(glob.glob(f"{G.HERE}/reg_g*.csv"))], ignore_index=True)
daily = pd.concat([pd.read_parquet(f) for f in sorted(glob.glob(f"{G.HERE}/daily_g*.parquet"))], axis=1)
daily = daily.loc[:, ~daily.columns.duplicated()]
a = G.PER["IS"][0]
dd = daily[daily.index >= a]
uniq = dd.T.round(10).drop_duplicates().shape[0]
print("configs:", len(reg), "unique return streams:", uniq)
pool = reg[(reg.IS_sr > 0) & (reg.VAL_sr > 0)].sort_values("IS_sr", ascending=False)
print("pass IS>0 & VAL>0:", len(pool))
sel = []
for n in pool.name:
    if all(abs(np.corrcoef(dd[n], dd[s])[0, 1]) <= 0.95 for s in sel):
        sel.append(n)
    if len(sel) == 10:
        break
top = pool.set_index("name").loc[sel].reset_index()
print(top[["name", "fam", "IS_sr", "IS_ret", "IS_dd", "VAL_sr", "VAL_ret", "VAL_dd", "turn"]].to_string(index=False))
top.to_csv(f"{G.HERE}/top10_selected.csv", index=False)
reg.to_csv(f"{G.HERE}/all_configs.csv", index=False)
# IS Sharpe dispersion across all trials (for DSR)
isr = []
for n in dd.columns:
    x = dd.loc[(dd.index >= G.PER["IS"][0]) & (dd.index < G.PER["IS"][1]), n]
    isr.append(x.mean() / x.std() if x.std() > 0 else 0.0)
ivr = []
for n in dd.columns:
    x = dd.loc[dd.index < G.VAL_END, n]
    ivr.append(x.mean() / x.std() if x.std() > 0 else 0.0)
pd.DataFrame({"name": dd.columns, "sr_is_daily": isr, "sr_isval_daily": ivr}).to_csv(f"{G.HERE}/trial_sharpes.csv", index=False)
print("std of daily IS SR across trials: %.4f (ann %.3f)" % (np.std(isr), np.std(isr) * np.sqrt(260)))
