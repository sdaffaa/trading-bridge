# -*- coding: utf-8 -*-
# كاروسيل 2 — أنواع ريتيست الأوردر بلوك الصاعد (وحدة محتوى «ريتيست»: ريل + شيت + كاروسيل)
# 1080×1350 · الغلاف غامق (بوستر) والمحتوى فاتح · زوايا حادة · أرقام لاتينية مائلة
import math, json, os
from reel_build import (CREAM, INK, TEAL, TEAL_D, TEAL_L, BULL, BEAR, RED, MUTE, GREY,
                        FONT_CSS, chart, htext, hend, GEM)

HERE = os.path.dirname(os.path.abspath(__file__))
REAL = {r["cls"]: r for r in json.load(open(os.path.join(HERE, "sheet_real.json")))}

CARDBD = "#DED8CC"; DK_BG = "#08131C"; CYAN = "#43D4DC"
DK_MAP = [("#2E8CA6", "#43D4DC"), ("#122F3E", "#5E7A88"), ("#0F2E3C", "#D8E5EB"),
          ("#F2EEE7", DK_BG), ("#1E627A", "#3AAFC0"), ("#D24B4B", "#E05656"),
          ("#5C6C73", "#8FA6AF"), ("rgba(15,46,60,0.06)", "rgba(255,255,255,0.06)")]
def dk(svg):
    for a, b in DK_MAP: svg = svg.replace(a, b)
    return svg
SYMAR = {"GC=F": "الذهب", "YM=F": "الداو جونز", "NQ=F": "الناسداك",
         "GBPUSD=X": "GBP/USD", "USDJPY=X": "USD/JPY", "AUDUSD=X": "AUD/USD"}
TFAR = {"5m": "5 دقائق", "15m": "15 دقيقة", "30m": "30 دقيقة", "1h": "فريم الساعة"}
def chip(row): return f'{SYMAR[row["sym"]]} · {TFAR[row["tf"]]} · {row["date"]}'

CH_H = 470

# ---------- الشموع الحقيقية (نفس مراسي الشيت — الماركب مثبّت على الفتائل) ----------
def cand_real(row, extras, W=556, H=CH_H):
    w = row["w"]; n = len(w)
    iH, bk, iob, ir = row["iH"], row["bk"], row["iob"], row["ir"]
    ymin = min(c["l"] for c in w); ymax = max(c["h"] for c in w)
    pad = (ymax - ymin) * 0.07; ymin -= pad * 1.6; ymax += pad
    svg, x, y, slot = chart(w, W, H, ymin, ymax, grid=4, pl=10, pr=14, pt=16, pb=12, body=0.6)
    ztop = w[iob]["o"]; zbot = w[iob]["l"]; lv = w[iH]["h"]
    zx0 = x(iob) - slot*0.5; zx1 = x(min(ir + 3, n - 1)) + slot*0.5
    svg += (f'<rect x="{zx0:.1f}" y="{y(ztop):.1f}" width="{zx1-zx0:.1f}" height="{y(zbot)-y(ztop):.1f}" '
            f'fill="{TEAL}" style="opacity:0.16"/>'
            f'<rect x="{zx0:.1f}" y="{y(ztop):.1f}" width="{zx1-zx0:.1f}" height="{y(zbot)-y(ztop):.1f}" '
            f'fill="none" stroke="{TEAL_D}" stroke-width="1"/>')
    svg += htext((zx0+zx1)/2, y(zbot)+23, "زون الطلب", TEAL_D, 17)
    svg += f'<line x1="{x(iH):.1f}" y1="{y(lv):.1f}" x2="{x(bk)+slot*0.55:.1f}" y2="{y(lv):.1f}" stroke="{INK}" stroke-width="1.7"/>'
    svg += hend(x(bk)+slot*0.55, y(lv), INK)
    svg += htext(x(iH)+slot*1.4, y(lv)-10, "BOS", INK, 16)
    svg += f'<circle cx="{x(ir):.1f}" cy="{y(w[ir]["l"]):.1f}" r="12" fill="none" stroke="{RED}" stroke-width="2.6"/>'
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
    s += htext(x((a+b)/2), y(max(hs))-28, "قناة تصحيحية", RED, 17)
    return s

