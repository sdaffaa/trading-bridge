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
from car_common import GEM

THEME = os.environ.get("LS_THEME", "light")
tv_chart.set_theme(THEME)
DK = THEME == "dark"

HERE = os.path.dirname(os.path.abspath(__file__))
CVW, CVH = 1080, 1400
set_canvas(CVW, CVH)
set_pad(18, 122, 92, 66)
DUR = 30.5
PL, PR, PT, PB = 18, 122, 92, 66
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
          htext(x(len(w) - 7), y(L["px"]) - 44,
                f'السعر فوق المتوسط بـ{L["gap"]*100:.2f}٪', TEAL_D, 30)]
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

BASE_CSS = """
.hl{top:118px;left:56px;right:56px;line-height:1.16}
.hl b{display:block;font-size:52px;font-weight:900;line-height:1.14;letter-spacing:-.6px}
.hl .why{display:block;margin-top:10px;font-size:30px;font-weight:600;color:__SUB__}
#chartclip{top:360px;left:0}
#chip{display:none} #endlogo{display:none} #res{display:none}
#cta{top:1792px} #cta .k{font-size:44px;padding:9px 30px} #cta .s{margin-top:8px;font-size:26px}
#edu{bottom:22px;font-size:19px;opacity:.5}
#brand{position:absolute;top:40px;left:0;right:0;text-align:center;z-index:7;opacity:.62}
#brand .g{width:26px;margin:0 auto} #brand .g svg{width:26px;height:auto}
#brand .w{margin-top:3px;font-size:12px;font-weight:800;letter-spacing:6px;color:__SUB__}
""".replace("__SUB__", "#8FA6AF" if DK else "#6B7C84") \
   .replace("__ACC__", "#43D4DC" if DK else "#1E627A")

BASE_HTML = (f'<div id="brand"><div class="g">{GEM}</div>'
             f'<div class="w">LIQUIDITY STATE</div></div>'
             )

# ═════════ الخط الزمني ═════════
# كل مرحلة ≤ ٣ ثوانٍ، وبعد كل واحدة تتغيّر الكاميرا والزوم والماركب.
PH_ = [
    (0.10, 2.90, "<b>القاع الذي انكسر<br>لم يكن كسراً.</b>"),
    (2.95, 6.00, '<b>هنا يبيع أغلبهم</b><span class="why">قاعان متساويان تحتهما أوامر إيقاف</span>'),
    (6.05, 9.20, f'<b>١ · اتجاه صاعد على الأربع ساعات</b><span class="why">{LAY[0]["detail"]}</span>'),
    (9.25, 12.30, f'<b>٢ · انحياز اليوم صاعد</b><span class="why">{LAY[1]["detail"]}</span>'),
    (12.35, 15.55, f'<b>٣ · هيكل استمراري على الساعة</b><span class="why">{LAY[2]["detail"]}</span>'),
    (15.60, 18.95, f'<b>٤ · سحب السيولة</b><span class="why">{LAY[3]["detail"]}</span>'),
    (19.00, 21.95, f'<b>٥ · إشارة الانعكاس</b><span class="why">{LAY[4]["detail"]}</span>'),
    (22.00, 26.15, f'<b>خمسة أسباب اجتمعت</b><span class="why">الدخول {PLAN["ENT"]:,.{DP}f} · الوقف {PLAN["STP"]:,.{DP}f} · المخاطرة {PLAN["R"]:,.{DP}f}</span>'),
    (26.20, 28.75, f'<b>الهدف ٢R عند {PLAN["TGT"]:,.{DP}f}</b><span class="why">تحقق بعد {HIT-FILL} شمعات</span>'),
]

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

cfg = dict(
    w=M5, dark=DK, extra_css=BASE_CSS, extra_html=BASE_HTML,
    grid=False,
    pre_svg=tv_chart.furniture(M5, dec=2, sym=D["sym"], tf=EXEC,
                               tlabels=[c["d"][11:] for c in M5]),
    lp_pill=True, lp_dec=2, lp_col=tv_chart.T["PILL"], lp_txt=tv_chart.T["PILLTX"],
    base=BASE, openmax=len(M5), open_t=[[BASE, 0.45]], story=STORY,
    extra_svg=EX5 + p_4h() + p_1d() + p_1h(),
    marks=MARKS, fullset=FULLSET, drawset=["lvl"],
    dom_marks=[],
    preview_a=0.0, preview_b=0.0, res_tease=False, sweep_op=0.0,
    txt=[(f"t{i+1}", a, b, s, 52, INK) for i, (a, b, s) in enumerate(PH_)],
    chip="", res="", cta_k="اكتب «شامل»", cta_s="ويصلك التحليل كاملاً",
    edu=f'{D["sym"]} · {TF_AR.get(EXEC, EXEC)} · {D["anchor_utc"][:10]} — مثال تعليمي',
    dur=DUR, res_t=999, cta_t=28.9,
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
