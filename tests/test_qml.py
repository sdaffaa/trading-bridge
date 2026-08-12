import pytest

from qml.bars import BadPayload, Bar, parse_bars
from qml.detector import (
    ARMED,
    BEARISH,
    BULLISH,
    Config,
    FORMING,
    INVALIDATED,
    TRIGGERED,
    find_setups,
    latest_setup,
)
from qml.swings import HIGH, LOW, Swing, collapse, find_swings

EPS = 0.1


def build(start, legs):
    """Bars tracing a path through `legs` of (target_price, bar_count).

    Each bar is a doji at its point on the path, so pivots land exactly on the
    turning points and closes are trivially predictable.
    """
    prices = [start]
    for target, count in legs:
        origin = prices[-1]
        for step in range(1, count + 1):
            prices.append(origin + (target - origin) * step / count)
    return [
        Bar(time=float(i), open=p, high=p + EPS, low=p - EPS, close=p)
        for i, p in enumerate(prices)
    ]


# L1 100 -> H1 106 -> L2 95 (lower low) -> H2 112 (CHoCH over H1) -> back to 99
BULLISH_LEGS = [(100, 6), (106, 6), (95, 6), (112, 6), (99, 6), (104, 6)]

# H1 100 -> L1 94 -> H2 105 (higher high) -> L2 93 (CHoCH under L1) -> back to 101
BEARISH_LEGS = [(100, 6), (94, 6), (105, 6), (93, 6), (101, 6), (96, 6)]


def test_bullish_qml_triggers_at_the_left_shoulder_low():
    bars = build(110, BULLISH_LEGS)
    setups = find_setups(bars)

    assert len(setups) == 1
    setup = setups[0]
    assert setup.direction == BULLISH
    assert setup.status == TRIGGERED

    # QML is the left shoulder low, target the swing high that made the CHoCH.
    assert setup.qml == pytest.approx(100 - EPS)
    assert setup.choch == pytest.approx(106 + EPS)
    assert setup.head == pytest.approx(95 - EPS)
    assert setup.tp == pytest.approx(112 + EPS)
    assert setup.entry == setup.qml

    assert setup.sl < setup.qml, "stop must sit under the level being defended"
    assert setup.sl < 99, "stop must clear the sweep of the QML"
    assert setup.rr > 1
    assert setup.meets_min_rr


def test_bearish_qml_is_the_mirror():
    bars = build(90, BEARISH_LEGS)
    setups = find_setups(bars)

    assert len(setups) == 1
    setup = setups[0]
    assert setup.direction == BEARISH
    assert setup.status == TRIGGERED

    assert setup.qml == pytest.approx(100 + EPS)
    assert setup.choch == pytest.approx(94 - EPS)
    assert setup.head == pytest.approx(105 + EPS)
    assert setup.tp == pytest.approx(93 - EPS)

    assert setup.sl > setup.qml
    assert setup.sl > 101
    assert setup.meets_min_rr


def test_lower_low_without_a_choch_is_not_a_setup():
    # Same shape, but the rally off the head stops short of H1 — no change of
    # character, so there is nothing to trade.
    bars = build(110, [(100, 6), (106, 6), (95, 6), (104, 6), (99, 6), (102, 6)])
    assert find_setups(bars) == []


def test_setup_expires_when_the_retrace_never_arrives():
    bars = build(110, [(100, 6), (106, 6), (95, 6), (112, 6), (110, 6), (120, 6), (120, 6)])
    setups = find_setups(bars, Config(max_bars_to_retrace=5))

    assert len(setups) == 1
    assert setups[0].direction == BULLISH
    assert setups[0].status == INVALIDATED


def test_setup_survives_while_the_retrace_window_is_still_open():
    bars = build(110, [(100, 6), (106, 6), (95, 6), (112, 6), (110, 6), (120, 6), (120, 6)])
    setups = find_setups(bars, Config(max_bars_to_retrace=100))

    assert len(setups) == 1
    assert setups[0].status == ARMED


