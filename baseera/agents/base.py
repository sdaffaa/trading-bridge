"""
الفئة الأساسية للوكلاء (BaseAgent).

كل وكيل في شركة بَصيرة كابيتال يرث من BaseAgent، وله:
- مسمّى وظيفي عربي (agent_ar) ومهمة محددة (mission)
- شخصية/تعليمات (system prompt) تُمرَّر لنموذج Claude
- دالة analyze() التي تُنتج تقريراً موحّداً من نوع AgentReport

يعمل الوكيل بوضعين:
1) وضع الذكاء (LLM): إن توفّر ANTHROPIC_API_KEY يستدعي Claude للحصول على
   تحليل نصي غني، مع الاستفادة من الأرقام التي حسبها الوكيل مسبقاً.
2) الوضع الاحتياطي (Heuristic): إن لم يتوفّر مفتاح أو فشل الاتصال، يعتمد
   الوكيل على قواعد كمية صريحة ينتجها بنفسه، فلا يتوقف النظام أبداً.
"""
from __future__ import annotations

import json
import os
from typing import Any, Dict, Optional

from ..data.models import Stock, AgentReport

try:  # الاستيراد اختياري حتى يعمل الوضع الاحتياطي بدون الحزمة
    import anthropic  # type: ignore
except Exception:  # pragma: no cover
    anthropic = None


DEFAULT_MODEL = os.environ.get("CLAUDE_MODEL", "claude-sonnet-4-5-20250929")


class BaseAgent:
    """الأساس المشترك لجميع الوكلاء المتخصصين."""

    name: str = "base"
    agent_ar: str = "وكيل"
    mission: str = "مهمة عامة"

    def __init__(self, client: Optional[Any] = None, model: str = DEFAULT_MODEL):
        self.model = model
        # يُمرَّر عميل مشترك من المنسّق لتفادي إنشاء عملاء متعددين
        if client is not None:
            self.client = client
        elif anthropic is not None and os.environ.get("ANTHROPIC_API_KEY"):
            self.client = anthropic.Anthropic(
                api_key=os.environ["ANTHROPIC_API_KEY"]
            )
        else:
            self.client = None

    # ------------------------------------------------------------------
    # واجهة يجب أن يوفّرها كل وكيل فرعي
    # ------------------------------------------------------------------
    def system_prompt(self) -> str:
        """تعليمات الشخصية/الدور التي تُمرَّر للنموذج."""
        raise NotImplementedError

    def compute(self, stock: Stock) -> Dict[str, Any]:
        """
        الحسابات الكمية الخاصة بالوكيل (نِسب، مؤشرات، درجات فرعية).
        تُستخدم نتائجها في كل من نداء LLM والوضع الاحتياطي.
        """
        return {}

    def heuristic(self, stock: Stock, facts: Dict[str, Any]) -> AgentReport:
        """التحليل القائم على القواعد — يُستخدم بدون LLM."""
        raise NotImplementedError

    def user_prompt(self, stock: Stock, facts: Dict[str, Any]) -> str:
        """نص المهمة الموجّه للنموذج بلغة عربية مع الأرقام المحسوبة."""
        raise NotImplementedError

    # ------------------------------------------------------------------
    # المنطق المشترك
    # ------------------------------------------------------------------
    def analyze(self, stock: Stock) -> AgentReport:
        facts = self.compute(stock)
        if self.client is None:
            return self.heuristic(stock, facts)
        try:
            return self._analyze_with_llm(stock, facts)
        except Exception as exc:  # pragma: no cover - أمان تشغيلي
            report = self.heuristic(stock, facts)
            report.risks.append(f"تعذّر استدعاء النموذج، استُخدم الوضع الاحتياطي ({exc}).")
            return report

    def _analyze_with_llm(self, stock: Stock, facts: Dict[str, Any]) -> AgentReport:
        instruction = (
            self.user_prompt(stock, facts)
            + "\n\nأعد ردّك بصيغة JSON فقط دون أي نص إضافي، بالمخطط التالي:\n"
            '{"signal": "إيجابي|سلبي|محايد", "score": <رقم من -100 إلى 100>, '
            '"confidence": <رقم من 0 إلى 1>, "summary": "ملخص عربي موجز", '
            '"highlights": ["نقطة", ...], "risks": ["تحفظ", ...]}'
        )
        msg = self.client.messages.create(
            model=self.model,
            max_tokens=900,
            system=self.system_prompt(),
            messages=[{"role": "user", "content": instruction}],
        )
        text = msg.content[0].text.strip()
        data = self._extract_json(text)
        # درجة الوكيل الكمية تُستخدم كسند احتياطي إن نقص شيء من رد النموذج
        base = self.heuristic(stock, facts)
        return AgentReport(
            agent=self.name,
            agent_ar=self.agent_ar,
            signal=data.get("signal", base.signal),
            score=float(data.get("score", base.score)),
            confidence=float(data.get("confidence", base.confidence)),
            summary=data.get("summary", base.summary),
            highlights=data.get("highlights", base.highlights),
            risks=data.get("risks", base.risks),
            raw=facts,
        )

    @staticmethod
    def _extract_json(text: str) -> Dict[str, Any]:
        """يستخرج كتلة JSON من رد النموذج بتسامح."""
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            try:
                return json.loads(text[start : end + 1])
            except json.JSONDecodeError:
                pass
        return {}

    # أدوات مساعدة مشتركة ------------------------------------------------
    @staticmethod
    def _clamp(value: float, low: float = -100, high: float = 100) -> float:
        return max(low, min(high, value))

    @staticmethod
    def _signal_from_score(score: float) -> str:
        if score >= 20:
            return "إيجابي"
        if score <= -20:
            return "سلبي"
        return "محايد"
