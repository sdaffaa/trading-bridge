"""Central configuration, all from environment variables (never hard-code secrets).

Everything the runtime needs to know lives here so behavior is auditable in one
place. Safe defaults: the agent starts in DRY-RUN and acts on nothing external
until you deliberately set AGENT_DRY_RUN=0.
"""
import os


def _flag(name: str, default: str = "0") -> bool:
    return os.environ.get(name, default).strip().lower() in {"1", "true", "yes", "on"}


def _csv(name: str, default: str) -> set:
    return {x.strip() for x in os.environ.get(name, default).split(",") if x.strip()}


# --- model / reasoning ---
MODEL = os.environ.get("AGENT_MODEL", "claude-opus-4-8")
MAX_TOKENS = int(os.environ.get("AGENT_MAX_TOKENS", "8000"))

# --- safety switches ---
DRY_RUN = _flag("AGENT_DRY_RUN", "1")                 # default: safe
KILL_SWITCH_FILE = os.environ.get("AGENT_KILL_FILE", "/tmp/agent.kill")

# --- policy / validation ---
ALLOWED_SYMBOLS = _csv("AGENT_ALLOWED_SYMBOLS", "OANDA:XAUUSD,BINANCE:BTCUSDT,FX:EURUSD")
ALLOWED_ACTIONS = _csv("AGENT_ALLOWED_ACTIONS", "buy,sell,info")

# --- run limits (reliability envelope) ---
MAX_ITERATIONS = int(os.environ.get("AGENT_MAX_ITERS", "8"))
RUN_TIMEOUT_S = float(os.environ.get("AGENT_TIMEOUT_S", "90"))

# --- persistence (idempotency across restarts) ---
STATE_DIR = os.environ.get("AGENT_STATE_DIR", "/tmp/agent-state")

# --- optional capabilities ---
ENABLE_CHART_READS = _flag("AGENT_ENABLE_CHART_READS", "0")  # drives the TV skill

# --- webhook ---
WEBHOOK_SECRET = os.environ.get("WEBHOOK_SECRET", "")       # optional shared secret
PORT = int(os.environ.get("PORT", "5000"))
HOST = os.environ.get("HOST", "0.0.0.0")

# --- telegram (used only inside the notify side effect) ---
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")


def summary() -> dict:
    """Non-secret view of the active config — safe to log at startup."""
    return {
        "model": MODEL,
        "dry_run": DRY_RUN,
        "kill_switch_file": KILL_SWITCH_FILE,
        "allowed_symbols": sorted(ALLOWED_SYMBOLS),
        "allowed_actions": sorted(ALLOWED_ACTIONS),
        "max_iterations": MAX_ITERATIONS,
        "run_timeout_s": RUN_TIMEOUT_S,
        "enable_chart_reads": ENABLE_CHART_READS,
        "webhook_secret_set": bool(WEBHOOK_SECRET),
        "telegram_configured": bool(TELEGRAM_TOKEN and TELEGRAM_CHAT_ID),
    }