def ex_consol(row, w, x, y, slot):
    ca, cb = row["ca"], row["cb"]
    rt = max(w[k]["h"] for k in range(ca, cb+1)); rb = min(w[k]["l"] for k in range(ca, cb+1))
    s = (f'<line x1="{x(ca)-slot*0.4:.1f}" y1="{y(rt):.1f}" x2="{x(cb)+slot*0.55:.1f}" y2="{y(rt):.1f}" stroke="{INK}" stroke-width="1.6"/>'
         f'<line x1="{x(ca)-slot*0.4:.1f}" y1="{y(rb):.1f}" x2="{x(cb)+slot*0.55:.1f}" y2="{y(rb):.1f}" stroke="{INK}" stroke-width="1.6"/>')
    s += htext(x((ca+cb)/2), y(rt)-12, "تجميع جانبي", INK, 17)
    return s

def ex_sweep(row, w, x, y, slot):
    i1, i2, ipdl = row["i1"], row["i2"], row["ipdl"]
    eq = w[i1]["h"]; pdl = w[ipdl]["l"]
    s = (f'<line x1="{x(i1)-slot*0.6:.1f}" y1="{y(eq):.1f}" x2="{x(i2)+slot*0.55:.1f}" y2="{y(eq):.1f}" stroke="{RED}" stroke-width="1.7"/>'
         f'<line x1="{x(ipdl)-slot*1.6:.1f}" y1="{y(pdl):.1f}" x2="{x(ipdl)+slot*1.6:.1f}" y2="{y(pdl):.1f}" stroke="{INK}" stroke-width="1.5" stroke-dasharray="5 4"/>')
    s += htext(x((i1+i2)/2), y(max(eq, w[i2]["h"]))-14, "سيولة القمم", RED, 17)
    s += htext(x(ipdl), y(pdl)+24, "PDL", INK, 15)
    return s

# ---------- الرسم التخطيطي ----------
def sk(pts, W=396, H=CH_H, lines=(), zone=None, circle=None, arrow=None, texts=(), bos=None, fs0=17):
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
        s.append(htext((mx(za)+mx(zb2))/2, my(zbo)-9, "زون الطلب", TEAL_D, fs0-1))
    for seg in lines:
        p = " ".join(f"{mx(a):.1f},{my(b):.1f}" for a, b in seg["p"])
        d = f' stroke-dasharray="{seg["dash"]}"' if seg.get("dash") else ''
        s.append(f'<polyline points="{p}" fill="none" stroke="{seg["c"]}" stroke-width="1.8"{d}/>')
    p = " ".join(f"{mx(a):.1f},{my(b):.1f}" for a, b in pts)
    s.append(f'<polyline points="{p}" fill="none" stroke="{INK}" stroke-width="2.8" stroke-linecap="round" stroke-linejoin="round"/>')
    if bos:
        (bx0, bx1, bv) = bos
        s.append(f'<line x1="{mx(bx0):.1f}" y1="{my(bv):.1f}" x2="{mx(bx1):.1f}" y2="{my(bv):.1f}" stroke="{INK}" stroke-width="1.6"/>')
        s.append(f'<polygon points="{mx(bx1):.1f},{my(bv)-4:.1f} {mx(bx1):.1f},{my(bv)+4:.1f} {mx(bx1)+8:.1f},{my(bv):.1f}" fill="{INK}"/>')
        s.append(htext(mx(bx0)+18, my(bv)-9, "BOS", INK, fs0-1))
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

