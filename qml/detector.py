"""QML (Quasimodo Level) pattern engine.

Quasimodo is a head-and-shoulders variant in which the right shoulder returns to
the *left shoulder's* extreme. That extreme is the QML — the "Key Level" traders
wait for after a change of character (CHoCH).

Bullish, over a strictly alternating swing sequence L1 -> H1 -> L2 -> H2:

    L1  left-shoulder low          -> QML lives here
    H1  high after L1
    L2  head low, L2 < L1          -> the lower low
    H2  high after L2, H2 > H1     -> the break of H1 is the CHoCH

    Price then retraces down into L1. Entry at the QML, stop below the sweep of
    it, target H2 (the swing high before price hit the Key Level, i.e. external
    range liquidity / EQH).

Bearish is the exact mirror: H1 -> L1 -> H2 -> L2 with H2 > H1 and L2 < L1, QML
at H1, target L2.
"""

from dataclasses import dataclass, field

from qml.swings import HIGH, LOW, Swing, find_swings

BULLISH = "BULLISH"
BEARISH = "BEARISH"

Direction = str

# Lifecycle of a setup.
FORMING = "FORMING"          # CHoCH broken intrabar, right shoulder not confirmed yet
ARMED = "ARMED"              # confirmed, waiting for price to retrace into the QML
TRIGGERED = "TRIGGERED"      # price reached the QML
INVALIDATED = "INVALIDATED"  # head broken, or the retrace never arrived in time

Status = str


@dataclass(frozen=True)
class Config:
    swing_left: int = 3
    swing_right: int = 3
    max_bars_to_retrace: int = 100
    atr_period: int = 14
    atr_mult: float = 0.15
    sweep_lookahead: int = 3
    min_rr: float = 1.5


@dataclass
class Setup:
    direction: Direction
    status: Status
    qml: float
    choch: float
    head: float
    entry: float
    sl: float
    tp: float
    rr: float = None
    meets_min_rr: bool = False
    trigger_index: int = None
    confirmed_index: int = None
    swings: list = field(default_factory=list)

    def as_dict(self):
        return {
            "direction": self.direction,
            "status": self.status,
            "qml": self.qml,
            "choch": self.choch,
            "head": self.head,
            "entry": self.entry,
            "sl": self.sl,
            "tp": self.tp,
            "rr": self.rr,
            "meets_min_rr": self.meets_min_rr,
            "trigger_index": self.trigger_index,
            "confirmed_index": self.confirmed_index,
        }


def true_ranges(bars):
    ranges = []
    for i, bar in enumerate(bars):
        if i == 0:
            ranges.append(bar.high - bar.low)
            continue
        previous_close = bars[i - 1].close
        ranges.append(
            max(
                bar.high - bar.low,
                abs(bar.high - previous_close),
                abs(bar.low - previous_close),
            )
        )
    return ranges


def atr(bars, upto_index, period):
    """Mean true range over the `period` bars ending at `upto_index`."""
    if not bars:
        return 0.0
    end = min(upto_index, len(bars) - 1) + 1
    window = true_ranges(bars[:end])[-period:]
    if not window:
        return 0.0
    return sum(window) / len(window)


def _risk_reward(entry, sl, tp):
    risk = abs(entry - sl)
    if risk <= 0:
        return None
    return abs(tp - entry) / risk


def _resolve(bars, cfg, direction, qml, head_price, start_index):
    """Walk forward from the confirmed right-shoulder swing.

    Returns (status, trigger_index, sweep_extreme).
    """
    bullish = direction == BULLISH
    sweep = qml

    for i in range(start_index + 1, len(bars)):
        bar = bars[i]

        # A bar that closes through the head kills the setup, even if the same
        # bar dipped into the QML on its way there.
        broke_head = bar.close < head_price if bullish else bar.close > head_price
        if broke_head:
            return INVALIDATED, None, sweep

        reached = bar.low <= qml if bullish else bar.high >= qml
        if reached:
            end = min(i + cfg.sweep_lookahead, len(bars) - 1)
            extremes = [b.low for b in bars[i : end + 1]] if bullish else [
                b.high for b in bars[i : end + 1]
            ]
            sweep = min(extremes) if bullish else max(extremes)
            return TRIGGERED, i, sweep

        if i - start_index >= cfg.max_bars_to_retrace:
            return INVALIDATED, None, sweep

    return ARMED, None, sweep


