# -*- coding: utf-8 -*-
# Volume Profile trade reel (60s) — approved Liquidity State engine + all permanent rules.
import os, math, json
from reel_build import (CREAM, CREAM2, INK, TEAL, TEAL_D, TEAL_L, BULL, BEAR, RED, GREY, MUTE,
                        LINE, CARDBD, CYAN, CYANG, FONT_CSS, GEM, chart, gen, htext, hend,
                        logo, IUP, IDN, CSS as BASECSS)
HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 980, 470

# ================= volume profile math (time-at-price, exact bins) =================
def profile(cands, nbins=22):
    hi = max(c["h"] for c in cands); lo = min(c["l"] for c in cands)
    bh = (hi - lo) / nbins; vols = [0.0] * nbins
    for c in cands:
        rng = max(c["h"] - c["l"], 1e-9)
        b0 = max(0, int((c["l"] - lo) / bh)); b1 = min(nbins - 1, int((c["h"] - lo) / bh))
        for b in range(b0, b1 + 1):
            slo = lo + b * bh; shi = slo + bh
            ov = min(c["h"], shi) - max(c["l"], slo)
            if ov > 0: vols[b] += ov / rng
    poc = max(range(nbins), key=lambda b: vols[b])
    order = sorted(range(nbins), key=lambda b: -vols[b]); acc = 0; inc = set()
    for b in order:
        inc.add(b); acc += vols[b]
        if acc >= 0.70 * sum(vols): break
    return dict(lo=lo, hi=hi, bh=bh, vols=vols, ipoc=poc,
                pocp=lo + (poc + 0.5) * bh, vah=lo + (max(inc) + 1) * bh, val=lo + min(inc) * bh)

def vp_bars(prof, x, y, plotL, maxw, cls="vpb"):
    out = []; mx = max(prof["vols"]) or 1
    for b, v in enumerate(prof["vols"]):
        if v <= 0: continue
        p0 = prof["lo"] + b * prof["bh"]; p1 = p0 + prof["bh"]
        yy0 = y(p1); hh = y(p0) - y(p1)
        w = maxw * v / mx
        col = TEAL_D if b == prof["ipoc"] else TEAL
        op = 0.55 if b == prof["ipoc"] else 0.32
        out.append(f'<rect class="{cls}" x="{plotL+2:.2f}" y="{yy0+hh*0.12:.2f}" width="{w:.2f}" '
                   f'height="{hh*0.76:.2f}" fill="{col}" opacity="{op}"/>')
    return "".join(out)

# ================= REAL trade (EUR/USD daily 2025-03-11..2025-04-21) =================
RW = json.load(open(os.path.join(HERE, "vp_window.json")))
for c in RW: c["d"] = c["d"][5:]           # axis shows MM-DD; year shown in the ticker chip
BK, JR = 17, 18                            # breakout / retest candles (from the scan)
PROF_R = profile(RW[:BK])
ENTRY = RW[JR]["c"]; TARGET = RW[29]["c"]
PIPS = round((TARGET - ENTRY) * 10000)

