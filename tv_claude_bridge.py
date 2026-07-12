from flask import Flask, request, jsonify
import anthropic
import json
import os
import requests

app = Flask(__name__)
client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

DEFAULT_SYMBOL = os.environ.get("DEFAULT_SYMBOL", "EURUSD")

def send_telegram(message):
    url = "https://api.telegram.org/bot" + str(TELEGRAM_TOKEN) + "/sendMessage"
    resp = requests.post(url, json={"chat_id": str(TELEGRAM_CHAT_ID), "text": message})
    print("Telegram response: " + str(resp.status_code) + " " + resp.text)

def parse_alert(req):
    # TradingView sends alerts as text/plain by default, so don't rely on
    # request.json (which requires an application/json content-type).
    data = req.get_json(silent=True)
    if data is None:
        raw = req.get_data(as_text=True).strip()
        try:
            data = json.loads(raw)
        except (ValueError, TypeError):
            data = {"raw": raw} if raw else {}
    return data

def extract_symbol(data):
    if isinstance(data, dict):
        for key in ("ticker", "symbol", "pair"):
            val = data.get(key)
            if val:
                return str(val).upper().replace("/", "")
    return DEFAULT_SYMBOL

@app.route('/webhook', methods=['POST'])
def receive_alert():
    data = parse_alert(request)
    print("Alert received: " + str(data))
    symbol = extract_symbol(data)
    prompt = "Analyze this " + symbol + " signal: " + json.dumps(data)
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}]
    )
    analysis = message.content[0].text
    print("Analysis done, sending to Telegram...")
    send_telegram(symbol + " Alert\n\n" + analysis)
    return jsonify({"status": "ok", "symbol": symbol})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
