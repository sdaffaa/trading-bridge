# -*- coding: utf-8 -*-
"""تشغيلة ٢٨ — ريل تحليل شامل سينمائي: أربعة فريمات، خمسة أسباب، كاميرا حيّة.

🔒 أمر فهد 2026-08-05 (بريف المخرج): هوك يوقف التمرير في أول ٣ ثوانٍ ·
   كشف المشكلة بزوم على مكان الخطأ · شرح بخطوات ≤٣ ثوانٍ · تغيير زاوية
   وزوم بعد كل خطوة · لا ثبات للشاشة أكثر من ثانية · أسلوب استوديو تداول.

الكاميرا لم تعد ثابتة. القاعدة السابقة («الشاشة لا تتجوّل») وُضعت لأن
التكبير كان يقصّ محور السعر — والحل هنا أن المحور يتحرك مع الجارت فيبقى
كل وسم ملاصقاً لسعره، فيصحّ التكبير ولا يكذب الرقم.

الأسباب الخمسة كلها من topdown.py، ولا سطر منها مكتوب بالنظر.
"""
import json, os
from reel_build import INK, TEAL, TEAL_D, RED, GREY, htext, gen
from reel_sfx_kit import (build_reel, line_el, zone_el, xmark, checkmark, pos_box,
                          set_canvas, set_pad, plot_box)
import tv_chart, topdown
import tv_shell as TV
from car_common import GEM

THEME = os.environ.get("LS_THEME", "light")
tv_chart.set_theme(THEME)
DK = THEME == "dark"

HERE = os.path.dirname(os.path.abspath(__file__))
# 🔒 أمر فهد 2026-08-06: «اريد الجارت وكأني داخل تريدنق فيو وأقوم بماركب،
#    وليس كريلز». فاللوحة لم تعد تملأ الإطار: تنكمش لتفسح لعمود الأدوات
#    يساراً وللشريطين العلوي والسفلي — والتخطيط كله في `tv_shell`.
CVW, CVH = 996, 1500
set_canvas(CVW, CVH)
set_pad(18, 118, 84, 60)
DUR = 30.5
PL, PR, PT, PB = 18, 118, 84, 60
CX, CY = TV.CX, TV.CY
PW, PH = CVW - PL - PR, CVH - PT - PB

SET = os.environ.get("LS_SET", "gc_td2_2026-08-04.json")
TAG = SET.replace(".json", "")
D, LAY, PLAN = topdown.build(SET)
DP = PLAN["dp"]                     # منزلة العرض تتبع دقّة الأداة
FILL, HIT = PLAN["fill"], PLAN["hit"]
# النافذة المعروضة يجب أن تبلغ شمعة الهدف. كانت مثبَّتة على ٤٨ شمعة،
# والدخول عند الأربعين — فكل صفقة تحتاج أكثر من ثماني شمعات لتبلغ هدفها
# كانت علامةُ تحقّقها تُرسم خارج حدود الرسم ولا تُرى. صفقة النفط احتاجت
# ثماني عشرة شمعة، والفضة إحدى عشرة.
EXEC = D.get("exec_tf", "5m")        # ٣ دقائق أو ٥ — يُقرأ من الملف
TF_AR = {"3m": "٣ دقائق", "5m": "٥ دقائق", "15m": "١٥ دقيقة"}
M5 = D[EXEC]["w"][:min(len(D[EXEC]["w"]), max(48, HIT + 4))]


def scale_of(w):
    lo = min(c["l"] for c in w); hi = max(c["h"] for c in w)
    pad = (hi - lo) * 0.08
    return lo - pad * 1.7, hi + pad


def geo(w):
    ymin, ymax = scale_of(w)
    slot = PW / len(w)
    return (lambda i: PL + slot * i + slot / 2,
            lambda p: PT + (ymax - p) / (ymax - ymin) * PH, slot, ymin, ymax)


