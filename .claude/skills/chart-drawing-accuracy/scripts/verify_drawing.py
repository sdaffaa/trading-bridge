#!/usr/bin/env python3
"""
verify_drawing.py — check that every line and box on a chart ends where price
broke it, and report the bar index it should have ended at.

Usage:
    python3 verify_drawing.py spec.json                 # report
    python3 verify_drawing.py spec.json --fix out.json  # report + write corrected spec
    python3 verify_drawing.py spec.json --fix out.json --snap   # also snap bad anchors
    python3 verify_drawing.py spec.json --json          # machine-readable report
    python3 verify_drawing.py --selftest                # verify the install

Spec format:
{
  "candles": [{"o":1,"h":2,"l":0.5,"c":1.5}, ...],       # index 0 = oldest
  "drawings": [
    {"id":"BSL",  "kind":"level", "price":100, "from":4,  "to":null},
    {"id":"TP",   "kind":"target","price":62,  "from":30},
    {"id":"OB",   "kind":"zone",  "top":87, "bottom":83.5, "from":41, "to":62},
    {"id":"path", "kind":"projection", "from":62, "to":68}
  ]
}

Per-drawing options:
  mode   "touch" (default) | "close" | "fill"   — what counts as breaking it
  side   "above" | "below" | "auto" (default)   — levels only; which way price must go
  edge   true (default)                         — levels only; must sit on a wick tip
  whole  true (default)                         — zones only; must wrap the candle entirely
  spanBars  int, default 1                      — zones only; how many candles the box wraps
  tolerance  float, default 0                   — absolute price slack for a touch

Exit code 0 if every drawing is accurate, 1 if any violation was found.
"""

import json
import os
import sys

OK, TOO_LONG, TOO_SHORT, FLOATING, ANCHOR, EDGE, PARTIAL, INVALID = (
    "ok", "too_long", "too_short", "floating", "anchor", "edge", "partial", "invalid")


def zone_extent(candles, start, span=1):
    """Full range of the candle(s) the box is anchored to."""
    seg = candles[start:start + max(1, span)]
    return max(c["h"] for c in seg), min(c["l"] for c in seg)


def nearest_anchor(candles, contains, start, span=8):
    """Bar closest to `start` whose range actually contains the drawing."""
    for r in range(0, span + 1):
        for j in (start - r, start + r):
            if 0 <= j < len(candles) and contains(candles[j]):
                return j
    return None


# --------------------------------------------------------------------------
# break detection
# --------------------------------------------------------------------------

def first_departure(candles, start, touching):
    """First bar after `start` where price is clear of the drawing.

    A level or zone is anchored to the candle that created it, so price is
    sitting on it at birth — the next bar "touching" it is not a break, it is
    price not having left yet. Nothing counts as a break until price has been
    away at least once. Returns None if price never leaves, which means the
    drawing is anchored somewhere price never departs from and the anchor
    itself is wrong.
    """
    for j in range(start + 1, len(candles)):
        if not touching(candles[j]):
            return j
    return None


def level_break_bar(candles, price, start, mode="touch", side="auto", tol=0.0,
                    require_departure=True):
    """First bar index where price breaks the level, else None.

    side "above" means the level sits above price and is broken by an up-move
    (a high reaching it, or a close through it); "below" is the mirror. "auto"
    infers the side from where the origin candle closed relative to the level.
    Returns (break_bar, departure_bar).
    """
    if side == "auto":
        side = "above" if price >= candles[start]["c"] else "below"

    def touching(c):
        return (c["h"] >= price - tol) if side == "above" else (c["l"] <= price + tol)

    dep = first_departure(candles, start, touching) if require_departure else start
    if dep is None:
        return None, None

    for j in range(dep + 1, len(candles)):
        c = candles[j]
        if mode == "close":
            hit = c["c"] > price + tol if side == "above" else c["c"] < price - tol
        else:                                    # touch / wick
            hit = touching(c)
        if hit:
            return j, dep
    return None, dep


def zone_break_bar(candles, top, bottom, start, mode="touch", tol=0.0,
                   require_departure=True):
    """First bar that trades back into the zone (mitigation), after price left it.
    Returns (break_bar, departure_bar)."""

    def overlaps(c):
        return c["h"] >= bottom - tol and c["l"] <= top + tol

    dep = first_departure(candles, start, overlaps) if require_departure else start
    if dep is None:
        return None, None

    for j in range(dep + 1, len(candles)):
        c = candles[j]
        if mode == "fill":                       # fully traversed
            hit = c["l"] <= bottom + tol and c["h"] >= top - tol
        elif mode == "close":                    # closed inside or through
            hit = bottom - tol <= c["c"] <= top + tol
        else:                                    # touch: any overlap
            hit = overlaps(c)
        if hit:
            return j, dep
    return None, dep


def level_ever_reached(candles, price, start, tol=0.0):
    """Did any bar from `start` onward come within tol of the level at all?"""
    return any(c["l"] - tol <= price <= c["h"] + tol for c in candles[start:])


