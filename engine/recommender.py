"""Turn a market snapshot into a structured trading recommendation.

Primary path: Claude (claude-opus-4-8) reads the real indicators and returns a
structured JSON recommendation with Arabic reasoning, grounded on ATR-based
entry/stop/target suggestions the engine computes.

Fallback path: if the Anthropic API is unavailable (no key, network error), a
transparent rule-based recommendation is used instead so the app still works.
"""

import json
import os

try:
    import anthropic
except ImportError:  # pragma: no cover
    anthropic = None

MODEL = os.environ.get("CLAUDE_MODEL", "claude-opus-4-8")

_RECOMMENDATION_SCHEMA = {
    "type": "object",
    "properties": {
        "direction": {"type": "string", "enum": ["BUY", "SELL", "NEUTRAL"]},
        "confidence": {"type": "integer"},
        "entry": {"type": "number"},
        "stop_loss": {"type": "number"},
        "take_profit_1": {"type": "number"},
        "take_profit_2": {"type": "number"},
        "timeframe": {"type": "string"},
        "summary_ar": {"type": "string"},
        "reasons_ar": {"type": "array", "items": {"type": "string"}},
        "risk_note_ar": {"type": "string"},
    },
    "required": [
        "direction", "confidence", "entry", "stop_loss",
        "take_profit_1", "take_profit_2", "timeframe",
        "summary_ar", "reasons_ar", "risk_note_ar",
    ],
    "additionalProperties": False,
}

_client = None


def _get_client():
    global _client
    if _client is not None:
        return _client
    if anthropic is None or not os.environ.get("ANTHROPIC_API_KEY"):
        return None
    _client = anthropic.Anthropic()
    return _client


def _atr_levels(snapshot, direction):
    """Compute sensible entry/SL/TP levels from ATR to ground the model."""
    price = snapshot["price"]
    atr = snapshot.get("atr14") or (price * 0.005)
    if direction == "BUY":
        return {
            "entry": price,
            "stop_loss": price - 1.5 * atr,
            "take_profit_1": price + 1.5 * atr,
            "take_profit_2": price + 3.0 * atr,
        }
    if direction == "SELL":
        return {
            "entry": price,
            "stop_loss": price + 1.5 * atr,
            "take_profit_1": price - 1.5 * atr,
            "take_profit_2": price - 3.0 * atr,
        }
    return {
        "entry": price,
        "stop_loss": price - 1.5 * atr,
        "take_profit_1": price + 1.5 * atr,
        "take_profit_2": price + 3.0 * atr,
    }


def _bias(snapshot):
    """Rule-based directional bias from indicators. Returns (direction, score)."""
    score = 0
    trend = snapshot.get("trend")
    rsi = snapshot.get("rsi14")
    momentum = snapshot.get("momentum_pct") or 0
    price = snapshot["price"]
    ema50 = snapshot.get("ema50")

    if trend == "up":
        score += 2
    elif trend == "down":
        score -= 2

    if ema50:
        score += 1 if price > ema50 else -1

    if rsi is not None:
        if rsi < 30:
            score += 2          # oversold -> potential bounce
        elif rsi > 70:
            score -= 2          # overbought -> potential pullback
        elif rsi > 55:
            score += 1
        elif rsi < 45:
            score -= 1

    if momentum > 0.5:
        score += 1
    elif momentum < -0.5:
        score -= 1

    if score >= 2:
        return "BUY", score
    if score <= -2:
        return "SELL", score
    return "NEUTRAL", score


def _fallback(instrument, snapshot):
    direction, score = _bias(snapshot)
    levels = _atr_levels(snapshot, direction)
    confidence = min(90, 45 + abs(score) * 9)

    reasons = []
    trend_ar = {"up": "الاتجاه صاعد", "down": "الاتجاه هابط", "neutral": "الاتجاه عرضي"}
    reasons.append(trend_ar.get(snapshot.get("trend"), "الاتجاه عرضي") +
                   " حسب ترتيب المتوسطات المتحركة.")
    if snapshot.get("rsi14") is not None:
        reasons.append("مؤشر RSI عند " + str(snapshot["rsi14"]) + ".")
    reasons.append("الزخم الأخير " + str(snapshot.get("momentum_pct")) + "%.")

    summary = {
        "BUY": "إشارة شراء محتملة بناءً على المؤشرات الفنية.",
        "SELL": "إشارة بيع محتملة بناءً على المؤشرات الفنية.",
        "NEUTRAL": "لا توجد إشارة واضحة حالياً، يُفضّل الانتظار.",
    }[direction]

    return {
        "direction": direction,
        "confidence": confidence,
        "entry": round(levels["entry"], 6),
        "stop_loss": round(levels["stop_loss"], 6),
        "take_profit_1": round(levels["take_profit_1"], 6),
        "take_profit_2": round(levels["take_profit_2"], 6),
        "timeframe": "ساعة (H1)",
        "summary_ar": summary,
        "reasons_ar": reasons,
        "risk_note_ar": "التوصيات لأغراض تعليمية فقط وليست نصيحة استثمارية. التزم بإدارة رأس المال.",
        "engine": "rules",
    }


def _prompt(instrument, snapshot, levels_by_dir):
    return (
        "أنت محلل فني محترف في الأسواق المالية. حلّل بيانات الأداة التالية وأعطِ "
        "توصية تداول واحدة واضحة (شراء/بيع/محايد) للمضاربة على فريم الساعة.\n\n"
        f"الأداة: {instrument['name_ar']} ({instrument['name_en']} / {instrument['id']})\n"
        f"السعر الحالي: {snapshot['price']}\n"
        f"المؤشرات الفنية:\n{json.dumps(snapshot, ensure_ascii=False, indent=2)}\n\n"
        "مستويات مقترحة محسوبة من ATR (استخدمها كمرجع ونقّحها إن لزم):\n"
        f"{json.dumps(levels_by_dir, ensure_ascii=False, indent=2)}\n\n"
        "التعليمات:\n"
        "- اختر الاتجاه الأنسب بناءً على المؤشرات (لا تجبر إشارة إن كان السوق عرضياً).\n"
        "- حدّد دخول، وقف خسارة، وهدفين واقعيين ومتناسقين مع الاتجاه المختار.\n"
        "- confidence رقم من 0 إلى 100 يعكس قوة الإشارة.\n"
        "- summary_ar جملة مختصرة، reasons_ar نقاط فنية موجزة، risk_note_ar تنبيه مخاطر.\n"
        "- كل النصوص باللغة العربية. أرقام الأسعار أرقام فقط بدون رموز عملات.\n"
    )


def recommend(instrument, snapshot):
    """Return a structured recommendation dict for the instrument."""
    client = _get_client()
    if client is None:
        return _fallback(instrument, snapshot)

    levels_by_dir = {
        "BUY": _atr_levels(snapshot, "BUY"),
        "SELL": _atr_levels(snapshot, "SELL"),
    }
    try:
        resp = client.messages.create(
            model=MODEL,
            max_tokens=1200,
            output_config={"format": {"type": "json_schema", "schema": _RECOMMENDATION_SCHEMA}},
            messages=[{"role": "user", "content": _prompt(instrument, snapshot, levels_by_dir)}],
        )
        text = next((b.text for b in resp.content if b.type == "text"), None)
        if not text:
            return _fallback(instrument, snapshot)
        rec = json.loads(text)
        rec["engine"] = "ai"
        # clamp confidence defensively
        rec["confidence"] = max(0, min(100, int(rec.get("confidence", 50))))
        return rec
    except Exception:
        # any API/parse failure -> transparent rule-based recommendation
        return _fallback(instrument, snapshot)