def panel(gid, w, sym, tf, extra="", dec=2):
    """لوحة فريم كاملة داخل مجموعة واحدة: خلفية معتمة + أثاث + شموع + ماركب.

    الخلفية المعتمة ضرورية: اللوحات تتراكب فوق جارت الخمس دقائق، وبلا
    تعتيمها تظهر شموعُه من تحتها فيصير الجارت مشوّشاً."""
    x, y, slot, ymin, ymax = geo(w)
    T = tv_chart.T
    o = [f'<g id="{gid}" opacity="0">',
         f'<rect x="0" y="0" width="{CVW}" height="{CVH}" fill="{T["BG"]}"/>']
    # شبكة + محور سعر
    import math
    st = tv_chart._step(ymax - ymin, 5)
    v = (int(ymin / st) + 1) * st
    while v < ymax:
        yy = y(v)
        o.append(f'<line x1="{PL}" y1="{yy:.1f}" x2="{CVW-PR}" y2="{yy:.1f}" '
                 f'stroke="{T["GRID"]}" stroke-width="1.4"/>')
        o.append(f'<text x="{CVW-PR+9}" y="{yy+6:.1f}" fill="{T["AXTX"]}" font-size="19" '
                 f'font-weight="600" font-family="system-ui,sans-serif" direction="ltr">{v:,.{dec}f}</text>')
        v += st
    o.append(f'<line x1="{CVW-PR}" y1="{PT}" x2="{CVW-PR}" y2="{CVH-PB}" '
             f'stroke="{T["AXBD"]}" stroke-width="1.6"/>')
    o.append(f'<line x1="{PL}" y1="{CVH-PB}" x2="{CVW-PR}" y2="{CVH-PB}" '
             f'stroke="{T["AXBD"]}" stroke-width="1.6"/>')
    # وسم الرمز الباهت
    o.append(f'<text x="{(PL+CVW-PR)/2:.0f}" y="{PT+PH*0.45:.0f}" fill="{T["WMK"]}" '
             f'font-size="120" font-weight="900" text-anchor="middle" '
             f'font-family="system-ui,sans-serif">{tf}</text>')
    # شموع
    bw = slot * 0.6
    BULL, BEAR = ("#43D4DC", "#5E7A88") if DK else ("#2E8CA6", "#122F3E")
    for i, c in enumerate(w):
        cx = x(i); up = c["c"] >= c["o"]; col = BULL if up else BEAR
        top, bot = y(max(c["o"], c["c"])), y(min(c["o"], c["c"]))
        o.append(f'<line x1="{cx:.1f}" y1="{y(c["h"]):.1f}" x2="{cx:.1f}" y2="{y(c["l"]):.1f}" '
                 f'stroke="{col}" stroke-width="2.4"/>'
                 f'<rect x="{cx-bw/2:.1f}" y="{top:.1f}" width="{bw:.1f}" '
                 f'height="{max(bot-top,2.4):.1f}" fill="{col}" rx="1"/>')
    # شريط الرمز والفريم
    o.append(f'<text x="{PL+4}" y="{PT-34}" fill="{T["LEGT"]}" font-size="26" font-weight="800" '
             f'font-family="system-ui,sans-serif" direction="ltr">{sym}  ·  {tf}</text>')
    o.append(extra)
    o.append("</g>")
    return "".join(o)