SPEC1 = dict(
    pts=[(0,4.2),(0.8,6.2),(1.6,3.4),(2.4,10),(3.0,8.6),(3.6,12.2),(4.2,10.2),(4.6,11.4),(5.2,9.4),(5.6,10.4),(6.2,8.2),(6.6,9.0),(7.1,6.9),(7.9,12.6),(8.6,11.2),(9.4,14.5)],
    lines=[{"p":[(3.6,12.6),(7.0,9.3)],"c":RED},{"p":[(4.0,9.6),(7.35,6.5)],"c":RED}],
    zone=[(1.9,8.2),(7.15,5.6)], circle=(7.1,6.95), arrow=((8.0,9.0),(9.3,13.6)),
    bos=(0.8,2.9,6.4), texts=[(5.6,13.3,"قناة تصحيحية",RED,17)])
SPEC2 = dict(
    pts=[(0,4.4),(0.8,6.4),(1.6,3.5),(2.4,10.4),(3.1,9.0),(3.7,12.4),(4.3,10.6),(4.9,11.8),(5.5,10.5),(6.1,11.7),(6.7,10.6),(7.3,7.0),(8.1,12.8),(8.8,11.4),(9.6,14.7)],
    lines=[{"p":[(4.0,12.1),(6.9,12.1)],"c":INK},{"p":[(4.0,10.3),(7.1,10.3)],"c":INK}],
    zone=[(1.9,8.4),(7.35,5.7)], circle=(7.3,7.05), arrow=((8.2,9.2),(9.5,13.8)),
    bos=(0.8,2.9,6.6), texts=[(5.5,13.2,"تجميع جانبي",INK,17)])
SPEC3 = dict(
    pts=[(0,4.3),(0.8,6.3),(1.6,3.5),(2.4,10.2),(3.1,9.0),(3.8,12.5),(4.5,9.6),(5.3,12.9),(6.0,10.4),(6.6,11.2),(7.3,7.0),(8.1,12.7),(8.8,11.3),(9.6,14.6)],
    lines=[{"p":[(3.4,12.5),(5.8,12.5)],"c":RED},{"p":[(4.1,9.6),(5.0,9.6)],"c":INK,"dash":"5 4"}],
    zone=[(1.9,8.4),(7.35,5.7)], circle=(7.3,7.05), arrow=((8.2,9.2),(9.5,13.7)),
    bos=(0.8,2.9,6.5), texts=[(4.6,13.4,"سيولة القمم",RED,17),(4.55,8.6,"PDL",INK,15)])
SK1 = sk(**SPEC1); SK2 = sk(**SPEC2); SK3 = sk(**SPEC3)

# تعريف الريتيست (تخطيطي أساسي عريض)
SK_DEF = sk(
    pts=[(0,8.6),(0.8,7.0),(1.6,7.8),(2.4,5.6),(3.2,6.2),(3.9,4.2),(4.7,7.2),(5.3,9.6),(6.1,8.6),(6.9,11.8),(7.7,8.8),(8.3,5.3),(9.0,7.6),(9.8,12.6)],
    W=880, H=400, zone=[(3.5,8.6),(5.8,4.0)], circle=(8.3,5.35),
    arrow=((8.9,8.8),(9.7,11.9)), bos=(0,5.0,8.6),
    texts=[(8.3,4.55,"الريتيست",RED,17)], fs0=18)

# هيرو الغلاف الغامق (تخطيطي السحب — هو الهوك)
HERO = dk(sk(**{**SPEC3, "W":820, "H":330,
                "texts":[(4.6,13.6,"سيولة القمم",RED,18),(4.55,8.5,"PDL",INK,16)]}))

R1 = cand_real(REAL["chan"], ex_chan)
R2 = cand_real(REAL["consol"], ex_consol)
R3 = cand_real(REAL["sweep"], ex_sweep)

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

def pattern_slide(idx, num, ttl, chp, lead, sksvg, cndsvg, note):
    return f'''<div class="slide" {CW}>
  {counter(idx)}
  {brandbar(True)}
  <div class="cont2">
    <div class="numrow"><span class="num">{num}</span><h2 class="ttl">{ttl}</h2><span class="ticker">{chp}</span></div>
    <p class="lead">{lead}</p>
    <div class="rcols">
      <div class="col sk"><div class="colcap">التخطيطي</div>{sksvg}</div>
      <div class="col cn"><div class="colcap">السوق الحقيقي</div>{cndsvg}</div>
    </div>
    <div class="note">{note}</div>
    <div class="tiny">لغرض تعليمي · الشموع من السوق الحقيقي والرسم التخطيطي توضيحي</div>
  </div>
  {swipe()}{dots(idx)}
</div>'''

