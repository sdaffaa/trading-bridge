#!/usr/bin/env python3
"""
واجهة سطر الأوامر لشركة بَصيرة كابيتال.

أمثلة:
    python main.py list                 # عرض الأسهم المتاحة
    python main.py agents               # عرض الوكلاء ومهامهم
    python main.py analyze KFH          # تحليل سهم وإصدار توصية
    python main.py analyze ZAIN --json  # مخرجات JSON
    python main.py analyze NBK --telegram   # إرسال الملخص عبر تيليجرام
"""
from __future__ import annotations

import argparse
import json
import os
import sys

from baseera.orchestrator import (
    BaseeraCapital,
    format_report,
    format_screen,
    telegram_summary,
    COMPANY_NAME,
    COMPANY_TAGLINE,
)


def _send_telegram(text: str) -> None:
    import requests

    token = os.environ.get("TELEGRAM_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        print("⚠ لم يتم ضبط TELEGRAM_TOKEN / TELEGRAM_CHAT_ID — تم تخطي الإرسال.")
        return
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    resp = requests.post(url, json={"chat_id": str(chat_id), "text": text})
    print(f"تيليجرام: {resp.status_code}")


def cmd_list(args) -> int:
    firm = BaseeraCapital(live=args.live)
    print(f"{COMPANY_NAME} — الأسهم المتاحة في قاعدة البيانات:")
    for sym in firm.list_symbols():
        stock = firm.provider.get_quote(sym)
        print(f"  {sym:<10} {stock.name_ar}  ({stock.sector})")
    return 0


def cmd_agents(args) -> int:
    firm = BaseeraCapital(live=args.live)
    print(f"{COMPANY_NAME} — {COMPANY_TAGLINE}")
    print("فريق الوكلاء ومهام كل منهم:\n")
    for i, a in enumerate(firm.roster(), 1):
        print(f"  {i}. {a['agent_ar']}")
        print(f"     المهمة: {a['mission']}\n")
    return 0


def cmd_top(args) -> int:
    firm = BaseeraCapital(live=args.live)
    ranked = firm.screen()
    if args.json:
        payload = [{k: v for k, v in r.items() if not k.startswith("_")}
                   for r in ranked[:args.count]]
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0
    print(format_screen(ranked, top=args.count))
    # تفاصيل السهم الأول (الأعلى نمواً متوقعاً)
    if ranked:
        best = ranked[0]
        print(f"\n  ⭐ الأعلى نمواً متوقعاً هذا الشهر: {best['name_ar']} ({best['symbol']})")
        print(f"     درجة النمو {best['growth_score']} | نمو أرباح {best['profit_growth']}% | "
              f"صعود متوقع {best['upside_pct']}% حتى {best['target_price']} د.ك")
    return 0


def cmd_analyze(args) -> int:
    firm = BaseeraCapital(live=args.live)
    try:
        result = firm.analyze(args.symbol)
    except KeyError as exc:
        print(f"خطأ: {exc}")
        return 1

    if args.json:
        payload = {k: v for k, v in result.items() if not k.startswith("_")}
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(format_report(result))

    if args.telegram:
        _send_telegram(telegram_summary(result))
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description=f"{COMPANY_NAME} — {COMPANY_TAGLINE}"
    )
    p.add_argument("--live", action="store_true",
                   help="استخدام مزوّد البيانات الحيّة (يتطلب ربطاً فعلياً)")
    sub = p.add_subparsers(dest="command", required=True)

    sub.add_parser("list", help="عرض الأسهم المتاحة").set_defaults(func=cmd_list)
    sub.add_parser("agents", help="عرض الوكلاء ومهامهم").set_defaults(func=cmd_agents)

    t = sub.add_parser("top", help="ترتيب الأسهم حسب النمو المتوقع")
    t.add_argument("-n", "--count", type=int, default=10, help="عدد الأسهم المعروضة")
    t.add_argument("--json", action="store_true", help="مخرجات بصيغة JSON")
    t.set_defaults(func=cmd_top)

    a = sub.add_parser("analyze", help="تحليل سهم وإصدار توصية")
    a.add_argument("symbol", help="رمز السهم، مثل: KFH أو NBK أو ZAIN")
    a.add_argument("--json", action="store_true", help="مخرجات بصيغة JSON")
    a.add_argument("--telegram", action="store_true", help="إرسال الملخص عبر تيليجرام")
    a.set_defaults(func=cmd_analyze)
    return p


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
