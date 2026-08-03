# -*- coding: utf-8 -*-
# تشغيلة 4 — تحديث بوستات اليوم بالمقاسات الجديدة:
#   3 كاروسيلات «٥ صفقات» (فومو، باكتست، لوت) + 5 أدلة 15–20 صفحة
# النصوص من content/run4_copy.json (ايجنت صانع المحتوى)
import json, os
from car_common import (CW, brandbar, counter, swipe, dots, cover_slide, cta_slide,
                        dkmap, build_carousel, INK, TEAL, TEAL_D, RED, GREY, MUTE)
from reel_build import gen, chart, htext, hend
from guide_build import build_guide
import chart_registry

HERE = os.path.dirname(os.path.abspath(__file__))
CP = json.load(open(os.path.join(HERE, "..", "content", "run4_copy.json")))
C = json.load(open(os.path.join(HERE, "sheet_candidates.json")))

# ================= مولد جارت الصفقة (تخطيطي — سيناريوهات متمايزة) =================
# كل سيناريو: anchors تشكل القصة + فهارس مراسي معلومة للماركب — 30 شمعة (قاعدة §4)
N = 30

def _story(kind, v):
    """أشكال القصص. v = متغير السيلويت (0/1) للتنويع بين الكاروسيلات."""
    if kind == "chase":          # اندفاع ← ملاحقة بالقمة ← تنفس يطق الستوب ← يكمل بدونك
        a = [(0, 10.0), (4, 10.8 + v*0.5), (8, 10.2), (14, 17.5 + v*0.8), (16, 17.0),
             (20, 14.4 - v*0.3), (23, 15.2), (29, 21.5 + v*0.9)]
        return a, dict(xe=14, stop=20, cont=29)
    if kind == "retest":         # اندفاع ← رجعة للزون ← دخلة صح ← هدف
        a = [(0, 10.0), (5, 9.4 + v*0.4), (9, 10.1), (14, 16.8 + v*0.6), (17, 15.4),
             (21, 12.9 - v*0.4), (23, 13.3), (29, 19.8 + v*1.0)]
        return a, dict(iz=8, xe=14, ie=21, tgt=29)
    if kind == "skip":           # اندفاع ما رجع — الصح إنك ما تلحقه
        a = [(0, 10.0), (6, 10.6), (10, 11.0 - v*0.3), (16, 16.2), (21, 17.8), (29, 22.6 + v*0.7)]
        return a, dict(iz=9, top=16)
    if kind == "loss":           # كسر هابط ياخذ صفقة شراء غلط — خسارة نظيفة بحجمها
        a = [(0, 18.0), (5, 18.6), (9, 17.2), (13, 17.9 - v*0.3), (18, 13.8), (23, 12.4), (29, 13.6)]
        return a, dict(ie=12, brk=18)
    raise ValueError(kind)

def _zone_from(w, i):
    return w[i]["o"], w[i]["l"]

