# -*- coding: utf-8 -*-
# Order Block reel (60s) — inherits the approved Liquidity State engine from reel_build.
import os, math, json
from reel_build import (CREAM, CREAM2, INK, TEAL, TEAL_D, TEAL_L, BULL, BEAR, RED, GREY, MUTE,
                        LINE, CARDBD, CYAN, CYANG, FONT_CSS, GEM, C, chart, gen, htext, lbl,
                        zzline, hend, logo, IUP, IDN, ISW, CSS as BASECSS)
HERE = os.path.dirname(os.path.abspath(__file__))

# ============ OB scenarios — a DIFFERENT chart per scene (no chart repeats) ============
W, H = 980, 470

def make_ob(seed, anchors, swings, iH, iswl, ilast, iret=None):
    cs = gen(anchors, 30, seed, swings=swings)
    o = cs[ilast-1]["c"]
    cs[ilast]["o"] = o; cs[ilast]["c"] = o - 1.0; cs[ilast]["h"] = o + 0.35
    zb = min(cs[iswl]["l"] - 0.5, cs[ilast]["c"] - 0.4)
    if o - zb > 1.9:                     # cap zone height to keep the OB realistic
        zb = o - 1.9
        if zb > cs[iswl]["l"] - 0.15:    # sweep must still undercut the swept low
            cs[iswl]["l"] = zb + 0.35
    cs[ilast]["l"] = zb
    nxt = ilast + 1
    cs[nxt]["o"] = cs[ilast]["c"]; cs[nxt]["c"] = cs[ilast]["c"] + 2.2
    cs[nxt]["h"] = cs[nxt]["c"] + 0.3; cs[nxt]["l"] = cs[nxt]["o"] - 0.25
    cs[nxt+1]["o"] = cs[nxt]["c"]
    ztop = cs[ilast]["o"]; zbot = cs[ilast]["l"]; lv = cs[iH]["h"]
    try:
        bi = next(i for i in range(nxt, 30) if cs[i]["c"] > lv)
    except StopIteration:
        bi = min(nxt + 2, 29)
        cs[bi]["c"] = lv + 0.7; cs[bi]["h"] = max(cs[bi]["h"], cs[bi]["c"] + 0.2)
        if bi + 1 < 30: cs[bi+1]["o"] = cs[bi]["c"]
    if iret:
        cs[iret]["o"] = cs[iret-1]["c"]; cs[iret]["c"] = max(cs[iret-1]["c"], ztop + 0.9)
        cs[iret]["l"] = ztop; cs[iret]["h"] = max(cs[iret]["o"], cs[iret]["c"]) + 0.3
        if iret + 1 < 30: cs[iret+1]["o"] = cs[iret]["c"]
    return dict(cs=cs, ztop=ztop, zbot=zbot, lv=lv, bi=bi, swl=cs[iswl]["l"],
                iH=iH, iswl=iswl, ilast=ilast, iret=iret,
                ymin=min(c["l"] for c in cs) - 1.6, ymax=max(c["h"] for c in cs) + 2.8)

OBA = make_ob(101, [(0,11),(5,16),(12,12.8),(16,18),(21,16),(29,20.5)],
              [(5,'H'),(9,'L'),(12,'L'),(16,'H'),(21,'L')], 5, 9, 12)                 # s3 definition
OBB = make_ob(202, [(0,13.5),(7,18.5),(14,14.2),(18,20),(24,18.2),(29,22.5)],
              [(7,'H'),(11,'L'),(14,'L'),(18,'H'),(24,'L')], 7, 11, 14)               # s5 last candle
OBC = make_ob(303, [(0,10.5),(6,15.5),(11,13.5),(15,12.2),(19,18.6),(29,21.5)],
              [(6,'H'),(11,'L'),(15,'L'),(19,'H')], 6, 11, 15)                        # s6 BOS
OBD = make_ob(404, [(0,14),(8,19),(13,15),(17,20.8),(23,19.5),(29,23)],
              [(8,'H'),(10,'L'),(13,'L'),(17,'H'),(23,'L')], 8, 10, 13)               # s7 sweep
OBE = make_ob(505, [(0,12.5),(5,17),(10,14.8),(14,13.2),(18,19),(23,17.5),(29,21.8)],
              [(5,'H'),(10,'L'),(14,'L'),(18,'H'),(23,'L')], 5, 10, 14)               # s8 zone
OBF = make_ob(606, [(0,11.5),(6,16.8),(12,13),(16,18.4),(21,13.9),(29,20)],
              [(6,'H'),(9,'L'),(12,'L'),(16,'H'),(21,'L')], 6, 9, 12, iret=21)        # s9 retest

