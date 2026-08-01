# -*- coding: utf-8 -*-
# شيت النماذج 1 — أنواع ريتيست الأوردر بلوك الصاعد (1080×1350)
# الشموع: نوافذ حقيقية من السوق (sheet_real.json من sheet_scan.py) — الرسم التخطيطي مفهومي.
import math, json, os
from reel_build import (CREAM, INK, TEAL, TEAL_D, TEAL_L, BULL, BEAR, RED, MUTE, GREY,
                        FONT_CSS, chart, htext, hend, GEM)

HERE = os.path.dirname(os.path.abspath(__file__))
REAL = {r["cls"]: r for r in json.load(open(os.path.join(HERE, "sheet_real.json")))}
SYMAR = {"GC=F": "الذهب", "YM=F": "الداو جونز", "NQ=F": "الناسداك",
         "GBPUSD=X": "GBP/USD", "USDJPY=X": "USD/JPY", "AUDUSD=X": "AUD/USD"}
TFAR = {"5m": "5 دقائق", "15m": "15 دقيقة", "30m": "30 دقيقة", "1h": "فريم الساعة"}

# ---------- real-window candle side ----------
def cand_real(row, extras):
    w = row["w"]; n = len(w)
    iH, bk, iob, ir = row["iH"], row["bk"], row["iob"], row["ir"]
    ymin = min(c["l"] for c in w); ymax = max(c["h"] for c in w)
    pad = (ymax - ymin) * 0.07; ymin -= pad * 1.6; ymax += pad
    svg, x, y, slot = chart(w, 560, 300, ymin, ymax, grid=4, pl=10, pr=14, pt=14, pb=10, body=0.6)
    ztop = w[iob]["o"]; zbot = w[iob]["l"]; lv = w[iH]["h"]
    zx0 = x(iob) - slot*0.5; zx1 = x(min(ir + 3, n - 1)) + slot*0.5
    svg += (f'<rect x="{zx0:.1f}" y="{y(ztop):.1f}" width="{zx1-zx0:.1f}" height="{y(zbot)-y(ztop):.1f}" '
            f'fill="{TEAL}" style="opacity:0.16"/>'
            f'<rect x="{zx0:.1f}" y="{y(ztop):.1f}" width="{zx1-zx0:.1f}" height="{y(zbot)-y(ztop):.1f}" '
            f'fill="none" stroke="{TEAL_D}" stroke-width="1"/>')
    svg += htext((zx0+zx1)/2, y(zbot)+21, "زون الطلب", TEAL_D, 15)
    # BOS: from the broken swing high to the break candle only
    svg += f'<line x1="{x(iH):.1f}" y1="{y(lv):.1f}" x2="{x(bk)+slot*0.55:.1f}" y2="{y(lv):.1f}" stroke="{INK}" stroke-width="1.7"/>'
    svg += hend(x(bk)+slot*0.55, y(lv), INK)
    svg += htext(x(iH)+slot*1.4, y(lv)-9, "BOS", INK, 14)
    # retest circle on the actual touch low
    svg += f'<circle cx="{x(ir):.1f}" cy="{y(w[ir]["l"]):.1f}" r="11" fill="none" stroke="{RED}" stroke-width="2.4"/>'
    svg += extras(row, w, x, y, slot)
    return svg + "</svg>"

def ex_chan(row, w, x, y, slot):
    (a, b), (c, d) = row["chi"], row["clo"]
    hs = (w[a]["h"], w[b]["h"]); ls = (w[c]["l"], w[d]["l"])
    ir = row["ir"]
    sl_h = (hs[1]-hs[0]) / (b-a)
    sl_l = (ls[1]-ls[0]) / (d-c) if d != c else sl_h
    e_h = ir; e_l = max(ir - 1, d)
    s = (f'<line x1="{x(a):.1f}" y1="{y(hs[0]):.1f}" x2="{x(e_h):.1f}" y2="{y(hs[0]+sl_h*(e_h-a)):.1f}" stroke="{RED}" stroke-width="1.7"/>'
         f'<line x1="{x(c):.1f}" y1="{y(ls[0]):.1f}" x2="{x(e_l):.1f}" y2="{y(ls[0]+sl_l*(e_l-c)):.1f}" stroke="{RED}" stroke-width="1.7"/>')
    s += htext(x((a+b)/2), y(max(hs))-26, "نموذج استمرار", RED, 15)
    return s

