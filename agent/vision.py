"""Vision multi-agent — each school marks up the chart image, a coordinator
merges them into a graded trade plan.

Given a chart screenshot, runs one Claude vision agent per school (ICT, SMC,
Volume Profile, Footprint) that reads and marks up the image through that
school's rules, then a coordinator agent that combines the markups per the
schools' conditions into a trade with entry / stop / targets and risk.
"""
import json
import base64
import threading

from anthropic import Anthropic

from . import config, risk
from .logging_setup import jlog

_client = None
_lock = threading.Lock()

SCHOOLS = {
    "ict": (
        "You are a MASTER ICT (Inner Circle Trader) analyst. Read this chart with the "
        "full ICT toolkit and report only what is actually present:\n"
        "- Liquidity: buy-side/sell-side (BSL/SSL), equal highs/lows, old highs/lows, "
        "relative equal levels, session/Asian-range liquidity, and the DRAW ON "
        "LIQUIDITY (where price is likely being pulled).\n"
        "- PD arrays: fair value gaps (BISI/SIBI), order blocks (bullish/bearish), "
        "breaker blocks, mitigation blocks, rejection blocks, propulsion blocks, and "
        "liquidity voids.\n"
        "- Structure & intent: displacement, market structure shift (MSS) vs BOS, and "
        "any liquidity sweep/stop-run that PRECEDED a shift (the setup trigger).\n"
        "- Dealing range: mark equilibrium (50%) and whether price is at a PREMIUM "
        "(favor shorts) or DISCOUNT (favor longs); locate the OTE zone (62-79% retrace).\n"
        "- Model context: Power of Three (accumulation-manipulation-distribution), Judas "
        "swing, turtle soup, and killzone timing if inferable.\n"
        "Give the ICT bias, the specific numeric levels, and the single highest-probability "
        "PD array + its draw-on-liquidity target."),
    "smc": (
        "You are a MASTER Smart Money Concepts analyst. Map the chart precisely:\n"
        "- Structure: label HH/HL/LH/LL, distinguish INTERNAL vs EXTERNAL structure, and "
        "mark every BOS and CHoCH (change of character = the real reversal signal).\n"
        "- Liquidity: inducement (IDM) that traps early entries, engineered/equal highs-"
        "lows, and liquidity sweeps into a POI.\n"
        "- POI: the valid, refined order block (last opposing candle before the impulse "
        "that broke structure) or supply/demand zone; note if it is fresh or mitigated, "
        "and any breaker/flip zone.\n"
        "- Imbalance: FVG within the leg and whether it has been mitigated.\n"
        "- Location: premium/discount relative to the dealing-range equilibrium (50%).\n"
        "Give the SMC bias, the exact POI zone (numeric range), the inducement level it "
        "needs to sweep first, and the CHoCH level that confirms entry."),
    "volume_profile": (
        "You are a MASTER Volume Profile / Auction Market Theory analyst. From the visible "
        "range and any volume bars, read the auction:\n"
        "- Key levels: Point of Control (POC), Value Area High/Low (VAH/VAL, ~70% of "
        "volume), and any naked/virgin POC left untested.\n"
        "- Nodes: High Volume Nodes (HVN = magnets/acceptance) and Low Volume Nodes "
        "(LVN = rejection/fast-move zones).\n"
        "- Profile shape: D (balanced), P (short-covering/bullish), b (long-liquidation/"
        "bearish), B (double distribution/trend day), or thin/trend.\n"
        "- Auction state: is price ACCEPTING (building value) or REJECTING (excess, single "
        "prints, poor high/low) value? Initiative vs responsive activity; balance vs "
        "imbalance; the 80% rule if price re-enters value.\n"
        "Give the auction bias and the numeric POC/VAH/VAL plus the nearest HVN magnet and "
        "LVN that price would travel through."),
    "footprint": (
        "You are a MASTER order-flow / footprint analyst working from a chart image (no "
        "tick/delta feed), so INFER order flow from price action and any visible volume "
        "bars:\n"
        "- Absorption: large effort with little price result (big volume/long bars that "
        "fail to move price) = a passive player absorbing — often a reversal zone.\n"
        "- Exhaustion: climax volume into a swing with a wide-range bar then stall.\n"
        "- Delta proxy: strong closes near highs (buy pressure) vs near lows (sell "
        "pressure); track the sequence for a delta/price DIVERGENCE.\n"
        "- Trapped traders: failed breakout / stop-run beyond a level that snaps back "
        "(liquidity grab) — fade the trapped side.\n"
        "- Unfinished auction: swing extreme with no rejection wick (no excess) that price "
        "should revisit; effort-vs-result at key levels.\n"
        "State whether flow favors up or down and the exact absorption/exhaustion/trap "
        "levels that confirm or reject a trade."),
}

