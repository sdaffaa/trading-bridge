# -*- coding: utf-8 -*-
# 20-page Market Structure guide — Liquidity State approved defaults.
# Reuses the approved components (colors, gem, charts, htext, data) from reel_build.
import os
from reel_build import (CREAM, CREAM2, INK, TEAL, TEAL_D, TEAL_L, BULL, BEAR, RED, GREY, MUTE,
                        LINE, CARDBD, CYAN, CYANG, FONT_CSS, GEM, C, chart, gen, htext, lbl,
                        zzline, hend, _zpts, UP, UPz, UPh, UPl, DN, DNz, DNl, DNh, CH, CHz, SW,
                        MUP, MCH, MDN, RNG, sc_up, sc_dn, sc_ch, sc_swing, mini_state, mini_bos,
                        mini_choch, sc_real, IUP, IDN, ISW)
import math
HERE = os.path.dirname(os.path.abspath(__file__))
N = 20

# ---------------- extra schematics (all anchored to exact candle OHLC) ----------------
def def_chart():
    cs = UP; W, H = 980, 480
    ymin = min(c["l"] for c in cs) - 1.5; ymax = max(c["h"] for c in cs) + 2.8
    svg, x, y, _ = chart(cs, W, H, ymin, ymax, grid=4, pt=48, pb=22, pl=16, pr=16, body=0.5)
    svg += zzline(x, y, _zpts(cs, UPz), TEAL_D, w=2.2, op=.5)
    svg += lbl(x(17), y(cs[17]["h"]), "قمة", TEAL_D, True)
    svg += lbl(x(22), y(cs[22]["l"]), "قاع", INK, False)
    return svg + "</svg>"

def sc_range():
    cs = gen([(0,15),(4,16.3),(8,13.8),(12,16.2),(16,13.9),(20,16.4),(24,13.7),(28,15.6)], 30, 21,
             wick=0.8, bn=0.45, swings=[(4,'H'),(8,'L'),(12,'H'),(16,'L'),(20,'H'),(24,'L')])
    W, H = 980, 480
    ymin = min(c["l"] for c in cs) - 1.8; ymax = max(c["h"] for c in cs) + 2.6
    svg, x, y, slot = chart(cs, W, H, ymin, ymax, grid=4, pt=48, pb=22, pl=16, pr=16, body=0.5)
    # box bounded by the EXACT highest / lowest wick of the whole range — nothing pierces it
    top_p, top_i = max((cs[i]["h"], i) for i in range(len(cs)))
    bot_p, bot_i = min((cs[i]["l"], i) for i in range(len(cs)))
    x0 = x(0) - slot/2; x1 = x(29) + slot/2
    svg += f'<rect x="{x0:.2f}" y="{y(top_p):.2f}" width="{x1-x0:.2f}" height="{y(bot_p)-y(top_p):.2f}" fill="{TEAL}" opacity="0.15" stroke="{TEAL_D}" stroke-width="1"/>'
    svg += f'<line x1="{x0:.2f}" y1="{y(top_p):.2f}" x2="{x1:.2f}" y2="{y(top_p):.2f}" stroke="{INK}" stroke-width="1.6"/>'
    svg += f'<line x1="{x0:.2f}" y1="{y(bot_p):.2f}" x2="{x1:.2f}" y2="{y(bot_p):.2f}" stroke="{INK}" stroke-width="1.6"/>'
    svg += hend(x0, y(top_p), INK) + hend(x1, y(top_p), INK) + hend(x0, y(bot_p), INK) + hend(x1, y(bot_p), INK)
    svg += f'<circle cx="{x(top_i):.2f}" cy="{y(top_p):.2f}" r="4.5" fill="{INK}" stroke="{CREAM}" stroke-width="1.5"/>'
    svg += f'<circle cx="{x(bot_i):.2f}" cy="{y(bot_p):.2f}" r="4.5" fill="{INK}" stroke="{CREAM}" stroke-width="1.5"/>'
    svg += htext(x(top_i), y(top_p) - 16, "قمة الرينج", INK, 19)
    svg += htext(x(bot_i), y(bot_p) + 28, "قاع الرينج", INK, 19)
    return svg + "</svg>"