def ex_consol(row, w, x, y, slot):
    ca, cb = row["ca"], row["cb"]
    rt = max(w[k]["h"] for k in range(ca, cb+1)); rb = min(w[k]["l"] for k in range(ca, cb+1))
    s = (f'<line x1="{x(ca)-slot*0.4:.1f}" y1="{y(rt):.1f}" x2="{x(cb)+slot*0.55:.1f}" y2="{y(rt):.1f}" stroke="{INK}" stroke-width="1.6"/>'
         f'<line x1="{x(ca)-slot*0.4:.1f}" y1="{y(rb):.1f}" x2="{x(cb)+slot*0.55:.1f}" y2="{y(rb):.1f}" stroke="{INK}" stroke-width="1.6"/>')
    s += htext(x((ca+cb)/2), y(rt)-10, "تجميع جانبي", INK, 15)
    return s

def ex_sweep(row, w, x, y, slot):
    i1, i2, ipdl = row["i1"], row["i2"], row["ipdl"]
    eq = w[i1]["h"]; pdl = w[ipdl]["l"]
    s = (f'<line x1="{x(i1)-slot*0.6:.1f}" y1="{y(eq):.1f}" x2="{x(i2)+slot*0.55:.1f}" y2="{y(eq):.1f}" stroke="{RED}" stroke-width="1.7"/>'
         f'<line x1="{x(ipdl)-slot*1.6:.1f}" y1="{y(pdl):.1f}" x2="{x(ipdl)+slot*1.6:.1f}" y2="{y(pdl):.1f}" stroke="{INK}" stroke-width="1.5" stroke-dasharray="5 4"/>')
    s += htext(x((i1+i2)/2), y(max(eq, w[i2]["h"]))-12, "سيولة القمم", RED, 15)
    s += htext(x(ipdl), y(pdl)+22, "PDL", INK, 13)
    return s

# ---------- schematic (line sketch) side ----------
def sk(pts, W=430, H=300, lines=(), zone=None, circle=None, arrow=None, texts=(), bos=None):
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    for seg in lines: xs += [q[0] for q in seg["p"]]; ys += [q[1] for q in seg["p"]]
    x0, x1 = min(xs), max(xs); y0, y1 = min(ys), max(ys)
    mx = lambda v: 18 + (v-x0)/(x1-x0)*(W-36)
    my = lambda v: 16 + (y1-v)/(y1-y0)*(H-44)
    s = [f'<svg viewBox="0 0 {W} {H}" width="{W}" height="{H}" xmlns="http://www.w3.org/2000/svg">']
    if zone:
        (za, zb2), (zt, zbo) = zone
        s.append(f'<rect x="{mx(za):.1f}" y="{my(zt):.1f}" width="{mx(zb2)-mx(za):.1f}" height="{my(zbo)-my(zt):.1f}" fill="{TEAL}" style="opacity:0.16"/>')
        s.append(f'<rect x="{mx(za):.1f}" y="{my(zt):.1f}" width="{mx(zb2)-mx(za):.1f}" height="{my(zbo)-my(zt):.1f}" fill="none" stroke="{TEAL_D}" stroke-width="1"/>')
        s.append(htext((mx(za)+mx(zb2))/2, my(zbo)-8, "زون الطلب", TEAL_D, 14))
    for seg in lines:
        p = " ".join(f"{mx(a):.1f},{my(b):.1f}" for a, b in seg["p"])
        d = f' stroke-dasharray="{seg["dash"]}"' if seg.get("dash") else ''
        s.append(f'<polyline points="{p}" fill="none" stroke="{seg["c"]}" stroke-width="1.8"{d}/>')
    p = " ".join(f"{mx(a):.1f},{my(b):.1f}" for a, b in pts)
    s.append(f'<polyline points="{p}" fill="none" stroke="{INK}" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/>')
    if bos:
        (bx0, bx1, bv) = bos
        s.append(f'<line x1="{mx(bx0):.1f}" y1="{my(bv):.1f}" x2="{mx(bx1):.1f}" y2="{my(bv):.1f}" stroke="{INK}" stroke-width="1.5"/>')
        s.append(f'<polygon points="{mx(bx1):.1f},{my(bv)-4:.1f} {mx(bx1):.1f},{my(bv)+4:.1f} {mx(bx1)+7:.1f},{my(bv):.1f}" fill="{INK}"/>')
        s.append(htext(mx(bx0)+16, my(bv)-8, "BOS", INK, 14))
    if circle:
        s.append(f'<circle cx="{mx(circle[0]):.1f}" cy="{my(circle[1]):.1f}" r="12" fill="none" stroke="{RED}" stroke-width="2.4"/>')
    if arrow:
        (a0, a1) = arrow
        ax0, ay0, ax1, ay1 = mx(a0[0]), my(a0[1]), mx(a1[0]), my(a1[1])
        ang = math.atan2(ay1-ay0, ax1-ax0)
        s.append(f'<line x1="{ax0:.1f}" y1="{ay0:.1f}" x2="{ax1:.1f}" y2="{ay1:.1f}" stroke="{INK}" stroke-width="2.6"/>')
        for da in (ang+2.65, ang-2.65):
            s.append(f'<line x1="{ax1:.1f}" y1="{ay1:.1f}" x2="{ax1+12*math.cos(da):.1f}" y2="{ay1+12*math.sin(da):.1f}" stroke="{INK}" stroke-width="2.6" stroke-linecap="round"/>')
    for (tx, tv, txt, col, fs) in texts:
        s.append(htext(mx(tx), my(tv), txt, col, fs))
    return "".join(s) + "</svg>"