def ob_chart(ctx, *layers, animate_last=True):
    svg, x, y, slot = chart(ctx["cs"], W, H, ctx["ymin"], ctx["ymax"],
                            grid=4, pt=48, pb=22, pl=16, pr=16, body=0.5)
    n = len(layers)
    for k, layer in enumerate(layers):
        new = (k == n - 1) and animate_last
        svg += layer(ctx, x, y, slot, new)
    return svg + "</svg>"

def cl(new, anim):
    return anim if new else "pre"

def L_last(ctx, x, y, slot, new):
    cs = ctx["cs"]; il = ctx["ilast"]; g = cl(new, "pop")
    bx = x(il); pad = slot * 0.45
    return (f'<g class="{g}"><rect x="{bx-pad:.2f}" y="{y(cs[il]["h"])-8:.2f}" width="{2*pad:.2f}" '
            f'height="{y(cs[il]["l"])-y(cs[il]["h"])+16:.2f}" fill="none" stroke="{RED}" stroke-width="2" stroke-dasharray="6 5"/>'
            f'{htext(bx, y(cs[il]["h"])-22, "آخر شمعة عكسية", RED, 19)}</g>')

def L_bos(ctx, x, y, slot, new, word=True):
    cs = ctx["cs"]; lv = ctx["lv"]; iH = ctx["iH"]; bi = ctx["bi"]; il = ctx["ilast"]
    g = cl(new, "pop"); gd = cl(new, "draw")
    lx1 = x(bi) + slot*0.78
    s = f'<line class="{gd}" x1="{x(iH):.2f}" y1="{y(lv):.2f}" x2="{lx1:.2f}" y2="{y(lv):.2f}" stroke="{INK}" stroke-width="1.8"/>'
    s += f'<g class="{g}">{hend(x(iH), y(lv), INK)}'
    s += htext(x(iH)-14, y(lv)-14, "آخر قمة", TEAL_D, 17, "end")
    s += htext(x(iH+3), y(lv)-16, "BOS", INK, 21, weight=800)
    ax = x(bi) + slot*0.55   # clear gap beside the break candle
    ay0 = y(cs[bi]["l"]) + 30
    s += (f'<line x1="{ax:.2f}" y1="{ay0:.2f}" x2="{ax:.2f}" y2="{y(lv)+3:.2f}" stroke="{TEAL_D}" stroke-width="2.4"/>'
          f'<polygon points="{ax:.2f},{y(lv)+3:.2f} {ax-6:.2f},{y(lv)+14:.2f} {ax+6:.2f},{y(lv)+14:.2f}" fill="{TEAL_D}"/>')
    if word:
        s += htext(x(bi)+10, y(cs[il+1]["c"])+4, "اندفاع", TEAL_D, 19, "start", italic=True, weight=800)
    return s + "</g>"

def L_sweep(ctx, x, y, slot, new):
    cs = ctx["cs"]; il = ctx["ilast"]; iswl = ctx["iswl"]; swl = ctx["swl"]
    g = cl(new, "pop"); gd = cl(new, "draw")
    s = f'<line class="{gd}" x1="{x(iswl):.2f}" y1="{y(swl):.2f}" x2="{x(il):.2f}" y2="{y(swl):.2f}" stroke="{RED}" stroke-width="1.8" stroke-dasharray="6 5"/>'
    s += f'<g class="{g}">{hend(x(iswl), y(swl), RED)}'
    s += f'<circle cx="{x(il):.2f}" cy="{y(cs[il]["l"]):.2f}" r="4.5" fill="{RED}" stroke="{CREAM}" stroke-width="1.5"/>'
    s += htext(x(il), y(cs[il]["l"])+30, "سحب سيولة", RED, 19)
    return s + "</g>"

def L_zone(ctx, x, y, slot, new, to_edge=True):
    il = ctx["ilast"]; gp = cl(new, "pop")
    head = 'class="obzone"' if new else 'style="opacity:0.16"'
    x0 = x(il) - slot/2; x1 = (W-16) if to_edge else x(min(il+11, 29))
    s = (f'<rect {head} x="{x0:.2f}" y="{y(ctx["ztop"]):.2f}" width="{x1-x0:.2f}" height="{y(ctx["zbot"])-y(ctx["ztop"]):.2f}" '
         f'fill="{TEAL}" stroke="{TEAL_D}" stroke-width="1"/>')
    s += f'<g class="{gp}">{htext(x0+56, (y(ctx["ztop"])+y(ctx["zbot"]))/2+7, "OB", TEAL_D, 22, weight=800)}'
    s += htext(x(min(il+7, 27)), y(ctx["ztop"])-10, "الفتح", INK, 15)
    s += htext(x(min(il+7, 27)), y(ctx["zbot"])+22, "قاع السيولة", INK, 15)
    return s + "</g>"