def _build(bars, cfg, direction, s1, s2, s3, s4):
    """Assemble a confirmed setup from its four anchor swings."""
    bullish = direction == BULLISH
    qml = s1.price
    choch = s2.price
    head = s3.price
    tp = s4.price

    status, trigger_index, sweep = _resolve(bars, cfg, direction, qml, head, s4.index)

    buffer = cfg.atr_mult * atr(bars, s4.index, cfg.atr_period)
    entry = qml
    sl = (min(sweep, qml) - buffer) if bullish else (max(sweep, qml) + buffer)

    rr = _risk_reward(entry, sl, tp)
    return Setup(
        direction=direction,
        status=status,
        qml=qml,
        choch=choch,
        head=head,
        entry=entry,
        sl=sl,
        tp=tp,
        rr=rr,
        meets_min_rr=rr is not None and rr >= cfg.min_rr,
        trigger_index=trigger_index,
        confirmed_index=s4.index,
        swings=[s1, s2, s3, s4],
    )


def _forming(bars, cfg, swings):
    """Detect a CHoCH that has broken but whose right shoulder is unconfirmed.

    `find_swings` cannot confirm a pivot until `swing_right` bars have closed
    after it, so a live break of H1/L1 shows up here first — the "watch this
    level" state, before there is a tradeable retrace.
    """
    if len(swings) < 3:
        return None

    s1, s2, s3 = swings[-3:]
    if s1.kind == LOW and s2.kind == HIGH and s3.kind == LOW:
        direction, bullish = BULLISH, True
        if not s3.price < s1.price:
            return None
    elif s1.kind == HIGH and s2.kind == LOW and s3.kind == HIGH:
        direction, bullish = BEARISH, False
        if not s3.price > s1.price:
            return None
    else:
        return None

    tail = bars[s3.index + 1 :]
    if not tail:
        return None

    broke = (
        any(bar.close > s2.price for bar in tail)
        if bullish
        else any(bar.close < s2.price for bar in tail)
    )
    if not broke:
        return None

    # The extreme reached since the head stands in for the not-yet-confirmed
    # right shoulder, so the target is provisional.
    tp = max(bar.high for bar in tail) if bullish else min(bar.low for bar in tail)
    qml = s1.price
    buffer = cfg.atr_mult * atr(bars, len(bars) - 1, cfg.atr_period)
    sl = qml - buffer if bullish else qml + buffer
    rr = _risk_reward(qml, sl, tp)

    return Setup(
        direction=direction,
        status=FORMING,
        qml=qml,
        choch=s2.price,
        head=s3.price,
        entry=qml,
        sl=sl,
        tp=tp,
        rr=rr,
        meets_min_rr=rr is not None and rr >= cfg.min_rr,
        confirmed_index=None,
        swings=[s1, s2, s3],
    )


def find_setups(bars, cfg=None, include_forming=True):
    """Find every QML setup in `bars`, oldest first.

    Windows overlap, so a long series can yield several setups; callers that
    want the current one should use `latest_setup`.
    """
    cfg = cfg or Config()
    swings = find_swings(bars, cfg.swing_left, cfg.swing_right)

    setups = []
    for i in range(len(swings) - 3):
        s1, s2, s3, s4 = swings[i : i + 4]

        if s1.kind == LOW and s3.price < s1.price and s4.price > s2.price:
            setups.append(_build(bars, cfg, BULLISH, s1, s2, s3, s4))
        elif s1.kind == HIGH and s3.price > s1.price and s4.price < s2.price:
            setups.append(_build(bars, cfg, BEARISH, s1, s2, s3, s4))

    if include_forming:
        forming = _forming(bars, cfg, swings)
        if forming is not None:
            setups.append(forming)

    return setups


# Most actionable first. A confirmed setup sitting at its level beats one whose
# right shoulder has not printed yet, whatever order they were found in.
_PRIORITY = [TRIGGERED, ARMED, FORMING, INVALIDATED]


def latest_setup(bars, cfg=None, include_forming=True):
    """The most actionable setup in the series, breaking ties by recency."""
    setups = find_setups(bars, cfg, include_forming)
    if not setups:
        return None

    for status in _PRIORITY:
        matching = [s for s in setups if s.status == status]
        if matching:
            return matching[-1]
    return setups[-1]
