# -*- coding: utf-8 -*-
"""ريلا تشغيلة ٥١ — محرّك «جلسة متداول» على ملفّات محتوى ٥١.

لا محرّك جديد هنا: `run32_desk` هو المحرّك المعتمد (§11)، وهذا الملف
يمدّه بمُحمِّل محتواه ونافذتَي الريلين، ثم يبني الاثنين بنمطين مختلفين
كي لا يتشابه ريلان في يومٍ واحد.

    python3 run51_reel.py            # يبني الاثنين
    python3 run51_reel.py <slug>
"""
import json, os, sys

import run32_desk as D

HERE = os.path.dirname(os.path.abspath(__file__))
CONT = os.path.normpath(os.path.join(HERE, "..", "content"))


def load(slug):
    with open(os.path.join(CONT, f"run51_{slug}.json"), encoding="utf-8") as f:
        C = json.load(f)
    C.setdefault("kw", C["car"]["cta"]["keyword"])
    C.setdefault("gtitle", C["car"]["title"])
    C.setdefault("geyebrow", "دليل — " + C["car"]["eyebrow"])
    return C


def reels():
    """وحدات الريل في التشغيلة، ونمط كلٍّ منها كما أثبته `--preflight`."""
    out = {}
    for fn in sorted(os.listdir(CONT)):
        if not (fn.startswith("run51_") and fn.endswith(".json")):
            continue
        slug = fn[len("run51_"):-len(".json")]
        C = json.load(open(os.path.join(CONT, fn), encoding="utf-8"))
        if C.get("media") == "reel":
            out[slug] = C.get("arch")
    return out


def main(slugs=None):
    D.LOAD = load
    plan = reels()
    for slug in (slugs or list(plan)):
        # `win_idx=None` مقصود: المحرّك يقرأ النافذة من `C["window"]` ولا
        # يقيّدها بنفسه. القيد واحدٌ للوحدة كلها في `run51_factory` —
        # وتقييده هنا أيضاً يجعل الوحدة تصدّ نفسها عند البناء الثاني.
        D.build(slug, win_idx=None, arch=plan[slug])


if __name__ == "__main__":
    main(sys.argv[1:] or None)