def sc_defense():
    cs = UP; W, H = 980, 480
    ymin = min(c["l"] for c in cs) - 2.2; ymax = max(c["h"] for c in cs) + 2.8
    svg, x, y, _ = chart(cs, W, H, ymin, ymax, grid=4, pt=48, pb=22, pl=16, pr=16, body=0.5)
    svg += zzline(x, y, _zpts(cs, UPz), TEAL_D, w=2.0, op=.45)
    hl = cs[22]["l"]  # last higher-low — exact wick
    svg += f'<line x1="{x(22):.2f}" y1="{y(hl):.2f}" x2="{W-16:.2f}" y2="{y(hl):.2f}" stroke="{RED}" stroke-width="2" stroke-dasharray="7 6" opacity="0.9"/>'
    svg += hend(x(22), y(hl), RED)
    svg += lbl(x(28), y(cs[28]["h"]), "HH", TEAL_D, True)
    svg += f'<g>{htext(x(26), y(hl)+30, "خط الدفاع: آخر قاع أعلى", RED, 19)}</g>'
    return svg + "</svg>"

def sc_bos():
    cs = UP; W, H = 980, 480
    ymin = min(c["l"] for c in cs) - 1.5; ymax = max(c["h"] for c in cs) + 3.0
    svg, x, y, _ = chart(cs, W, H, ymin, ymax, grid=4, pt=50, pb=22, pl=16, pr=16, body=0.5)
    lv = cs[17]["h"]  # swing-high wick — exact
    bi = next(i for i in range(18, len(cs)) if cs[i]["c"] > lv)  # first CLOSE above
    svg += zzline(x, y, _zpts(cs, UPz), TEAL_D, w=2.0, op=.4)
    svg += f'<line x1="{x(17):.2f}" y1="{y(lv):.2f}" x2="{W-16:.2f}" y2="{y(lv):.2f}" stroke="{INK}" stroke-width="1.8"/>'
    svg += hend(x(17), y(lv), INK) + hend(W-16, y(lv), INK)
    svg += htext(x(17)-14, y(lv)-14, "آخر قمة", TEAL_D, 18, "end")
    svg += htext(x(21), y(lv)-16, "BOS", INK, 22, weight=800)
    lo_zone = min(cs[i]["l"] for i in range(18, bi+1))
    ay0 = y(lo_zone) + 40
    svg += (f'<line x1="{x(bi):.2f}" y1="{ay0:.2f}" x2="{x(bi):.2f}" y2="{y(lv):.2f}" stroke="{TEAL_D}" stroke-width="2.4"/>'
            f'<polygon points="{x(bi):.2f},{y(lv):.2f} {x(bi)-6:.2f},{y(lv)+11:.2f} {x(bi)+6:.2f},{y(lv)+11:.2f}" fill="{TEAL_D}"/>')
    svg += htext(x(bi), ay0 + 26, "إغلاق فوق القمة", TEAL_D, 18)
    return svg + "</svg>"

def sc_wick():
    cs = gen([(0,12),(5,14.2),(10,13.2),(15,15.8)], 16, 33, wick=0.6, bn=0.35, swings=[(5,'H')])
    lv = cs[5]["h"]  # exact swing-high level
    # candle 9: wick pierces, closes back below (liquidity sweep) — exact construction
    cs[9]["o"] = lv - 0.9; cs[9]["c"] = lv - 0.45; cs[9]["h"] = lv + 0.85; cs[9]["l"] = lv - 1.15
    # candle 13: full-body close above (confirmed break)
    cs[13]["o"] = lv - 0.5; cs[13]["c"] = lv + 0.95; cs[13]["h"] = lv + 1.25; cs[13]["l"] = lv - 0.7
    cs[14]["o"] = cs[13]["c"]; cs[15]["o"] = cs[14]["c"]
    W, H = 980, 480
    ymin = min(c["l"] for c in cs) - 1.6; ymax = max(c["h"] for c in cs) + 2.4
    svg, x, y, _ = chart(cs, W, H, ymin, ymax, grid=4, pt=48, pb=22, pl=16, pr=16, body=0.52)
    svg += f'<line x1="{x(5):.2f}" y1="{y(lv):.2f}" x2="{W-16:.2f}" y2="{y(lv):.2f}" stroke="{INK}" stroke-width="1.8"/>'
    svg += hend(x(5), y(lv), INK) + hend(W-16, y(lv), INK)
    svg += f'<circle cx="{x(9):.2f}" cy="{y(cs[9]["h"]):.2f}" r="4.5" fill="{RED}" stroke="{CREAM}" stroke-width="1.5"/>'
    svg += htext(x(9), y(cs[9]["h"]) - 16, "فتيل فقط = سيولة", RED, 19)
    svg += f'<circle cx="{x(13):.2f}" cy="{y(cs[13]["c"]):.2f}" r="4.5" fill="{TEAL_D}" stroke="{CREAM}" stroke-width="1.5"/>'
    svg += htext(x(13), y(cs[13]["h"]) - 16, "إغلاق فوق = كسر مؤكد", TEAL_D, 19)
    return svg + "</svg>"

