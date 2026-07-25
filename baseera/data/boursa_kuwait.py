"""
مزوّد بيانات بورصة الكويت (Boursa Kuwait Data Provider).

طبقة تجريد فوق مصدر البيانات. تأتي بوضعين:

1) الوضع النموذجي (SampleProvider) — يعمل فوراً بدون أي اشتراك، ويحتوي
   على شركات كويتية مدرجة فعلية مع بيانات مالية معقولة، ويولّد سلسلة سعرية
   حتمية (seeded) لكل سهم ثم يحسب المؤشرات الفنية حساباً حقيقياً منها
   (RSI, MACD, SMA, ATR ...). فالأرقام الفنية ليست مُختلقة بل محسوبة.

2) نقطة تمديد للبيانات الحيّة (LiveProvider) — هيكل جاهز لربط واجهة
   بيانات حقيقية من بورصة الكويت أو مزوّد خارجي. تُترك التفاصيل للمشترك
   حسب مصدر البيانات المتاح لديه.

للانتقال إلى البيانات الحيّة: طبّق دوال LiveProvider مع الحفاظ على نفس
التواقيع (الـ interface)، ولن يحتاج بقية النظام لأي تعديل.
"""
from __future__ import annotations

import hashlib
import math
from typing import Dict, List

from .models import (
    Quote,
    TechnicalSnapshot,
    Financials,
    NewsItem,
    Stock,
)

# ---------------------------------------------------------------------------
# قاعدة الشركات النموذجية — أسهم قيادية فعلية في بورصة الكويت (السوق الأول)
# ---------------------------------------------------------------------------
# القيم أدناه تمثيلية لأغراض العرض، وتُستبدل ببيانات حيّة عبر LiveProvider.
_COMPANIES: Dict[str, Dict] = {
    "NBK": {
        "name_ar": "بنك الكويت الوطني",
        "sector": "البنوك",
        "base_price": 0.965, "eps": 0.061, "pe": 15.8, "pb": 1.6, "roe": 11.2,
        "net_margin": 38.0, "de": 0.0, "div_yield": 3.6, "rev_growth": 8.5,
        "profit_growth": 9.7, "book_value": 0.60, "market_cap": 8200.0, "beta": 0.9,
    },
    "KFH": {
        "name_ar": "بيت التمويل الكويتي (بيتك)",
        "sector": "البنوك الإسلامية",
        "base_price": 0.735, "eps": 0.039, "pe": 18.9, "pb": 1.9, "roe": 12.8,
        "net_margin": 34.0, "de": 0.0, "div_yield": 2.9, "rev_growth": 11.0,
        "profit_growth": 14.2, "book_value": 0.39, "market_cap": 12100.0, "beta": 1.0,
    },
    "BOUBYAN": {
        "name_ar": "بنك بوبيان",
        "sector": "البنوك الإسلامية",
        "base_price": 0.640, "eps": 0.021, "pe": 30.5, "pb": 2.8, "roe": 10.5,
        "net_margin": 30.0, "de": 0.0, "div_yield": 1.8, "rev_growth": 13.5,
        "profit_growth": 15.0, "book_value": 0.23, "market_cap": 3600.0, "beta": 0.85,
    },
    "GBK": {
        "name_ar": "بنك الخليج",
        "sector": "البنوك",
        "base_price": 0.290, "eps": 0.017, "pe": 17.1, "pb": 1.3, "roe": 8.9,
        "net_margin": 28.0, "de": 0.0, "div_yield": 4.2, "rev_growth": 5.0,
        "profit_growth": 6.1, "book_value": 0.22, "market_cap": 900.0, "beta": 0.95,
    },
    "ZAIN": {
        "name_ar": "شركة الاتصالات المتنقلة (زين)",
        "sector": "الاتصالات",
        "base_price": 0.560, "eps": 0.048, "pe": 11.7, "pb": 1.1, "roe": 9.4,
        "net_margin": 15.5, "de": 0.7, "div_yield": 6.1, "rev_growth": 3.2,
        "profit_growth": 2.5, "book_value": 0.51, "market_cap": 2400.0, "beta": 1.1,
    },
    "AGILITY": {
        "name_ar": "أجيليتي للمخازن العمومية",
        "sector": "الخدمات اللوجستية",
        "base_price": 0.410, "eps": 0.011, "pe": 37.2, "pb": 1.0, "roe": 4.5,
        "net_margin": 6.0, "de": 1.2, "div_yield": 2.4, "rev_growth": 18.0,
        "profit_growth": -5.0, "book_value": 0.41, "market_cap": 2050.0, "beta": 1.3,
    },
    "MABANEE": {
        "name_ar": "شركة مباني (الأفنيوز)",
        "sector": "العقار",
        "base_price": 0.780, "eps": 0.052, "pe": 15.0, "pb": 1.7, "roe": 12.0,
        "net_margin": 45.0, "de": 0.9, "div_yield": 3.1, "rev_growth": 9.0,
        "profit_growth": 8.0, "book_value": 0.46, "market_cap": 1500.0, "beta": 1.05,
    },
    "HUMANSOFT": {
        "name_ar": "شركة هيومن سوفت القابضة",
        "sector": "التعليم",
        "base_price": 3.10, "eps": 0.230, "pe": 13.5, "pb": 6.5, "roe": 48.0,
        "net_margin": 40.0, "de": 0.1, "div_yield": 7.5, "rev_growth": 7.0,
        "profit_growth": 6.5, "book_value": 0.48, "market_cap": 1860.0, "beta": 0.8,
    },
    "GFH": {
        "name_ar": "مجموعة جي إف إتش المالية",
        "sector": "الخدمات المالية",
        "base_price": 0.230, "eps": 0.014, "pe": 16.4, "pb": 1.2, "roe": 7.8,
        "net_margin": 22.0, "de": 1.5, "div_yield": 3.9, "rev_growth": 12.0,
        "profit_growth": 4.0, "book_value": 0.19, "market_cap": 830.0, "beta": 1.4,
    },
    "KPROJ": {
        "name_ar": "مشاريع الكويت القابضة (كيبكو)",
        "sector": "الاستثمار",
        "base_price": 0.163, "eps": 0.006, "pe": 27.2, "pb": 0.9, "roe": 3.3,
        "net_margin": 9.0, "de": 2.1, "div_yield": 2.0, "rev_growth": 4.5,
        "profit_growth": 1.0, "book_value": 0.18, "market_cap": 480.0, "beta": 1.25,
    },
    "AKTETAB": {
        "name_ar": "شركة اكتتاب القابضة",
        "sector": "الاستثمار",
        "base_price": 0.0975, "eps": 0.0032, "pe": 30.5, "pb": 1.1, "roe": 3.6,
        "net_margin": 12.0, "de": 0.8, "div_yield": 0.0, "rev_growth": 22.0,
        "profit_growth": 15.0, "book_value": 0.089, "market_cap": 42.0, "beta": 1.5,
    },
}