# --------------------------------------------------------------------------
# checking
# --------------------------------------------------------------------------

def check_drawing(candles, d):
    """Return a finding dict for one drawing."""
    last = len(candles) - 1
    kind = d.get("kind", "level")
    dev = d.get("id", kind)
    start = d.get("from", 0)
    end = d.get("to")
    mode = d.get("mode", "touch")
    tol = float(d.get("tolerance", 0))

    def finding(status, msg, should_end=None):
        return {"id": dev, "kind": kind, "status": status, "message": msg,
                "from": start, "to": end, "should_end_at": should_end}

    # ---- structural sanity ------------------------------------------------
    if not isinstance(start, int) or not (0 <= start <= last):
        return finding(INVALID, f"origin bar {start} is outside the series (0..{last})")
    if end is not None and end < start:
        return finding(INVALID, f"ends at bar {end}, before it starts at {start}")

    if kind == "projection":
        # A projection is the one drawing allowed past the last bar — that is
        # its whole job. It must not start in the future or sit on real bars
        # it would be asserting things about.
        if end is not None and end <= last:
            return finding(TOO_SHORT,
                           f"a projection should extend past the last bar ({last}); "
                           f"it ends at {end}, on top of real candles")
        return finding(OK, "projection extends beyond the last bar, as intended")

    if kind == "target":
        # A target marks price that has not happened yet — untapped liquidity, a
        # take-profit. It has no anchor candle and cannot be "broken", so it is
        # exempt. The one thing it must be is actually untouched: the moment
        # price trades there it stops being a target and becomes a level.
        price = d["price"]
        if level_ever_reached(candles, price, start, tol):
            hit = next(j for j, c in enumerate(candles[start:], start)
                       if c["l"] - tol <= price <= c["h"] + tol)
            return finding(TOO_LONG,
                           f"declared a target, but price reaches {price} at bar {hit}; "
                           f"it is a level and must stop there", hit)
        return finding(OK, f"untapped target at {price}; price never gets there")

    dep_required = d.get("require_departure", True)

    if kind == "zone":
        top, bottom = d["top"], d["bottom"]
        if top <= bottom:
            return finding(INVALID, f"top ({top}) must be above bottom ({bottom})")

        def holds(c): return c["h"] >= bottom - tol and c["l"] <= top + tol
        if not holds(candles[start]):
            near = nearest_anchor(candles, holds, start)
            hint = f"; bar {near} does" if near is not None else ""
            return finding(ANCHOR,
                           f"bar {start} never trades in {bottom}–{top}, so the box is "
                           f"anchored to a candle that did not create it{hint}")
        # The box has to contain the candle whole. Cropped to the body it hides
        # the wick — which is the part that did the sweeping.
        if d.get("whole", True):
            hi, lo = zone_extent(candles, start, d.get("spanBars", 1))
            if abs(top - hi) > tol or abs(bottom - lo) > tol:
                return finding(PARTIAL,
                               f"is {bottom:.4g}–{top:.4g} but the candle(s) it wraps run "
                               f"{lo:.4g}–{hi:.4g}; the box must cover them wick to wick")

        brk, dep = zone_break_bar(candles, top, bottom, start, mode, tol, dep_required)
        if dep is None:
            return finding(INVALID,
                           f"price never leaves the zone after bar {start} — the box is "
                           f"anchored where price is still trading, so it has no origin")
    elif kind == "level":
        price = d["price"]
        side = d.get("side", "auto")

        def holds(c): return c["l"] - tol <= price <= c["h"] + tol
        if not holds(candles[start]):
            near = nearest_anchor(candles, holds, start)
            hint = f"; bar {near} reaches it" if near is not None else ""
            return finding(ANCHOR,
                           f"bar {start} never reaches {price}, so the line starts from a "
                           f"candle that did not make that level{hint}",
                           None)
        # A level is a wick tip. Drawn mid-candle it marks a price the candle
        # merely passed through, which is every price in its range — the line
        # then means nothing in particular.
        if d.get("edge", True):
            c0 = candles[start]
            if min(abs(price - c0["h"]), abs(price - c0["l"])) > tol:
                near = c0["h"] if abs(price - c0["h"]) <= abs(price - c0["l"]) else c0["l"]
                return finding(EDGE,
                               f"sits mid-candle at {price}; bar {start} runs "
                               f"{c0['l']:.4g}–{c0['h']:.4g}, so the level is {near:.4g}")

        brk, dep = level_break_bar(candles, price, start, mode, side, tol, dep_required)
        if dep is None:
            return finding(INVALID,
                           f"price never leaves {price} after bar {start} — the line is "
                           f"anchored inside the range it is meant to mark")
        if brk is None and not level_ever_reached(candles, price, start, tol):
            return finding(FLOATING,
                           f"price never returns to {price} after bar {start}; the line "
                           f"runs to the edge without ever being tested")
    else:
        return finding(INVALID, f"unknown kind '{kind}'")

    # ---- the actual rule --------------------------------------------------
    if brk is None:
        # never broken → it is allowed to run to the last bar
        if end is None or end == last:
            return finding(OK, "never broken; runs to the last bar")
        return finding(TOO_SHORT,
                       f"never broken, so it should run to bar {last}, not {end}",
                       last)

    if end is None:
        return finding(TOO_LONG,
                       f"runs to the right edge but bar {brk} breaks it "
                       f"({mode}); it should stop there", brk)
    if end > brk:
        return finding(TOO_LONG,
                       f"ends at bar {end} but bar {brk} already broke it "
                       f"({mode}); it is drawn {end - brk} bars too long", brk)
    if end < brk:
        return finding(TOO_SHORT,
                       f"ends at bar {end} but survives until bar {brk}; "
                       f"it is cut {brk - end} bars short", brk)
    return finding(OK, f"ends exactly at the breaking bar {brk}")


