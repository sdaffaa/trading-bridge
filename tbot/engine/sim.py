"""Simulated exchange/broker shared by the backtester AND the paper-trading runner.

Execution model (all declared, all configurable for stress tests):
  * Decision at bar i close -> market order executes at the OPEN of bar i+1+latency_bars.
    Buys fill at ASK, sells at BID, plus adverse slippage (fixed + uniform random).
  * Orders older than `max_exec_delay` when their execution bar arrives are cancelled
    (stale market, e.g. weekend gap) — logged as `expired`.
  * Random rejection with probability `reject_prob` (seeded RNG).
  * Partial fill: if `max_fill_volume` is set, the fill is capped and the rest cancelled.
  * Stop-loss = stop-market order: triggers when the relevant side touches the level,
    fills at the level minus slippage, or at the bar open if the bar gaps through it.
    A stop is NOT a guaranteed price.
  * Take-profit = limit order: triggers only if price trades through the level by
    `limit_penetration`; fills at the limit price (no positive slippage assumed).
  * Long positions are evaluated on BID, shorts on ASK.
  * If SL and TP are both touched inside one bar and the bar data cannot tell which
    came first, `intrabar` policy decides: "worst" (default, SL first) or "best"
    (used only as a sensitivity bound). Never silently optimistic.
  * Swap charged at each trading-day rollover per lot (triple on configured weekday).
  * Commission per lot per side charged at each fill.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from tbot.instrument import InstrumentSpec


@dataclass
class ExecConfig:
    latency_bars: int = 0
    slippage_fixed: float = 0.0
    slippage_random: float = 0.0
    reject_prob: float = 0.0
    max_fill_volume: float | None = None
    intrabar: str = "worst"
    limit_penetration: float = 0.0
    max_exec_delay: pd.Timedelta = pd.Timedelta(minutes=5)
    seed: int = 0


@dataclass
class Order:
    cid: str
    kind: str            # "entry" | "close"
    side: int            # +1 buy / -1 sell (for close: side of the closing trade)
    volume: float
    created: pd.Timestamp
    stop: float = np.nan
    target: float = np.nan
    tag: str = ""
    pid: int | None = None     # position to close
    planned_risk: float = 0.0
    reason: str = ""
    delay_left: int = 0


@dataclass
class Position:
    pid: int
    side: int
    volume: float
    entry: float
    entry_time: pd.Timestamp
    stop: float
    target: float
    tag: str
    planned_risk: float
    commission: float = 0.0
    swap: float = 0.0
    slippage_cost: float = 0.0
    spread_cost: float = 0.0
    mae: float = 0.0     # worst adverse excursion, price units (conservative bar extremes)
    mfe: float = 0.0


@dataclass
class Trade:
    pid: int
    tag: str
    side: int
    volume: float
    entry_time: pd.Timestamp
    entry: float
    exit_time: pd.Timestamp
    exit: float
    exit_reason: str
    gross: float
    commission: float
    swap: float
    net: float
    planned_risk: float
    slippage_cost: float
    spread_cost: float
    mae: float
    mfe: float
    ambiguous: bool


class SimBroker:
    def __init__(self, spec: InstrumentSpec, cfg: ExecConfig, balance: float):
        self.spec, self.cfg = spec, cfg
        self.balance = balance
        self.positions: list[Position] = []
        self.pending: list[Order] = []
        self.trades: list[Trade] = []
        self.log: list[dict] = []
        self.seen_cids: set[str] = set()
        self.rng = np.random.default_rng(cfg.seed)
        self._pid = 0
        self.n_ambiguous = 0

    # ---------------------------------------------------------------- orders
    def submit(self, order: Order) -> bool:
        if order.cid in self.seen_cids:
            self.log.append({"t": order.created, "ev": "duplicate_rejected", "cid": order.cid})
            return False
        self.seen_cids.add(order.cid)
        order.delay_left = self.cfg.latency_bars
        self.pending.append(order)
        self.log.append({"t": order.created, "ev": "submitted", "cid": order.cid, "kind": order.kind,
                         "side": order.side, "vol": order.volume, "reason": order.reason})
        return True

    def _slip(self) -> float:
        c = self.cfg
        return c.slippage_fixed + (self.rng.uniform(0, c.slippage_random) if c.slippage_random > 0 else 0.0)

    def _close(self, p: Position, price: float, t, reason: str, slip: float, spread: float, ambiguous=False):
        comm = self.spec.commission_per_lot_side * p.volume
        p.commission += comm
        p.slippage_cost += slip * self.spec.value_per_price_unit(p.volume)
        p.spread_cost += spread / 2 * self.spec.value_per_price_unit(p.volume)
        gross = self.spec.pnl(p.side, p.entry, price, p.volume)
        net = gross - p.commission + p.swap
        self.balance += gross - comm   # entry commission & swaps already booked to balance
        self.trades.append(Trade(p.pid, p.tag, p.side, p.volume, p.entry_time, p.entry, t, price, reason,
                                 gross, p.commission, p.swap, net, p.planned_risk, p.slippage_cost,
                                 p.spread_cost, p.mae, p.mfe, ambiguous))
        self.positions.remove(p)
        self.log.append({"t": t, "ev": "exit", "pid": p.pid, "price": price, "reason": reason, "net": net})

    # ---------------------------------------------------------------- per bar
    def process_bar(self, t: pd.Timestamp, bar) -> list[dict]:
        """bar: tuple(bid_o,bid_h,bid_l,bid_c,ask_o,ask_h,ask_l,ask_c). Returns fill events."""
        bo, bh, bl, bc, ao, ah, al, ac = bar
        events = []
        # 1) pending market orders at the open
        still = []
        for o in self.pending:
            if o.delay_left > 0:
                o.delay_left -= 1
                still.append(o)
                continue
            if t - o.created > self.cfg.max_exec_delay:
                self.log.append({"t": t, "ev": "expired", "cid": o.cid})
                continue
            if self.cfg.reject_prob > 0 and self.rng.random() < self.cfg.reject_prob:
                self.log.append({"t": t, "ev": "rejected", "cid": o.cid})
                events.append({"ev": "rejected", "order": o})
                continue
            slip = self._slip()
            spread = ao - bo
            if o.kind == "close":
                p = next((q for q in self.positions if q.pid == o.pid), None)
                if p is None:
                    continue
                price = (bo - slip) if p.side == 1 else (ao + slip)
                self._close(p, price, t, o.reason or "close", slip, spread)
                events.append({"ev": "closed", "order": o})
                continue
            vol = o.volume
            if self.cfg.max_fill_volume is not None and vol > self.cfg.max_fill_volume:
                vol = self.spec.floor_volume(self.cfg.max_fill_volume)
                self.log.append({"t": t, "ev": "partial", "cid": o.cid, "filled": vol, "requested": o.volume})
                if vol <= 0:
                    continue
            price = (ao + slip) if o.side == 1 else (bo - slip)
            self._pid += 1
            p = Position(self._pid, o.side, vol, price, t, o.stop, o.target, o.tag,
                         o.planned_risk * vol / o.volume)
            comm = self.spec.commission_per_lot_side * vol
            p.commission += comm
            p.slippage_cost += slip * self.spec.value_per_price_unit(vol)
            p.spread_cost += spread / 2 * self.spec.value_per_price_unit(vol)
            self.balance -= comm
            self.positions.append(p)
            self.log.append({"t": t, "ev": "fill", "cid": o.cid, "pid": p.pid, "side": o.side,
                             "vol": vol, "price": price})
            events.append({"ev": "filled", "order": o, "pos": p})
        self.pending = still
        # 2) protective orders within the bar
        for p in list(self.positions):
            if p.side == 1:
                o_, h_, l_ = bo, bh, bl
                sl_hit = p.stop == p.stop and l_ <= p.stop
                tp_hit = p.target == p.target and h_ >= p.target + self.cfg.limit_penetration
                p.mae = max(p.mae, p.entry - l_)
                p.mfe = max(p.mfe, h_ - p.entry)
            else:
                o_, h_, l_ = ao, ah, al
                sl_hit = p.stop == p.stop and h_ >= p.stop
                tp_hit = p.target == p.target and l_ <= p.target - self.cfg.limit_penetration
                p.mae = max(p.mae, h_ - p.entry)
                p.mfe = max(p.mfe, p.entry - l_)
            if not (sl_hit or tp_hit):
                continue
            spread = ao - bo
            gap_sl = sl_hit and ((p.side == 1 and o_ <= p.stop) or (p.side == -1 and o_ >= p.stop))
            gap_tp = tp_hit and ((p.side == 1 and o_ >= p.target) or (p.side == -1 and o_ <= p.target))
            ambiguous = sl_hit and tp_hit and not gap_sl and not gap_tp
            if ambiguous:
                self.n_ambiguous += 1
                use_sl = self.cfg.intrabar != "best"
            else:
                use_sl = gap_sl or (sl_hit and not gap_tp)
            if use_sl:
                slip = self._slip()
                level = o_ if gap_sl else p.stop
                price = level - slip if p.side == 1 else level + slip
                self._close(p, price, t, "stop", slip, spread, ambiguous)
            else:
                self._close(p, p.target, t, "target", 0.0, spread, ambiguous)
            events.append({"ev": "exit"})
        return events

    def rollover(self, weekday: int, t) -> None:
        mult = 3 if weekday == self.spec.triple_swap_weekday else 1
        for p in self.positions:
            rate = self.spec.swap_long if p.side == 1 else self.spec.swap_short
            amt = rate * p.volume * mult
            p.swap += amt
            self.balance += amt
        if self.positions:
            self.log.append({"t": t, "ev": "swap", "mult": mult})

    def equity(self, bid: float, ask: float) -> float:
        """Liquidation equity: longs at bid, shorts at ask (no exit commission)."""
        e = self.balance
        for p in self.positions:
            e += self.spec.pnl(p.side, p.entry, bid if p.side == 1 else ask, p.volume)
        return e

    def worst_equity(self, bar) -> float:
        """Most adverse mark within the bar (conservative, for loss-limit checks)."""
        bo, bh, bl, bc, ao, ah, al, ac = bar
        e = self.balance
        for p in self.positions:
            e += self.spec.pnl(p.side, p.entry, bl if p.side == 1 else ah, p.volume)
        return e

    def used_margin(self) -> float:
        return sum(self.spec.margin(p.volume, p.entry) for p in self.positions)
