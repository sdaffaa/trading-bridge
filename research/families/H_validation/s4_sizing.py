"""Item 4: position sizing for the best credible candidate (A1 = current EA) and, for context, its
always-long twin and E1. Trades in R from harness2 (consecutive, so no overlap for A1); equity compounds
per trade: eq *= 1 + risk_t * R. Each period starts at equity 1 (independent evaluation).
Schemes (all parameters estimated on IS only):
  FF    : fixed fractional, risk_t = base.
  VT    : volatility-targeted, risk_t = base * clip(sigma_IS / sigma_t, 0.5, 2), sigma_t = std of the
          strategy's daily R over the previous 20 trading days (causal), sigma_IS = IS median of sigma_t.
  KELLY : fractional Kelly, f* = mean(R)/var(R) per trade on IS; 1/4 and 1/2 Kelly; plus a 'CI-Kelly'
          that uses the lower 95% bootstrap bound of IS mean R (estimation-risk-shrunk).
Metrics per period: CAGR, maxDD %, green days %, green months %, P(losing month) = observed share and
stationary-bootstrap estimate (21-day months, mean block 10 days, 5000 draws)."""
import sys, numpy as np, pandas as pd, json
sys.path.insert(0, "/home/user/trading-bridge/research")
import hlib as L
days_all = pd.to_datetime(pd.read_parquet(f"{L.SCR}/daily.parquet").index)
rng = np.random.default_rng(7)


def sim(tr, risk):
    """risk: array per trade. Returns daily % return series on the weekday calendar."""
    eq = np.cumprod(1 + risk * tr.R.values)
    e = pd.Series(eq, index=tr.exit_t.dt.normalize()).groupby(level=0).last()
    e = e.reindex(days_all).ffill().fillna(1.0)
    return e.pct_change().fillna(e.iloc[0] - 1)


def metrics(r, xd):
    """xd: boolean Series, True on days with >=1 exit. Green day = equity up that day (flat +1R-1R days are
    slightly negative after compounding and count as not green; harness2.stats counts R-sums of ~1e-14 as green)."""
    eq = (1 + r).cumprod(); yrs = len(r) / 260
    mo = (1 + r).groupby(r.index.to_period("M")).prod() - 1
    x = r.values; B = 5000
    idx = L.stationary_idx(len(x), B, 10, rng)[:, :21]
    pm = ((1 + x[idx]).prod(1) - 1 < 0).mean()
    return dict(CAGR=round((eq.iloc[-1] ** (1 / yrs) - 1) * 100, 1), maxDD=round(((eq / eq.cummax()) - 1).min() * 100, 1),
                green_days=round((r[xd] > 1e-12).mean() * 100, 1), green_wkdays=round((r > 1e-12).mean() * 100, 1), green_months=round((mo > 0).mean() * 100, 1),
                P_lose_month_obs=round((mo < 0).mean() * 100, 1), P_lose_month_boot=round(pm * 100, 1))


out = []
for cand in ("A1", "A1_long", "E1"):
    TR = pd.read_parquet(f"{L.SCR}/trades_{cand}.parquet").sort_values("exit_t").reset_index(drop=True)
    isR = TR.R[TR.t < "2023-07-01"].values
    kelly = isR.mean() / isR.var()
    lo = np.percentile(isR[rng.integers(0, len(isR), (10000, len(isR)))].mean(1), 2.5)
    kelly_lo = max(lo, 0) / isR.var()
    # causal trailing vol of the strategy's daily R (unit risk)
    dR = TR.groupby(TR.exit_t.dt.normalize()).R.sum().reindex(days_all).fillna(0)
    sig = dR.rolling(20).std().shift(1)
    sig_is = sig[(sig.index >= "2020-07-01") & (sig.index < "2023-07-01")].median()
    lev_d = (sig_is / sig).clip(0.5, 2).fillna(1.0)
    lev = lev_d.reindex(TR.t.dt.normalize()).fillna(1.0).values   # known at start of entry day
    schemes = {}
    for b in (0.0025, 0.005, 0.01):
        schemes[f"FF {b*100:.2f}%"] = np.full(len(TR), b)
        schemes[f"VT {b*100:.2f}%"] = b * lev
    for fr in (0.25, 0.5):
        schemes[f"Kelly x{fr} ({kelly*fr*100:.2f}%)"] = np.full(len(TR), max(kelly, 0) * fr)
    schemes[f"CI-Kelly x0.5 ({kelly_lo*50:.2f}%)"] = np.full(len(TR), kelly_lo * 0.5)
    print(cand, "IS Kelly f* =", round(kelly * 100, 2), "% ; CI-lower Kelly =", round(kelly_lo * 100, 2), "%; sigma_IS", round(sig_is, 3), flush=True)
    for nm, rk in schemes.items():
        r = sim(TR, rk)
        xd = pd.Series(days_all.isin(TR.exit_t.dt.normalize()), index=days_all)
        for p in ("IS", "VAL", "HOLDOUT"):
            m = metrics(L.sl_period(r, p), L.sl_period(xd, p)); out.append(dict(cand=cand, scheme=nm, period=p, **m))
df = pd.DataFrame(out); df.to_csv("s4_sizing.csv", index=False)
pd.set_option("display.width", 250)
print(df.to_string(index=False))
