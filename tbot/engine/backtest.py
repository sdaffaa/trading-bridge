"""Bar-by-bar engine. `TradingCore.step` is THE per-bar logic, shared by the
backtester (run_backtest) and the paper/live runner (tbot/live/runner.py), so the
research and execution versions cannot silently diverge.

Signals are precomputed for backtests but MUST be causal (row i uses only
bars[:i+1]); tests/test_leakage_metrics.py enforces this for every strategy.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from tbot.data.bars import BAR_COLS, trading_day
from tbot.engine.sim import ExecConfig, Order, SimBroker
from tbot.instrument import InstrumentSpec
from tbot.risk.engine import RiskConfig, RiskEngine


@dataclass
class BacktestResult:
    trades: pd.DataFrame
    equity: pd.Series            # bar-close liquidation equity
    daily: pd.DataFrame          # per trading day: equity_end, active, pnl, ret
    decisions: Counter
    risk_events: list
    n_ambiguous: int
    exposure_bars: int
    n_bars: int
    max_margin_used: float
    broker_log: list = field(default_factory=list)


class TradingCore:
    def __init__(self, spec: InstrumentSpec, risk_cfg: RiskConfig, exec_cfg: ExecConfig,
                 initial_balance: float, stopout_level: float = 0.5, broker=None,
                 bar_td: pd.Timedelta = pd.Timedelta(minutes=1)):
        self.spec = spec
        self.broker = broker or SimBroker(spec, exec_cfg, initial_balance)
        self.risk = RiskEngine(spec, risk_cfg)
        self.stopout_level = stopout_level
        self.decisions: Counter = Counter()
        self.active_days: set = set()
        self.day_end: dict = {}
        self.exposure = 0
        self.max_margin = 0.0
        self.last_eq = initial_balance
        self.day = None
        self.prev_bar = None
        self.n = 0
        self.bar_td = bar_td   # decisions are made at bar CLOSE = open + bar_td

    def _cancel_entries(self, t, reason):
        b = self.broker
        keep = [o for o in b.pending if o.kind != "entry"]
        for o in b.pending:
            if o.kind == "entry":
                b.log.append({"t": t, "ev": "cancelled", "cid": o.cid, "reason": reason})
                self.decisions["entry_cancelled_" + reason] += 1
        b.pending = keep

    def _flatten(self, t, reason):
        """Idempotent: submits a close for every open position without a pending close.
        Called on every bar while the condition holds, so rejected/expired closes are retried."""
        b = self.broker
        for p in b.positions:
            if not any(o.kind == "close" and o.pid == p.pid for o in b.pending):
                b.submit(Order(f"close-{p.pid}-{reason}-{t.value}", "close", -p.side, p.volume, t,
                               pid=p.pid, reason=reason))

    def new_day_if_needed(self, t, day):
        if self.day is None:
            self.day = day
            self.risk.on_new_day(day, self.last_eq)
            return
        if day != self.day:
            b = self.broker
            if b.positions:
                b.rollover(pd.Timestamp(self.day).weekday(), t)
                self.last_eq = b.equity(self.prev_bar[3], self.prev_bar[7])
                self.active_days.add(day)
            self.day_end[self.day] = self.last_eq
            self.day = day
            self.risk.on_new_day(day, self.last_eq)

    def idle(self, entry: int) -> bool:
        b = self.broker
        return not b.positions and not b.pending and entry == 0

    def step(self, t, bar, day, entry=0, stop=np.nan, target=np.nan, exit_=0, tag="",
             kill_switch=False) -> float:
        """Process one CLOSED bar: fills at its open/inside it, risk checks at its close,
        then the decision for this bar's close. Returns bar-close equity."""
        self.n += 1
        self.new_day_if_needed(t, day)
        b, risk = self.broker, self.risk
        tc = t + self.bar_td
        if kill_switch and not risk.state.kill_switch:
            risk.trigger_kill_switch(t)
        if risk.must_flatten or risk.state.daily_halted or risk.state.dd_halted:
            self._cancel_entries(t, "halt")   # also in block_new mode (review N2)
        if self.idle(entry):
            self.prev_bar = bar
            self.last_eq = b.balance
            return self.last_eq
        events = b.process_bar(t, bar)
        for ev in events:
            if ev["ev"] == "filled":
                risk.on_fill()
                self.decisions["filled"] += 1
            elif ev["ev"] == "rejected":
                self.decisions["broker_rejected"] += 1
        if b.positions or events:
            self.active_days.add(day)
        if b.positions:
            self.exposure += 1
            self.max_margin = max(self.max_margin, b.used_margin())
            e_close = b.equity(bar[3], bar[7])
            risk.on_equity(b.worst_equity(bar), t, close_equity=e_close)
            if risk.must_flatten or risk.state.daily_halted or risk.state.dd_halted:
                self._cancel_entries(t, "halt")
            if risk.must_flatten:
                self._flatten(tc, "kill_switch" if risk.state.kill_switch else "risk_halt")
            if e_close < self.stopout_level * b.used_margin():
                self.decisions["margin_stopout"] += 1
                self._flatten(tc, "stopout")
        else:
            e_close = b.balance
            risk.on_equity(e_close, t, close_equity=e_close)
        self.last_eq = e_close
        self.prev_bar = bar
        if exit_ and b.positions:
            self._flatten(tc, "signal_exit")
        if entry != 0:
            ref = bar[7] if entry == 1 else bar[3]
            open_risk = sum(p.planned_risk for p in b.positions)
            pend = [o for o in b.pending if o.kind == "entry"]
            dec = risk.size_order(side=entry, ref_price=ref, stop=stop, spread=bar[7] - bar[3],
                                  equity=e_close, open_positions=b.positions, open_risk=open_risk,
                                  pending_entries=pend)
            self.decisions[dec.reason] += 1
            if dec.reason == "ok":
                b.submit(Order(f"e-{t.value}-{entry}", "entry", entry, dec.volume, tc, stop, target,
                               str(tag), planned_risk=dec.planned_risk))
        return e_close

    def finish(self, t, bar):
        b = self.broker
        for p in list(b.positions):
            price = bar[3] if p.side == 1 else bar[7]
            b._close(p, price, t, "end_of_data", 0.0, bar[7] - bar[3])
        if b.positions == []:
            self.last_eq = b.balance
        self.day_end[self.day] = self.last_eq
        return self.last_eq

    def daily_frame(self, initial_balance) -> pd.DataFrame:
        d = pd.DataFrame({"equity_end": pd.Series(self.day_end)})
        d["active"] = [x in self.active_days for x in d.index]
        prev = d["equity_end"].shift(1).fillna(initial_balance)
        d["pnl"] = d["equity_end"] - prev
        d["ret"] = d["pnl"] / prev
        d.index = pd.to_datetime(d.index)
        return d


