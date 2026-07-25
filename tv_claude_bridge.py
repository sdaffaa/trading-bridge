"""
خادم بَصيرة كابيتال (Flask API).

يوفّر واجهة HTTP لشركة التحليل متعددة الوكلاء، مع الحفاظ على مسار
/webhook الأصلي للتوافق مع تنبيهات TradingView.

المسارات:
    GET  /                      معلومات الشركة
    GET  /health                فحص الصحة
    GET  /agents                قائمة الوكلاء ومهامهم
    GET  /symbols               الأسهم المتاحة
    GET  /analyze/<symbol>      تحليل سهم وإصدار توصية (JSON)
    POST /analyze               تحليل سهم عبر body: {"symbol": "KFH", "telegram": true}
    POST /webhook               (توافق قديم) استقبال تنبيه وتحليله
"""
from __future__ import annotations

import os

from flask import Flask, request, jsonify

from baseera.orchestrator import (
    BaseeraCapital,
    telegram_summary,
    format_report,
    COMPANY_NAME,
    COMPANY_TAGLINE,
)

app = Flask(__name__)
firm = BaseeraCapital(live=os.environ.get("BASEERA_LIVE") == "1")

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")


def send_telegram(message: str) -> None:
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram not configured; skipping send.")
        return
    import requests

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    resp = requests.post(
        url, json={"chat_id": str(TELEGRAM_CHAT_ID), "text": message}
    )
    print(f"Telegram response: {resp.status_code} {resp.text}")


def _public(result: dict) -> dict:
    """يزيل الكائنات الداخلية غير القابلة للتسلسل قبل إرجاع JSON."""
    return {k: v for k, v in result.items() if not k.startswith("_")}


@app.route("/", methods=["GET"])
def index():
    return jsonify({
        "company": COMPANY_NAME,
        "tagline": COMPANY_TAGLINE,
        "mode": firm.mode,
        "endpoints": ["/health", "/agents", "/symbols", "/analyze/<symbol>"],
    })


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "mode": firm.mode})


@app.route("/agents", methods=["GET"])
def agents():
    return jsonify({"company": COMPANY_NAME, "agents": firm.roster()})


@app.route("/symbols", methods=["GET"])
def symbols():
    return jsonify({"symbols": firm.list_symbols()})


@app.route("/analyze/<symbol>", methods=["GET"])
def analyze_get(symbol):
    try:
        result = firm.analyze(symbol)
    except KeyError as exc:
        return jsonify({"error": str(exc)}), 404
    return jsonify(_public(result))


@app.route("/analyze", methods=["POST"])
def analyze_post():
    data = request.json or {}
    symbol = data.get("symbol")
    if not symbol:
        return jsonify({"error": "الحقل 'symbol' مطلوب."}), 400
    try:
        result = firm.analyze(symbol)
    except KeyError as exc:
        return jsonify({"error": str(exc)}), 404
    if data.get("telegram"):
        send_telegram(telegram_summary(result))
    return jsonify(_public(result))


@app.route("/webhook", methods=["POST"])
def receive_alert():
    """توافق قديم: تنبيه TradingView يحمل رمز سهم كويتي فيُحلَّل ويُرسل."""
    data = request.json or {}
    print(f"Alert received: {data}")
    symbol = data.get("symbol") or data.get("ticker")
    if not symbol:
        return jsonify({"status": "error", "message": "لا يوجد رمز سهم في التنبيه."}), 400
    try:
        result = firm.analyze(symbol)
    except KeyError as exc:
        return jsonify({"status": "error", "message": str(exc)}), 404
    send_telegram(telegram_summary(result))
    print(format_report(result))
    return jsonify({"status": "ok", "recommendation": _public(result)["recommendation"]})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
