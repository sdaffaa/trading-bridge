"""Final top-10 (chosen by IS win rate, diversified across idea families; nothing
confirmed on VAL) evaluated ONCE on all periods with harness.run_consecutive."""
import pickle, numpy as np, pandas as pd
from numba import njit
from core import *
from features_d import build, NAMES
from rule_search_fns import rule_dir_all
import state_ideas_fns as SF

X = np.ascontiguousarray(build())
col = {n: np.asarray(X[:, j], np.float64) for j, n in enumerate(NAMES)}
a1 = atr_m1("1h"); px = htf(M1.close.resample("1D").last().dropna(), "1D")
SCH = {"1xATRh1": a1, "2xATRh1": 2 * a1, "4xATRh1": 4 * a1, "0.25%px": 0.0025 * px,
       "0.5%px": 0.005 * px, "$8": np.full(N, 8.0)}
SP = "/tmp/claude-0/-home-user-trading-bridge/b109c4cd-e10b-5fab-96f6-d6f544632108/scratchpad/"
fin = []
for tag, take, lab in (("", 4, "GA(all dists)"), ("_mid", 2, "GA(2xATR/0.5%)"), ("_small", 1, "GA(1xATR/0.25%)")):
    d = pickle.load(open(SP + f"D_rules{tag}.pkl", "rb"))
    seen = set(); k = 0
    for r in d["ga"]:
        kk = r["K"] + (r["kind"] == 1)          # genes actually used by the rule
        key = (r["kind"], r["K"], tuple(r["f"][:kk]), tuple(r["q"][:kk]), tuple(r["s"][:kk]),
               r["A"] if r["kind"] == 1 else 0, r["sc"])
        if key in seen: continue
        seen.add(key)
        dirs = rule_dir_all(X, r["kind"], r["f"], r["q"], r["s"], r["K"], r["A"], d["QT"])
        fin.append((f"{lab} #{k+1} {d['SN'][r['sc']]}", dirs, SCH[d["SN"][r["sc"]]]))
        k += 1
        if k >= take: break
    if tag == "":
        r = d["rnd"][0]
        fin.append((f"random-search best-IS {d['SN'][r['sc']]}",
                    rule_dir_all(X, r["kind"], r["f"], r["q"], r["s"], r["K"], r["A"], d["QT"]), SCH[d["SN"][r["sc"]]]))
# structure: prevday toward-farther, dist = far level (floor 2xATR)
u = col["to_pdh"] * a1; dd = col["to_pdl"] * a1
u = np.where(u > 0, u, np.nan); dd = np.where(dd > 0, dd, np.nan)
upnear = u < dd; far = np.where(upnear, dd, u)
fin.append(("structure: prev-day level, toward farther, dist=far(>=2ATR)", np.where(upnear, -1.0, 1.0),
            np.fmax(np.nan_to_num(far, nan=0), 2 * a1)))
poc = col["to_poc"] * a1
fin.append(("volume-profile: away from prev-day POC, dist=|c-POC|(>=2ATR)", np.where(poc > 0, 1.0, -1.0),
            np.fmax(np.abs(poc), 2 * a1)))
u = -col["to_vah"] * a1; dd = col["to_val"] * a1
u = np.where(u > 0, u, np.nan); dd = np.where(dd > 0, dd, np.nan)
upnear = u < dd; far = np.where(upnear, dd, u)
fin.append(("structure: value-area edge, toward farther, dist=far(>=2ATR)", np.where(upnear, -1.0, 1.0),
            np.fmax(np.nan_to_num(far, nan=0), 2 * a1)))
# asymmetry: per-hour (distance scheme, side) chosen on IS in asym.py (mapping copied from asym.out)
ad = atr_m1("1D")
SCA = {"4xATRh1": 4 * a1, "2xATRh1": 2 * a1, "0.5xATRd1": 0.5 * ad, "$8": np.full(N, 8.0),
       "0.5%px": 0.005 * px, "$5": np.full(N, 5.0), "$13": np.full(N, 13.0), "0.25%px": 0.0025 * px}
HB = {0: ("4xATRh1", 1), 1: ("2xATRh1", -1), 2: ("2xATRh1", -1), 3: ("2xATRh1", -1), 4: ("2xATRh1", -1),
      5: ("4xATRh1", -1), 6: ("4xATRh1", -1), 7: ("0.5xATRd1", -1), 8: ("4xATRh1", -1), 9: ("$8", -1),
      10: ("$8", -1), 11: ("0.5%px", -1), 12: ("$8", -1), 13: ("$8", -1), 14: ("$5", -1), 15: ("$13", 1),
      16: ("$13", 1), 17: ("$13", 1), 18: ("$13", 1), 19: ("$13", 1), 20: ("$13", 1), 21: ("$13", 1),
      22: ("0.25%px", 1), 23: ("4xATRh1", 1)}
hr = T.hour.values; dA = np.zeros(N); sA = np.zeros(N)
for h_, (sc_, sd_) in HB.items():
    m_ = hr == h_; dA[m_] = SCA[sc_][m_]; sA[m_] = sd_
fin.append(("asymmetry: per-hour best (dist scheme, side) from IS", sA, dA))
rows = []
for name, dirs, dist in fin:
    tr, st = full_run(np.nan_to_num(dirs), dist)
    rows.append((name, st)); print(H.fmt(name[:45], st), "PASS" if H.passes(st) else "", flush=True)
# state idea (custom loop, same fills)
e, x, r, s = SF.run_state(O, HI, LO, np.asarray(4 * a1, np.float64), H.SPREAD, WARM0, N, 4, 4)
st = H.stats(to_df(e, x, r, s)); name = "state: follow barrier, fade after 4 | 4xATRh1"
rows.append((name, st)); print(H.fmt(name[:45], st), "PASS" if H.passes(st) else "", flush=True)
e, x, r, s = SF.run_state(O, HI, LO, np.asarray(4 * a1, np.float64), H.SPREAD, WARM0, N, 0, 0)
st = H.stats(to_df(e, x, r, s)); name = "state: barrier-momentum | 4xATRh1"
rows.append((name, st)); print(H.fmt(name[:45], st), "PASS" if H.passes(st) else "", flush=True)
out = pd.DataFrame([dict(name=n, **{f"{p}_{k}": v[p].get(k) for p in ("IS", "VAL", "HOLDOUT") for k in ("n", "wr")},
                         passes=H.passes(v)) for n, v in rows])
out.to_csv("final_top10.csv", index=False); print(out.to_string())