def trade_chart(kind, seed, outcome, ok, v=0, extra=None, Wd=920, H=470):
    anchors, ix = _story(kind, v)
    chart_registry.assert_fresh_synthetic(seed, anchors, label=f"run4-{kind}")
    w = gen(anchors, N, seed, wick=0.85)
    ymin = min(c["l"] for c in w); ymax = max(c["h"] for c in w)
    pad = (ymax - ymin) * 0.08; ymin -= pad * 1.7; ymax += pad * 1.2
    svg, x, y, slot = chart(w, Wd, H, ymin, ymax, grid=4, pl=12, pr=16, pt=20, pb=14, body=0.6)
    r = 11
    if kind == "chase":
        XE, ST, CO = ix["xe"], ix["stop"], ix["cont"]
        hx, hy = x(XE), y(w[XE]["h"])
        svg += (f'<line x1="{hx-r:.1f}" y1="{hy-r:.1f}" x2="{hx+r:.1f}" y2="{hy+r:.1f}" stroke="{RED}" stroke-width="3.2" stroke-linecap="round"/>'
                f'<line x1="{hx-r:.1f}" y1="{hy+r:.1f}" x2="{hx+r:.1f}" y2="{hy-r:.1f}" stroke="{RED}" stroke-width="3.2" stroke-linecap="round"/>')
        svg += htext(hx, hy - 20, "هني أغروك تلحق", RED, 19)
        sl = w[ST]["l"]
        svg += f'<line x1="{x(XE)-slot*0.6:.1f}" y1="{y(sl):.1f}" x2="{x(ST)+slot*0.7:.1f}" y2="{y(sl):.1f}" stroke="{RED}" stroke-width="1.8" stroke-dasharray="7 5"/>'
        svg += htext(x(ST), y(sl) + 26, "طق الستوب", RED, 18)
        svg += htext(x(CO)-slot*1.4, y(w[CO]["h"]) - 16, "وكمّل بدونك", TEAL_D, 18)
    elif kind == "retest":
        IZ, XE, IE, TG = ix["iz"], ix["xe"], ix["ie"], ix["tgt"]
        ZT, ZB = _zone_from(w, IZ)
        zx0 = x(IZ) - slot*0.5; zx1 = x(min(IE+3, N-1)) + slot*0.5
        svg += (f'<rect x="{zx0:.1f}" y="{y(ZT):.1f}" width="{zx1-zx0:.1f}" height="{y(ZB)-y(ZT):.1f}" fill="{TEAL}" style="opacity:0.16"/>'
                f'<rect x="{zx0:.1f}" y="{y(ZT):.1f}" width="{zx1-zx0:.1f}" height="{y(ZB)-y(ZT):.1f}" fill="none" stroke="{TEAL_D}" stroke-width="1.2"/>')
        svg += htext((zx0+zx1)/2, y(ZB) + 24, "زون الانطلاق", TEAL_D, 17)
        hx, hy = x(XE), y(w[XE]["h"])
        svg += (f'<line x1="{hx-r:.1f}" y1="{hy-r:.1f}" x2="{hx+r:.1f}" y2="{hy+r:.1f}" stroke="{RED}" stroke-width="3" stroke-linecap="round"/>'
                f'<line x1="{hx-r:.1f}" y1="{hy+r:.1f}" x2="{hx+r:.1f}" y2="{hy-r:.1f}" stroke="{RED}" stroke-width="3" stroke-linecap="round"/>')
        svg += htext(hx, hy - 20, "هني أغروك", RED, 18)
        svg += f'<circle cx="{x(IE):.1f}" cy="{y(w[IE]["l"]):.1f}" r="13" fill="none" stroke="{TEAL_D}" stroke-width="3"/>'
        svg += htext(x(IE), y(w[IE]["l"]) + 34, "الدخلة الصح", TEAL_D, 19)
        if extra and extra.get("stop_pts"):     # قوس مسافة الستوب (كاروسيل اللوت / RR)
            sv = w[IE]["l"] - (ymax - ymin) * extra.get("stop_frac", 0.06)
            bx = x(IE) + slot * 1.6
            svg += (f'<line x1="{bx:.1f}" y1="{y(w[IE]["l"]):.1f}" x2="{bx:.1f}" y2="{y(sv):.1f}" stroke="{INK}" stroke-width="1.8"/>'
                    f'<line x1="{bx-6:.1f}" y1="{y(w[IE]["l"]):.1f}" x2="{bx+6:.1f}" y2="{y(w[IE]["l"]):.1f}" stroke="{INK}" stroke-width="1.8"/>'
                    f'<line x1="{bx-6:.1f}" y1="{y(sv):.1f}" x2="{bx+6:.1f}" y2="{y(sv):.1f}" stroke="{INK}" stroke-width="1.8"/>'
                    f'<line x1="{x(IE)-slot*0.6:.1f}" y1="{y(sv):.1f}" x2="{bx+6:.1f}" y2="{y(sv):.1f}" stroke="{RED}" stroke-width="1.6" stroke-dasharray="6 5"/>')
            svg += htext(bx + 14, (y(w[IE]["l"]) + y(sv))/2 + 6, extra["stop_pts"], INK, 18, anchor="start")
        svg += htext(x(TG)-slot*1.2, y(w[TG]["h"]) - 16, "الهدف", TEAL_D, 18)
    elif kind == "skip":
        IZ, TP = ix["iz"], ix["top"]
        ZT, ZB = _zone_from(w, IZ)
        zx0 = x(IZ) - slot*0.5; zx1 = x(N-1) + slot*0.5
        svg += (f'<rect x="{zx0:.1f}" y="{y(ZT):.1f}" width="{zx1-zx0:.1f}" height="{y(ZB)-y(ZT):.1f}" fill="{TEAL}" style="opacity:0.14"/>'
                f'<rect x="{zx0:.1f}" y="{y(ZT):.1f}" width="{zx1-zx0:.1f}" height="{y(ZB)-y(ZT):.1f}" fill="none" stroke="{TEAL_D}" stroke-width="1.2" stroke-dasharray="7 5"/>')
        svg += htext((zx0+zx1)/2, y(ZB) + 24, "زونك — ما رجع له", TEAL_D, 17)
        svg += htext(x(TP), y(w[TP]["h"]) - 18, "راحت؟ خلها تروح", INK, 19)
    elif kind == "loss":
        IE, BK = ix["ie"], ix["brk"]
        svg += f'<circle cx="{x(IE):.1f}" cy="{y(w[IE]["h"]):.1f}" r="12" fill="none" stroke="{RED}" stroke-width="2.6"/>'
        svg += htext(x(IE), y(w[IE]["h"]) - 20, "دخلة شراء", RED, 18)
        sl = min(c["l"] for c in w[IE:BK])
        svg += f'<line x1="{x(IE)-slot*0.6:.1f}" y1="{y(w[BK]["h"]):.1f}" x2="{x(BK)+slot*0.7:.1f}" y2="{y(w[BK]["h"]):.1f}" stroke="{RED}" stroke-width="1.8" stroke-dasharray="7 5"/>'
        svg += htext(x(BK), y(w[BK]["h"]) - 16, "الستوب — خروج نظيف", RED, 18)
    # شارة النتيجة
    col = TEAL_D if ok else RED
    svg += (f'<g><rect x="{Wd-268}" y="16" width="252" height="46" fill="{"#EAF3F5" if ok else "#F8ECEC"}" stroke="{col}" stroke-width="1.4"/>'
            + htext(Wd-142, 47, outcome, col, 21) + '</g>')
    return svg + "</svg>", (seed, anchors)

