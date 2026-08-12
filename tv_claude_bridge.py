"""TradingView -> QML detection -> Telegram bridge.

Accepts two payload shapes on POST /webhook:

  * a bar series      {"symbol": "XAUUSD", "tf": "15", "bars": [...]}
    which is run through the QML engine here, and
  * a detected setup  {"symbol": "XAUUSD", "direction": "BULLISH", "qml": ...}
    as fired by pine/qml_quasimodo.pine, which is validated and formatted.

Both require the shared secret in WEBHOOK_SECRET, sent either as the
X-Webhook-Secret header or as a "secret" field in the body.
"""

import hmac
import logging
import os

import requests
from flask import Flask, jsonify, request

from qml.bars import BadPayload, parse_bars
from qml.detector import BEARISH, BULLISH, Config, Setup, latest_setup
from qml.format import format_setup

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s"
)
log = logging.getLogger("tv-bridge")

app = Flask(__name__)

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
WEBHOOK_SECRET = os.environ.get("WEBHOOK_SECRET")

MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-5")
HTTP_TIMEOUT = 10


def _flag(name, default):
    raw = os.environ.get(name)
    if raw is None:
        return default
    return raw.strip().lower() in ("1", "true", "yes", "on")


# Commentary is a garnish on an already-structured setup, so it stays off unless
# there is a key to use.
ENABLE_LLM_COMMENTARY = _flag("ENABLE_LLM_COMMENTARY", bool(ANTHROPIC_API_KEY))


def send_telegram(message):
    if not (TELEGRAM_TOKEN and TELEGRAM_CHAT_ID):
        log.warning("Telegram not configured, skipping send")
        return False

    url = "https://api.telegram.org/bot%s/sendMessage" % TELEGRAM_TOKEN
    try:
        resp = requests.post(
            url,
            json={"chat_id": str(TELEGRAM_CHAT_ID), "text": message},
            timeout=HTTP_TIMEOUT,
        )
    except requests.RequestException as exc:
        log.error("Telegram request failed: %s", exc)
        return False

    if resp.status_code != 200:
        log.error("Telegram returned %s: %s", resp.status_code, resp.text)
        return False
    return True


def add_commentary(setup, symbol, timeframe, body):
    """Ask Claude to comment on the setup. Never fatal — the setup is the payload."""
    if not (ENABLE_LLM_COMMENTARY and ANTHROPIC_API_KEY):
        return None

    try:
        import anthropic

        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        prompt = (
            "A Quasimodo (QML) setup was detected mechanically on %s %s.\n\n%s\n\n"
            "In at most four sentences, comment on how this setup should be "
            "managed. Do not restate the numbers and do not invent levels that "
            "are not listed above." % (symbol, timeframe or "", body)
        )
        message = client.messages.create(
            model=MODEL,
            max_tokens=300,
            messages=[{"role": "user", "content": prompt}],
        )
        return message.content[0].text
    except Exception as exc:  # noqa: BLE001 - commentary must never break the alert
        log.error("Commentary failed: %s", exc)
        return None


def _authorized(payload):
    if not WEBHOOK_SECRET:
        return False
    supplied = request.headers.get("X-Webhook-Secret")
    if supplied is None and isinstance(payload, dict):
        supplied = payload.get("secret")
    return isinstance(supplied, str) and hmac.compare_digest(supplied, WEBHOOK_SECRET)


def _digits(payload, reference):
    if isinstance(payload, dict) and payload.get("digits") is not None:
        try:
            return int(payload["digits"])
        except (TypeError, ValueError):
            pass
    # Gold and indices quote to 2dp, FX pairs to 5 — magnitude is a good enough tell.
    return 5 if reference is not None and abs(reference) < 20 else 2


_SETUP_FIELDS = ("direction", "qml", "entry", "sl", "tp")


def _setup_from_payload(payload):
    """Rebuild a Setup from a pre-detected alert (the Pine indicator's output)."""
    missing = [f for f in _SETUP_FIELDS if payload.get(f) is None]
    if missing:
        raise BadPayload("setup payload is missing: %s" % ", ".join(missing))

    direction = str(payload["direction"]).upper()
    if direction not in (BULLISH, BEARISH):
        raise BadPayload("direction must be BULLISH or BEARISH, got %r" % direction)

    def number(name, required=True):
        value = payload.get(name)
        if value is None:
            if required:
                raise BadPayload("missing '%s'" % name)
            return None
        try:
            return float(value)
        except (TypeError, ValueError):
            raise BadPayload("'%s' is not a number: %r" % (name, value))

    entry = number("entry")
    sl = number("sl")
    tp = number("tp")
    risk = abs(entry - sl)
    rr = abs(tp - entry) / risk if risk > 0 else None

    return Setup(
        direction=direction,
        status=str(payload.get("status", "TRIGGERED")).upper(),
        qml=number("qml"),
        choch=number("choch", required=False),
        head=number("head", required=False),
        entry=entry,
        sl=sl,
        tp=tp,
        rr=rr,
        meets_min_rr=rr is not None and rr >= Config().min_rr,
    )


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


@app.route("/webhook", methods=["POST"])
def receive_alert():
    payload = request.get_json(silent=True)
    if payload is None:
        return jsonify({"error": "body must be JSON"}), 400

    if not WEBHOOK_SECRET:
        log.error("WEBHOOK_SECRET is not set, refusing to process alerts")
        return jsonify({"error": "server is missing WEBHOOK_SECRET"}), 503
    if not _authorized(payload):
        log.warning("Rejected alert with a bad or missing secret")
        return jsonify({"error": "unauthorized"}), 401

    symbol = str(payload.get("symbol", "?")) if isinstance(payload, dict) else "?"
    timeframe = payload.get("tf") if isinstance(payload, dict) else None

    try:
        if isinstance(payload, dict) and "bars" in payload:
            bars = parse_bars(payload)
            setup = latest_setup(bars, Config())
            if setup is None:
                log.info("No QML setup in %d bars of %s", len(bars), symbol)
                return jsonify({"status": "ok", "setup": None})
        elif isinstance(payload, dict):
            setup = _setup_from_payload(payload)
        else:
            raise BadPayload("payload must be a JSON object")
    except BadPayload as exc:
        log.warning("Bad payload: %s", exc)
        return jsonify({"error": str(exc)}), 400

    body = format_setup(setup, symbol, timeframe, _digits(payload, setup.entry))
    log.info("Setup: %s %s %s", symbol, setup.direction, setup.status)

    commentary = add_commentary(setup, symbol, timeframe, body)
    if commentary:
        body = "%s\n\n%s" % (body, commentary)

    delivered = send_telegram(body)
    return jsonify(
        {"status": "ok", "delivered": delivered, "setup": setup.as_dict()}
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
