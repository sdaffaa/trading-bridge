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
# The per-school chart reads (the bulk of the calls) run on a cheaper model; only
# the coordinator that makes the final decision uses AGENT_MODEL. This is the main
# cost lever — set to claude-opus-4-8 to disable, or claude-haiku-4-5 for cheapest.
VISION_MARKUP_MODEL = os.environ.get("AGENT_VISION_MARKUP_MODEL", "claude-sonnet-5")

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

# --- scheduled (autonomous) trigger: the system analyzes on its own, no webhook ---
SCHEDULE_SECONDS = int(os.environ.get("AGENT_SCHEDULE_SECONDS", "0"))  # 0 = off
SCHEDULE_SYMBOLS = _csv("AGENT_SCHEDULE_SYMBOLS", "")                    # empty = first allowed
SCHEDULE_TIMEFRAME = os.environ.get("AGENT_SCHEDULE_TIMEFRAME", "240")


def schedule_symbols() -> set:
    """Symbols the scheduler analyzes. If AGENT_SCHEDULE_SYMBOLS is unset, default
    to ALL allowed exchange-prefixed symbols (e.g. OANDA:XAUUSD) — the bare aliases
    like XAUUSD are skipped since the chart needs the exchange-qualified symbol."""
    if SCHEDULE_SYMBOLS:
        return SCHEDULE_SYMBOLS
    prefixed = {s for s in ALLOWED_SYMBOLS if ":" in s}
    return prefixed or set(sorted(ALLOWED_SYMBOLS)[:1])

# --- webhook ---
WEBHOOK_SECRET = os.environ.get("WEBHOOK_SECRET", "")       # optional shared secret
PORT = int(os.environ.get("PORT", "5000"))
HOST = os.environ.get("HOST", "0.0.0.0")

# --- telegram (used only inside the notify side effect) ---
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

# --- live market data (so the scheduler analyzes real data, no browser) ---
# provider: "none" | "fmp" | "generic"
DATA_PROVIDER = os.environ.get("AGENT_DATA_PROVIDER", "none").strip().lower()
DATA_API_KEY = os.environ.get("AGENT_DATA_API_KEY", "")
# generic provider: an HTTPS URL with {symbol}, and a dot-path to the price
DATA_URL_TEMPLATE = os.environ.get("AGENT_DATA_URL_TEMPLATE", "")
DATA_PRICE_PATH = os.environ.get("AGENT_DATA_PRICE_PATH", "price")
DATA_TIMEOUT_S = float(os.environ.get("AGENT_DATA_TIMEOUT_S", "10"))

# --- market-hours awareness (skip scheduled runs when the market is closed) ---
RESPECT_MARKET_HOURS = _flag("AGENT_RESPECT_MARKET_HOURS", "1")

# --- methodology the agent analyzes with (ict | smc | volume_profile | footprint | confluence) ---
METHODOLOGY = _csv("AGENT_METHODOLOGY", "confluence")

# --- notifications: by default only ping on actionable setups, not every no_trade ---
NOTIFY_ON_NO_TRADE = _flag("AGENT_NOTIFY_ON_NO_TRADE", "0")

# --- risk management (the agent defines the trade + appropriate risk) ---
ACCOUNT_BALANCE = float(os.environ.get("AGENT_ACCOUNT_BALANCE", "0"))  # 0 = unknown
RISK_PERCENT = float(os.environ.get("AGENT_RISK_PERCENT", "1.0"))      # % risked per trade
MIN_RR = float(os.environ.get("AGENT_MIN_RR", "2.0"))                  # min reward:risk

# --- vision mode: agents open the chart, screenshot it, and mark it up visually ---
VISION_MODE = _flag("AGENT_VISION_MODE", "0")
CHROMIUM_PATH = os.environ.get("PLAYWRIGHT_BROWSERS_PATH", "/opt/pw-browsers") + "/chromium"
CHART_URL_TEMPLATE = os.environ.get(
    "AGENT_CHART_URL",
    "https://www.tradingview.com/chart/?symbol={symbol}&interval={interval}")