# ================= سلايد الصفقة =================
def trade_slide(idx, total, n, t, chart_svg, strip_html=""):
    return f'''<div class="slide" {CW}>
  {counter(idx, total)}
  {brandbar(True)}
  <div class="cont">
    <div class="numrow"><span class="num">{n}</span><h2 class="ttl">{t["title"]}</h2></div>
    <div class="tlabel">{t["label"]}</div>
    <div class="chartwrap">{chart_svg}</div>
    {strip_html}
    <div class="rulerow"><span class="rn x">✗</span><p>{t["bait"]}</p></div>
    <div class="rulerow"><span class="rn">✓</span><p>{t["right"]}</p></div>
    <div class="note">{t["because"]}</div>
  </div>
  {swipe()}{dots(idx, total)}
</div>'''

def quote_cta_slide(idx, total, cc, kw):
    return f'''<div class="slide" {CW}>
  {counter(idx, total)}
  {brandbar(True)}
  <div class="cta">
    <h1 class="big2">{cc["quote_a"]}<br><span style="color:{TEAL_D}">{cc["quote_b"]}</span></h1>
    <p class="tag2 center" style="margin-top:10px">{cc["quote_tag"]}</p>
    <div class="kwbox"><span>اكتب بالتعليقات</span><b>«{kw}»</b></div>
    <p class="tag2 center">{cc["promise"]}</p>
    <p class="tag2 center" style="opacity:.75">{cc["share_line"]}</p>
  </div>
  <div class="botmeta">لغرض تعليمي · @liquidity.state</div>
</div>'''

