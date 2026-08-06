# -*- coding: utf-8 -*-
"""تشغيلة ٣٢ — ريل «جلسة متداول»: كأن أحدهم فتح المنصّة وجهّز الصفقة بيده.

🔒 أمر فهد 2026-08-06: «اريد الفيديو ان يكون كأنك متداول فتح جارت تريدنق
   فيو و يقوم بتجهيز الست اب لدخول الصفقة» — والثلاثة معاً: واجهة منصّة
   كاملة، ومؤشر فأرة يرسم، وتذكرة أمر تُضغط.

الفرق عن `run31_reel`: هناك الوسوم تنبثق جاهزة، وهنا **تُرسم**. المؤشر
يمسك الأداة من الشريط، يسحب المنطقة فتنمو تحته، يفتح التذكرة، ثم يضغط
«شراء». الكاميرا مجمّدة (`cam=[]`) لأن تسجيل الشاشة لا يتنفّس.

النتيجة أولاً (§7) تُنفَّذ بآلية **موجودة في المحرّك ومعطَّلة في كل الريلات**:
`preview_a/preview_b` مع `openmax`. قبل `preview_b` تكون كل الشموع مكشوفة
وكل الماركب في حالته المكتملة، ثم يتلاشى الكل ويبدأ الريبلاي من الصفر —
أي رجوعٌ حقيقي لا بطاقة نصّية تدّعيه.

كل رقم في التذكرة مشتقّ من الشموع، عدا رأس المال ونسبة المخاطرة —
وهذان **مطبوعان على الشاشة** بوصفهما افتراضاً لا واقعاً.

    python3 run32_desk.py <slug>
"""
import json, os, sys

from reel_build import INK, TEAL, TEAL_D, RED, GREY, htext
from reel_sfx_kit import (build_reel, line_el, zone_drag_el, ring, pos_box,
                          checkmark, set_canvas, set_pad)
import tv_chart
import run31_charts as RC

HERE = os.path.dirname(os.path.abspath(__file__))
CONT = os.path.normpath(os.path.join(HERE, "..", "content"))

# ═══ تخطيط الطرفية: الجارت 996×1300 داخل إطار 1080×1920 ═══
CX, CY = 84, 160                       # ركن الجارت في إحداثيات #stage
CVW, CVH = 996, 1300
set_canvas(CVW, CVH)
set_pad(18, 118, 84, 60)
PL, PR, PT, PB = 18, 118, 84, 60
PW, PH = CVW - PL - PR, CVH - PT - PB
DUR = 22.4                             # سقف skip-rate (§12)
tv_chart.set_theme("light")

# الخانات العشرية وقيمة النقطة لكل أداة (§4 + مواصفات العقود العامة)
DEC = {"GC=F": 1, "NQ=F": 0, "YM=F": 0, "USDJPY=X": 3,
       "AUDUSD=X": 5, "GBPUSD=X": 5, "EURUSD=X": 5}
# قيمة وحدة النقطة للوت الواحد بالدولار: الذهب ١٠٠ أونصة/عقد فـ0.1$ = 10$،
# الناسداك 20$/نقطة، الداو 5$/نقطة، والفوركس لوت قياسي 100k فالبِب = 10$.
POINT_VALUE = {"GC=F": 10.0, "NQ=F": 20.0, "YM=F": 5.0,
               "AUDUSD=X": 10.0, "GBPUSD=X": 10.0, "EURUSD=X": 10.0,
               "USDJPY=X": 9.0}
ACCOUNT, RISK_PCT = 10000.0, 0.01      # افتراض مُعلَن على الشاشة
TF_SECONDS = {"5m": 300, "15m": 900, "30m": 1800, "1h": 3600}
TF_AR = {"5m": "٥د", "15m": "١٥د", "30m": "٣٠د", "1h": "١س"}
TOOLS = ["سهم", "خط", "أفقي", "مربع", "صفقة", "نص"]
TOOL_TOP = [320, 412, 504, 596, 688, 780]


def geo(W):
    lo = min(c["l"] for c in W); hi = max(c["h"] for c in W)
    pad = (hi - lo) * 0.08
    ymin, ymax = lo - pad * 1.7, hi + pad
    slot = PW / len(W)
    return (lambda i: PL + slot * i + slot / 2,
            lambda p: PT + (ymax - p) / (ymax - ymin) * PH, slot)


