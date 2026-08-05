# -*- coding: utf-8 -*-
"""تشغيلة 24 — ثلاث وحدات نفسية: احتمالات · مبكر · تردد.

🔒 بنية جديدة (أمر فهد 2026-08-05): الكاروسيل **ثلاث صفحات فقط**
   ١ غلاف داكن · ٢ الجارت البطل بدرسه · ٣ نداء الفعل بالكلمة المفتاحية
   والشرح المكثّف كله ينتقل إلى دليل الـPDF (١٦ صفحة بخمسة جارتات).
   الكاروسيل يفتح الشهية، والـPDF يعلّم.
"""
import json, os, sys
from car_common import (CW, brandbar, counter, dots, cover_slide, build_carousel,
                        dkmap, INK, TEAL, TEAL_D, RED, GREY, CARDBD)
from guide_build import build_guide
from run15_build import X15
import run24_charts as RC
import chart_registry
import run15_charts as RC15

TOTAL = 3

def hero_page(idx, body):
    # الووردمارك في شريط العدّاد نفسه: حضور للهوية بلا اقتطاع من ارتفاع الجارت
    return (f'<div class="slide" {CW}>{counter(idx, TOTAL)}'
            f'<div class="hwm2">LIQUIDITY STATE</div>'
            f'<div class="cont hero">{body}</div>{dots(idx, TOTAL)}</div>')

X_HERO = '''
.ttl9{font-size:44px;font-weight:900;color:#0F2E3C;line-height:1.14;text-align:center;letter-spacing:-.5px}
.ttl9 b{color:#1E627A}
.hpt{font-size:25px;font-weight:700;color:#5C6C73;text-align:center;line-height:1.4;margin-top:2px}
.hpt b{color:#0F2E3C;font-weight:900}
.hwm2{position:absolute;top:64px;right:80px;z-index:6;font-size:20px;font-weight:700;
  letter-spacing:5px;color:#1E627A;opacity:.72}
'''

HERE = os.path.dirname(os.path.abspath(__file__))
CONT = os.path.join(HERE, "..", "content")

def dk(svg):
    """dkmap لا يغطي خلفية بطاقة الرسم ولا حشوات الشارة، فتبقى فاتحة فوق الغلاف الداكن."""
    svg = dkmap(svg)
    for a, b in [("#FBF9F5", "#08131C"),
                 ("#EAF3F5", "rgba(67,212,220,0.10)"),
                 ("#F8ECEC", "rgba(224,86,86,0.14)")]:
        svg = svg.replace(a, b)
    return svg

UNITS = {
    "prob":  dict(kw="احتمالات", cat="نفسية",
                  gtitle="صفقة واحدة<br>لا تحكم عليك", geyebrow="دليل — عقلية الاحتمالات"),
    "early": dict(kw="مبكر", cat="نفسية",
                  gtitle="الخروج<br>قبل الهدف", geyebrow="دليل — علم نفس التنفيذ"),
    "hesit": dict(kw="تردد", cat="نفسية",
                  gtitle="التردد<br>عند الإشارة", geyebrow="دليل — علم نفس التنفيذ"),
}

def build_unit(key):
    u = UNITS[key]
    with open(os.path.join(CONT, f"run24_{key}.json"), encoding="utf-8") as f:
        C = json.load(f)
    car, gd = C["car"], C["guide"]
    charts = RC.CAR_CHARTS[key]

    # ── ١) الغلاف الداكن ──
    slides = [cover_slide(car["eyebrow"], car["title"], car["tag"],
                          dk(RC.HERO[key](700, 300)), total=TOTAL)]

    # ── ٢) الجارت البطل: الحالة الأقوى في الوحدة (يحددها key_page) ──
    ki = car.get("key_page", 0)
    pg = car["pages"][ki]
    RC15.set_scale(1.45)
    svg = charts[ki](1000, 950)
    RC15.set_scale(1.0)
    pts = "".join(f'<p class="hpt">{t}</p>' for t in pg.get("bullets", [])[:2])
    slides.append(hero_page(2, f'<h1 class="ttl9">{pg["title"]}</h1>'
                               f'<div class="chartwrap">{svg}</div>{pts}'))

    # ── ٣) نداء الفعل: بقية الحالات الأربع داخل الدليل ──
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
    build_carousel(slides, f'{u["kw"]} — Liquidity State',
                   os.path.join(HERE, f"car24_{key}.html"), extra_css=X15 + X_HERO)

    # ── الدليل: يحمل الشرح المكثّف والحالات الخمس كلها ──
    pages, tk = [], 0
    for p_ in gd["pages"]:
        p = dict(title=p_["title"], paras=p_.get("paras", []))
        if p_.get("rules"):
            p["rules"] = [dict(t=r["t"], bad=bool(r.get("bad"))) for r in p_["rules"]]
        if p_.get("note"):
            p["note"] = p_["note"]
        if tk < len(charts) and p_["title"].strip().startswith("الصفقة"):
            p["svg"] = charts[tk](880, 260); tk += 1
        pages.append(p)
    cfg = dict(eyebrow=u["geyebrow"], title=u["gtitle"], keyword=u["kw"],
               subtitle=gd["subtitle"], hero=dk(RC.HERO[key](700, 320)), pages=pages,
               outro_title=gd["outro_title"], outro_items=gd["outro_items"])
    n = build_guide(cfg, os.path.join(HERE, f"guide24_{key}.html"))
    print(f"{key:<6} car24: {len(slides)} slides | guide24: {n} pages | charts: {tk}")

RUN_ID = "run24-psy-2026-08-05"

def _unregister():
    """يسمح بإعادة البناء: يشطب تسجيل التشغيلة السابقة قبل إعادة توليد الجارتات."""
    p = os.path.join(HERE, "used_charts.json")
    d = json.load(open(p, encoding="utf-8"))
    n = len(d["synthetic"])
    d["synthetic"] = [e for e in d["synthetic"] if e.get("video") != RUN_ID]
    if n != len(d["synthetic"]):
        json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

if __name__ == "__main__":
    _unregister()
    for k in (sys.argv[1:] or list(UNITS)):
        build_unit(k)
    uniq, seen = [], set()
    for seed, anch, label in RC.CHARTS:
        if seed not in seen:
            seen.add(seed); uniq.append((seed, anch, label))
    chart_registry.register_synthetic(RUN_ID, uniq)
    print("registered charts:", len(uniq))
