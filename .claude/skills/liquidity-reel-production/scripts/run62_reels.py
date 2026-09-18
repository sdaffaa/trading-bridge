# -*- coding: utf-8 -*-
"""تشغيلة ٦٢ — بناء الريل الواحد على محرّك «جلسة متداول» (§11 · §12).

`run32_desk` يقرأ محتواه من `run31_build.load` أي من `content/run31_*.json`،
وملفّات هذه التشغيلة `content/run62_*.json`. والمحرّك ترك لذلك مقبضاً
(`LOAD`) — فهذا ما يستعمله هذا السائق، ومعه فهرسُ النافذة ونمطُها
المتحقّق (كلاهما مقيسٌ بـ`run32_desk.preflight` قبل الكتابة):

    ريل اليوم → النافذة ٦٥ · نمط `sweep` — البتكوين ٣٠ دقيقة، قمّتان
    متساويتان فرقُهما ٢٫٨٪ من المدى وأربعة قيعان متلاصقة تحتهما

**وريلٌ واحد لا اثنان**: النافذة الحرّة الثانية (٦٤ · عقد الجنيه الآجل)
تسقط عند بوابة الخطة نفسها — `ترتيب الوقف/الدخول/الهدف غير سليم` لأن
هدف المضاعفين لم يتحقّق داخلها — فصارت كاروسيلاً، ولم يُبنَ ريلٌ ثانٍ
على سلسلةٍ تخطيطية: تذكرةُ الأمر تطبع أسعاراً، والسلسلة المولّدة بلا
أداةٍ ولا سعر (§11 البديلة).

    python3 run62_reels.py            # يبني HTML الريل
"""
import json, os, sys

import run32_desk as D

HERE = os.path.dirname(os.path.abspath(__file__))
CONT = os.path.normpath(os.path.join(HERE, "..", "content"))

PLAN = {}
ARCH_OF_WIN = {65: "sweep"}


def load(slug):
    """محمّل محتوى ٦٢ — بنفس عقد `run31_build.load`."""
    with open(os.path.join(CONT, f"run62_{slug}.json"), encoding="utf-8") as f:
        C = json.load(f)
    C.setdefault("kw", C["car"]["cta"]["keyword"])
    C.setdefault("gtitle", C["car"]["title"])
    C.setdefault("geyebrow", "دليل — " + C["car"]["eyebrow"])
    return C


def _reel_units():
    """وحدات الريل في مجلّد المحتوى — تُعرف بـ`media == "reel"` لا بقائمة."""
    out = {}
    for fn in sorted(os.listdir(CONT)):
        if not (fn.startswith("run62_") and fn.endswith(".json")):
            continue
        with open(os.path.join(CONT, fn), encoding="utf-8") as f:
            C = json.load(f)
        if C.get("media") == "reel":
            out[fn[len("run62_"):-len(".json")]] = C
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
