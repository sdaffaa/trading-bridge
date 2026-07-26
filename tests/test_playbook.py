"""School playbook — build (stubbed), persist, load, and compact summary."""
import json

from agent import playbook


class _Block:
    type = "text"
    def __init__(self, t): self.text = t


class _Resp:
    def __init__(self, t): self.content = [_Block(t)]


class _Msgs:
    def __init__(self, payload): self._p = payload
    def create(self, **kw): return _Resp(json.dumps(self._p))


class _Client:
    def __init__(self, payload): self.messages = _Msgs(payload)


_PATTERNS = {"patterns": [
    {"name": "FVG + liquidity sweep", "setup": "sweep of SSL then bullish FVG",
     "why_it_works": "traps sellers and rebalances price", "entry_trigger": "return to FVG",
     "invalidation": "close below the sweep low"},
    {"name": "Order block retest", "setup": "bullish OB after BOS",
     "why_it_works": "unmitigated demand", "entry_trigger": "tap of OB",
     "invalidation": "OB fully traded through"},
]}


def test_build_school_persists_and_loads(monkeypatch):
    monkeypatch.setattr(playbook, "_client", _Client(_PATTERNS))
    monkeypatch.setattr(playbook, "_cache", {})
    pats = playbook.build_school("ict")
    assert len(pats) == 2
    # a fresh load (cache cleared) reads it back from disk
    monkeypatch.setattr(playbook, "_cache", {})
    assert len(playbook.load("ict")) == 2


def test_summary_is_compact_and_cites_reason(monkeypatch):
    monkeypatch.setattr(playbook, "_client", _Client(_PATTERNS))
    monkeypatch.setattr(playbook, "_cache", {})
    playbook.build_school("smc")
    monkeypatch.setattr(playbook, "_cache", {})
    s = playbook.summary("smc")
    assert "FVG + liquidity sweep" in s
    assert "wins because" in s               # the reason is surfaced to the agent


def test_summary_empty_when_not_built(monkeypatch):
    monkeypatch.setattr(playbook, "_cache", {})
    assert playbook.summary("footprint") == ""     # nothing learned yet -> no injection


def test_build_all_covers_every_school(monkeypatch):
    monkeypatch.setattr(playbook, "_client", _Client(_PATTERNS))
    monkeypatch.setattr(playbook, "_cache", {})
    out = playbook.build_all()
    assert set(out) == set(playbook.SCHOOL_NAMES)
    assert all(v == 2 for v in out.values())