def L_retest(ctx, x, y, slot, new):
    g = cl(new, "pop"); mx = x(ctx["iret"]); zt = ctx["ztop"]
    s = (f'<g class="{g}"><line x1="{mx:.2f}" y1="{y(zt)-64:.2f}" x2="{mx:.2f}" y2="{y(zt)-6:.2f}" stroke="{TEAL_D}" stroke-width="2.4"/>'
         f'<polygon points="{mx:.2f},{y(zt)-2:.2f} {mx-6:.2f},{y(zt)-14:.2f} {mx+6:.2f},{y(zt)-14:.2f}" fill="{TEAL_D}"/>')
    s += (f'<circle cx="{mx:.2f}" cy="{y(zt):.2f}" r="9" fill="none" stroke="{TEAL_D}" stroke-width="2.4"/>'
          f'<polyline points="{mx-4:.2f},{y(zt):.2f} {mx-1:.2f},{y(zt)+3.5:.2f} {mx+5:.2f},{y(zt)-4:.2f}" '
          f'fill="none" stroke="{TEAL_D}" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/>')
    s += htext(mx, y(zt)-78, "دخول عند الاختبار", TEAL_D, 19)
    return s + "</g>"

def ob_chart_steps(ctx):
    """One persistent chart; candles phased (cp1..cp4) + layers .lyN for step-timed reveal."""
    svg, x, y, slot = chart(ctx["cs"], W, H, ctx["ymin"], ctx["ymax"],
                            grid=4, pt=48, pb=22, pl=16, pr=16, body=0.5)
    parts = svg.split('<g class="cndl">')
    svg = parts[0]
    for i, p in enumerate(parts[1:]):
        if i <= ctx["ilast"]: ph = "cp1"        # decline into the OB candle
        elif i <= ctx["bi"]: ph = "cp2"          # displacement + break
        elif i <= (ctx["iret"] or 99): ph = "cp3"  # pullback into the zone
        else: ph = "cp4"                          # payoff rally
        svg += f'<g class="cndl {ph}">' + p
    svg += f'<g class="ly1">{L_last(ctx, x, y, slot, True)}</g>'
    svg += f'<g class="ly2">{L_bos(ctx, x, y, slot, True, word=False)}</g>'
    svg += f'<g class="ly3">{L_sweep(ctx, x, y, slot, True)}</g>'
    svg += f'<g class="ly4">{L_zone(ctx, x, y, slot, True)}</g>'
    svg += f'<g class="ly5">{L_retest(ctx, x, y, slot, True)}</g>'
    return svg + "</svg>"

def sc_def():
    return ob_chart(OBA, L_bos, L_sweep, lambda c,x,y,s,n: L_zone(c,x,y,s,n,to_edge=False), animate_last=True)