X4CSS = f'''
.tlabel{{display:inline-block;border:1.5px solid {TEAL_D};color:{TEAL_D};font-size:23px;font-weight:800;padding:6px 18px;margin:2px 0 12px;border-radius:2px}}
.kwbox{{margin:34px auto 18px;border:1.5px solid {TEAL_D};background:#EAF3F5;padding:20px 44px;text-align:center;border-radius:2px}}
.kwbox span{{display:block;font-size:24px;color:{GREY};font-weight:700}}
.kwbox b{{font-size:44px;color:{TEAL_D};font-weight:900}}
'''

def strip(txt):
    return f'<div class="note" style="text-align:center;font-weight:800">{txt}</div>'

# ================= بناء الكاروسيلات الثلاثة =================
# خطة المرئيات: (kind, seed, ok, variant, extra) لكل صفقة — بذور جديدة كلياً (4100+)
PLANS = {
 "fomo":     [("chase", 4101, False, 0, None), ("retest", 4102, True, 0, None),
              ("skip", 4103, True, 0, None),   ("chase", 4104, False, 1, None),
              ("retest", 4105, True, 1, {"stop_pts": "ستوب قريب", "stop_frac": 0.05})],
 "backtest": [("retest", 4111, True, 0, None), ("chase", 4112, False, 0, None),
              ("loss", 4113, False, 0, None),  ("retest", 4114, True, 1, None),
              ("skip", 4115, True, 1, None)],
 "lot":      [("retest", 4121, True, 0, {"stop_pts": "30 نقطة", "stop_frac": 0.045}),
              ("retest", 4122, True, 1, {"stop_pts": "90 نقطة", "stop_frac": 0.115}),
              ("retest", 4123, True, 0, {"stop_pts": "50 نقطة", "stop_frac": 0.07}),
              ("loss", 4124, False, 0, None),
              ("retest", 4125, True, 1, {"stop_pts": "60 نقطة", "stop_frac": 0.08})],
}
KW = {"fomo": "فومو", "backtest": "باكتست", "lot": "لوت"}
TOTAL = 7
registered = []

def build_car5(key):
    cc = CP[key]["car5"]
    plan = PLANS[key]
    hero_svg, _ = trade_chart(plan[1][0], plan[1][1] + 900, cc["trades"][1]["outcome"], plan[1][2], plan[1][3], plan[1][4], Wd=700, H=330)
    SL = [cover_slide(cc["cover_eyebrow"], cc["cover_title"], cc["cover_tag"], dkmap(hero_svg), total=TOTAL)]
    for i, (t, pl) in enumerate(zip(cc["trades"], plan)):
        kind, seed, ok, v, extra = pl
        svg, reg = trade_chart(kind, seed, t["outcome"], ok, v, extra)
        registered.append(reg + (f'run4-{key}-t{i+1}',))
        sh = ""
        if key == "lot" and t.get("calc"): sh = strip(t["calc"])
        if key == "backtest" and t.get("tally"): sh = strip(t["tally"])
        SL.append(trade_slide(2 + i, TOTAL, str(i + 1), t, svg, sh))
    SL.append(quote_cta_slide(TOTAL, TOTAL, cc, KW[key]))
    build_carousel(SL, f'{KW[key]} — Liquidity State', os.path.join(HERE, f"car4_{key}.html"), extra_css=X4CSS)
    print(f"car4_{key}.html: {len(SL)} slides")

