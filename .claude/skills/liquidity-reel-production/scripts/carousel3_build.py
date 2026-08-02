# -*- coding: utf-8 -*-
# كاروسيل 3 — الفجوة السعرية FVG (موضوع جديد — قاعدة عدم تكرار المواضيع)
# 1080×1350 · الغلاف غامق (بوستر) والمحتوى فاتح · زوايا حادة · أرقام لاتينية مائلة
import math, json, os
from reel_build import (CREAM, INK, TEAL, TEAL_D, TEAL_L, BULL, BEAR, RED, MUTE, GREY,
                        FONT_CSS, chart, htext, hend, GEM)

HERE = os.path.dirname(os.path.abspath(__file__))
CAND = json.load(open(os.path.join(HERE, "sheet_candidates.json")))
ROW = CAND[3]                      # NQ=F 30m 2026-07-23 — نافذة حرة (غير مستخدمة)
W31 = ROW["w"][:31]                # قص الذيل — القصة: اندفاع → فجوة → رجعة → استمرار
I1, I2, I3, IRT, IEND = 22, 23, 24, 25, 30
GB = W31[I1]["h"]; GT = W31[I3]["l"]   # حدود الفجوة على الفتائل الحقيقية

CARDBD = "#DED8CC"; DK_BG = "#08131C"; CYAN = "#43D4DC"
DK_MAP = [("#2E8CA6", "#43D4DC"), ("#122F3E", "#5E7A88"), ("#0F2E3C", "#D8E5EB"),
          ("#F2EEE7", DK_BG), ("#1E627A", "#3AAFC0"), ("#D24B4B", "#E05656"),
          ("#5C6C73", "#8FA6AF"), ("rgba(15,46,60,0.06)", "rgba(255,255,255,0.06)")]
def dk(svg):
    for a, b in DK_MAP: svg = svg.replace(a, b)
    return svg

# ---------- تخطيطي ثلاث الشموع (رسم يدوي مثبّت) ----------
def candles3(W, H, numbered=False, levels=False):
    C1 = dict(o=3.2, h=4.6, l=2.6, c=4.2)
    C2 = dict(o=4.2, h=11.0, l=3.9, c=10.6)
    C3 = dict(o=10.6, h=12.4, l=7.6, c=11.8)
    y0, y1 = 1.6, 13.4
    my = lambda v: 16 + (y1-v)/(y1-y0)*(H-56)
    xs = [W*0.22, W*0.40, W*0.58]; bw = W*0.085
    s = [f'<svg viewBox="0 0 {W} {H}" width="{W}" height="{H}" xmlns="http://www.w3.org/2000/svg">']
    # صندوق الفجوة: من قمة فتيل 1 إلى قاع فتيل 3 — يمتد يمين
    bx0 = xs[0]-bw*0.9; bx1 = W-18
    s.append(f'<rect x="{bx0:.1f}" y="{my(C3["l"]):.1f}" width="{bx1-bx0:.1f}" height="{my(C1["h"])-my(C3["l"]):.1f}" fill="{TEAL}" style="opacity:0.16"/>')
    s.append(f'<rect x="{bx0:.1f}" y="{my(C3["l"]):.1f}" width="{bx1-bx0:.1f}" height="{my(C1["h"])-my(C3["l"]):.1f}" fill="none" stroke="{TEAL_D}" stroke-width="1"/>')
    s.append(htext((bx0+bx1)/2+W*0.14, (my(C3["l"])+my(C1["h"]))/2+7, "FVG", TEAL_D, 26))
    if levels:
        s.append(f'<line x1="{xs[0]:.1f}" y1="{my(C1["h"]):.1f}" x2="{bx1:.1f}" y2="{my(C1["h"]):.1f}" stroke="{INK}" stroke-width="1.4" stroke-dasharray="5 4" opacity="0.55"/>')
        s.append(f'<line x1="{xs[2]:.1f}" y1="{my(C3["l"]):.1f}" x2="{bx1:.1f}" y2="{my(C3["l"]):.1f}" stroke="{INK}" stroke-width="1.4" stroke-dasharray="5 4" opacity="0.55"/>')
        s.append(htext(bx1-70, my(C1["h"])+24, "قمة الشمعة 1", INK, 15))
        s.append(htext(bx1-70, my(C3["l"])-10, "قاع الشمعة 3", INK, 15))
    for k, (cx, c) in enumerate(zip(xs, (C1, C2, C3))):
        up = c["c"] >= c["o"]; col = BULL if up else BEAR
        top = my(max(c["o"], c["c"])); bot = my(min(c["o"], c["c"]))
        s.append(f'<line x1="{cx:.1f}" y1="{my(c["h"]):.1f}" x2="{cx:.1f}" y2="{my(c["l"]):.1f}" stroke="{col}" stroke-width="3"/>')
        s.append(f'<rect x="{cx-bw/2:.1f}" y="{top:.1f}" width="{bw:.1f}" height="{max(bot-top,3):.1f}" fill="{col}" rx="1"/>')
        if numbered:
            s.append(f'<text x="{cx:.1f}" y="{H-10:.1f}" fill="{TEAL_D}" font-size="24" font-family="Tajawal" '
                     f'font-weight="900" font-style="italic" text-anchor="middle">{k+1}</text>')
    return "".join(s) + "</svg>"

