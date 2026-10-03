"""Pre-registered hypotheses H1..H5 (see RESEARCH_PLAN.md for rationale,
invalidation criteria and the frozen parameter grids). Signals use MID prices;
execution uses bid/ask in the SimBroker. All timing is DST-aware via zoneinfo.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from tbot.data.bars import mid, trading_day
from tbot.strategies.base import (Strategy, daily_context, empty_signals, first_true_per_day,
                                  local_clock)

NY = "America/New_York"
LDN = "Europe/London"
FLAT_BY_NY = 16 * 60 + 30   # all intraday hypotheses flat by 16:30 NY (before 17:00 rollover)


def _time_exit(sig: pd.DataFrame, close_min_ny: np.ndarray, day: np.ndarray, at_min: int) -> None:
    """exit=1 on the first bar of each day whose CLOSE is >= at_min (NY minutes)."""
    m = close_min_ny >= at_min
    sig.loc[first_true_per_day(m, day), "exit"] = 1


def _apply_entries(sig, trig_long, trig_short, ref, stop_l, stop_s, rr, day, tag):
    trig = trig_long | trig_short
    first = first_true_per_day(trig, day)
    side = np.where(first & trig_long, 1, np.where(first & trig_short, -1, 0))
    stop = np.where(side == 1, stop_l, np.where(side == -1, stop_s, np.nan))
    risk = np.abs(ref - stop)
    tgt = ref + side * rr * risk if rr else np.full(len(ref), np.nan)
    sig["entry"] = side
    sig["stop"] = np.where(side != 0, stop, np.nan)
    sig["target"] = np.where(side != 0, tgt, np.nan)
    sig.loc[side != 0, "tag"] = tag


class H1_NYOpeningRange(Strategy):
    """Breakout of the opening range after the COMEX open (08:20 NY)."""
    name = "H1_ny_orb"
    param_grid = {"range_min": [10, 30, 60], "stop_mode": ["opposite", "mid"], "rr": [1.0, 2.0, 0]}
    ordinal = ("range_min",)
    ANCHOR = 8 * 60 + 20
    LAST_ENTRY = 11 * 60 + 30

    def signals(self, bars):
        p = self.params
        mp = mid(bars)
        day = trading_day(bars.index)
        om, cm = local_clock(bars.index, NY)
        in_rng = (om >= self.ANCHOR) & (om < self.ANCHOR + p["range_min"])
        hi = mp["h"].where(in_rng).groupby(day).transform("max").to_numpy()
        lo = mp["l"].where(in_rng).groupby(day).transform("min").to_numpy()
        n_rng = pd.Series(in_rng).groupby(day).transform("sum").to_numpy()
        # range is complete (and therefore known) only for bars opening after the window
        ok = (om >= self.ANCHOR + p["range_min"]) & (om < self.LAST_ENTRY) & (n_rng >= p["range_min"] * 0.8)
        c = mp["c"].to_numpy()
        midr = (hi + lo) / 2
        sig = empty_signals(bars.index)
        stop_l = lo if p["stop_mode"] == "opposite" else midr
        stop_s = hi if p["stop_mode"] == "opposite" else midr
        _apply_entries(sig, ok & (c > hi), ok & (c < lo), c, stop_l, stop_s, p["rr"], day, self.name)
        _time_exit(sig, cm, day, FLAT_BY_NY)
        return sig


class H2_LondonAsianBreakout(Strategy):
    """Breakout of the Asian-session range (00:00-07:00 London) during 07:00-10:00 London."""
    name = "H2_ldn_asia_bo"
    param_grid = {"buffer": [0.0, 0.1], "stop_mode": ["opposite", "mid"], "rr": [1.0, 2.0, 0]}
    ordinal = ("buffer",)

    def signals(self, bars):
        p = self.params
        mp = mid(bars)
        day = trading_day(bars.index)
        oml, _ = local_clock(bars.index, LDN)
        _, cm = local_clock(bars.index, NY)
        in_rng = (oml >= 0) & (oml < 7 * 60)
        hi = mp["h"].where(in_rng).groupby(day).transform("max").to_numpy()
        lo = mp["l"].where(in_rng).groupby(day).transform("min").to_numpy()
        n_rng = pd.Series(in_rng).groupby(day).transform("sum").to_numpy()
        width = hi - lo
        ok = (oml >= 7 * 60) & (oml < 10 * 60) & (n_rng >= 300)
        c = mp["c"].to_numpy()
        up, dn = hi + p["buffer"] * width, lo - p["buffer"] * width
        midr = (hi + lo) / 2
        sig = empty_signals(bars.index)
        stop_l = lo if p["stop_mode"] == "opposite" else midr
        stop_s = hi if p["stop_mode"] == "opposite" else midr
        _apply_entries(sig, ok & (c > up), ok & (c < dn), c, stop_l, stop_s, p["rr"], day, self.name)
        _time_exit(sig, cm, day, FLAT_BY_NY)
        return sig


class H3_IntradayMomentum(Strategy):
    """Return from previous day's close to decision time predicts the rest of the NY session."""
    name = "H3_intraday_mom"
    param_grid = {"decision": [10 * 60, 12 * 60], "k": [0.0, 0.25, 0.5], "stop_atr": [0.5, 1.0]}
    ordinal = ("decision", "k", "stop_atr")

    def signals(self, bars):
        p = self.params
        mp = mid(bars)
        day = trading_day(bars.index)
        _, cm = local_clock(bars.index, NY)
        ctx = daily_context(bars)
        c = mp["c"].to_numpy()
        r = np.log(c / ctx["prev_close"].to_numpy())
        thr = p["k"] * ctx["vol"].to_numpy()
        at = cm == p["decision"]
        atr = ctx["atr"].to_numpy()
        valid = at & np.isfinite(thr) & np.isfinite(atr)
        sig = empty_signals(bars.index)
        _apply_entries(sig, valid & (r > thr) & (r > 0), valid & (r < -thr) & (r < 0), c,
                       c - p["stop_atr"] * atr, c + p["stop_atr"] * atr, 0, day, self.name)
        _time_exit(sig, cm, day, FLAT_BY_NY)
        return sig