_PLAN_SCHEMA = {
    "type": "object",
    "properties": {
        "action": {"type": "string", "enum": ["long", "short", "no_trade", "alert_human"]},
        "grade": {"type": "string", "enum": ["A", "B", "C", "none"]},
        "confidence": {"type": "number"},
        "entry": {"type": "number"},
        "stop_loss": {"type": "number"},
        "take_profit": {"type": "number"},
        "reason": {"type": "string"},
        # vertical position (0=top edge .. 1=bottom edge) of each level on THIS
        # chart image, so the markup can be drawn on it. Filled for long/short.
        "entry_y": {"type": "number"},
        "stop_y": {"type": "number"},
        "target_y": {"type": "number"},
        # the schools' key levels/zones to draw on the chart (FVG, order blocks,
        # POC/VAH/VAL, liquidity, BOS/CHoCH). price2 marks a zone's other bound.
        "key_levels": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "label": {"type": "string"},
                    "price": {"type": "number"},
                    "price2": {"type": "number"},
                    "kind": {"type": "string", "enum": ["bull", "bear", "neutral"]},
                },
                "required": ["label", "price", "kind"],
                "additionalProperties": False,
            },
        },
    },
    "required": ["action", "grade", "confidence", "entry", "stop_loss",
                 "take_profit", "reason"],
    "additionalProperties": False,
}


def _c():
    global _client
    with _lock:
        if _client is None:
            _client = Anthropic()
    return _client


def _img(png: bytes) -> dict:
    return {"type": "image", "source": {"type": "base64", "media_type": "image/png",
            "data": base64.b64encode(png).decode()}}


def _markup(school: str, png: bytes, symbol: str, timeframe: str,
            htf_context: str = "") -> dict:
    prompt = (f"{SCHOOLS[school]}\n\nChart: {symbol} {timeframe}. Read prices precisely "
              "from the right-hand axis. Report only elements ACTUALLY visible (do not "
              "invent). Be tight (<=160 words): the bias, the specific numeric levels, "
              "and the single highest-probability setup this school sees.")
    if htf_context:
        prompt += ("\n\nHigher-timeframe bias to respect (align entries with it):\n"
                   + htf_context)
    resp = _c().messages.create(
        model=config.VISION_MARKUP_MODEL, max_tokens=1100, thinking={"type": "adaptive"},
        messages=[{"role": "user", "content": [_img(png), {"type": "text", "text": prompt}]}])
    text = next((b.text for b in resp.content if b.type == "text"), "")
    jlog("vision_markup", school=school, symbol=symbol, ok=bool(text))
    return {"school": school, "markup": text.strip()}


