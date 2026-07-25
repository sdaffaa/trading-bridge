"""
وكيل بيانات السوق (Market Data Agent).

المهمة: جمع بيانات السهم اللحظية والتأكد من جودتها واكتمالها، وتقديم
لقطة سوقية موجزة (السعر، التغير، السيولة، الموقع ضمن مدى 52 أسبوعاً)
تُشكّل الأساس الذي يبني عليه بقية الفريق تحليلهم.

هذا الوكيل لا يُصدر توصية شراء/بيع؛ دوره ضبط الحقائق وتقييم السيولة
وجودة البيانات فقط.
"""
from __future__ import annotations

from typing import Any, Dict

from ..data.models import Stock, AgentReport
from .base import BaseAgent


class MarketDataAgent(BaseAgent):
    name = "market_data"
    agent_ar = "وكيل بيانات السوق"
    mission = "جمع بيانات السهم اللحظية، تقييم السيولة، والتحقق من جودة البيانات"

    def system_prompt(self) -> str:
        return (
            "أنت محلل بيانات سوق في شركة (بَصيرة كابيتال) متخصصة في بورصة الكويت. "
            "مهمتك تلخيص الحالة السوقية اللحظية للسهم بدقّة: السعر، التغير، حجم "
            "وقيمة التداول، والموقع ضمن مدى 52 أسبوعاً، وتقييم السيولة وجودة "
            "البيانات. لا تُصدر توصية استثمار — فقط حقائق ومؤشرات سيولة. "
            "الدرجة تعكس مدى صحّة/دعم البيانات لاتخاذ قرار (سيولة عالية = درجة أعلى)."
        )

    def compute(self, stock: Stock) -> Dict[str, Any]:
        q = stock.quote
        rng = q.week52_high - q.week52_low
        pos_in_range = ((q.last_price - q.week52_low) / rng * 100) if rng else 50.0
        # السيولة: قيمة تداول أعلى من مليون دينار تُعدّ سيولة صحية
        liquidity_score = self._clamp((q.value_traded / 1_000_000 - 1) * 15, -40, 60)
        return {
            "position_in_52w_range_pct": round(pos_in_range, 1),
            "value_traded_kwd": q.value_traded,
            "volume": q.volume,
            "liquidity_score": round(liquidity_score, 1),
        }

    def user_prompt(self, stock: Stock, facts: Dict[str, Any]) -> str:
        q = stock.quote
        return (
            f"سهم: {q.name_ar} ({q.symbol}) — القطاع: {q.sector}\n"
            f"آخر سعر: {q.last_price} د.ك | التغير: {q.change} ({q.change_pct}%)\n"
            f"حجم التداول: {q.volume:,} سهم | قيمة التداول: {q.value_traded:,.0f} د.ك\n"
            f"أعلى/أدنى اليوم: {q.day_high} / {q.day_low}\n"
            f"مدى 52 أسبوعاً: {q.week52_low} — {q.week52_high} "
            f"(الموقع الحالي: {facts['position_in_52w_range_pct']}% من المدى)\n"
            "لخّص الحالة السوقية وقيّم السيولة وجودة البيانات."
        )

    def heuristic(self, stock: Stock, facts: Dict[str, Any]) -> AgentReport:
        q = stock.quote
        score = facts["liquidity_score"]
        highlights = [
            f"قيمة التداول {q.value_traded:,.0f} د.ك — "
            + ("سيولة صحية." if q.value_traded > 1_000_000 else "سيولة محدودة."),
            f"السهم عند {facts['position_in_52w_range_pct']}% من مدى 52 أسبوعاً.",
            f"التغير اليومي {q.change_pct}%.",
        ]
        risks = []
        if q.value_traded < 500_000:
            risks.append("سيولة منخفضة قد تصعّب الدخول/الخروج بأحجام كبيرة.")
        return AgentReport(
            agent=self.name,
            agent_ar=self.agent_ar,
            signal=self._signal_from_score(score),
            score=round(score, 1),
            confidence=0.9,
            summary=(
                f"{q.name_ar} يتداول عند {q.last_price} د.ك بتغير {q.change_pct}% "
                f"وقيمة تداول {q.value_traded:,.0f} د.ك."
            ),
            highlights=highlights,
            risks=risks,
            raw=facts,
        )