# ---- real-data pages (EUR/USD daily, exact wicks) ----
def real_down():
    cs = C[0:15]; W, H = 980, 520
    ymin = 1.1300; ymax = 1.1660
    svg, x, y, _ = chart(cs, W, H, ymin, ymax, price_axis=True, dates=True, grid=5, pt=52, pb=38, pl=12, pr=70)
    svg += zzline(x, y, [(0, cs[0]["h"]), (7, cs[7]["l"]), (13, cs[13]["h"])], LINE, w=2.0, op=.8, dash="1 7")
    svg += f'<circle cx="{x(0):.2f}" cy="{y(cs[0]["h"]):.2f}" r="4.5" fill="{INK}" stroke="{CREAM}" stroke-width="1.5"/>'
    svg += htext(x(0)+10, y(cs[0]["h"]) - 14, "قمة", INK, 19, "start")
    svg += f'<circle cx="{x(7):.2f}" cy="{y(cs[7]["l"]):.2f}" r="4.5" fill="{RED}" stroke="{CREAM}" stroke-width="1.5"/>'
    svg += htext(x(7), y(cs[7]["l"]) + 30, "LL", RED, 20)
    svg += f'<circle cx="{x(13):.2f}" cy="{y(cs[13]["h"]):.2f}" r="4.5" fill="{INK}" stroke="{CREAM}" stroke-width="1.5"/>'
    svg += htext(x(13), y(cs[13]["h"]) - 16, "LH", INK, 20)
    svg += htext(x(4), y(1.1630), "قمم أدنى + قيعان أدنى = هابط ↓", RED, 17, weight=800)
    return svg + "</svg>"

def real_range():
    cs = C[5:33]; off = 5; W, H = 980, 520
    ymin = 1.1280; ymax = 1.1560
    svg, x, y, slot = chart(cs, W, H, ymin, ymax, price_axis=True, dates=True, grid=5, pt=52, pb=38, pl=12, pr=70)
    iLL = 7 - off + 0  # =2  (low 1.13240)
    top_p = C[22]["h"]; bot_p = C[31]["l"]  # 1.14820 / 1.13530 exact
    bx0 = x(22-off) - slot/2; bx1 = x(31-off) + slot/2  # accumulation ends before the thrust candle
    svg += f'<rect x="{bx0:.2f}" y="{y(top_p):.2f}" width="{bx1-bx0:.2f}" height="{y(bot_p)-y(top_p):.2f}" fill="{TEAL}" opacity="0.15" stroke="{TEAL_D}" stroke-width="1"/>'
    svg += htext((bx0+bx1)/2, y((top_p+bot_p)/2)+6, "تجميع", TEAL_D, 20)
    sx0 = x(iLL); sx1 = x(iLL+11)
    svg += f'<line x1="{sx0:.2f}" y1="{y(C[7]["l"]):.2f}" x2="{sx1:.2f}" y2="{y(C[7]["l"]):.2f}" stroke="{INK}" stroke-width="1.6" stroke-dasharray="6 5"/>'
    svg += hend(sx0, y(C[7]["l"]), INK) + hend(sx1, y(C[7]["l"]), INK)
    svg += htext(sx1+18, y(C[7]["l"])+6, "SSL", INK, 18, "start", weight=800)
    svg += f'<circle cx="{x(iLL):.2f}" cy="{y(C[7]["l"]):.2f}" r="4.5" fill="{RED}" stroke="{CREAM}" stroke-width="1.5"/>'
    svg += htext(x(iLL), y(C[7]["l"]) + 30, "LL", RED, 20)
    return svg + "</svg>"

# ---------------- layout ----------------
def pcount(i, dark=False):
    col = CYAN if dark else TEAL_D
    return f'<div class="pcount" style="color:{col};border-color:{col}"><b>{i}</b><i>/</i><b>{N}</b></div>'

def header(i):
    return f'''{pcount(i)}<div class="hd"><div class="hgem">{GEM}</div>
    <div class="hwm"><span class="hln"></span><span class="hwmt">LIQUIDITY STATE</span><span class="hln"></span></div></div>'''

def pbar(i):
    return f'<div class="pbar"><i style="width:{i/N*100:.1f}%"></i></div>'

def eyebrow(t):
    return f'<div class="eyeb"><span class="dsh"></span>{t}<span class="dsh"></span></div>'

PAGES = []
def page(html, dark=False, tag=None):
    i = len(PAGES) + 1
    t = f'<div class="tag">{tag}</div>' if tag else ''
    if dark:
        PAGES.append(f'<div class="slide dark" data-canvas-width="1080" data-canvas-height="1350">{html}{t}{pbar(i)}</div>')
    else:
        PAGES.append(f'<div class="slide" data-canvas-width="1080" data-canvas-height="1350">{header(i)}{html}{t}{pbar(i)}</div>')

