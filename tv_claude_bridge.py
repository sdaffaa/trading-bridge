from flask import Flask, request, jsonify
import anthropic
import json
import os
import requests

app = Flask(__name__)
client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

def send_telegram(message):
    url = "https://api.telegram.org/bot" + str(TELEGRAM_TOKEN) + "/sendMessage"
    resp = requests.post(url, json={"chat_id": str(TELEGRAM_CHAT_ID), "text": message})
    print("Telegram response: " + str(resp.status_code) + " " + resp.text)

@app.route('/webhook', methods=['POST'])
def receive_alert():
    data = request.json
    print("Alert received: " + str(data))
    prompt = "Analyze this XAUUSD signal: " + json.dumps(data)
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}]
    )
    analysis = message.content[0].text
    print("Analysis done, sending to Telegram...")
    send_telegram("XAUUSD Alert\n\n" + analysis)
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
