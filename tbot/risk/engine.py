"""Risk engine — independent of signal logic.

The strategy proposes (side, stop, target). Only the risk engine decides the
volume, and it can veto any order. Strategies cannot override these limits.

Halt semantics (declared, see PROJECT_SPEC.md §Risk):
  * daily loss limit  -> mode `daily_halt_mode`: "block_new" (no new entries until
    next trading day) or "flatten" (block new AND close open positions with a
    market order at the next available price).
  * max drawdown      -> mode `dd_halt_mode`, and the halt is PERMANENT until a
    human resets it (state flag `dd_halted`).
  * kill switch       -> same as dd halt, triggered externally.
A stop-loss order is NOT a guaranteed price: gaps and slippage can make the
realised loss larger than the planned risk. Daily limits can therefore be
exceeded by the size of a gap; this is measured and reported, not hidden.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from tbot.instrument import InstrumentSpec


@dataclass
class RiskConfig:
    risk_per_trade_frac: float = 0.005     # of current equity, at stop distance + cost allowance
    max_open_positions: int = 1
    max_total_risk_frac: float = 0.01      # sum of open planned risk
    daily_loss_limit_frac: float = 0.02    # vs equity at start of trading day
    max_drawdown_frac: float = 0.10        # vs peak equity -> permanent halt
    daily_halt_mode: str = "flatten"       # block_new | flatten
    dd_halt_mode: str = "flatten"
    max_spread: float = float("inf")       # price units, checked at decision time
    max_trades_per_day: int = 10**6
    max_margin_usage: float = 0.5          # fraction of equity that can be used as margin
    cost_allowance: float = 0.0            # price units added to stop distance when sizing (slippage+spread)
    min_stop_distance: float = 0.0         # in addition to instrument stops_level
    fixed_volume: float | None = None      # if set, use this volume (still subject to all checks)

    def validate(self) -> None:
        assert 0 < self.risk_per_trade_frac <= 0.05, "risk per trade must be in (0, 5%]"
        assert self.daily_halt_mode in ("block_new", "flatten")
        assert self.dd_halt_mode in ("block_new", "flatten")
        assert 0 < self.max_margin_usage <= 1


@dataclass
class RiskState:
    day: object = None
    day_start_equity: float = 0.0
    peak_equity: float = 0.0
    trades_today: int = 0
    daily_halted: bool = False
    dd_halted: bool = False
    kill_switch: bool = False
    events: list = field(default_factory=list)


@dataclass
class SizeDecision:
    volume: float
    reason: str          # "ok" or rejection reason
    planned_risk: float  # account ccy at stop incl. cost allowance


class RiskEngine:
    def __init__(self, spec: InstrumentSpec, cfg: RiskConfig):
        cfg.validate()
        self.spec, self.cfg = spec, cfg
        self.state = RiskState()

    # ---- day / equity bookkeeping -------------------------------------------------
    def on_new_day(self, day, equity: float) -> None:
        s = self.state
        s.day, s.day_start_equity, s.trades_today, s.daily_halted = day, equity, 0, False
        s.peak_equity = max(s.peak_equity, equity)

    def on_equity(self, equity: float, ts=None, close_equity: float | None = None) -> str | None:
        """`equity` = conservative (intrabar worst) mark used for limit checks; the peak is
        tracked on `close_equity` (bar-close mark) so bar lows never understate it.
        Returns halt action when a halt flips on, else None."""
        s = self.state
        s.peak_equity = max(s.peak_equity, equity if close_equity is None else close_equity)
        action = None
        if not s.dd_halted and s.peak_equity > 0 and (s.peak_equity - equity) / s.peak_equity >= self.cfg.max_drawdown_frac:
            s.dd_halted = True
            s.events.append((ts, "dd_halt", equity))
            action = self.cfg.dd_halt_mode
        if not s.daily_halted and s.day_start_equity > 0 and \
                (s.day_start_equity - equity) / s.day_start_equity >= self.cfg.daily_loss_limit_frac:
            s.daily_halted = True
            s.events.append((ts, "daily_halt", equity))
            if action != "flatten":
                action = self.cfg.daily_halt_mode
        return action

    def trigger_kill_switch(self, ts=None) -> str:
        self.state.kill_switch = True
        self.state.events.append((ts, "kill_switch", None))
        return "flatten"

    @property
    def must_flatten(self) -> bool:
        """True while any active halt requires positions to be flat (re-checked every bar)."""
        s, c = self.state, self.cfg
        return s.kill_switch or (s.dd_halted and c.dd_halt_mode == "flatten") or \
            (s.daily_halted and c.daily_halt_mode == "flatten")

    @property
    def blocked(self) -> str | None:
        s = self.state
        if s.kill_switch:
            return "kill_switch"
        if s.dd_halted:
            return "dd_halted"
        if s.daily_halted:
            return "daily_halted"
        if s.trades_today >= self.cfg.max_trades_per_day:
            return "max_trades_per_day"
        return None

    # ---- order sizing / validation ------------------------------------------------
    def size_order(self, *, side: int, ref_price: float, stop: float, spread: float,
                   equity: float, open_positions: list, open_risk: float,
                   pending_entries: list = ()) -> SizeDecision:
        """pending_entries: submitted but unfilled entry orders — they count against position,
        risk and trades-per-day limits (review defect 6)."""
        cfg, spec = self.cfg, self.spec
        b = self.blocked
        if b:
            return SizeDecision(0.0, b, 0.0)
        if self.state.trades_today + len(pending_entries) >= cfg.max_trades_per_day:
            return SizeDecision(0.0, "max_trades_per_day", 0.0)
        open_risk = open_risk + sum(o.planned_risk for o in pending_entries)
        if len(open_positions) + len(pending_entries) >= cfg.max_open_positions:
            return SizeDecision(0.0, "max_open_positions", 0.0)
        if not (spread <= cfg.max_spread):
            return SizeDecision(0.0, "spread_too_wide", 0.0)
        if side not in (1, -1) or stop != stop:
            return SizeDecision(0.0, "invalid_signal", 0.0)
        dist = (ref_price - stop) * side
        if dist <= 0:
            return SizeDecision(0.0, "stop_wrong_side", 0.0)
        if dist < max(spec.stops_level, cfg.min_stop_distance):
            return SizeDecision(0.0, "stop_too_close", 0.0)
        per_lot_risk = (dist + cfg.cost_allowance) * spec.value_per_price_unit(1.0) \
            + 2 * spec.commission_per_lot_side
        budget = min(cfg.risk_per_trade_frac * equity, cfg.max_total_risk_frac * equity - open_risk)
        if budget <= 0:
            return SizeDecision(0.0, "total_risk_cap", 0.0)
        raw = cfg.fixed_volume if cfg.fixed_volume is not None else budget / per_lot_risk
        vol = spec.floor_volume(raw)
        if vol <= 0:
            return SizeDecision(0.0, "below_min_volume", 0.0)
        if vol * per_lot_risk > budget * (1 + 1e-9):
            return SizeDecision(0.0, "volume_exceeds_risk_budget", 0.0)
        used = sum(spec.margin(p.volume, p.entry) for p in open_positions)
        if used + spec.margin(vol, ref_price) > cfg.max_margin_usage * equity:
            return SizeDecision(0.0, "margin", 0.0)
        return SizeDecision(vol, "ok", vol * per_lot_risk)

    def on_fill(self) -> None:
        self.state.trades_today += 1