# مرادفات الرموز (بحث بالاسم العربي أو أسماء بديلة)
_ALIASES = {
    "اكتتاب": "AKTETAB",
    "اكتتاب القابضة": "AKTETAB",
    "AKTTAB": "AKTETAB",
    "بيتك": "KFH",
    "الوطني": "NBK",
    "زين": "ZAIN",
}

# أخبار نموذجية على مستوى القطاع (تُستبدل بمصدر أخبار حيّ لاحقاً)
_SECTOR_NEWS: Dict[str, List[Dict]] = {
    "البنوك": [
        {"headline": "بنك الكويت المركزي يثبّت سعر الخصم عند مستواه الحالي",
         "source": "بورصة الكويت", "date": "2026-07-20",
         "summary": "قرار يدعم هوامش الفائدة للبنوك ويحافظ على استقرار الائتمان."},
        {"headline": "نمو محفظة القروض في القطاع المصرفي الكويتي بنسبة سنوية جيدة",
         "source": "تقرير سوق", "date": "2026-07-18",
         "summary": "توسّع في تمويل الشركات والأفراد يعزز إيرادات الفوائد."},
    ],
    "البنوك الإسلامية": [
        {"headline": "ارتفاع الودائع في البنوك الإسلامية مع نمو الصيرفة المتوافقة مع الشريعة",
         "source": "بورصة الكويت", "date": "2026-07-19",
         "summary": "زيادة القاعدة التمويلية تدعم النمو المستقبلي للأرباح."},
    ],
    "الاتصالات": [
        {"headline": "ضغوط على الإيرادات في بعض الأسواق الإقليمية لمشغلي الاتصالات",
         "source": "تقرير قطاعي", "date": "2026-07-15",
         "summary": "تقلبات العملات في أسواق خارجية تؤثر على الإيرادات المجمّعة."},
        {"headline": "استمرار توزيعات نقدية مرتفعة يجذب مستثمري الدخل",
         "source": "بورصة الكويت", "date": "2026-07-10",
         "summary": "عائد توزيعات جذّاب يدعم الطلب على السهم دفاعياً."},
    ],
    "العقار": [
        {"headline": "معدلات إشغال قوية للمجمعات التجارية الكبرى في الكويت",
         "source": "تقرير عقاري", "date": "2026-07-17",
         "summary": "تدفقات إيجارية مستقرة تدعم التدفقات النقدية التشغيلية."},
    ],
    "التعليم": [
        {"headline": "نمو أعداد الطلبة في قطاع التعليم الخاص يدعم الإيرادات المتكررة",
         "source": "تقرير قطاعي", "date": "2026-07-12",
         "summary": "طلب هيكلي مستقر مع هوامش ربحية مرتفعة."},
    ],
}

