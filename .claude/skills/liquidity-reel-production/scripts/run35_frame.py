# -*- coding: utf-8 -*-
"""تشغيلة ٣٥ — كاروسيل «الفريم والوقت المتاح» + دليله.

البنية تتبع §198: الكاروسيل **ثلاث صفحات** (غلاف داكن · الجارت البطل ·
نداء الفعل)، والشرح المكثّف كله في دليل من ١٦ صفحة.

الجارتات **حقيقية** من `raw_windows` (برنت · تنفيذ ٣ دقائق)، بعد أن
عادت التعبئة وامتلأ المخزون — فلا تخطيطي هنا ولا سلايد مؤجَّل.

الجارت البطل هو **زمن الصفقة**: ثماني شمعات من الدخول إلى الهدف = أربع
وعشرون دقيقة. وهو رقم مقيس على الشموع، وهو نفسه موضوع الوحدة: الفريم
يحدّد كم دقيقة يجب أن تكون حاضراً.

    python3 run35_frame.py
"""
import json, os

from car_common import CW, brandbar, counter, dots, cover_slide, build_carousel
from guide_build import build_guide
from run15_build import X15
from run31_build import X_HERO, dk, hero_page
import chart_registry
import run15_charts as RC15
import run31_charts as RC
import run35_charts as SC

HERE = os.path.dirname(os.path.abspath(__file__))
CONT = os.path.normpath(os.path.join(HERE, "..", "content"))
RUN_ID = "run35-frame-2026-08-07"
SLUG = "frame"
TOTAL = 3
HERO = SC.c_plan                        # البطل: الصفقة وزمنها
CH = {f.__name__: f for f in SC.CASES}
TEAL_D = "#1E627A"


def load():
    with open(os.path.join(CONT, f"run35_{SLUG}.json"), encoding="utf-8") as f:
        return json.load(f)


def build_car(C):
    car = C["car"]
    ki = car.get("key_page", 0)
    RC15.set_minimal(True)
    cover = dk(HERO(700, 300))               # الغلاف يحمل الجارت البطل مصغّراً
    RC15.set_minimal(False)
    slides = [cover_slide(car["eyebrow"], car["title"], car["tag"], cover, total=TOTAL)]

    pg = car["pages"][min(ki, len(car["pages"]) - 1)]
    RC.set_scale(1.45)
    svg = HERO(1000, 950)
    RC.set_scale(1.0)
    pts = "".join(f'<p class="hpt">{t}</p>' for t in pg.get("bullets", [])[:2])
    slides.append(hero_page(2, f'<h1 class="ttl9">{pg["title"]}</h1>'
                               f'<div class="chartwrap">{svg}</div>{pts}'))

    cta = car["cta"]
    items = "".join(f'<div class="cti"><span class="ck8">{i+1}</span><p>{t}</p></div>'
                    for i, t in enumerate(cta["items"]))
    slides.append(f'''<div class="slide" {CW}>{counter(TOTAL, TOTAL)}{brandbar(True)}
      <div class="cta"><h1 class="big2">{cta["quote_a"]}<br><span style="color:{TEAL_D}">{cta["quote_b"]}</span></h1>
      <p class="tag2 center" style="margin-top:8px">{cta["tag"]}</p>
      <div class="ctabox">{items}</div>
      <div class="kwbox"><span>اكتب في التعليقات</span><b>«{cta["keyword"]}»</b></div>
      <p class="tag2 center">{cta["promise"]}</p>
      <p class="tag2 center" style="opacity:.75">{cta["share"]}</p></div>
      <div class="botmeta">لغرض تعليمي · <span dir="ltr">@liquidity.state</span></div>{dots(TOTAL, TOTAL)}</div>''')

    out = os.path.join(HERE, f"car35_{SLUG}.html")
    build_carousel(slides, f'{cta["keyword"]} — Liquidity State', out, extra_css=X15 + X_HERO)
    return out, len(slides)


def build_gd(C):
    gd = C["guide"]
    # كل جارت مربوط بصفحته بالاسم في ملف المحتوى، لا موزَّع بالتساوي: الصفحة
    # التي تشرح القاعين يجب أن تحمل جارت القاعين لا ما يصادفه العدّاد.
    pages, tk = [], 0
    for p_ in gd["pages"]:
        p = dict(title=p_["title"], paras=p_.get("paras", []))
        if p_.get("note"):
            p["note"] = p_["note"]
        if p_.get("chart"):
            p["svg"] = CH[p_["chart"]](880, 260); tk += 1
        pages.append(p)
    RC15.set_minimal(True)
    ghero = dk(HERO(700, 320))
    RC15.set_minimal(False)
    cfg = dict(eyebrow="دليل — " + C["car"]["eyebrow"], title=C["car"]["title"],
               keyword=C["car"]["cta"]["keyword"], subtitle=gd["subtitle"],
               hero=ghero, pages=pages, outro_title=gd["outro_title"],
               outro_items=gd["outro_items"])
    out = os.path.join(HERE, f"guide35_{SLUG}.html")
    return out, build_guide(cfg, out), tk


def _unregister():
    """يمسح قيود هذه التشغيلة قبل إعادة البناء — وإلا صدّت التشغيلةُ نفسَها
    عند أول إعادة بناء بحجّة أن البذرة مستعملة."""
    p = os.path.join(HERE, "used_charts.json")
    d = json.load(open(p, encoding="utf-8"))
    for k in ("synthetic", "real"):
        d[k] = [e for e in d[k] if e.get("video") != RUN_ID]
    json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


def main():
    C = load()
    _unregister()
    W = SC.W
    chart_registry.assert_fresh_real(SC.D["sym"], SC.EXEC,
                                     f'{SC.D["anchor_utc"][:10]} {W[0]["d"][11:]}',
                                     f'{SC.D["anchor_utc"][:10]} {W[-1]["d"][11:]}',
                                     label=f"run35-{SLUG}")
    car, ns = build_car(C)
    gpath, ng, tk = build_gd(C)
    chart_registry.register_real(RUN_ID, SC.D["sym"], SC.EXEC,
                                 f'{SC.D["anchor_utc"][:10]} {W[0]["d"][11:]}',
                                 f'{SC.D["anchor_utc"][:10]} {W[-1]["d"][11:]}',
                                 label=f"run35-{SLUG}")
    print(f'كاروسيل {ns} صفحات · دليل {ng} صفحة ({tk} جارتات) · نافذة حقيقية '
          f'{SC.D["sym"]} · {SC.EXEC} · {SC.D["anchor_utc"]} · '
          f'صفقة {SC.BARS} شمعات = {SC.MINUTES} دقيقة')
    return car, gpath


if __name__ == "__main__":
    main()