for k in ["fomo", "backtest", "lot"]:
    build_car5(k)

# ================= الأدلة الخمسة (15–20 صفحة) =================
TITLES = {"istidraj": ("دليل — SMC", "الاستدراج<br>قبل الحركة", "استدراج"),
          "nus": ("دليل — SMC", "البريميوم<br>والديسكاونت", "نص"),
          "fomo": ("دليل — نفسية التداول", "علاج<br>الفومو", "فومو"),
          "backtest": ("دليل — أساسيات", "الباك تست<br>الصح", "باكتست"),
          "lot": ("دليل — إدارة المخاطر", "حجم العقد<br>وحسبة الـ1%", "لوت")}

# مرئيات صفحات الصفقات بالأدلة: نفس مولد الصفقات (بذور جديدة لكل دليل)
GSEED = {"istidraj": 4200, "nus": 4230, "fomo": 4260, "backtest": 4290, "lot": 4320}
GKINDS = ["retest", "chase", "skip", "loss", "retest"]

from run3_build import istidraj_static, nus_static, fomo_chase, BT_TABLE, LOT_CARD

HEROES = {"istidraj": dkmap(istidraj_static(760, 360)), "nus": dkmap(nus_static(760, 360)),
          "fomo": dkmap(fomo_chase(700, 330)),
          "backtest": dkmap(BT_TABLE.replace("#FBF9F5", "#0D2430").replace("#DED8CC", "#1E627A").replace("#0F2E3C", "#ECF3F6").replace("#5C6C73", "#8FA6AF")),
          "lot": dkmap(LOT_CARD.replace("#FBF9F5", "#0D2430").replace("#DED8CC", "#1E627A").replace("#0F2E3C", "#ECF3F6").replace("#5C6C73", "#8FA6AF"))}

for key, (eyeb, ttl, kw) in TITLES.items():
    g = CP[key]["guide15"]
    pages = []
    tseed = GSEED[key]; tk = 0
    for i, pg in enumerate(g["pages"]):
        p = dict(title=pg["title"])
        if pg.get("lead"): p["lead"] = pg["lead"]
        if pg.get("paras"): p["paras"] = pg["paras"]
        if pg.get("rules"): p["rules"] = [dict(t=r["t"], bad=bool(r.get("bad"))) for r in pg["rules"]]
        if pg.get("note"): p["note"] = pg["note"]
        # صفحات الصفقات (يحددها الايجنت بحقل trade=true) تاخذ جارت
        if pg.get("trade") and tk < 5:
            kind = GKINDS[tk]
            seed = tseed + tk
            # قصتا الذهب والداو الحقيقيتان: الصفقة الأولى بجارتهما الحقيقي
            if key == "istidraj" and tk == 0:
                p["svg"] = istidraj_static(880, 380); p["ticker"] = "الذهب · 15 دقيقة · 2026-05-29"
            elif key == "nus" and tk == 0:
                p["svg"] = nus_static(880, 380); p["ticker"] = "الداو جونز · فريم الساعة · 2025-10-29"
            else:
                ok = kind in ("retest", "skip")
                svg, reg = trade_chart(kind, seed, pg.get("outcome", "—"), ok, tk % 2, None, Wd=880, H=380)
                registered.append(reg + (f'run4-guide-{key}-t{tk+1}',))
                p["svg"] = svg
            tk += 1
        pages.append(p)
    cfg = dict(eyebrow=eyeb, title=ttl, keyword=kw, subtitle=g["subtitle"], hero=HEROES[key],
               pages=pages, outro_title=g["outro_title"], outro_items=g["outro_items"])
    n = build_guide(cfg, os.path.join(HERE, f"guide4_{key}.html"))
    print(f"guide4_{key}.html", n, "pages")

chart_registry.register_synthetic("run4-2026-08-03", [(s, a, l) for s, a, l in registered])
print("registered", len(registered), "synthetic charts")
