"""
بَصيرة كابيتال (Baseera Capital)
================================
شركة تحليل مالي وفني ذكي متخصصة في بورصة الكويت، تعمل بنظام فريق من
الوكلاء المتخصصين، كل وكيل له مهمة محددة، يجتمعون لإصدار توصية استثمارية.

الاستخدام السريع:
    from baseera.orchestrator import BaseeraCapital, format_report
    firm = BaseeraCapital()
    result = firm.analyze("KFH")
    print(format_report(result))
"""
from .orchestrator import (
    BaseeraCapital,
    format_report,
    telegram_summary,
    COMPANY_NAME,
    COMPANY_TAGLINE,
)

__all__ = [
    "BaseeraCapital",
    "format_report",
    "telegram_summary",
    "COMPANY_NAME",
    "COMPANY_TAGLINE",
]

__version__ = "1.0.0"
