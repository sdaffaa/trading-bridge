# -*- coding: utf-8 -*-
"""تشغيلة ٥٩ — بناء الريلين على محرّك «جلسة متداول» (§11 · §12).

`run32_desk` يقرأ محتواه من `run31_build.load` أي من `content/run31_*.json`،
وملفّات هذه التشغيلة `content/run59_*.json`. والمحرّك ترك لذلك مقبضاً
(`LOAD`) «بدل نسخ المحرّك كلّه لأجل مسار ملف» — فهذا ما يستعمله هذا
السائق، ومعه فهرسُ النافذة ونمطُها المتحقّق:

    nafida → النافذة ٤٨ · نمط `chan` — قناة هابطة تُخترَق
    thania → النافذة ٥٠ · نمط `zone` — منطقة أصل بعد كسر هيكل

والنمطان مختلفان عمداً (§11: «النمط يُختار من فئة النافذة فلا يتشابه
ريلان من فئتين»)، وكلٌّ منهما اجتاز بوابة الأسباب الثلاثة.

    python3 run59_reels.py            # يبني HTML الريلين
"""
import json, os, sys

import run32_desk as D

HERE = os.path.dirname(os.path.abspath(__file__))
CONT = os.path.normpath(os.path.join(HERE, "..", "content"))

PLAN = {"nafida": (48, "chan"), "thania": (50, "zone")}


def load(slug):
    """محمّل محتوى ٥٩ — بنفس عقد `run31_build.load`."""
    with open(os.path.join(CONT, f"run59_{slug}.json"), encoding="utf-8") as f:
        C = json.load(f)
    C.setdefault("kw", C["car"]["cta"]["keyword"])
    C.setdefault("gtitle", C["car"]["title"])
    C.setdefault("geyebrow", "دليل — " + C["car"]["eyebrow"])
    return C


def main(slugs=None):
    D.LOAD = load
    for slug in (slugs or list(PLAN)):
        win, arch = PLAN[slug]
        C = load(slug)
        assert C["window"] == win, f'{slug}: نافذة الملف {C["window"]} لا {win}'
        D.build(slug, win_idx=win, arch=arch)


if __name__ == "__main__":
    main(sys.argv[1:] or None)
