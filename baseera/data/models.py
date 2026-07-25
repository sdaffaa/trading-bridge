"""
نماذج البيانات (Data Models) لشركة بَصيرة كابيتال.

تعرّف هذه الوحدة الهياكل الأساسية التي تنتقل بين الوكلاء:
- Quote            : بيانات السعر اللحظية
- TechnicalSnapshot: المؤشرات الفنية المحسوبة
- Financials       : البيانات المالية والنِسب الأساسية
- NewsItem         : خبر مفرد
- Stock            : تجميعة كاملة لسهم واحد
- AgentReport      : تقرير صادر من وكيل متخصص
- FinalRecommendation : التوصية النهائية من مدير الاستثمار
"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict, Any


@dataclass
class Quote:
    """بيانات السعر اللحظية لسهم في بورصة الكويت."""
    symbol: str
    name_ar: str
    sector: str
    last_price: float          # آخر سعر (فلس كويتي)
    change: float              # التغير المطلق
    change_pct: float          # نسبة التغير %
    volume: int                # حجم التداول (عدد الأسهم)
    value_traded: float        # قيمة التداول (دينار كويتي)
    day_high: float
    day_low: float
    week52_high: float
    week52_low: float
    currency: str = "KWD"


@dataclass
class TechnicalSnapshot:
    """لقطة للمؤشرات الفنية المحسوبة من السلسلة السعرية."""
    sma_20: float
    sma_50: float
    sma_200: float
    rsi_14: float
    macd: float
    macd_signal: float
    macd_hist: float
    atr_14: float              # متوسط المدى الحقيقي (تقلب)
    support: float             # أقرب دعم
    resistance: float          # أقرب مقاومة
    trend: str                 # صاعد / هابط / عرضي
    price_series: List[float] = field(default_factory=list)


@dataclass
class Financials:
    """البيانات والنِسب المالية الأساسية."""
    market_cap: float          # القيمة السوقية (مليون دينار)
    eps: float                 # ربحية السهم
    pe_ratio: float            # مكرر الربحية
    pb_ratio: float            # مكرر القيمة الدفترية
    roe: float                 # العائد على حقوق الملكية %
    net_margin: float          # هامش صافي الربح %
    debt_to_equity: float      # الدين إلى حقوق الملكية
    dividend_yield: float      # عائد التوزيعات %
    revenue_growth: float      # نمو الإيرادات السنوي %
    profit_growth: float       # نمو صافي الربح السنوي %
    book_value: float          # القيمة الدفترية للسهم


@dataclass
class NewsItem:
    """خبر مرتبط بالشركة أو القطاع."""
    headline: str
    source: str
    date: str
    summary: str = ""


@dataclass
class Stock:
    """التجميعة الكاملة لسهم واحد كما تُسلَّم للوكلاء."""
    quote: Quote
    technicals: TechnicalSnapshot
    financials: Financials
    news: List[NewsItem] = field(default_factory=list)

    @property
    def symbol(self) -> str:
        return self.quote.symbol

    @property
    def name_ar(self) -> str:
        return self.quote.name_ar


@dataclass
class AgentReport:
    """تقرير موحّد يُصدره كل وكيل متخصص."""
    agent: str                 # الاسم البرمجي للوكيل
    agent_ar: str              # الاسم العربي / المسمّى الوظيفي
    signal: str                # الإشارة: إيجابي / سلبي / محايد
    score: float               # درجة من -100 (سلبي جداً) إلى +100 (إيجابي جداً)
    confidence: float          # الثقة 0..1
    summary: str               # ملخص عربي موجز
    highlights: List[str] = field(default_factory=list)   # نقاط رئيسية
    risks: List[str] = field(default_factory=list)        # مخاطر / تحفظات
    raw: Dict[str, Any] = field(default_factory=dict)     # بيانات خام مساعدة

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class FinalRecommendation:
    """التوصية النهائية الصادرة عن مدير الاستثمار (CIO)."""
    symbol: str
    name_ar: str
    action: str                # شراء / بيع / احتفاظ
    conviction: str            # قوة القناعة: عالية / متوسطة / منخفضة
    composite_score: float     # الدرجة المجمّعة الموزونة
    confidence: float          # الثقة الكلية 0..1
    entry_zone: str            # منطقة الدخول المقترحة
    target_price: float        # السعر المستهدف
    stop_loss: float           # وقف الخسارة
    time_horizon: str          # الأفق الزمني
    rationale: str             # المسوّغ / الأساس المنطقي
    agent_reports: List[AgentReport] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        return d