# ---------- تخطيطي zigzag (خط سعر) ----------
def sk(pts, W=880, H=400, lines=(), zone=None, zlabel="FVG", circle=None, arrow=None,
       texts=(), bos=None, fs0=18):
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    for seg in lines: xs += [q[0] for q in seg["p"]]; ys += [q[1] for q in seg["p"]]
    x0, x1 = min(xs), max(xs); y0, y1 = min(ys), max(ys)
    mx = lambda v: 20 + (v-x0)/(x1-x0)*(W-40)
    my = lambda v: 18 + (y1-v)/(y1-y0)*(H-50)
    s = [f'<svg viewBox="0 0 {W} {H}" width="{W}" height="{H}" xmlns="http://www.w3.org/2000/svg">']
    if zone:
        (za, zb2), (zt, zbo) = zone
        s.append(f'<rect x="{mx(za):.1f}" y="{my(zt):.1f}" width="{mx(zb2)-mx(za):.1f}" height="{my(zbo)-my(zt):.1f}" fill="{TEAL}" style="opacity:0.16"/>')
        s.append(f'<rect x="{mx(za):.1f}" y="{my(zt):.1f}" width="{mx(zb2)-mx(za):.1f}" height="{my(zbo)-my(zt):.1f}" fill="none" stroke="{TEAL_D}" stroke-width="1"/>')
        s.append(htext((mx(za)+mx(zb2))/2, (my(zt)+my(zbo))/2+6, zlabel, TEAL_D, fs0-1))
    for seg in lines:
        p = " ".join(f"{mx(a):.1f},{my(b):.1f}" for a, b in seg["p"])
        d = f' stroke-dasharray="{seg["dash"]}"' if seg.get("dash") else ''
        s.append(f'<polyline points="{p}" fill="none" stroke="{seg["c"]}" stroke-width="{seg.get("w",1.8)}"{d}/>')
    p = " ".join(f"{mx(a):.1f},{my(b):.1f}" for a, b in pts)
    s.append(f'<polyline points="{p}" fill="none" stroke="{INK}" stroke-width="2.8" stroke-linecap="round" stroke-linejoin="round"/>')
    if bos:
        (bx0, bx1, bv) = bos
        s.append(f'<line x1="{mx(bx0):.1f}" y1="{my(bv):.1f}" x2="{mx(bx1):.1f}" y2="{my(bv):.1f}" stroke="{INK}" stroke-width="1.6"/>')
        s.append(f'<polygon points="{mx(bx1):.1f},{my(bv)-4:.1f} {mx(bx1):.1f},{my(bv)+4:.1f} {mx(bx1)+8:.1f},{my(bv):.1f}" fill="{INK}"/>')
        s.append(htext(mx(bx0)+18, my(bv)-9, "BOS", INK, fs0-2))
    if circle:
        s.append(f'<circle cx="{mx(circle[0]):.1f}" cy="{my(circle[1]):.1f}" r="13" fill="none" stroke="{RED}" stroke-width="2.6"/>')
    if arrow:
        (a0, a1) = arrow
        ax0, ay0, ax1, ay1 = mx(a0[0]), my(a0[1]), mx(a1[0]), my(a1[1])
        ang = math.atan2(ay1-ay0, ax1-ax0)
        s.append(f'<line x1="{ax0:.1f}" y1="{ay0:.1f}" x2="{ax1:.1f}" y2="{ay1:.1f}" stroke="{INK}" stroke-width="2.8"/>')
        for da in (ang+2.65, ang-2.65):
            s.append(f'<line x1="{ax1:.1f}" y1="{ay1:.1f}" x2="{ax1+13*math.cos(da):.1f}" y2="{ay1+13*math.sin(da):.1f}" stroke="{INK}" stroke-width="2.8" stroke-linecap="round"/>')
    for (tx, tv, txt, col, fs) in texts:
        s.append(htext(mx(tx), my(tv), txt, col, fs))
    return "".join(s) + "</svg>"

