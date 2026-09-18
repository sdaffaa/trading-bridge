# -*- coding: utf-8 -*-
"""تشغيلة ٥٦ — ريل «وين يروح الستوب؟» بمنطقة القيمة (VAH · POC · VAL).

🔒 أمر فهد 2026-08-12 يفرض دقّة صفرية: ممنوع اختراع أو تعديل شمعة، وممنوع
تحريكها إلى مستوى غير حقيقي، و«إذا لم تكن الأسعار قابلة للتحقق، احذف جميع
الأرقام بدل وضع أرقام تقديرية».

**الفيديو المرجعي وبيانات الصفقة الأصلية لم تصل.** فلا 105.80 ولا 103.80
ولا +1.51R ولا +3.15R يمكن مطابقتها — وحذفُها هو ما يأمر به البريف نفسه.
فبُني الريل على نافذةٍ **تتحقّق بالكامل**: صندوق الشركات الصغيرة IWM يومي،
بيانات OHLCV من Alpha Vantage محفوظة في `content/run55_data/IWM.csv`،
والحجم **حجم أسهم حقيقي من المزوّد لا Tick Volume** (الشرط ٧ يخصّ الذهب
CFD وهذه ليست كذلك).

النموذج الذي تُثبته الشموع — لا الذي نتمنّاه:

    نطاق البروفايل (Fixed Range) 2026-04-09 → 2026-05-05 · ١٩ شمعة يومية
    VAH 282.64 · POC 276.60 · VAL 271.16
    الخروج فوق VAH: 05-06 بإغلاق فوقه · أعلى نقطة 287.58 (فتيل 05-07)
    الإغلاق راجعاً داخل القيمة: 05-07 عند 282.26  ← الدخول
    الوقف 288.01 = قمّة الخروج + هامش ٠٫١٥٪ (لا ملاصقاً للفتيل)
    الهدف ١ = POC بلغه 05-18 · الهدف ٢ = VAL بلغه 05-19
    R يُحسب لا يُكتب: |الهدف − الدخول| ÷ |الدخول − الوقف|

كل رقم أعلاه يمرّ على `assert` في `plan()` قبل أن يُرسم.

    python3 run56_stop.py            # يكتب out56/reel56.html
"""
import math, os, sys

from run55_facts import load, vprofile, idx
from run55_kit import FONT_CSS, Panel, num, dnum, svg, t
import run55_page as RP

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out56")
os.makedirs(OUT, exist_ok=True)

SYM, TF = "IWM", "يومي"
NAME = "صندوق الشركات الصغيرة"
RANGE_A, RANGE_Z = "2026-04-09", "2026-05-05"
SL_MARGIN = 0.0015          # هامش فوق قمّة الخروج — لا وقف ملاصق للفتيل

# ═══════════ لوحة الريل ═══════════
NAVY = "#020F1A"
NAVY2 = "#061824"
OFFW = "#F4F1EA"            # Warm off-white
CARD = "#0B1B24"            # بطاقة الشارت الداكنة
EDGE = "#1B3540"
TXD = "#0B2635"             # نص فوق الخلفية الفاتحة
TXL = "#EAF2F5"             # نص داخل الشارت
MUT = "#8FA6AF"
CYAN = "#35C6D8"            # VAH و VAL
AMBER = "#D9A441"           # POC — أمبر هادئ
RED = "#DF7573"             # الوقف وحده
GRN = "#7FBF7E"             # الأهداف وحدها
BULL = "#20939E"
BEAR = "#61808E"


