"""Paper/live runner. Uses the SAME TradingCore.step as the backtester.

Safety rules (PROJECT_SPEC.md §Execution):
  * Mode "paper" uses SimBroker on incoming closed bars. Mode "live" requires a real
    BrokerAdapter AND explicit written approval recorded in configs (live_approved=true)
    AND env TBOT_LIVE_APPROVED=1. No live adapter is implemented yet.
  * Kill switch: file <state_dir>/KILL -> block new orders and flatten (permanent until reset).
  * Stale data: a bar older than `max_bar_age` at processing time is NOT traded on
    (decision suppressed, fills still processed) and logged.
  * Duplicate orders: client order ids are deterministic (bar time + side) and the
    broker rejects any id already seen, including across restarts (persisted).
  * Restart: full state is pickled after every bar; `LiveRunner.resume()` restores it.
  * Reconciliation: `reconcile(external_positions)` compares with the broker; any
    mismatch triggers the kill switch and is logged as an error.
"""
from __future__ import annotations

import json
import os
import pickle
from collections import deque
from pathlib import Path

import numpy as np
import pandas as pd

from tbot.data.bars import BAR_COLS, trading_day
from tbot.engine.backtest import TradingCore
from tbot.engine.sim import ExecConfig
from tbot.instrument import InstrumentSpec
from tbot.risk.engine import RiskConfig


class LiveTradingNotApproved(RuntimeError):
    pass


class LiveRunner:
    def __init__(self, strategy, spec: InstrumentSpec, risk_cfg: RiskConfig, exec_cfg: ExecConfig,
                 initial_balance: float, state_dir: str | Path, buffer_bars: int,
                 mode: str = "paper", max_bar_age: pd.Timedelta = pd.Timedelta(minutes=3),
                 live_approved: bool = False):
        if mode == "live":
            if not (live_approved and os.environ.get("TBOT_LIVE_APPROVED") == "1"):
                raise LiveTradingNotApproved("Live trading requires explicit owner approval (see PROJECT_SPEC.md).")
            raise NotImplementedError("No live broker adapter implemented yet.")
        self.strategy = strategy
        self.core = TradingCore(spec, risk_cfg, exec_cfg, initial_balance)
        self.state_dir = Path(state_dir)
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.buffer = deque(maxlen=buffer_bars)
        self.max_bar_age = max_bar_age
        self.last_t = None
        self.log_path = self.state_dir / "events.jsonl"

    # ------------------------------------------------------------ persistence
    def save(self):
        tmp = self.state_dir / "state.pkl.tmp"
        with open(tmp, "wb") as f:
            pickle.dump({"core": self.core, "buffer": self.buffer, "last_t": self.last_t}, f)
        tmp.replace(self.state_dir / "state.pkl")

    @classmethod
    def resume(cls, strategy, state_dir, **kw) -> "LiveRunner":
        r = cls.__new__(cls)
        r.strategy = strategy
        r.state_dir = Path(state_dir)
        st = pickle.loads((r.state_dir / "state.pkl").read_bytes())
        r.core, r.buffer, r.last_t = st["core"], st["buffer"], st["last_t"]
        r.max_bar_age = kw.get("max_bar_age", pd.Timedelta(minutes=3))
        r.log_path = r.state_dir / "events.jsonl"
        r._log({"ev": "resumed", "last_t": str(r.last_t)})
        return r

    def _log(self, rec: dict):
        with open(self.log_path, "a") as f:
            f.write(json.dumps(rec, default=str) + "\n")

    # ------------------------------------------------------------ main loop
    def on_bar(self, t: pd.Timestamp, bar: dict | pd.Series, now: pd.Timestamp | None = None) -> None:
        if self.last_t is not None and t <= self.last_t:
            self._log({"ev": "duplicate_or_old_bar_ignored", "t": t})
            return
        row = [float(bar[c]) for c in BAR_COLS]
        self.buffer.append((t, row))
        idx = pd.DatetimeIndex([x[0] for x in self.buffer])
        df = pd.DataFrame([x[1] for x in self.buffer], index=idx, columns=BAR_COLS)
        sig = self.strategy.signals(df).iloc[-1]
        entry, stop, target, exit_ = int(sig["entry"]), float(sig["stop"]), float(sig["target"]), int(sig["exit"])
        now = now if now is not None else t + pd.Timedelta(minutes=1)
        if now - (t + pd.Timedelta(minutes=1)) > self.max_bar_age:
            if entry:
                self._log({"ev": "stale_bar_signal_suppressed", "t": t, "entry": entry})
            entry = 0
        kill = (self.state_dir / "KILL").exists()
        n_trades = len(self.core.broker.trades)
        n_log = len(self.core.broker.log)
        eq = self.core.step(t, np.array(row), trading_day(pd.DatetimeIndex([t]))[0], entry, stop, target,
                            exit_, sig.get("tag", ""), kill_switch=kill)
        for rec in self.core.broker.log[n_log:]:
            self._log(rec)
        if entry:
            self._log({"ev": "signal", "t": t, "entry": entry, "stop": stop, "target": target,
                       "decision": dict(self.core.decisions)})
        if len(self.core.broker.trades) > n_trades:
            self._log({"ev": "trade_closed", "trade": self.core.broker.trades[-1].__dict__})
        self.last_t = t
        self.save()
        return eq

    def reconcile(self, external_positions: list[dict]) -> bool:
        """external_positions: [{'side':1,'volume':0.1}, ...] as reported by the broker."""
        mine = sorted((p.side, round(p.volume, 8)) for p in self.core.broker.positions)
        theirs = sorted((int(p["side"]), round(float(p["volume"]), 8)) for p in external_positions)
        if mine != theirs:
            self._log({"ev": "RECONCILE_MISMATCH", "internal": mine, "broker": theirs})
            self.core.risk.trigger_kill_switch(self.last_t)
            return False
        return True
