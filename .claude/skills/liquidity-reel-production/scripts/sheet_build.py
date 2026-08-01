# -*- coding: utf-8 -*-
# شيت النماذج 1 — أنواع ريتيست الأوردر بلوك الصاعد (1080×1350)
import math
from reel_build import (CREAM, INK, TEAL, TEAL_D, TEAL_L, BULL, BEAR, RED, MUTE, GREY,
                        FONT_CSS, gen, chart, htext, hend, GEM)

# ---------- candle scenario factory (bullish OB retest, pattern-specific pullback) ----------
def make_sheet(seed, anchors, swings, iH, ilast, iret, n=36):
    cs = gen(anchors, n, seed, swings=swings)
    o = cs[ilast-1]["c"]
    cs[ilast]["o"] = o; cs[ilast]["c"] = o - 1.0; cs[ilast]["h"] = o + 0.35
    zb = cs[ilast]["c"] - 0.55
    if o - zb > 1.9: zb = o - 1.9
    cs[ilast]["l"] = zb
    nxt = ilast + 1
    cs[nxt]["o"] = cs[ilast]["c"]; cs[nxt]["c"] = cs[ilast]["c"] + 2.3
    cs[nxt]["h"] = cs[nxt]["c"] + 0.3; cs[nxt]["l"] = cs[nxt]["o"] - 0.25
    cs[nxt+1]["o"] = cs[nxt]["c"]
    ztop = cs[ilast]["o"]; zbot = cs[ilast]["l"]; lv = cs[iH]["h"]
    try:
        bi = next(i for i in range(nxt, n) if cs[i]["c"] > lv)
    except StopIteration:
        bi = min(nxt + 2, n-1)
        cs[bi]["c"] = lv + 0.7; cs[bi]["h"] = max(cs[bi]["h"], cs[bi]["c"] + 0.2)
        if bi + 1 < n: cs[bi+1]["o"] = cs[bi]["c"]
    # retest candle: its wick low touches the zone top exactly, closes back above
    cs[iret]["o"] = cs[iret-1]["c"]
    cs[iret]["l"] = ztop
    cs[iret]["c"] = max(cs[iret]["o"], ztop + 0.8)
    cs[iret]["h"] = max(cs[iret]["o"], cs[iret]["c"]) + 0.3
    if iret + 1 < n: cs[iret+1]["o"] = cs[iret]["c"]
    return dict(cs=cs, ztop=ztop, zbot=zbot, lv=lv, bi=bi, iH=iH, ilast=ilast, iret=iret, n=n)

def pin(cs, i, side, v, m=0.25):
    """anchor a wick extreme to an exact pattern-line price, keeping the body readable"""
    if side == 'h':
        cs[i]["h"] = v
        for k in ("o", "c"):
            if cs[i][k] > v - m: cs[i][k] = v - m
    else:
        cs[i]["l"] = v
        for k in ("o", "c"):
            if cs[i][k] < v + m: cs[i][k] = v + m

def tame_tail(S, k=4, cap=0.75):
    """cap wick length on the final rally candles"""
    for i in range(S["n"]-k, S["n"]):
        c = S["cs"][i]
        c["h"] = min(c["h"], max(c["o"], c["c"]) + cap)
        c["l"] = max(c["l"], min(c["o"], c["c"]) - cap)

def guard_zone(S):
    """after the impulse, only the circled retest candle may touch the zone top"""
    ztop = S["ztop"]
    for i in range(S["ilast"]+2, S["n"]):
        if i == S["iret"]: continue
        c = S["cs"][i]
        for k in ("o", "c"):
            if c[k] < ztop + 0.2: c[k] = ztop + 0.2
        if c["l"] < ztop + 0.12: c["l"] = ztop + 0.12
        c["h"] = max(c["h"], max(c["o"], c["c"]) + 0.05)

SEED1, SEED2, SEED3 = 801, 802, 803
AN1 = [(0,15.5),(2,14.6),(7,10.6),(9,16.2),(14,19.8),(18,17.4),(21,15.6),(25,13.4),(27,13.4),(35,21.5)]
AN2 = [(0,15.2),(2,14.4),(6,10.4),(8,16.0),(12,19.4),(13,18.4),(22,18.2),(25,13.1),(27,13.3),(35,21.0)]
AN3 = [(0,15.0),(2,14.2),(6,10.5),(8,15.8),(13,19.6),(17,16.6),(21,19.6),(26,13.0),(27,13.2),(35,21.2)]
SW1 = [(2,'H'),(7,'L'),(14,'H'),(16,'H'),(19,'L'),(21,'H'),(23,'L')]
SW2 = [(2,'H'),(6,'L'),(12,'H')]
SW3 = [(2,'H'),(6,'L'),(13,'H'),(17,'L'),(21,'H')]