def plan_numbers(r):
    """أرقام الصفقة من الشموع وحدها — بلا استشراف: المدى حتى شمعة الدخول."""
    W = r["w"]; iob, ir = r["iob"], r["ir"]
    seg = W[:ir + 1]
    rng = max(c["h"] for c in seg) - min(c["l"] for c in seg)
    dp = DEC.get(r["sym"], 2)
    ent = round(W[ir]["c"], dp)
    stp = round(W[iob]["l"] - rng * 0.006, dp)
    tgt = round(ent + (ent - stp) * 2.0, dp)
    pip = RC.PIP.get(r["sym"], 1.0)
    pts = (ent - stp) / pip
    pv = POINT_VALUE.get(r["sym"], 10.0)
    risk_usd = ACCOUNT * RISK_PCT
    lot = risk_usd / max(pts * pv, 1e-9)
    # شمعة بلوغ الهدف: أول شمعة تلامس ٢R بعد الدخول — لا أعلى قمة في
    # النافذة. الأمر يُغلق عند هدفه، فإعلان قمة السوق كلها ربحاً كذب.
    hit = next((j for j in range(ir + 1, len(W)) if W[j]["h"] >= tgt), None)
    assert hit is not None, "السعر لم يبلغ هدف ٢R في هذه النافذة"
    assert stp < ent < tgt, "ترتيب الوقف/الدخول/الهدف غير سليم"
    assert lot >= 0.01, "الحجم المحسوب أصغر من أدنى لوت"
    return dict(ent=ent, stp=stp, tgt=tgt, dp=dp, pts=pts, lot=lot,
                risk=risk_usd, reward=risk_usd * 2, top_i=hit,
                result_pts=int(round(pts * 2)))


# ═══════════ واجهة المنصّة (HTML + CSS) ═══════════
def chrome_html(r, P):
    tfs = "".join(
        f'<span class="tf{" on" if k == r["tf"] else ""}">{v}</span>'
        for k, v in TF_AR.items())
    tools = "".join(
        f'<div class="tb" style="top:{TOOL_TOP[i]}px" id="tb{i}">'
        f'<span class="tglow" id="tg{i}"></span><span class="tl">{t}</span></div>'
        for i, t in enumerate(TOOLS))
    d = P["dp"]
    ticket = f'''<div id="ticket">
  <div class="tkh"><b>أمر شراء</b><span>{r["sym"]} · سوق</span></div>
  <div class="tkg">
    <div class="tkf" id="tf1"><span>السعر</span><b>{P["ent"]:,.{d}f}</b></div>
    <div class="tkf" id="tf2"><span>وقف الخسارة</span><b class="dn">{P["stp"]:,.{d}f}</b></div>
    <div class="tkf" id="tf3"><span>جني الأرباح</span><b class="up">{P["tgt"]:,.{d}f}</b></div>
    <div class="tkf" id="tf4"><span>الحجم</span><b>{P["lot"]:.2f}</b></div>
    <div class="tkf" id="tf5"><span>المخاطرة</span><b class="dn">−{P["risk"]:,.0f}$</b></div>
    <div class="tkf" id="tf6"><span>العائد · ٢R</span><b class="up">+{P["reward"]:,.0f}$</b></div>
  </div>
  <div class="tkb" id="tkbuy">شراء {P["lot"]:.2f}</div>
  <div class="tkn">مثال: حساب 10,000$ · مخاطرة ١٪ — الحجم مشتقّ منهما</div>
</div>'''
    return (f'<div id="topbar"><span class="sym">{r["sym"]}</span>'
            f'<span class="dot"></span><span class="mk">السوق مفتوح</span>'
            f'<span class="cd" id="cdown">--:--</span></div>'
            f'<div id="tfrow">{tfs}</div>'
            f'<div id="tools">{tools}</div>{ticket}')


