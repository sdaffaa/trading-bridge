# -*- coding: utf-8 -*-
"""تشغيلة ٤٨ — ريل «نموذج السيولة»: درسٌ مفاهيمي على نافذة حقيقية.

🔒 أمر فهد 2026-08-09: أرسل تسجيلاً لريل حساب آخر (@sixlots) بعنوان
«Liquidity Model» — رسمٌ تخطيطي داكن بلون بنفسجي — وطلب اللون بهويته.
فلم يُعَد تلوين ريل غيرنا ولا قصُّه: بُني الدرس نفسه من جديد بتركيبتنا
وبألفاظ فهد وبنافذة **حقيقية** من مخزن السكان. والمفاهيم الأربعة (بركة
سيولة · سحب · كسر هيكل · سيولة مقابلة) اصطلاحاتُ رسمٍ عامّة لا مِلكَ
لأحد؛ أمّا العنوان والتركيبة والكابشن فتخصّ صاحبها ولم يُنقل منها شيء.

النافذة: الجنيه/الدولار · يومي · 2023-02-22 → 2023-04-28 (٤٨ شمعة).
مخزن `sheet_candidates` نفد كلّه (٢٨/٢٨ مبصومة)، فجُلبت سلسلة يومية من
مصدر §4 المعتمد واختيرت النافذة بالقياس: فرق القاعين ٠٫٣٨٪ من المدى،
وشمعة السحب تغوص ١١٫٥٪ تحتهما وترتدّ بذيلٍ يبلغ ٨٣٪ من مداها.

كل رقمٍ يُقرأ من الشموع عند البناء؛ فإن تغيّرت النافذة تغيّر معها أو سقط
البناء. ولا دخول ولا وقف ولا هدف في هذا الريل: درسٌ لا صفقة.

    python3 run48_model.py           # يكتب reel48_model.html
"""
import json, math, os

from reel_build import (CREAM, INK, TEAL, TEAL_D, RED, GREY, MUTE, RBULL, RBEAR,
                        FONT_CSS, htext, GEM)
import chart_registry

HERE = os.path.dirname(os.path.abspath(__file__))
SLUG, DUR = "model", 21.6
RUN_ID = "run48-model-2026-08-09"
# النافذة من مخزنٍ يوميّ مستقلّ لا من `sheet_candidates`: ذاك المخزن نفد
# بالكامل (٢٨/٢٨ مبصومة في `used_charts.json`)، وإعادة نشر نافذة منشورة
# ممنوعة. فجُلبت سلسلة يومية حقيقية من مصدر §4 المعتمد (Alpha Vantage
# `FX_DAILY`) — خمسة آلاف شمعة بلا فجوة تتجاوز خمسة أيام — واختيرت منها
# النافذة بالقياس: أعلى ذيل رفض على شمعة السحب في كل ما طابق الشروط.
WIN_FILE = "daily_windows/gbpusd_1d_2023-02-22.json"

with open(os.path.join(HERE, WIN_FILE), encoding="utf-8") as _f:
    R = json.load(_f)
W = R["w"]; N = len(W)
NAME = {"BTC-USD": "بتكوين", "ETH-USD": "إيثيريوم", "GC=F": "الذهب",
        "NQ=F": "الناسداك", "YM=F": "الداو جونز", "ES=F": "الإس آند بي",
        "GBPUSD=X": "الجنيه/الدولار", "USDJPY=X": "الدولار/ين"}.get(R["sym"], R["sym"])
TF = {"1d": "يومي", "1h": "ساعة", "30m": "٣٠ دقيقة", "15m": "١٥ دقيقة"}.get(R["tf"], R["tf"])
DP = 0 if max(c["h"] for c in W) > 1000 else 4

# ═════════ القصّة تُستخرج من الشموع ═════════
SPAN = max(c["h"] for c in W) - min(c["l"] for c in W)
TOL = SPAN * 0.05