# ---- P1 cover (dark poster) ----
page(f'''{pcount(1, True)}<div class="ptag">الدليل الكامل</div>
<div class="pmid">
  <div class="pgem">{GEM}</div>
  <div class="pwm"><span class="pln l"></span><span class="pwmt">LIQUIDITY STATE</span><span class="pln r"></span></div>
  <div class="pdivg"><span></span><i></i><span></span></div>
  <h1 class="ptitle">الماركت<br>ستركجر</h1>
  <div class="pdivg"><span></span><i></i><span></span></div>
  <div class="peyeb">اقرأ السوق قبل لا يتحرّك</div>
  <div class="psub">الدليل الكامل — من تحديد القمم والقيعان إلى قراءة الانعكاس بأمثلة حقيقية</div>
  <div class="ppill">20 صفحة · أمثلة حقيقية</div>
  <div class="prow">
    <div class="pi"><div class="pic">{IUP}</div><span>صاعد؟</span></div><div class="pv"></div>
    <div class="pi"><div class="pic">{IDN}</div><span>هابط؟</span></div><div class="pv"></div>
    <div class="pi"><div class="pic">{ISW}</div><span>انقلاب؟</span></div>
  </div>
</div>''', dark=True)

# ---- P2 problem ----
page(f'''<div class="body">
{eyebrow("ليش هذا الدليل؟")}
<h2 class="ttl">٩٠٪ يدخلون<br><span class="tr">ضد الاتجاه</span></h2>
<p class="lead">السبب مو المؤشرات ولا الحظ… السبب إنهم <b>ما يقرون هيكل السوق</b>. قبل أي صفقة لازم تجاوب سؤال واحد: <b class="tt">منو المسيطر الحين؟</b></p>
<div class="pillrow"><span class="pl">شراء عشوائي</span><span class="pl">ستوب سريع</span><span class="pl">حيرة مستمرة</span></div>
<p class="lead2">بنهاية الدليل بتعرف تحدد الاتجاه، تقرأ الكسر الصح، وتعرف متى السوق انقلب فعلًا.</p>
</div>''')

# ---- P3 definition ----
page(f'''<div class="body">
{eyebrow("التعريف")}
<h2 class="ttl">شنو الماركت ستركجر؟</h2>
<p class="lead">هو <b>تسلسل القمم والقيعان</b> اللي يرسمها السعر. هذا التسلسل هو «خريطة» السوق: منه تعرف السوق صاعد، هابط، أو على وشك ينقلب.</p>
<div class="chartw">{def_chart()}</div>
<div class="note">بدون قراءة الهيكل، تدخل ضد الاتجاه وتسمّيه «ارتداد».</div>
</div>''')

# ---- P4 swing points ----
page(f'''<div class="body">
{eyebrow("الأساس")}
<h2 class="ttl">كيف تحدد القمة والقاع؟</h2>
<p class="rule">القمة المؤثرة = أعلى من الشمعتين اللي حولها، والقاع المؤثر = أدنى من الشمعتين اللي حوله.</p>
<div class="chartw">{sc_swing()}</div>
<p class="capt">حدد القمم والقيعان الصح ← <b>يبين معاك الهيكل</b></p>
</div>''')

# ---- P5 three states ----
page(f'''<div class="body">
{eyebrow("الصورة الكاملة")}
<h2 class="ttl">السوق ما عنده إلا ٣ حالات</h2>
<div class="grid3">
  <div class="st"><div class="mc">{mini_state(MUP,TEAL)}</div><div class="stt tt">صاعد</div></div>
  <div class="st"><div class="mc">{mini_state(MDN,RED)}</div><div class="stt tr">هابط</div></div>
  <div class="st"><div class="mc">{mini_state(RNG,INK)}</div><div class="stt">عرضي</div></div>
</div>
<p class="capt">وظيفتك الأولى قبل أي صفقة: تعرف <b>وين إحنا الحين</b>.</p>
</div>''')

# ---- P6 uptrend ----
page(f'''<div class="body">
<div class="numrow"><span class="num">1</span><h2 class="ttl">الاتجاه الصاعد</h2></div>
<p class="rule"><b class="tt">قمم أعلى (HH)</b> + <b class="tt">قيعان أعلى (HL)</b></p>
<div class="chartw">{sc_up()}</div>
<p class="capt">كل قمة أعلى من اللي قبلها وكل قاع أعلى من اللي قبله ← <b class="tt">المشترين مسيطرين</b>. طالما آخر قاع أعلى ما انكسر، اتجاهك مع الصعود.</p>
</div>''')