SHOT_WAIT_MS = int(os.environ.get("AGENT_SHOT_WAIT_MS", "10000"))
# which schools each get their own vision markup agent
VISION_SCHOOLS = _csv("AGENT_VISION_SCHOOLS", "ict,smc,volume_profile,footprint")
# multi-timeframe top-down: analyze the higher TF for bias, then the lower TF for
# the entry. Order matters (higher first). Empty = single TF (the alert's own).
VISION_TIMEFRAMES = [x.strip() for x in
                     os.environ.get("AGENT_VISION_TIMEFRAMES", "240,15").split(",")
                     if x.strip()]

# --- cost / rate controls ---
DAILY_TOKEN_BUDGET = int(os.environ.get("AGENT_DAILY_TOKEN_BUDGET", "0"))  # 0 = unlimited
MIN_RUN_INTERVAL_S = float(os.environ.get("AGENT_MIN_RUN_INTERVAL_S", "0"))  # throttle

# --- self-monitoring / failure alerting ---
ALERT_ON_FAILURE = _flag("AGENT_ALERT_ON_FAILURE", "1")
ALERT_FAILS_THRESHOLD = int(os.environ.get("AGENT_ALERT_FAILS_THRESHOLD", "3"))
HEARTBEAT_MAX_SILENCE_S = int(os.environ.get("AGENT_HEARTBEAT_MAX_SILENCE_S", "0"))  # 0=off

# --- optional execution layer (place orders) — OFF by default, deliberately ---
ENABLE_EXECUTION = _flag("AGENT_ENABLE_EXECUTION", "0")
BROKER = os.environ.get("AGENT_BROKER", "paper").strip().lower()  # "paper" | ...
MAX_POSITION_SIZE = float(os.environ.get("AGENT_MAX_POSITION_SIZE", "0.01"))
MAX_OPEN_POSITIONS = int(os.environ.get("AGENT_MAX_OPEN_POSITIONS", "1"))
MIN_CONFIDENCE_TO_TRADE = float(os.environ.get("AGENT_MIN_CONFIDENCE_TO_TRADE", "0.7"))


def summary() -> dict:
    """Non-secret view of the active config — safe to log at startup."""
    return {
        "model": MODEL,
        "vision_markup_model": VISION_MARKUP_MODEL,
        "dry_run": DRY_RUN,
        "kill_switch_file": KILL_SWITCH_FILE,
        "allowed_symbols": sorted(ALLOWED_SYMBOLS),
        "allowed_actions": sorted(ALLOWED_ACTIONS),
        "max_iterations": MAX_ITERATIONS,
        "run_timeout_s": RUN_TIMEOUT_S,
        "enable_chart_reads": ENABLE_CHART_READS,
        "webhook_secret_set": bool(WEBHOOK_SECRET),
        "telegram_configured": bool(TELEGRAM_TOKEN and TELEGRAM_CHAT_ID),
        "schedule_seconds": SCHEDULE_SECONDS,
        "schedule_symbols": sorted(schedule_symbols()) if SCHEDULE_SECONDS > 0 else [],
        "schedule_timeframe": SCHEDULE_TIMEFRAME,
        "data_provider": DATA_PROVIDER,
        "methodology": sorted(METHODOLOGY),
        "respect_market_hours": RESPECT_MARKET_HOURS,
        "daily_token_budget": DAILY_TOKEN_BUDGET,
        "min_run_interval_s": MIN_RUN_INTERVAL_S,
        "alert_on_failure": ALERT_ON_FAILURE,
        "heartbeat_max_silence_s": HEARTBEAT_MAX_SILENCE_S,
        "enable_execution": ENABLE_EXECUTION,
        "broker": BROKER if ENABLE_EXECUTION else None,
        "vision_mode": VISION_MODE,
        "vision_schools": sorted(VISION_SCHOOLS) if VISION_MODE else [],
        "vision_timeframes": VISION_TIMEFRAMES if VISION_MODE else [],
        "account_balance_set": ACCOUNT_BALANCE > 0,
        "risk_percent": RISK_PERCENT,
        "min_rr": MIN_RR,
    }