_DEFAULT_NEWS = [
    {"headline": "تحسّن السيولة العامة في بورصة الكويت خلال الجلسات الأخيرة",
     "source": "بورصة الكويت", "date": "2026-07-21",
     "summary": "ارتفاع قيم التداول يعكس تحسّن شهية المخاطرة."},
]


def _seed(symbol: str) -> int:
    """بذرة حتمية مشتقة من الرمز لتوليد سلسلة قابلة للتكرار."""
    h = hashlib.sha256(symbol.encode("utf-8")).hexdigest()
    return int(h[:8], 16)


def _price_series(symbol: str, base_price: float, n: int = 220) -> List[float]:
    """
    توليد سلسلة أسعار يومية حتمية (بدون عشوائية حقيقية) حول السعر الأساسي.
    نستخدم دوال جيبية متراكبة + انحياز طفيف لمحاكاة اتجاه واقعي.
    الهدف: مؤشرات فنية محسوبة من بيانات متسقة، لا أرقام مُختلقة.
    """
    seed = _seed(symbol)
    phase = (seed % 360) * math.pi / 180.0
    drift = ((seed >> 8) % 7 - 3) * 0.00025          # انحياز اتجاهي صغير
    amp1 = 0.06 + ((seed >> 4) % 5) * 0.01           # اتساع الموجة الطويلة
    amp2 = 0.02 + ((seed >> 2) % 4) * 0.005          # اتساع الموجة القصيرة
    series: List[float] = []
    for i in range(n):
        t = i / n
        wave = (
            amp1 * math.sin(2 * math.pi * 2 * t + phase)
            + amp2 * math.sin(2 * math.pi * 9 * t + phase * 1.7)
        )
        trend = drift * i
        micro = 0.004 * math.sin(2 * math.pi * 23 * t + phase * 0.5)
        price = base_price * (1 + wave + trend + micro)
        series.append(round(max(price, 0.001), 4))
    return series


def _sma(series: List[float], period: int) -> float:
    if len(series) < period:
        period = len(series)
    return round(sum(series[-period:]) / period, 4)


def _ema_series(series: List[float], period: int) -> List[float]:
    k = 2 / (period + 1)
    ema = [series[0]]
    for price in series[1:]:
        ema.append(price * k + ema[-1] * (1 - k))
    return ema


def _rsi(series: List[float], period: int = 14) -> float:
    if len(series) <= period:
        return 50.0
    gains, losses = 0.0, 0.0
    for i in range(-period, 0):
        diff = series[i] - series[i - 1]
        if diff >= 0:
            gains += diff
        else:
            losses -= diff
    avg_gain = gains / period
    avg_loss = losses / period
    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    return round(100 - (100 / (1 + rs)), 2)


def _macd(series: List[float]):
    ema12 = _ema_series(series, 12)
    ema26 = _ema_series(series, 26)
    macd_line = [a - b for a, b in zip(ema12, ema26)]
    signal = _ema_series(macd_line, 9)
    macd_v = round(macd_line[-1], 5)
    sig_v = round(signal[-1], 5)
    return macd_v, sig_v, round(macd_v - sig_v, 5)


def _atr(series: List[float], period: int = 14) -> float:
    """تقريب لمتوسط المدى الحقيقي من سلسلة الإغلاق (تقلب)."""
    if len(series) <= period:
        period = max(len(series) - 1, 1)
    ranges = [abs(series[i] - series[i - 1]) for i in range(-period, 0)]
    return round(sum(ranges) / period, 5)


def _trend(sma20: float, sma50: float, sma200: float, last: float) -> str:
    if last > sma20 > sma50 and sma50 >= sma200:
        return "صاعد"
    if last < sma20 < sma50 and sma50 <= sma200:
        return "هابط"
    return "عرضي"