# ═══════════════════ الخطة: تُقاس ولا تُملى ═══════════════════
def plan():
    B = load(SYM)
    a, z = idx(B, RANGE_A), idx(B, RANGE_Z)
    P = vprofile(B[a:z + 1], 40)
    vah, poc, val = P["vah"], P["poc_price"], P["val"]
    assert val < poc < vah, "ترتيب منطقة القيمة غير سليم"

    # «رينج واضح»: آخر ست شمعات من النطاق أغلقت كلّها داخل منطقة القيمة
    assert all(val <= c["c"] <= vah for c in B[z - 5:z + 1]), \
        "النطاق ليس رينجاً واضحاً — الإغلاقات الأخيرة خارج القيمة"

    ex = next((k for k in range(z + 1, z + 9)
               if B[k]["h"] > vah and B[k]["c"] > vah), None)
    assert ex is not None, "لا خروج فوق VAH بعد النطاق"

    rt = next((k for k in range(ex + 1, ex + 4) if val < B[k]["c"] < vah), None)
    assert rt is not None, "لم يُغلق راجعاً داخل منطقة القيمة — لا فشل قبول"

    ex_high = max(B[k]["h"] for k in range(ex, rt + 1))
    ent = B[rt]["c"]
    sl = ex_high * (1 + SL_MARGIN)
    risk = sl - ent
    assert risk > 0, "الوقف تحت الدخول"

    t1 = next((k for k in range(rt + 1, len(B)) if B[k]["l"] <= poc), None)
    assert t1 is not None, "POC لم يُبلَغ"
    assert max(c["h"] for c in B[rt + 1:t1 + 1]) < sl, "الوقف ضُرب قبل POC"
    t2 = next((k for k in range(t1, len(B)) if B[k]["l"] <= val), None)
    assert t2 is not None, "VAL لم يُبلَغ"
    assert max(c["h"] for c in B[rt + 1:t2 + 1]) < sl, "الوقف ضُرب قبل VAL"

    return dict(B=B, a=a, z=z, P=P, vah=vah, poc=poc, val=val, ex=ex, rt=rt,
                ex_high=ex_high, ent=ent, sl=sl, risk=risk, t1=t1, t2=t2,
                r1=(ent - poc) / risk, r2=(ent - val) / risk,
                i0=max(0, a - 2), i1=min(len(B) - 1, t2 + 3))