# ================= real chart (EUR/USD): zoomed on the story =================
def sc_real_ob():
    SUB = C[5:35]                           # 06-22..07-31 — 30 candles: full story with context
    Wr, Hr = 980, 660; ymin, ymax = 1.1300, 1.1580
    iSH, iOB, iSWP, iHH = 17, 25, 26, 29    # structure high / OB candle / sweep / HH
    BOSv = SUB[iSH]["h"]                    # 1.14820 exact
    ztop = SUB[iOB]["o"]                    # 1.13690 exact
    zbot = SUB[iSWP]["l"]                   # 1.13530 exact
    swl  = SUB[24]["l"]                     # 1.13640 swept low (07-24)
    svg, x, y, slot = chart(SUB, Wr, Hr, ymin, ymax, price_axis=True, dates=True, grid=5,
                            pt=54, pb=40, pl=12, pr=70, brk={27,28,29})
    # OB zone projected forward — exact prices
    zx0 = x(iOB) - slot/2
    svg += (f'<rect class="obzone" x="{zx0:.2f}" y="{y(ztop):.2f}" width="{(Wr-70)-zx0:.2f}" '
            f'height="{y(zbot)-y(ztop):.2f}" fill="{TEAL}" stroke="{TEAL_D}" stroke-width="1"/>')
    svg += f'<g class="pop">{htext(Wr-70-14, y(zbot)+26, "OB", TEAL_D, 22, "end", weight=800)}</g>'
    # liquidity sweep — line stops at the sweep candle
    svg += (f'<line class="draw lvl" x1="{x(24):.2f}" y1="{y(swl):.2f}" x2="{x(iSWP):.2f}" y2="{y(swl):.2f}" '
            f'stroke="{RED}" stroke-width="1.8" stroke-dasharray="6 5"/>')
    svg += (f'<g class="pop"><circle cx="{x(iSWP):.2f}" cy="{y(zbot):.2f}" r="4.5" fill="{RED}" stroke="{CREAM}" stroke-width="1.5"/>'
            f'{htext(x(iSWP), y(zbot)+30, "سحب سيولة", RED, 18)}</g>')
    # last opposite candle
    svg += f'<g class="pop">{htext(x(iOB)-14, y(SUB[iOB]["h"])-14, "آخر شمعة عكسية", RED, 17, "end")}</g>'
    # BOS ray stops just past the break candle; arrow with a clear gap beside it
    ly = y(BOSv); bi = 28
    svg += f'<line class="draw zz" x1="{x(iSH):.2f}" y1="{ly:.2f}" x2="{x(bi)+slot*0.78:.2f}" y2="{ly:.2f}" stroke="{INK}" stroke-width="1.8"/>'
    svg += f'<g class="bospill">{hend(x(iSH), ly, INK)}{htext(x(iSH)+12, ly-12, "BOS", INK, 21, "start", weight=800)}</g>'
    brkx = x(bi) + slot*0.55
    svg += (f'<g class="brkfx"><line x1="{brkx:.2f}" y1="{y(SUB[bi]["l"])+26:.2f}" x2="{brkx:.2f}" y2="{ly+3:.2f}" stroke="{TEAL_D}" stroke-width="2.6"/>'
            f'<polygon points="{brkx:.2f},{ly+3:.2f} {brkx-6:.2f},{ly+14:.2f} {brkx+6:.2f},{ly+14:.2f}" fill="{TEAL_D}"/>'
            f'{htext(x(bi)-slot*0.5, y(1.14980), "اندفاع", TEAL_D, 18, "end", italic=True, weight=800)}</g>')
    svg += (f'<g class="hhpop"><circle cx="{x(iHH):.2f}" cy="{y(SUB[iHH]["h"]):.2f}" r="4.5" fill="{TEAL_D}" stroke="{CREAM}" stroke-width="1.5"/>'
            f'{htext(x(iHH)-24, y(SUB[iHH]["h"])-15, "HH", TEAL_D, 20)}</g>')
    svg += f'<rect class="flash" x="0" y="0" width="{Wr}" height="{Hr}" fill="#ffffff" opacity="0"/>'
    return svg + "</svg>"

# icon: entry-into-zone (for poster)
IENT = (f'<svg viewBox="0 0 40 40" xmlns="http://www.w3.org/2000/svg"><circle cx="20" cy="20" r="17" fill="none" stroke="{CYAN}" stroke-width="2"/>'
        f'<rect x="12" y="23" width="16" height="6" fill="none" stroke="{CYAN}" stroke-width="2"/>'
        f'<path d="M20 10 V20 M14.5 15.5 L20 21 L25.5 15.5" fill="none" stroke="{CYAN}" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/></svg>')

# ================= scenes =================
scenes = []
def scene(id, dur, html): scenes.append({"id": id, "dur": dur, "html": html, "tw": []})
def T(sel, ls, d, sp, stag=0): scenes[-1]["tw"].append([sel, round(ls, 3), d, sp, stag])

# 1 POSTER
scene("s1", 4.8, f'''<div class="poster">
  <div class="ptag">درس الأوردر بلوك</div>
  <div class="pgem">{GEM}</div>
  <div class="pwm"><span class="pln l"></span><span class="pwmt">LIQUIDITY STATE</span><span class="pln r"></span></div>
  <div class="pdivg pd1"><span></span><i></i><span></span></div>
  <h1 class="ptitle">الأوردر<br>بلوك</h1>
  <div class="pdivg pd2"><span></span><i></i><span></span></div>
  <div class="peyeb">وين تدخل المؤسسات؟</div>
  <div class="psub2">تعلّم تحدد منطقة أوامرهم قبل ما يرجع لها السعر</div>
  <div class="ppill">4 شروط + مثال حقيقي</div>
  <div class="prow">
    <div class="pi p_a"><div class="pic">{IDN}</div><span>سيولة؟</span></div>
    <div class="pv"></div>
    <div class="pi p_b"><div class="pic">{IUP}</div><span>اندفاع؟</span></div>
    <div class="pv"></div>
    <div class="pi p_c"><div class="pic">{IENT}</div><span>دخول؟</span></div>
  </div></div>''')
