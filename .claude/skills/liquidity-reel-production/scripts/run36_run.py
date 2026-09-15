# -*- coding: utf-8 -*-
"""تشغيلة ٣٦ — مصنع المحتوى اليومي: خمس وحدات، لكلٍّ دليل PDF بكلمتها.

البنية والمحرّكات كما في `run31_build` حرفياً (§11 · §198): الكاروسيل ثلاث
صفحات، والدليل ست عشرة صفحة، والريل ≤22.4 ثانية بمؤثرات فقط (§12) عبر
`run32_desk`. الذي يخصّ هذه التشغيلة ملفُّ محتواها ونوافذُها ومعرّفُها.

**التركيبة المسلَّمة أربعة كاروسيلات وريلٌ واحد لا اثنان.** والسبب مقيس
لا مقدَّر: بوابة `run32_desk` تشترط ثلاثة أسباب متحقّقة على النافذة قبل
أن يُبنى ريل («ألّا يكون تحليلاً بسيطاً» — شرط فهد). ومن ستّ نوافذ حرّة
جُلبت اليوم لم تجتز البوابةَ إلا واحدة؛ الباقيتان من فئة السحب أعطتا
سببين فقط، واثنتان لم يبلغ فيهما السعر هدف ٢R في حساب التذكرة. والبوابة
لا تُخفَّض لتكتمل تركيبة — تُنقَص الوحدة ويُذكر ذلك.

    python3 run36_run.py            # الوحدات الخمس
    python3 run36_run.py <slug> ... # وحدة بعينها
"""
import json, os, sys

import run31_build as B

HERE = os.path.dirname(os.path.abspath(__file__))
RUN_ID = "run36-daily-2026-08-08"

# slug: (فهرس النافذة في sheet_candidates، الصيغة، الفئة)
# النوافذ الستّ الحرّة جُلبت اليوم بمسح جديد (SI · CL · ES · EUR · NZD ·
# BTC · ETH · USDCAD)، ولا تتكرّر أداة+فريم+تاريخ بين وحدتين.
PLAN = {
    "disp":    (16, "reel",     "فنية"),      # BTC ساعة 2025-12-28 — النافذة الوحيدة التي اجتازت بوابة الريل
    "miss":    (18, "carousel", "فنية"),      # BTC ساعة 2025-09-02
    "irhaq":   (14, "carousel", "نفسية"),     # ES ٣٠ دقيقة 2026-07-01
    "laebeen": (19, "carousel", "أساسية"),    # ES ساعة 2025-09-03
    "saqf":    (15, "carousel", "مالية"),     # ETH ساعة 2026-05-10
}


def _patch():
    """يعيد توجيه محرّك ٣١ إلى ملفات هذه التشغيلة ومعرّفها.

    النسخ الكامل للمحرّك كان يعني نسخ خطأين محتملين بدل واحد. فبدل ذلك
    يُعاد استعمال `run31_build` كما هو، ويُبدَّل فيه ثلاثة أشياء فقط:
    بادئة ملف المحتوى، وبادئة الملفات المخرَجة، ومعرّف التسجيل."""
    B.RUN_ID = RUN_ID
    B.WINDOWS.update({k: v for k, (v, _m, _c) in PLAN.items()})
    B.MEDIA.update({k: m for k, (_w, m, _c) in PLAN.items()})

    _load = B.load

    def load(slug):
        with open(os.path.join(B.CONT, f"run36_{slug}.json"), encoding="utf-8") as f:
            C = json.load(f)
        C.setdefault("kw", C["car"]["cta"]["keyword"])
        C.setdefault("gtitle", C["car"]["title"])
        C.setdefault("geyebrow", "دليل — " + C["car"]["eyebrow"])
        C.setdefault("window", B.WINDOWS[slug])
        C.setdefault("media", B.MEDIA.get(slug, "reel" if C.get("reel") else "carousel"))
        return C

    B.load = load

    # أسماء المخرجات: `car31_x.html` → `car36_x.html` وكذلك الدليل.
    _bc, _bg = B.build_carousel_unit, B.build_guide_unit
    _car = B.build_carousel
    _guide = B.build_guide

    def car_out(slides, title, out, **kw):
        return _car(slides, title, out.replace("car31_", "car36_"), **kw)

    def guide_out(cfg, out):
        return _guide(cfg, out.replace("guide31_", "guide36_"))

    B.build_carousel = car_out
    B.build_guide = guide_out

    # جارتات الدليل تُربط بصفحات «الحالة …» بالترتيب لا تُوزَّع بالتساوي:
    # التوزيع بالعدّاد كان يضع رسم «الدخول المبكر» على صفحةٍ تشرح رسم
    # المنطقة، فيقول الرسمُ غير ما يقوله النصّ فوقه.
    _bgu = B.build_guide_unit

    def build_guide_unit(slug, C, r, ok):
        gd = C["guide"]
        case_idx = [i for i, p in enumerate(gd["pages"])
                    if p["title"].startswith("الحالة")]
        pages, tk = [], 0
        for i, p_ in enumerate(gd["pages"]):
            p = dict(title=p_["title"], paras=p_.get("paras", []))
            if p_.get("note"):
                p["note"] = p_["note"]
            if tk < len(ok) and i in case_idx:
                p["svg"] = ok[tk](r, 880, 260); tk += 1
            pages.append(p)
        B.RC15.set_minimal(True)
        ghero = B.dk(ok[0](r, 700, 320))
        B.RC15.set_minimal(False)
        cfg = dict(eyebrow=C["geyebrow"], title=C["gtitle"], keyword=C["kw"],
                   subtitle=gd["subtitle"], hero=ghero, pages=pages,
                   outro_title=gd["outro_title"], outro_items=gd["outro_items"])
        n = B.build_guide(cfg, os.path.join(B.HERE, f"guide31_{slug}.html"))
        return n, tk

    B.build_guide_unit = build_guide_unit


def main(slugs=None):
    _patch()
    B._unregister()
    import run32_desk as D            # يقرأ الوحدة عبر `run31_build.load` المرقَّع
    done, reels, failed = [], [], []
    for k in (slugs or list(PLAN)):
        try:
            B.build_unit(k)
            done.append(k)
        except Exception as e:
            print(f"✗ {k}: {type(e).__name__}: {e}"); failed.append((k, str(e)[:60])); continue
        if PLAN[k][1] != "reel":
            continue
        try:
            D.build(k); reels.append(k)
        except Exception as e:
            print(f"✗ ريل {k}: {type(e).__name__}: {e}"); failed.append((k + " (ريل)", str(e)[:60]))
    print(f'\nوحدات {len(done)}/{len(slugs or PLAN)} · ريلات {len(reels)}')
    if reels:
        print("للرندر والمؤثرات:  python3 run32_post.py " + " ".join(reels))
    for k, why in failed:
        print(f"  ✗ {k}: {why}")
    return done, reels, failed


if __name__ == "__main__":
    main(sys.argv[1:] or None)