def sc_real_vp(anim=True):
    Wr, Hr = 980, 660
    ymin = min(c["l"] for c in RW) - 0.004; ymax = max(c["h"] for c in RW) + 0.006
    svg, x, y, slot = chart(RW, Wr, Hr, ymin, ymax, price_axis=True, dates=True, grid=5,
                            pt=54, pb=40, pl=12, pr=70)
    # phase candle classes when animated: rp1 range / rp2 breakout / rp3 retest / rp4 rally
    if anim:
        parts = svg.split('<g class="cndl">'); svg = parts[0]
        for i, p in enumerate(parts[1:]):
            ph = "rp1" if i < BK else ("rp2" if i == BK else ("rp3" if i == JR else "rp4"))
            svg += f'<g class="cndl {ph}">' + p
    A = lambda cl: (f'class="{cl}"' if anim else 'class="st"')
    vah, val, pocp = PROF_R["vah"], PROF_R["val"], PROF_R["pocp"]
    plotL = 12
    # value-area band across the range region only
    svg += (f'<rect {A("vband")} x="{plotL:.2f}" y="{y(vah):.2f}" width="{x(BK-1)+slot*0.5-plotL:.2f}" '
            f'height="{y(val)-y(vah):.2f}" fill="{TEAL}" opacity="{0 if anim else 0.10}"/>')
    svg += f'<g {A("vpbwrap")}>{vp_bars(PROF_R, x, y, plotL, (x(BK-1)-plotL)*0.42)}</g>'
    # POC / VAL stop at end of range; VAH stops at the retest candle (its candle)
    svg += f'<line {A("vline draw")} x1="{plotL:.2f}" y1="{y(pocp):.2f}" x2="{x(BK-1)+slot*0.5:.2f}" y2="{y(pocp):.2f}" stroke="{INK}" stroke-width="1.8" stroke-dasharray="7 6"/>'
    svg += f'<line {A("vline draw")} x1="{plotL:.2f}" y1="{y(val):.2f}" x2="{x(BK-1)+slot*0.5:.2f}" y2="{y(val):.2f}" stroke="{MUTE}" stroke-width="1.5"/>'
    svg += f'<line {A("vline draw")} x1="{plotL:.2f}" y1="{y(vah):.2f}" x2="{x(JR)+slot*0.78:.2f}" y2="{y(vah):.2f}" stroke="{INK}" stroke-width="1.8"/>'
    svg += f'<g {A("vlbl pop")}>{hend(x(JR)+slot*0.78, y(vah), INK)}'
    svg += htext(x(2), y(vah)-12, "VAH", INK, 17, weight=800)
    svg += htext(x(BK-3), y(pocp)-12, "POC", INK, 17, weight=800)
    svg += htext(x(2), y(val)+24, "VAL", MUTE, 16, weight=800)
    svg += htext(x(8), y((vah+val)/2)+6, "منطقة القيمة", TEAL_D, 17) + "</g>"
    # breakout arrow with the mandatory gap beside its candle
    ax = x(BK) + slot*0.55
    svg += (f'<g {A("brkfx")}><line x1="{ax:.2f}" y1="{y(RW[BK]["l"])+28:.2f}" x2="{ax:.2f}" y2="{y(vah)+3:.2f}" stroke="{TEAL_D}" stroke-width="2.6"/>'
            f'<polygon points="{ax:.2f},{y(vah)+3:.2f} {ax-6:.2f},{y(vah)+14:.2f} {ax+6:.2f},{y(vah)+14:.2f}" fill="{TEAL_D}"/>'
            f'{htext(x(BK)-slot*0.6, y(RW[BK]["h"])-14, "قبول فوق القيمة", TEAL_D, 17, "end", italic=True, weight=800)}</g>')
    # entry at the retest close + stop under POC
    svg += (f'<g {A("entry pop")}><circle cx="{x(JR):.2f}" cy="{y(ENTRY):.2f}" r="9" fill="none" stroke="{TEAL_D}" stroke-width="2.4"/>'
            f'<polyline points="{x(JR)-4:.2f},{y(ENTRY):.2f} {x(JR)-1:.2f},{y(ENTRY)+3.5:.2f} {x(JR)+5:.2f},{y(ENTRY)-4:.2f}" fill="none" stroke="{TEAL_D}" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/>'
            f'{htext(x(JR), y(RW[JR]["l"])+30, "دخول عند الرجعة", TEAL_D, 17)}</g>')
    # target line + pips
    svg += (f'<g {A("tgt pop")}><line x1="{x(JR):.2f}" y1="{y(TARGET):.2f}" x2="{x(29)+slot*0.5:.2f}" y2="{y(TARGET):.2f}" stroke="{TEAL_D}" stroke-width="1.8" stroke-dasharray="6 5"/>'
            f'{hend(x(29)+slot*0.5, y(TARGET), TEAL_D)}'
            f'{htext(x(24), y(TARGET)-14, f"الهدف  +{PIPS} نقطة", TEAL_D, 19, weight=800)}</g>')
    if anim: svg += f'<rect class="flash" x="0" y="0" width="{Wr}" height="{Hr}" fill="#ffffff" opacity="0"/>'
    return svg + "</svg>"