T(".pgem",0.1,0.6,{"op":[0,1],"s":[.7,1],"ease":"ob"})
T(".pwm",0.55,0.5,{"op":[0,1],"ty":[14,0],"ease":"oc"})
T(".pd1",0.8,0.45,{"op":[0,1],"s":[.4,1],"ease":"oc"})
T(".ptitle",0.95,0.6,{"op":[0,1],"s":[.86,1],"ease":"ob"})
T(".pd2",1.6,0.4,{"op":[0,1],"s":[.4,1],"ease":"oc"})
T(".peyeb",1.75,0.45,{"op":[0,1],"ty":[16,0],"ease":"oc"})
T(".psub2",2.0,0.45,{"op":[0,1],"ty":[16,0],"ease":"oc"})
T(".ppill",2.35,0.45,{"op":[0,1],"s":[.7,1],"ease":"ob"})
T(".p_a",2.7,0.4,{"op":[0,1],"ty":[18,0],"ease":"oc"})
T(".p_b",2.85,0.4,{"op":[0,1],"ty":[18,0],"ease":"oc"})
T(".p_c",3.0,0.4,{"op":[0,1],"ty":[18,0],"ease":"oc"})

# 2 HOOK
scene("s2", 4.6, f'''{logo(160)}<div class="mid">
  <div class="a eyeb">صارحني</div>
  <div class="b hookbig">كل شمعة حمراء</div>
  <div class="c hookbig tt2">أوردر بلوك؟</div>
  <div class="d hooksub">هذا بالضبط اللي ياكل ستوباتك</div></div>''')
T(".a",0.15,0.5,{"op":[0,1],"ty":[30,0],"ease":"oc"})
T(".b",0.55,0.5,{"op":[0,1],"s":[.7,1],"ease":"ob"})
T(".c",1.05,0.5,{"op":[0,1],"s":[.7,1],"ease":"ob"})
T(".d",1.9,0.5,{"op":[0,1],"ty":[20,0],"ease":"oc"})

# 3 DEFINITION
scene("s3", 5.6, f'''{logo(120)}<div class="top">
  <div class="realh"><span class="eyeb">التعريف</span></div>
  <h2 class="ttl">شنو الأوردر بلوك؟</h2>
  <div class="rule bull">آخر شمعة <b>عكسية</b> قبل اندفاع <b>يكسر الهيكل</b> — منطقة أوامر المؤسسات</div></div>
  <div class="chartbox mid2">{sc_def()}</div>''')
T(".realh",0.15,0.4,{"op":[0,1],"ty":[20,0],"ease":"oc"})
T(".ttl",0.3,0.45,{"op":[0,1],"tx":[40,0],"ease":"oc"})
T(".rule",0.6,0.45,{"op":[0,1],"ty":[20,0],"ease":"oc"})
T(".chartbox",0.75,0.4,{"op":[0,1],"ty":[30,0],"ease":"oc"})
T(".cndl",0.9,0.28,{"op":[0,1],"sy":[.2,1],"ease":"ob"},0.09)
T(".obzone",4.0,0.6,{"op":[0,0.16],"ease":"oc"})
T(".pop",4.2,0.4,{"op":[0,1],"s":[0,1],"ease":"ob"},0.15)

# 4 WHY
scene("s4", 3.8, f'''{logo(150)}<div class="mid">
  <div class="a eyeb2">ليش تشتغل؟</div>
  <div class="b hooksub">المؤسسات ما تدخل بضغطة وحدة —<br>يوزعون أوامرهم على منطقة</div>
  <div class="d pillrow"><span class="pl">أوامر ضخمة</span><span class="pl">تنفيذ على مراحل</span><span class="pl">السعر يرجع لهم</span></div></div>''')
T(".a",0.15,0.45,{"op":[0,1],"ty":[20,0],"ease":"oc"})
T(".b",0.5,0.5,{"op":[0,1],"ty":[20,0],"ease":"oc"})
T(".d .pl",1.2,0.4,{"op":[0,1],"s":[.6,1],"ease":"ob"},0.22)

