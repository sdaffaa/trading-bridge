# -*- coding: utf-8 -*-
# تشغيلة المصنع 3 — 3 كاروسيلات (فومو، باكتست، لوت) + 5 أدلة، النصوص من run3_copy.json
import json, os
from car_common import (CW, brandbar, counter, swipe, dots, eyebrow, cover_slide, quote_slide,
                        cta_slide, sk, dkmap, build_carousel, htext, hend,
                        INK, TEAL, TEAL_D, RED, GREY, MUTE)
from run1_carousels import numbered, problem, rules, W
from reel_build import chart
from guide_build import build_guide

HERE = os.path.dirname(os.path.abspath(__file__))
CP = json.load(open(os.path.join(HERE, "..", "content", "run3_copy.json")))
C = json.load(open(os.path.join(HERE, "sheet_candidates.json")))

# ================= مرئيات =================
def fomo_chase(Wd=880, H=400):
    """دخلة اللحاق بالقمة vs دخلة الانتظار بالرجعة."""
    pts = [(0,4.2),(0.8,5.6),(1.5,4.6),(2.6,9.8),(3.4,12.6),(4.2,11.2),(5.0,9.0),(5.8,7.6),(6.6,9.9),(7.4,12.0),(8.2,14.2)]
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    x0,x1,y0,y1 = min(xs),max(xs),min(ys)-1.6,max(ys)+1.4
    mx = lambda v: 20+(v-x0)/(x1-x0)*(Wd-40); my = lambda v: 18+(y1-v)/(y1-y0)*(H-50)
    s = [f'<svg viewBox="0 0 {Wd} {H}" width="{Wd}" height="{H}" xmlns="http://www.w3.org/2000/svg">']
    s.append(f'<rect x="{mx(1.9):.0f}" y="{my(8.0):.0f}" width="{mx(6.9)-mx(1.9):.0f}" height="{my(6.6)-my(8.0):.0f}" fill="{TEAL}" opacity="0.16"/>')
    s.append(f'<rect x="{mx(1.9):.0f}" y="{my(8.0):.0f}" width="{mx(6.9)-mx(1.9):.0f}" height="{my(6.6)-my(8.0):.0f}" fill="none" stroke="{TEAL_D}" stroke-width="1"/>')
    p = " ".join(f"{mx(a):.1f},{my(b):.1f}" for a,b in pts)
    s.append(f'<polyline points="{p}" fill="none" stroke="{INK}" stroke-width="2.8" stroke-linecap="round" stroke-linejoin="round"/>')
    s.append(f'<circle cx="{mx(3.4):.1f}" cy="{my(12.6):.1f}" r="13" fill="none" stroke="{RED}" stroke-width="2.6"/>')
    s.append(htext(mx(3.3), my(13.9), "دخلة اللحاق — رأس الاندفاع", RED, 19))
    s.append(f'<line x1="{mx(3.4):.1f}" y1="{my(12.2):.1f}" x2="{mx(3.4):.1f}" y2="{my(7.9):.1f}" stroke="{RED}" stroke-width="2" stroke-dasharray="6 5"/>')
    s.append(htext(mx(4.55), my(6.1), "نزل عليك وانت شايل الخسارة", RED, 17))
    s.append(f'<circle cx="{mx(5.8):.1f}" cy="{my(7.6):.1f}" r="13" fill="none" stroke="{TEAL_D}" stroke-width="2.6"/>')
    s.append(htext(mx(6.3), my(5.0), "دخلة الانتظار — من الزون", TEAL_D, 19))
    return "".join(s)+"</svg>"

