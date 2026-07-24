"""Shared pytest fixtures — isolate config, idempotency state, and the Claude call.

No network or API key is needed: the Anthropic client is stubbed so the agent
loop runs but calls nothing.
"""
import pytest

from agent import config, idempotency, tools
import agent.runtime as runtime


@pytest.fixture(autouse=True)
def isolate(tmp_path, monkeypatch):
    """Per-test isolation: fresh state dir, dry-run on, deterministic policy."""
    monkeypatch.setattr(config, "STATE_DIR", str(tmp_path / "state"))
    monkeypatch.setattr(config, "DRY_RUN", True)
    monkeypatch.setattr(config, "ENABLE_CHART_READS", False)
    monkeypatch.setattr(config, "KILL_SWITCH_FILE", str(tmp_path / "kill"))
    monkeypatch.setattr(config, "ALLOWED_SYMBOLS", {"OANDA:XAUUSD", "BINANCE:BTCUSDT"})
    monkeypatch.setattr(config, "ALLOWED_ACTIONS", {"buy", "sell", "info"})
    monkeypatch.setattr(config, "WEBHOOK_SECRET", "")
    # reset the file-backed idempotency cache between tests
    monkeypatch.setattr(idempotency, "_SEEN", set())
    monkeypatch.setattr(idempotency, "_LOADED", False)
    yield


class _FakeMessages:
    def __init__(self, calls):
        self._calls = calls

    def tool_runner(self, **kw):
        self._calls.append(kw)
        return iter([])          # agent does nothing; loop ends immediately


class _FakeBeta:
    def __init__(self, calls):
        self.messages = _FakeMessages(calls)


class _FakeClient:
    def __init__(self, calls):
        self.beta = _FakeBeta(calls)


@pytest.fixture
def stub_claude(monkeypatch):
    """Replace the Anthropic client with a fake; return the captured call list."""
    calls = []
    monkeypatch.setattr(runtime, "_client", _FakeClient(calls))
    return calls