CHROME_CSS = f"""
#topbar{{position:absolute;top:0;left:0;right:0;height:96px;display:flex;align-items:center;
  gap:16px;padding:0 26px;background:#FBF9F5;border-bottom:1.5px solid rgba(15,46,60,.14);z-index:8}}
#topbar .sym{{font-size:32px;font-weight:900;color:{INK};direction:ltr}}
#topbar .dot{{width:11px;height:11px;border-radius:50%;background:#3FA96A}}
#topbar .mk{{font-size:22px;font-weight:700;color:#6B7C84}}
#topbar .cd{{margin-right:auto;font-size:27px;font-weight:800;color:{TEAL_D};direction:ltr;
  background:rgba(46,125,150,.10);padding:5px 14px;border:1.4px solid rgba(30,98,122,.30)}}
#tfrow{{position:absolute;top:96px;left:0;right:0;height:64px;display:flex;align-items:center;
  gap:10px;padding:0 26px;background:#FBF9F5;border-bottom:1.5px solid rgba(15,46,60,.10);z-index:8}}
#tfrow .tf{{font-size:23px;font-weight:800;color:#8C9BA2;padding:5px 15px;
  border:1.4px solid transparent}}
#tfrow .tf.on{{color:{TEAL_D};background:rgba(46,125,150,.12);border-color:rgba(30,98,122,.34)}}
#tools{{position:absolute;top:0;left:0;width:84px;height:1920px;z-index:9}}
.tb{{position:absolute;left:10px;width:64px;height:76px;border:1.4px solid rgba(15,46,60,.16);
  background:#FBF9F5;display:flex;align-items:center;justify-content:center;overflow:hidden}}
.tb .tl{{font-size:19px;font-weight:800;color:#6B7C84;position:relative;z-index:2}}
.tglow{{position:absolute;inset:0;background:rgba(46,125,150,.30);opacity:0}}
#ticket{{position:absolute;top:1010px;left:84px;width:996px;height:450px;
  padding:24px 30px 26px;
  background:#FBF9F5;border-top:2.5px solid {TEAL_D};box-shadow:0 -20px 46px rgba(15,46,60,.13);
  z-index:10;opacity:0}}
#ticket .tkh{{display:flex;align-items:baseline;gap:14px;margin-bottom:18px}}
#ticket .tkh b{{font-size:30px;font-weight:900;color:{INK}}}
#ticket .tkh span{{font-size:21px;font-weight:700;color:#6B7C84;direction:ltr}}
#ticket .tkg{{display:grid;grid-template-columns:1fr 1fr 1fr;gap:14px 18px}}
.tkf{{border:1.4px solid rgba(15,46,60,.15);padding:10px 14px;opacity:0}}
.tkf span{{display:block;font-size:19px;font-weight:700;color:#6B7C84;margin-bottom:3px}}
.tkf b{{display:block;font-size:31px;font-weight:900;color:{INK};direction:ltr}}
.tkf b.up{{color:{TEAL_D}}} .tkf b.dn{{color:{RED}}}
#ticket .tkb{{margin-top:20px;background:{TEAL_D};color:#FBF9F5;font-size:33px;font-weight:900;
  text-align:center;padding:16px;direction:ltr}}
#ticket .tkn{{margin-top:12px;font-size:19px;font-weight:600;color:#8C9BA2;text-align:center}}
.hl{{top:1486px;left:70px;right:70px}}
.hl b{{display:block;font-size:46px;font-weight:900;line-height:1.16;letter-spacing:-.5px}}
.hl .why{{display:block;margin-top:9px;font-size:27px;font-weight:600;color:#6B7C84}}
#chartclip{{top:{CY}px;left:{CX}px}}
#chip{{display:none}} #res{{display:none}} #endlogo{{display:none}}
#cta{{top:1706px}} #cta .k{{font-size:42px;padding:8px 28px}} #cta .s{{margin-top:7px;font-size:25px}}
#edu{{bottom:26px;font-size:19px;opacity:.55}}
"""

# عدّاد إغلاق الشمعة: العنصر الوحيد «الحي» في الواجهة. يُحدَّث بتغليف
# `window.__setFrame` بعد التحميل — لا يحتاج تعديل المحرّك، والتغليف يقع
# بعد تعريف الدالة لأن `load` يلي تنفيذ سكربت المحرّك.
COUNTDOWN_JS = """<script>
window.addEventListener('load', () => {
  const base = window.__setFrame, TOT = __TOT__, START = __START__;
  const el = document.getElementById('cdown');
  window.__setFrame = t => {
    base(t);
    const left = Math.max(0, START - t);
    const m = Math.floor(left / 60), s = Math.floor(left % 60);
    el.textContent = String(m).padStart(2,'0') + ':' + String(s).padStart(2,'0');
  };
});
</script>"""


