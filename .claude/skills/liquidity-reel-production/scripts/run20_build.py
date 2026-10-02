# -*- coding: utf-8 -*-
"""وحدة «الفريمين» — كاروسيل 8 صفحات + دليل PDF. نفس معمار run15."""
import json, os
from car_common import (CW, brandbar, counter, swipe, dots, cover_slide, build_carousel,
                        dkmap, INK, TEAL, TEAL_D, GREY, CARDBD)
from guide_build import build_guide
import run20_charts as RC
import chart_registry

HERE = os.path.dirname(os.path.abspath(__file__))
CONT = os.path.join(HERE, "..", "content")
TOTAL = 8
RUN_ID = "run20-frames-2026-08-04"
KW, GTITLE, GEYEB = "فريم", "فريم القرار<br>وفريم التنفيذ", "دليل — منهج السيولة"

X20 = f'''
.cont.dense{{top:168px;bottom:148px;gap:18px;justify-content:center}}
.cont.dense .rulerow p{{font-size:26px;line-height:1.46}}
.ttl8{{font-size:46px;font-weight:900;color:{INK};line-height:1.16;text-align:center;letter-spacing:-.5px}}
.lead8{{font-size:29px;line-height:1.55;color:{GREY};font-weight:500;text-align:center}}
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
.cti p{{font-size:28px;font-weight:700;color:{GREY}}}
.ck8{{width:44px;height:44px;flex:none;display:flex;align-items:center;justify-content:center;
  border-radius:50%;border:2.5px solid {TEAL};color:{TEAL_D};font-size:21px;font-weight:900}}
'''

def bullets(items):
    return "".join(f'<div class="rulerow"><span class="rn">{i+1}</span><p>{t}</p></div>'
                   for i, t in enumerate(items))

def page(idx, body):
    return (f'<div class="slide" {CW}>{counter(idx, TOTAL)}{brandbar(True)}'
            f'<div class="cont dense">{body}</div>{swipe()}{dots(idx, TOTAL)}</div>')

def trim(lead, n=170):
    if len(lead) <= n: return lead
    cut = lead[:n].rfind("،")
    return lead[:cut if cut > 95 else n].rstrip("،. ") + "."

def _unregister():
    p = os.path.join(HERE, "used_charts.json")
    d = json.load(open(p, encoding="utf-8"))
    n = len(d["synthetic"])
    d["synthetic"] = [e for e in d["synthetic"] if e.get("video") != RUN_ID]
    if n != len(d["synthetic"]):
        json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

def build():
    C = json.load(open(os.path.join(CONT, "run20_frames.json"), encoding="utf-8"))
    car, gd = C["car"], C["guide"]
    charts = RC.CAR_CHARTS

    slides = [cover_slide(car["eyebrow"], car["title"], car["tag"],
                          dkmap(RC.HERO(700, 300)), total=TOTAL)]
    for i, pg in enumerate(car["pages"]):
        has = i < len(charts)
        bl = pg.get("bullets", [])
        if has:
            body_chart = f'<div class="chartwrap">{charts[i](880, 250)}</div>'
            keep, lead = bl[:2], trim(pg["lead"])
        else:
            body_chart = ""
            keep = bl[:4] if sum(len(t) for t in bl[:4]) < 470 else bl[:3]
            lead = pg["lead"]
        slides.append(page(2 + i, f'<h1 class="ttl8">{pg["title"]}</h1>'
                                 f'<p class="lead8">{lead}</p>' + body_chart + bullets(keep)))
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
    build_carousel(slides, f"{KW} — Liquidity State",
                   os.path.join(HERE, "car20_frames.html"), extra_css=X20)

    pages, tk = [], 0
    for pg in gd["pages"]:
        p = dict(title=pg["title"], paras=pg.get("paras", []))
        if pg.get("rules"):
            p["rules"] = [dict(t=r["t"], bad=bool(r.get("bad"))) for r in pg["rules"]]
        if pg.get("note"): p["note"] = pg["note"]
        if pg["title"].strip().startswith("الحالة") and tk < len(charts):
            p["svg"] = charts[tk](880, 260); tk += 1
        pages.append(p)
    cfg = dict(eyebrow=GEYEB, title=GTITLE, keyword=KW, subtitle=gd["subtitle"],
               hero=dkmap(RC.HERO(700, 320)), pages=pages,
               outro_title=gd["outro_title"], outro_items=gd["outro_items"])
    n = build_guide(cfg, os.path.join(HERE, "guide20_frames.html"))
    print(f"car20: {len(slides)} slides | guide20: {n} pages | charts: {tk}")

if __name__ == "__main__":
    _unregister()
    build()
    uniq, seen = [], set()
    for seed, anch, label in RC.CHARTS:
        if seed not in seen:
            seen.add(seed); uniq.append((seed, anch, label))
    chart_registry.register_synthetic(RUN_ID, uniq)
    print("registered charts:", len(uniq))
