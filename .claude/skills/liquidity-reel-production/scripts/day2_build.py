# -*- coding: utf-8 -*-
"""بانى وحدات اليوم الثلاث: كاروسيل 8 صفحات + دليل 16 صفحة لكل موضوع (V2).
يقرأ نصوص الايجنتات من content/day2_*.json ويستخدم جارتات day2_charts.
"""
import json, os, sys
from car_common import (CW, brandbar, counter, swipe, dots, cover_slide, build_carousel,
                        dkmap, INK, TEAL, TEAL_D, RED, GREY, CARDBD)
from guide_build import build_guide
import day2_charts as DC
import chart_registry

HERE = os.path.dirname(os.path.abspath(__file__))
CONT = os.path.join(HERE, "..", "content")

UNITS = {
 "internal": dict(file="day2_internal.json", kw="داخلية",
                  gtitle="السيولة الداخلية<br>والخارجية", geyebrow="دليل — مفاهيم السيولة",
                  hero=lambda: DC.internal_chart(700, 330, hero=True),
                  page_charts=[DC.internal_chart, DC.internal_wrong, DC.internal_right],
                  guide_charts=[lambda: DC.internal_chart(880, 260, seed=5111),
                                lambda: DC.internal_wrong(880, 260, seed=5112),
                                lambda: DC.internal_right(880, 260, seed=5113),
                                lambda: DC.internal_chart(880, 260, seed=5114),
                                lambda: DC.internal_right(880, 260, seed=5115)]),
 "confirm":  dict(file="day2_confirm.json", kw="تأكيد",
                  gtitle="ما هو التأكيد<br>فعلياً؟", geyebrow="دليل — نموذج التنفيذ",
                  hero=lambda: DC.confirm_chart(700, 330, hero=True),
                  page_charts=[DC.confirm_chart, DC.confirm_wrong, DC.confirm_choch],
                  guide_charts=[lambda: DC.confirm_chart(880, 260, seed=5211),
                                lambda: DC.confirm_wrong(880, 260, seed=5212),
                                lambda: DC.confirm_choch(880, 260, seed=5213),
                                lambda: DC.confirm_chart(880, 260, seed=5214),
                                lambda: DC.confirm_wrong(880, 260, seed=5215)]),
 "breaker":  dict(file="day2_breaker.json", kw="بريكر",
                  gtitle="البريكر<br>بلوك", geyebrow="دليل — مفاهيم SMC",
                  hero=lambda: DC.breaker_chart(700, 330, hero=True),
                  page_charts=[DC.breaker_chart, DC.breaker_ob, DC.breaker_wrong],
                  guide_charts=[lambda: DC.breaker_chart(880, 260, seed=5311),
                                lambda: DC.breaker_ob(880, 260, seed=5312),
                                lambda: DC.breaker_wrong(880, 260, seed=5313),
                                lambda: DC.breaker_chart(880, 260, seed=5314),
                                lambda: DC.breaker_ob(880, 260, seed=5315)]),
}

TOTAL = 8

def bullets(items):
    return "".join(f'<div class="rulerow"><span class="rn">{i+1}</span><p>{t}</p></div>'
                   for i, t in enumerate(items))

def page(idx, body):
    return (f'<div class="slide" {CW}>{counter(idx, TOTAL)}{brandbar(True)}'
            f'<div class="cont dense">{body}</div>{swipe()}{dots(idx, TOTAL)}</div>')

