# -*- coding: utf-8 -*-
"""تشغيلة 15 — خمس وحدات كاملة: كاروسيل 8 صفحات + دليل 15 صفحة لكل موضوع (V2).
تشوك (فنية) · محروق (فنية) · آسيا (أساسية) · سبريد (مالية) · غرور (نفسية)
النصوص من content/run15_*.json والجارتات من run15_charts.
"""
import json, os, sys
from car_common import (CW, brandbar, counter, swipe, dots, cover_slide, build_carousel,
                        dkmap, INK, TEAL, TEAL_D, RED, GREY, CARDBD)
from guide_build import build_guide
import run15_charts as RC
import chart_registry

HERE = os.path.dirname(os.path.abspath(__file__))
CONT = os.path.join(HERE, "..", "content")
TOTAL = 8

UNITS = {
    "choch":  dict(kw="تشوك",  cat="فنية",
                   gtitle="تغيّر الطابع<br>(CHoCH)", geyebrow="دليل — هيكل السوق"),
    "burn":   dict(kw="محروق", cat="فنية",
                   gtitle="المنطقة<br>المحروقة", geyebrow="دليل — مناطق الطلب والعرض"),
    "asia":   dict(kw="آسيا",  cat="أساسية",
                   gtitle="نطاق الجلسة<br>الآسيوية", geyebrow="دليل — توقيت الجلسات"),
    "spread": dict(kw="سبريد", cat="مالية",
                   gtitle="السبريد<br>وتكلفة التنفيذ", geyebrow="دليل — تكلفة التداول"),
    "ego":    dict(kw="غرور",  cat="نفسية",
                   gtitle="الثقة الزائدة<br>بعد الأرباح", geyebrow="دليل — علم نفس التداول"),
}

def bullets(items):
    return "".join(f'<div class="rulerow"><span class="rn">{i+1}</span><p>{t}</p></div>'
                   for i, t in enumerate(items))

def page(idx, body):
    return (f'<div class="slide" {CW}>{counter(idx, TOTAL)}{brandbar(True)}'
            f'<div class="cont dense">{body}</div>{swipe()}{dots(idx, TOTAL)}</div>')

X15 = f'''
.cont.dense{{top:168px;bottom:148px;gap:18px;justify-content:center}}
.cont.dense .rulerow p{{font-size:26px;line-height:1.46}}
.ttl8{{font-size:46px;font-weight:900;color:{INK};line-height:1.16;text-align:center;letter-spacing:-.5px}}
.ttl8 b{{color:{TEAL_D}}}
.lead8{{font-size:29px;line-height:1.55;color:{GREY};font-weight:500;text-align:center}}
.lead8 b{{color:{INK};font-weight:800}}
.kwbox{{margin:28px auto 14px;border:1.5px solid {TEAL_D};background:#EAF3F5;padding:19px 44px;text-align:center}}
.kwbox span{{display:block;font-size:24px;color:{GREY};font-weight:700}}
.kwbox b{{font-size:44px;color:{TEAL_D};font-weight:900}}
.ctabox{{width:100%;background:#FBF9F5;border:1px solid {CARDBD};padding:10px 26px;
  box-shadow:0 16px 40px rgba(15,46,60,0.10)}}
.cta{{top:196px;bottom:178px;gap:22px}}
.cta .big2{{font-size:60px}}
.cta .tag2{{margin-top:6px;font-size:30px}}
.cti{{display:flex;align-items:center;gap:16px;padding:16px 4px;border-bottom:1px solid #EDE7DB}}
.cti:last-child{{border-bottom:none}}
.cti p{{font-size:28px;font-weight:700;color:{GREY}}} .cti p b{{font-weight:900;color:{TEAL_D}}}
.ck8{{width:44px;height:44px;flex:none;display:flex;align-items:center;justify-content:center;
  border-radius:50%;border:2.5px solid {TEAL};color:{TEAL_D};font-size:21px;font-weight:900}}
'''

def trim(lead, n=170):
    if len(lead) <= n:
        return lead
    cut = lead[:n].rfind("،")
    return lead[:cut if cut > 95 else n].rstrip("،. ") + "."

def build_unit(key):
    u = UNITS[key]
    with open(os.path.join(CONT, f"run15_{key}.json"), encoding="utf-8") as f:
        C = json.load(f)
    car, gd = C["car"], C["guide"]
    charts = RC.CAR_CHARTS[key]

    # ── الكاروسيل: غلاف داكن + 5 صفقات بجارتاتها + خلاصة + CTA ──
    slides = [cover_slide(car["eyebrow"], car["title"], car["tag"],
                          dkmap(RC.HERO[key](700, 300)), total=TOTAL)]
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
                   os.path.join(HERE, f"car15_{key}.html"), extra_css=X15)

    # ── الدليل: الجارت يُلحق بصفحات «الصفقة/الجلسة/اللحظة» بالترتيب ──
    pages, tk = [], 0
    for pg in gd["pages"]:
        p = dict(title=pg["title"], paras=pg.get("paras", []))
        if pg.get("rules"):
            p["rules"] = [dict(t=r["t"], bad=bool(r.get("bad"))) for r in pg["rules"]]
        if pg.get("note"):
            p["note"] = pg["note"]
        t = pg["title"].strip()
        if tk < len(charts) and (t.startswith("الصفقة") or t.startswith("الجلسة")
                                 or t.startswith("اللحظة")):
            p["svg"] = charts[tk](880, 260); tk += 1
        pages.append(p)
    cfg = dict(eyebrow=u["geyebrow"], title=u["gtitle"], keyword=u["kw"],
               subtitle=gd["subtitle"], hero=dkmap(RC.HERO[key](700, 320)), pages=pages,
               outro_title=gd["outro_title"], outro_items=gd["outro_items"])
    n = build_guide(cfg, os.path.join(HERE, f"guide15_{key}.html"))
    print(f"{key:<7} car15: {len(slides)} slides | guide15: {n} pages | charts: {tk}")

RUN_ID = "run15-2026-08-04"

def _unregister():
    """يسمح بإعادة البناء: يشطب تسجيل التشغيلة السابقة قبل إعادة توليد الجارتات."""
    import json as _j
    p = os.path.join(HERE, "used_charts.json")
    d = _j.load(open(p, encoding="utf-8"))
    n = len(d["synthetic"])
    d["synthetic"] = [e for e in d["synthetic"] if e.get("video") != RUN_ID]
    if n != len(d["synthetic"]):
        _j.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

if __name__ == "__main__":
    _unregister()
    keys = sys.argv[1:] or list(UNITS)
    for k in keys:
        build_unit(k)
    uniq, seen = [], set()
    for seed, anch, label in RC.CHARTS:           # الجارت نفسه يُستعمل في الكاروسيل والدليل
        if seed not in seen:
            seen.add(seed); uniq.append((seed, anch, label))
    chart_registry.register_synthetic(RUN_ID, uniq)
    print("registered charts:", len(uniq))