# ================= synthetic scenarios (fresh seeds; realistic gen) =================
def make_vp(seed, lvl, amp):
    anchors = [(0, lvl), (3, lvl+amp*0.35), (6, lvl-amp*0.4), (9, lvl+amp*0.3), (12, lvl-amp*0.35),
               (15, lvl+amp*0.1), (19, lvl+2.6), (22, lvl+1.5), (29, lvl+3.5)]
    cs = gen(anchors, 30, seed, swings=[(4,'H'), (8,'L'), (12,'H')])
    hi = lvl + amp; lo = lvl - amp
    prev = None
    for i in range(16):                                # keep the value build inside its band
        c0 = cs[i]
        if prev is not None: c0["o"] = prev
        c0["c"] = max(lo+0.15, min(hi-0.15, c0["c"])); c0["o"] = max(lo+0.1, min(hi-0.1, c0["o"]))
        c0["h"] = min(max(c0["h"], max(c0["o"], c0["c"])+0.03), hi)
        c0["l"] = max(min(c0["l"], min(c0["o"], c0["c"])-0.03), lo)
        prev = c0["c"]
    prof = profile(cs[:16])
    # breakout candle 16: full-body acceptance above the range
    cs[16]["o"] = prev; cs[16]["c"] = hi + 1.0
    cs[16]["h"] = cs[16]["c"] + 0.35; cs[16]["l"] = cs[16]["o"] - 0.25
    for i in range(17, 30): cs[i]["o"] = cs[i-1]["c"]  # rechain
    # retest candle 21: low touches VAH exactly, bullish reaction
    cs[21]["o"] = cs[20]["c"]; cs[21]["c"] = max(cs[20]["c"], prof["vah"] + 0.8)
    cs[21]["l"] = prof["vah"]; cs[21]["h"] = max(cs[21]["o"], cs[21]["c"]) + 0.3
    cs[22]["o"] = cs[21]["c"]
    return dict(cs=cs, prof=prof, hi=hi, lo=lo, bk=16, jr=21,
                ymin=min(c["l"] for c in cs)-1.4, ymax=max(c["h"] for c in cs)+2.4)

VPA = make_vp(701, 13.0, 1.9)   # definition chart
VPF = make_vp(706, 12.0, 1.8)   # step-by-step trade chart

def vp_def():
    ctx = VPA; cs = ctx["cs"]; prof = ctx["prof"]
    svg, x, y, slot = chart(cs, W, H, ctx["ymin"], ctx["ymax"], grid=4, pt=48, pb=22, pl=16, pr=16, body=0.5)
    plotL = 16
    svg += (f'<rect class="obzone" x="{plotL}" y="{y(prof["vah"]):.2f}" width="{x(15)+slot*0.5-plotL:.2f}" '
            f'height="{y(prof["val"])-y(prof["vah"]):.2f}" fill="{TEAL}"/>')
    svg += f'<g class="vpbwrap">{vp_bars(prof, x, y, plotL, (x(15)-plotL)*0.42)}</g>'
    svg += f'<line class="draw" x1="{plotL}" y1="{y(prof["pocp"]):.2f}" x2="{x(15)+slot*0.5:.2f}" y2="{y(prof["pocp"]):.2f}" stroke="{INK}" stroke-width="1.8" stroke-dasharray="7 6"/>'
    svg += f'<g class="pop">{htext(x(12), y(prof["pocp"])-12, "POC", INK, 18, weight=800)}'
    svg += htext(x(8), y(prof["vah"])-12, "منطقة القيمة 70%", TEAL_D, 17) + "</g>"
    return svg + "</svg>"

