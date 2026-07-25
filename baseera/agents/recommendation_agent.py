"""
وكيل التوصية النهائية / مدير الاستثمار (Chief Investment Officer).

المهمة: تجميع تقارير الوكلاء المتخصصين (الفني، المالي، الأخبار، المخاطر،
بيانات السوق)، وموازنتها بأوزان، لإصدار توصية نهائية واضحة (شراء / بيع /
احتفاظ) مع سعر مستهدف، وقف خسارة، أفق زمني، ومسوّغ مكتوب.

هذا الوكيل لا يحلّل البيانات الخام مباشرة؛ بل يوازن آراء الفريق ويحكم.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from ..data.models import Stock, AgentReport, FinalRecommendation
from .base import BaseAgent


# أوزان دمج آراء الوكلاء (المجموع = 1.0)
WEIGHTS = {
    "technical": 0.30,
    "fundamental": 0.32,
    "news": 0.13,
    "risk": 0.15,
    "market_data": 0.10,
}


class RecommendationAgent(BaseAgent):
    name = "cio"
    agent_ar = "مدير الاستثمار (التوصية النهائية)"
    mission = "دمج آراء الفريق وإصدار توصية نهائية بسعر مستهدف ووقف خسارة وأفق زمني"

    def system_prompt(self) -> str:
        return (
            "أنت مدير الاستثمار (CIO) في شركة (بَصيرة كابيتال) لبورصة الكويت. "
            "تستلم تقارير فريقك: التحليل الفني، التحليل المالي، الأخبار والمشاعر، "
            "وإدارة المخاطر، وبيانات السوق. مهمتك موازنة هذه الآراء بحكمة وإصدار "
            "توصية نهائية واضحة (شراء/بيع/احتفاظ) مع سعر مستهدف ووقف خسارة وأفق "
            "زمني ومسوّغ مقنع. توازن بين العائد والمخاطر، ولا تتجاهل رأي إدارة "
            "المخاطر. كن صريحاً ومسؤولاً — هذه ليست نصيحة استثمارية شخصية."
        )

    # ------------------------------------------------------------------
    def combine(self, reports: List[AgentReport]) -> Dict[str, Any]:
        by_name = {r.agent: r for r in reports}
        composite = 0.0
        weight_sum = 0.0
        for name, w in WEIGHTS.items():
            if name in by_name:
                composite += by_name[name].score * w
                weight_sum += w
        composite = composite / weight_sum if weight_sum else 0.0
        confidence = (
            sum(r.confidence for r in reports) / len(reports) if reports else 0.5
        )
        return {"composite": round(composite, 1), "confidence": round(confidence, 2)}

    def decide(self, composite: float) -> (str, str):
        if composite >= 35:
            return "شراء", "عالية"
        if composite >= 12:
            return "شراء", "متوسطة"
        if composite <= -35:
            return "بيع", "عالية"
        if composite <= -12:
            return "بيع", "متوسطة"
        return "احتفاظ", "منخفضة"

    def recommend(self, stock: Stock, reports: List[AgentReport]) -> FinalRecommendation:
        combo = self.combine(reports)
        composite = combo["composite"]
        action, conviction = self.decide(composite)

        tech = next((r for r in reports if r.agent == "technical"), None)
        risk = next((r for r in reports if r.agent == "risk"), None)
        last = stock.quote.last_price

        # سعر مستهدف مبني على الدرجة المجمّعة (حركة متوقعة مقيدة واقعياً)
        expected_move = max(-0.20, min(0.20, composite / 100 * 0.5))
        target = round(last * (1 + expected_move), 4)
        stop_loss = (
            risk.raw.get("stop_loss") if risk and risk.raw else None
        ) or (tech.raw.get("stop_loss") if tech and tech.raw else round(last * 0.95, 4))
        entry = tech.raw.get("entry_zone") if tech and tech.raw else f"{round(last, 4)}"
        horizon = "متوسط المدى (1-3 أشهر)" if action != "احتفاظ" else "مراقبة"

        rationale = self._compose_rationale(stock, reports, composite, action)

        rec = FinalRecommendation(
            symbol=stock.symbol,
            name_ar=stock.name_ar,
            action=action,
            conviction=conviction,
            composite_score=composite,
            confidence=combo["confidence"],
            entry_zone=entry,
            target_price=target,
            stop_loss=stop_loss,
            time_horizon=horizon,
            rationale=rationale,
            agent_reports=reports,
        )

        # إن توفّر LLM، نُثري المسوّغ بصياغة مدير الاستثمار
        if self.client is not None:
            try:
                rec.rationale = self._llm_rationale(stock, reports, rec)
            except Exception:
                pass
        return rec

    def _compose_rationale(self, stock, reports, composite, action) -> str:
        parts = [
            f"الدرجة المجمّعة الموزونة للسهم {composite} مما يدعم توصية «{action}»."
        ]
        for r in reports:
            parts.append(f"— {r.agent_ar}: {r.summary}")
        return "\n".join(parts)

    def _llm_rationale(self, stock: Stock, reports: List[AgentReport],
                       rec: FinalRecommendation) -> str:
        team = "\n".join(
            f"- {r.agent_ar}: إشارة {r.signal}، درجة {r.score}. {r.summary}"
            for r in reports
        )
        prompt = (
            f"سهم: {stock.name_ar} ({stock.symbol}) — سعر {stock.quote.last_price} د.ك\n"
            f"الدرجة المجمّعة: {rec.composite_score} | التوصية المبدئية: {rec.action} "
            f"(قناعة {rec.conviction})\n"
            f"سعر مستهدف: {rec.target_price} | وقف: {rec.stop_loss}\n\n"
            f"تقارير الفريق:\n{team}\n\n"
            "بصفتك مدير الاستثمار، اكتب مسوّغاً نهائياً موجزاً (3-5 جمل) بالعربية "
            "يوازن بين العائد والمخاطر ويبرّر التوصية. لا تضف تنسيق JSON."
        )
        msg = self.client.messages.create(
            model=self.model,
            max_tokens=500,
            system=self.system_prompt(),
            messages=[{"role": "user", "content": prompt}],
        )
        return msg.content[0].text.strip()

    # الوكيل الأساسي يتطلب هذه، لكنه هنا يعمل عبر recommend()
    def compute(self, stock: Stock) -> Dict[str, Any]:  # pragma: no cover
        return {}

    def heuristic(self, stock: Stock, facts: Dict[str, Any]):  # pragma: no cover
        raise NotImplementedError("استخدم recommend() لهذا الوكيل.")

    def user_prompt(self, stock: Stock, facts: Dict[str, Any]) -> str:  # pragma: no cover
        return ""