X8 = f'''
.cont.dense{{top:172px;bottom:150px;gap:20px;justify-content:center}}
.cont.dense .rulerow p{{font-size:26px;line-height:1.46}}
.cont.dense .note{{font-size:27px}}
.ttl8{{font-size:48px;font-weight:900;color:{INK};line-height:1.16;text-align:center;letter-spacing:-.5px}}
.ttl8 b{{color:{TEAL_D}}}
.lead8{{font-size:30px;line-height:1.55;color:{GREY};font-weight:500;text-align:center}}
.lead8 b{{color:{INK};font-weight:800}}
.kwbox{{margin:30px auto 16px;border:1.5px solid {TEAL_D};background:#EAF3F5;padding:20px 44px;text-align:center}}
.kwbox span{{display:block;font-size:24px;color:{GREY};font-weight:700}}
.kwbox b{{font-size:44px;color:{TEAL_D};font-weight:900}}
.ctabox{{width:100%;background:#FBF9F5;border:1px solid {CARDBD};padding:10px 26px;
  box-shadow:0 16px 40px rgba(15,46,60,0.10)}}
.cti{{display:flex;align-items:center;gap:16px;padding:17px 4px;border-bottom:1px solid #EDE7DB}}
.cti:last-child{{border-bottom:none}}
.cti p{{font-size:29px;font-weight:700;color:{GREY}}} .cti p b{{font-weight:900;color:{TEAL_D}}}
.ck8{{width:44px;height:44px;flex:none;display:flex;align-items:center;justify-content:center;
  border-radius:50%;border:2.5px solid {TEAL};color:{TEAL_D};font-size:21px;font-weight:900}}
'''

def build_unit(key):
    u = UNITS[key]
    with open(os.path.join(CONT, u["file"]), encoding="utf-8") as f:
        C = json.load(f)
    car, gd = C["car"], C["guide"]
    # ── الكاروسيل ──
    slides = [cover_slide(car["eyebrow"], car["title"], car["tag"], dkmap(u["hero"]()), total=TOTAL)]
    for i, pg in enumerate(car["pages"]):
        has_chart = i < len(u["page_charts"])
        lead = pg["lead"]
        bl = pg.get("bullets", [])
        note = pg.get("note", "")
        if has_chart:
            # صفحة بجارت: تمهيد مختصر + بندان فقط (السعة البصرية أهم من الكم)
            if len(lead) > 165:
                cut = lead[:165].rfind("،")
                lead = lead[:cut if cut > 90 else 165].rstrip("،. ") + "."
            keep, note = bl[:2], ""
            chart_html = f'<div class="chartwrap">{u["page_charts"][i](880, 250)}</div>'
        else:
            keep = bl[:4] if sum(len(t) for t in bl[:4]) < 460 else bl[:3]
            chart_html = ""
        body = (f'<h1 class="ttl8">{pg["title"]}</h1>'
                f'<p class="lead8">{lead}</p>'
                + chart_html + bullets(keep)
                + (f'<div class="note">{note}</div>' if note else ""))
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
    build_carousel(slides, f'{u["kw"]} — Liquidity State', os.path.join(HERE, f"car_day2_{key}.html"), extra_css=X8)
    print(f"car_day2_{key}.html: {len(slides)} slides")

    # ── الدليل ──
    pages, tk = [], 0
    for pg in gd["pages"]:
        p = dict(title=pg["title"], paras=pg.get("paras", []))
        if pg.get("rules"):
            p["rules"] = [dict(t=r["t"], bad=bool(r.get("bad"))) for r in pg["rules"]]
        if pg.get("note"):
            p["note"] = pg["note"]
        if pg["title"].strip().startswith("الصفقة") and tk < len(u["guide_charts"]):
            p["svg"] = u["guide_charts"][tk]()
            tk += 1
        pages.append(p)
    cfg = dict(eyebrow=u["geyebrow"], title=u["gtitle"], keyword=u["kw"], subtitle=gd["subtitle"],
               hero=dkmap(u["hero"]()), pages=pages,
               outro_title=gd["outro_title"], outro_items=gd["outro_items"])
    n = build_guide(cfg, os.path.join(HERE, f"guide_day2_{key}.html"))
    print(f"guide_day2_{key}.html: {n} pages | charts in guide: {tk}")

if __name__ == "__main__":
    keys = sys.argv[1:] or list(UNITS)
    for k in keys:
        build_unit(k)
    chart_registry.register_synthetic("day2-2026-08-04", DC.CHARTS)
    print("registered charts:", len(DC.CHARTS))
