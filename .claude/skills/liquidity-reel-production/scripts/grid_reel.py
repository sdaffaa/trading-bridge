# -*- coding: utf-8 -*-
"""ريل «ورقة الغش» — شبكة 2×3 تُبنى تباعاً (فكرة مطلوبة من فهد 2026-08-04).
الموضوع: ست مناطق على الجارت وماذا تفعل عند كل واحدة.
عقد التشغيل نفسه: #stage / window.__DUR / window.__setFrame(t) — يعمل مع reel_render_any.py
"""
import json, os
from reel_build import INK, TEAL, TEAL_D, TEAL_L, BULL, BEAR, RED, GREY, MUTE, CARDBD, FONT_CSS, htext, GEM

HERE = os.path.dirname(os.path.abspath(__file__))

# ───────── هندسة الشبكة ─────────
SW, SH = 1080, 1920
COLS, ROWS = 2, 3
MX, TOP = 52, 428          # هامش جانبي وبداية الشبكة
GAP_X, GAP_Y = 34, 100
CW_ = (SW - MX * 2 - GAP_X) // COLS       # عرض الخانة
CH_ = 300                                  # ارتفاع الخانة

def cell_xy(i):
    r, c = divmod(i, COLS)
    return MX + c * (CW_ + GAP_X), TOP + r * (CH_ + GAP_Y)

# ───────── رسومات مصغّرة داخل الخانات ─────────
def cnd(cx, o, c, h, l, w=26, col=None):
    up = c <= o                      # إحداثيات الشاشة: y الأصغر = سعر أعلى
    color = col or (BULL if up else BEAR)
    top, bot = min(o, c), max(o, c)
    return (f'<line x1="{cx}" y1="{h}" x2="{cx}" y2="{l}" stroke="{color}" stroke-width="2.4"/>'
            f'<rect x="{cx-w/2}" y="{top}" width="{w}" height="{max(bot-top,3)}" fill="{color}" rx="1"/>')