# 5..9 MERGED — one chart, marked up step by step
scene("s5", 26.6, f"""{logo(120)}
  <div class="stepwrap">
    <div class="stephead sh1"><div class="numrow"><span class="num">1</span><h2 class="ttl">آخر شمعة عكسية</h2></div>
      <div class="rule redr">قبل الحركة القوية، حدد <b>آخر شمعة هابطة</b></div></div>
    <div class="stephead sh2"><div class="numrow"><span class="num">2</span><h2 class="ttl">اندفاع يكسر الهيكل</h2></div>
      <div class="rule bull">حركة <b>قوية</b> تغلق فوق آخر قمة (BOS)</div></div>
    <div class="stephead sh3"><div class="numrow"><span class="num">3</span><h2 class="ttl">سحب سيولة قبلها</h2></div>
      <div class="rule redr">أقوى بلوك = اللي فتيله <b>يكسح قاع</b> قبل الاندفاع</div></div>
    <div class="stephead sh4"><div class="numrow"><span class="num">4</span><h2 class="ttl">ارسم المنطقة</h2></div>
      <div class="rule bull">من <b>فتح</b> الشمعة العكسية إلى <b>قاع</b> السيولة — ومدّها لقدام</div></div>
    <div class="stephead sh5"><div class="numrow"><span class="num">✓</span><h2 class="ttl">انتظر الاختبار</h2></div>
      <div class="rule neutral">لا تطارد الاندفاع — <b>خل السعر يرجع للمنطقة</b></div></div>
  </div>
  <div class="chartbox mid2s">{ob_chart_steps(OBF)}</div>
  <div class="stepcap sc1">هذي الشمعة هي بصمة دخول المؤسسات — <b>مو أي شمعة حمراء</b></div>
  <div class="stepcap sc2">بدون كسر هيكل ← <b class="tr">ما تصير أوردر بلوك</b></div>
  <div class="stepcap sc3">المؤسسات تجمع سيولتها أول — <b>بعدين تتحرك</b></div>
  <div class="stepcap sc4">هذي منطقتك — <b class="tt">خلها مرسومة وانطر</b></div>
  <div class="stepcap sc5">أول لمسة للمنطقة = <b class="tt">فرصتك</b> — والستوب تحت قاعها</div>""")
# chart shell in; candles unfold phase by phase with the story
T(".chartbox",0.2,0.4,{"op":[0,1],"ty":[30,0],"ease":"oc"})
T(".cp1",0.4,0.22,{"op":[0,1],"sy":[.2,1],"ease":"ob"},0.1)
T(".cp2",5.5,0.26,{"op":[0,1],"sy":[.2,1],"ease":"ob"},0.22)
T(".cp3",21.5,0.26,{"op":[0,1],"sy":[.2,1],"ease":"ob"},0.28)
T(".cp4",23.9,0.2,{"op":[0,1],"sy":[.2,1],"ease":"ob"},0.13)
# step windows: 1)0-5.2  2)5.2-10.6  3)10.6-15.6  4)15.6-21.2  5)21.2-26.6
T(".sh1",0.15,0.4,{"op":[0,1],"ty":[16,0],"ease":"oc"});  T(".sh1",4.85,0.35,{"op":[1,0],"gate":1})
T(".sc1",2.9,0.4,{"op":[0,1],"ty":[14,0],"ease":"oc"});   T(".sc1",4.85,0.35,{"op":[1,0],"gate":1})
T(".ly1 .pop",2.6,0.45,{"op":[0,1],"s":[.2,1],"ease":"ob"},0.2)
T(".sh2",5.3,0.4,{"op":[0,1],"ty":[16,0],"ease":"oc"});   T(".sh2",10.25,0.35,{"op":[1,0],"gate":1})
T(".sc2",7.8,0.4,{"op":[0,1],"ty":[14,0],"ease":"oc"});   T(".sc2",10.25,0.35,{"op":[1,0],"gate":1})
T(".ly2 .draw",6.7,0.7,{"draw":True,"ease":"oc"})
T(".ly2 .pop",7.3,0.4,{"op":[0,1],"s":[.2,1],"ease":"ob"},0.18)
T(".sh3",10.7,0.4,{"op":[0,1],"ty":[16,0],"ease":"oc"});  T(".sh3",15.25,0.35,{"op":[1,0],"gate":1})
T(".sc3",11.9,0.4,{"op":[0,1],"ty":[14,0],"ease":"oc"});  T(".sc3",15.25,0.35,{"op":[1,0],"gate":1})
T(".ly3 .draw",11.1,0.6,{"draw":True,"ease":"oc"})
T(".ly3 .pop",11.5,0.4,{"op":[0,1],"s":[.2,1],"ease":"ob"},0.18)
T(".sh4",15.7,0.4,{"op":[0,1],"ty":[16,0],"ease":"oc"});  T(".sh4",20.85,0.35,{"op":[1,0],"gate":1})
T(".sc4",17.1,0.4,{"op":[0,1],"ty":[14,0],"ease":"oc"});  T(".sc4",20.85,0.35,{"op":[1,0],"gate":1})
T(".ly4 .obzone",16.1,0.7,{"op":[0,0.16],"ease":"oc"})
T(".ly4 .pop",16.5,0.4,{"op":[0,1],"s":[.2,1],"ease":"ob"},0.16)
T(".sh5",21.3,0.4,{"op":[0,1],"ty":[16,0],"ease":"oc"})
T(".sc5",23.6,0.4,{"op":[0,1],"ty":[14,0],"ease":"oc"})
T(".ly5 .pop",23.1,0.45,{"op":[0,1],"s":[.2,1],"ease":"ob"},0.2)

