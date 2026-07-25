"""
وكيل إدارة المخاطر (Risk Management Agent).

المهمة: قياس مخاطر السهم (التقلب عبر ATR، معامل بيتا، المديونية،
السيولة، وبُعد السعر عن الدعم) واقتراح حجم مركز مناسب ووقف خسارة،
وإصدار درجة مخاطر (كلما ارتفعت المخاطر، انخفضت الدرجة).
"""
from __future__ import annotations

from typing import Any, Dict

from ..data.models import Stock, AgentReport
from .base import BaseAgent


class RiskManagementAgent(BaseAgent):
    name = "risk"
    agent_ar = "وكيل إدارة المخاطر"
    mission = "قياس التقلب والمخاطر واقتراح حجم المركز ووقف الخسارة"

    def __init__(self, *args, beta: float = 1.0, **kwargs):
        super().__init__(*args, **kwargs)
        self.beta = beta

    def system_prompt(self) -> str:
        return (
            "أنت مدير مخاطر في شركة (بَصيرة كابيتال) لبورصة الكويت. "
            "تقيس مخاطر السهم: التقلب (ATR كنسبة من السعر)، معامل بيتا مقابل "
            "المؤشر، المديونية، السيولة، وبُعد السعر عن الدعم. تقترح حجم مركز "
            "منضبطاً ووقف خسارة يحمي رأس المال. درجتك تنخفض كلما ارتفعت المخاطر. "
            "دورك حماية رأس المال لا تعظيم العائد."
        )

    def compute(self, stock: Stock) -> Dict[str, Any]:
        t = stock.technicals
        q = stock.quote
        f = stock.financials
        atr_pct = (t.atr_14 / q.last_price * 100) if q.last_price else 0
        score = 40.0  # نبدأ من مخاطر منخفضة ونخصم مع كل عامل خطر
        risks, notes = [], []

        if atr_pct > 3:
            score -= 25; risks.append(f"تقلب مرتفع (ATR={atr_pct:.1f}% من السعر).")
        elif atr_pct > 1.5:
            score -= 10; notes.append(f"تقلب معتدل (ATR={atr_pct:.1f}%).")
        else:
            notes.append(f"تقلب منخفض (ATR={atr_pct:.1f}%).")

        if self.beta > 1.2:
            score -= 12; risks.append(f"بيتا مرتفع ({self.beta}) — حساسية عالية للسوق.")
        elif self.beta < 0.9:
            score += 8; notes.append(f"بيتا دفاعي ({self.beta}).")

        if f.debt_to_equity > 1.5:
            score -= 12; risks.append(f"رافعة مالية مرتفعة (D/E={f.debt_to_equity}).")

        if q.value_traded < 500_000:
            score -= 12; risks.append("سيولة منخفضة تزيد مخاطر التنفيذ.")

        score = self._clamp(score)
        # حجم مركز مقترح: أقل تقلباً => وزن أكبر (بحد أقصى 8% من المحفظة)
        suggested_weight = round(max(2.0, min(8.0, 12 - atr_pct * 2 - max(0, self.beta - 1) * 4)), 1)
        stop_loss = round(t.support - t.atr_14, 4)
        risk_per_share = round(q.last_price - stop_loss, 4)
        return {
            "score": round(score, 1),
            "atr_pct": round(atr_pct, 2),
            "beta": self.beta,
            "suggested_weight_pct": suggested_weight,
            "stop_loss": stop_loss,
            "risk_per_share": risk_per_share,
            "risks": risks,
            "notes": notes,
        }

    def user_prompt(self, stock: Stock, facts: Dict[str, Any]) -> str:
        q = stock.quote
        return (
            f"سهم: {q.name_ar} ({q.symbol}) — سعر {q.last_price} د.ك\n"
            f"ATR كنسبة من السعر: {facts['atr_pct']}% | بيتا: {facts['beta']}\n"
            f"الدين/حقوق الملكية: {stock.financials.debt_to_equity} | "
            f"قيمة التداول: {q.value_traded:,.0f} د.ك\n"
            f"الدعم: {stock.technicals.support} | وقف مقترح: {facts['stop_loss']}\n"
            "قيّم المخاطر واقترح حجم مركز ووقف خسارة، وأصدر درجة مخاطر."
        )

    def heuristic(self, stock: Stock, facts: Dict[str, Any]) -> AgentReport:
        score = facts["score"]
        return AgentReport(
            agent=self.name,
            agent_ar=self.agent_ar,
            signal=self._signal_from_score(score),
            score=score,
            confidence=0.85,
            summary=(
                f"مخاطر {'منخفضة' if score > 20 else 'مرتفعة' if score < -10 else 'معتدلة'}: "
                f"تقلب {facts['atr_pct']}%، بيتا {facts['beta']}. "
                f"وزن مقترح {facts['suggested_weight_pct']}% ووقف {facts['stop_loss']}."
            ),
            highlights=facts["notes"][:3] + [
                f"حجم مركز مقترح: {facts['suggested_weight_pct']}% من المحفظة.",
                f"مخاطرة السهم الواحد: {facts['risk_per_share']} د.ك حتى الوقف.",
            ],
            risks=facts["risks"][:4],
            raw=facts,
        )