def verify(spec):
    candles = spec["candles"]
    findings = [check_drawing(candles, d) for d in spec.get("drawings", [])]
    return findings


def apply_fixes(spec, findings, snap=False):
    """Return a copy of the spec with endpoints corrected.

    With snap=True, a mis-anchored level is pulled onto the extreme of the
    candle it claims to start from, rather than the line being slid along to
    some other bar. That matches how this gets fixed by hand: the level *is*
    the high or the low of that candle, so the price moves, not the anchor.
    """
    out = json.loads(json.dumps(spec))
    candles = out["candles"]
    by_id = {f["id"]: f for f in findings}
    for d in out.get("drawings", []):
        f = by_id.get(d.get("id", d.get("kind")))
        if not f:
            continue
        if f["status"] in (TOO_LONG, TOO_SHORT) and f["should_end_at"] is not None:
            d["to"] = f["should_end_at"]
        elif f["status"] in (ANCHOR, EDGE, PARTIAL) and snap:
            c = candles[d["from"]]
            if d.get("kind") == "level":
                # pull the line onto whichever wick tip it was closest to
                d["price"] = c["h"] if abs(c["h"] - d["price"]) <= abs(c["l"] - d["price"]) else c["l"]
            elif d.get("kind") == "zone":
                d["top"], d["bottom"] = zone_extent(candles, d["from"], d.get("spanBars", 1))
    return out


# --------------------------------------------------------------------------

ICON = {OK: "ok  ", TOO_LONG: "LONG", TOO_SHORT: "SHRT", FLOATING: "FLOAT",
        ANCHOR: "ANCH", EDGE: "EDGE", PARTIAL: "PART", INVALID: "BAD "}


def selftest():
    """Run the bundled example and confirm the rules still fire as documented.
    Verifies an install without needing a chart of your own."""
    here = os.path.dirname(os.path.abspath(__file__))
    spec_path = os.path.join(here, "..", "examples", "demo-spec.json")
    exp_path = os.path.join(here, "..", "examples", "demo-spec.expected.json")
    spec = json.load(open(spec_path))
    expected = json.load(open(exp_path))
    got = {f["id"]: f["status"] for f in verify(spec)}
    bad = {k: (v, got.get(k)) for k, v in expected.items() if got.get(k) != v}
    for k, v in expected.items():
        mark = "ok  " if got.get(k) == v else "FAIL"
        print(f"  [{mark}] {k:<14} expected {v}, got {got.get(k)}")
    if bad:
        print(f"\n{len(bad)} check(s) failed — the rules are not behaving as documented.")
        return 1
    print(f"\nall {len(expected)} checks pass; the skill is installed and working.")
    return 0


def main():
    args = sys.argv[1:]
    if args and args[0] == "--selftest":
        return selftest()
    if not args:
        print(__doc__)
        return 2
    spec = json.load(open(args[0]))
    findings = verify(spec)

    if "--json" in args:
        print(json.dumps({"findings": findings}, ensure_ascii=False, indent=2))
    else:
        bad = [f for f in findings if f["status"] != OK]
        print(f"{len(spec['candles'])} candles · {len(findings)} drawings · "
              f"{len(bad)} violation(s)\n")
        for f in findings:
            tail = "" if f["should_end_at"] is None else f"  → to: {f['should_end_at']}"
            print(f"  [{ICON[f['status']]}] {f['id']:<14} {f['message']}{tail}")
        if bad:
            print("\nEvery line and box must stop at the candle that broke it — "
                  "past that point it is no longer a level, it is decoration.")

    if "--fix" in args:
        out = args[args.index("--fix") + 1]
        json.dump(apply_fixes(spec, findings, snap="--snap" in args), open(out, "w"),
                  ensure_ascii=False, indent=2)
        print(f"\ncorrected spec written to {out}")

    return 1 if any(f["status"] != OK for f in findings) else 0


if __name__ == "__main__":
    sys.exit(main())