SL = []
CW = 'data-canvas-width="1080" data-canvas-height="1350"'

# 1 — الغلاف (بوستر غامق)
SL.append(f'''<div class="slide dark" {CW}>
  {counter(1)}
  <div class="dhd"><div class="hgem">{GEM}</div><div class="hwm"><span class="hln"></span>LIQUIDITY STATE<span class="hln" style="transform:scaleX(-1)"></span></div></div>
  <div class="dcover">
    <div class="deyeb"><span class="dsh"></span>درس — الأوردر بلوك<span class="dsh"></span></div>
    <h1 class="dbig">أنواع ريتيست<br>الأوردر بلوك</h1>
    <div class="tbar"></div>
    <p class="dtag">نفس الزون… نتيجتين. والفرق كله بشكل الرجعة</p>
    <div class="dchart">{HERO}</div>
  </div>
  {swipe(True)}{dots(1, dark=True)}
</div>''')

# 2 — التعريف
SL.append(f'''<div class="slide" {CW}>
  {counter(2)}
  {brandbar(True)}
  <div class="cont">
    {eyebrow("التعريف")}
    <h2 class="ttl big">شنو الريتيست؟</h2>
    <p class="lead">السعر يكسر الهيكل <b>(BOS)</b> ويطلع، بعدها يرجع يختبر <b>زون الطلب</b> اللي طلّع الكسر — هالرجعة اسمها <b class="tt">الريتيست</b>.</p>
    <div class="chartwrap">{SK_DEF}</div>
    <div class="note">المشكلة؟ الرجعة ما تجي بشكل واحد… تجي بثلاث نماذج — وكل نموذج له تعامل مختلف.</div>
  </div>
  {swipe()}{dots(2)}
</div>''')

# 3/4/5 — النماذج الثلاثة
SL.append(pattern_slide(3, "1", "نموذج الاستمرار — قناة تصحيحية", chip(REAL["chan"]),
  'رجعة منظمة: قمم وقيعان هابطة داخل قناة صغيرة، توصّل السعر للزون خطوة خطوة.',
  SK1, R1,
  'التأكيد: كسر الحد العلوي للقناة وهو داخل الزون — هني الدخول، مو قبل.'))
SL.append(pattern_slide(4, "2", "التجميع الجانبي", chip(REAL["consol"]),
  'السعر يوقف برينج ضيق فوق الزون — يجمع سيولة، وبعدين ينزل نزلة أخيرة يختبر الزون.',
  SK2, R2,
  'التأكيد: كسر الرينج لفوق بعد لمسة الزون — الرينج نفسه مو دخول.'))
SL.append(pattern_slide(5, "3", "سحب سيولة القمم", chip(REAL["sweep"]),
  'قمتين متساويتين فوق الزون = ستوبات مجمّعة. السوق يسحبها أول، وبعدها ينزل للزون ويرتد.',
  SK3, R3,
  'هذا اللي يطق ستوب المستعجل — لا تدخل قبل السحب، وخلّ الستوب تحت PDL.'))

