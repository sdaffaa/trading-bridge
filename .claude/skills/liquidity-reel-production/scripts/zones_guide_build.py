# -*- coding: utf-8 -*-
"""دليل «ست مناطق على الجارت» — يعيد استخدام جارتات ريل الشبكة بحجم الصفحة."""
import json, os
import grid_reel as G
from guide_build import build_guide
from car_common import dkmap

HERE = os.path.dirname(os.path.abspath(__file__))
CONT = os.path.join(HERE, "..", "content")

# (الرسم، الحكم، لون الحكم) — نفس ترتيب المناطق في الريل
ARTS = [(G.art_fvg, "انتظر العودة", G.TEAL_D), (G.art_ob, "شراء من المنطقة", G.TEAL_D),
        (G.art_breaker, "بيع من المنطقة", G.RED), (G.art_eqh, "سيولة… لا هدف", G.RED),
        (G.art_eq, "اشترِ تحت النصف", G.TEAL_D), (G.art_sweep, "ادخل بعد السحب", G.TEAL_D)]

def page_chart(item, Wd=700, H=310):
    """يوسّع رسم الخانة إلى مقاس صفحة الدليل مع شارة الحكم داخل الإطار."""
    fn, verdict, vcol = item
    cw, ch = G.CW_, G.CH_
    G.CW_, G.CH_ = Wd, H
    try:
        body = fn(0, 0)
    finally:
        G.CW_, G.CH_ = cw, ch
    bw = len(verdict) * 15 + 30
    badge = (f'<rect x="16" y="14" width="{bw}" height="40" fill="{"#EAF3F5" if vcol == G.TEAL_D else "#F8ECEC"}" '
             f'stroke="{vcol}" stroke-width="1.6"/>'
             + G.htext(16 + bw/2, 42, verdict, vcol, 23))
    return (f'<svg class="chartsvg" viewBox="0 0 {Wd} {H}" width="{Wd}" height="{H}" '
            f'xmlns="http://www.w3.org/2000/svg">{body}{badge}</svg>')

def hero():
    cw, ch = G.CW_, G.CH_
    G.CW_, G.CH_ = 700, 330
    try:
        body = G.art_ob(0, 0)
    finally:
        G.CW_, G.CH_ = cw, ch
    return dkmap(f'<svg class="chartsvg" viewBox="0 0 700 330" width="700" height="330" '
                 f'xmlns="http://www.w3.org/2000/svg">{body}</svg>')

if __name__ == "__main__":
    gd = json.load(open(os.path.join(CONT, "zones_guide.json"), encoding="utf-8"))["guide"]
    pages, k = [], 0
    for pg in gd["pages"]:
        p = dict(title=pg["title"], paras=pg.get("paras", []))
        if pg.get("rules"):
            p["rules"] = [dict(t=r["t"], bad=bool(r.get("bad"))) for r in pg["rules"]]
        if pg.get("note"):
            p["note"] = pg["note"]
        if pg["title"].strip().startswith("المنطقة") and k < 6:
            p["svg"] = page_chart(ARTS[k]); k += 1
        pages.append(p)
    cfg = dict(eyebrow="دليل — خريطة الجارت", title="ست مناطق<br>على الجارت",
               keyword="مناطق", subtitle=gd["subtitle"], hero=hero(), pages=pages,
               outro_title=gd["outro_title"], outro_items=gd["outro_items"])
    n = build_guide(cfg, os.path.join(HERE, "guide_zones.html"))
    print("guide_zones.html:", n, "pages | charts:", k)
