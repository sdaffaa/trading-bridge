from flask import Flask, request, jsonify
import anthropic
import json
import os

app = Flask(__name__)
client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

@app.route('/webhook', methods=['POST'])
def receive_alert():
    data = request.json
    print(f"\n Alert وصل: {data}")
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=500,
        messages=[{"role": "user", "content": f"حلل هذه الاشارة على XAUUSD: {json.dumps(data)}"}]
    )
    analysis = message.content[0].text
    print(f"Claude: {analysis}")
    return jsonify({"status": "ok", "analysis": analysis})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