# 6 — شلون تتعامل مع الثلاثة؟
CARDS = [
    ("1", "قناة تصحيحية", "قمم وقيعان هابطة منظمة توصل للزون", "كسر القناة وهو داخل الزون"),
    ("2", "تجميع جانبي", "رينج ضيق يجمع سيولة فوق الزون", "كسر الرينج بعد لمسة الزون"),
    ("3", "سحب السيولة", "قمم متساوية فوق الزون = ستوبات", "بعد السحب والارتداد من الزون"),
]
cards_html = "".join(f'''<div class="card">
  <span class="num">{n}</span>
  <div class="cbody">
    <h3>{t}</h3>
    <div class="crow"><span class="clab">العلامة</span><p>{sign}</p></div>
    <div class="crow"><span class="clab go">الدخول</span><p>{go}</p></div>
  </div>
</div>''' for n, t, sign, go in CARDS)
SL.append(f'''<div class="slide" {CW}>
  {counter(6)}
  {brandbar(True)}
  <div class="cont mid">
    {eyebrow("الخلاصة")}
    <h2 class="ttl big">شلون تتعامل مع الثلاثة؟</h2>
    <div class="cards">{cards_html}</div>
    <div class="note">القاعدة وحدة: الزون يحدد <b>المكان</b> — والنموذج يحدد <b>التوقيت</b>.</div>
  </div>
  {swipe()}{dots(6)}
</div>''')

# 7 — اقتباس
SL.append(f'''<div class="slide" {CW}>
  {counter(7)}
  {brandbar(True)}
  <div class="quote">
    <div class="qm">”</div>
    <h1 class="big2">نفس الزون…<br><span class="tt">نتيجتين.</span></h1>
    <p class="tag2 center">الزون ما يتغيّر — اللي يتغيّر شكل الرجعة اللي توصله.</p>
  </div>
  {swipe()}{dots(7)}
</div>''')