def _pool():
    """أقربُ قاعين متساويين — بركة السيولة. الشرط ثلاث شمعات بينهما على
    الأقل: قاعان متلاصقان شمعةٌ واحدة ممتدّة لا بركة."""
    lows = sorted(range(N), key=lambda i: W[i]["l"])[:7]
    best = None
    for a in range(len(lows)):
        for b in range(a + 1, len(lows)):
            i, j = sorted((lows[a], lows[b]))
            if j - i < 3:
                continue
            d = abs(W[i]["l"] - W[j]["l"])
            if d <= TOL and (best is None or d < best[2]):
                best = (i, j, d)
    return best


_p = _pool()
assert _p, "النافذة لا تحمل بركة سيولة — لا يُبنى الدرس عليها"
L1, L2, DLOW = _p
POOL = min(W[L1]["l"], W[L2]["l"])

# شمعة السحب: تغوص تحت البركة وتغلق فوقها — الغوصُ وحده ليس سحباً.
SW = next((k for k in range(L2 + 1, N) if W[k]["l"] < POOL and W[k]["c"] > POOL), None)
assert SW is not None, "لا شمعة تسحب البركة وترتدّ — القصّة ناقصة"
_c = W[SW]
DEPTH = POOL - _c["l"]
WICK = DEPTH / (_c["h"] - _c["l"]) if _c["h"] > _c["l"] else 0

# القمّة المرجعية قبل السحب، ثم إغلاقٌ فوقها = كسر الهيكل
HREF = max(range(L1, SW), key=lambda i: W[i]["h"])
LVLH = W[HREF]["h"]
BOS = next((k for k in range(SW + 1, N) if W[k]["c"] > LVLH), None)
assert BOS is not None, "لم يُكسر الهيكل بعد السحب — القصّة ناقصة"
TOP = max(range(BOS, N), key=lambda i: W[i]["h"])
assert TOP > BOS, "لا امتداد بعد الكسر"
RUN = (W[TOP]["h"] - POOL) / SPAN            # نصيب الحركة من مدى النافذة
assert RUN >= 0.5, f"الحركة بعد السحب أقصر من نصف المدى ({RUN:.0%})"
assert L2 < SW < BOS < TOP, "ترتيب القصّة غير متسلسل"

# الطرفان تاريخان كاملان هنا، فالبصمة مباشرة وسليمة المقارنة.
chart_registry.assert_fresh_real(R["sym"], R["tf"], R["start"], R["end"],
                                 label=f"run48-{SLUG}")

# ═════════ هندسة الجارت ═════════
CW, CH = 1000, 1120
_lo = min(c["l"] for c in W); _hi = max(c["h"] for c in W)
# الهامشان غير متساويين عمداً: تحت القيعان يجلس صفّان من الوسوم (السيولة
# ثم السحب)، وفوقها لا وسم إلا وسمُ الهدف الملاصق لقمّته. فهامشٌ متساوٍ
# إمّا يقصّ الصفّ الثاني أو يترك أعلى اللوحة بياضاً.
pl, pr, pt, pb = 16, 22, 26, 24
pw, ph = CW - pl - pr, CH - pt - pb
# الهامش العلوي يُشتقّ من ارتفاع وسم القمّة لا يُثبَّت برقم: الوسم يجلس
# ٥٠ بكسل فوق أعلى فتيل، فهامشٌ أقلّ يدفعه خارج اللوحة (أمسكه `assert`
# أدناه عند ٦٪). والحلّ أن يُحسب الكسر الذي يعطي هذه البكسلات بالضبط.
PAD_LO = 0.20
_need = 56.0                                    # ٢٢ إزاحة + ٢٨ قامة + تنفّس
PAD_HI = round(_need * (1 + PAD_LO) / (ph - _need) + 0.004, 4)
ymin, ymax = _lo - SPAN * PAD_LO, _hi + SPAN * PAD_HI
slot = pw / N; bw = slot * 0.58
def x(i): return pl + slot * i + slot / 2
def y(p): return pt + (ymax - p) / (ymax - ymin) * ph


def tw(txt, fs):
    """عرضٌ تقريبي للنصّ من محارفه — الوسوم تُوضع بالقياس لا بالتقدير،
    وطول الكلمة يتغيّر بالأداة واللغة."""
    return len(txt) * fs * 0.56


def clampx(cx, half):
    """يُبقي وسماً موسَّطاً داخل اللوحة. الرقم المقصوص أسوأ من الوسم المزاح."""
    return min(max(cx, pl + half + 6), CW - pr - half - 6)