def _coordinate(markups, png, symbol, timeframe, htf_context: str = "") -> dict:
    lenses = "\n\n".join(f"[{m['school'].upper()}]\n{m['markup']}" for m in markups)
    htf_block = ""
    if htf_context:
        htf_block = ("\n\nHIGHER-TIMEFRAME BIAS (already analyzed — the trade must "
                     f"align with this direction):\n{htf_context}\n")
    tf_note = (f" The entry, stop and targets are read from this {timeframe} chart, "
               "but the direction must respect the higher-timeframe bias above."
               if htf_context else "")
    prompt = (
        f"You are the head analyst combining four schools on {symbol} {timeframe}. "
        "Below are each school's markup of the attached chart. Apply the schools in "
        "confluence and grade the setup: A = 3-4 schools agree, B = 2, C = 1, none = "
        f"conflict/flat. Only propose long/short on a {config.MIN_GRADE} setup or better "
        f"with reward:risk >= {config.MIN_RR}. Set stop_loss beyond the structural invalidation and "
        "take_profit at the opposing liquidity / value-area edge. If no valid trade, "
        "use action no_trade (or alert_human if a human should look). Read levels from "
        "the chart axis. Write the 'reason' field in ARABIC — a concise sentence citing "
        "the schools that agree and the key levels (اكتب حقل reason بالعربية). "
        "If action is long or short, ALSO return entry_y, stop_y and target_y: the "
        "vertical position of the entry, stop and target on THIS image as a fraction "
        "from 0.0 (very top edge) to 1.0 (very bottom edge), read against the right-hand "
        "price axis (higher price = smaller fraction). ALSO return key_levels: up to 6 of "
        "the most important levels/zones the schools identified to draw on the chart — "
        "FVG, order blocks, POC/VAH/VAL, liquidity pools, BOS/CHoCH levels — each with a "
        "short English label (e.g. 'FVG', 'OB', 'POC', 'BSL', 'SSL'), its price (and "
        "price2 for a zone's other edge), and kind (bull=support/demand, bear=supply/"
        "resistance, neutral=reference)."
        f"{tf_note}{htf_block}\n\n{lenses}")
    # generous budget: with a multi-timeframe chain the context is large and the
    # structured output carries the plan + drawing coordinates + key_levels + an
    # Arabic reason. Too small a cap truncates the JSON and it fails to parse.
    resp = _c().messages.create(
        model=config.MODEL, max_tokens=4000, thinking={"type": "adaptive"},
        output_config={"effort": "high", "format": {"type": "json_schema", "schema": _PLAN_SCHEMA}},
        messages=[{"role": "user", "content": [_img(png), {"type": "text", "text": prompt}]}])
    text = next((b.text for b in resp.content if b.type == "text"), "") or ""
    try:
        plan = json.loads(text) if text.strip() else {}
    except json.JSONDecodeError:
        plan = {}
    if not plan:
        plan = {"action": "alert_human", "grade": "none", "confidence": 0.0,
                "entry": 0, "stop_loss": 0, "take_profit": 0,
                "reason": "coordinator returned unparseable output"}
    return plan


_REVIEW_SCHEMA = {
    "type": "object",
    "properties": {
        "reviews": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                    "status": {"type": "string",
                               "enum": ["tp_hit", "sl_hit", "running", "unclear"]},
                    "manage": {"type": "string",
                               "enum": ["hold", "move_sl_be", "partial_tp",
                                        "trail_sl", "tighten_sl", "exit"]},
                    "note": {"type": "string"},
                },
                "required": ["id", "status", "manage", "note"],
                "additionalProperties": False,
            },
        }
    },
    "required": ["reviews"],
    "additionalProperties": False,
}


def evaluate_open_trades(png: bytes, symbol: str, timeframe: str, trades: list) -> dict:
    """Review still-open trades against the current chart image.

    For each open trade (entry/SL/TP), judge from the screenshot whether price has
    since hit the take-profit, hit the stop-loss, or is still running. Returns a
    map of trade id -> {status, note}. The 'note' is written in Arabic.
    """
    if not trades:
        return {}
    listing = "\n".join(
        f"- id={t['id']} | {t['action']} | دخول {t.get('entry')} | "
        f"وقف {t.get('sl')} | هدف {t.get('tp')}" for t in trades)
    prompt = (
        f"These are OPEN trades previously signalled on {symbol} {timeframe}. Using the "
        "attached current chart, for EACH trade decide two things:\n"
        "1) status — has price reached take_profit (tp_hit), hit stop_loss (sl_hit), or "
        "is it still running (running)? Use 'unclear' only if the levels are off-screen. "
        "For a LONG, tp is above and sl is below entry; for a SHORT, the reverse.\n"
        "2) manage — a trade-management recommendation from the current price action "
        "(only meaningful while running): 'hold' (on track, do nothing), 'move_sl_be' "
        "(in decent profit — move stop to entry/breakeven), 'partial_tp' (near a level / "
        "extended — bank partial profit), 'trail_sl' (trending your way — trail the stop "
        "behind structure), 'tighten_sl' (momentum fading — tighten the stop), or 'exit' "
        "(structure/context flipped against the trade — close early). Be conservative: "
        "prefer 'hold' unless the chart clearly warrants an action.\n"
        "Read levels from the right-hand axis. Write each 'note' in ARABIC — a short "
        "sentence justifying the management call (سطر قصير بالعربية).\n\n"
        f"{listing}")
    try:
        resp = _c().messages.create(
            model=config.VISION_MARKUP_MODEL, max_tokens=1500, thinking={"type": "adaptive"},
            output_config={"effort": "high",
                           "format": {"type": "json_schema", "schema": _REVIEW_SCHEMA}},
            messages=[{"role": "user",
                       "content": [_img(png), {"type": "text", "text": prompt}]}])
        text = next((b.text for b in resp.content if b.type == "text"), "{}")
        reviews = json.loads(text).get("reviews", [])
    except Exception as e:
        jlog("vision_review_error", symbol=symbol, error=str(e)[:200])
        return {}
    out = {r["id"]: {"status": r.get("status", "unclear"),
                     "manage": r.get("manage", "hold"), "note": r.get("note", "")}
           for r in reviews if r.get("id")}
    jlog("vision_review", symbol=symbol, reviewed=len(out))
    return out


