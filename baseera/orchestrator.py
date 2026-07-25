"""
المنسّق (Orchestrator) — الإدارة التنفيذية لشركة بَصيرة كابيتال.

يدير دورة تحليل كاملة لسهم واحد:
  1) يطلب من مزوّد البيانات لقطة السهم الكاملة.
  2) يشغّل الوكلاء المتخصصين، كلٌّ على مهمته (بيانات، فني، مالي، أخبار، مخاطر).
  3) يمرّر تقاريرهم إلى مدير الاستثمار لإصدار التوصية النهائية.
  4) يعيد ملفاً كاملاً (dossier) قابلاً للطباعة أو التصدير JSON.

يشترك جميع الوكلاء في عميل Claude واحد إن توفّر المفتاح، وإلا عملوا
جميعاً بالوضع الاحتياطي الكمّي.
"""
from __future__ import annotations

import os
from dataclasses import asdict
from typing import Any, Dict, List, Optional

from .data.boursa_kuwait import get_provider
from .data.models import Stock, AgentReport, FinalRecommendation
from .agents import (
    MarketDataAgent,
    TechnicalAnalysisAgent,
    FundamentalAnalysisAgent,
    NewsSentimentAgent,
    RiskManagementAgent,
    RecommendationAgent,
)

try:
    import anthropic  # type: ignore
except Exception:  # pragma: no cover
    anthropic = None


COMPANY_NAME = "بَصيرة كابيتال"
COMPANY_TAGLINE = "بيت تحليل مالي وفني ذكي — بورصة الكويت"


class BaseeraCapital:
    """الشركة: تنسّق فريق الوكلاء وتُصدر التوصيات."""

    def __init__(self, live: bool = False, model: Optional[str] = None):
        self.provider = get_provider(live=live)
        self.model = model or os.environ.get(
            "CLAUDE_MODEL", "claude-sonnet-4-5-20250929"
        )
        # عميل مشترك (اختياري)
        if anthropic is not None and os.environ.get("ANTHROPIC_API_KEY"):
            self.client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
            self.mode = "ذكاء اصطناعي (Claude)"
        else:
            self.client = None
            self.mode = "احتياطي كمّي (بدون مفتاح API)"

    # ------------------------------------------------------------------
    def team(self, stock: Stock) -> List:
        """يبني فريق المحللين (بيتا المخاطر يُقرأ من المزوّد)."""
        beta = self.provider.beta(stock.symbol)
        common = dict(client=self.client, model=self.model)
        return [
            MarketDataAgent(**common),
            TechnicalAnalysisAgent(**common),
            FundamentalAnalysisAgent(**common),
            NewsSentimentAgent(**common),
            RiskManagementAgent(beta=beta, **common),
        ]

    def roster(self) -> List[Dict[str, str]]:
        """قائمة الوكلاء ومهامهم — للعرض التعريفي."""
        agents = [
            MarketDataAgent, TechnicalAnalysisAgent, FundamentalAnalysisAgent,
            NewsSentimentAgent, RiskManagementAgent, RecommendationAgent,
        ]
        return [{"agent": a.name, "agent_ar": a.agent_ar, "mission": a.mission}
                for a in agents]

    # ------------------------------------------------------------------
    def analyze(self, symbol: str) -> Dict[str, Any]:
        """يشغّل دورة تحليل كاملة ويعيد الملف الكامل."""
        stock = self.provider.get_stock(symbol)
        reports: List[AgentReport] = [agent.analyze(stock) for agent in self.team(stock)]
        cio = RecommendationAgent(client=self.client, model=self.model)
        recommendation = cio.recommend(stock, reports)
        return {
            "company": COMPANY_NAME,
            "mode": self.mode,
            "symbol": stock.symbol,
            "name_ar": stock.name_ar,
            "sector": stock.quote.sector,
            "last_price": stock.quote.last_price,
            "reports": [r.to_dict() for r in reports],
            "recommendation": recommendation.to_dict(),
            "_recommendation_obj": recommendation,
            "_stock_obj": stock,
        }

    def list_symbols(self) -> List[str]:
        return self.provider.list_symbols()


# ---------------------------------------------------------------------------
# طباعة تقرير عربي أنيق في الطرفية
# ---------------------------------------------------------------------------
def format_report(result: Dict[str, Any]) -> str:
    rec: FinalRecommendation = result["_recommendation_obj"]
    lines: List[str] = []
    bar = "═" * 66
    lines.append(bar)
    lines.append(f"  {COMPANY_NAME} — {COMPANY_TAGLINE}")
    lines.append(f"  وضع التشغيل: {result['mode']}")
    lines.append(bar)
    lines.append(
        f"  السهم: {result['name_ar']} ({result['symbol']})  |  "
        f"القطاع: {result['sector']}  |  السعر: {result['last_price']} د.ك"
    )
    lines.append("─" * 66)
    lines.append("  تقارير فريق المحللين:")
    for r in rec.agent_reports:
        icon = "🟢" if r.signal == "إيجابي" else "🔴" if r.signal == "سلبي" else "⚪"
        lines.append(f"\n  {icon} {r.agent_ar}  [إشارة: {r.signal} | درجة: {r.score:+.0f}]")
        lines.append(f"     {r.summary}")
        for h in r.highlights[:3]:
            lines.append(f"       • {h}")
        for rk in r.risks[:2]:
            lines.append(f"       ⚠ {rk}")

    lines.append("\n" + bar)
    action_icon = "🟢" if rec.action == "شراء" else "🔴" if rec.action == "بيع" else "🟡"
    lines.append(f"  {action_icon} التوصية النهائية (مدير الاستثمار): «{rec.action}»")
    lines.append(f"     قوة القناعة: {rec.conviction}  |  الدرجة المجمّعة: {rec.composite_score:+.0f}"
                 f"  |  الثقة: {rec.confidence:.0%}")
    lines.append(f"     منطقة الدخول: {rec.entry_zone}")
    lines.append(f"     السعر المستهدف: {rec.target_price} د.ك  |  وقف الخسارة: {rec.stop_loss} د.ك")
    lines.append(f"     الأفق الزمني: {rec.time_horizon}")
    lines.append("─" * 66)
    lines.append("  المسوّغ:")
    for ln in rec.rationale.split("\n"):
        lines.append(f"     {ln}")
    lines.append(bar)
    lines.append("  تنبيه: هذا تحليل آلي لأغراض تعليمية وليس نصيحة استثمارية.")
    lines.append(bar)
    return "\n".join(lines)


def telegram_summary(result: Dict[str, Any]) -> str:
    """ملخص مختصر مناسب للإرسال عبر تيليجرام."""
    rec: FinalRecommendation = result["_recommendation_obj"]
    icon = "🟢" if rec.action == "شراء" else "🔴" if rec.action == "بيع" else "🟡"
    top = "\n".join(
        f"• {r.agent_ar}: {r.signal} ({r.score:+.0f})" for r in rec.agent_reports
    )
    return (
        f"{COMPANY_NAME} | توصية آلية\n"
        f"السهم: {rec.name_ar} ({rec.symbol})\n"
        f"السعر: {result['last_price']} د.ك\n\n"
        f"{top}\n\n"
        f"{icon} التوصية: {rec.action} (قناعة {rec.conviction})\n"
        f"الهدف: {rec.target_price} | الوقف: {rec.stop_loss}\n"
        f"الأفق: {rec.time_horizon}\n\n"
        f"تنبيه: تحليل آلي تعليمي وليس نصيحة استثمارية."
    )
