# -*- coding: utf-8 -*-
"""تشغيلة ٦١ — بناء الريلين على محرّك «جلسة متداول» (§11 · §12).

`run32_desk` يقرأ محتواه من `run31_build.load` أي من `content/run31_*.json`،
وملفّات هذه التشغيلة `content/run61_*.json`. والمحرّك ترك لذلك مقبضاً
(`LOAD`) — فهذا ما يستعمله هذا السائق، ومعه فهرسُ النافذة ونمطُها
المتحقّق (كلاهما مقيسٌ بـ`run32_desk.preflight` قبل الكتابة):

    ريل اليوم → النافذة ٦١ · نمط `zone` — البتكوين ٣٠ دقيقة، منطقة طلب

والنمطان مختلفان عمداً (§11: «النمط يُختار من فئة النافذة فلا يتشابه
ريلان من فئتين»): النافذة ٥٧ فئتها `consol` ولا تثبت عليها إلا `zone`،
والنافذة ٥٣ فئتها `chan` وتثبت عليها. وكلٌّ منهما اجتاز بوابة الأسباب
الثلاثة المقيسة.

    python3 run61_reels.py            # يبني HTML الريلين
"""
import json, os, sys

import run32_desk as D

HERE = os.path.dirname(os.path.abspath(__file__))
CONT = os.path.normpath(os.path.join(HERE, "..", "content"))

# السلَق الثاني يُقرأ من ملفّه: الوحدة الفنية الثانية موضوعها جديد
# فاسمها يأتي مع نصّها، ولا يُثبَّت هنا قبل أن يُكتب.
PLAN = {}
ARCH_OF_WIN = {61: "zone"}


def load(slug):
    """محمّل محتوى ٦٠ — بنفس عقد `run31_build.load`."""
    with open(os.path.join(CONT, f"run61_{slug}.json"), encoding="utf-8") as f:
        C = json.load(f)
    C.setdefault("kw", C["car"]["cta"]["keyword"])
    C.setdefault("gtitle", C["car"]["title"])
    C.setdefault("geyebrow", "دليل — " + C["car"]["eyebrow"])
    return C


def _reel_units():
    """وحدات الريل في مجلّد المحتوى — تُعرف بـ`media == "reel"` لا بقائمة."""
    out = {}
    for fn in sorted(os.listdir(CONT)):
        if not (fn.startswith("run61_") and fn.endswith(".json")):
            continue
        with open(os.path.join(CONT, fn), encoding="utf-8") as f:
            C = json.load(f)
        if C.get("media") == "reel":
            out[fn[len("run61_"):-len(".json")]] = C
    return out


def main(slugs=None):
    D.LOAD = load
    units = _reel_units()
    for slug in (slugs or list(units)):
        C = units[slug]
        win = C["window"]
        arch = PLAN.get(slug, (win, ARCH_OF_WIN.get(win)))[1]
        assert arch, f"{slug}: نمط النافذة {win} غير معروف — قِسه بـpreflight أولاً"
        D.build(slug, win_idx=win, arch=arch)


if __name__ == "__main__":
    main(sys.argv[1:] or None)
