# -*- coding: utf-8 -*-
"""تشغيلة 23 — وحدة واحدة: كاروسيل 8 صفحات + دليل 16 صفحة (V2).
أمر معلّق أم تنفيذ فوري؟ (فئة: تنفيذ)
النصوص من content/run23_limit.json والجارتات من run23_charts.
"""
import json, os, sys
from car_common import (CW, brandbar, counter, swipe, dots, cover_slide, build_carousel,
                        dkmap, INK, TEAL, TEAL_D, RED, GREY, CARDBD)
from guide_build import build_guide
from run15_build import X15, page, bullets, trim, TOTAL
import run23_charts as RC
import chart_registry

HERE = os.path.dirname(os.path.abspath(__file__))
CONT = os.path.join(HERE, "..", "content")

def dk(svg):
    """dkmap لا يغطي خلفية بطاقة الرسم ولا حشوات الشارة، فتبقى فاتحة فوق الغلاف الداكن."""
    svg = dkmap(svg)
    for a, b in [("#FBF9F5", "#08131C"),                 # بطاقة الرسوم الحسابية
                 ("#EAF3F5", "rgba(67,212,220,0.10)"),   # شارة الحكم الإيجابي
                 ("#F8ECEC", "rgba(224,86,86,0.14)")]:   # شارة الحكم السلبي
        svg = svg.replace(a, b)
    return svg

UNITS = {
    "limit": dict(kw="ليمت", cat="تنفيذ",
                  gtitle="أمر معلّق<br>أم تنفيذ فوري؟", geyebrow="دليل — تنفيذ الصفقة"),
}

def build_unit(key):
    u = UNITS[key]
    with open(os.path.join(CONT, f"run23_{key}.json"), encoding="utf-8") as f:
        C = json.load(f)
    car, gd = C["car"], C["guide"]
    charts = RC.CAR_CHARTS[key]

    # ── الكاروسيل: غلاف داكن + 5 حالات بجارتاتها + خلاصة + CTA ──
    slides = [cover_slide(car["eyebrow"], car["title"], car["tag"],
                          dk(RC.HERO[key](700, 300)), total=TOTAL)]
    for i, pg in enumerate(car["pages"]):
        has_chart = i < len(charts)
        bl = pg.get("bullets", [])
        if has_chart:
            keep = bl[:2]
            chart_html = f'<div class="chartwrap">{charts[i](880, 250)}</div>'
            lead = trim(pg["lead"])
        else:
            keep = bl[:4] if sum(len(t) for t in bl[:4]) < 470 else bl[:3]
            chart_html, lead = "", pg["lead"]
        body = (f'<h1 class="ttl8">{pg["title"]}</h1><p class="lead8">{lead}</p>'
                + chart_html + bullets(keep))
        slides.append(page(2 + i, body))
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
                   os.path.join(HERE, f"car23_{key}.html"), extra_css=X15)

    # ── الدليل: الجارت يُلحق بصفحات «الصفقة …» بالترتيب ──
    pages, tk = [], 0
    for pg in gd["pages"]:
        p = dict(title=pg["title"], paras=pg.get("paras", []))
        if pg.get("rules"):
            p["rules"] = [dict(t=r["t"], bad=bool(r.get("bad"))) for r in pg["rules"]]
        if pg.get("note"):
            p["note"] = pg["note"]
        if tk < len(charts) and pg["title"].strip().startswith("الصفقة"):
            p["svg"] = charts[tk](880, 260); tk += 1
        pages.append(p)
    cfg = dict(eyebrow=u["geyebrow"], title=u["gtitle"], keyword=u["kw"],
               subtitle=gd["subtitle"], hero=dk(RC.HERO[key](700, 320)), pages=pages,
               outro_title=gd["outro_title"], outro_items=gd["outro_items"])
    n = build_guide(cfg, os.path.join(HERE, f"guide23_{key}.html"))
    print(f"{key:<5} car23: {len(slides)} slides | guide23: {n} pages | charts: {tk}")

RUN_ID = "run23-limit-2026-08-05"

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
    for seed, anch, label in RC.CHARTS:        # الجارت نفسه يُستعمل في الكاروسيل والدليل
        if seed not in seen:
            seen.add(seed); uniq.append((seed, anch, label))
    chart_registry.register_synthetic(RUN_ID, uniq)
    print("registered charts:", len(uniq))