# ═════════ لوحات الفريمات الأعلى ═════════
def p_4h():
    w = D["4H"]["w"][:D["4H"]["anchor"] + 1][-30:]
    x, y, slot, *_ = geo(w)
    L = LAY[0]
    j = len(w) - 1
    # بعد إلغاء شرط الإغلاقات لم تعد الدوائر الثلاث تصف شيئاً: الطبقة صارت
    # موقعَ السعر من المتوسط، فيُظلَّل ما بينهما ويُقاس الفارق.
    ex = [f'<rect x="{PL}" y="{min(y(L["px"]), y(L["ma"])):.1f}" width="{CVW-PR-PL}" '
          f'height="{abs(y(L["ma"])-y(L["px"])):.1f}" fill="{TEAL}" fill-opacity=".13"/>',
          f'<line x1="{PL}" y1="{y(L["ma"]):.1f}" x2="{CVW-PR}" y2="{y(L["ma"]):.1f}" '
          f'stroke="{TEAL_D}" stroke-width="2" stroke-dasharray="9 7" opacity=".85"/>',
          htext(x(len(w) - 9), y(L["ma"]) + 44, f'متوسط ٢٠ · {L["ma"]:,.{DP}f}', TEAL_D, 28),
          f'<circle cx="{x(j):.1f}" cy="{y(L["px"]):.1f}" r="13" fill="none" '
          f'stroke="{TEAL_D}" stroke-width="3.4"/>',
          # نصّ النسبة انتقل إلى ملاحظة الجارت — وقولها مرّتين حشو
          ]
    return panel("tf4h", w, D["sym"], "4H", "".join(ex))


def p_1d():
    w = D["1D"]["w"][-14:]
    x, y, slot, *_ = geo(w)
    L = LAY[1]
    j = len(w) - 1
    ex = [f'<rect x="{x(j)-slot*.5:.1f}" y="{y(L["pdh"]):.1f}" width="{CVW-PR-x(j)+slot*.5:.1f}" '
          f'height="{y(L["pdl"])-y(L["pdh"]):.1f}" fill="{TEAL}" fill-opacity=".10" '
          f'stroke="{TEAL_D}" stroke-width="1.6" stroke-opacity=".6"/>',
          f'<line x1="{x(j)-slot*.6:.1f}" y1="{y(L["mid"]):.1f}" x2="{CVW-PR}" y2="{y(L["mid"]):.1f}" '
          f'stroke="{TEAL_D}" stroke-width="2.4" stroke-dasharray="8 6"/>',
          htext(x(j) - slot * 4.2, y(L["mid"]) - 16, f'منتصف مدى الأمس {L["mid"]:,.{DP}f}', TEAL_D, 28),
          htext(x(j) - slot * 3.6, y(L["pdl"]) + 34, f'قاع الأمس {L["pdl"]:,.{DP}f} لم يُلمس', RED, 28)]
    return panel("tf1d", w, D["sym"], "1D", "".join(ex))


def p_1h():
    a = D["1h"]["anchor"]
    w = D["1h"]["w"][max(0, a - 22):a + 1]; off = max(0, a - 22)
    x, y, slot, *_ = geo(w)
    L = LAY[2]
    hi, lo = L["hi"] - off, L["lo"] - off
    ex = [f'<line x1="{PL}" y1="{y(w[hi]["h"]):.1f}" x2="{CVW-PR}" y2="{y(w[hi]["h"]):.1f}" '
          f'stroke="{tv_chart.T["LVL"]}" stroke-width="2.2"/>',
          htext(x(6), y(w[hi]["h"]) - 16, f'قمة {w[hi]["h"]:,.{DP}f}', tv_chart.T["LVL"], 28),
          f'<line x1="{PL}" y1="{y(L["prev_lo"]):.1f}" x2="{CVW-PR}" y2="{y(L["prev_lo"]):.1f}" '
          f'stroke="{GREY}" stroke-width="1.8" stroke-dasharray="7 6"/>',
          f'<circle cx="{x(lo):.1f}" cy="{y(w[lo]["l"]):.1f}" r="13" fill="none" '
          f'stroke="{TEAL_D}" stroke-width="3.4"/>',
          htext(x(lo) - slot * 3.4, y(w[lo]["l"]) + 48, f'قاعٌ أعلى {w[lo]["l"]:,.{DP}f}', TEAL_D, 29)]
    return panel("tf1h", w, D["sym"], "1h", "".join(ex))