# S2: اندفاع يخلي فراغ والسعر فوق — سهم يرجع للفراغ
SK_GAP = sk(
    pts=[(0,5.2),(0.8,6.6),(1.6,4.2),(2.4,5.4),(3.0,3.6),(4.4,9.8),(5.2,8.8),(6.0,11.6),(6.8,10.4),(7.6,12.6),(8.4,11.4)],
    W=880, H=380, zone=[(3.3,8.8),(7.4,5.6)], zlabel="فراغ ما تداول فيه أحد",
    lines=[{"p":[(8.4,11.0),(8.4,7.8)],"c":RED,"dash":"6 5","w":2.2}],
    texts=[(8.35,7.2,"؟",RED,26)], fs0=17)

# S4: فجوة قوية = بعد BOS مع اندفاع
SK_STRONG = sk(
    pts=[(0,4.6),(0.8,6.4),(1.6,3.6),(2.4,7.4),(3.2,5.4),(4.6,11.4),(5.4,10.2),(6.2,12.8),(7.0,11.6),(7.8,13.8)],
    W=880, H=380, zone=[(3.6,7.7),(8.6,6.4)], bos=(0.8,3.95,6.4),
    texts=[(4.75,12.2,"اندفاع",TEAL_D,17)], fs0=18)

# S5: الرجعة تعبّي الفجوة — دخول/ستوب/هدف
SK_TRADE = sk(
    pts=[(0,4.4),(0.9,6.2),(1.7,3.8),(3.2,10.6),(4.0,9.6),(4.8,11.8),(6.0,7.0),(6.9,9.4),(7.9,13.2)],
    W=880, H=420, zone=[(2.4,6.4),(7.6,5.8)],
    lines=[{"p":[(2.4,3.4),(6.9,3.4)],"c":RED,"dash":"6 5","w":2.0},
           {"p":[(5.6,13.6),(8.6,13.6)],"c":TEAL_D,"dash":"2 6","w":2.0}],
    circle=(6.0,7.05), arrow=((6.9,10.6),(7.85,12.7)),
    texts=[(6.0,5.0,"الدخول",RED,17),(4.6,2.7,"الستوب — تحت قاع الاندفاع",RED,16),
           (6.55,12.95,"الهدف: السيولة اللي فوق",TEAL_D,16)], fs0=18)

# ---------- السوق الحقيقي: الناسداك 30 دقيقة ----------
def fvg_real(W=880, H=480):
    w = W31; n = len(w)
    ymin = min(c["l"] for c in w); ymax = max(c["h"] for c in w)
    pad = (ymax - ymin) * 0.07; ymin -= pad; ymax += pad
    svg, x, y, slot = chart(w, W, H, ymin, ymax, grid=4, pl=10, pr=14, pt=16, pb=12, body=0.6)
    bx0 = x(I1) - slot*0.5; bx1 = x(IEND) + slot*0.5
    svg += (f'<rect x="{bx0:.1f}" y="{y(GT):.1f}" width="{bx1-bx0:.1f}" height="{y(GB)-y(GT):.1f}" '
            f'fill="{TEAL}" style="opacity:0.16"/>'
            f'<rect x="{bx0:.1f}" y="{y(GT):.1f}" width="{bx1-bx0:.1f}" height="{y(GB)-y(GT):.1f}" '
            f'fill="none" stroke="{TEAL_D}" stroke-width="1"/>')
    svg += htext(x(28), (y(GT)+y(GB))/2+6, "FVG", TEAL_D, 19)
    svg += htext(x(I2), y(w[I2]["h"])-12, "اندفاع", TEAL_D, 16)
    svg += f'<circle cx="{x(IRT):.1f}" cy="{y(w[IRT]["l"]):.1f}" r="12" fill="none" stroke="{RED}" stroke-width="2.6"/>'
    svg += htext(x(IRT)+slot*0.2, y(w[IRT]["l"])+30, "الرجعة", RED, 16)
    hi = max(c["h"] for c in w[IRT+1:])
    svg += htext(x(26)+slot*0.6, y(hi)-12, "قمة جديدة", INK, 15)
    return svg + "</svg>"

