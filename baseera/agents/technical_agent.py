"""
وكيل التحليل الفني (Technical Analysis Agent).

المهمة: قراءة السلوك السعري والمؤشرات الفنية (المتوسطات المتحركة، RSI،
MACD، الاتجاه، الدعوم والمقاومات) وإصدار إشارة فنية مع درجة قوة، إضافة
إلى مناطق دخول ووقف خسارة أولية من منظور فني بحت.
"""
from __future__ import annotations

from typing import Any, Dict

from ..data.models import Stock, AgentReport
from .base import BaseAgent


class TechnicalAnalysisAgent(BaseAgent):
    name = "technical"
    agent_ar = "وكيل التحليل الفني"
    mission = "تحليل المؤشرات الفنية (RSI, MACD, المتوسطات) وتحديد الاتجاه والإشارة الفنية"

    def system_prompt(self) -> str:
        return (
            "أنت محلل فني خبير في شركة (بَصيرة كابيتال) لبورصة الكويت. "
            "تقرأ المؤشرات الفنية بدقّة: علاقة السعر بالمتوسطات (20/50/200)، "
            "مستوى RSI (تشبّع شرائي فوق 70 / بيعي تحت 30)، تقاطعات MACD، "
            "الاتجاه العام، والدعوم والمقاومات. تُصدر إشارة فنية موضوعية "
            "ودرجة قوة، وتذكر مناطق الدخول والوقف الفنية دون مبالغة."
        )

    def compute(self, stock: Stock) -> Dict[str, Any]:
        t = stock.technicals
        last = stock.quote.last_price
        score = 0.0
        reasons = []

        # 1) موقع السعر من المتوسطات
        if last > t.sma_20:
            score += 12; reasons.append("السعر فوق متوسط 20 يوماً (زخم قصير إيجابي).")
        else:
            score -= 12; reasons.append("السعر تحت متوسط 20 يوماً (ضعف قصير المدى).")
        if t.sma_50 >= t.sma_200:
            score += 15; reasons.append("متوسط 50 فوق 200 (هيكل صاعد / تقاطع ذهبي).")
        else:
            score -= 15; reasons.append("متوسط 50 تحت 200 (هيكل هابط / تقاطع الموت).")

        # 2) مؤشر القوة النسبية RSI
        if t.rsi_14 >= 70:
            score -= 10; reasons.append(f"RSI {t.rsi_14} تشبّع شرائي — احتمال تصحيح.")
        elif t.rsi_14 <= 30:
            score += 10; reasons.append(f"RSI {t.rsi_14} تشبّع بيعي — فرصة ارتداد.")
        elif 45 <= t.rsi_14 <= 60:
            score += 5; reasons.append(f"RSI {t.rsi_14} في منطقة متوازنة صحية.")

        # 3) MACD
        if t.macd_hist > 0:
            score += 10; reasons.append("هيستوجرام MACD موجب (زخم صاعد).")
        else:
            score -= 10; reasons.append("هيستوجرام MACD سالب (زخم هابط).")

        # 4) الاتجاه العام
        if t.trend == "صاعد":
            score += 12
        elif t.trend == "هابط":
            score -= 12

        score = self._clamp(score)
        # مناطق فنية مبنية على ATR والدعوم/المقاومات
        stop = round(t.support - t.atr_14, 4)
        target = round(t.resistance, 4)
        return {
            "score": round(score, 1),
            "reasons": reasons,
            "entry_zone": f"{round(min(last, t.sma_20), 4)} — {round(last, 4)}",
            "stop_loss": stop,
            "target": target,
        }

    def user_prompt(self, stock: Stock, facts: Dict[str, Any]) -> str:
        t = stock.technicals
        q = stock.quote
        return (
            f"سهم: {q.name_ar} ({q.symbol}) — آخر سعر {q.last_price} د.ك\n"
            f"المتوسطات: SMA20={t.sma_20} | SMA50={t.sma_50} | SMA200={t.sma_200}\n"
            f"RSI(14)={t.rsi_14} | MACD={t.macd} | إشارة MACD={t.macd_signal} | "
            f"هيستوجرام={t.macd_hist}\n"
            f"ATR(14)={t.atr_14} | الدعم={t.support} | المقاومة={t.resistance}\n"
            f"الاتجاه العام: {t.trend}\n"
            "حلّل الوضع الفني وأصدر إشارة ودرجة قوة، واذكر مناطق الدخول والوقف الفنية."
        )

    def heuristic(self, stock: Stock, facts: Dict[str, Any]) -> AgentReport:
        score = facts["score"]
        return AgentReport(
            agent=self.name,
            agent_ar=self.agent_ar,
            signal=self._signal_from_score(score),
            score=score,
            confidence=0.8,
            summary=(
                f"الاتجاه {stock.technicals.trend}، RSI عند {stock.technicals.rsi_14}، "
                f"والدرجة الفنية {score}. منطقة الدخول {facts['entry_zone']} "
                f"ووقف {facts['stop_loss']} وهدف {facts['target']}."
            ),
            highlights=facts["reasons"][:4],
            risks=(
                ["تشبّع شرائي — انتظر تصحيحاً قبل الدخول."]
                if stock.technicals.rsi_14 >= 70 else []
            ),
            raw=facts,
        )