# ═════════ ماركب الخمس دقائق ═════════
def _clampx(cx, half):
    """يبقي وسماً موسَّطاً داخل اللوحة: نصف عرضه لا يتجاوز أي حافة.

    بلا هذا يُقصّ الرقم عند الحافة كلما وقع الحدث في طرف النافذة —
    والرقم المقصوص أسوأ من الوسم المزاح."""
    return min(max(cx, PL + half), CVW - PR - half)


def m5_svg():
    x, y, slot, *_ = geo(M5)
    R = CVW - PR
    L4, L5 = LAY[3], LAY[4]
    lvl, eq, sw = L4["lvl"], L4["eq"], L4["sw"]
    # ثلاثة وسوم تتزاحم حول قاع واحد: المستوى والذيل والكنس. إزاحاتٌ
    # ثابتة عن كلٍّ لا تكفي — الكنس على النحاس أعمقُ من المستوى بـ0.0005
    # فقط (٠٫٤٪ من المدى) فيقع صفّ الذيل على صفّ المستوى. فتُحسب الصفوف
    # بحدٍّ أدنى بينها: ما يليه لا يقترب منه أقلّ من ٣٤ بكسل.
    YL_ROW = y(lvl) + 34
    Y_WICK = max(y(M5[sw]["l"]) + 30, YL_ROW + 40)
    Y_SWP = Y_WICK + 52
    ex = [line_el(x(min(eq)) - slot, y(lvl), R, y(lvl), tv_chart.T["LVL"], 3.0, id="lvl"),
          # تحت الخطّ لا فوقه: الدوائر مركزها الخطّ نفسه، وقد يبعد الدخول
          # عن المستوى ٢٢ نقطة فقط فلا يتّسع ما بينهما لسطر. وممتدّاً
          # يساراً من أول قاع (الارتساء `start` في العربية هو الحافة
          # اليمنى) فينتهي قبل الدوائر. ولا يُدفع يمين آخر قاع: الكاميرا
          # لا تؤطّر ما لم يتكشّف بعدُ، فوسمٌ هناك يُقصّ.
          f'<g id="lvllbl" opacity="0">'
          f'{htext(max(x(min(eq)) - slot * 1.2, PL + 8 + 400), YL_ROW, f"قيعان متساوية {lvl:,.{DP}f}", tv_chart.T["LVL"], 28, anchor="start")}</g>']
    for n, j in enumerate(eq):
        ex.append(f'<g id="eq{n}" opacity="0"><circle cx="{x(j):.1f}" cy="{y(M5[j]["l"]):.1f}" '
                  f'r="13" fill="none" stroke="{tv_chart.T["LVL"]}" stroke-width="3.6"/></g>')
    ex.append(xmark(x(sw), y(M5[sw]["l"]) + 34, id="swp", r=22))
    # «كَنْس» و«ذيل رفض» و«الوقف» تتزاحم كلها حول قاع شمعة واحدة. تُفرَّق
    # رأسياً وأفقياً: الكنس تحت العلامة يساراً، والذيل بمنتصفه يميناً.
    ex.append(f'<g id="swplbl" opacity="0">{htext(x(sw) - slot * 7.4, Y_SWP, "كَنْس", RED, 32)}</g>')
    # ذيل الرفض: خط رأسي يبرز الذيل نفسه
    c = M5[sw]
    wick_txt = "ذيل رفض " + str(round(L5["wick"] * 100)) + "٪"
    ex.append(f'<g id="wick" opacity="0"><line x1="{x(sw):.1f}" y1="{y(min(c["o"],c["c"])):.1f}" '
              f'x2="{x(sw):.1f}" y2="{y(c["l"]):.1f}" stroke="{RED}" stroke-width="9" '
              f'stroke-linecap="round" opacity=".55"/></g>')
    # منتصف الذيل يقع على ارتفاع مستوى القيعان تقريباً، فكان وسم الذيل
    # يصطدم بوسم «قيعان متساوية» أفقياً. يُنزَل تحت قاع الشمعة: صفٌّ أحمر
    # مستقلّ فوق «كَنْس»، ويبقى ملاصقاً لما يصفه.
    wy = Y_WICK
    # يميناً كان يصطدم بـ«الوقف»: صندوق الصفقة يشغل يمين شمعة الدخول كله.
    # وبلا زوم (تشغيلة ٢٩) يضيق ما تبقّى، فأُبعدت الوسوم إلى يسار الصندوق.
    ex.append(f'<g id="wicklbl" opacity="0">{htext(x(sw) - slot * 7.4, wy, wick_txt, RED, 30)}</g>')
    ex.append(pos_box("box", x(FILL) - slot * .6, R, y(PLAN["ENT"]), y(PLAN["STP"]), y(PLAN["TGT"]),
                      lbl_e=f'الدخول {PLAN["ENT"]:,.{DP}f}', lbl_s=f'الوقف {PLAN["STP"]:,.{DP}f}',
                      lbl_t=f'الهدف ٢R  {PLAN["TGT"]:,.{DP}f}', anchor_e="start",
                      col_e="#ECF3F6" if DK else INK, fs=28))
    t = 13
    ex.append(f'<g id="ex" opacity="0">'
              f'<path d="M {x(FILL)-t*2.2:.1f} {y(PLAN["ENT"])-t:.1f} L {x(FILL)-t*.5:.1f} {y(PLAN["ENT"]):.1f} '
              f'L {x(FILL)-t*2.2:.1f} {y(PLAN["ENT"])+t:.1f} Z" fill="{TEAL_D}"/>'
              f'<circle cx="{x(FILL):.1f}" cy="{y(PLAN["ENT"]):.1f}" r="5.5" fill="{TEAL_D}"/>'
              + htext(x(FILL) - t * 2.6, y(PLAN["ENT"]) - 48, "تنفيذ", TEAL_D, 30, anchor="start") + '</g>')
    ex.append(checkmark(x(HIT), y(PLAN["TGT"]) - 42, id="ck"))
    return "".join(ex), x, y, slot


