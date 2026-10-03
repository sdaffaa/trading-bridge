"""Shared pytest fixtures — isolate config, idempotency state, and the Claude call.

No network or API key is needed: the Anthropic client is stubbed so the agent
loop runs but calls nothing.
"""
import pytest

from agent import config, store, budget, monitoring, tools
import agent.runtime as runtime


@pytest.fixture(autouse=True)
def isolate(tmp_path, monkeypatch):
    """Per-test isolation: fresh SQLite store, dry-run on, deterministic policy."""
    monkeypatch.setattr(config, "STATE_DIR", str(tmp_path / "state"))
    monkeypatch.setattr(config, "DRY_RUN", True)
    monkeypatch.setattr(config, "ENABLE_CHART_READS", False)
    monkeypatch.setattr(config, "ENABLE_EXECUTION", False)
    monkeypatch.setattr(config, "RESPECT_MARKET_HOURS", True)
    monkeypatch.setattr(config, "DATA_PROVIDER", "none")
    monkeypatch.setattr(config, "KILL_SWITCH_FILE", str(tmp_path / "kill"))
    monkeypatch.setattr(config, "ALLOWED_SYMBOLS", {"OANDA:XAUUSD", "BINANCE:BTCUSDT"})
    monkeypatch.setattr(config, "ALLOWED_ACTIONS", {"buy", "sell", "info"})
    monkeypatch.setattr(config, "WEBHOOK_SECRET", "")
    monkeypatch.setattr(config, "DAILY_TOKEN_BUDGET", 0)
    monkeypatch.setattr(config, "MIN_RUN_INTERVAL_S", 0)
    # fresh durable store bound to this test's dir
    store.reset_for_tests()
    # reset in-memory counters between tests
    monkeypatch.setattr(budget, "_day", None)
    monkeypatch.setattr(budget, "_tokens_used", 0)
    monkeypatch.setattr(budget, "_last_run_ts", 0.0)
    monkeypatch.setattr(monitoring, "_consecutive_failures", 0)
    yield
    store.reset_for_tests()


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