BT_TABLE = '''<table class="tblx" style="border-collapse:collapse;width:100%;background:#FBF9F5;border:1px solid #DED8CC">
<tr><th style="background:#1E627A;color:#fff;font-size:26px;font-weight:800;padding:13px">العينة</th><th style="background:#1E627A;color:#fff;font-size:26px;font-weight:800;padding:13px">الإصابة</th><th style="background:#1E627A;color:#fff;font-size:26px;font-weight:800;padding:13px">RR المتوسط</th><th style="background:#1E627A;color:#fff;font-size:26px;font-weight:800;padding:13px">أطول سلسلة خسائر</th></tr>
<tr><td style="font-size:27px;padding:13px;text-align:center;border-top:1px solid #EDE7DB;color:#0F2E3C;font-weight:800">50 صفقة</td><td style="font-size:27px;padding:13px;text-align:center;border-top:1px solid #EDE7DB;color:#1E627A;font-weight:800">42%</td><td style="font-size:27px;padding:13px;text-align:center;border-top:1px solid #EDE7DB;color:#1E627A;font-weight:800">1 : 2.1</td><td style="font-size:27px;padding:13px;text-align:center;border-top:1px solid #EDE7DB;color:#D24B4B;font-weight:800">5 ورا بعض</td></tr>
</table>'''

LOT_CARD = '''<div style="background:#FBF9F5;border:1px solid #DED8CC;border-radius:3px;padding:30px;text-align:center">
<div style="font-size:34px;font-weight:900;color:#0F2E3C">اللوت = مبلغ المخاطرة ÷ (مسافة الستوب × قيمة النقطة)</div>
<div style="margin-top:22px;font-size:29px;font-weight:700;color:#5C6C73">حساب <b style="color:#0F2E3C">$1000</b> · مخاطرة 1% = <b style="color:#0F2E3C">$10</b> · ستوب <b style="color:#0F2E3C">50 نقطة</b></div>
<div style="margin-top:14px;font-size:33px;font-weight:900;color:#1E627A">‎10 ÷ (50 × 10$) = 0.02 لوت</div>
</div>'''

def _base(w, Wd, H):
    ymin = min(c["l"] for c in w); ymax = max(c["h"] for c in w)
    pad = (ymax - ymin) * 0.07; ymin -= pad * 1.5; ymax += pad
    return chart(w, Wd, H, ymin, ymax, grid=4, pl=10, pr=14, pt=16, pb=12, body=0.6)

def istidraj_static(Wd=880, H=430):
    w = C[13]["w"]; I1, IS1, IOB, IR, RB = 13, 18, 9, 24, 30
    EQ = w[I1]["h"]; XP = max(range(16, 19), key=lambda j: w[j]["h"])
    svg, x, y, slot = _base(w, Wd, H)
    svg += f'<line x1="{x(I1)-slot*0.5:.1f}" y1="{y(EQ):.1f}" x2="{x(IS1)+slot*0.55:.1f}" y2="{y(EQ):.1f}" stroke="{RED}" stroke-width="1.7"/>'
    svg += htext(x(14.5), y(max(EQ, w[XP]["h"]))-16, "الطعم", RED, 17)
    r=11
    svg += (f'<line x1="{x(XP)-r:.1f}" y1="{y(w[XP]["h"])-r:.1f}" x2="{x(XP)+r:.1f}" y2="{y(w[XP]["h"])+r:.1f}" stroke="{RED}" stroke-width="3.2" stroke-linecap="round"/>'
            f'<line x1="{x(XP)-r:.1f}" y1="{y(w[XP]["h"])+r:.1f}" x2="{x(XP)+r:.1f}" y2="{y(w[XP]["h"])-r:.1f}" stroke="{RED}" stroke-width="3.2" stroke-linecap="round"/>')
    ZT, ZB = w[IOB]["o"], w[IOB]["l"]
    zx0 = x(IOB)-slot*0.5; zx1 = x(min(IR+3, len(w)-1))+slot*0.5
    svg += (f'<rect x="{zx0:.1f}" y="{y(ZT):.1f}" width="{zx1-zx0:.1f}" height="{y(ZB)-y(ZT):.1f}" fill="{TEAL}" style="opacity:0.16"/>'
            f'<rect x="{zx0:.1f}" y="{y(ZT):.1f}" width="{zx1-zx0:.1f}" height="{y(ZB)-y(ZT):.1f}" fill="none" stroke="{TEAL_D}" stroke-width="1"/>')
    svg += htext((zx0+zx1)/2, y(ZB)+22, "المنطقة الحقيقية", TEAL_D, 16)
    svg += f'<circle cx="{x(IR):.1f}" cy="{y(w[IR]["l"]):.1f}" r="11" fill="none" stroke="{RED}" stroke-width="2.4"/>'
    svg += htext(x(RB)-slot*0.6, y(max(c["h"] for c in w[RB:]))-14, "الحركة الحقيقية", TEAL_D, 16)
    return svg + "</svg>"