HERO = dk(candles3(680, 350))

# ---------- مكونات ----------
def brandbar(compact=False):
    sz = 44 if compact else 54; ws = 22 if compact else 26
    return f'''<div class="brand">
      <div class="gem" style="width:{sz}px;height:{sz}px">{GEM}</div>
      <div class="wm"><span class="ln"></span><span class="wmt" style="font-size:{ws}px">LIQUIDITY STATE</span><span class="ln"></span></div>
    </div>'''
def counter(i, total=8):
    return f'<div class="counter"><b>{i}</b><i>/</i><b>{total}</b></div>'
def swipe(dark=False):
    return f'<div class="swipe {"dk" if dark else ""}"><span>اسحب&nbsp;&nbsp;→</span></div>'
def dots(active, total=8, dark=False):
    return f'<div class="dots {"dk" if dark else ""}">' + ''.join(
        f'<span class="dot {"on" if i == active else ""}"></span>' for i in range(1, total+1)) + '</div>'
def eyebrow(t):
    return f'<div class="eyebrow"><span class="dash"></span>{t}<span class="dash"></span></div>'

SL = []
CW = 'data-canvas-width="1080" data-canvas-height="1350"'

# 1 — الغلاف (بوستر غامق): الهوك
SL.append(f'''<div class="slide dark" {CW}>
  {counter(1)}
  <div class="dhd"><div class="hgem">{GEM}</div><div class="hwm"><span class="hln"></span>LIQUIDITY STATE<span class="hln" style="transform:scaleX(-1)"></span></div></div>
  <div class="dcover">
    <div class="deyeb"><span class="dsh"></span>درس — برايس أكشن<span class="dsh"></span></div>
    <h1 class="dbig">ليش السعر يرجع<br>لنفس النقطة؟</h1>
    <div class="tbar"></div>
    <p class="dtag">مو صدفة — اسمها <b>الفجوة السعرية (FVG)</b></p>
    <div class="dchart">{HERO}</div>
  </div>
  {swipe(True)}{dots(1, dark=True)}
</div>''')

# 2 — Stakes
SL.append(f'''<div class="slide" {CW}>
  {counter(2)}
  {brandbar(True)}
  <div class="cont">
    {eyebrow("المشكلة")}
    <h2 class="ttl big">الكل يشوف الاندفاع</h2>
    <p class="lead">الشمعة الاندفاعية تمشي بسرعة… وتخلي وراها <b>فراغ ما تداول فيه أحد</b>. انت تشوف الاندفاع — والسوق شايف الفراغ. وبيرجع له.</p>
    <div class="chartwrap">{SK_GAP}</div>
  </div>
  {swipe()}{dots(2)}
</div>''')

# 3 — شنو الفجوة
SL.append(f'''<div class="slide" {CW}>
  {counter(3)}
  {brandbar(True)}
  <div class="cont">
    <div class="numrow"><span class="num">1</span><h2 class="ttl">شنو الفجوة السعرية؟</h2></div>
    <p class="lead">ثلاث شموع. الوسطى تندفع بقوة. الفراغ بين <b>فتيل الشمعة 1</b> و<b>فتيل الشمعة 3</b> — هذي اهي الفجوة.</p>
    <div class="chartwrap">{candles3(880, 430, numbered=True, levels=True)}</div>
    <div class="note">السعر ما تداول بهالمنطقة أصلًا — عشان جذي يرجع لها بعدين.</div>
  </div>
  {swipe()}{dots(3)}
</div>''')

