# -*- coding: utf-8 -*-
"""تشغيلة ٥٢ — أربعة كاروسيلات، خمس صفحات لكلٍّ، عن أربعة نماذج دخول.

🔒 طلب فهد 2026-08-11: «صمملي ٤ كاروسيلات من خمس صفحات لكل كاروسيل لدخول
صفقات مختلفة» — فالبنية هنا **خمس صفحات** لا ثلاثاً كبنية المصنع اليومي
(§11)، لأن الطلب صريح والدرس يحتاج ثلاث حالات لا حالةً واحدة:

    ١ غلاف داكن (هوك + الجارت البطل مصغّراً)
    ٢ الحالة الأولى — الجارت البطل كبيراً
    ٣ الحالة الثانية
    ٤ الحالة الثالثة
    ٥ نداء الفعل بالكلمة المفتاحية

كل حالة تُربط بصفحتها **بالاسم** في ملف المحتوى (`case`) لا بالترتيب:
نافذةٌ تسقط منها حالة تُعلن الخطأ بدل أن تُزحزح الجارتات صفحةً فتصير
الصورة تشرح درساً غير درسها.

والنافذة حقيقية حرّة من `sheet_candidates.json`، تُفحص بالسجل قبل البناء
وتُقيَّد بعده — نافذة لكل كاروسيل، وأربع أدوات مختلفة.

    python3 run52_entries.py [slug ...]
"""
import json, os, sys

from car_common import (CW, brandbar, counter, dots, cover_slide,
                        build_carousel)
from run15_build import X15
from run31_build import X_HERO, dk
import run15_charts as RC15
import run31_charts as RC

HERE = os.path.dirname(os.path.abspath(__file__))
CONT = os.path.normpath(os.path.join(HERE, "..", "content"))
RUN_ID = "run52-entries-2026-08-11"
TOTAL = 5
TEAL_D = "#1E627A"


def units():
    out = {}
    for fn in sorted(os.listdir(CONT)):
        if fn.startswith("run52_") and fn.endswith(".json"):
            slug = fn[len("run52_"):-len(".json")]
            with open(os.path.join(CONT, fn), encoding="utf-8") as f:
                out[slug] = json.load(f)
    return out


def pick(ok, name):
    for f in ok:
        if f.__name__ == name:
            return f
    raise RuntimeError(f"الحالة {name} لا تثبت على هذه النافذة: "
                       + ", ".join(f.__name__ for f in ok))


def chart_page(idx, pg, r, fn, hero=False):
    """صفحة جارت: عنوان ← الرسم ← سطران. البطل أكبر والباقي على مقاسه."""
    RC.set_no_title(True)                    # العنوان في <h1> الصفحة
    if hero:
        RC.set_scale(1.45)
        svg = fn(r, 1000, 950)
        RC.set_scale(1.0)
    else:
        RC.set_scale(1.30)
        svg = fn(r, 1000, 760)
        RC.set_scale(1.0)
    RC.set_no_title(False)
    pts = "".join(f'<p class="hpt">{t}</p>' for t in pg.get("bullets", [])[:2])
    return (f'<div class="slide" {CW}>{counter(idx, TOTAL)}'
            f'<div class="hwm2">LIQUIDITY STATE</div>'
            f'<div class="cont hero">'
            f'<h1 class="ttl9">{pg["title"]}</h1>'
            f'<div class="chartwrap">{svg}</div>{pts}'
            # بلا زرّ «اسحب» على صفحات الجارت: `.cont.hero` ينزل إلى 74
            # بكسل من القاع، والزرّ مثبّت هناك — فيقع فوق سطرَي الخلاصة.
            # النقاط وحدها تكفي دليلاً على أن بعدها صفحة.
            f'</div>{dots(idx, TOTAL)}</div>')


def cta_page(C):
    cta = C["car"]["cta"]
    head = C.get("close", {}).get("title") or C["car"]["title"]
    return f'''<div class="slide" {CW}>{counter(TOTAL, TOTAL)}{brandbar(True)}
      <div class="cta"><h1 class="big2">{head}</h1>
      <p class="tag2 center" style="margin-top:8px">{cta["line"]}</p>
      <div class="kwbox"><span>اكتب في التعليقات</span><b>«{cta["keyword"]}»</b></div>
      <p class="tag2 center">{cta["promise"]}</p>
      <p class="tag2 center" style="opacity:.75">{cta["share"]}</p></div>
      <div class="botmeta">لغرض تعليمي · <span dir="ltr">@liquidity.state</span></div>{dots(TOTAL, TOTAL)}</div>'''


def build(slug, C):
    r, ok, dropped = RC.unit_charts(C["window"])
    RC.claim_fresh(r, f"run52-{slug}")
    car = C["car"]
    pages = car["pages"][:3]
    assert len(pages) == 3, f"{slug}: {len(pages)} صفحات جارت والمطلوب ثلاث"
    fns = [pick(ok, p["case"]) for p in pages]

    RC15.set_minimal(True)
    cover = dk(fns[0](r, 700, 300))
    RC15.set_minimal(False)
    slides = [cover_slide(car["eyebrow"], car["title"], car["tag"], cover, total=TOTAL)]
    for i, (pg, fn) in enumerate(zip(pages, fns)):
        slides.append(chart_page(2 + i, pg, r, fn, hero=(i == 0)))
    slides.append(cta_page(C))

    assert len(slides) == TOTAL, f"{len(slides)} صفحة والمعلن {TOTAL}"
    out = os.path.join(HERE, f"car52_{slug}.html")
    build_carousel(slides, f'{C["keyword"]} — Liquidity State', out,
                   extra_css=X15 + X_HERO)
    RC.register(RUN_ID, r, f"run52-{slug}")
    print(f'{slug:<10} {len(slides)} صفحات · كلمة «{C["keyword"]}» · '
          f'حالات {", ".join(p["case"] for p in pages)} · نافذة {r["slug"]}'
          + ("" if not dropped else f' · سقط {len(dropped)}'))
    return out


def _unregister():
    p = os.path.join(HERE, "used_charts.json")
    d = json.load(open(p, encoding="utf-8"))
    for k in ("synthetic", "real"):
        d[k] = [e for e in d[k] if e.get("video") != RUN_ID]
    json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


def main(slugs=None):
    U = units()
    _unregister()
    for slug in (slugs or list(U)):
        try:
            build(slug, U[slug])
        except Exception as e:
            print(f"✗ {slug}: {type(e).__name__}: {e}")


if __name__ == "__main__":
    main(sys.argv[1:] or None)