def nus_static(Wd=880, H=430):
    w = C[4]["w"]; ILO, IHI, IOB, IR = 2, 26, 18, 39
    LO = w[ILO]["l"]; HI = w[IHI]["h"]; MID = (LO+HI)/2
    svg, x, y, slot = _base(w, Wd, H)
    n = len(w)
    svg += (f'<rect x="{x(ILO):.1f}" y="{y(HI):.1f}" width="{x(n-1)-x(ILO):.1f}" height="{y(MID)-y(HI):.1f}" fill="{RED}" opacity="0.06"/>'
            f'<rect x="{x(ILO):.1f}" y="{y(MID):.1f}" width="{x(n-1)-x(ILO):.1f}" height="{y(LO)-y(MID):.1f}" fill="{TEAL}" opacity="0.08"/>')
    svg += f'<line x1="{x(ILO):.1f}" y1="{y(MID):.1f}" x2="{x(n-1)+slot*0.4:.1f}" y2="{y(MID):.1f}" stroke="{INK}" stroke-width="1.7" stroke-dasharray="8 6"/>'
    svg += hend(x(n-1)+slot*0.4, y(MID), INK)
    svg += htext(x(6), y(MID)-12, "نص المدى", INK, 16)
    svg += htext(x(7), y((HI+MID)/2), "غالي", RED, 17)
    svg += htext(x(7), y((MID+LO)/2), "رخيص", TEAL_D, 17)
    ZT, ZB = w[IOB]["o"], w[IOB]["l"]
    zx0 = x(IOB)-slot*0.5; zx1 = x(min(IR+2, n-1))+slot*0.5
    svg += (f'<rect x="{zx0:.1f}" y="{y(ZT):.1f}" width="{zx1-zx0:.1f}" height="{y(ZB)-y(ZT):.1f}" fill="{TEAL}" style="opacity:0.16"/>'
            f'<rect x="{zx0:.1f}" y="{y(ZT):.1f}" width="{zx1-zx0:.1f}" height="{y(ZB)-y(ZT):.1f}" fill="none" stroke="{TEAL_D}" stroke-width="1"/>')
    svg += f'<circle cx="{x(IR):.1f}" cy="{y(w[IR]["l"]):.1f}" r="11" fill="none" stroke="{RED}" stroke-width="2.4"/>'
    return svg + "</svg>"

# ================= بناء كاروسيل من نصوص الايجنت =================
def car_from_copy(key, kw, heroes, section_visuals, out_html, title):
    cc = CP[key]["car"]
    SL = [cover_slide(cc["cover_eyebrow"], cc["cover_title"], cc["cover_tag"], heroes)]
    SL.append(problem(2, cc["problem_title"], cc["problem_lead"], section_visuals.get("problem", "")))
    for i, sec in enumerate(cc["sections"]):
        inner = section_visuals.get(i, "")
        if sec.get("rules"):
            inner = rules([(r[0], bool(r[1])) for r in sec["rules"]]) + inner
        SL.append(numbered(3+i, str(i+1), sec["title"], sec.get("lead"), inner, sec.get("note")))
    SL.append(quote_slide(7, f'{cc["quote_a"]}<br><span class="tt">{cc["quote_b"]}</span>', cc["quote_tag"]))
    SL.append(cta_slide(8, kw, cc["share_line"], cc["promise"]))
    build_carousel(SL, title, os.path.join(HERE, out_html))

