"""Always-in-market 1:1 XAUUSD backtester on M1 bars.

Rules modelled exactly like the EA:
  * one position at a time, fixed SL distance = TP distance (1:1)
  * a new position opens on the first bar after the previous one closes
    (or after the direction signal appears, if `wait` is used)
  * if SL and TP are both inside the same M1 bar -> counted as a LOSS (conservative)
  * spread is paid on every trade (entry at ask for buys / bid for sells)
"""
import sys
import numpy as np
import pandas as pd

DATA = sys.argv[1] if len(sys.argv) > 1 else "XAUUSD_M1.csv"
SPREAD = 0.25  # USD per ounce, typical ECN gold spread


def load(path):
    df = pd.read_csv(path, parse_dates=["datetime"]).set_index("datetime")
    return df[["open", "high", "low", "close"]].astype(float)


def indicators(m1):
    m5 = m1.resample("5min").agg({"open": "first", "high": "max", "low": "min", "close": "last"}).dropna()
    tr = pd.concat([m5.high - m5.low, (m5.high - m5.close.shift()).abs(), (m5.low - m5.close.shift()).abs()], axis=1).max(axis=1)
    f = pd.DataFrame(index=m5.index)
    f["atr"] = tr.rolling(14).mean()
    f["ema_fast"] = m5.close.ewm(span=20).mean()
    f["ema_slow"] = m5.close.ewm(span=50).mean()
    f["ema200"] = m5.close.ewm(span=200).mean()
    d = m5.close.diff()
    up = d.clip(lower=0).ewm(alpha=1 / 14).mean()
    dn = (-d.clip(upper=0)).ewm(alpha=1 / 14).mean()
    f["rsi"] = 100 - 100 / (1 + up / dn)
    f["mom"] = m5.close - m5.close.shift(12)
    f["close"] = m5.close
    mid = m5.close.rolling(20).mean()
    sd = m5.close.rolling(20).std()
    f["bb_z"] = (m5.close - mid) / sd
    # H1 trend
    h1 = m1.close.resample("1h").last().dropna()
    h1ema = h1.ewm(span=50).mean()
    f["h1_trend"] = np.sign(h1 - h1ema).shift(1).reindex(f.index, method="ffill")  # completed H1 only
    # shift by one M5 bar: only completed bars are known at decision time
    f = f.shift(1)
    return f.reindex(m1.index, method="ffill")


STRATS = {
    "random": lambda r, rng: rng.choice([1, -1]),
    "trend_ema": lambda r, rng: 1 if r.ema_fast > r.ema_slow else -1,
    "trend_ema200": lambda r, rng: 1 if r.close > r.ema200 else -1,
    "momentum": lambda r, rng: 1 if r.mom > 0 else -1,
    "h1_trend": lambda r, rng: 1 if r.h1_trend > 0 else -1,
    "meanrev_rsi": lambda r, rng: 1 if r.rsi < 50 else -1,
    "meanrev_bb": lambda r, rng: 1 if r.bb_z < 0 else -1,
    "trend_pullback": lambda r, rng: (1 if r.rsi < 50 else -1) if (r.ema_fast > r.ema_slow) == (r.rsi < 50) else 0,
    "confluence": lambda r, rng: (1 if r.h1_trend > 0 else -1) if ((r.ema_fast > r.ema_slow) == (r.h1_trend > 0) == (r.mom > 0)) else 0,
}


def run(m1, f, strat, atr_mult, max_wait=None, seed=0):
    rng = np.random.default_rng(seed)
    o, h, l = m1.open.values, m1.high.values, m1.low.values
    fx = f.values
    cols = {c: i for i, c in enumerate(f.columns)}
    Row = type("Row", (), {})
    res, days = [], []
    i, n = 300, len(m1)
    fn = STRATS[strat]
    while i < n - 1:
        r = Row()
        for c, k in cols.items():
            setattr(r, c, fx[i, k])
        if np.isnan(r.atr):
            i += 1
            continue
        d = fn(r, rng)
        if d == 0:  # strategy says wait
            i += 1
            continue
        dist = atr_mult * r.atr
        entry = o[i] + (SPREAD / 2) * d  # buy at ask / sell at bid
        tp, sl = entry + d * dist, entry - d * dist
        j = i
        out = None
        while j < n:
            # exits are triggered on the opposite side of the book
            hi, lo = h[j] + (SPREAD / 2 if d < 0 else -SPREAD / 2) * -1 * -1, l[j]
            if d > 0:
                hit_sl, hit_tp = l[j] - SPREAD / 2 <= sl, h[j] - SPREAD / 2 >= tp
            else:
                hit_sl, hit_tp = h[j] + SPREAD / 2 >= sl, l[j] + SPREAD / 2 <= tp
            if hit_sl:
                out = -1
                break
            if hit_tp:
                out = 1
                break
            j += 1
        if out is None:
            break
        res.append(out)
        days.append(m1.index[i].date())
        i = j + 1
    res = np.array(res)
    return res, pd.Series(res, index=pd.Index(days))


def summary(name, res, byday):
    if len(res) == 0:
        return None
    wr = (res > 0).mean()
    daily = byday.groupby(level=0).apply(lambda s: (s > 0).mean())
    return dict(strategy=name, trades=len(res), winrate=round(wr * 100, 1),
                net_R=int(res.sum()), days=len(daily),
                days_65_85=round(((daily >= .65)).mean() * 100, 1),
                median_daily_wr=round(daily.median() * 100, 1))


if __name__ == "__main__":
    m1 = load(DATA)
    f = indicators(m1)
    split = m1.index[int(len(m1) * 0.66)]
    rows = []
    for name in STRATS:
        for k in (0.5, 1.0, 2.0, 4.0):
            for part, sl in (("IS", slice(None, split)), ("OOS", slice(split, None))):
                mm, ff = m1.loc[sl], f.loc[sl]
                res, byday = run(mm, ff, name, k)
                s = summary(name, res, byday)
                if s:
                    s.update(atr_mult=k, sample=part)
                    rows.append(s)
    out = pd.DataFrame(rows)
    pd.set_option("display.width", 200)
    print(out.sort_values(["sample", "winrate"], ascending=[True, False]).to_string(index=False))