def line(x1, y1, x2, y2, col, w=2.4, dash=None, eid=""):
    ln = math.hypot(x2 - x1, y2 - y1)
    d = f' stroke-dasharray="{dash}"' if dash else ''
    i = f' id="{eid}"' if eid else ''
    return (f'<line{i} data-len="{ln:.0f}" x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" '
            f'y2="{y2:.1f}" stroke="{col}" stroke-width="{w}"{d}/>')


svg = [f'<svg viewBox="0 0 {CW} {CH}" width="{CW}" height="{CH}" xmlns="http://www.w3.org/2000/svg">']
for k in range(5):
    gy = pt + ph * k / 4
    svg.append(f'<line x1="{pl}" y1="{gy:.0f}" x2="{CW-pr}" y2="{gy:.0f}" '
               f'stroke="rgba(15,46,60,0.06)" stroke-width="1.5"/>')
for i, c in enumerate(W):
    cx = x(i); up = c["c"] >= c["o"]; col = RBULL if up else RBEAR
    yh, yl, yo, yc = y(c["h"]), y(c["l"]), y(c["o"]), y(c["c"])
    top, bot = min(yo, yc), max(yo, yc); bh = max(bot - top, 2.6)
    svg.append(f'<g class="cnd" id="c{i}">'
               f'<line x1="{cx:.1f}" y1="{yh:.1f}" x2="{cx:.1f}" y2="{yl:.1f}" '
               f'stroke="{col}" stroke-width="2.6"/>'
               f'<rect x="{cx-bw/2:.1f}" y="{top:.1f}" width="{bw:.1f}" height="{bh:.1f}" '
               f'fill="{col}" rx="1"/></g>')

# ── ١) البركة ──
svg.append(line(x(L1) - slot * .7, y(POOL), x(N - 1), y(POOL), TEAL_D, 2.8, eid="pool"))
for n_, j in enumerate((L1, L2)):
    svg.append(f'<g id="eq{n_}" opacity="0"><circle cx="{x(j):.1f}" cy="{y(W[j]["l"]):.1f}" '
               f'r="13" fill="none" stroke="{TEAL_D}" stroke-width="3.4"/></g>')
# صفّان تحت القيعان: وسم البركة أعلاهما ووسم السحب أسفلهما — فلا يلتقيان
# ولا يلامس أيّهما علامة الـ✕. وموضع وسم البركة يُدفع يميناً بعيداً عن
# شمعة السحب: فوقه تقع الشموع، وعند القاعين نفسِهما يشطبها النصّ.
ROW1 = y(POOL) + 40
ROW2 = y(W[SW]["l"]) + 92
PL_TXT, PL_FS = "سيولة تحت القيعان", 27
SW_TXT, SW_FS = "سحب السيولة", 29
PL_X = clampx(x(min(N - 1, SW + 12)), tw(PL_TXT, PL_FS) / 2)
SW_X = clampx(x(SW), tw(SW_TXT, SW_FS) / 2)
assert ROW2 + 16 <= CH - pb, f"صفّ «سحب السيولة» خارج اللوحة ({ROW2:.0f})"
assert ROW2 - ROW1 >= 40, "صفّا الوسوم متلاصقان"
# الوسمان لا يلتقيان أفقياً حين يتقاربان رأسياً
assert abs(PL_X - SW_X) >= (tw(PL_TXT, PL_FS) + tw(SW_TXT, SW_FS)) / 2 + 20 \
    or ROW2 - ROW1 >= 46, "وسما البركة والسحب يتزاحمان"
svg.append(f'<g id="poollbl" opacity="0">'
           + htext(PL_X, ROW1, PL_TXT, TEAL_D, PL_FS) + '</g>')

# ── ٢) السحب ──
svg.append(f'<g id="wick" opacity="0">'
           f'<line x1="{x(SW):.1f}" y1="{y(min(_c["o"], _c["c"])):.1f}" '
           f'x2="{x(SW):.1f}" y2="{y(_c["l"]):.1f}" stroke="{RED}" stroke-width="10" '
           f'stroke-linecap="round" opacity=".5"/></g>')