# 10 REAL (climax)
scene("s10", 9.4, f'''{logo(110)}<div class="top">
  <div class="realh"><span class="eyeb">على السوق الحقيقي</span><span class="tick">EUR/USD يومي</span></div></div>
  <div class="chartbox big mid2">{sc_real_ob()}</div>
  <div class="flowbox"><span class="fx bear">سيولة</span><span class="aw">←</span><span class="fx lvl">اندفاع</span><span class="aw">←</span><span class="fx bull">BOS</span><span class="aw">←</span><span class="fx bull">OB</span></div>
  <div class="capt s6cap">الشروط الأربعة اكتملت — <b class="tt">والمنطقة جاهزة للاختبار</b></div>''')
T(".realh",0.15,0.4,{"op":[0,1],"ty":[20,0],"ease":"oc"})
T(".chartbox",0.25,0.4,{"op":[0,1],"ty":[30,0],"ease":"oc"})
T(".cndl:not(.brk)",0.4,0.18,{"op":[0,1],"sy":[.25,1],"ease":"ob"},0.12)
T(".lvl",3.9,0.6,{"draw":True,"ease":"oc"})
T(".pop",4.2,0.4,{"op":[0,1],"s":[0,1],"ease":"ob"},0.24)
T(".obzone",5.1,0.7,{"op":[0,0.16],"ease":"oc"})
T(".brk",6.3,0.24,{"op":[0,1],"sy":[.15,1],"ease":"ob"},0.18)
T(".brkfx",6.6,0.4,{"op":[0,1],"ty":[26,0],"ease":"oc"})
T(".zz",6.7,0.6,{"draw":True,"ease":"oc"})
T(".bospill",7.0,0.4,{"op":[0,1],"s":[.2,1],"ease":"ob"})
T(".hhpop",7.3,0.45,{"op":[0,1],"s":[.2,1],"ease":"ob"})
T(".flowbox",7.6,0.5,{"op":[0,1],"ty":[20,0],"ease":"oc"})
T(".s6cap",7.9,0.5,{"op":[0,1],"ty":[20,0],"ease":"oc"})

# 11 QUOTE
scene("s11", 3.2, f'''{logo(150)}<div class="mid">
  <div class="qm">”</div>
  <div class="a titan2">المؤسسات ما تطارد السعر…<br><span class="tt">تخليه يرجع لها.</span></div>
  <div class="c hooksub">وأنت؟ ارسم منطقتك وانطرها.</div></div>''')
T(".qm",0.1,0.4,{"op":[0,1],"s":[.4,1],"ease":"ob"})
T(".a",0.4,0.6,{"op":[0,1],"s":[.82,1],"ease":"ob"})
T(".c",1.1,0.5,{"op":[0,1],"ty":[20,0],"ease":"oc"})

# 12 CTA
scene("s12", 3.6, f'''{logo(150)}<div class="mid">
  <div class="a titan2">خلّ الدرس معاك</div>
  <div class="b cbox">احفظ الريل 📌 وشاركه مع متداول</div>
  <div class="c cbox key">علّق «<b class="tt">بلوك</b>» ويوصلك ملف الشرح PDF</div>
  <div class="d hand">{GEM}<span>@liquidity.state</span></div></div>''')
T(".a",0.15,0.5,{"op":[0,1],"s":[.8,1],"ease":"ob"})
T(".b",0.55,0.45,{"op":[0,1],"ty":[24,0],"ease":"oc"})
T(".c",0.9,0.45,{"op":[0,1],"ty":[24,0],"ease":"oc"})
T(".d",1.3,0.45,{"op":[0,1],"ty":[20,0],"ease":"oc"})

# ================= timeline assembly (approved engine) =================
SCN = []; TW = []; t = 0.0
for s in scenes:
    st = round(t, 3); en = round(t + s["dur"], 3); SCN.append([s["id"], st, en])
    for sel, ls, d, sp, stag in s["tw"]:
        TW.append({"sel": f'#{s["id"]} {sel}', "start": round(st + ls, 3), "dur": d, "stag": stag, "sp": sp})
    t = en
DUR = round(t, 3)
REAL = [x for x in SCN if x[0] == "s10"][0][1]
BRK = round(REAL + 6.3, 3)

STAGE = "".join(f'<div class="scene" id="{s["id"]}">{s["html"]}</div>' for s in scenes)

