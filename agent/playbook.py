"""School 'playbook' — the distilled winning patterns of each methodology.

A labelled corpus of 1000 real winning trades per school isn't wired (no
historical chart dataset), and faking a backtest would be dishonest. But 1000
winners are not 1000 different setups — they repeat a finite set of models. So a
master agent distills that set per school: each recurring pattern, WHY it wins,
its entry trigger, and its invalidation. We persist it (survives restarts via
the state volume) and inject a compact form back into every markup, so the live
agents recognise and prioritise the setups that actually repeat in winners.

Build once:  python tv_claude_bridge.py --learn
"""
import os
import json
import threading

from anthropic import Anthropic

from . import config
from .logging_setup import jlog

_client = None
_lock = threading.Lock()
_cache = {}

SCHOOL_NAMES = {
    "ict": "ICT (Inner Circle Trader)",
    "smc": "Smart Money Concepts",
    "volume_profile": "Volume Profile / Auction Market Theory",
    "footprint": "Order Flow / Footprint",
}

_SCHEMA = {
    "type": "object",
    "properties": {
        "patterns": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "setup": {"type": "string"},
                    "why_it_works": {"type": "string"},
                    "entry_trigger": {"type": "string"},
                    "invalidation": {"type": "string"},
                },
                "required": ["name", "setup", "why_it_works",
                             "entry_trigger", "invalidation"],
                "additionalProperties": False,
            },
        }
    },
    "required": ["patterns"],
    "additionalProperties": False,
}


def _c():
    global _client
    with _lock:
        if _client is None:
            _client = Anthropic()
    return _client


def _dir():
    d = os.path.join(config.STATE_DIR, "playbook")
    os.makedirs(d, exist_ok=True)
    return d


def _path(school):
    return os.path.join(_dir(), f"{school}.json")


def build_school(school: str, n: int = 18) -> list:
    """Distill the recurring winning models for one school and persist them."""
    name = SCHOOL_NAMES.get(school, school)
    prompt = (
        f"You are a master {name} trader who has reviewed thousands of WINNING "
        f"{name} trades. Distill the recurring, high-probability models those winners "
        f"repeat — the finite set of patterns that a thousand winning trades collapse "
        f"into. Return up to {n} distinct models. For EACH: name, setup (exactly what it "
        "looks like on the chart), why_it_works (the market-mechanics reason it wins — "
        "who is trapped, what liquidity is taken, why price must move), entry_trigger "
        "(the precise confirmation to enter), and invalidation (what proves it wrong). "
        "Be concrete and practical; these guide live trade selection.")
    resp = _c().messages.create(
        model=config.MODEL, max_tokens=12000, thinking={"type": "adaptive"},
        output_config={"effort": "high",
                       "format": {"type": "json_schema", "schema": _SCHEMA}},
        messages=[{"role": "user", "content": prompt}])
    text = next((b.text for b in resp.content if b.type == "text"), "") or ""
    try:
        patterns = json.loads(text).get("patterns", []) if text.strip() else []
    except json.JSONDecodeError:
        patterns = []
    with open(_path(school), "w", encoding="utf-8") as f:
        json.dump({"school": school, "patterns": patterns}, f,
                  ensure_ascii=False, indent=2)
    _cache.pop(school, None)
    jlog("playbook_built", school=school, patterns=len(patterns))
    return patterns


def build_all(schools=None) -> dict:
    """Build (or rebuild) the playbook for each school. Returns {school: count}."""
    schools = schools or list(SCHOOL_NAMES)
    out = {}
    for s in schools:
        try:
            out[s] = len(build_school(s))
        except Exception as e:
            jlog("playbook_build_error", school=s, error=str(e)[:200])
            out[s] = 0
    return out


def load(school: str) -> list:
    if school in _cache:
        return _cache[school]
    try:
        with open(_path(school), encoding="utf-8") as f:
            pats = json.load(f).get("patterns", [])
    except (FileNotFoundError, json.JSONDecodeError):
        pats = []
    _cache[school] = pats
    return pats


def summary(school: str, limit: int = 8) -> str:
    """Compact form injected into a markup prompt: name + setup + why (one line each)."""
    pats = load(school)
    if not pats:
        return ""
    return "\n".join(
        f"- {p.get('name')}: {p.get('setup')} (wins because {p.get('why_it_works')})"
        for p in pats[:limit])


def status() -> dict:
    """How many patterns are stored per school (for /status and diagnostics)."""
    return {s: len(load(s)) for s in SCHOOL_NAMES}