# ---- P7 downtrend ----
page(f'''<div class="body">
<div class="numrow"><span class="num">2</span><h2 class="ttl">الاتجاه الهابط</h2></div>
<p class="rule"><b class="tr">قمم أدنى (LH)</b> + <b class="tr">قيعان أدنى (LL)</b></p>
<div class="chartw">{sc_dn()}</div>
<p class="capt">كل قمة وقاع أدنى ← <b class="tr">البائعين مسيطرين</b>. لا تشتري بحجة إنه «صار رخيص».</p>
</div>''')

# ---- P8 range ----
page(f'''<div class="body">
<div class="numrow"><span class="num">3</span><h2 class="ttl">السوق العرضي (الرينج)</h2></div>
<p class="rule">قمم وقيعان عند <b>نفس المستوى تقريبًا</b> — توازن بين الطرفين.</p>
<div class="chartw">{sc_range()}</div>
<p class="capt">لا تطارد السعر داخل الرينج — <b>انتظر الكسر منه</b> وحدد اتجاهك بعده.</p>
</div>''')

# ---- P9 golden rule ----
page(f'''<div class="body">
{eyebrow("قاعدة ذهبية")}
<h2 class="ttl">الاتجاه ما يتغير…<br>إلا بكسر مؤكد</h2>
<p class="lead">آخر قاع أعلى في الصاعد هو <b class="tr">خط الدفاع</b>. طالما صامد، أي نزول مجرد تصحيح — مو انعكاس.</p>
<div class="chartw">{sc_defense()}</div>
<p class="capt">راقب خط الدفاع قبل ما تحكم على السوق.</p>
</div>''')

# ---- P10 BOS ----
page(f'''<div class="body">
{eyebrow("مفهوم الكسر ١")}
<h2 class="ttl">كسر الهيكل — BOS</h2>
<p class="rule">إغلاق <b class="tt">فوق آخر قمة</b> في الصاعد (أو تحت آخر قاع في الهابط) = <b class="tt">استمرار</b> الاتجاه.</p>
<div class="chartw">{sc_bos()}</div>
<p class="capt">BOS يقول لك: الاتجاه الحالي <b>لسا حي</b> — كمّل معه.</p>
</div>''')

# ---- P11 CHoCH ----
page(f'''<div class="body">
{eyebrow("مفهوم الكسر ٢")}
<h2 class="ttl">تغيّر النمط — CHoCH</h2>
<p class="rule">أول كسر <b class="tr">لآخر قاع مؤثر</b> في الصاعد = <b class="tr">تغيّر نمط</b> وبداية انعكاس محتملة.</p>
<div class="chartw">{sc_ch()}</div>
<p class="capt">هنا الاتجاه <b class="tr">انقلب</b> — لا تكابر معه.</p>
</div>''')

# ---- P12 BOS vs CHoCH ----
page(f'''<div class="body">
{eyebrow("الفرق الجوهري")}
<h2 class="ttl">BOS ولا CHoCH؟</h2>
<div class="cmp">
  <div class="cc"><div class="cmc">{mini_bos()}</div><div class="cl tt">BOS</div><div class="cd">كسر <b>مع</b> الاتجاه<br>= استمرار</div></div>
  <div class="cc"><div class="cmc">{mini_choch()}</div><div class="cl tr">CHoCH</div><div class="cd">كسر <b>عكس</b> الاتجاه<br>= انعكاس</div></div>
</div>
<p class="capt">نفس «الكسر» — بس اتجاهه يقلب المعنى. الفرق بينهم = <b>الفرق بين ربح وخسارة</b>.</p>
</div>''')

# ---- P13 wick vs close ----
page(f'''<div class="body">
{eyebrow("قاعدة التأكيد")}
<h2 class="ttl">الفتيل ولا الإغلاق؟</h2>
<p class="rule">الكسر ما يتأكد إلا <b class="tt">بإغلاق شمعة</b> خلف المستوى. الفتيل وحده غالبًا <b class="tr">سحب سيولة</b>.</p>
<div class="chartw">{sc_wick()}</div>
<p class="capt">استعجلت على الفتيل؟ دخلت بفخ السيولة. <b>انتظر الإغلاق</b>.</p>
</div>''')

# ---- P14 real example 1 ----
page(f'''<div class="body">
<div class="realh">{eyebrow("مثال حقيقي ١")}<span class="tick">EUR/USD يومي</span></div>
<h2 class="ttl2">قراءة الهبوط</h2>
<div class="chartw">{real_down()}</div>
<p class="capt">قمة، بعدها قاع أدنى <b class="tr">(LL)</b>، والارتداد وقف بقمة أدنى <b>(LH)</b> — هيكل هابط واضح: البيع هو الاتجاه.</p>
</div>''', tag="لغرض تعليمي · بيانات حقيقية")