EXTRA_CSS = '.pre{opacity:1}\n.obzone{opacity:0}\n.stepwrap{position:absolute;top:250px;left:80px;right:80px;height:260px}\n.stephead{position:absolute;inset:0;display:flex;flex-direction:column;gap:22px;opacity:0}\n.mid2s{position:absolute;top:560px;left:70px;right:70px}\n.stepcap{position:absolute;bottom:250px;left:90px;right:90px;text-align:center;color:#5C6C73;font-weight:600;font-size:44px;line-height:1.5;opacity:0}\n.stepcap b{color:#0F2E3C;font-weight:900}\n#s10 .flowbox{bottom:428px}\n#s10 .s6cap{bottom:268px;font-size:40px}\n'

JS = f'''
const FPS=30,DUR={DUR},BRK={BRK};
const SCN={json.dumps(SCN)};
const TW={json.dumps(TW)};
function clamp(v,a,b){{return v<a?a:v>b?b:v}}
function E(u,t){{u=clamp(u,0,1);
 if(t=='oc')return 1-Math.pow(1-u,3);
 if(t=='ob'){{const c=1.70158,d=c+1;return 1+d*Math.pow(u-1,3)+c*Math.pow(u-1,2);}}
 return u;}}
function L(a,b,u){{return a+(b-a)*u}}
function apply(el,sp,u){{let tr='';
 if('s'in sp)tr+=`scale(${{L(sp.s[0],sp.s[1],u)}}) `;
 if('sy'in sp)tr+=`scaleY(${{L(sp.sy[0],sp.sy[1],u)}}) `;
 if('tx'in sp)tr+=`translateX(${{L(sp.tx[0],sp.tx[1],u)}}px) `;
 if('ty'in sp)tr+=`translateY(${{L(sp.ty[0],sp.ty[1],u)}}px) `;
 if(tr)el.style.transform=tr;
 if('op'in sp)el.style.opacity=L(sp.op[0],sp.op[1],u);
 if('draw'in sp){{if(el.__len===undefined){{el.__len=(typeof el.getTotalLength==='function')?el.getTotalLength():0;}}
   if(el.__len>0){{el.style.strokeDasharray=el.__len;el.style.strokeDashoffset=el.__len*(1-u);}}else{{el.style.opacity=u;}}}}
}}
function bind(){{for(const w of TW){{w.els=[...document.querySelectorAll(w.sel)];}}}}
function setFrame(t){{
 for(const [id,st,en] of SCN){{
   const el=document.getElementById(id);const FIN=0.45,FOUT=0.4;let op=0;
   if(t>=st-FIN&&t<=en){{if(t<st)op=E((t-(st-FIN))/FIN,'oc');else if(t>en-FOUT)op=1-E((t-(en-FOUT))/FOUT,'oc');else op=1;}}
   el.style.opacity=op;
   const p=clamp((t-st)/(en-st),0,1);el.style.transform=`scale(${{1.008+0.02*p}})`;
 }}
 for(const w of TW){{if(!w.els)continue;w.els.forEach((el,i)=>{{const s=w.start+i*w.stag;if(w.sp.gate&&t<s)return;apply(el,w.sp,E((t-s)/w.dur,w.sp.ease||'lin'));}});}}
 const fl=document.querySelector('#s10 .flash');
 if(fl){{let ft=t-BRK;let o=0;if(ft>0&&ft<0.45){{o=ft<0.12?(ft/0.12)*0.5:0.5*(1-(ft-0.12)/0.33);}}fl.style.opacity=Math.max(0,o);}}
 const cs=document.querySelector('#s10 .chartsvg');
 if(cs){{let zt=t-BRK;let z=0;if(zt>0&&zt<1.1){{z=Math.sin((zt/1.1)*Math.PI)*0.06;}}cs.style.transformOrigin='88% 40%';cs.style.transform=`scale(${{1+z}})`;}}
}}
window.__setFrame=setFrame;window.__DUR=DUR;
bind();setFrame(0);
'''

HTML = f'''<!DOCTYPE html><html lang="ar" dir="rtl"><head><meta charset="UTF-8">
<style>{FONT_CSS}\n{BASECSS}\n{EXTRA_CSS}</style></head>
<body><div id="stage">{STAGE}</div><script>{JS}</script></body></html>'''
open(os.path.join(HERE, "reel_ob.html"), "w", encoding="utf-8").write(HTML)
print(f"wrote reel_ob.html {len(HTML)} bytes | DUR={DUR}s | scenes={len(scenes)} | frames={int(DUR*30)}")
print("scene starts:", [(s[0], s[1]) for s in SCN])
for nm, cx in (("A",OBA),("B",OBB),("C",OBC),("D",OBD),("E",OBE),("F",OBF)):
    print(f"OB{nm}: zone {cx['ztop']:.2f}->{cx['zbot']:.2f} lv {cx['lv']:.2f} bi {cx['bi']}")
