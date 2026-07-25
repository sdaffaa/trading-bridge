"""
اختبارات أساسية لشركة بَصيرة كابيتال.
تعمل بالوضع الاحتياطي الكمّي (بدون مفتاح API) لضمان الحتمية.

التشغيل:  python -m pytest -q   أو   python tests/test_baseera.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from baseera.orchestrator import BaseeraCapital, format_report
from baseera.data.boursa_kuwait import SampleProvider


def test_provider_has_symbols():
    p = SampleProvider()
    assert "KFH" in p.list_symbols()
    assert len(p.list_symbols()) >= 10


def test_stock_snapshot_is_consistent():
    p = SampleProvider()
    stock = p.get_stock("NBK")
    assert stock.quote.last_price > 0
    assert 0 <= stock.technicals.rsi_14 <= 100
    assert stock.technicals.support <= stock.technicals.resistance
    # حتمية: نفس الرمز يعطي نفس السعر
    assert p.get_quote("NBK").last_price == p.get_quote("NBK").last_price


def test_full_analysis_produces_six_reports_and_recommendation():
    firm = BaseeraCapital()
    result = firm.analyze("KFH")
    # خمسة محللين + التوصية النهائية
    assert len(result["reports"]) == 5
    rec = result["recommendation"]
    assert rec["action"] in ("شراء", "بيع", "احتفاظ")
    assert rec["conviction"] in ("عالية", "متوسطة", "منخفضة")
    assert rec["target_price"] > 0
    assert rec["stop_loss"] > 0


def test_every_agent_has_distinct_mission():
    firm = BaseeraCapital()
    roster = firm.roster()
    missions = [a["mission"] for a in roster]
    assert len(roster) == 6
    assert len(set(missions)) == 6  # كل وكيل بمهمة مختلفة


def test_scores_in_range():
    firm = BaseeraCapital()
    result = firm.analyze("ZAIN")
    for r in result["reports"]:
        assert -100 <= r["score"] <= 100
        assert 0 <= r["confidence"] <= 1


def test_report_formats_without_error():
    firm = BaseeraCapital()
    result = firm.analyze("HUMANSOFT")
    text = format_report(result)
    assert "بَصيرة كابيتال" in text
    assert "التوصية النهائية" in text


def test_invalid_symbol_raises():
    firm = BaseeraCapital()
    try:
        firm.analyze("NOPE")
        assert False, "يجب أن يرفع خطأ"
    except KeyError:
        pass


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    passed = 0
    for fn in fns:
        fn()
        print(f"✓ {fn.__name__}")
        passed += 1
    print(f"\nنجحت جميع الاختبارات: {passed}/{len(fns)}")
