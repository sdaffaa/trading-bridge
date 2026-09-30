"""Build trade lists (harness2.run, R units) for all candidates and their always-long baselines.
Output: SCR/trades_<name>.parquet and SCR/daily.parquet (calendar = all weekdays with M1 data, 0 when no exit)."""
import sys, os, time, numpy as np, pandas as pd
R = "/home/user/trading-bridge/research"
for p in (R, R + "/solution", R + "/families/A_indicators"):
    sys.path.insert(0, p)
import harness as H, harness2 as H2
SCR = "/tmp/claude-0/-home-user-trading-bridge/b109c4cd-e10b-5fab-96f6-d6f544632108/scratchpad/H"
os.makedirs(SCR, exist_ok=True)
m1 = H.load_m1(); N = len(m1); IDX = m1.index
START = IDX >= pd.Timestamp(H.PERIODS["IS"][0])
out = {}

def save(name, tr):
    tr.to_parquet(f"{SCR}/trades_{name}.parquet"); out[name] = tr
    print(H2.fmt(name, H2.stats(tr)), flush=True)

t0 = time.time()
# (a) family A combo #1, SL=TP=3xATR(H1), consecutive
import validate_lib as V
c = pd.read_csv(R + "/families/A_indicators/final10_holdout.csv").iloc[0]
d = V.dirs_of(c.combo); d = (-d if c.inv else d).astype(np.float64); d[~START] = 0
sl = np.asarray(V.R[c.dist], float)
np.save(f"{SCR}/A1_dirs.npy", d); np.save(f"{SCR}/A1_sl.npy", sl)
save("A1", H2.run(d, sl, sl))
save("A1_long", H2.run(np.where(START, 1.0, 0.0), sl, sl))
print("A done", round(time.time() - t0), flush=True)

# (b) family E top 3
import importlib.util
def load(name, path):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sys.modules[name] = m; sp.loader.exec_module(m); return m
EC = load('ecommon', R + '/families/E_profit/common.py')
spec = pd.read_csv(R + "/families/E_profit/final10_spec.csv").head(3)
E = EC.registry()
for k, r in spec.iterrows():
    trk = None if pd.isna(r.trk) else r.trk
    dd, s, tp, trl, mb = EC.build(r["name"], r.slmode, r.slk, r.tpr, trk, int(r.mb), r.filt, E)
    dd = np.where(START, dd, 0.0)
    save(f"E{k+1}", H2.run(dd, s, tp, trl, mb))
    save(f"E{k+1}_long", H2.run(np.where(START, 1.0, 0.0), s, tp, trl, mb))           # L_every
    save(f"E{k+1}_Lsame", H2.run(np.where(dd != 0, 1.0, 0.0), s, tp, trl, mb))        # L_same
print("E done", round(time.time() - t0), flush=True)

# (c) family C reg 1h tp1.5 both theta=0 (cached seed-0 OOF / walk-forward predictions)
sys.path.insert(0, R + '/families/C_ml'); sys.modules.pop('common', None)
import profit as CP
g = [x for x in CP.GEOMS if x[0] == "tp1.5"][0]
b, L, P = CP.oof("1h", g, "reg")
dc = CP.trade_dirs(b, "1h", L, P, 0.0, "both"); dc[~START] = 0
a1h = H.htf_to_m1(H.atr(H.bars("1h"), 14), "1h")
s, tp, trl, mb = CP.geom_arrays(g, a1h)
save("C1", H2.run(dc, s, tp, trl, mb))
dl = np.zeros(N); dl[L.i.values] = 1.0; dl[~START] = 0
save("C1_long", H2.run(dl, s, tp, trl, mb))
print("C done", round(time.time() - t0), flush=True)

# daily calendar
days = pd.Index(sorted(set(IDX[START].date)))
days = days[pd.to_datetime(days).dayofweek < 5]
D = pd.DataFrame({k: H2.daily(v).reindex(days).fillna(0.0) for k, v in out.items()}, index=days)
D.to_parquet(f"{SCR}/daily.parquet")
print(D.shape, "total", round(time.time() - t0))