# ---- P15 real example 2 ----
page(f'''<div class="body">
<div class="realh">{eyebrow("مثال حقيقي ٢")}<span class="tick">EUR/USD يومي</span></div>
<h2 class="ttl2">سحب السيولة والتجميع</h2>
<div class="chartw">{real_range()}</div>
<p class="capt">بعد القاع <b class="tr">(LL)</b> بقت السيولة تحته <b>(SSL)</b>، ودخل السعر <b class="tt">رينج تجميع</b> — الهدوء اللي يسبق الكسر.</p>
</div>''', tag="لغرض تعليمي · بيانات حقيقية")

# ---- P16 real example 3 ----
page(f'''<div class="body">
<div class="realh">{eyebrow("مثال حقيقي ٣")}<span class="tick">EUR/USD يومي</span></div>
<h2 class="ttl2">الكسر والانعكاس الكامل</h2>
<div class="chartw big">{sc_real().replace('class="boxpop"','class="boxpop" opacity="0.16"')}</div>
<p class="capt">LL ← HL ← <b class="tt">BOS</b> ← HH — انقلب السوق من هابط إلى صاعد، خطوة بخطوة قدامك.</p>
</div>''', tag="لغرض تعليمي · بيانات حقيقية")

# ---- P17 trading plan ----
page(f'''<div class="body">
{eyebrow("التطبيق")}
<h2 class="ttl">خطة القراءة بثلاث خطوات</h2>
<div class="steps">
  <div class="stp"><span class="num">1</span><p>حدد القمم والقيعان المؤثرة ← <b>يبين معاك الهيكل</b> والاتجاه.</p></div>
  <div class="stp"><span class="num">2</span><p>علّق عينك على <b>آخر قمة وآخر قاع مؤثرين</b> — هنا يصير القرار.</p></div>
  <div class="stp"><span class="num">3</span><p>انتظر <b class="tt">الكسر المؤكد بالإغلاق</b>: BOS كمّل معه، CHoCH اقلب معه.</p></div>
</div>
</div>''')

# ---- P18 mistakes ----
page(f'''<div class="body">
{eyebrow("انتبه")}
<h2 class="ttl">٣ أخطاء تدمّر قراءتك</h2>
<div class="steps">
  <div class="stp"><span class="xnum">✕</span><p>تحدد قمم وقيعان <b>عشوائية</b> بدون قاعدة الشمعتين.</p></div>
  <div class="stp"><span class="xnum">✕</span><p>تعتبر <b>كل كسر انعكاس</b> — وتنسى الفرق بين BOS وCHoCH.</p></div>
  <div class="stp"><span class="xnum">✕</span><p>تدخل على <b>الفتيل قبل الإغلاق</b> — وتصير وقود سيولة.</p></div>
</div>
</div>''')

# ---- P19 quote ----
page(f'''<div class="qmid">
<div class="qm">”</div>
<h1 class="qttl">لا تتوقّع السوق…<br><span class="tt">اقرأ هيكله.</span></h1>
<p class="qsub">الاتجاه مو رأي — هو تسلسل قمم وقيعان تشوفه بعينك.</p>
</div>''')

# ---- P20 CTA ----
page(f'''<div class="body ctab">
<h2 class="ttl center">خلّ الدرس معاك</h2>
<div class="steps wide">
  <div class="stp"><span class="cnum">✓</span><p><b>احفظ الملف</b> — يرجع لك وقت التحليل.</p></div>
  <div class="stp"><span class="cnum">✓</span><p><b>شاركه</b> مع متداول يحتاجه.</p></div>
  <div class="stp"><span class="cnum">✓</span><p>علّق «<b class="tt">ستركجر</b>» على المنشور ويوصلك كل جديد.</p></div>
</div>
<div class="hand">{GEM}<span dir="ltr">@liquidity.state</span></div>
</div>''', tag="لغرض تعليمي")

assert len(PAGES) == N, f"expected {N} pages, got {len(PAGES)}"