EX5, X5, Y5, SLOT5 = m5_svg()

# ═════════ الواجهة والملاحظات ═════════
# العنوان العائم ٥٢px والـCTA كانا أكثر ما يجعل المشهد ريلاً — ومهارة
# `tradingview-platform-pov` تسمّيهما بالاسم: «عنصر يطفو فوق المنصّة لا
# يحتويه أي تسجيل شاشة». فالعنوان صار **ملاحظات على الجارت** بجانب ما
# تصفه (قرار فهد)، والـCTA صار **بطاقة ختام بعد انتهاء الجلسة**.
BASE_CSS = TV.SHELL_CSS + TV.FOOT_CSS + TV.NOTE_CSS + """
#edu{display:none}
#cta{inset:0;top:0;left:0;right:0;bottom:0;display:flex;flex-direction:column;
  align-items:center;justify-content:center;gap:22px;background:#F2EEE7;z-index:14}
#cta .k{font-size:60px;padding:16px 46px}
#cta .s{margin-top:4px;font-size:32px}
#cta .egm{width:56px;margin:44px auto 0} #cta .egm svg{width:56px;height:auto}
#cta .ewm{margin-top:10px;font-size:19px;font-weight:800;letter-spacing:8px;color:#6B7C84}
"""

FX = lambda i: CX + X5(i)            # من إحداثيات اللوحة إلى إحداثيات الإطار
FY = lambda p: CY + Y5(p)