FC = fomo_chase()
car_from_copy("fomo", "فومو", dkmap(fomo_chase(700, 330)),
              {"problem": W(FC), 1: W(FC) if False else "", 2: ""}, "car_fomo.html", "الفومو — Liquidity State")
car_from_copy("backtest", "باكتست", dkmap(BT_TABLE.replace("#FBF9F5", "#0D2430").replace("#DED8CC", "#1E627A").replace("#0F2E3C", "#ECF3F6").replace("#5C6C73", "#8FA6AF")),
              {"problem": "", 2: BT_TABLE}, "car_backtest.html", "الباك تست — Liquidity State")
car_from_copy("lot", "لوت", dkmap(LOT_CARD.replace("#FBF9F5", "#0D2430").replace("#DED8CC", "#1E627A").replace("#0F2E3C", "#ECF3F6").replace("#5C6C73", "#8FA6AF")),
              {"problem": "", 1: LOT_CARD}, "car_lot.html", "حجم العقد — Liquidity State")
print("built 3 carousels (run3)")

# ================= الأدلة الخمسة =================
HEROES = {"istidraj": dkmap(istidraj_static(760, 360)), "nus": dkmap(nus_static(760, 360)),
          "fomo": dkmap(fomo_chase(700, 330)),
          "backtest": dkmap(BT_TABLE.replace("#FBF9F5", "#0D2430").replace("#DED8CC", "#1E627A").replace("#0F2E3C", "#ECF3F6").replace("#5C6C73", "#8FA6AF")),
          "lot": dkmap(LOT_CARD.replace("#FBF9F5", "#0D2430").replace("#DED8CC", "#1E627A").replace("#0F2E3C", "#ECF3F6").replace("#5C6C73", "#8FA6AF"))}
TITLES = {"istidraj": ("دليل — SMC", "الاستدراج<br>قبل الحركة", "استدراج"),
          "nus": ("دليل — SMC", "البريميوم<br>والديسكاونت", "نص"),
          "fomo": ("دليل — نفسية التداول", "علاج<br>الفومو", "فومو"),
          "backtest": ("دليل — أساسيات", "الباك تست<br>الصح", "باكتست"),
          "lot": ("دليل — إدارة المخاطر", "حجم العقد<br>وحسبة الـ1%", "لوت")}
PAGE_SVGS = {("istidraj", 0): istidraj_static(), ("nus", 0): nus_static(),
             ("fomo", 0): fomo_chase(880, 360)}
PAGE_HTML = {("backtest", 2): BT_TABLE, ("lot", 1): LOT_CARD}

for key, (eyeb, ttl, kw) in TITLES.items():
    g = CP[key]["guide"]
    pages = []
    for i, pg in enumerate(g["pages"]):
        p = dict(title=pg["title"])
        if pg.get("lead"): p["lead"] = pg["lead"]
        if pg.get("rules"): p["rules"] = [dict(t=r["t"], bad=bool(r.get("bad"))) for r in pg["rules"]]
        if pg.get("note"): p["note"] = pg["note"]
        if (key, i) in PAGE_SVGS: p["svg"] = PAGE_SVGS[(key, i)]
        if (key, i) in PAGE_HTML: p["html"] = PAGE_HTML[(key, i)]
        if key == "istidraj" and i == 0: p["ticker"] = "الذهب · 15 دقيقة · 2026-05-29"
        if key == "nus" and i == 0: p["ticker"] = "الداو جونز · فريم الساعة · 2025-10-29"
        pages.append(p)
    cfg = dict(eyebrow=eyeb, title=ttl, keyword=kw, subtitle=g["subtitle"], hero=HEROES[key],
               pages=pages, outro_title=g["outro_title"], outro_items=g["outro_items"])
    n = build_guide(cfg, os.path.join(HERE, f"guide_{key}.html"))
    print(f"guide_{key}.html", n, "pages")