CSS = f'''*{{margin:0;padding:0;box-sizing:border-box}}
body{{background:#cfcabf;font-family:'Tajawal',sans-serif}}
.slide{{position:relative;width:1080px;height:1350px;overflow:hidden;direction:rtl;
  background:radial-gradient(120% 90% at 50% 0%, #F7F3EC 0%, {CREAM} 45%, {CREAM2} 100%);color:{INK}}}
.slide.dark{{background:radial-gradient(135% 95% at 50% 24%, #0C2029 0%, #08131C 46%, #04090F 100%)}}
.pcount{{position:absolute;top:54px;left:80px;z-index:6;direction:ltr;display:inline-flex;align-items:center;gap:7px;
  font-weight:800;font-size:27px;padding:5px 20px;border-radius:3px;border:1.5px solid;background:transparent}}
.pcount i{{font-style:normal;opacity:.5;font-weight:600}}
.hd{{position:absolute;top:52px;left:0;right:0;display:flex;flex-direction:column;align-items:center;gap:7px;z-index:5}}
.hgem{{width:46px;height:46px;filter:drop-shadow(0 5px 10px rgba(15,46,60,.16))}}
.hwm{{display:flex;align-items:center;gap:12px}}
.hln{{width:34px;height:2px;background:{TEAL_L};display:inline-block}}
.hwmt{{color:{TEAL_D};font-weight:500;letter-spacing:5px;font-size:20px}}
.pbar{{position:absolute;bottom:0;left:0;right:0;height:6px;background:rgba(15,46,60,0.08)}}
.slide.dark .pbar{{background:rgba(67,212,220,0.12)}}
.pbar i{{display:block;height:100%;background:{TEAL}}}
.slide.dark .pbar i{{background:{CYAN}}}
.tag{{position:absolute;bottom:34px;left:0;right:0;text-align:center;color:{MUTE};font-size:21px;font-weight:600}}

.body{{position:absolute;top:180px;left:84px;right:84px;bottom:96px;display:flex;flex-direction:column;gap:26px;justify-content:center}}
.eyeb{{display:flex;align-items:center;justify-content:center;gap:14px;color:{TEAL};font-weight:800;font-size:26px}}
.dsh{{width:42px;height:3px;background:{TEAL_L};display:inline-block}}
.ttl{{font-size:64px;font-weight:900;line-height:1.12;letter-spacing:-.5px;text-align:center}}
.ttl.center{{text-align:center}}
.ttl2{{font-size:54px;font-weight:900;letter-spacing:-.5px;text-align:center}}
.lead{{font-size:34px;line-height:1.6;color:{GREY};font-weight:500;text-align:center}}
.lead b{{color:{INK};font-weight:800}}
.lead2{{font-size:31px;line-height:1.55;color:{GREY};font-weight:500;text-align:center}}
.tt{{color:{TEAL_D}!important}} .tr{{color:{RED}!important}}
.rule{{font-size:35px;font-weight:800;color:{GREY};text-align:center;line-height:1.5}}
.rule b{{font-weight:900}}
.chartw{{width:100%}} .chartw svg{{width:100%;height:auto;display:block}}
.note{{font-size:30px;font-weight:700;color:{INK};background:rgba(46,125,150,0.07);
  border-right:5px solid {TEAL};border-radius:0;padding:20px 26px}}
.capt{{font-size:32px;line-height:1.55;color:{GREY};font-weight:600;text-align:center}}
.capt b{{color:{INK};font-weight:900}}
.pillrow{{display:flex;gap:16px;justify-content:center}}
.pl{{font-size:29px;font-weight:800;color:{RED};border:1.5px solid rgba(210,75,75,.5);padding:11px 24px;border-radius:2px}}
.numrow{{display:flex;align-items:center;gap:20px;justify-content:center}}
.num{{width:76px;height:76px;flex:none;display:flex;align-items:center;justify-content:center;font-size:46px;font-weight:900;
  font-style:italic;color:#fff;background:linear-gradient(135deg,{TEAL},{TEAL_D});border-radius:0}}
.grid3{{display:flex;gap:24px;width:100%}}
.st{{flex:1;text-align:center}} .st .mc svg{{width:100%;height:auto}}
.stt{{font-size:38px;font-weight:900;color:{INK};margin-top:6px}}
.cmp{{display:flex;gap:28px}}
.cc{{flex:1;text-align:center}} .cmc svg{{width:100%;height:auto}}
.cl{{font-size:48px;font-weight:900;margin-top:8px}}
.cd{{font-size:29px;color:{GREY};font-weight:600;margin-top:4px;line-height:1.45}} .cd b{{color:{INK};font-weight:900}}
.realh{{display:flex;align-items:center;justify-content:space-between}}
.tick{{color:{TEAL_D};font-weight:800;font-size:28px;border:1.5px solid {TEAL_L};border-radius:2px;padding:6px 18px}}
.chartw.big svg{{width:100%}}
.steps{{display:flex;flex-direction:column;gap:0;border:1.5px solid {CARDBD};border-radius:0}}
.stp{{display:flex;align-items:center;gap:22px;padding:27px 26px;border-bottom:1.5px solid {CARDBD}}}
.stp:last-child{{border-bottom:none}}
.stp p{{font-size:33px;font-weight:600;color:{GREY};line-height:1.5;text-align:right}}
.stp p b{{color:{INK};font-weight:900}}
.stp .num{{width:64px;height:64px;font-size:38px}}
.xnum{{width:64px;height:64px;flex:none;display:flex;align-items:center;justify-content:center;font-size:34px;
  font-weight:900;color:{RED};border:2px solid {RED};border-radius:0}}
.cnum{{width:64px;height:64px;flex:none;display:flex;align-items:center;justify-content:center;font-size:34px;
  font-weight:900;color:{TEAL_D};border:2px solid {TEAL_D};border-radius:0}}
.hand{{display:flex;align-items:center;gap:14px;justify-content:center;margin-top:10px}}
.hand svg{{width:52px;height:52px}} .hand span{{font-size:36px;font-weight:800;color:{TEAL_D}}}
.qmid{{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;padding:0 100px;text-align:center}}
.qm{{font-size:150px;color:{TEAL_L};line-height:.5;font-weight:900;opacity:.55;margin-bottom:26px}}
.qttl{{font-size:84px;font-weight:900;line-height:1.16;letter-spacing:-1px}}
.qsub{{margin-top:32px;font-size:33px;color:{GREY};font-weight:600}}
.ctab{{justify-content:center}}

/* dark poster (P1) */
.ptag{{position:absolute;top:56px;right:80px;color:{CYAN};border:1.5px solid rgba(67,212,220,.5);border-radius:3px;
  padding:8px 24px;font-size:26px;font-weight:800}}
.pmid{{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;padding:0 90px}}
.pgem{{width:130px;height:130px;filter:drop-shadow(0 0 32px {CYANG})}}
.pwm{{display:flex;align-items:center;gap:14px;margin-top:12px}}
.pln{{width:56px;height:2px}} .pln.l{{background:linear-gradient(90deg,transparent,{CYAN})}} .pln.r{{background:linear-gradient(90deg,{CYAN},transparent)}}
.pwmt{{font-size:34px;font-weight:600;letter-spacing:9px;background:linear-gradient(180deg,#ffffff,#8fa6b0);-webkit-background-clip:text;background-clip:text;color:transparent}}
.pdivg{{display:flex;align-items:center;gap:12px;width:54%;margin:24px 0}}
.pdivg span{{flex:1;height:2px;background:linear-gradient(90deg,transparent,{CYAN},transparent);box-shadow:0 0 12px {CYANG}}}
.pdivg i{{width:10px;height:10px;background:{CYAN};transform:rotate(45deg);box-shadow:0 0 12px {CYAN};flex:none}}
.ptitle{{font-size:126px;font-weight:900;line-height:.98;letter-spacing:-3px;background:linear-gradient(180deg,#ffffff 0%,#C4D4DB 55%,#7F97A1 100%);-webkit-background-clip:text;background-clip:text;color:transparent;filter:drop-shadow(0 3px 18px rgba(67,212,220,.18))}}
.peyeb{{color:{CYAN};font-size:32px;font-weight:800}}
.psub{{color:#C7D6DC;font-size:31px;font-weight:600;margin-top:12px;line-height:1.5;max-width:760px}}
.ppill{{margin-top:30px;color:#EAF2F5;border:1.5px solid rgba(67,212,220,.5);border-radius:3px;padding:13px 34px;font-size:30px;font-weight:800}}
.prow{{display:flex;align-items:flex-start;gap:26px;margin-top:48px}}
.pi{{display:flex;flex-direction:column;align-items:center;gap:12px;width:150px}}
.pic{{width:56px;height:56px;filter:drop-shadow(0 0 10px rgba(67,212,220,.4))}} .pic svg{{width:100%;height:100%;display:block}}
.pi span{{color:{CYAN};font-size:29px;font-weight:800}}
.pv{{width:1.5px;height:82px;background:linear-gradient(180deg,transparent,rgba(67,212,220,.45),transparent);margin-top:8px}}
'''

HTML = f'''<!DOCTYPE html><html lang="ar" dir="rtl"><head><meta charset="UTF-8">
<title>الماركت ستركجر — الدليل الكامل | Liquidity State</title>
<meta name="hz:slide-selector" content=".slide">
<meta name="hz:canvas-width" content="1080"><meta name="hz:canvas-height" content="1350">
<style>{FONT_CSS}\n{CSS}</style></head><body>
{''.join(PAGES)}
</body></html>'''
open(os.path.join(HERE, "guide.html"), "w", encoding="utf-8").write(HTML)
print(f"wrote guide.html {len(HTML)} bytes, {len(PAGES)} pages")