def band(x0, y0, x1, y1, col=TEAL, stroke=TEAL_D, op=0.16, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ''
    return (f'<rect x="{x0}" y="{y0}" width="{x1-x0}" height="{y1-y0}" fill="{col}" opacity="{op}"/>'
            f'<rect x="{x0}" y="{y0}" width="{x1-x0}" height="{y1-y0}" fill="none" stroke="{stroke}" '
            f'stroke-width="1.4"{d}/>')

def hline(x0, x1, y, col=INK, w=1.8, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<line x1="{x0}" y1="{y}" x2="{x1}" y2="{y}" stroke="{col}" stroke-width="{w}"{d}/>'

def arrow(x0, y0, x1, y1, col, w=3.4):
    import math
    ang = math.atan2(y1 - y0, x1 - x0)
    a1 = (x1 - 15 * math.cos(ang - 0.42), y1 - 15 * math.sin(ang - 0.42))
    a2 = (x1 - 15 * math.cos(ang + 0.42), y1 - 15 * math.sin(ang + 0.42))
    return (f'<line x1="{x0:.0f}" y1="{y0:.0f}" x2="{x1:.0f}" y2="{y1:.0f}" stroke="{col}" '
            f'stroke-width="{w}" stroke-linecap="round"/>'
            f'<polygon points="{x1:.0f},{y1:.0f} {a1[0]:.0f},{a1[1]:.0f} {a2[0]:.0f},{a2[1]:.0f}" fill="{col}"/>')

# كل خانة: (المفتاح، العنوان، دالة الرسم، الحكم، لون الحكم، دالة سهم الحكم)
def art_fvg(X, Y):
    s = [band(X + 52, Y + 148, X + 254, Y + 196)]
    s.append(cnd(X + 96, Y + 168, Y + 214, Y + 150, Y + 232, w=30))
    s.append(cnd(X + 156, Y + 214, Y + 108, Y + 96, Y + 224, w=30))
    s.append(cnd(X + 216, Y + 100, Y + 132, Y + 88, Y + 146, w=30))
    s.append(htext(X + 74, Y + 178, "FVG", TEAL_D, 20))
    return "".join(s)

def art_ob(X, Y):
    s = [cnd(X + 72, Y + 150, Y + 186, Y + 138, Y + 200, col=BEAR)]
    s.append(band(X + 56, Y + 148, X + 250, Y + 188, dash="4 4"))
    for k, (cx, o, c) in enumerate(((142, 148, 108), (192, 108, 78), (238, 78, 60))):
        s.append(cnd(X + cx, Y + o, Y + c, Y + c - 12, Y + o + 12))
    return "".join(s)

def art_breaker(X, Y):
    s = [band(X + 56, Y + 96, X + 250, Y + 136, col=RED, stroke=RED, op=0.13)]
    s.append(cnd(X + 78, Y + 100, Y + 134, Y + 92, Y + 146, col=BEAR))
    for k, (cx, o, c) in enumerate(((132, 134, 176), (176, 176, 206), (220, 206, 232))):
        s.append(cnd(X + cx, Y + o, Y + c, Y + o - 8, Y + c + 10, col=BEAR))
    s.append(htext(X + 200, Y + 122, "انقلبت", RED, 17))
    return "".join(s)

def art_eqh(X, Y):
    s = [hline(X + 46, X + 258, Y + 138, INK, 2.2)]
    for cx, o, c in ((92, 208, 162), (152, 200, 158), (216, 212, 166)):
        s.append(cnd(X + cx, Y + o, Y + c, Y + 138, Y + o + 22, w=30))
    for k in range(3):
        yy = Y + 126 - k * 11
        s.append(f'<line x1="{X+56}" y1="{yy}" x2="{X+250}" y2="{yy}" stroke="{RED}" '
                 f'stroke-width="3" stroke-dasharray="10 8" opacity="{0.9-k*0.2:.2f}"/>')
    s.append(htext(X + 152, Y + 240, "أوامر وقف فوقها", RED, 18))
    return "".join(s)

def art_eq(X, Y):
    s = [band(X + 46, Y + 152, X + 258, Y + 240, op=0.13)]
    s.append(hline(X + 46, X + 258, Y + 64, INK, 2.2))
    s.append(hline(X + 46, X + 258, Y + 240, INK, 2.2))
    s.append(hline(X + 46, X + 258, Y + 152, TEAL_D, 2.4, dash="7 6"))
    for cx, o, c in ((92, 210, 176), (146, 176, 128), (206, 128, 96)):
        s.append(cnd(X + cx, Y + o, Y + c, Y + c - 14, Y + o + 14, w=26))
    s.append(htext(X + 84, Y + 142, "50%", TEAL_D, 19))
    s.append(htext(X + 92, Y + 232, "الرخيص", TEAL_D, 18))
    s.append(htext(X + 92, Y + 84, "الغالي", GREY, 18))
    return "".join(s)

def art_sweep(X, Y):
    s = [hline(X + 46, X + 258, Y + 196, INK, 2.2, dash="6 5")]
    for cx, o, c in ((84, 118, 156), (134, 156, 182)):
        s.append(cnd(X + cx, Y + o, Y + c, Y + o - 12, Y + c + 14, col=BEAR, w=28))
    s.append(cnd(X + 184, Y + 182, Y + 146, Y + 138, Y + 242, col=BULL, w=28))
    s.append(cnd(X + 232, Y + 146, Y + 92, Y + 82, Y + 154, col=BULL, w=28))
    s.append(htext(X + 96, Y + 236, "سحب تحت القاع", RED, 18))
    return "".join(s)

CELLS = [
    ("fvg",     "الفجوة السعرية (FVG)", art_fvg,     "انتظر العودة", TEAL_D,
     lambda X, Y: arrow(X + 230, Y + 214, X + 150, Y + 158, TEAL_D)),
    ("ob",      "أوردر بلوك",           art_ob,      "شراء من المنطقة", TEAL_D,
     lambda X, Y: arrow(X + 80, Y + 200, X + 236, Y + 74, TEAL_D)),
    ("breaker", "بريكر بلوك",           art_breaker, "بيع من المنطقة", RED,
     lambda X, Y: arrow(X + 84, Y + 96, X + 238, Y + 226, RED)),
    ("eqh",     "قمم متساوية",          art_eqh,     "سيولة… لا هدف", RED,
     lambda X, Y: arrow(X + 246, Y + 74, X + 176, Y + 118, RED)),
    ("eq",      "منتصف المدى",          art_eq,      "اشترِ تحت النصف", TEAL_D,
     lambda X, Y: arrow(X + 244, Y + 108, X + 176, Y + 196, TEAL_D)),
    ("sweep",   "سحب السيولة",          art_sweep,   "ادخل بعد السحب", TEAL_D,
     lambda X, Y: arrow(X + 84, Y + 214, X + 232, Y + 104, TEAL_D)),
]

def build(out_html="reel_grid.html"):
    frames, arts, verds, labels = [], [], [], []
    for i, (key, title, art, verdict, vcol, varrow) in enumerate(CELLS):
        X, Y = cell_xy(i)
        frames.append(f'<g id="fr{i}" opacity="0">'
                      f'<rect x="{X}" y="{Y}" width="{CW_}" height="{CH_}" fill="#FBF9F5" '
                      f'stroke="{CARDBD}" stroke-width="2"/></g>')
        labels.append(f'<g id="lb{i}" opacity="0">{htext(X + CW_/2, Y + CH_ + 42, title, INK, 27)}</g>')
        arts.append(f'<g id="ar{i}" opacity="0">{art(X, Y)}</g>')
        verds.append(f'<g id="vd{i}" opacity="0">{varrow(X, Y)}'
                     f'<rect x="{X+14}" y="{Y+14}" width="{len(verdict)*15+30}" height="42" '
                     f'fill="{"#EAF3F5" if vcol == TEAL_D else "#F8ECEC"}" stroke="{vcol}" stroke-width="1.6"/>'
                     + htext(X + 14 + (len(verdict)*15+30)/2, Y + 44, verdict, vcol, 24) + '</g>')

    # جداول التوقيت: [id, بداية, نهاية, نمط]
    marks = []
    for i in range(6):
        a = 2.75 + i * 0.22
        marks += [[f"fr{i}", a, a + 0.28, "pop"], [f"lb{i}", a + 0.12, a + 0.4, "fade"]]
    for i in range(6):
        a = 5.2 + i * 0.95
        marks.append([f"ar{i}", a, a + 0.55, "grow"])
    for i in range(6):
        a = 11.6 + i * 1.15
        marks.append([f"vd{i}", a, a + 0.42, "pop"])

    CTA_T, DUR = 19.6, 24.4
    SVG = ("".join(frames) + "".join(labels) + "".join(arts) + "".join(verds))

    html = f'''<!DOCTYPE html><html lang="ar" dir="rtl"><head><meta charset="utf-8"><style>
{FONT_CSS}
*{{margin:0;padding:0;box-sizing:border-box}}
#stage{{width:{SW}px;height:{SH}px;position:relative;overflow:hidden;font-family:Tajawal;
  background:radial-gradient(120% 90% at 50% 0%, #F7F3EC 0%, #F2EEE7 55%, #ECE6DB 100%)}}
#hd{{position:absolute;top:140px;left:40px;right:40px;text-align:center;opacity:0}}
#hd h1{{font-size:62px;font-weight:900;color:{INK};line-height:1.16;letter-spacing:-1px}}
#hd p{{margin-top:14px;font-size:31px;font-weight:600;color:{GREY}}}
#grid{{position:absolute;inset:0;transform-origin:540px 960px}}
#res{{position:absolute;top:1612px;left:40px;right:40px;text-align:center;font-size:46px;
  font-weight:900;color:{TEAL_D};opacity:0}}
#cta{{position:absolute;top:1694px;left:70px;right:70px;text-align:center;opacity:0}}
#cta .k{{display:inline-block;border:2.5px solid {INK};color:{INK};font-weight:900;font-size:52px;padding:12px 40px}}
#cta .s{{margin-top:14px;font-size:31px;font-weight:700;color:{GREY}}}
#edu{{position:absolute;bottom:44px;left:0;right:0;text-align:center;font-size:22px;color:#93A2A8;font-weight:600}}
#flash{{position:absolute;inset:0;background:#fff;opacity:0;pointer-events:none}}
#intro{{position:absolute;inset:0;z-index:5;display:flex;flex-direction:column;align-items:center;
  justify-content:center;gap:22px;background:radial-gradient(120% 90% at 50% 0%, #0C2029 0%, #08131C 55%, #04090F 100%)}}
#intro .ig{{width:112px}} #intro .ig svg{{width:112px;height:auto}}
#intro .iwm{{font-size:24px;font-weight:800;letter-spacing:10px;color:#B8C8CC}}
#intro .ieyeb{{margin-top:22px;font-size:29px;font-weight:700;color:#43D4DC}}
#intro .ihook{{font-size:72px;font-weight:900;color:#EDF4F5;text-align:center;line-height:1.26;padding:0 60px;opacity:0}}
#intro .ibar{{width:320px;height:3px;background:linear-gradient(90deg,transparent,#43D4DC,transparent)}}
#intro .isub{{font-size:32px;font-weight:700;color:#B8C8CC;opacity:0;padding:0 60px;text-align:center}}
#isweep{{position:absolute;top:0;bottom:0;left:0;width:340px;z-index:6;opacity:0;pointer-events:none;
  background:linear-gradient(100deg,transparent 0%,rgba(255,255,255,0.85) 45%,rgba(67,212,220,0.3) 55%,transparent 100%);
  transform:skewX(-12deg)}}
</style></head><body><div id="stage">
<div id="hd"><h1>ست مناطق على الجارت</h1><p>وماذا تفعل عند كل واحدة</p></div>
<svg id="grid" viewBox="0 0 {SW} {SH}" width="{SW}" height="{SH}" xmlns="http://www.w3.org/2000/svg">{SVG}</svg>
<div id="res">احفظها… ستحتاجها في كل جلسة</div>
<div id="cta"><span class="k">اكتب «مناطق»</span><div class="s">ليصلك الدليل الكامل — ست مناطق بشروطها</div></div>
<div id="edu">لغرض تعليمي — أمثلة تخطيطية</div>
<div id="flash"></div>
<div id="intro"><div class="ig">{GEM}</div><div class="iwm">LIQUIDITY STATE</div>
  <div class="ieyeb">ورقة الجارت السريعة</div>
  <div class="ihook" id="ihook">ست مناطق…<br>وقرار واحد لكلٍّ منها</div>
  <div class="ibar"></div>
  <div class="isub" id="isub">احفظها قبل جلسة الغد</div></div>
<div id="isweep"></div>
</div>
<script>
window.__DUR = {DUR};
const $ = id => document.getElementById(id);
const clamp=(v,a,b)=>Math.max(a,Math.min(b,v));
const seg=(t,a,b)=>clamp((t-a)/(b-a),0,1);
const oc=t=>1-Math.pow(1-t,3);
const ob=t=>{{const c1=1.70158,c3=c1+1;return 1+c3*Math.pow(t-1,3)+c1*Math.pow(t-1,2);}};
const MARKS = {json.dumps(marks)};
const CTA_T = {CTA_T};
window.__setFrame = function(t) {{
  // الافتتاحية الداكنة ثم المسحة الضوئية
  const iw = seg(t, 2.5, 3.05), intro = $("intro");
  if (iw >= 1) intro.style.display = "none";
  else {{ intro.style.display=""; intro.style.clipPath = `inset(0 0 0 ${{(iw*100).toFixed(2)}}%)`; }}
  const ihk = oc(seg(t, 0.2, 0.75));
  $("ihook").style.opacity = ihk;
  $("ihook").style.transform = `translateY(${{((1-ihk)*26).toFixed(1)}}px)`;
  $("isub").style.opacity = oc(seg(t, 0.65, 1.1));
  const iswk = seg(t, 2.45, 3.12), isw = $("isweep");
  if (iswk>0 && iswk<1) {{ isw.style.opacity = 0.7*Math.sin(Math.PI*iswk);
    isw.style.transform = `translateX(${{(-360+1560*iswk).toFixed(0)}}px) skewX(-12deg)`; }}
  else isw.style.opacity = 0;
  // العنوان
  const hk = oc(seg(t, 2.6, 3.1));
  $("hd").style.opacity = hk * (1 - seg(t, CTA_T-0.6, CTA_T));
  $("hd").style.transform = `translateY(${{((1-hk)*18).toFixed(1)}}px)`;
  // عناصر الشبكة
  for (const [id,a,b,mode] of MARKS) {{
    const el = $(id); const k = seg(t,a,b);
    if (mode === "pop") {{
      el.style.opacity = oc(k);
      el.style.transformBox="fill-box"; el.style.transformOrigin="50% 50%";
      el.style.transform = `scale(${{(0.72+0.28*ob(k)).toFixed(4)}})`;
    }} else if (mode === "grow") {{
      el.style.opacity = Math.min(oc(k*1.6),1);
      el.style.transformBox="fill-box"; el.style.transformOrigin="50% 100%";
      el.style.transform = `scaleY(${{(0.25+0.75*oc(k)).toFixed(4)}})`;
    }} else {{ el.style.opacity = oc(k); }}
  }}
  // نبضة إضاءة على الخانة لحظة صدور حكمها
  for (let i=0;i<6;i++) {{
    const a = 11.6 + i*1.15;
    const p = seg(t, a, a+0.5);
    const fr = $("fr"+i).querySelector("rect");
    if (p>0 && p<1) {{ fr.setAttribute("stroke", "{TEAL}"); fr.setAttribute("stroke-width", (2+2.4*Math.sin(Math.PI*p)).toFixed(2)); }}
    else if (p>=1) {{ fr.setAttribute("stroke", "{CARDBD}"); fr.setAttribute("stroke-width", 2); }}
  }}
  // تنفّس مجهري للشبكة + انكماش خفيف عند الخلاصة
  const br = 1 + 0.0035*Math.sin(t*0.7);
  const shrink = 1 - 0.045*seg(t, CTA_T-1.0, CTA_T+0.4);
  $("grid").style.transform = `scale(${{(br*shrink).toFixed(4)}})`;
  // الخلاصة والدعوة
  $("res").style.opacity = oc(seg(t, 18.4, 18.9)) * (1 - seg(t, CTA_T-0.2, CTA_T+0.2));
  const ck = oc(seg(t, CTA_T, CTA_T+0.45));
  $("cta").style.opacity = ck;
  $("cta").style.transform = `translateY(${{((1-ck)*26).toFixed(1)}}px) scale(${{(1+0.02*Math.sin(2*Math.PI*(t-CTA_T)*0.75)).toFixed(4)}})`;
  const f1 = seg(t, 18.4, 18.55), f2 = seg(t, 18.55, 18.95);
  $("flash").style.opacity = f1>0 && f2<1 ? 0.32*(f1<1?f1:(1-f2)) : 0;
}};
window.__setFrame(0);
</script></body></html>'''
    p = os.path.join(HERE, out_html)
    open(p, "w", encoding="utf-8").write(html)
    print("grid reel:", len(html), "| DUR", DUR, "| CTA", CTA_T)
    return DUR, CTA_T

if __name__ == "__main__":
    build()
