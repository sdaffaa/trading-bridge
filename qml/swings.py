"""Fractal swing detection.

The QML detector reads a strictly alternating high/low sequence, so this module
collapses runs of same-kind pivots down to the single most extreme one.
"""

from dataclasses import dataclass

HIGH = "HIGH"
LOW = "LOW"

SwingKind = str


@dataclass(frozen=True)
class Swing:
    index: int
    time: float
    price: float
    kind: SwingKind


def _is_pivot_high(bars, i, left, right):
    pivot = bars[i].high
    for j in range(i - left, i):
        if bars[j].high >= pivot:
            return False
    for j in range(i + 1, i + right + 1):
        if bars[j].high > pivot:
            return False
    return True


def _is_pivot_low(bars, i, left, right):
    pivot = bars[i].low
    for j in range(i - left, i):
        if bars[j].low <= pivot:
            return False
    for j in range(i + 1, i + right + 1):
        if bars[j].low < pivot:
            return False
    return True


def collapse(swings):
    """Reduce runs of consecutive same-kind swings to their extreme member."""
    collapsed = []
    for swing in swings:
        if collapsed and collapsed[-1].kind == swing.kind:
            previous = collapsed[-1]
            more_extreme = (
                swing.price > previous.price
                if swing.kind == HIGH
                else swing.price < previous.price
            )
            if more_extreme:
                collapsed[-1] = swing
            continue
        collapsed.append(swing)
    return collapsed


def find_swings(bars, left=3, right=3):
    """Return alternating pivot highs and lows, oldest first.

    A pivot needs `left` bars before and `right` bars after it, so the last
    `right` bars can never produce one — that lag is inherent to fractals.
    """
    if left < 1 or right < 1:
        raise ValueError("left and right must both be >= 1")

    swings = []
    for i in range(left, len(bars) - right):
        bar = bars[i]
        # A bar can qualify as both; keep both and let collapse() sort out the
        # ordering, since only one of them can survive alternation anyway.
        if _is_pivot_high(bars, i, left, right):
            swings.append(Swing(i, bar.time, bar.high, HIGH))
        if _is_pivot_low(bars, i, left, right):
            swings.append(Swing(i, bar.time, bar.low, LOW))

    return collapse(swings)
