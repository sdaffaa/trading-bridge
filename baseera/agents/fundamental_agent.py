"""
وكيل التحليل المالي / الأساسي (Fundamental Analysis Agent).

المهمة: قراءة القوائم والنِسب المالية (مكرر الربحية P/E، مكرر القيمة
الدفترية P/B، العائد على حقوق الملكية ROE، هامش الربح، المديونية،
عائد التوزيعات، ونمو الإيرادات والأرباح) لتقييم جاذبية السهم من حيث
القيمة والجودة والنمو، وإصدار درجة أساسية.
"""
from __future__ import annotations

from typing import Any, Dict

from ..data.models import Stock, AgentReport
from .base import BaseAgent


class FundamentalAnalysisAgent(BaseAgent):
    name = "fundamental"
    agent_ar = "وكيل التحليل المالي"
    mission = "قراءة النِسب المالية (P/E, P/B, ROE, المديونية, التوزيعات) وتقييم القيمة والجودة"

    def system_prompt(self) -> str:
        return (
            "أنت محلل مالي أساسي في شركة (بَصيرة كابيتال) لبورصة الكويت. "
            "تقرأ القوائم والنِسب المالية لتقييم السهم من ثلاث زوايا: القيمة "
            "(P/E, P/B)، الجودة (ROE، هامش الربح، المديونية)، والنمو (نمو "
            "الإيرادات والأرباح، وجاذبية التوزيعات). تراعي طبيعة القطاع "
            "(البنوك مثلاً تُقيّم بمكرر أعلى). تُصدر درجة أساسية موضوعية "
            "وتبرزّ نقاط القوة والمخاطر المالية."
        )

    def compute(self, stock: Stock) -> Dict[str, Any]:
        f = stock.financials
        score = 0.0
        reasons, risks = [], []

        # التقييم (القيمة)
        if f.pe_ratio and f.pe_ratio < 12:
            score += 15; reasons.append(f"مكرر ربحية منخفض ({f.pe_ratio}) — تقييم جذّاب.")
        elif f.pe_ratio > 25:
            score -= 12; risks.append(f"مكرر ربحية مرتفع ({f.pe_ratio}) — تقييم مكلف.")
        if f.pb_ratio and f.pb_ratio < 1.2:
            score += 8; reasons.append(f"مكرر قيمة دفترية {f.pb_ratio} قرب القيمة العادلة.")
        elif f.pb_ratio > 4:
            score -= 6; risks.append(f"مكرر قيمة دفترية مرتفع ({f.pb_ratio}).")

        # الجودة
        if f.roe >= 15:
            score += 15; reasons.append(f"عائد على حقوق الملكية مرتفع ({f.roe}%) — جودة تشغيلية.")
        elif f.roe < 6:
            score -= 10; risks.append(f"عائد على حقوق الملكية ضعيف ({f.roe}%).")
        if f.net_margin >= 25:
            score += 8; reasons.append(f"هامش صافي ربح قوي ({f.net_margin}%).")
        if f.debt_to_equity > 1.5:
            score -= 10; risks.append(f"مديونية مرتفعة (D/E={f.debt_to_equity}).")
        elif f.debt_to_equity <= 0.5:
            score += 5; reasons.append("مركز مالي متين ومديونية منخفضة.")

        # النمو والدخل
        if f.profit_growth >= 10:
            score += 12; reasons.append(f"نمو أرباح قوي ({f.profit_growth}%).")
        elif f.profit_growth < 0:
            score -= 12; risks.append(f"تراجع في الأرباح ({f.profit_growth}%).")
        if f.dividend_yield >= 4:
            score += 8; reasons.append(f"عائد توزيعات جذّاب ({f.dividend_yield}%).")

        score = self._clamp(score)
        return {"score": round(score, 1), "reasons": reasons, "risks": risks}

    def user_prompt(self, stock: Stock, facts: Dict[str, Any]) -> str:
        f = stock.financials
        q = stock.quote
        return (
            f"سهم: {q.name_ar} ({q.symbol}) — القطاع: {q.sector}\n"
            f"القيمة السوقية: {f.market_cap} مليون د.ك | ربحية السهم: {f.eps}\n"
            f"مكرر الربحية P/E={f.pe_ratio} | مكرر القيمة الدفترية P/B={f.pb_ratio}\n"
            f"ROE={f.roe}% | هامش صافي الربح={f.net_margin}% | "
            f"الدين/حقوق الملكية={f.debt_to_equity}\n"
            f"عائد التوزيعات={f.dividend_yield}% | نمو الإيرادات={f.revenue_growth}% | "
            f"نمو الأرباح={f.profit_growth}%\n"
            "قيّم السهم أساسياً من حيث القيمة والجودة والنمو، وأصدر درجة."
        )

    def heuristic(self, stock: Stock, facts: Dict[str, Any]) -> AgentReport:
        score = facts["score"]
        f = stock.financials
        return AgentReport(
            agent=self.name,
            agent_ar=self.agent_ar,
            signal=self._signal_from_score(score),
            score=score,
            confidence=0.82,
            summary=(
                f"P/E={f.pe_ratio}, ROE={f.roe}%, نمو أرباح={f.profit_growth}%, "
                f"توزيعات={f.dividend_yield}% — الدرجة الأساسية {score}."
            ),
            highlights=facts["reasons"][:4],
            risks=facts["risks"][:4],
            raw=facts,
        )