_LOCATE_SCHEMA = {
    "type": "object",
    "properties": {
        "entry_y": {"type": "number"},
        "stop_y": {"type": "number"},
        "target_y": {"type": "number"},
    },
    "required": ["entry_y", "stop_y", "target_y"],
    "additionalProperties": False,
}


def locate_levels(png: bytes, symbol: str, timeframe: str, decision: dict) -> dict:
    """Find where the trade's price levels sit on the image, so they can be drawn.

    Returns each level's vertical position as a fraction 0.0 (top edge) .. 1.0
    (bottom edge), read against the right-hand price axis. Empty on failure.
    """
    entry, sl, tp = (decision.get("entry"), decision.get("stop_loss"),
                     decision.get("take_profit"))
    if None in (entry, sl, tp):
        return {}
    prompt = (
        f"On this {symbol} {timeframe} chart, give the VERTICAL position of each price "
        "level as it appears in the image, as a fraction from 0.0 (very top edge) to 1.0 "
        "(very bottom edge). Read against the right-hand price axis and interpolate "
        f"between the visible gridline prices:\n- entry = {entry} -> entry_y\n"
        f"- stop_loss = {sl} -> stop_y\n- take_profit = {tp} -> target_y\n"
        "Higher price = smaller fraction (nearer the top).")
    try:
        # ample max_tokens: adaptive thinking must not starve the JSON output
        # (a tight cap makes the model spend the budget thinking and emit nothing).
        resp = _c().messages.create(
            model=config.VISION_MARKUP_MODEL, max_tokens=2000, thinking={"type": "adaptive"},
            output_config={"effort": "high",
                           "format": {"type": "json_schema", "schema": _LOCATE_SCHEMA}},
            messages=[{"role": "user",
                       "content": [_img(png), {"type": "text", "text": prompt}]}])
        text = next((b.text for b in resp.content if b.type == "text"), "") or ""
        raw = json.loads(text) if text.strip() else {}
    except Exception as e:
        jlog("vision_locate_error", symbol=symbol, error=str(e)[:200])
        return {}
    out = {}
    for k in ("entry_y", "stop_y", "target_y"):
        v = raw.get(k)
        if v is not None:
            out[k] = min(1.0, max(0.0, float(v)))
    complete = len(out) == 3
    jlog("vision_locate", symbol=symbol, ok=complete, **out)
    return out if complete else {}


def analyze(png: bytes, symbol: str, timeframe: str) -> dict:
    """Run the four school markups + coordinator. Returns {decision, markups}."""
    return _finalize(_run_schools(png, symbol, timeframe), png, symbol, timeframe)


def _run_schools(png, symbol, timeframe, htf_context=""):
    markups = []
    for school in config.VISION_SCHOOLS:
        if school not in SCHOOLS:
            continue
        try:
            markups.append(_markup(school, png, symbol, timeframe, htf_context))
        except Exception as e:
            jlog("vision_markup_error", school=school, error=str(e)[:200])
            markups.append({"school": school, "markup": f"(failed: {e})"})
    return markups


