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
        "You are an ICT (Inner Circle Trader) analyst. Mark up this chart the ICT "
        "way: identify buy-side and sell-side liquidity (equal highs/lows, old "
        "highs/lows), fair value gaps (imbalances), order blocks, displacement, and "
        "any liquidity sweep followed by a shift. State the ICT bias and the key "
        "price levels (as numbers read from the axis)."),
    "smc": (
        "You are a Smart Money Concepts analyst. Mark up market structure: label "
        "the trend via BOS/CHoCH, mark swing highs/lows, and identify the valid "
        "point of interest (order block / supply-demand) for a pullback entry, plus "
        "inducement/liquidity. State the SMC bias and key levels as numbers."),
    "volume_profile": (
        "You are a Volume Profile / Auction analyst. From the visible range estimate "
        "the Point of Control, Value Area High/Low, and any high/low volume nodes. "
        "Judge whether price is accepting or rejecting value. State the bias and the "
        "POC/VAH/VAL levels as numbers."),
    "footprint": (
        "You are an order-flow analyst. From candle bodies, wicks, and relative bar "
        "sizes infer momentum, absorption, and exhaustion (you have no tick data, so "
        "reason from price action). State whether flow supports up or down and note "
        "any exhaustion/absorption levels."),
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


def _markup(school: str, png: bytes, symbol: str, timeframe: str) -> dict:
    prompt = (f"{SCHOOLS[school]}\n\nChart: {symbol} {timeframe}. Read prices from the "
              "right-hand axis. Be concise (<=120 words): bias + the specific levels.")
    resp = _c().messages.create(
        model=config.MODEL, max_tokens=700, thinking={"type": "adaptive"},
        messages=[{"role": "user", "content": [_img(png), {"type": "text", "text": prompt}]}])
    text = next((b.text for b in resp.content if b.type == "text"), "")
    jlog("vision_markup", school=school, symbol=symbol, ok=bool(text))
    return {"school": school, "markup": text.strip()}


def _coordinate(markups, png, symbol, timeframe) -> dict:
    lenses = "\n\n".join(f"[{m['school'].upper()}]\n{m['markup']}" for m in markups)
    prompt = (
        f"You are the head analyst combining four schools on {symbol} {timeframe}. "
        "Below are each school's markup of the attached chart. Apply the schools in "
        "confluence and grade the setup: A = 3-4 schools agree, B = 2, C = 1, none = "
        "conflict/flat. Only propose long/short on a B setup or better with reward:risk "
        f">= {config.MIN_RR}. Set stop_loss beyond the structural invalidation and "
        "take_profit at the opposing liquidity / value-area edge. If no valid trade, "
        "use action no_trade (or alert_human if a human should look). Read levels from "
        f"the chart axis.\n\n{lenses}")
    resp = _c().messages.create(
        model=config.MODEL, max_tokens=1500, thinking={"type": "adaptive"},
        output_config={"effort": "high", "format": {"type": "json_schema", "schema": _PLAN_SCHEMA}},
        messages=[{"role": "user", "content": [_img(png), {"type": "text", "text": prompt}]}])
    text = next((b.text for b in resp.content if b.type == "text"), "{}")
    try:
        plan = json.loads(text)
    except json.JSONDecodeError:
        plan = {"action": "alert_human", "grade": "none", "confidence": 0.0,
                "entry": 0, "stop_loss": 0, "take_profit": 0,
                "reason": "coordinator returned unparseable output"}
    return plan


def analyze(png: bytes, symbol: str, timeframe: str) -> dict:
    """Run the four school markups + coordinator. Returns {decision, markups}."""
    markups = []
    for school in config.VISION_SCHOOLS:
        if school not in SCHOOLS:
            continue
        try:
            markups.append(_markup(school, png, symbol, timeframe))
        except Exception as e:
            jlog("vision_markup_error", school=school, error=str(e)[:200])
            markups.append({"school": school, "markup": f"(failed: {e})"})

    plan = _coordinate(markups, png, symbol, timeframe)
    decision = {
        "action": plan.get("action", "alert_human"),
        "confidence": float(plan.get("confidence", 0) or 0),
        "grade": plan.get("grade", "none"),
        "reason": plan.get("reason", ""),
    }
    decision.update(risk.compute(decision["action"], plan.get("entry", 0),
                                 plan.get("stop_loss", 0), plan.get("take_profit", 0)))
    jlog("vision_decision", symbol=symbol, action=decision["action"],
         grade=decision["grade"], rr=decision.get("risk_reward"))
    return {"decision": decision, "markups": markups}
