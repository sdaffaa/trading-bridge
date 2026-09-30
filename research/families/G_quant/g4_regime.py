"""Family 4: regime models. Gaussian HMM (2/3 states, expanding quarterly refit, forward-filtered probs only),
Markov-switching regression fit on IS (filtered probs), GARCH(1,1) (IS fit) for sizing and as a filter.
Trend overlay = IS-best family-1 trend forecasts (ewmac_128_512, tsmom_ra_10d), chosen on IS only."""
import numpy as np, pandas as pd, time, warnings
warnings.filterwarnings("ignore")
import common as G, signals as S
import statsmodels.api as sm

t0 = time.time()
trend = {"ewmac128": S.ewmac(128), "tsmomra10d": S.tsmom_ra(230), "ewmacmid": S.blend([S.ewmac(f) for f in (32, 64, 128, 256)])}
one = pd.Series(1.0, index=G.C.index)
gv, gp = S.garch_vol(); print("GARCH IS params", gp.round(4).to_dict())
gvb = S.daily_to_bars(gv)
# --- GARCH sizing (replaces 20d realised vol) and GARCH filter
def vt_garch(f, target=0.10):
    return (f * (target / gvb).clip(upper=3.0)).fillna(0.0)
for nm, f in [("bh", one)] + list(trend.items()):
    for m in ("LS", "LF"):
        if nm == "bh" and m == "LF": continue
        ff = S.mode(f, m)
        G.evaluate(f"garchsize_{nm}_{m}", "4_garch", G.buffer(vt_garch(ff)), dict(sig=nm, m=m))
        med = gv.rolling(260, min_periods=120).median()
        for q, lab in ((1.0, "lowvol"), (None, "scaled")):
            if q:
                gate = S.daily_to_bars((gv < med).astype(float))
                g2 = ff * gate
            else:
                g2 = ff * S.daily_to_bars((med / gv).clip(0, 2))
            G.evaluate(f"garchfilt_{lab}_{nm}_{m}", "4_garch", S.to_pos(g2), dict(sig=nm, m=m, filt=lab))
print("garch done", round(time.time() - t0), flush=True)
# --- HMM
for K in (2, 3):
    for feats in (("r", "lrv"), ("r",)):
        hm = S.hmm_expanding(K, feats)
        tag = f"hmm{K}_{'rv' if 'lrv' in feats else 'r'}"
        er = S.daily_to_bars(hm.er)
        # (a) HMM expected-return sign / magnitude
        G.evaluate(f"{tag}_ersign_LS", "4_hmm", S.to_pos(np.sign(er).fillna(0)), dict(K=K, feats=feats, rule="ersign"))
        G.evaluate(f"{tag}_ersign_LF", "4_hmm", S.to_pos(np.sign(er).clip(lower=0).fillna(0)), dict(K=K, feats=feats, rule="ersign_LF"))
        # (b) trend in calm state, reduce/flip otherwise
        pcalm = S.daily_to_bars(hm.p0); phigh = S.daily_to_bars(hm[f"p{K-1}"])
        for tn, f in trend.items():
            for m in ("LS", "LF"):
                ff = S.mode(f, m)
                G.evaluate(f"{tag}_{tn}_calmonly_{m}", "4_hmm", S.to_pos(ff * pcalm.fillna(0)), dict(K=K, feats=feats, sig=tn, m=m, rule="calm"))
                G.evaluate(f"{tag}_{tn}_cuthigh_{m}", "4_hmm", S.to_pos(ff * (1 - phigh.fillna(0))), dict(K=K, feats=feats, sig=tn, m=m, rule="cuthigh"))
                G.evaluate(f"{tag}_{tn}_fliphigh_{m}", "4_hmm", S.to_pos(ff * (1 - 2 * phigh.fillna(0))), dict(K=K, feats=feats, sig=tn, m=m, rule="fliphigh"))
        print(tag, "done", round(time.time() - t0), flush=True)
# --- Markov switching regression (2 regimes, switching mean+variance), fit on IS daily returns only
dr = np.log(S.daily_close()).diff().dropna() * 100; dr = dr[dr.index >= "2015-01-01"]
fit = dr[(dr.index >= G.PER["IS"][0]) & (dr.index < G.PER["IS"][1])]
ms = sm.tsa.MarkovRegression(fit.values, k_regimes=2, switching_variance=True).fit(disp=False)
print(ms.params)
full = sm.tsa.MarkovRegression(dr.values, k_regimes=2, switching_variance=True)
fr = full.filter(ms.params)
pf = pd.DataFrame(fr.filtered_marginal_probabilities, index=dr.index)
hi = int(np.argmax([ms.params[-2], ms.params[-1]]))   # sigma2 entries
consts = ms.params[2:4]; P = ms.regime_transition  # not used directly
ph = S.daily_to_bars(pf[hi])
erm = S.daily_to_bars(pf[0] * consts[0] + pf[1] * consts[1])
G.evaluate("ms2_ersign_LS", "4_ms", S.to_pos(np.sign(erm).fillna(0)), dict(rule="ersign"))
for tn, f in trend.items():
    for m in ("LS", "LF"):
        ff = S.mode(f, m)
        G.evaluate(f"ms2_{tn}_cuthigh_{m}", "4_ms", S.to_pos(ff * (1 - ph.fillna(0))), dict(sig=tn, m=m, rule="cuthigh"))
        G.evaluate(f"ms2_{tn}_fliphigh_{m}", "4_ms", S.to_pos(ff * (1 - 2 * ph.fillna(0))), dict(sig=tn, m=m, rule="fliphigh"))
G.evaluate("ms2_bh_cuthigh", "4_ms", S.to_pos(1 - ph.fillna(0)), dict(sig="bh", rule="cuthigh"))
df = G.save("g4"); print(len(df), "configs", round(time.time() - t0), "s"); G.show(df, n=25)