_xr = 20
svg.append(f'<g id="swp" opacity="0">'
           f'<line data-len="57" x1="{x(SW)-_xr:.1f}" y1="{y(_c["l"])+30-_xr:.1f}" '
           f'x2="{x(SW)+_xr:.1f}" y2="{y(_c["l"])+30+_xr:.1f}" stroke="{RED}" '
           f'stroke-width="5" stroke-linecap="round"/>'
           f'<line data-len="57" x1="{x(SW)-_xr:.1f}" y1="{y(_c["l"])+30+_xr:.1f}" '
           f'x2="{x(SW)+_xr:.1f}" y2="{y(_c["l"])+30-_xr:.1f}" stroke="{RED}" '
           f'stroke-width="5" stroke-linecap="round"/></g>')
svg.append(f'<g id="swplbl" opacity="0">'
           + htext(SW_X, ROW2, SW_TXT, RED, SW_FS) + '</g>')

# ── ٣) كسر الهيكل ──
svg.append(line(x(HREF) - slot * .7, y(LVLH), x(min(BOS + 4, N - 1)), y(LVLH),
                INK, 2.4, dash="9 7", eid="bos"))
BOS_TXT, BOS_FS = "كسر الهيكل", 28
BOS_X = clampx(x(HREF) + slot * 3.2, tw(BOS_TXT, BOS_FS) / 2)
svg.append(f'<g id="boslbl" opacity="0">'
           + htext(BOS_X, y(LVLH) - 22, BOS_TXT, INK, BOS_FS) + '</g>')
svg.append(f'<g id="bosdot" opacity="0"><circle cx="{x(BOS):.1f}" cy="{y(W[BOS]["c"]):.1f}" '
           f'r="13" fill="none" stroke="{INK}" stroke-width="3.4"/></g>')

# ── ٤) السيولة المقابلة ──
svg.append(line(x(TOP) - slot * 5.0, y(W[TOP]["h"]), x(N - 1), y(W[TOP]["h"]),
                TEAL_D, 2.6, eid="target"))
TG_TXT, TG_FS = "السيولة المقابلة", 28
# قمّة النافذة تقع عند حافتها اليمنى، فوسمٌ موسَّط عليها يخرج نصفه —
# وهو ما قصّ «الس» من «السيولة». يُقصّ الموضع لا النصّ.
TG_X = clampx(x(TOP) - slot * 1.2, tw(TG_TXT, TG_FS) / 2)
assert TG_X + tw(TG_TXT, TG_FS) / 2 <= CW - pr, "وسم «السيولة المقابلة» يتجاوز الحافة"
assert y(W[TOP]["h"]) - 22 - TG_FS >= pt, "وسم «السيولة المقابلة» يعلو حدّ اللوحة"
svg.append(f'<g id="targetlbl" opacity="0">'
           + htext(TG_X, y(W[TOP]["h"]) - 22, TG_TXT, TEAL_D, TG_FS) + '</g>')
svg.append('</svg>')
CHART = "".join(svg)

# فريم-٠ والشموع تتحرّك (§12): التكشّف يبدأ من ٠٫٠٨ لا من صفر
OPEN = [(i, round(0.08 + 0.021 * i, 3)) for i in range(N)]

TXT = [
    ("t1", 0.25, 2.55, "السوق ما يتحرّك عشوائي<br>يمشي على <b>سيولة</b>", 60, INK),
    ("t2", 2.85, 6.10, "أول شي: وين الأوامر محبوسة؟", 54, TEAL_D),
    ("t3", 6.40, 9.90, "ياخذها بشمعة وحدة… ويرجع", 54, RED),
    ("t4", 10.20, 13.60, "بعدها يكسر الهيكل", 54, INK),
    ("t5", 13.90, 17.10, "ويمشي للسيولة المقابلة", 54, TEAL_D),
]
MARKS = [
    ("pool", 3.00, 3.70, "draw"),
    ("eq0", 3.65, 3.92, "pop"), ("eq1", 3.92, 4.19, "pop"),
    ("poollbl", 4.30, 4.62, "pop"),
    ("wick", 6.60, 7.05, "fade"),
    ("swp", 7.05, 7.55, "drawx"),
    ("swplbl", 7.65, 7.97, "pop"),
    ("bos", 10.40, 11.10, "draw"),
    ("bosdot", 11.10, 11.40, "pop"),
    ("boslbl", 11.50, 11.82, "pop"),
    ("target", 14.10, 14.85, "draw"),
    ("targetlbl", 14.95, 15.30, "pop"),
]
DRAWSET = ["pool", "bos", "target"]
DRAWX = ["swp"]
FULLSET = ["eq0", "eq1", "poollbl", "wick", "swplbl", "bosdot", "boslbl", "targetlbl"]