# 8 — CTA
SL.append(f'''<div class="slide" {CW}>
  {counter(8)}
  {brandbar()}
  <div class="cta">
    <h1 class="big2">خذ الدرس معك</h1>
    <div class="checkbox">
      <div class="ci"><span class="ck">✓</span><p>احفظ المنشور يرجع لك وقت التحليل</p></div>
      <div class="ci"><span class="ck">✓</span><p>شاركه مع متداول يطق ستوبه الريتيست</p></div>
      <div class="ci"><span class="ck">✓</span><p>علّق كلمة <b class="tt">«ريتيست»</b> ويوصلك ملف الشرح الكامل</p></div>
    </div>
    <p class="tag2 center">أرسلك الثلاث نماذج بملف PDF 📩</p>
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
.ttl{{font-size:50px;font-weight:900;color:{INK};line-height:1.12;letter-spacing:-.5px}}
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

.cont{{position:absolute;top:190px;left:90px;right:90px;bottom:150px;display:flex;flex-direction:column;gap:28px}}
.cont.mid{{justify-content:center;bottom:170px;gap:34px}}
.cont2{{position:absolute;top:176px;left:56px;right:56px;bottom:206px;display:flex;flex-direction:column;gap:22px}}
.numrow{{display:flex;align-items:center;gap:18px}}
.num{{width:66px;height:66px;flex:none;display:flex;align-items:center;justify-content:center;font-size:38px;
  font-weight:900;font-style:italic;color:#fff;background:linear-gradient(135deg,{TEAL},{TEAL_D});
  border-radius:2px;box-shadow:0 10px 22px rgba(46,125,150,0.30)}}
.numrow .ttl{{flex:1;min-width:0;font-size:44px}}
.ticker{{color:{TEAL_D};font-weight:800;font-size:24px;background:rgba(46,125,150,0.10);
  padding:7px 16px;border-radius:2px;border:1px solid {TEAL_L};white-space:nowrap}}
.cont2 .lead{{font-size:30px}}
.rcols{{flex:1;display:flex;gap:16px;min-height:0}}
.col{{background:#FBF9F5;border:1px solid {CARDBD};border-radius:3px;padding:14px;
  box-shadow:0 14px 34px rgba(15,46,60,0.09);display:flex;flex-direction:column;align-items:center}}
.col.sk{{flex:0 0 408px}} .col.cn{{flex:1}}
.col svg{{width:100%;height:auto;display:block;flex:1;min-height:0}}
.colcap{{font-size:21px;font-weight:800;color:{MUTE};letter-spacing:.5px;margin-bottom:6px}}

.cards{{display:flex;flex-direction:column;gap:20px}}
.card{{display:flex;gap:20px;background:#FBF9F5;border:1px solid {CARDBD};border-radius:3px;
  padding:24px 26px;box-shadow:0 12px 30px rgba(15,46,60,0.08);align-items:flex-start}}
.card .num{{width:58px;height:58px;font-size:32px;margin-top:4px}}
.cbody{{flex:1;min-width:0}}
.cbody h3{{font-size:36px;font-weight:900;color:{INK};margin-bottom:8px}}
.crow{{display:flex;align-items:baseline;gap:14px;margin-top:6px}}
.clab{{flex:none;font-size:22px;font-weight:900;color:#fff;background:{INK};padding:3px 14px;border-radius:2px}}
.clab.go{{background:{TEAL_D}}}
.crow p{{font-size:27px;font-weight:600;color:{GREY};line-height:1.4}}

.quote{{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;padding:0 110px;text-align:center}}
.qm{{font-size:170px;color:{TEAL_L};line-height:.5;font-weight:900;opacity:.6;margin-bottom:24px}}
.quote .big2{{font-size:92px}} .quote .tag2{{margin-top:34px}}

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

/* ---------- الغلاف الغامق ---------- */
.slide.dark{{background:radial-gradient(120% 90% at 50% 0%, #0C2029 0%, #08131C 55%, #04090F 100%);color:#ECF3F6}}
.dhd{{position:absolute;top:64px;left:0;right:0;display:flex;flex-direction:column;align-items:center;gap:10px}}
.hgem{{width:58px;height:58px}} .hgem svg{{width:100%;height:100%;filter:drop-shadow(0 0 18px rgba(67,212,220,0.45))}}
.hwm{{display:flex;align-items:center;gap:12px;font-weight:700;font-size:18px;letter-spacing:8px;
  background:linear-gradient(180deg,#ffffff,#C4D4DB 55%,#8FA6AF);-webkit-background-clip:text;background-clip:text;color:transparent}}
.hln{{display:block;width:70px;height:1px;background:linear-gradient(90deg,transparent,rgba(67,212,220,0.7))}}
.dcover{{position:absolute;top:250px;left:80px;right:80px;display:flex;flex-direction:column;align-items:center;text-align:center}}
.deyeb{{display:flex;align-items:center;gap:12px;color:{CYAN};font-weight:800;font-size:27px}}
.dsh{{display:block;width:30px;height:2px;background:{CYAN};box-shadow:0 0 8px rgba(67,212,220,0.5)}}
.dbig{{margin-top:20px;font-size:104px;font-weight:900;line-height:1.1;letter-spacing:-1px;
  background:linear-gradient(180deg,#ffffff,#C4D4DB 60%,#7F97A1);-webkit-background-clip:text;background-clip:text;color:transparent;
  filter:drop-shadow(0 0 26px rgba(67,212,220,0.22))}}
.tbar{{width:430px;height:3px;margin:24px auto 0;
  background:linear-gradient(90deg,transparent,{CYAN},transparent);box-shadow:0 0 10px rgba(67,212,220,0.4)}}
.dtag{{margin-top:24px;font-size:36px;color:#B9CBD3;font-weight:500;line-height:1.5}}
.dchart{{margin-top:44px;width:100%;background:rgba(255,255,255,0.025);border:1px solid rgba(67,212,220,0.28);
  border-radius:3px;padding:22px}}
.dchart svg{{width:100%;height:auto;display:block}}
'''

HTML = f'''<!DOCTYPE html><html lang="ar" dir="rtl"><head><meta charset="UTF-8">
<title>أنواع ريتيست الأوردر بلوك — Liquidity State</title>
<meta name="hz:slide-selector" content=".slide">
<meta name="hz:canvas-width" content="1080"><meta name="hz:canvas-height" content="1350">
<style>{FONT_CSS}\n{CSS}</style></head><body>
{''.join(SL)}
</body></html>'''
with open(os.path.join(HERE, "carousel2.html"), "w", encoding="utf-8") as f:
    f.write(HTML)
print("wrote carousel2.html", len(HTML), "bytes", len(SL), "slides")
