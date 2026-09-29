"""Random + genetic rule search (always-in-market formulas over the feature library).

Rule forms (always output a direction):
  VOTE   : dir = sign( sum_k s_k * sign(X[f_k] - th_k) ), K in {1,3,5}
  IFELSE : if all_k<m (s_k*(X[f_k]-th_k) > 0) -> dir A  else dir = s_d*sign(X[f_d]-th_d)
Each rule also picks one SL/TP distance scheme. Fitness = IS win rate (n>=300).
VAL is only recorded (never used for selection). HOLDOUT untouched here.
"""
import time, json, numpy as np, pandas as pd
from numba import njit
from core import *
from features_d import build, NAMES

X = np.ascontiguousarray(build()[: VAL1 + 1])          # rows up to VAL end only
F = X.shape[1]
a1 = atr_m1("1h")
px = htf(M1.close.resample("1D").last().dropna(), "1D")
SCH = {"1xATRh1": a1, "2xATRh1": 2 * a1, "4xATRh1": 4 * a1, "0.25%px": 0.0025 * px,
       "0.5%px": 0.005 * px, "$8": np.full(N, 8.0)}
import os
TAG = os.environ.get("TAG", "")
if os.environ.get("SCHEMES"):
    SCH = {k: SCH[k] for k in os.environ["SCHEMES"].split(",")}
SN = list(SCH)
print("schemes", SN)
t0 = time.time()
TB = [tables(SCH[s], WARM0, VAL1 + 1) for s in SN]
WL = np.stack([t[0][: VAL1 + 1] for t in TB]); EL = np.stack([t[1][: VAL1 + 1] for t in TB])
WS = np.stack([t[2][: VAL1 + 1] for t in TB]); ES = np.stack([t[3][: VAL1 + 1] for t in TB])
del TB
print("tables", round(time.time() - t0, 1), "s", flush=True)
QL = np.arange(0.05, 0.951, 0.05)
sub = X[IS0:IS1:7]
QT = np.stack([np.nanquantile(sub[:, j], QL) for j in range(F)]).astype(np.float64)  # (F, 19)


from rule_search_fns import rule_dir


@njit(cache=True)
def eval_rule(X, kind, f, q, s, K, A, sc, QT, WL, EL, WS, ES, i0, i1, v0, v1):
    """Walk from i0 to v1; return IS (n, wins) on [i0,i1) and VAL (n, wins) on [v0,v1)."""
    wl = WL[sc]; el = EL[sc]; ws = WS[sc]; es = ES[sc]
    n1 = 0; w1 = 0; n2 = 0; w2 = 0
    i = i0
    while i < v1:
        d = rule_dir(X[i], kind, f, q, s, K, A, QT)
        if d > 0:
            r = wl[i]; j = el[i]
        else:
            r = ws[i]; j = es[i]
        if r == 0:
            i += 1; continue
        if i < i1:
            n1 += 1; w1 += r > 0
        elif i >= v0:
            n2 += 1; w2 += r > 0
        i = j + 1
    return n1, w1, n2, w2


rng = np.random.default_rng(42)
KMAX = 6


def rand_rule():
    kind = int(rng.integers(0, 2))
    K = int(rng.choice([1, 3, 5])) if kind == 0 else int(rng.integers(1, 4))
    f = rng.integers(0, F, KMAX); q = rng.integers(0, len(QL), KMAX); s = rng.choice([-1.0, 1.0], KMAX)
    return dict(kind=kind, K=K, f=f, q=q, s=s, A=float(rng.choice([-1.0, 1.0])), sc=int(rng.integers(0, len(SN))))


def ev(r):
    n1, w1, n2, w2 = eval_rule(X, r["kind"], r["f"], r["q"], r["s"], r["K"], r["A"], r["sc"], QT,
                               WL, EL, WS, ES, IS0, IS1, VAL0, VAL1)
    return n1, (w1 / n1 if n1 else 0), n2, (w2 / n2 if n2 else 0)


def desc(r):
    cond = lambda k: f"{NAMES[r['f'][k]]}{'>' if r['s'][k] > 0 else '<'}q{QL[r['q'][k]]:.2f}"
    if r["kind"] == 0:
        body = "VOTE[" + ", ".join(cond(k) for k in range(r["K"])) + "] (+1 if true)"
    else:
        body = "IF " + " & ".join(cond(k) for k in range(r["K"])) + f" -> {int(r['A']):+d} ELSE {'+1' if r['s'][r['K']]>0 else '-1'}*sign({NAMES[r['f'][r['K']]]}-q{QL[r['q'][r['K']]]:.2f})"
    return body + f" | dist={SN[r['sc']]}"


# ---------------- 1) pure random search ----------------
NR = 60000
t0 = time.time(); res = []
rules = []
for it in range(NR):
    r = rand_rule(); n1, p1, n2, p2 = ev(r)
    rules.append(r); res.append((n1, p1, n2, p2))
res = np.array(res)
print("random search", NR, "rules in", round(time.time() - t0, 1), "s", flush=True)
ok = res[:, 0] >= 300
R = pd.DataFrame(res[ok], columns=["nIS", "wrIS", "nVAL", "wrVAL"])
R["idx"] = np.where(ok)[0]
R = R.sort_values("wrIS", ascending=False)
print("rules with IS n>=300:", len(R))
print("IS wr quantiles:", R.wrIS.quantile([.5, .9, .99, .999, 1]).round(4).to_dict())
print("\nDecay curve (random search): rank bucket by IS wr -> mean IS wr, mean VAL wr")
for lo, hi in ((0, 10), (10, 100), (100, 1000), (1000, 10000), (10000, len(R))):
    g = R.iloc[lo:hi]
    print(f"  IS rank {lo:>6}-{hi:<6} mean IS {g.wrIS.mean()*100:.2f}  mean VAL {g.wrVAL.mean()*100:.2f}  max VAL {g.wrVAL.max()*100:.2f}")