def test_closing_through_the_head_invalidates_before_any_entry():
    # A single bar collapses from 105 straight through the QML at 100 and closes
    # below the head at 95 — the level was never defended, so no entry.
    bars = build(110, [(100, 6), (106, 6), (95, 6), (112, 6), (105, 4), (94, 1), (94, 6)])

    # The same path also prints a valid bearish quasimodo (head 112, CHoCH under
    # the 95 low, QML back at 106), so pick out the bullish one under test.
    bullish = [s for s in find_setups(bars) if s.direction == BULLISH]

    assert len(bullish) == 1
    assert bullish[0].status == INVALIDATED
    assert bullish[0].trigger_index is None


def test_choch_break_before_the_right_shoulder_confirms_is_forming():
    # The rally off the head closes above H1 on the final bar, so the pivot that
    # would become H2 cannot be confirmed yet — the level is worth watching but
    # there is no confirmed target.
    bars = build(110, [(100, 6), (106, 6), (95, 6), (108, 6)])
    setups = find_setups(bars)

    assert len(setups) == 1
    setup = setups[0]
    assert setup.direction == BULLISH
    assert setup.status == FORMING
    assert setup.qml == pytest.approx(100 - EPS)
    assert setup.choch == pytest.approx(106 + EPS)
    assert setup.confirmed_index is None


def test_forming_setups_can_be_suppressed():
    bars = build(110, [(100, 6), (106, 6), (95, 6), (108, 6)])
    assert find_setups(bars, include_forming=False) == []


def test_latest_setup_prefers_the_triggered_one_over_older_noise():
    bars = build(110, BULLISH_LEGS)
    setup = latest_setup(bars)

    assert setup is not None
    assert setup.status == TRIGGERED
    assert setup.as_dict()["direction"] == BULLISH


def test_no_setup_in_a_flat_series():
    bars = build(100, [(100, 40)])
    assert find_setups(bars) == []
    assert latest_setup(bars) is None


def test_swings_alternate_and_collapse_to_the_extreme():
    bars = build(110, BULLISH_LEGS)
    swings = find_swings(bars)

    kinds = [s.kind for s in swings]
    assert kinds == [LOW, HIGH, LOW, HIGH, LOW]
    assert all(a != b for a, b in zip(kinds, kinds[1:]))


def test_collapse_keeps_only_the_most_extreme_of_a_run():
    run = [
        Swing(0, 0.0, 105.0, HIGH),
        Swing(1, 1.0, 108.0, HIGH),
        Swing(2, 2.0, 106.0, HIGH),
        Swing(3, 3.0, 95.0, LOW),
        Swing(4, 4.0, 93.0, LOW),
    ]
    collapsed = collapse(run)

    assert [s.price for s in collapsed] == [108.0, 93.0]


def test_parse_bars_accepts_both_key_styles():
    long_form = parse_bars(
        {"bars": [{"time": 1, "open": 2, "high": 3, "low": 1, "close": 2.5}]}
    )
    short_form = parse_bars([{"t": 1, "o": 2, "h": 3, "l": 1, "c": 2.5}])

    assert long_form == short_form
    assert long_form[0].high == 3


def test_parse_bars_sorts_by_time():
    bars = parse_bars(
        [
            {"t": 2, "o": 1, "h": 1, "l": 1, "c": 1},
            {"t": 1, "o": 1, "h": 1, "l": 1, "c": 1},
        ]
    )
    assert [b.time for b in bars] == [1, 2]


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"bars": []},
        {"bars": "nope"},
        [{"o": 1, "h": 2, "l": 0}],
        [{"t": 1, "o": 1, "h": 0, "l": 2, "c": 1}],
        [{"t": 1, "o": 9, "h": 2, "l": 1, "c": 1}],
        [{"t": 1, "o": "x", "h": 2, "l": 1, "c": 1}],
        ["not a bar"],
    ],
)
def test_parse_bars_rejects_garbage(payload):
    with pytest.raises(BadPayload):
        parse_bars(payload)