def vp_steps():
    ctx = VPF; cs = ctx["cs"]; prof = ctx["prof"]
    svg, x, y, slot = chart(cs, W, H, ctx["ymin"], ctx["ymax"], grid=4, pt=48, pb=22, pl=16, pr=16, body=0.5)
    parts = svg.split('<g class="cndl">'); svg = parts[0]
    for i, p in enumerate(parts[1:]):
        ph = "cp1" if i <= 15 else ("cp2" if i <= 19 else ("cp3" if i <= 22 else "cp4"))
        svg += f'<g class="cndl {ph}">' + p
    plotL = 16; vah, val, pocp = prof["vah"], prof["val"], prof["pocp"]
    # ly1: profile + value area
    svg += f'<g class="ly1"><rect class="obzone" x="{plotL}" y="{y(vah):.2f}" width="{x(15)+slot*0.5-plotL:.2f}" height="{y(val)-y(vah):.2f}" fill="{TEAL}"/>'
    svg += f'<g class="vpbwrap">{vp_bars(prof, x, y, plotL, (x(15)-plotL)*0.42)}</g>'
    svg += f'<line class="draw" x1="{plotL}" y1="{y(pocp):.2f}" x2="{x(15)+slot*0.5:.2f}" y2="{y(pocp):.2f}" stroke="{INK}" stroke-width="1.8" stroke-dasharray="7 6"/>'
    svg += f'<line class="draw" x1="{plotL}" y1="{y(val):.2f}" x2="{x(15)+slot*0.5:.2f}" y2="{y(val):.2f}" stroke="{MUTE}" stroke-width="1.5"/>'
    svg += f'<line class="draw" x1="{plotL}" y1="{y(vah):.2f}" x2="{x(21)+slot*0.78:.2f}" y2="{y(vah):.2f}" stroke="{INK}" stroke-width="1.8"/>'
    svg += f'<g class="pop">{hend(x(21)+slot*0.78, y(vah), INK)}'
    svg += htext(x(2), y(vah)-12, "VAH", INK, 16, weight=800)
    svg += htext(x(12), y(pocp)-12, "POC", INK, 17, weight=800)
    svg += htext(x(2), y(val)+24, "VAL", MUTE, 15, weight=800)
    svg += htext(x(8), y((vah+val)/2)+6, "منطقة القيمة", TEAL_D, 16) + "</g></g>"
    # ly2: breakout acceptance
    ax = x(16) + slot*0.55
    svg += (f'<g class="ly2"><g class="pop"><line x1="{ax:.2f}" y1="{y(cs[16]["l"])+28:.2f}" x2="{ax:.2f}" y2="{y(vah)+3:.2f}" stroke="{TEAL_D}" stroke-width="2.4"/>'
            f'<polygon points="{ax:.2f},{y(vah)+3:.2f} {ax-6:.2f},{y(vah)+14:.2f} {ax+6:.2f},{y(vah)+14:.2f}" fill="{TEAL_D}"/>'
            f'{htext(x(16)-slot*0.6, y(cs[16]["h"])-14, "إغلاق فوق القيمة", TEAL_D, 17, "end", italic=True, weight=800)}</g></g>')
    # ly3: retest
    svg += (f'<g class="ly3"><g class="pop"><circle cx="{x(21):.2f}" cy="{y(vah):.2f}" r="6" fill="{CREAM}" stroke="{RED}" stroke-width="2.2"/>'
            f'{htext(x(21), y(cs[21]["h"])-16, "رجعة تختبر القيمة", RED, 17)}</g></g>')
    # ly4: entry + stop under POC
    svg += (f'<g class="ly4"><g class="pop"><circle cx="{x(21):.2f}" cy="{y(cs[21]["c"]):.2f}" r="9" fill="none" stroke="{TEAL_D}" stroke-width="2.4"/>'
            f'<polyline points="{x(21)-4:.2f},{y(cs[21]["c"]):.2f} {x(21)-1:.2f},{y(cs[21]["c"])+3.5:.2f} {x(21)+5:.2f},{y(cs[21]["c"])-4:.2f}" fill="none" stroke="{TEAL_D}" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/>'
            f'{htext(x(21)+14, y(cs[21]["c"])-14, "دخول", TEAL_D, 18, "start", weight=800)}'
            f'<line x1="{x(18):.2f}" y1="{y(pocp)+0:.2f}" x2="{x(24):.2f}" y2="{y(pocp)+0:.2f}" stroke="{RED}" stroke-width="1.6" stroke-dasharray="5 5"/>'
            f'{htext(x(24)+10, y(pocp)+6, "ستوب تحت POC", RED, 15, "start")}</g></g>')
    return svg + "</svg>"

# poster icon: profile bars
IPRO = (f'<svg viewBox="0 0 40 40" xmlns="http://www.w3.org/2000/svg"><circle cx="20" cy="20" r="17" fill="none" stroke="{CYAN}" stroke-width="2"/>'
        f'<path d="M13 14 H27 M13 20 H24 M13 26 H19" fill="none" stroke="{CYAN}" stroke-width="2.6" stroke-linecap="round"/></svg>')