# 4 — متى تكون قوية
SL.append(f'''<div class="slide" {CW}>
  {counter(4)}
  {brandbar(True)}
  <div class="cont">
    <div class="numrow"><span class="num">2</span><h2 class="ttl">متى تكون الفجوة قوية؟</h2></div>
    <div class="rulerow"><span class="rn">✓</span><p>تجي بعد <b>كسر هيكل (BOS)</b></p></div>
    <div class="rulerow"><span class="rn">✓</span><p>الاندفاع واضح — شمعة كبيرة بجسم كامل</p></div>
    <div class="rulerow"><span class="rn">✓</span><p>مع اتجاهك — الفجوة اللي ضد الاتجاه تفشل وايد</p></div>
    <div class="chartwrap">{SK_STRONG}</div>
  </div>
  {swipe()}{dots(4)}
</div>''')

# 5 — شلون تتداولها
SL.append(f'''<div class="slide" {CW}>
  {counter(5)}
  {brandbar(True)}
  <div class="cont">
    <div class="numrow"><span class="num">3</span><h2 class="ttl">شلون تتداولها؟</h2></div>
    <p class="lead">ما تلحق السعر. <b>تستنى</b> — لين يرجع يعبّي الفجوة، هني مكانك.</p>
    <div class="chartwrap">{SK_TRADE}</div>
    <div class="note">الدخول عند حد الفجوة العلوي أو نصها · الستوب تحت قاع الاندفاع · الهدف السيولة اللي فوق.</div>
  </div>
  {swipe()}{dots(5)}
</div>''')

# 6 — السوق الحقيقي
SL.append(f'''<div class="slide" {CW}>
  {counter(6)}
  {brandbar(True)}
  <div class="cont">
    <div class="realhead">{eyebrow("السوق الحقيقي")}<span class="ticker">الناسداك · 30 دقيقة · {ROW["date"]}</span></div>
    <div class="chartwrap">{fvg_real()}</div>
    <p class="lead">شوف الجارت: اندفاع خلّى فجوة 97 نقطة — السعر رجع، عبّى أولها، وطلع لقمة جديدة.</p>
    <div class="tiny">لغرض تعليمي · بيانات حقيقية</div>
  </div>
  {swipe()}{dots(6)}
</div>''')

# 7 — اقتباس
SL.append(f'''<div class="slide" {CW}>
  {counter(7)}
  {brandbar(True)}
  <div class="quote">
    <div class="qm">”</div>
    <h1 class="big2">السعر ما يحب الفراغ…<br><span class="tt">يرجع يعبّيه.</span></h1>
    <p class="tag2 center">حدد الفجوة قبل — وخلها اهي اللي تجيبك للصفقة.</p>
  </div>
  {swipe()}{dots(7)}
</div>''')

# 8 — CTA
SL.append(f'''<div class="slide" {CW}>
  {counter(8)}
  {brandbar()}
  <div class="cta">
    <h1 class="big2">خلّ الدرس معاك</h1>
    <div class="checkbox">
      <div class="ci"><span class="ck">✓</span><p>احفظ المنشور يرجع لك وقت التحليل</p></div>
      <div class="ci"><span class="ck">✓</span><p>شاركه مع متداول يلحق الاندفاع</p></div>
      <div class="ci"><span class="ck">✓</span><p>علّق كلمة <b class="tt">«فجوة»</b> ويوصلك ملف FVG الكامل</p></div>
    </div>
    <p class="tag2 center">أرسلك الشرح كامل بملف PDF 📩</p>
  </div>
  <div class="botmeta">لغرض تعليمي</div>{dots(8)}
</div>''')