class SampleProvider:
    """مزوّد البيانات النموذجي — يعمل فوراً بدون اشتراك."""

    def list_symbols(self) -> List[str]:
        return list(_COMPANIES.keys())

    def _resolve(self, symbol: str) -> str:
        """يحوّل الاسم/الرمز المُدخل إلى رمز رسمي (يدعم المرادفات العربية)."""
        raw = symbol.strip()
        if raw in _ALIASES:                 # مطابقة عربية مباشرة
            return _ALIASES[raw]
        key = raw.upper()
        if key in _ALIASES:
            return _ALIASES[key]
        return key

    def _require(self, symbol: str) -> Dict:
        key = self._resolve(symbol)
        if key not in _COMPANIES:
            raise KeyError(
                f"الرمز '{symbol}' غير موجود في قاعدة البيانات النموذجية. "
                f"الرموز المتاحة: {', '.join(_COMPANIES)}"
            )
        return _COMPANIES[key]

    def get_quote(self, symbol: str) -> Quote:
        c = self._require(symbol)
        symbol = self._resolve(symbol)
        series = _price_series(symbol, c["base_price"])
        last = series[-1]
        prev = series[-2]
        change = round(last - prev, 4)
        change_pct = round((change / prev) * 100, 2) if prev else 0.0
        seed = _seed(symbol)
        volume = 500_000 + (seed % 9_000_000)
        return Quote(
            symbol=symbol.upper(),
            name_ar=c["name_ar"],
            sector=c["sector"],
            last_price=last,
            change=change,
            change_pct=change_pct,
            volume=volume,
            value_traded=round(last * volume, 2),
            day_high=round(max(series[-2:]), 4),
            day_low=round(min(series[-2:]), 4),
            week52_high=round(max(series), 4),
            week52_low=round(min(series), 4),
        )

    def get_technicals(self, symbol: str) -> TechnicalSnapshot:
        c = self._require(symbol)
        symbol = self._resolve(symbol)
        series = _price_series(symbol, c["base_price"])
        sma20 = _sma(series, 20)
        sma50 = _sma(series, 50)
        sma200 = _sma(series, 200)
        macd_v, sig_v, hist = _macd(series)
        last = series[-1]
        window = series[-60:]
        return TechnicalSnapshot(
            sma_20=sma20,
            sma_50=sma50,
            sma_200=sma200,
            rsi_14=_rsi(series),
            macd=macd_v,
            macd_signal=sig_v,
            macd_hist=hist,
            atr_14=_atr(series),
            support=round(min(window), 4),
            resistance=round(max(window), 4),
            trend=_trend(sma20, sma50, sma200, last),
            price_series=series[-60:],
        )

    def get_financials(self, symbol: str) -> Financials:
        c = self._require(symbol)
        return Financials(
            market_cap=c["market_cap"],
            eps=c["eps"],
            pe_ratio=c["pe"],
            pb_ratio=c["pb"],
            roe=c["roe"],
            net_margin=c["net_margin"],
            debt_to_equity=c["de"],
            dividend_yield=c["div_yield"],
            revenue_growth=c["rev_growth"],
            profit_growth=c["profit_growth"],
            book_value=c["book_value"],
        )

    def get_news(self, symbol: str) -> List[NewsItem]:
        c = self._require(symbol)
        items = _SECTOR_NEWS.get(c["sector"], []) + _DEFAULT_NEWS
        return [NewsItem(**n) for n in items]

    def get_stock(self, symbol: str) -> Stock:
        return Stock(
            quote=self.get_quote(symbol),
            technicals=self.get_technicals(symbol),
            financials=self.get_financials(symbol),
            news=self.get_news(symbol),
        )

    def beta(self, symbol: str) -> float:
        return self._require(symbol).get("beta", 1.0)


class LiveProvider(SampleProvider):
    """
    نقطة تمديد للبيانات الحيّة من بورصة الكويت أو مزوّد خارجي.

    أعِد تنفيذ الدوال أدناه لجلب بيانات حقيقية (REST API / تغذية سوق).
    ما دمت تحافظ على نفس التواقيع، سيعمل بقية النظام دون تعديل.
    حالياً يرث السلوك النموذجي حتى لا ينكسر التشغيل قبل الربط الفعلي.
    """

    def get_quote(self, symbol: str) -> Quote:  # pragma: no cover - هيكل تمديد
        # TODO: اربط واجهة بورصة الكويت هنا وأعد كائن Quote حقيقياً.
        return super().get_quote(symbol)


def get_provider(live: bool = False) -> SampleProvider:
    """مصنع بسيط لاختيار المزوّد."""
    return LiveProvider() if live else SampleProvider()