class H4_AsiaMeanReversion(Strategy):
    """Fade short-term extremes during the quiet Asian session (19:00-02:00 NY)."""
    name = "H4_asia_mr"
    param_grid = {"lookback": [30, 60], "z": [2.0, 2.5, 3.0], "stop_sd": [2.0, 3.0]}
    ordinal = ("lookback", "z", "stop_sd")
    HOLD = 60

    def signals(self, bars):
        p = self.params
        mp = mid(bars)
        day = trading_day(bars.index)
        om, _ = local_clock(bars.index, NY)
        c = mp["c"]
        mu = c.rolling(p["lookback"], min_periods=p["lookback"]).mean()
        sd = c.rolling(p["lookback"], min_periods=p["lookback"]).std()
        z = ((c - mu) / sd).to_numpy()
        sdv = sd.to_numpy()
        win = (om >= 19 * 60) | (om < 2 * 60)
        cv = c.to_numpy()
        long_ = win & (z < -p["z"])
        short_ = win & (z > p["z"])
        side = np.where(long_, 1, np.where(short_, -1, 0))
        sig = empty_signals(bars.index)
        sig["entry"] = side
        sig["stop"] = np.where(side != 0, cv - side * p["stop_sd"] * sdv, np.nan)
        sig["target"] = np.where(side != 0, mu.to_numpy(), np.nan)  # revert to mean
        sig.loc[side != 0, "tag"] = self.name
        # time stop: exit when the session window ends or HOLD bars after a signal
        recent = pd.Series(side != 0).rolling(self.HOLD, min_periods=1).max().to_numpy() > 0
        ex = (~win) | (~recent)
        sig["exit"] = ex.astype(int)
        return sig


class H5_TimeOfDayDrift(Strategy):
    """Fixed-window intraday drift (session seasonality)."""
    name = "H5_tod_drift"
    param_grid = {"window": [(18, 3), (3, 8), (8, 12), (12, 16)], "side": [1, -1]}
    STOP_ATR = 1.0
    ENTRY_DELAY = 5

    @classmethod
    def neighbors(cls, params):
        """Window boundaries shifted by +-1h (same side); these configs are run for robustness only."""
        s, e = params["window"]
        out = []
        for ds, de in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            ns, ne = (s + ds) % 24, (e + de) % 24
            if ns != ne and not (ns == 17 or ne == 18):   # avoid the 17:00-18:00 NY break
                out.append({"window": (ns, ne), "side": params["side"]})
        return out

    def signals(self, bars):
        p = self.params
        mp = mid(bars)
        day = trading_day(bars.index)
        om, cm = local_clock(bars.index, NY)
        s_h, e_h = p["window"]
        ctx = daily_context(bars)
        atr = ctx["atr"].to_numpy()
        c = mp["c"].to_numpy()
        at = cm == s_h * 60 + self.ENTRY_DELAY   # session reopens 18:00 NY: wait 5 min for all windows
        valid = at & np.isfinite(atr)
        sig = empty_signals(bars.index)
        side = p["side"]
        _apply_entries(sig, valid & (side == 1), valid & (side == -1), c,
                       c - self.STOP_ATR * atr, c + self.STOP_ATR * atr, 0, day, self.name)
        # exit on first bar whose close reaches the window end
        ex = cm == e_h * 60
        sig.loc[ex, "exit"] = 1
        return sig


ALL = [H1_NYOpeningRange, H2_LondonAsianBreakout, H3_IntradayMomentum, H4_AsiaMeanReversion, H5_TimeOfDayDrift]