# مؤثرات §12 — على أزمان الأحداث نفسها لا على إيقاعٍ مخترع
SFX = [("whoosh", 0.12, -8), ("tick", 3.00, -12), ("pop", 3.65, -13), ("pop", 3.92, -13),
       ("riser", 5.90, -14), ("impact", 6.62, -7), ("pop", 7.65, -11),
       ("tick", 10.40, -12), ("pop", 11.10, -12),
       ("riser", 13.30, -14), ("success", 14.15, -9), ("pop", 17.30, -10)]

texts = "".join(f'<div class="hl" id="{i}" style="font-size:{fs}px;color:{col}">{t}</div>'
                for i, a, b, t, fs, col in TXT)

html = f'''<!DOCTYPE html><html lang="ar" dir="rtl"><head><meta charset="utf-8"><style>
{FONT_CSS}
*{{margin:0;padding:0;box-sizing:border-box}}
#stage{{width:1080px;height:1920px;position:relative;overflow:hidden;font-family:Tajawal;
  background:radial-gradient(120% 90% at 50% 0%, #F7F3EC 0%, #F2EEE7 55%, #ECE6DB 100%)}}
.hl{{position:absolute;top:154px;left:44px;right:44px;text-align:center;font-weight:900;
  line-height:1.24;opacity:0}}
.hl b{{color:{TEAL_D}}}
#head{{position:absolute;top:52px;left:0;right:0;text-align:center;opacity:0}}
#head .gm{{width:44px;margin:0 auto}} #head .gm svg{{width:44px;height:auto}}
#head .wm{{margin-top:6px;font-size:19px;font-weight:800;letter-spacing:7px;color:{MUTE}}}
#chartwrap{{position:absolute;top:372px;left:40px;width:1000px;height:1120px}}
.cnd{{transform-box:fill-box;transform-origin:50% 100%}}
#chip{{position:absolute;top:314px;right:44px;border:2px solid {TEAL_D};color:{TEAL_D};
  font-weight:800;font-size:25px;padding:7px 18px;opacity:0}}
#res{{position:absolute;top:1522px;left:60px;right:60px;text-align:center;font-weight:900;
  font-size:46px;color:{INK};line-height:1.3;opacity:0}}
#res b{{color:{TEAL_D}}}
#cta{{position:absolute;top:1662px;left:70px;right:70px;text-align:center;opacity:0}}
#cta .k{{display:inline-block;border:2.5px solid {INK};color:{INK};font-weight:900;
  font-size:52px;padding:13px 42px}}
#cta .s{{margin-top:15px;font-weight:700;font-size:30px;color:{GREY}}}
#edu{{position:absolute;bottom:44px;left:0;right:0;text-align:center;font-size:21px;
  color:{MUTE};font-weight:600}}
</style></head><body><div id="stage">
<div id="head"><div class="gm">{GEM}</div><div class="wm">LIQUIDITY STATE</div></div>
{texts}
<div id="chip">{NAME} · {TF}</div>
<div id="chartwrap">{CHART}</div>
<div id="res">من البركة إلى السيولة المقابلة<br><b>{RUN*100:.0f}٪ من مدى النافذة</b></div>
<div id="cta"><span class="k">احفظ المنشور</span><div class="s">وارجع له أول ما تشوف قيعان متساوية</div></div>
<div id="edu">لغرض تعليمي — مو توصية · بيانات حقيقية · {R["date"]}</div>
</div>
<script>
window.__DUR = {DUR};
const $ = id => document.getElementById(id);
const clamp=(v,a,b)=>Math.max(a,Math.min(b,v));
const oc=t=>1-Math.pow(1-t,3);
const ob=t=>{{const c1=1.70158,c3=c1+1;return 1+c3*Math.pow(t-1,3)+c1*Math.pow(t-1,2);}};
const seg=(t,a,b)=>clamp((t-a)/(b-a),0,1);
const OPEN={json.dumps(OPEN)};
const TXTS={json.dumps([[i, a, b] for i, a, b, _, __, ___ in TXT])};
const MARKS={json.dumps(MARKS)};
const DRAWSET={json.dumps(DRAWSET)};
const DRAWX={json.dumps(DRAWX)};
const FULLSET={json.dumps(FULLSET)};
function setLine(el,k){{
  const len=+el.dataset.len||300;
  el.style.strokeDasharray=el.getAttribute("stroke-dasharray")&&k>=1
    ? el.getAttribute("stroke-dasharray") : len;
  el.style.strokeDashoffset=len*(1-k);
  el.style.opacity=k>0?1:0;
}}
window.__setFrame=function(t){{
  for(let i=0;i<{N};i++){{
    const el=$("c"+i), o=OPEN[i], k=seg(t,o[1],o[1]+0.40);
    el.style.opacity=k>0?1:0;
    el.style.transform=`scaleY(${{k>=1?1:0.25+0.75*ob(k)}})`;
  }}
  $("head").style.opacity=oc(seg(t,0.10,0.60));
  $("chip").style.opacity=oc(seg(t,0.20,0.70));
  for(const id of DRAWSET){{
    const m=MARKS.find(m=>m[0]===id);
    setLine($(id), m?seg(t,m[1],m[2]):0);
  }}
  for(const id of DRAWX){{
    const el=$(id), m=MARKS.find(m=>m[0]===id), k=m?seg(t,m[1],m[2]):0;
    el.style.opacity=k>0?1:0;
    const ls=el.querySelectorAll("line");
    setLine(ls[0], Math.min(k*2,1)); setLine(ls[1], clamp(k*2-1,0,1));
  }}
  for(const id of FULLSET){{
    const el=$(id), m=MARKS.find(m=>m[0]===id), k=m?seg(t,m[1],m[2]):0;
    el.style.opacity=oc(k);
    if(m&&m[3]==="pop"){{
      el.style.transformBox="fill-box"; el.style.transformOrigin="50% 50%";
      el.style.transform=`scale(${{0.45+0.55*ob(k)}})`;
    }}
  }}
  for(const [id,a,b] of TXTS){{
    const el=$(id), kin=seg(t,a,a+0.30), kout=seg(t,b,b+0.26);
    el.style.opacity=oc(kin)*(1-kout);
    el.style.transform=`translateY(${{(1-oc(kin))*24}}px)`;
  }}
  $("res").style.opacity=oc(seg(t,17.30,17.90));
  const kc=seg(t,18.60,19.20);
  $("cta").style.opacity=oc(kc);
  $("cta").style.transform=`scale(${{0.88+0.12*ob(kc)}})`;
}};
window.__setFrame(0);
</script></body></html>'''


def _unregister():
    p = os.path.join(HERE, "used_charts.json")
    d = json.load(open(p, encoding="utf-8"))
    for k in ("synthetic", "real"):
        d[k] = [e for e in d[k] if e.get("video") != RUN_ID]
    json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    out = os.path.join(HERE, f"reel48_{SLUG}.html")
    with open(out, "w", encoding="utf-8") as f:
        f.write(html)
    print(f'{SLUG} | {NAME} {TF} {R["date"]} | {DUR}s | شموع {N}\n'
          f'  بركة {L1},{L2} فرق {DLOW:.{DP}f} ({DLOW/SPAN*100:.1f}٪ من المدى)\n'
          f'  سحب عند {SW} · غوص {DEPTH:.{DP}f} · ذيل رفض {WICK*100:.0f}٪ من مدى الشمعة\n'
          f'  كسر الهيكل عند {BOS} فوق قمّة {HREF} · قمّة {TOP} · الحركة {RUN*100:.0f}٪ من المدى\n'
          f'  نافذة {R["date"]} · {len(html)} bytes · مؤثرات {len(SFX)}')