# ═══════════════════ الشارت: طبقات مفصولة تُشغَّل بالزمن ═══════════════════
def chart(p, W=980, H=820):
    B = p["B"]
    pn = Panel(B, p["i0"], p["i1"], W, H, pad=dict(l=18, r=104, t=26, b=52))
    pn.ext(lo=p["val"], hi=p["sl"]).fin(0.05)

    def gr():
        s = []
        for k in range(6):
            v = pn.LO + (pn.HI - pn.LO) * k / 5
            Y = pn.y(v)
            s.append(f'<line x1="{pn.px0:.1f}" y1="{Y:.1f}" x2="{pn.px1:.1f}" '
                     f'y2="{Y:.1f}" stroke="rgba(255,255,255,0.055)" stroke-width="1"/>')
            s.append(t(pn.px1 + 12, Y + 8, num(v, 2), MUT, 21, 500, "start",
                       rtl=False, halo=CARD))
        return "".join(s)

    def cds():
        """كل شمعة مجموعة مستقلّة — الكشف يتمّ بإظهارها كاملة لا بجزء منها."""
        s = []
        bw = max(4.0, pn.slot * 0.64)
        for i in range(p["i0"], p["i1"] + 1):
            c = B[i]
            col = BULL if c["c"] >= c["o"] else BEAR
            X = pn.x(i)
            s.append(f'<g class="cd" data-i="{i}" opacity="0">'
                     f'<line x1="{X:.1f}" y1="{pn.y(c["h"]):.1f}" x2="{X:.1f}" '
                     f'y2="{pn.y(c["l"]):.1f}" stroke="{col}" stroke-width="2.2"/>'
                     f'<rect x="{X - bw / 2:.1f}" y="{min(pn.y(c["o"]), pn.y(c["c"])):.1f}" '
                     f'width="{bw:.1f}" height="{max(2.0, abs(pn.y(c["c"]) - pn.y(c["o"]))):.1f}" '
                     f'fill="{col}"/></g>')
        return "".join(s)

    def lvl(v, col, tag, dash=None):
        """خطّ المستوى + شريحة سعره في مِزراب المحور يميناً.

        الوسم كان عند الحافة اليسرى، فكانت الكاميرا — وهي تقرّب نحو اليمين —
        تقصّه. والمِزراب يبقى داخل الإطار في كل حركات الكاميرا الثلاث، وهو
        موضع الوسم على المنصّة أصلاً."""
        d = f' stroke-dasharray="{dash}"' if dash else ""
        Y = pn.y(v)
        return (f'<line x1="{pn.px0:.1f}" y1="{Y:.1f}" x2="{pn.px1:.1f}" '
                f'y2="{Y:.1f}" stroke="{col}" stroke-width="2.4"{d}/>'
                + t(pn.px1 - 116, Y - 13, f'{tag} {num(v, 2)}', col, 25, 700,
                    "start", halo=CARD))

    xa, xz = pn.x(p["a"]) - pn.slot * .6, pn.x(p["z"]) + pn.slot * .6
    rng_top = max(c["h"] for c in B[p["a"]:p["z"] + 1])
    rng_bot = min(c["l"] for c in B[p["a"]:p["z"] + 1])

    L = {}
    L["grid"] = gr()
    L["cds"] = cds()
    # نطاق البروفايل: حدوده معلَنة على الصورة لا في الكابشن وحده
    L["range"] = (
        f'<rect x="{xa:.1f}" y="{pn.y(rng_top):.1f}" width="{xz - xa:.1f}" '
        f'height="{pn.y(rng_bot) - pn.y(rng_top):.1f}" fill="#FFFFFF" '
        f'opacity="0.045"/>'
        f'<rect x="{xa:.1f}" y="{pn.y(rng_top):.1f}" width="{xz - xa:.1f}" '
        f'height="{pn.y(rng_bot) - pn.y(rng_top):.1f}" fill="none" '
        f'stroke="{MUT}" stroke-width="1.6" stroke-dasharray="8 6"/>'
        + t((xa + xz) / 2, pn.y(rng_bot) + 34, 'نطاق البروفايل', MUT, 23,
            600, "middle", halo=CARD))
    L["vah"] = lvl(p["vah"], CYAN, "VAH")
    L["poc"] = lvl(p["poc"], AMBER, "POC")
    L["val"] = lvl(p["val"], CYAN, "VAL", "9 6")

    # علامة صغيرة عند قمّة الخروج — لا سهم كبير
    ei = max(range(p["ex"], p["rt"] + 1), key=lambda k: B[k]["h"])
    L["exmark"] = (
        f'<circle cx="{pn.x(ei):.1f}" cy="{pn.y(p["ex_high"]):.1f}" r="9" '
        f'fill="none" stroke="{CYAN}" stroke-width="3"/>'
        + t(pn.x(ei), pn.y(p["ex_high"]) - 34, f'قمّة الخروج {num(p["ex_high"])}',
            CYAN, 23, 700, "middle", halo=CARD))

    # إطار رفيع حول شمعة الإغلاق الفعلية داخل القيمة
    bw = max(4.0, pn.slot * 0.64)
    cr = B[p["rt"]]
    L["rtbox"] = (
        f'<rect x="{pn.x(p["rt"]) - bw:.1f}" y="{pn.y(cr["h"]) - 8:.1f}" '
        f'width="{bw * 2:.1f}" height="{pn.y(cr["l"]) - pn.y(cr["h"]) + 16:.1f}" '
        f'fill="none" stroke="{TXL}" stroke-width="2.2"/>')

    L["dim"] = (f'<rect x="{pn.px0:.1f}" y="{pn.py0:.1f}" '
                f'width="{pn.px1 - pn.px0:.1f}" height="{pn.py1 - pn.py0:.1f}" '
                f'fill="{CARD}" opacity="0.15"/>')

    # طبقة الضوء: شمعتا الخروج والعودة تبقيان بكامل الوضوح فوق التعتيم
    spot = []
    for i in (ei, p["rt"]):
        c = B[i]
        col = BULL if c["c"] >= c["o"] else BEAR
        X = pn.x(i)
        spot.append(f'<line x1="{X:.1f}" y1="{pn.y(c["h"]):.1f}" x2="{X:.1f}" '
                    f'y2="{pn.y(c["l"]):.1f}" stroke="{col}" stroke-width="2.2"/>'
                    f'<rect x="{X - bw / 2:.1f}" y="{min(pn.y(c["o"]), pn.y(c["c"])):.1f}" '
                    f'width="{bw:.1f}" height="{max(2.0, abs(pn.y(c["c"]) - pn.y(c["o"]))):.1f}" '
                    f'fill="{col}"/>')
    L["spot"] = "".join(spot)

    # الدخول: خطّ قصير يربط الليبل بالشمعة نفسها
    xe = pn.x(p["rt"])
    L["entry"] = (
        f'<line x1="{pn.px0:.1f}" y1="{pn.y(p["ent"]):.1f}" x2="{pn.px1:.1f}" '
        f'y2="{pn.y(p["ent"]):.1f}" stroke="{TXL}" stroke-width="2.2"/>'
        f'<line x1="{xe:.1f}" y1="{pn.y(p["ent"]):.1f}" x2="{xe + 30:.1f}" '
        f'y2="{pn.y(p["ent"]) + 40:.1f}" stroke="{TXL}" stroke-width="1.8"/>'
        + t(pn.px0 + 156, pn.y(p["ent"]) + 44, f'الدخول {num(p["ent"])}', TXL,
            24, 700, "end", halo=CARD))

    L["sl"] = (
        f'<rect x="{pn.px0:.1f}" y="{pn.y(p["sl"]):.1f}" '
        f'width="{pn.px1 - pn.px0:.1f}" '
        f'height="{pn.y(p["ex_high"]) - pn.y(p["sl"]):.1f}" fill="{RED}" '
        f'opacity="0.22"/>'
        f'<line x1="{pn.px0:.1f}" y1="{pn.y(p["sl"]):.1f}" x2="{pn.px1:.1f}" '
        f'y2="{pn.y(p["sl"]):.1f}" stroke="{RED}" stroke-width="2.4"/>'
        + t(pn.px0 + 156, pn.y(p["sl"]) - 15, f'الوقف {num(p["sl"])}', RED,
            24, 700, "end", halo=CARD))

    L["t1"] = (f'<circle cx="{pn.x(p["t1"]):.1f}" cy="{pn.y(p["poc"]):.1f}" '
               f'r="10" fill="none" stroke="{GRN}" stroke-width="3"/>')
    L["t2"] = (f'<circle cx="{pn.x(p["t2"]):.1f}" cy="{pn.y(p["val"]):.1f}" '
               f'r="10" fill="none" stroke="{GRN}" stroke-width="3"/>')

    # محور الزمن يظهر مع الشموع المكشوفة فقط
    tm = []
    every = max(1, (p["i1"] - p["i0"]) // 7)
    for i in range(p["i0"], p["i1"] + 1):
        if (i - p["i0"]) % every:
            continue
        X = pn.x(i)
        if pn.px0 + 14 < X < pn.px1 - 14:
            tm.append(f'<g class="tm" data-i="{i}" opacity="0">'
                      + t(X, pn.py1 + 34, dnum(B[i]["d"][5:]), MUT, 21, 500,
                          "middle", rtl=False, halo=CARD) + '</g>')
    L["tm"] = "".join(tm)

    body = (L["grid"] + L["range"] + L["cds"] + L["tm"] +
            f'<g id="gvah" opacity="0">{L["vah"]}</g>'
            f'<g id="gpoc" opacity="0">{L["poc"]}</g>'
            f'<g id="gval" opacity="0">{L["val"]}</g>'
            f'<g id="gdim" opacity="0">{L["dim"]}</g>'
            f'<g id="gspot" opacity="0">{L["spot"]}</g>'
            f'<g id="gex" opacity="0">{L["exmark"]}</g>'
            f'<g id="grt" opacity="0">{L["rtbox"]}</g>'
            f'<g id="gent" opacity="0">{L["entry"]}</g>'
            f'<g id="gsl" opacity="0">{L["sl"]}</g>'
            f'<g id="gt1" opacity="0">{L["t1"]}</g>'
            f'<g id="gt2" opacity="0">{L["t2"]}</g>')
    return svg(W, H, body), pn


# ═══════════════════ الصفحة والزمن ═══════════════════
DUR = 23.5


def hook_chart(p, W=560, H=460):
    """قطعة الهوك: شمعتا الخروج بحجمٍ كبير وخطُّ قمّة الفتيل — بلا سياق.

    شمعتان حقيقيتان بأسعارهما، لا رسمٌ تمثيلي: هذا هو الفتيل الذي يمسح
    الستوب، وعرضُه قريباً هو الهوك نفسه."""
    B = p["B"]
    i0, i1 = p["ex"], p["rt"]
    seg = B[i0:i1 + 1]
    lo = min(c["l"] for c in seg); hi = max(c["h"] for c in seg)
    pad = (hi - lo) * 0.18
    LO, HI = lo - pad, hi + pad
    y = lambda v: H - 74 - (v - LO) / (HI - LO) * (H - 150)
    n = len(seg)
    xs = lambda k: 150 + (k + 0.5) * (W - 300) / n
    bw = (W - 300) / n * 0.5
    s = []
    for k, c in enumerate(seg):
        col = BULL if c["c"] >= c["o"] else BEAR
        X = xs(k)
        s.append(f'<line x1="{X:.1f}" y1="{y(c["h"]):.1f}" x2="{X:.1f}" '
                 f'y2="{y(c["l"]):.1f}" stroke="{col}" stroke-width="4"/>'
                 f'<rect x="{X - bw / 2:.1f}" y="{min(y(c["o"]), y(c["c"])):.1f}" '
                 f'width="{bw:.1f}" '
                 f'height="{max(3.0, abs(y(c["c"]) - y(c["o"]))):.1f}" fill="{col}"/>')
    s.append(f'<line x1="40" y1="{y(p["ex_high"]):.1f}" x2="{W - 40}" '
             f'y2="{y(p["ex_high"]):.1f}" stroke="{RED}" stroke-width="2.4" '
             f'stroke-dasharray="9 7"/>')
    s.append(t(W - 44, y(p["ex_high"]) - 16, f'قمّة الفتيل {num(p["ex_high"])}',
               RED, 26, 700, "start", halo=NAVY))
    return svg(W, H, "".join(s))


def build(p):
    sv, pn = chart(p)
    hv = hook_chart(p)
    B = p["B"]
    # مواضع الكاميرا الثلاثة: نسبة من عرض/ارتفاع الشارت
    def rel(i, v):
        return pn.x(i) / 980.0, pn.y(v) / 820.0
    cx1, cy1 = rel(p["ex"], p["ex_high"])          # منطقة الخروج
    cx2, cy2 = rel(p["rt"], p["ent"])              # شمعة العودة
    cx3, cy3 = rel(p["t1"], p["poc"])              # الأهداف
    cxr = (pn.x(p["a"]) + pn.x(p["z"])) / 2 / 980.0
    cyr = pn.y((max(c["h"] for c in B[p["a"]:p["z"] + 1])
                + min(c["l"] for c in B[p["a"]:p["z"] + 1])) / 2) / 820.0

    r1, r2 = p["r1"], p["r2"]
    js = f"""
const S=(t,a,b)=>Math.max(0,Math.min(1,(t-a)/(b-a)));
const E=x=>x<.5?4*x*x*x:1-Math.pow(-2*x+2,3)/2;
const $=id=>document.getElementById(id);
const CDS=[...document.querySelectorAll('.cd')];
const TMS=[...document.querySelectorAll('.tm')];
const I0={p['i0']}, IZ={p['z']}, IEX={p['ex']}, IRT={p['rt']}, IT1={p['t1']}, IT2={p['t2']}, I1={p['i1']};
// جدول الكشف: الشموع تظهر كاملةً واحدةً بعد الأخرى — لا حركة داخل الشمعة.
function revealTo(t){{
  let n;
  if(t<3.30) n=IZ;                                  // النطاق فقط
  else if(t<6.40) n=IZ;
  else if(t<8.20) n=IZ+Math.round(S(t,6.40,8.05)*(IEX-IZ));
  else if(t<10.20) n=IEX+Math.round(S(t,8.20,9.60)*(IRT-IEX));
  else if(t<15.70) n=IRT;
  else if(t<17.00) n=IRT+Math.round(S(t,15.70,16.95)*(IT1-IRT));
  else if(t<18.20) n=IT1+Math.round(S(t,17.00,18.10)*(IT2-IT1));
  else n=I1;
  return n;
}}
// ثلاث حركات كاميرا فقط، وكلٌّ منها تؤطّر ما هو **مكشوف** في لحظتها.
const CAM=[
 [0.00,1.10,{cxr:.4f},{cyr:.4f}],[3.30,1.10,{cxr:.4f},{cyr:.4f}],
 [6.40,1.12,{cx1:.4f},{cy1:.4f}],[8.20,1.12,{cx1:.4f},{cy1:.4f}],
 [9.30,1.16,{cx2:.4f},{cy2:.4f}],[13.60,1.16,{cx2:.4f},{cy2:.4f}],
 [15.70,1.10,{cx3:.4f},{cy3:.4f}],[18.20,1.10,{cx3:.4f},{cy3:.4f}],
 [19.30,1.00,0.50,0.50],[23.50,1.00,0.50,0.50]];
function cam(t){{
  let a=CAM[0],b=CAM[CAM.length-1];
  for(let i=0;i<CAM.length-1;i++){{if(t>=CAM[i][0]&&t<=CAM[i+1][0]){{a=CAM[i];b=CAM[i+1];break;}}}}
  const u=b[0]===a[0]?0:E(S(t,a[0],b[0]));
  let s=a[1]+(b[1]-a[1])*u, cx=a[2]+(b[2]-a[2])*u, cy=a[3]+(b[3]-a[3])*u;
  // لا حافة تخرج من الإطار: المركز مقيَّد بنصف ما تراه العدسة.
  const h=0.5/s;
  cx=Math.max(h,Math.min(1-h,cx)); cy=Math.max(h,Math.min(1-h,cy));
  return [s,cx,cy];
}}
const TX=[
 ['t1',0.00,0.70],['t2',0.70,1.72],['t3',2.05,3.30],['t4',3.30,4.70],
 ['t5',4.70,6.40],['t6',6.40,8.20],['t7',8.20,10.20],['t8',10.20,11.70],
 ['t9',11.70,13.60],['t10',13.60,15.70],['t11',15.70,18.20],
 ['t12',18.20,20.00],['t13',20.00,23.50]];
window.__DUR={DUR};
window.__setFrame=function(t){{
  // الخلفية: كحلي أول ثانيتين ثم أوف‑وايت
  const sw=E(S(t,1.72,2.02));
  $('navy').style.opacity=(1-sw);
  $('light').style.opacity=sw;
  $('card').style.opacity=E(S(t,1.90,2.35))*(1-E(S(t,19.95,20.35)));
  // لقطة الفتيل القريبة تعيش في الكحلي وحده وتخرج مع تبدّل الخلفية
  $('hook').style.opacity=(1-E(S(t,1.50,1.80)));

  const n=revealTo(t);
  for(const g of CDS){{const i=+g.dataset.i; g.setAttribute('opacity', i<=n?1:0);}}
  for(const g of TMS){{const i=+g.dataset.i; g.setAttribute('opacity', i<=n?1:0);}}

  const [s,cx,cy]=cam(t);
  $('cam').style.transform=`scale(${{s.toFixed(4)}})`;
  $('cam').style.transformOrigin=`${{(cx*100).toFixed(2)}}% ${{(cy*100).toFixed(2)}}%`;

  // الرسم بعد الحدث لا قبله
  $('gvah').setAttribute('opacity', E(S(t,4.80,5.15)));
  $('gpoc').setAttribute('opacity', E(S(t,5.40,5.75)));
  $('gval').setAttribute('opacity', E(S(t,6.00,6.35)));
  $('gex').setAttribute('opacity',  E(S(t,7.55,7.90)));
  $('grt').setAttribute('opacity',  E(S(t,9.40,9.75)));
  const dm=E(S(t,10.20,10.60))*(1-E(S(t,15.40,15.80)));
  $('gdim').setAttribute('opacity', dm);
  $('gspot').setAttribute('opacity', dm>0.02?1:0);
  $('gent').setAttribute('opacity', E(S(t,12.10,12.45)));
  $('gsl').setAttribute('opacity',  E(S(t,13.95,14.35)));
  $('gt1').setAttribute('opacity',  E(S(t,16.95,17.20)));
  $('gt2').setAttribute('opacity',  E(S(t,18.05,18.25)));

  // بطاقتا الهدف: كل واحدة تُفعَّل عند وصول السعر إليها
  const kOff=1-E(S(t,18.30,18.55));
  $('k1').style.opacity=E(S(t,16.95,17.25))*kOff;
  $('k2').style.opacity=E(S(t,18.05,18.30))*kOff;

  for(const [id,a,b] of TX){{
    const o=E(S(t,a,a+0.18))*(1-E(S(t,b-0.16,b)));
    const el=$(id); el.style.opacity=o;
    el.style.transform=`translateY(${{((1-E(S(t,a,a+0.30)))*14).toFixed(2)}}px)`;
  }}
  // ملخّص ثلاث نقاط
  for(let i=0;i<3;i++){{
    $('s'+i).style.opacity=E(S(t,18.45+i*0.28,18.75+i*0.28))*(1-E(S(t,19.84,20.00)));
  }}
}};
window.__setFrame(0);
"""

    def TX(i, main, sub="", cls=""):
        s = f'<div class="sub">{sub}</div>' if sub else ""
        return f'<div class="tx {cls}" id="t{i}"><div class="mn">{main}</div>{s}</div>'

    texts = (
        TX(1, "أقرب ظل يضرب ستوبك.", "", "hook")
        + TX(2, "وين مكانه المنطقي؟", "", "hook")
        + TX(3, "فوق بطلان الفكرة…<br>مو فوق أي ظل.")
        + TX(4, "وهذا المثال فقط<br>داخل رينج واضح.",
             f'{NAME} · {TF}<br>نطاق البروفايل {dnum(RANGE_A[5:])} → '
             f'{dnum(RANGE_Z[5:])} · ⁦{p["z"] - p["a"] + 1}⁩ شمعة')
        + TX(5, "VAH فوق · POC وسط · VAL تحت",
             "سقف القيمة · أكثر سعر تداولاً · قاع القيمة"
             "<br>منطقة القيمة = ⁦70⁩٪ من حجم النطاق")
        + TX(6, "السعر خرج فوق VAH", "")
        + TX(7, "ثم أغلق داخل منطقة القيمة", "إغلاق، لا مجرّد ذيل")
        + TX(8, "هذا فشل قبول…<br>مو اختراق.", "")
        + TX(9, "الدخول بعد تأكيد الرجوع",
             f'إغلاق يومي داخل القيمة عند {num(p["ent"])}')
        + TX(10, "الستوب فوق قمة الخروج",
             f'{num(p["ex_high"])} + هامش ⁦0.15⁩٪ = {num(p["sl"])}')
        + TX(11, "الهدف الأول POC… ثم VAL", "")
        + TX(12, "السياق يحدد الستوب،<br>مو أقرب ظل.", "")
        + TX(13, 'اكتب «ستوب» وخذ قائمة الفحص',
             "احفظها قبل صفقتك الجاية<br>وأرسلها لمتداول يحط الستوب عشوائي",
             "cta")
    )

    cards = (
        f'<div class="kk" id="k1"><b>الهدف ١ — POC</b>'
        f'<span>{num(p["poc"])} · {dnum(B[p["t1"]]["d"][5:])} · '
        f'⁦{r1:.2f}⁩R</span></div>'
        f'<div class="kk" id="k2"><b>الهدف ٢ — VAL</b>'
        f'<span>{num(p["val"])} · {dnum(B[p["t2"]]["d"][5:])} · '
        f'⁦{r2:.2f}⁩R</span></div>')

    summ = ("".join(
        f'<div class="sm" id="s{i}"><i>{i+1}</i>{x}</div>'
        for i, x in enumerate(["رينج واضح", "فشل قبول خارج VAH",
                               "ستوب فوق قمة الخروج"])))

    html = f"""<!DOCTYPE html><html lang="ar" dir="rtl"><head><meta charset="UTF-8">
<style>{FONT_CSS}
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{background:#000}}
#stage{{position:relative;width:1080px;height:1920px;overflow:hidden;
  font-family:'PlexAr',sans-serif;direction:rtl}}
#navy{{position:absolute;inset:0;background:
  radial-gradient(120% 80% at 50% 12%, {NAVY2} 0%, {NAVY} 62%, #01080F 100%)}}
#light{{position:absolute;inset:0;background:{OFFW};opacity:0}}
#brand{{position:absolute;top:104px;left:0;right:0;display:flex;
  flex-direction:column;align-items:center;gap:10px;z-index:9}}
#brand .g{{width:60px;height:60px}}
#brand .w{{font-family:'Inter',sans-serif;font-size:22px;letter-spacing:7px;
  color:{CYAN};font-weight:500}}

#card{{position:absolute;top:552px;left:48px;right:48px;height:936px;
  background:{CARD};border:1.5px solid {EDGE};overflow:hidden;opacity:0;z-index:3}}
#cam{{width:100%;height:100%;will-change:transform}}
#cam svg{{width:100%;height:100%;display:block}}

#hook{{position:absolute;top:1080px;left:0;right:0;display:flex;
  justify-content:center;z-index:7;opacity:0}}
#hook svg{{width:560px;height:460px;display:block}}
.tx{{position:absolute;top:262px;left:70px;right:70px;text-align:center;
  opacity:0;z-index:8}}
.tx .mn{{font-size:72px;font-weight:700;line-height:1.24;color:{TXD};
  letter-spacing:-1px}}
.tx .sub{{margin-top:18px;font-size:31px;font-weight:400;color:#5C6C73;
  line-height:1.5}}
.tx.hook{{top:430px;left:70px;right:70px;text-align:center}}
.tx.hook .mn{{font-size:98px;color:#F7FAFB;line-height:1.22}}
.tx.cta{{top:0;bottom:0;display:flex;flex-direction:column;
  align-items:center;justify-content:center}}
.tx.cta .mn{{font-size:88px;color:{TXD}}}
.tx.cta .sub{{font-size:36px;color:#5C6C73;margin-top:34px;line-height:1.6}}

#kk{{position:absolute;top:1500px;left:60px;right:60px;display:flex;gap:18px;
  z-index:8}}
.kk{{flex:1;background:#E8E3D9;border:1.5px solid #C3D2D4;padding:20px 18px;
  text-align:center;opacity:0}}
.kk b{{display:block;font-size:29px;font-weight:600;color:{TXD}}}
.kk span{{display:block;margin-top:8px;font-size:27px;color:#4E8E4C;
  font-weight:600;font-family:'Inter',sans-serif;direction:ltr}}

#summ{{position:absolute;top:1500px;left:60px;right:60px;display:flex;gap:16px;
  z-index:8}}
.sm{{flex:1;background:#E8E3D9;border:1.5px solid #C3D2D4;padding:22px 12px;
  font-size:28px;font-weight:600;color:{TXD};text-align:center;opacity:0;
  display:flex;flex-direction:column;align-items:center;gap:10px}}
.sm i{{font-family:'Inter',sans-serif;font-style:italic;font-weight:800;
  font-size:25px;color:{OFFW};background:{BULL};width:42px;height:42px;
  display:flex;align-items:center;justify-content:center}}
</style></head><body>
<div id="stage">
  <div id="navy"></div><div id="light"></div>
  <div id="brand"><div class="g">{RP.GEM}</div><div class="w">LIQUIDITY STATE</div></div>
  <div id="hook">{hv}</div>
  <div id="card"><div id="cam">{sv}</div></div>
  <div id="kk">{cards}</div>
  <div id="summ">{summ}</div>
  {texts}
</div>
<script>{js}</script></body></html>"""
    path = os.path.join(OUT, "reel56.html")
    open(path, "w", encoding="utf-8").write(html)
    return path


if __name__ == "__main__":
    p = plan()
    B = p["B"]
    print(f'النافذة: {SYM} {TF} · {B[p["i0"]]["d"]} → {B[p["i1"]]["d"]}')
    print(f'نطاق البروفايل: {RANGE_A} → {RANGE_Z} ({p["z"]-p["a"]+1} شمعة)')
    print(f'VAH {p["vah"]:.2f} · POC {p["poc"]:.2f} · VAL {p["val"]:.2f}')
    print(f'الخروج {B[p["ex"]]["d"]} · قمّة الخروج {p["ex_high"]:.2f}')
    print(f'العودة والدخول {B[p["rt"]]["d"]} عند {p["ent"]:.2f}')
    print(f'الوقف {p["sl"]:.2f} · المخاطرة {p["risk"]:.2f}')
    print(f'الهدف ١ POC {B[p["t1"]]["d"]} = {p["r1"]:.2f}R · '
          f'الهدف ٢ VAL {B[p["t2"]]["d"]} = {p["r2"]:.2f}R')
    print("→", build(p))
