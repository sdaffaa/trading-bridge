"""Family 6: combinations (weights from IS daily-return covariance only), position-level netting,
rescaled to 10% IS vol. Also EA-friendly execution variants (rebalance once a day at NY 16:00 bar)."""
import numpy as np, pandas as pd, json
from scipy.optimize import minimize
import common as G, signals as S, build as Bd, harness3 as H3

a, b = G.PER["IS"]
names = ["tsmom_ra_10d_LF", "ewmac_128_512_LF", "kf_slope_ql1.0_qs1e-05_LF", "hmm3_r_tsmomra10d_fliphigh_LF",
         "garchfilt_scaled_tsmomra10d_LF", "ou_L240_z2.5_0.0_hurst120_LF", "twapmom_z1.5_LS",
         "bh_vt10", "ewmac_128_512_LS", "tsmom_ra_10d_LS"]
P = {n: Bd.pos(n) for n in names}
D = pd.DataFrame({n: G.daily_all(H3.pnl(P[n], G.B)) for n in names})
Dis = D[(D.index >= a) & (D.index < b)]
print("IS corr\n", Dis.corr().round(2).to_string())


def erc(cov):
    n = len(cov); x0 = np.ones(n) / n
    f = lambda w: ((w * (cov @ w)) / (w @ cov @ w) - 1 / n).__pow__(2).sum()
    r = minimize(f, x0, bounds=[(0, 1)] * n, constraints={"type": "eq", "fun": lambda w: w.sum() - 1})
    return r.x


def combo(tag, members, method):
    cov = Dis[members].cov().values
    if method == "erc": w = erc(cov)
    elif method == "ivar": w = 1 / np.diag(cov); w /= w.sum()
    elif method == "ivol": w = 1 / np.sqrt(np.diag(cov)); w /= w.sum()
    else: w = np.ones(len(members)) / len(members)
    p = sum(wi * P[m] for wi, m in zip(w, members))
    d = G.daily_all(H3.pnl(p, G.B)); v = d[(d.index >= a) & (d.index < b)].std() * np.sqrt(260)
    k = 0.10 / v
    p = p * k
    wts = {m: round(float(wi * k), 3) for wi, m in zip(w, members)}
    row = G.evaluate(tag, "6_combo", p, dict(method=method, weights=wts))
    print(tag, wts)
    return row


ALL = names[:7]
TREND = names[:5]
for meth in ("erc", "ivar", "ivol", "eq"):
    combo(f"combo_all7_{meth}", ALL, meth)
    combo(f"combo_trend5_{meth}", TREND, meth)
combo("combo_trend3+intraday_erc", ["tsmom_ra_10d_LF", "ewmac_128_512_LF", "kf_slope_ql1.0_qs1e-05_LF", "twapmom_z1.5_LS"], "erc")
combo("combo_bh+trendLS+intraday_erc", ["bh_vt10", "ewmac_128_512_LS", "tsmom_ra_10d_LS", "twapmom_z1.5_LS"], "erc")
combo("combo_bh+trendLS_erc", ["bh_vt10", "ewmac_128_512_LS", "tsmom_ra_10d_LS"], "erc")
combo("combo_bh+trendLF+intraday_erc", ["bh_vt10", "ewmac_128_512_LF", "tsmom_ra_10d_LF", "twapmom_z1.5_LS"], "erc")
# EA execution variants: rebalance only at the NY 16:00 bar (decision at 17:00 NY close)
for n in ("tsmom_ra_10d_LF", "ewmac_128_512_LF", "kf_slope_ql1.0_qs1e-05_LF"):
    G.evaluate(f"{n}_daily16", "6_exec", Bd.pos(n, hours=[16]), dict(base=n, rebalance="NY16 daily"))
df = G.save("g6"); print(len(df), "configs"); G.show(df, n=30)