SK1 = sk(
    pts=[(0,4.2),(0.8,6.2),(1.6,3.4),(2.4,10),(3.0,8.6),(3.6,12.2),(4.2,10.2),(4.6,11.4),(5.2,9.4),(5.6,10.4),(6.2,8.2),(6.6,9.0),(7.1,6.9),(7.9,12.6),(8.6,11.2),(9.4,14.5)],
    lines=[{"p":[(3.6,12.6),(7.0,9.3)],"c":RED},{"p":[(4.0,9.6),(7.35,6.5)],"c":RED}],
    zone=[(1.9,8.2),(7.15,5.6)], circle=(7.1,6.95), arrow=((8.0,9.0),(9.3,13.6)),
    bos=(0.8,2.9,6.4), texts=[(5.6,13.3,"نموذج استمرار",RED,15)])
SK2 = sk(
    pts=[(0,4.4),(0.8,6.4),(1.6,3.5),(2.4,10.4),(3.1,9.0),(3.7,12.4),(4.3,10.6),(4.9,11.8),(5.5,10.5),(6.1,11.7),(6.7,10.6),(7.3,7.0),(8.1,12.8),(8.8,11.4),(9.6,14.7)],
    lines=[{"p":[(4.0,12.1),(6.9,12.1)],"c":INK},{"p":[(4.0,10.3),(7.1,10.3)],"c":INK}],
    zone=[(1.9,8.4),(7.35,5.7)], circle=(7.3,7.05), arrow=((8.2,9.2),(9.5,13.8)),
    bos=(0.8,2.9,6.6), texts=[(5.5,13.2,"تجميع جانبي",INK,15)])
SK3 = sk(
    pts=[(0,4.3),(0.8,6.3),(1.6,3.5),(2.4,10.2),(3.1,9.0),(3.8,12.5),(4.5,9.6),(5.3,12.9),(6.0,10.4),(6.6,11.2),(7.3,7.0),(8.1,12.7),(8.8,11.3),(9.6,14.6)],
    lines=[{"p":[(3.4,12.5),(5.8,12.5)],"c":RED},{"p":[(4.1,9.6),(5.0,9.6)],"c":INK,"dash":"5 4"}],
    zone=[(1.9,8.4),(7.35,5.7)], circle=(7.3,7.05), arrow=((8.2,9.2),(9.5,13.7)),
    bos=(0.8,2.9,6.5), texts=[(4.6,13.4,"سيولة القمم",RED,15),(4.55,8.6,"PDL",INK,13)])

def chip(row):
    return f'{SYMAR[row["sym"]]} · {TFAR[row["tf"]]} · {row["date"]}'

ROWS = [
    ("1", "نموذج الاستمرار — قناة تصحيحية", "رجعة منظمة بقمم وقيعان هابطة توصل السعر للزون",
     SK1, cand_real(REAL["chan"], ex_chan), chip(REAL["chan"])),
    ("2", "التجميع الجانبي", "رينج ضيق يجمع سيولة ثم ينزل يختبر الزون",
     SK2, cand_real(REAL["consol"], ex_consol), chip(REAL["consol"])),
    ("3", "سحب سيولة القمم", "قمتين متساويتين فوقهم سيولة — يسحبها وينزل للزون",
     SK3, cand_real(REAL["sweep"], ex_sweep), chip(REAL["sweep"])),
]