S1 = make_sheet(SEED1, AN1, SW1, iH=2, ilast=7,  iret=27)   # قناة تصحيحية
S2 = make_sheet(SEED2, AN2, SW2, iH=2, ilast=6,  iret=25)   # تجميع جانبي
S3 = make_sheet(SEED3, AN3, SW3, iH=2, ilast=6,  iret=26)   # سحب سيولة القمم

# S1: descending channel — pin pullback wicks onto two parallel lines
CH_HI = [(16, 19.0), (21, 16.8)]           # upper touches (i, price)
CH_LO = [(19, 15.9), (23, 14.1)]           # lower touches
for i, v in CH_HI: pin(S1["cs"], i, 'h', v)
for i, v in CH_LO: pin(S1["cs"], i, 'l', v)
slope = (CH_HI[1][1]-CH_HI[0][1]) / (CH_HI[1][0]-CH_HI[0][0])
# extend both lines to the retest candle only (stop-at-candle rule)
CH_HI_END = (S1["iret"], CH_HI[0][1] + slope*(S1["iret"]-CH_HI[0][0]) )
CH_LO_END = (S1["iret"]-1, CH_LO[0][1] + slope*(S1["iret"]-1-CH_LO[0][0]))
# keep candles between the channel walls on the way down
for i in range(15, S1["iret"]):
    hi_line = CH_HI[0][1] + slope*(i-CH_HI[0][0]); lo_line = CH_LO[0][1] + slope*(i-CH_LO[0][0])
    c = S1["cs"][i]
    if c["h"] > hi_line: pin(S1["cs"], i, 'h', hi_line)
    if c["l"] < lo_line and i not in (S1["iret"],): pin(S1["cs"], i, 'l', lo_line)

# S2: consolidation — pin range candles between two horizontal bounds, then breakdown
R_TOP, R_BOT = 19.3, 17.0
for i in range(13, 23):
    c = S2["cs"][i]
    if c["h"] > R_TOP: pin(S2["cs"], i, 'h', R_TOP)
    if c["l"] < R_BOT: pin(S2["cs"], i, 'l', R_BOT)
pin(S2["cs"], 12, 'h', R_TOP + 0.8)
pin(S2["cs"], 14, 'h', R_TOP); pin(S2["cs"], 18, 'h', R_TOP)
pin(S2["cs"], 16, 'l', R_BOT); pin(S2["cs"], 20, 'l', R_BOT)
S2["cs"][23]["o"] = S2["cs"][22]["c"]
S2["cs"][23]["c"] = R_BOT - 1.6; S2["cs"][23]["h"] = S2["cs"][23]["o"] + 0.2
S2["cs"][23]["l"] = S2["cs"][23]["c"] - 0.3
S2["cs"][24]["o"] = S2["cs"][23]["c"]

# S3: buyside liquidity — line on the first high, second high sweeps above it
EQ = 19.6; PDL = 16.4
pin(S3["cs"], 13, 'h', EQ); pin(S3["cs"], 21, 'h', EQ + 0.4)
for k in ("o", "c"):  # sweep candle closes back under the liquidity line
    if S3["cs"][21][k] > EQ - 0.3: S3["cs"][21][k] = EQ - 0.3
pin(S3["cs"], 17, 'l', PDL)
for i in range(12, 23):
    if i not in (13, 21) and S3["cs"][i]["h"] > EQ - 0.25: pin(S3["cs"], i, 'h', EQ - 0.25)
S3["cs"][22]["o"] = S3["cs"][21]["c"]
S3["cs"][22]["c"] = PDL - 0.9; S3["cs"][22]["h"] = S3["cs"][22]["o"] + 0.25
S3["cs"][22]["l"] = S3["cs"][22]["c"] - 0.3
S3["cs"][23]["o"] = S3["cs"][22]["c"]
tame_tail(S1); tame_tail(S2); tame_tail(S3)
guard_zone(S1); guard_zone(S2); guard_zone(S3)