def run_backtest(bars: pd.DataFrame, signals: pd.DataFrame, spec: InstrumentSpec,
                 risk_cfg: RiskConfig, exec_cfg: ExecConfig, initial_balance: float,
                 entry_mask: np.ndarray | None = None, stopout_level: float = 0.5,
                 keep_log: bool = False) -> BacktestResult:
    assert bars.index.equals(signals.index), "signals must be aligned to bars"
    idx = bars.index
    n = len(idx)
    P = bars[BAR_COLS].to_numpy(dtype=float)
    entry = signals["entry"].fillna(0).to_numpy(dtype=int)
    stop = signals["stop"].to_numpy(dtype=float)
    target = signals["target"].to_numpy(dtype=float) if "target" in signals else np.full(n, np.nan)
    exit_ = signals["exit"].fillna(0).to_numpy(dtype=int) if "exit" in signals else np.zeros(n, int)
    tags = signals["tag"].to_numpy() if "tag" in signals else np.full(n, "")
    if entry_mask is not None:
        entry = np.where(entry_mask, entry, 0)
    days = trading_day(idx)
    core = TradingCore(spec, risk_cfg, exec_cfg, initial_balance, stopout_level)
    eq = np.empty(n)
    for i in range(n):
        eq[i] = core.step(idx[i], P[i], days[i], entry[i], stop[i], target[i], exit_[i], tags[i])
    eq[-1] = core.finish(idx[-1], P[-1])
    b = core.broker
    trades = pd.DataFrame([t.__dict__ for t in b.trades])
    if len(trades):
        trades["entry_day"] = pd.to_datetime(trading_day(pd.DatetimeIndex(trades["entry_time"])))
    return BacktestResult(trades, pd.Series(eq, index=idx),
                          core.daily_frame(initial_balance), core.decisions, core.risk.state.events,
                          b.n_ambiguous, core.exposure, n, core.max_margin, b.log if keep_log else [])
