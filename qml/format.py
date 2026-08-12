"""Human-readable rendering of a QML setup, kept free of Flask so it is testable."""

from qml.detector import ARMED, BULLISH, FORMING, INVALIDATED, TRIGGERED

_HEADLINE = {
    TRIGGERED: "price is at the QML",
    ARMED: "waiting for the retrace into the QML",
    FORMING: "CHoCH broken, right shoulder not confirmed yet",
    INVALIDATED: "setup invalidated",
}


def _price(value, digits):
    return "-" if value is None else "%.*f" % (digits, value)


def format_setup(setup, symbol="?", timeframe=None, digits=2):
    """Render a Setup as the Telegram message body."""
    side = "BUY" if setup.direction == BULLISH else "SELL"
    where = symbol if not timeframe else "%s %s" % (symbol, timeframe)

    lines = [
        "QML %s %s - %s" % (setup.direction, where, setup.status),
        _HEADLINE.get(setup.status, setup.status),
        "",
        "%s @ QML %s" % (side, _price(setup.entry, digits)),
        "SL %s" % _price(setup.sl, digits),
        "TP %s (external range liquidity)" % _price(setup.tp, digits),
    ]

    if setup.rr is None:
        lines.append("R:R n/a - stop sits on the entry")
    else:
        flag = "" if setup.meets_min_rr else "  <- below the R:R floor"
        lines.append("R:R %.2f%s" % (setup.rr, flag))

    lines += [
        "",
        "CHoCH %s" % _price(setup.choch, digits),
        "Head  %s" % _price(setup.head, digits),
    ]

    if setup.status == FORMING:
        lines.append("")
        lines.append("Target is provisional until the right shoulder confirms.")

    return "\n".join(lines)