# ---------- candle-side SVG ----------
def cand_svg(S, extras):
    cs = S["cs"]; n = S["n"]
    ymin = min(c["l"] for c in cs) - 0.9; ymax = max(c["h"] for c in cs) + 1.4
    svg, x, y, slot = chart(cs, 560, 300, ymin, ymax, grid=4, pl=10, pr=14, pt=12, pb=10, body=0.6)
    ztop, zbot, lv, bi, iH, ilast, iret = (S["ztop"], S["zbot"], S["lv"], S["bi"], S["iH"], S["ilast"], S["iret"])
    zx0 = x(ilast) - slot*0.5; zx1 = x(min(iret+3, n-1)) + slot*0.5
    svg += (f'<rect x="{zx0:.1f}" y="{y(ztop):.1f}" width="{zx1-zx0:.1f}" height="{y(zbot)-y(ztop):.1f}" '
            f'fill="{TEAL}" style="opacity:0.16"/>'
            f'<rect x="{zx0:.1f}" y="{y(ztop):.1f}" width="{zx1-zx0:.1f}" height="{y(zbot)-y(ztop):.1f}" '
            f'fill="none" stroke="{TEAL_D}" stroke-width="1"/>')
    svg += htext((zx0+zx1)/2, y(zbot)+20, "زون الطلب", TEAL_D, 15)
    # BOS line: from the broken swing high to the break candle only
    svg += (f'<line x1="{x(iH):.1f}" y1="{y(lv):.1f}" x2="{x(bi)+slot*0.55:.1f}" y2="{y(lv):.1f}" '
            f'stroke="{INK}" stroke-width="1.7"/>')
    svg += hend(x(bi)+slot*0.55, y(lv), INK)
    svg += htext(x(iH)+slot*1.2, y(lv)-9, "BOS", INK, 14)
    # retest circle on the exact touch point
    svg += f'<circle cx="{x(iret):.1f}" cy="{y(ztop):.1f}" r="11" fill="none" stroke="{RED}" stroke-width="2.4"/>'
    svg += extras(x, y, slot, cs)
    return svg + "</svg>"

def ex1(x, y, slot, cs):  # channel lines stop at the retest candle
    s = (f'<line x1="{x(CH_HI[0][0]):.1f}" y1="{y(CH_HI[0][1]):.1f}" x2="{x(CH_HI_END[0]):.1f}" y2="{y(CH_HI_END[1]):.1f}" stroke="{RED}" stroke-width="1.7"/>'
         f'<line x1="{x(CH_LO[0][0]):.1f}" y1="{y(CH_LO[0][1]):.1f}" x2="{x(CH_LO_END[0]):.1f}" y2="{y(CH_LO_END[1]):.1f}" stroke="{RED}" stroke-width="1.7"/>')
    s += htext(x(20), y(CH_HI[0][1])-24, "نموذج استمرار", RED, 15)
    return s

def ex2(x, y, slot, cs):  # consolidation bounds across the range candles only
    s = (f'<line x1="{x(13)-slot*0.4:.1f}" y1="{y(R_TOP):.1f}" x2="{x(22)+slot*0.4:.1f}" y2="{y(R_TOP):.1f}" stroke="{INK}" stroke-width="1.6"/>'
         f'<line x1="{x(13)-slot*0.4:.1f}" y1="{y(R_BOT):.1f}" x2="{x(23)+slot*0.55:.1f}" y2="{y(R_BOT):.1f}" stroke="{INK}" stroke-width="1.6"/>')
    s += htext(x(18), y(R_TOP)-10, "تجميع جانبي", INK, 15)
    return s

def ex3(x, y, slot, cs):  # buyside liquidity line + PDL
    s = (f'<line x1="{x(13)-slot*0.6:.1f}" y1="{y(EQ):.1f}" x2="{x(21)+slot*0.55:.1f}" y2="{y(EQ):.1f}" stroke="{RED}" stroke-width="1.7"/>'
         f'<line x1="{x(15):.1f}" y1="{y(PDL):.1f}" x2="{x(19):.1f}" y2="{y(PDL):.1f}" stroke="{INK}" stroke-width="1.5" stroke-dasharray="5 4"/>')
    s += htext(x(17), y(EQ)-10, "سيولة القمم", RED, 15)
    s += htext(x(17), y(PDL)+22, "PDL", INK, 13)
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

# schematic geometries (unitless)
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

ROWS = [
    ("1", "نموذج الاستمرار — قناة تصحيحية", "رجعة منظمة بقمم وقيعان هابطة توصل السعر للزون", SK1, cand_svg(S1, ex1)),
    ("2", "التجميع الجانبي", "رينج ضيق يجمع سيولة ثم ينزل يختبر الزون", SK2, cand_svg(S2, ex2)),
    ("3", "سحب سيولة القمم", "قمتين متساويتين فوقهم سيولة — يسحبها وينزل للزون", SK3, cand_svg(S3, ex3)),
]

rows_html = ""
for num, ttl, sub, sksvg, cndsvg in ROWS:
    rows_html += f'''<div class="row">
  <div class="rhead"><span class="num">{num}</span><div><h2>{ttl}</h2><p>{sub}</p></div></div>
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
.rhead h2{{color:{INK};font-size:23px;font-weight:800;line-height:1.15}}
.rhead p{{color:#5C6C73;font-size:15px;font-weight:500;margin-top:1px}}
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
<div class="ft"><span>لغرض تعليمي — رسم توضيحي للمفهوم</span><span>@liquidity.state</span></div>
</div></body></html>'''

open("sheet.html", "w").write(html)
print("wrote sheet.html", len(html), "bytes")