def build(slug, win_idx=None):
    import run31_run, run31_build          # خطة النوافذ والصيغ لكل وحدة
    C = run31_build.load(slug)
    r = RC.win(C["window"] if win_idx is None else win_idx)
    W = r["w"]; x, y, slot = geo(W)
    iH, bk, iob, ir = r["iH"], r["bk"], r["iob"], r["ir"]
    P = plan_numbers(r)
    lv = W[iH]["h"]; zt, zb = W[iob]["o"], W[iob]["l"]
    top_i = P["top_i"]
    sx = lambda i: CX + x(i)                 # إحداثيات #stage للمؤشر
    sy = lambda p: CY + y(p)

    ex = [
        line_el(x(iH) - slot * .6, y(lv), x(bk) + slot * .55, y(lv), INK, 2.4, id="bos"),
        f'<g id="boslbl" opacity="0">{htext(x(iH) + slot * 1.9, y(lv) - 16, "كسر الهيكل", INK, 25)}</g>',
        zone_drag_el("zn", x(iob) - slot * .6, y(zt), x(min(ir + 3, len(W) - 1)) + slot * .5,
                     y(zb), htext(x(iob) + slot * 3.2, y(zb) + 32, "منطقة الطلب", TEAL_D, 24)),
        ring("ent", x(ir), y(W[ir]["l"]), 15, TEAL_D, ""),
        pos_box("box", x(ir) - slot * .5, CVW - PR, y(P["ent"]), y(P["stp"]), y(P["tgt"]),
                lbl_e=f'الدخول {P["ent"]:,.{P["dp"]}f}',
                lbl_s=f'الوقف {P["stp"]:,.{P["dp"]}f}',
                lbl_t=f'الهدف ٢R {P["tgt"]:,.{P["dp"]}f}', anchor_e="start", col_e=INK),
        checkmark(x(top_i), y(W[top_i]["h"]) - 40, id="ck"),
    ]

    beats = [
        (0.10, 2.45, f'<b>هذي الصفقة أغلقت +{P["result_pts"]} نقطة</b>'
                     f'<span class="why">خلني أوريك كيف جهّزتها من الصفر</span>'),
        (2.70, 5.90, '<b>أول شي: وين انكسر الهيكل؟</b>'
                     '<span class="why">أحدد القمة اللي سكّر فوقها الجسم</span>'),
        (6.00, 9.30, '<b>المنطقة تنولد من الشمعة اللي قبل الكسر</b>'
                     '<span class="why">أسحبها بالمستطيل من فتيلها لجسمها</span>'),
        (9.40, 12.30, '<b>وأنتظر — ما أطارد</b>'
                      '<span class="why">لأن الدخول الصح من حافة المنطقة لا من وسط الحركة</span>'),
        (12.40, 16.30, '<b>رجع للمنطقة… أفتح التذكرة</b>'
                       '<span class="why">الوقف تحت المنطقة، والهدف ضعف المخاطرة</span>'),
        (16.45, 19.60, '<b>وأضغط شراء</b>'
                       '<span class="why">القرار انبنى قبل الضغطة لا بعدها</span>'),
        (19.70, 21.90, f'<b>الهدف تحقق — +{P["result_pts"]} نقطة</b>'
                       '<span class="why">نفس المنطقة اللي رسمناها بالثانية السادسة</span>'),
    ]
    txt = [(f"t{i+1}", a, b, s, 46, INK) for i, (a, b, s) in enumerate(beats)]

    marks = [
        ("bos", 3.55, 5.35, "draw"), ("boslbl", 5.45, 5.75, "pop"),
        ("zn", 6.60, 8.90, "zonedrag"),
        ("ent", 11.90, 12.35, "ring"),
        ("box", 17.05, 18.60, "posbox"),
        ("ck", 20.30, 20.70, "pop"),
    ]
    full = ["boslbl", "zn", "ent", "box", "ck"]

    # نقرات الأدوات: توهّج الزر عبر dom_marks الموجودة (§الخطة ٢)
    dom = [["tg2", 3.30, 3.50, 3.85, 0.25],      # الخط الأفقي
           ["tg3", 6.10, 6.30, 6.65, 0.25],      # المستطيل
           ["tg4", 12.45, 12.65, 13.00, 0.25],   # أداة الصفقة
           ["ticket", 12.70, 13.10, 17.00, 0.35]]
    for i in range(6):                            # حقول التذكرة تمتلئ تباعاً
        dom.append([f"tf{i+1}", 13.25 + i * 0.42, 13.55 + i * 0.42, 17.00, 0.3])

    # مسار المؤشر — إحداثيات #stage، ورأسه عند رأس ما يُرسَم
    cur = [
        [0.30, 880, 620], [2.70, 880, 620, "creep"],
        [3.20, 42, 542, "ramp"], [3.30, 42, 542, "ss", "down"],
        [3.55, sx(iH) - slot * .6, sy(lv), "ramp"],
        [5.35, sx(bk) + slot * .55, sy(lv), "lin"],
        [6.05, 42, 634, "ramp"], [6.15, 42, 634, "ss", "down"],
        [6.60, sx(iob) - slot * .6, sy(zt), "ramp"],
        [8.90, sx(min(ir + 3, len(W) - 1)) + slot * .5, sy(zb), "lin"],
        [10.20, sx(ir) + slot * 6, sy(zt) - 60, "creep"],
        [12.20, sx(ir), sy(W[ir]["l"]), "creep"],
        [12.40, 42, 726, "whip"], [12.50, 42, 726, "ss", "down"],
        [13.10, 700, 1180, "ramp"],
        [16.55, 560, 1392, "ramp"], [16.90, 560, 1392, "ss", "down"],
        [17.60, 900, 1180, "creep"], [19.40, 940, 700, "creep"],
    ]

    # base صغير ليُرى الريبلاي فعلاً بعد الرجوع، وopenmax=N ليكتمل الجارت
    # في لقطة النتيجة الأولى. الشموع تتكشّف على مرحلتين: حتى الكسر، ثم حتى
    # الدخول، ثم الباقي بعد ضغط «شراء».
    base = max(3, iob - 3)
    n = len(W)
    story = []
    for j in range(base + 1, bk + 3):
        story.append((j, round(3.10 + (j - base - 1) * 0.16, 2)))
    for j in range(bk + 3, ir + 1):
        story.append((j, round(9.50 + (j - bk - 3) * (2.6 / max(1, ir - bk - 2)), 2)))
    for j in range(ir + 1, n):
        story.append((j, round(18.70 + (j - ir - 1) * (2.2 / max(1, n - ir - 1)), 2)))
    tsec = TF_SECONDS.get(r["tf"], 900)
    js = COUNTDOWN_JS.replace("__TOT__", str(tsec)).replace(
        "__START__", f"{tsec * 0.42:.0f}")

    cfg = dict(
        w=W, dark=False, extra_css=CHROME_CSS,
        extra_html=chrome_html(r, P) + js, grid=False,
        pre_svg=tv_chart.furniture(W, dec=P["dp"], sym=r["sym"], tf=r["tf"],
                                   tlabels=[c["d"] for c in W]),
        lp_pill=True, lp_dec=P["dp"], lp_col=tv_chart.T["PILL"],
        lp_txt=tv_chart.T["PILLTX"],
        base=base, openmax=len(W) - 1, open_t=[[len(W) - 1, 0.35]], story=story,
        extra_svg="".join(ex), marks=marks, fullset=full, drawset=["bos"],
        dom_marks=dom, cursor=cur,
        # الرجوع الحقيقي: الجارت كامل بصفقته حتى 2.50 ثم يتلاشى ويُعاد بناؤه
        preview_a=2.50, preview_b=2.95, res_tease=False, sweep_op=0.45,
        txt=txt, chip="", res="",
        cta_k=f'اكتب «{C["car"]["cta"]["keyword"]}»', cta_s="ويصلك الدليل كاملاً",
        edu=f'{r["slug"]} — لغرض تعليمي · مثال حسابي لا توصية',
        dur=DUR, res_t=999, cta_t=DUR - 2.3,
        flash=(2.50, 2.95), flash_op=0.10, punch=(16.90, 17.30, 0.04),
        cam=[],                     # تسجيل الشاشة لا يتنفّس
    )
    out = os.path.join(HERE, f"reel32_{slug}.html")
    n = build_reel(cfg, out)
    print(f'{slug:<10} جلسة متداول {DUR}s · نافذة {r["slug"]}\n'
          f'  الدخول {P["ent"]:,.{P["dp"]}f} · الوقف {P["stp"]:,.{P["dp"]}f} · '
          f'الهدف {P["tgt"]:,.{P["dp"]}f} · {P["pts"]:.0f} نقطة · '
          f'حجم {P["lot"]:.2f} · النتيجة +{P["result_pts"]} نقطة · {n} bytes')
    return out


# مؤثرات §12: مؤثر واحد لكل حدث، والصمت بينها جزء من الإيقاع
SFX = [("success", 0.20, -4), ("whoosh", 2.55, -2), ("pop", 3.32, -5), ("whoosh", 3.60, -5),
       ("pop", 5.50, -4), ("pop", 6.12, -5), ("whoosh", 6.65, -5),
       ("pop", 8.95, -4), ("tick", 10.40, -8), ("tick", 11.60, -8),
       ("pop", 12.47, -5), ("whoosh", 12.75, -6), ("tick", 13.40, -9),
       ("tick", 14.60, -9), ("riser", 15.60, -3), ("impact", 16.92, 0),
       ("tick", 19.20, -8), ("success", 20.90, -2)]

if __name__ == "__main__":
    for s in sys.argv[1:]:
        build(s)