CSS = f'''
*{{margin:0;padding:0;box-sizing:border-box}}
body{{background:#cfcabf;font-family:'Tajawal',sans-serif}}
.slide{{position:relative;width:1080px;height:1350px;overflow:hidden;direction:rtl;
  background:radial-gradient(120% 90% at 50% 0%, #F7F3EC 0%, {CREAM} 45%, #ECE6DB 100%);color:{INK}}}
.counter{{position:absolute;top:56px;left:80px;z-index:6;direction:ltr;display:inline-flex;align-items:center;
  gap:7px;color:{TEAL_D};font-weight:800;font-size:29px;font-style:italic;padding:5px 20px;border-radius:3px;
  border:1.5px solid {TEAL_L};background:rgba(255,255,255,0.5)}}
.counter i{{font-style:normal;opacity:.5;font-weight:600}}
.slide.dark .counter{{color:{CYAN};border-color:rgba(67,212,220,0.55);background:rgba(255,255,255,0.04)}}
.brand{{position:absolute;top:56px;left:0;right:0;display:flex;flex-direction:column;align-items:center;gap:8px;z-index:5}}
.gem{{filter:drop-shadow(0 6px 12px rgba(15,46,60,0.18))}}
.wm{{display:flex;align-items:center;gap:14px}}
.wm .ln{{width:38px;height:2px;background:{TEAL_L};display:inline-block}}
.wmt{{color:{TEAL_D};font-weight:500;letter-spacing:6px}}

.eyebrow{{display:flex;align-items:center;justify-content:center;gap:16px;color:{TEAL};
  font-weight:800;font-size:27px;letter-spacing:.5px}}
.eyebrow .dash{{width:46px;height:3px;background:{TEAL_L};display:inline-block}}

.tt{{color:{TEAL_D}!important}}
.ttl{{font-size:52px;font-weight:900;color:{INK};line-height:1.12;letter-spacing:-.5px}}
.ttl.big{{font-size:62px;text-align:center}}
.big2{{font-size:82px;font-weight:900;color:{INK};line-height:1.14;letter-spacing:-1px;text-align:center}}
.tag2{{font-size:36px;color:{GREY};font-weight:500;margin-top:22px;line-height:1.5}}
.tag2 b{{color:{TEAL_D};font-weight:800}} .tag2.center{{text-align:center}}
.lead{{font-size:33px;line-height:1.55;color:{GREY};font-weight:500}}
.lead b{{color:{INK};font-weight:800}}
.note{{font-size:29px;font-weight:700;color:{INK};background:rgba(46,125,150,0.09);
  border-right:6px solid {TEAL};border-radius:3px;padding:18px 24px;line-height:1.5}}
.note b{{font-weight:900;color:{TEAL_D}}}
.tiny{{font-size:21px;color:{MUTE};font-weight:600;text-align:center}}
.chartwrap{{width:100%;background:#FBF9F5;border:1px solid {CARDBD};border-radius:3px;
  padding:20px;box-shadow:0 18px 44px rgba(15,46,60,0.10)}}
.chartwrap svg{{width:100%;height:auto;display:block}}

.cont{{position:absolute;top:190px;left:90px;right:90px;bottom:170px;display:flex;flex-direction:column;gap:26px;justify-content:center}}
.numrow{{display:flex;align-items:center;gap:18px}}
.num{{width:66px;height:66px;flex:none;display:flex;align-items:center;justify-content:center;font-size:38px;
  font-weight:900;font-style:italic;color:#fff;background:linear-gradient(135deg,{TEAL},{TEAL_D});
  border-radius:2px;box-shadow:0 10px 22px rgba(46,125,150,0.30)}}
.rulerow{{display:flex;align-items:center;gap:16px;background:#FBF9F5;border:1px solid {CARDBD};
  border-radius:3px;padding:16px 22px}}
.rulerow p{{font-size:30px;font-weight:700;color:{GREY}}}
.rulerow p b{{color:{INK};font-weight:900}}
.rn{{width:44px;height:44px;flex:none;display:flex;align-items:center;justify-content:center;border-radius:50%;
  border:2.5px solid {TEAL};color:{TEAL_D};font-size:22px;font-weight:900}}
.realhead{{display:flex;align-items:center;justify-content:space-between}}
.ticker{{color:{TEAL_D};font-weight:800;font-size:24px;background:rgba(46,125,150,0.10);
  padding:7px 16px;border-radius:2px;border:1px solid {TEAL_L};white-space:nowrap}}

.quote{{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;padding:0 110px;text-align:center}}
.qm{{font-size:170px;color:{TEAL_L};line-height:.5;font-weight:900;opacity:.6;margin-bottom:24px}}
.quote .big2{{font-size:72px}} .quote .tag2{{margin-top:34px}}

.cta{{position:absolute;top:210px;left:90px;right:90px;bottom:150px;display:flex;flex-direction:column;
  align-items:center;justify-content:center;gap:40px}}
.checkbox{{width:100%;background:#FBF9F5;border:1px solid {CARDBD};border-radius:3px;padding:14px 26px;
  box-shadow:0 16px 40px rgba(15,46,60,0.10)}}
.ci{{display:flex;align-items:center;gap:18px;padding:22px 4px;border-bottom:1px solid #EDE7DB}}
.ci:last-child{{border-bottom:none}}
.ci p{{font-size:32px;font-weight:700;color:{INK}}} .ci p b{{font-weight:900}}
.ck{{width:48px;height:48px;flex:none;display:flex;align-items:center;justify-content:center;border-radius:50%;
  border:2.5px solid {TEAL};color:{TEAL_D};font-size:26px;font-weight:900}}

.swipe{{position:absolute;bottom:96px;left:0;right:0;display:flex;justify-content:center;z-index:6}}
.swipe span{{color:{TEAL_D};font-weight:800;font-size:28px;padding:10px 34px;
  border:1.5px solid {TEAL_L};border-radius:3px;background:rgba(255,255,255,0.5)}}
.swipe.dk span{{color:{CYAN};border-color:rgba(67,212,220,0.55);background:rgba(255,255,255,0.04)}}
.botmeta{{position:absolute;bottom:100px;left:0;right:0;text-align:center;color:{MUTE};font-size:24px;font-weight:600}}
.dots{{position:absolute;bottom:54px;left:0;right:0;display:flex;gap:10px;justify-content:center;z-index:6}}
.dot{{width:10px;height:10px;border-radius:50%;background:rgba(15,46,60,0.18)}}
.dot.on{{background:{TEAL};width:30px;border-radius:6px}}
.dots.dk .dot{{background:rgba(255,255,255,0.20)}} .dots.dk .dot.on{{background:{CYAN}}}

.slide.dark{{background:radial-gradient(120% 90% at 50% 0%, #0C2029 0%, #08131C 55%, #04090F 100%);color:#ECF3F6}}
.dhd{{position:absolute;top:64px;left:0;right:0;display:flex;flex-direction:column;align-items:center;gap:10px}}
.hgem{{width:58px;height:58px}} .hgem svg{{width:100%;height:100%;filter:drop-shadow(0 0 18px rgba(67,212,220,0.45))}}
.hwm{{display:flex;align-items:center;gap:12px;font-weight:700;font-size:18px;letter-spacing:8px;
  background:linear-gradient(180deg,#ffffff,#C4D4DB 55%,#8FA6AF);-webkit-background-clip:text;background-clip:text;color:transparent}}
.hln{{display:block;width:70px;height:1px;background:linear-gradient(90deg,transparent,rgba(67,212,220,0.7))}}
.dcover{{position:absolute;top:250px;left:80px;right:80px;display:flex;flex-direction:column;align-items:center;text-align:center}}
.deyeb{{display:flex;align-items:center;gap:12px;color:{CYAN};font-weight:800;font-size:27px}}
.dsh{{display:block;width:30px;height:2px;background:{CYAN};box-shadow:0 0 8px rgba(67,212,220,0.5)}}
.dbig{{margin-top:20px;font-size:100px;font-weight:900;line-height:1.12;letter-spacing:-1px;
  background:linear-gradient(180deg,#ffffff,#C4D4DB 60%,#7F97A1);-webkit-background-clip:text;background-clip:text;color:transparent;
  filter:drop-shadow(0 0 26px rgba(67,212,220,0.22))}}
.tbar{{width:430px;height:3px;margin:24px auto 0;
  background:linear-gradient(90deg,transparent,{CYAN},transparent);box-shadow:0 0 10px rgba(67,212,220,0.4)}}
.dtag{{margin-top:24px;font-size:36px;color:#B9CBD3;font-weight:500;line-height:1.5}}
.dtag b{{color:{CYAN};font-weight:800}}
.dchart{{margin-top:44px;width:100%;background:rgba(255,255,255,0.025);border:1px solid rgba(67,212,220,0.28);
  border-radius:3px;padding:22px}}
.dchart svg{{width:72%;height:auto;display:block;margin:0 auto}}
'''

HTML = f'''<!DOCTYPE html><html lang="ar" dir="rtl"><head><meta charset="UTF-8">
<title>الفجوة السعرية FVG — Liquidity State</title>
<meta name="hz:slide-selector" content=".slide">
<meta name="hz:canvas-width" content="1080"><meta name="hz:canvas-height" content="1350">
<style>{FONT_CSS}\n{CSS}</style></head><body>
{''.join(SL)}
</body></html>'''
with open(os.path.join(HERE, "carousel3.html"), "w", encoding="utf-8") as f:
    f.write(HTML)
print("wrote carousel3.html", len(HTML), "bytes", len(SL), "slides | gap %.0f..%.0f (%.0f pts)" % (GB, GT, GT-GB))