rows_html = ""
for num, ttl, sub, sksvg, cndsvg, chp in ROWS:
    rows_html += f'''<div class="row">
  <div class="rhead"><span class="num">{num}</span><div class="rtt"><h2>{ttl}</h2><p>{sub}</p></div><span class="tick">{chp}</span></div>
  <div class="rcols"><div class="col sk">{sksvg}</div><div class="col cn">{cndsvg}</div></div>
</div>'''

html = f'''<!DOCTYPE html><html lang="ar" dir="rtl"><head><meta charset="utf-8"><style>
{FONT_CSS}
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:1080px;height:1350px;font-family:Tajawal;overflow:hidden;
  background:radial-gradient(120% 90% at 50% 0%, #F7F3EC 0%, #F2EEE7 55%, #ECE6DB 100%)}}
.sheet{{width:1080px;height:1350px;padding:44px 56px 30px;display:flex;flex-direction:column}}
.hd{{display:flex;flex-direction:column;align-items:center;gap:8px}}
.hgem{{width:46px;height:46px}} .hgem svg{{width:100%;height:100%}}
.hwm{{display:flex;align-items:center;gap:12px;color:#5C6C73;font-weight:700;font-size:15px;letter-spacing:7px}}
.hln{{display:block;width:70px;height:1px;background:linear-gradient(90deg,transparent,#9AA9AF)}}
.eyeb{{margin:18px auto 0;display:flex;align-items:center;gap:10px;color:{TEAL_D};font-weight:800;font-size:16px}}
.dsh{{display:block;width:26px;height:2px;background:{TEAL_D}}}
h1{{text-align:center;color:{INK};font-size:44px;font-weight:900;margin-top:4px}}
.tbar{{width:430px;height:4px;background:{INK};margin:10px auto 6px}}
.row{{flex:1;display:flex;flex-direction:column;margin-top:14px;min-height:0}}
.rhead{{display:flex;align-items:flex-start;gap:12px}}
.num{{width:34px;height:34px;border:2px solid {TEAL_D};color:{TEAL_D};font-weight:900;font-style:italic;
  font-size:20px;display:flex;align-items:center;justify-content:center;border-radius:0;flex:0 0 auto;margin-top:2px}}
.rtt{{flex:1;min-width:0}}
.rhead h2{{color:{INK};font-size:23px;font-weight:800;line-height:1.15}}
.rhead p{{color:#5C6C73;font-size:15px;font-weight:500;margin-top:1px}}
.tick{{border:1.5px solid {TEAL_D};color:{TEAL_D};font-weight:800;font-size:14px;padding:5px 12px;
  white-space:nowrap;margin-top:4px;border-radius:0}}
.rcols{{flex:1;display:flex;gap:16px;margin-top:6px;min-height:0}}
.col{{display:flex;align-items:center;justify-content:center}}
.col.sk{{flex:0 0 430px}} .col.cn{{flex:1}}
.col svg{{width:100%;height:100%;max-height:262px}}
.ft{{display:flex;align-items:center;justify-content:space-between;color:#93A2A8;font-size:13px;
  font-weight:600;margin-top:12px;border-top:1px solid rgba(15,46,60,0.10);padding-top:10px}}
</style></head><body><div class="sheet">
<div class="hd"><div class="hgem">{GEM}</div><div class="hwm"><span class="hln"></span>LIQUIDITY STATE<span class="hln" style="transform:scaleX(-1)"></span></div></div>
<div class="eyeb"><span class="dsh"></span>شيتات النماذج<span class="dsh"></span></div>
<h1>أنواع ريتيست الأوردر بلوك الصاعد</h1>
<div class="tbar"></div>
{rows_html}
<div class="ft"><span>لغرض تعليمي — الشموع من السوق الحقيقي والرسم التخطيطي توضيحي</span><span>@liquidity.state</span></div>
</div></body></html>'''

open("sheet.html", "w").write(html)
print("wrote sheet.html", len(html), "bytes |", {k: (v["sym"], v["tf"], v["date"], len(v["w"])) for k, v in REAL.items()})