IENT = (f'<svg viewBox="0 0 40 40" xmlns="http://www.w3.org/2000/svg"><circle cx="20" cy="20" r="17" fill="none" stroke="{CYAN}" stroke-width="2"/>'
        f'<rect x="12" y="23" width="16" height="6" fill="none" stroke="{CYAN}" stroke-width="2"/>'
        f'<path d="M20 10 V20 M14.5 15.5 L20 21 L25.5 15.5" fill="none" stroke="{CYAN}" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/></svg>')

# ================= scenes =================
scenes = []
def scene(id, dur, html): scenes.append({"id": id, "dur": dur, "html": html, "tw": []})
def T(sel, ls, d, sp, stag=0): scenes[-1]["tw"].append([sel, round(ls, 3), d, sp, stag])

# 1 POSTER
scene("s1", 4.8, f'''<div class="poster">
  <div class="ptag">درس الفوليوم بروفايل</div>
  <div class="pgem">{GEM}</div>
  <div class="pwm"><span class="pln l"></span><span class="pwmt">LIQUIDITY STATE</span><span class="pln r"></span></div>
  <div class="pdivg pd1"><span></span><i></i><span></span></div>
  <h1 class="ptitle">صفقة<br>الفوليوم بروفايل</h1>
  <div class="pdivg pd2"><span></span><i></i><span></span></div>
  <div class="peyeb">وين يجلس الفوليوم… هناك القرار</div>
  <div class="psub2">صفقة كاملة من منطقة القيمة — خطوة بخطوة</div>
  <div class="ppill">4 خطوات + صفقة حقيقية</div>
  <div class="prow">
    <div class="pi p_a"><div class="pic">{IPRO}</div><span>قيمة؟</span></div>
    <div class="pv"></div>
    <div class="pi p_b"><div class="pic">{IUP}</div><span>كسر؟</span></div>
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

# 2 RESULT FIRST (permanent rule)
scene("s2", 5.2, f'''{logo(110)}<div class="top">
  <div class="a eyeb">النتيجة أول شي</div>
  <h2 class="b pipshead">+{PIPS} نقطة</h2>
  <div class="c rule">من رجعة وحدة لمنطقة القيمة — <b>EUR/USD يومي</b></div></div>
  <div class="d chartbox mid2s">{sc_real_vp(anim=False)}</div>
  <div class="e capt s6cap">خلني أوريك <b class="tt">كيف تتحدد</b> هالصفقة خطوة بخطوة</div>''')
T(".a",0.15,0.4,{"op":[0,1],"ty":[20,0],"ease":"oc"})
T(".b",0.45,0.55,{"op":[0,1],"s":[.7,1],"ease":"ob"})
T(".c",1.0,0.45,{"op":[0,1],"ty":[16,0],"ease":"oc"})
T(".d",1.3,0.5,{"op":[0,1],"ty":[30,0],"ease":"oc"})
T(".e",2.4,0.5,{"op":[0,1],"ty":[20,0],"ease":"oc"})

# 3 DEFINITION
scene("s3", 5.4, f'''{logo(120)}<div class="top">
  <div class="realh"><span class="eyeb">التعريف</span></div>
  <h2 class="ttl">شنو الفوليوم بروفايل؟</h2>
  <div class="rule bull">توزيع التداول <b>على الأسعار</b> — يوريك وين جلس السوق فعلًا</div></div>
  <div class="chartbox mid2">{vp_def()}</div>
  <div class="capt"><b>POC</b> = أكثر سعر متداول · <b>منطقة القيمة</b> = 70% من التداول</div>''')
T(".realh",0.15,0.4,{"op":[0,1],"ty":[20,0],"ease":"oc"})
T(".ttl",0.3,0.45,{"op":[0,1],"tx":[40,0],"ease":"oc"})
T(".rule",0.6,0.45,{"op":[0,1],"ty":[20,0],"ease":"oc"})
T(".chartbox",0.75,0.4,{"op":[0,1],"ty":[30,0],"ease":"oc"})
T(".cndl",0.9,0.24,{"op":[0,1],"sy":[.2,1],"ease":"ob"},0.07)
T(".vpbwrap rect",3.0,0.4,{"op":[0,1],"sx":[0,1],"ease":"oc"},0.045)
T(".obzone",3.4,0.5,{"op":[0,0.12],"ease":"oc"})
T(".draw",3.7,0.6,{"draw":True,"ease":"oc"})
T(".pop",4.0,0.4,{"op":[0,1],"s":[.2,1],"ease":"ob"},0.16)
T(".capt",4.2,0.45,{"op":[0,1],"ty":[16,0],"ease":"oc"})

# 4 WHY
scene("s4", 3.6, f'''{logo(150)}<div class="mid">
  <div class="a eyeb2">ليش البروفايل؟</div>
  <div class="b hooksub">السعر يوريك وين راح…<br><b>والفوليوم يوريك وين جلس</b></div>
  <div class="d pillrow"><span class="pl">POC مغناطيس</span><span class="pl">القيمة تنقلب دعم</span><span class="pl">LVN ممرات سريعة</span></div></div>''')
T(".a",0.15,0.45,{"op":[0,1],"ty":[20,0],"ease":"oc"})
T(".b",0.5,0.5,{"op":[0,1],"ty":[20,0],"ease":"oc"})
T(".d .pl",1.15,0.4,{"op":[0,1],"s":[.6,1],"ease":"ob"},0.2)

# 5 MERGED STEPS — one persistent chart, live replay
scene("s5", 26.0, f'''{logo(120)}
  <div class="stepwrap">
    <div class="stephead sh1"><div class="numrow"><span class="num">1</span><h2 class="ttl">ارسم البروفايل</h2></div>
      <div class="rule bull">حدد <b>POC</b> ومنطقة القيمة <b>(70%)</b> على الرينج</div></div>
    <div class="stephead sh2"><div class="numrow"><span class="num">2</span><h2 class="ttl">انتظر القبول خارجها</h2></div>
      <div class="rule bull">إغلاق <b>كامل فوق VAH</b> = السوق قبل أسعار أعلى</div></div>
    <div class="stephead sh3"><div class="numrow"><span class="num">3</span><h2 class="ttl">الرجعة للقيمة</h2></div>
      <div class="rule redr">السعر يرجع <b>يختبر VAH</b> — القيمة القديمة تنقلب دعم</div></div>
    <div class="stephead sh4"><div class="numrow"><span class="num">✓</span><h2 class="ttl">الدخول</h2></div>
      <div class="rule neutral">عند الاختبار — <b>ستوب تحت POC</b> والهدف امتداد الحركة</div></div>
  </div>
  <div class="chartbox mid2s">{vp_steps()}</div>
  <div class="stepcap sc1"><b>POC</b> = أكثر سعر تداول عنده السوق — والقيمة حوله</div>
  <div class="stepcap sc2">فتيل فوق القيمة ما يكفي — <b>نبي إغلاق</b></div>
  <div class="stepcap sc3">هنا تنبنى الصفقة — <b>لا تطارد الكسر</b></div>
  <div class="stepcap sc4">أول لمسة للقيمة = <b class="tt">فرصتك</b> — والرالي يكمّل</div>''')
T(".chartbox",0.2,0.4,{"op":[0,1],"ty":[30,0],"ease":"oc"})
T(".cp1",0.4,0.2,{"op":[0,1],"sy":[.2,1],"ease":"ob"},0.11)
T(".cp2",7.0,0.26,{"op":[0,1],"sy":[.2,1],"ease":"ob"},0.24)
T(".cp3",13.7,0.28,{"op":[0,1],"sy":[.2,1],"ease":"ob"},0.3)
T(".cp4",21.0,0.2,{"op":[0,1],"sy":[.2,1],"ease":"ob"},0.16)
T(".sh1",0.15,0.4,{"op":[0,1],"ty":[16,0],"ease":"oc"});  T(".sh1",6.25,0.35,{"op":[1,0],"gate":1})
T(".ly1 .vpbwrap rect",2.9,0.4,{"op":[0,1],"sx":[0,1],"ease":"oc"},0.05)
T(".ly1 .obzone",3.5,0.5,{"op":[0,0.12],"ease":"oc"})
T(".ly1 .draw",3.8,0.6,{"draw":True,"ease":"oc"})
T(".ly1 .pop",4.2,0.4,{"op":[0,1],"s":[.2,1],"ease":"ob"},0.14)
T(".sc1",4.7,0.4,{"op":[0,1],"ty":[14,0],"ease":"oc"});   T(".sc1",6.25,0.35,{"op":[1,0],"gate":1})
T(".sh2",6.7,0.4,{"op":[0,1],"ty":[16,0],"ease":"oc"});   T(".sh2",12.85,0.35,{"op":[1,0],"gate":1})
T(".ly2 .pop",8.1,0.45,{"op":[0,1],"s":[.2,1],"ease":"ob"})
T(".sc2",8.8,0.4,{"op":[0,1],"ty":[14,0],"ease":"oc"});   T(".sc2",12.85,0.35,{"op":[1,0],"gate":1})
T(".sh3",13.4,0.4,{"op":[0,1],"ty":[16,0],"ease":"oc"});  T(".sh3",19.05,0.35,{"op":[1,0],"gate":1})
T(".ly3 .pop",14.9,0.45,{"op":[0,1],"s":[.2,1],"ease":"ob"})
T(".sc3",15.5,0.4,{"op":[0,1],"ty":[14,0],"ease":"oc"});  T(".sc3",19.05,0.35,{"op":[1,0],"gate":1})
T(".sh4",19.5,0.4,{"op":[0,1],"ty":[16,0],"ease":"oc"})
T(".ly4 .pop",20.2,0.45,{"op":[0,1],"s":[.2,1],"ease":"ob"})
T(".sc4",21.9,0.4,{"op":[0,1],"ty":[14,0],"ease":"oc"})

# 10 REAL TRADE (climax — returns to the s2 example)
scene("s10", 9.4, f'''{logo(110)}<div class="top">
  <div class="realh"><span class="eyeb">الصفقة الحقيقية</span><span class="tick">EUR/USD يومي · 2025</span></div></div>
  <div class="chartbox big mid2">{sc_real_vp(anim=True)}</div>
  <div class="flowbox"><span class="fx bull">قيمة</span><span class="aw">←</span><span class="fx lvl">كسر</span><span class="aw">←</span><span class="fx bear">رجعة</span><span class="aw">←</span><span class="fx bull">هدف</span></div>
  <div class="capt s6cap">نفس الخطوات الأربع — <b class="tt">+{PIPS} نقطة</b> من رجعة وحدة</div>''')
T(".realh",0.15,0.4,{"op":[0,1],"ty":[20,0],"ease":"oc"})
T(".chartbox",0.25,0.4,{"op":[0,1],"ty":[30,0],"ease":"oc"})
T(".rp1",0.4,0.18,{"op":[0,1],"sy":[.25,1],"ease":"ob"},0.13)
T(".vpbwrap rect",3.0,0.35,{"op":[0,1],"sx":[0,1],"ease":"oc"},0.04)
T(".vband",3.6,0.5,{"op":[0,0.10],"ease":"oc"})
T(".vline",3.9,0.55,{"draw":True,"ease":"oc"})
T(".vlbl",4.3,0.4,{"op":[0,1],"s":[.2,1],"ease":"ob"},0.14)
T(".rp2",5.4,0.26,{"op":[0,1],"sy":[.15,1],"ease":"ob"})
T(".brkfx",5.8,0.4,{"op":[0,1],"ty":[24,0],"ease":"oc"})
T(".rp3",6.4,0.26,{"op":[0,1],"sy":[.15,1],"ease":"ob"})
T(".entry",6.8,0.45,{"op":[0,1],"s":[.2,1],"ease":"ob"})
T(".rp4",7.2,0.16,{"op":[0,1],"sy":[.2,1],"ease":"ob"},0.1)
T(".tgt",8.1,0.45,{"op":[0,1],"s":[.3,1],"ease":"ob"})
T(".flowbox",8.4,0.45,{"op":[0,1],"ty":[20,0],"ease":"oc"})
T(".s6cap",8.7,0.45,{"op":[0,1],"ty":[20,0],"ease":"oc"})

# 11 QUOTE
scene("s11", 3.2, f'''{logo(150)}<div class="mid">
  <div class="qm">”</div>
  <div class="a titan2">السعر يتحرك…<br><span class="tt">والفوليوم يتذكر.</span></div>
  <div class="c hooksub">تداول وين جلس السوق — مو وين طاف.</div></div>''')
T(".qm",0.1,0.4,{"op":[0,1],"s":[.4,1],"ease":"ob"})
T(".a",0.4,0.6,{"op":[0,1],"s":[.82,1],"ease":"ob"})
T(".c",1.1,0.5,{"op":[0,1],"ty":[20,0],"ease":"oc"})

# 12 CTA
scene("s12", 3.8, f'''{logo(150)}<div class="mid">
  <div class="a titan2">خلّ الدرس معاك</div>
  <div class="b cbox">احفظ الريل 📌 وشاركه مع متداول</div>
  <div class="c cbox key">علّق «<b class="tt">بروفايل</b>» ويوصلك ملف الشرح PDF</div>
  <div class="d hand">{GEM}<span>@liquidity.state</span></div></div>''')
T(".a",0.15,0.5,{"op":[0,1],"s":[.8,1],"ease":"ob"})
T(".b",0.55,0.45,{"op":[0,1],"ty":[24,0],"ease":"oc"})
T(".c",0.9,0.45,{"op":[0,1],"ty":[24,0],"ease":"oc"})
T(".d",1.3,0.45,{"op":[0,1],"ty":[20,0],"ease":"oc"})

# ================= assembly =================
SCN = []; TW = []; t = 0.0
for s in scenes:
    st = round(t, 3); en = round(t + s["dur"], 3); SCN.append([s["id"], st, en])
    for sel, ls, d, sp, stag in s["tw"]:
        TW.append({"sel": f'#{s["id"]} {sel}', "start": round(st + ls, 3), "dur": d, "stag": stag, "sp": sp})
    t = en
DUR = round(t, 3)
REAL = [x for x in SCN if x[0] == "s10"][0][1]
BRK = round(REAL + 5.4, 3)
STAGE = "".join(f'<div class="scene" id="{s["id"]}">{s["html"]}</div>' for s in scenes)

EXTRA_CSS = ('.obzone{opacity:0}\n.st{}\n'
 '.vpb,.vpbwrap rect{transform-box:fill-box;transform-origin:left center}\n'
 '.stepwrap{position:absolute;top:250px;left:80px;right:80px;height:260px}\n'
 '.stephead{position:absolute;inset:0;display:flex;flex-direction:column;gap:22px;opacity:0}\n'
 '.mid2s{position:absolute;top:560px;left:70px;right:70px}\n'
 '.stepcap{position:absolute;bottom:250px;left:90px;right:90px;text-align:center;color:#5C6C73;'
 'font-weight:600;font-size:44px;line-height:1.5;opacity:0}\n'
 '.stepcap b{color:#0F2E3C;font-weight:900}\n'
 '.pipshead{font-size:110px;font-weight:900;color:#1E627A;text-align:center;letter-spacing:-2px}\n'
 '#s2 .top{top:200px;gap:18px;text-align:center}\n#s2 .rule{text-align:center}\n'
 '#s2 .mid2s{top:640px}\n#s2 .s6cap{bottom:200px;font-size:42px}\n'
 '#s10 .flowbox{bottom:428px}\n#s10 .s6cap{bottom:268px;font-size:40px}\n#s4 .pillrow{flex-wrap:wrap;justify-content:center;max-width:860px}\n#s4 .pl{white-space:nowrap}\n')

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
 if('sx'in sp)tr+=`scaleX(${{L(sp.sx[0],sp.sx[1],u)}}) `;
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
 if(cs){{let zt=t-BRK;let z=0;if(zt>0&&zt<1.1){{z=Math.sin((zt/1.1)*Math.PI)*0.06;}}cs.style.transformOrigin='62% 45%';cs.style.transform=`scale(${{1+z}})`;}}
}}
window.__setFrame=setFrame;window.__DUR=DUR;
bind();setFrame(0);
'''

HTML = f'''<!DOCTYPE html><html lang="ar" dir="rtl"><head><meta charset="UTF-8">
<style>{FONT_CSS}\n{BASECSS}\n{EXTRA_CSS}</style></head>
<body><div id="stage">{STAGE}</div><script>{JS}</script></body></html>'''
open(os.path.join(HERE, "reel_vp.html"), "w", encoding="utf-8").write(HTML)
print(f"wrote reel_vp.html {len(HTML)} bytes | DUR={DUR}s | scenes={len(scenes)} | frames={int(DUR*30)}")
print("real:", RW[0]["d"], "->", RW[29]["d"], "| entry", ENTRY, "| target", TARGET, "| pips", PIPS)
print("VAH", round(PROF_R["vah"],5), "VAL", round(PROF_R["val"],5), "POC", round(PROF_R["pocp"],5))
