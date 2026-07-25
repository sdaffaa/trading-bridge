"""
وكيل الأخبار والمشاعر (News & Sentiment Agent).

المهمة: قراءة الأخبار المرتبطة بالسهم/القطاع واستخلاص المشاعر السوقية
(إيجابية/سلبية/محايدة) وأثرها المحتمل على السهم، ثم إصدار درجة مشاعر.
"""
from __future__ import annotations

from typing import Any, Dict, List

from ..data.models import Stock, AgentReport
from .base import BaseAgent


# كلمات دالة لتقدير المشاعر في الوضع الاحتياطي
_POSITIVE = ["نمو", "ارتفاع", "قوي", "قوية", "تحسّن", "تحسن", "يدعم", "جذّاب",
             "جذاب", "زيادة", "مستقر", "استقرار", "توسّع", "توسع", "أرباح"]
_NEGATIVE = ["تراجع", "ضغوط", "ضعف", "انخفاض", "خسارة", "مخاطر", "تقلبات",
             "هبوط", "تباطؤ", "ديون", "تأثير سلبي"]


class NewsSentimentAgent(BaseAgent):
    name = "news"
    agent_ar = "وكيل الأخبار والمشاعر"
    mission = "قراءة الأخبار واستخلاص المشاعر السوقية وأثرها على السهم"

    def system_prompt(self) -> str:
        return (
            "أنت محلل أخبار ومشاعر سوق في شركة (بَصيرة كابيتال) لبورصة الكويت. "
            "تقرأ عناوين وملخّصات الأخبار المرتبطة بالسهم وقطاعه، وتحدّد اتجاه "
            "المشاعر (إيجابي/سلبي/محايد) وقوّته وأثره المحتمل على السعر. "
            "تتجنّب المبالغة وتميّز بين الضجيج والأخبار الجوهرية. تُصدر درجة مشاعر."
        )

    def compute(self, stock: Stock) -> Dict[str, Any]:
        pos = neg = 0
        scored: List[Dict[str, Any]] = []
        for item in stock.news:
            text = f"{item.headline} {item.summary}"
            p = sum(1 for w in _POSITIVE if w in text)
            n = sum(1 for w in _NEGATIVE if w in text)
            pos += p; neg += n
            polarity = "إيجابي" if p > n else "سلبي" if n > p else "محايد"
            scored.append({"headline": item.headline, "polarity": polarity})
        total = pos + neg
        if total == 0:
            score = 0.0
        else:
            score = self._clamp((pos - neg) / total * 60)
        return {"score": round(score, 1), "pos": pos, "neg": neg, "items": scored}

    def user_prompt(self, stock: Stock, facts: Dict[str, Any]) -> str:
        lines = [f"سهم: {stock.name_ar} ({stock.symbol}) — القطاع: {stock.quote.sector}",
                 "الأخبار المتاحة:"]
        for i, item in enumerate(stock.news, 1):
            lines.append(f"{i}. {item.headline} — {item.summary} ({item.source}, {item.date})")
        lines.append("حلّل المشاعر العامة وأثرها المحتمل على السهم، وأصدر درجة مشاعر.")
        return "\n".join(lines)

    def heuristic(self, stock: Stock, facts: Dict[str, Any]) -> AgentReport:
        score = facts["score"]
        highlights = [
            f"«{it['headline']}» — انطباع {it['polarity']}."
            for it in facts["items"][:3]
        ]
        return AgentReport(
            agent=self.name,
            agent_ar=self.agent_ar,
            signal=self._signal_from_score(score),
            score=score,
            confidence=0.65,
            summary=(
                f"المشاعر الإخبارية {'إيجابية' if score > 10 else 'سلبية' if score < -10 else 'محايدة'} "
                f"(إشارات إيجابية {facts['pos']} مقابل سلبية {facts['neg']})."
            ),
            highlights=highlights,
            risks=(["تدفق الأخبار قد يتغيّر سريعاً ويؤثر على المشاعر."]
                   if abs(score) < 10 else []),
            raw=facts,
        )
