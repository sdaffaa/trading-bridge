# -*- coding: utf-8 -*-
"""فحص مخزون النوافذ ووسم الفاسد منه.

**العيب في المصدر**: `sheet_scan.py` يقصّ نافذة العرض بسقف ٤٢ شمعة
(`we = min(len(cs)-1, ee+3, ws+41)`) ثم يعيد ترقيم الفهارس على بداية
النافذة — بلا تحقّق أن شمعة الدخول وقعت داخل القصّ. فحين يطول السحب بين
القمة والعودة تخرج `ir` من المصفوفة (`ir=50` وطول النافذة ٤٢): الشمعة
ليست ناقصة الترقيم بل **غير موجودة**، فلا تُصلَح بإعادة ترقيم.

**لا يُحذف المدخل**: `run31_run.PLAN` يشير إلى النوافذ **بفهرسها** في
هذا الملف، فحذف مدخل يزحزح ما بعده ويُسند لوحدةٍ نافذةَ غيرها. البديل
وسمٌ صريح `bad: [أسباب]` يقرأه `win()` فيرفض، والفهارس تبقى ثابتة.

    python3 fix_candidates.py --check     # يطبع ولا يكتب
    python3 fix_candidates.py --fix       # يكتب الوسم بعد نسخة احتياطية
"""
import json, os, shutil, sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "sheet_candidates.json")
IDX_KEYS = ("iH", "bk", "iob", "ir", "i1", "i2", "ipdl",
            "ca", "cb", "rt", "rb", "chi", "clo")
MIN_AFTER = 4          # شمعات بعد الدخول — دونها لا نتيجة تُروى


def problems(rec):
    """كل ما يجعل المدخل غير قابل للاستعمال، مع سببه."""
    out = []
    n = len(rec.get("w", []))
    if n < 20:
        out.append(f"النافذة {n} شمعة فقط")
    for k in IDX_KEYS:
        if k not in rec:
            continue
        v = rec[k]
        for j in (v if isinstance(v, list) else [v]):
            if not isinstance(j, int) or not (0 <= j < n):
                out.append(f"{k}={j} خارج المدى [0,{n})")
    # ترتيب القصّة: القمة قبل الكسر، والمنطقة قبله أو عنده، والعودة بعدها
    if not out and all(k in rec for k in ("iH", "bk", "iob", "ir")):
        if not (rec["iH"] < rec["bk"] and rec["iob"] <= rec["bk"] < rec["ir"]):
            out.append(f'ترتيب غير منطقي: iH={rec["iH"]} bk={rec["bk"]} '
                       f'iob={rec["iob"]} ir={rec["ir"]}')
        elif n - 1 - rec["ir"] < MIN_AFTER:
            out.append(f'{n - 1 - rec["ir"]} شمعات فقط بعد الدخول — لا تكفي للنتيجة')
    return out


def main(write):
    C = json.load(open(SRC, encoding="utf-8"))
    bad = 0
    for i, rec in enumerate(C):
        p = problems(rec)
        if p:
            bad += 1
            rec["bad"] = p
            print(f'✗ {i:>2} {rec["cls"]:<7} {rec["sym"]:<10} {rec["tf"]:<4} '
                  f'{rec.get("date","")} — {" · ".join(p)}')
        else:
            rec.pop("bad", None)
    good = [r for r in C if not r.get("bad")]
    print(f'\nسليم {len(good)} · موسوم بالفساد {bad} من {len(C)}')
    print("الفئات الصالحة:", dict(Counter(r["cls"] for r in good)))
    if write:
        shutil.copy(SRC, SRC + ".bak")
        json.dump(C, open(SRC, "w", encoding="utf-8"), ensure_ascii=False)
        print(f'كُتب الوسم على {len(C)} مدخلاً · الأصل في {os.path.basename(SRC)}.bak')


if __name__ == "__main__":
    main(write="--fix" in sys.argv)