print("Spearman(IS wr, VAL wr) all:", round(R[["wrIS", "wrVAL"]].corr("spearman").iloc[0, 1], 3),
      " top1000:", round(R.iloc[:1000][["wrIS", "wrVAL"]].corr("spearman").iloc[0, 1], 3))
print("\nTop 10 random rules by IS:")
for _, row in R.head(10).iterrows():
    print(f"  IS n={int(row.nIS)} wr={row.wrIS*100:.2f} | VAL n={int(row.nVAL)} wr={row.wrVAL*100:.2f} | {desc(rules[int(row.idx)])}")
print("Max IS wr by distance scheme:")
R["sc"] = [SN[rules[int(i)]["sc"]] for i in R.idx]
print(R.groupby("sc")[["wrIS", "wrVAL"]].max().round(4).to_string())

# ---------------- 2) genetic evolution on IS ----------------
def mutate(r):
    r = {k: (v.copy() if isinstance(v, np.ndarray) else v) for k, v in r.items()}
    for _ in range(int(rng.integers(1, 3))):
        m = rng.integers(0, 6 if len(SN) > 1 else 5)
        m = 5 if m == 4 and len(SN) == 1 else m
        k = int(rng.integers(0, KMAX))
        if m == 0: r["f"][k] = rng.integers(0, F)
        elif m == 1: r["q"][k] = np.clip(r["q"][k] + rng.integers(-2, 3), 0, len(QL) - 1)
        elif m == 2: r["s"][k] *= -1
        elif m == 3: r["A"] *= -1
        elif m == 4: r["sc"] = int(rng.integers(0, len(SN)))
        else:
            if r["kind"] == 0: r["K"] = int(rng.choice([1, 3, 5]))
            else: r["K"] = int(rng.integers(1, 4))
    return r


def cross(a, b):
    c = {k: (v.copy() if isinstance(v, np.ndarray) else v) for k, v in a.items()}
    m = rng.random(KMAX) < 0.5
    c["f"][m] = b["f"][m]; c["q"][m] = b["q"][m]; c["s"][m] = b["s"][m]
    return c


def fit(n1, p1):
    return p1 if n1 >= 300 else 0.0


POP, GEN = int(os.environ.get("POP", 400)), int(os.environ.get("GEN", 60))
# seed population with the best random rules (by IS only)
pop = [rules[int(i)] for i in R.idx[:POP // 2]] + [rand_rule() for _ in range(POP - POP // 2)]
sc = [ev(r) for r in pop]
curve = []
t0 = time.time()
for g in range(GEN):
    fits = np.array([fit(s[0], s[1]) for s in sc])
    order = np.argsort(-fits)
    elite = [pop[i] for i in order[:40]]; esc = [sc[i] for i in order[:40]]
    b = sc[order[0]]
    top10 = [sc[i] for i in order[:10]]
    curve.append(dict(gen=g, best_IS=b[1], best_VAL=b[3], top10_IS=np.mean([s[1] for s in top10]),
                      top10_VAL=np.mean([s[3] for s in top10]), nIS=b[0], nVAL=b[2]))
    if g % 10 == 0 or g == GEN - 1:
        print(f"gen {g}: best IS {b[1]*100:.2f} (n={b[0]}) -> VAL {b[3]*100:.2f} (n={b[2]}); top10 IS {curve[-1]['top10_IS']*100:.2f} VAL {curve[-1]['top10_VAL']*100:.2f}", flush=True)
    newp = list(elite); news = list(esc)
    while len(newp) < POP:
        i, j = rng.integers(0, len(pop), 2), rng.integers(0, len(pop), 2)
        pa = pop[i[0]] if fits[i[0]] > fits[i[1]] else pop[i[1]]
        pb = pop[j[0]] if fits[j[0]] > fits[j[1]] else pop[j[1]]
        c = mutate(cross(pa, pb) if rng.random() < 0.5 else pa)
        newp.append(c); news.append(ev(c))
    pop, sc = newp, news
print("GA time", round(time.time() - t0, 1), "s")
fits = np.array([fit(s[0], s[1]) for s in sc]); order = np.argsort(-fits)
print("\nGA final top 10 (selected on IS):")
seen = set(); out = []
for i in order:
    d = desc(pop[i])
    if d in seen: continue
    seen.add(d); s = sc[i]
    print(f"  IS n={s[0]} wr={s[1]*100:.2f} | VAL n={s[2]} wr={s[3]*100:.2f} | {d}")
    out.append(dict(rule=d, nIS=int(s[0]), wrIS=float(s[1]), nVAL=int(s[2]), wrVAL=float(s[3])))
    if len(out) >= 10: break
pd.DataFrame(curve).to_csv(f"ga_curve{TAG}.csv", index=False)
json.dump(out, open(f"ga_top10{TAG}.json", "w"), indent=1)
# save top random + GA rules (IS-selected) for later holdout of finalists
import pickle
pickle.dump(dict(ga=[pop[i] for i in order[:50]], rnd=[rules[int(i)] for i in R.idx[:50]], QT=QT, SN=SN),
            open(f"/tmp/claude-0/-home-user-trading-bridge/b109c4cd-e10b-5fab-96f6-d6f544632108/scratchpad/D_rules{TAG}.pkl", "wb"))
