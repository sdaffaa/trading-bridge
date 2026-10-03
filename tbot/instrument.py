"""Instrument (contract) specification and volume arithmetic.

All values must come from the broker's own symbol specification. A spec loaded
with verified=False may be used for code tests and *relative* comparisons only,
never for sizing claims or profitability statements (see DECISIONS.md D-004).
"""
from __future__ import annotations

import json
import math
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass(frozen=True)
class InstrumentSpec:
    symbol: str
    contract_size: float          # units of base per 1.0 lot (e.g. 100 oz)
    tick_size: float              # minimum price increment
    volume_min: float
    volume_step: float
    volume_max: float
    leverage: float               # account leverage for this symbol (margin = notional / leverage)
    stops_level: float            # minimum SL/TP distance from current price, price units
    commission_per_lot_side: float  # account ccy per 1.0 lot per side
    swap_long: float              # account ccy per 1.0 lot per rollover (negative = cost)
    swap_short: float
    triple_swap_weekday: int      # 0=Mon .. 6=Sun; weekday of the rollover charged x3
    quote_to_account: float = 1.0  # conversion of quote ccy (USD) to account ccy, constant approx
    verified: bool = False
    source: str = "UNVERIFIED"

    def pnl(self, side: int, entry: float, exit_: float, volume: float) -> float:
        return side * (exit_ - entry) * volume * self.contract_size * self.quote_to_account

    def value_per_price_unit(self, volume: float) -> float:
        """Account-currency P&L per 1.0 price move for `volume` lots."""
        return volume * self.contract_size * self.quote_to_account

    def margin(self, volume: float, price: float) -> float:
        return volume * self.contract_size * price * self.quote_to_account / self.leverage

    def floor_volume(self, raw: float) -> float:
        """Round DOWN to volume_step. Returns 0.0 if below volume_min (never rounds up risk)."""
        if not math.isfinite(raw) or raw <= 0:
            return 0.0
        steps = math.floor(raw / self.volume_step + 1e-9)
        v = round(steps * self.volume_step, 8)
        if v < self.volume_min - 1e-12:
            return 0.0
        return min(v, self.volume_max)

    def to_dict(self) -> dict:
        return asdict(self)


def load_instrument(path: str | Path) -> InstrumentSpec:
    d = json.loads(Path(path).read_text())
    d = {k: v for k, v in d.items() if not k.startswith("_")}
    return InstrumentSpec(**d)
