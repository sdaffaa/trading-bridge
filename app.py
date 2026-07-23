"""تطبيق توصيات التداول — Flask backend.

يجمع بيانات سوق حقيقية (Yahoo Finance) + مؤشرات فنية، ويولّد توصية عبر Claude،
ويقدّمها لواجهة ويب عربية.

التشغيل:
    pip install -r requirements.txt
    export ANTHROPIC_API_KEY=...        # اختياري: بدونه يعمل بمحرك القواعد
    python app.py
    # ثم افتح http://localhost:5000
"""

import time

from flask import Flask, jsonify, render_template

from engine import indicators, market_data, recommender, symbols

app = Flask(__name__)

# كاش بسيط في الذاكرة لتقليل الطلبات على المزوّد ونموذج الذكاء
_CACHE = {}
_CACHE_TTL = 120  # ثانية


def _cached(key, producer):
    now = time.time()
    hit = _CACHE.get(key)
    if hit and now - hit["at"] < _CACHE_TTL:
        return hit["value"]
    value = producer()
    _CACHE[key] = {"at": now, "value": value}
    return value


def _build_recommendation(instrument):
    data = market_data.get_candles(instrument["yahoo"], interval="1h", range_="1mo")
    snapshot = indicators.compute(data["candles"])
    snapshot["price"] = round(data["price"], 6)
    rec = recommender.recommend(instrument, snapshot)
    return {
        "instrument": {
            "id": instrument["id"],
            "name_ar": instrument["name_ar"],
            "name_en": instrument["name_en"],
            "category": instrument["category"],
            "decimals": instrument["decimals"],
        },
        "snapshot": snapshot,
        "recommendation": rec,
        "generated_at": int(time.time()),
    }


@app.route("/")
def index():
    return render_template(
        "index.html",
        instruments=symbols.all_instruments(),
        categories=symbols.CATEGORIES,
    )


@app.route("/api/instruments")
def api_instruments():
    return jsonify({
        "instruments": symbols.all_instruments(),
        "categories": symbols.CATEGORIES,
    })


@app.route("/api/recommendation/<symbol_id>")
def api_recommendation(symbol_id):
    instrument = symbols.get(symbol_id)
    if not instrument:
        return jsonify({"error": "أداة غير معروفة"}), 404
    try:
        payload = _cached(symbol_id, lambda: _build_recommendation(instrument))
        return jsonify(payload)
    except market_data.MarketDataError as exc:
        return jsonify({"error": str(exc)}), 502
    except Exception as exc:  # pragma: no cover
        return jsonify({"error": "خطأ غير متوقع: " + str(exc)}), 500


@app.route("/api/health")
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