def _finalize(markups, png, symbol, timeframe, htf_context=""):
    plan = _coordinate(markups, png, symbol, timeframe, htf_context)
    decision = {
        "action": plan.get("action", "alert_human"),
        "confidence": float(plan.get("confidence", 0) or 0),
        "grade": plan.get("grade", "none"),
        "reason": plan.get("reason", ""),
    }
    # enforce the minimum confluence grade: only fire on strong multi-school
    # agreement; weaker setups are downgraded to no_trade (kept for the record).
    _rank = {"A": 3, "B": 2, "C": 1, "none": 0}
    if decision["action"] in ("long", "short") and \
            _rank.get(decision["grade"], 0) < _rank.get(config.MIN_GRADE, 2):
        jlog("grade_gate", symbol=symbol, grade=decision["grade"],
             min_grade=config.MIN_GRADE, was=decision["action"])
        decision["action"] = "no_trade"

    decision.update(risk.compute(decision["action"], plan.get("entry", 0),
                                 plan.get("stop_loss", 0), plan.get("take_profit", 0)))
    # coordinator-provided drawing coordinates (primary source for the markup)
    levels = {}
    for k in ("entry_y", "stop_y", "target_y"):
        v = plan.get(k)
        if v is not None:
            levels[k] = min(1.0, max(0.0, float(v)))
    levels = levels if len(levels) == 3 else {}
    # the schools' key levels/zones to draw on the chart
    key_levels = []
    for it in (plan.get("key_levels") or [])[:6]:
        try:
            price = float(it.get("price"))
        except (TypeError, ValueError):
            continue
        lvl = {"label": str(it.get("label", ""))[:20], "price": price,
               "kind": it.get("kind", "neutral")}
        p2 = it.get("price2")
        if p2 not in (None, 0):
            try:
                lvl["price2"] = float(p2)
            except (TypeError, ValueError):
                pass
        key_levels.append(lvl)
    jlog("vision_decision", symbol=symbol, action=decision["action"],
         grade=decision["grade"], rr=decision.get("risk_reward"),
         located=bool(levels), key_levels=len(key_levels))
    return {"decision": decision, "markups": markups, "levels": levels,
            "key_levels": key_levels}


def analyze_chain(shots, symbol) -> dict:
    """Top-down over an ordered list of (timeframe, png), highest -> lowest.

    Each higher timeframe's read becomes bias context for the next one down, so a
    4H -> 15m -> 3m chain narrows from directional bias to the precise entry. The
    coordinator produces the trade (entry/stop/targets + drawing coordinates) on
    the LOWEST (entry) chart, constrained by everything above it.
    """
    if not shots:
        raise ValueError("no chart shots")
    if len(shots) == 1:
        tf, png = shots[0]
        return _finalize(_run_schools(png, symbol, tf), png, symbol, tf)

    context_parts, all_markups = [], []
    for tf, png in shots[:-1]:                     # every timeframe above the entry
        ms = _run_schools(png, symbol, tf, "\n\n".join(context_parts))
        for m in ms:
            m["timeframe"] = tf
        all_markups += ms
        context_parts.append(f"=== {tf} timeframe ===\n" + "\n".join(
            f"[{m['school'].upper()}] {m['markup']}" for m in ms))

    htf_context = "\n\n".join(context_parts)
    entry_tf, entry_png = shots[-1]                # the entry chart
    entry_ms = _run_schools(entry_png, symbol, entry_tf, htf_context)
    for m in entry_ms:
        m["timeframe"] = entry_tf
    out = _finalize(entry_ms, entry_png, symbol, entry_tf, htf_context)
    out["markups"] = all_markups + entry_ms
    out["decision"]["timeframe"] = entry_tf
    return out


def analyze_mtf(htf_png, ltf_png, symbol, htf, ltf) -> dict:
    """Two-timeframe convenience wrapper over analyze_chain (bias TF then entry TF)."""
    return analyze_chain([(htf, htf_png), (ltf, ltf_png)], symbol)