def notes():
    """كل سبب ملاحظةٌ عند ما يصفه — لا سطراً فوق الجارت.

    المواضع تتبع مرساها: ملاحظات الفريمات الأعلى في أعلى اللوحة لأن
    لوحاتها تغطّيها كاملةً، وملاحظات الخمس دقائق قرب الشمعة المعنيّة."""
    L4, L5 = LAY[3], LAY[4]
    eqx = FX(sum(L4["eq"]) // len(L4["eq"]))
    sw = L4["sw"]
    top = CY + 26
    XR = CX + CVW - PR - 18      # الحافة اليمنى للوحة
    out = [
        TV.note_el("n0", 0, top, "القاع الذي انكسر لم يكن كسراً",
                   "قاعان متساويان تحتهما أوامر إيقاف",
                   anchor=(eqx, FY(L4["lvl"])), xr=XR),
        TV.note_el("n1", 0, top, "١ · اتجاه صاعد على الأربع ساعات", LAY[0]["detail"], xr=XR),
        TV.note_el("n2", 0, top, "٢ · انحياز اليوم صاعد", LAY[1]["detail"], xr=XR),
        TV.note_el("n3", 0, top, "٣ · هيكل استمراري على الساعة", LAY[2]["detail"], xr=XR),
        TV.note_el("n4", 0, top, "٤ · سحب السيولة", L4["detail"],
                   anchor=(FX(sw), FY(M5[sw]["l"])), xr=XR),
        TV.note_el("n5", 0, top, "٥ · إشارة الانعكاس", L5["detail"],
                   anchor=(FX(sw), FY(M5[sw]["l"])), xr=XR),
        TV.note_el("n6", 0, top, "خمسة أسباب اجتمعت",
                   f'الدخول {PLAN["ENT"]:,.{DP}f} · الوقف {PLAN["STP"]:,.{DP}f} · '
                   f'المخاطرة {PLAN["R"]:,.{DP}f}', xr=XR),
        TV.note_el("n7", 0, top, f'الهدف ٢R عند {PLAN["TGT"]:,.{DP}f}',
                   f'تحقّق بعد {HIT - FILL} شمعات', xr=XR),
    ]
    return "".join(out)


# نوافذ ظهور الملاحظات — نفس إيقاع الأسباب السابق، بلا عنوان عائم
NOTE_T = [(0.55, 5.90), (6.35, 9.10), (9.55, 12.20), (12.65, 15.45),
          (17.30, 18.90), (19.55, 21.90), (22.60, 26.10), (26.60, 29.60)]

# عدّاد إغلاق الشمعة وساعة الجلسة: العنصران «الحيّان» في الواجهة، يجعلان
# اللقطة تسجيلاً لا صورة. يُحدَّثان بتغليف `window.__setFrame` بعد التحميل.
CLOCK_JS = """<script>
window.addEventListener('load', () => {
  const base = window.__setFrame, TOT = __TOT__, H0 = __H0__, M0 = __M0__;
  const cd = document.getElementById('cdown'), fc = document.getElementById('fclock');
  window.__setFrame = t => {
    base(t);
    const left = Math.max(0, TOT * 0.42 - t);
    cd.textContent = String(Math.floor(left / 60)).padStart(2, '0') + ':' +
                     String(Math.floor(left % 60)).padStart(2, '0');
    const sec = Math.floor(t);
    fc.textContent = String(H0).padStart(2, '0') + ':' + String(M0).padStart(2, '0') +
                     ':' + String(sec % 60).padStart(2, '0');
  };
});
</script>"""

_hh, _mm = (M5[FILL]["d"][11:13], M5[FILL]["d"][14:16]) if len(M5[FILL]["d"]) > 15 \
    else (M5[FILL]["d"][:2], M5[FILL]["d"][3:5])
TF_SEC = {"3m": 180, "5m": 300, "15m": 900, "30m": 1800, "1h": 3600}
BASE_HTML = (TV.shell_html(D["sym"], EXEC, foot=f'{D["sym"]} · {TF_AR.get(EXEC, EXEC)} · '
                           f'{D["anchor_utc"][:10]} — مثال تعليمي')
             + notes()
             + CLOCK_JS.replace("__TOT__", str(TF_SEC.get(EXEC, 300)))
                       .replace("__H0__", str(int(_hh))).replace("__M0__", str(int(_mm))))

# تكشّف الشموع: الجارت كامل من الإطار صفر.
#
# 🔒 أمر فهد 2026-08-06: «بدون زومات وهالأمور، فقط ماركب كأنه من الكمبيوتر».
# فحُذفت الكاميرا (١٩ مفتاحاً بزوم يبلغ 3.30×) ومعها `cam_fit` التي كانت
# تمنعها من تأطير ما لم يتكشّف. وبلا كاميرا صار التكشّف التدريجي يترك
# هامشاً يمينياً فارغاً حتى تصل الشموع — فكلّها تُفتح من البداية، وهو ما
# يبدو عليه جارتٌ مفتوح على الكمبيوتر فعلاً. الأنيميشن نصف ثانية يفي
# بقاعدة §12 «فريم-0 شموع تتحرك»، والقصّة يرويها الماركب لا التكشّف.
BASE = len(M5) - 1
STORY = []

MARKS = [
    # بلا زوم تصير الثواني الأولى جارتاً ساكناً مع نصّ — فيُقدَّم أول
    # ماركب إلى داخل الهوك، وهو يصف ما يقوله الهوك نفسه.
    ("lvl", 1.05, 1.85, "draw"),
    ("eq0", 1.90, 2.15, "pop"), ("eq1", 2.05, 2.30, "pop"),
    ("lvllbl", 2.15, 2.45, "pop"),
    ("tf4h", 6.05, 6.45, "fade", 9.00, .32),
    ("tf1d", 9.25, 9.65, "fade", 12.10, .32),
    ("tf1h", 12.35, 12.75, "fade", 15.35, .32),
    ("swp", 17.80, 18.20, "drawx"),
    ("swplbl", 18.20, 18.50, "pop"),
    ("wick", 19.20, 19.60, "fade"), ("wicklbl", 19.65, 19.95, "pop"),
    ("ex", 22.05, 22.45, "pop"),
    ("box", 22.25, 24.10, "posbox"),
    ("ck", 26.80, 27.15, "pop"),
]
FULLSET = ["eq0", "eq1", "lvllbl", "tf4h", "tf1d", "tf1h", "swp", "swplbl",
           "wick", "wicklbl", "ex", "box", "ck"]

# ═════════ تشغيل الجلسة: النقرة قبل الرسم دائماً ═════════
# قاعدة `tradingview-platform-pov`: «أداة رسم تظهر بلا نقرة في الشريط
# اليساري» عيبٌ يكسر الإيهام. فكل حدث هنا له سببه المرئي.
CUR, DOM = [[0.20, 700, 980]], []


def _do(pair):
    c, d = pair
    CUR.extend(c); DOM.append(d)


_do(TV.click_tool(TV.HLINE, 0.62, until=2.45))            # أداة الخط الأفقي
CUR += TV.draw_path(1.05, 1.85, FX(min(LAY[3]["eq"])) - SLOT5,
                    FY(LAY[3]["lvl"]), CX + CVW - PR, FY(LAY[3]["lvl"]))
CUR += [[2.35, FX(LAY[3]["eq"][0]), FY(M5[LAY[3]["eq"][0]]["l"]) + 40, "creep"]]
for i, (tf, t) in enumerate((("4H", 5.85), ("1D", 9.05), ("1h", 12.15), (EXEC, 15.40))):
    _do(TV.click_tf(tf, t))
    CUR += [[t + 0.9, 690, 620 + i * 40, "creep"]]        # يقرأ اللوحة
CUR += [[17.60, FX(LAY[3]["sw"]), FY(M5[LAY[3]["sw"]]["l"]) + 30, "ramp"],
        [19.10, FX(LAY[3]["sw"]) - SLOT5 * 1.4, FY(M5[LAY[3]["sw"]]["c"]), "creep"]]
_do(TV.click_tool(TV.TRADE, 21.95, until=24.20))          # أداة الصفقة
CUR += TV.draw_path(22.25, 24.10, FX(FILL), FY(PLAN["ENT"]),
                    FX(FILL) + 120, FY(PLAN["TGT"]))
CUR += [[26.40, FX(HIT), FY(PLAN["TGT"]) - 46, "creep"],
        [28.60, 760, 900, "creep"]]
# الفريم المختار: قرص واحد مضيء في كل لحظة — يُطفأ الخمس دقائق عند التبديل
# ويُعاد عند العودة، فالحالة تتبع النقرة لا تسبقها.
_TFI = {k: i for i, k in enumerate(TV.TF_ORDER)}
_E = _TFI.get(EXEC, 0)
DOM += [[f'tfo{_E}', 0.0, 0.05, 5.85, 0.15],
        [f'tfo{_TFI["4H"]}', 5.85, 6.00, 9.05, 0.15],
        [f'tfo{_TFI["1D"]}', 9.05, 9.20, 12.15, 0.15],
        [f'tfo{_TFI["1h"]}', 12.15, 12.30, 15.40, 0.15],
        [f'tfq{_E}', 15.40, 15.55, 0, 0]]      # القرص الاحتياطي عند العودة
# الملاحظات وخيوطها تظهر وتختفي بنافذة كل سبب
for i, (a, b) in enumerate(NOTE_T):
    DOM.append([f"n{i}", a, a + 0.32, b, 0.28])
    DOM.append([f"n{i}l", a + 0.10, a + 0.40, b, 0.28])

cfg = dict(
    w=M5, dark=DK, extra_css=BASE_CSS, extra_html=BASE_HTML,
    grid=False,
    pre_svg=tv_chart.furniture(M5, dec=2, sym=D["sym"], tf=EXEC,
                               tlabels=[c["d"][11:] for c in M5]),
    lp_pill=True, lp_dec=2, lp_col=tv_chart.T["PILL"], lp_txt=tv_chart.T["PILLTX"],
    base=BASE, openmax=len(M5), open_t=[[BASE, 0.45]], story=STORY,
    extra_svg=EX5 + p_4h() + p_1d() + p_1h(),
    marks=MARKS, fullset=FULLSET, drawset=["lvl"],
    dom_marks=DOM, cursor=CUR, crosshair=True, chart_at=(CX, CY),
    tlabels=[c["d"][11:] for c in M5],
    preview_a=0.0, preview_b=0.0, res_tease=False, sweep_op=0.0,
    txt=[],                       # لا عنوان عائم — الملاحظات على الجارت
    chip="", res="", cta_k="اكتب «شامل»",
    cta_s=f'ويصلك التحليل كاملاً<div class="egm">{GEM}</div>'
          f'<div class="ewm">LIQUIDITY STATE</div>',
    edu=f'{D["sym"]} · {TF_AR.get(EXEC, EXEC)} · {D["anchor_utc"][:10]} — مثال تعليمي',
    dur=DUR, res_t=999, cta_t=DUR - 2.4,
    # لا وميض ولا نبضة: الشاشة لا تومض. (الفرع الثابت في المحرّك يتجاهل
    # النبضة والاهتزاز أصلاً، والإطفاء هنا تصريحٌ لا تكرار.)
    flash=(0.0, 0.0), flash_op=0.0, punch=(0.0, 0.0, 0.0),
    cam=[],                       # أمر فهد: بدون زومات — ماركب فقط
)

if __name__ == "__main__":
    n = build_reel(cfg, os.path.join(HERE, f"reel28_{TAG}_{THEME}.html"))
    print(f'{TAG} | ريل شامل ثابت | {DUR}s | {len(LAY)} أسباب | '
          f'ماركب {len(MARKS)} | شموع {len(M5)} كلها مفتوحة | {n} bytes')
    for i, L in enumerate(LAY, 1):
        print(f'  {i} [{L["tf"]:>3}] {L["title"]}')
