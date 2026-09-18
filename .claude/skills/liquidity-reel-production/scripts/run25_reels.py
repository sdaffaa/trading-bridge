# -*- coding: utf-8 -*-
"""تشغيلة 25 — ثلاثة ريلات تحليل فني: كيف تدخل الصفقة بثلاثة نماذج مختلفة.

🔒 أمر فهد 2026-08-05:
   • مدة كل ريل ≤ ٢٠ ثانية.
   • الجارت ٧٠–٨٠٪ من مساحة الريل: لوحة 1080×1400 من 1920 = ٧٢٫٩٪.
   • بلا قالب حول الجارت — لا بطاقة ولا حد ولا شريحة، الشموع على الخلفية مباشرة.
     (chartwrap في المحرك بلا خلفية أصلاً؛ ما يُلغى هنا هو زخرفة القالب:
      chip والملخص واللوغو الختامي والوميض والكنس البصري.)

النماذج الثلاثة تختلف في **موضع الوقف وما يُبطل الصفقة**، لا في الشكل فقط:
   ١ كنس وإغلاق  — الوقف تحت أدنى نقطة الكنس
   ٢ منتصف الفجوة — الوقف تحت قاع الفجوة
   ٣ كسر وعودة   — الوقف تحت منطقة النشأة
"""
import os
from reel_build import INK, TEAL, TEAL_D, RED, GREY, MUTE, htext, gen
from reel_sfx_kit import build_reel, geom, line_el, zone_el, xmark, checkmark, set_canvas
from car_common import GEM

HERE = os.path.dirname(os.path.abspath(__file__))
CVW, CVH = 1080, 1400          # ٧٢٫٩٪ من ارتفاع الريل
set_canvas(CVW, CVH)

# قالب مُجرَّد: عنوان أعلى، جارت، سطر سفلي — بلا صناديق ولا لوحات
BASE_CSS = """
.hl{top:126px;left:56px;right:56px;line-height:1.22}
#chartwrap{top:360px;left:0}
#chip{display:none} #endlogo{display:none} #res{display:none}
#cta{top:1772px}
#cta .k{font-size:44px;padding:9px 30px}
#cta .s{margin-top:8px;font-size:26px}
#edu{bottom:26px;font-size:19px;opacity:.55}
#brand{position:absolute;top:44px;left:0;right:0;text-align:center;z-index:7;opacity:.72}
#brand .g{width:30px;margin:0 auto} #brand .g svg{width:30px;height:auto}
#brand .w{margin-top:4px;font-size:13px;font-weight:800;letter-spacing:6px;color:#7F97A1}
.step{position:absolute;top:250px;right:56px;z-index:7;opacity:0;
  color:#43D4DC;font-size:25px;font-weight:800;letter-spacing:.5px}
.step i{font-style:normal;color:#7F97A1;margin-left:10px}
"""
BASE_HTML = (f'<div id="brand"><div class="g">{GEM}</div>'
             f'<div class="w">LIQUIDITY STATE</div></div>'
             '<div class="step" id="st1"><i>١</i>الشرط</div>'
             '<div class="step" id="st2"><i>٢</i>الدخول</div>'
             '<div class="step" id="st3"><i>٣</i>الإبطال</div>')

def pose(W, x, fy, j, cs, back=14, margin=0.055, wt=0.70):
    """تأطير حيّ: أحدث شمعة مكشوفة قرب الحافة والكادر ممتلئ بما رُسم.

    wt = موضع نقطة التركيز داخل مدى الأسعار المرئي. كلما ارتفعت هبط المحتوى
    في الكادر: عند 0.70 يلامس القاع حافة الشاشة السفلى ويصطدم بسطر «لغرض تعليمي».
    المشاهد التي تحمل وسوماً أسفل القاع (الكنس · الوقف) تحتاج قيمة أدنى.
    """
    lim = (cs - 1) / (2 * cs)
    cx = min(max(x(j) / CVW - lim + margin, 0.5 - lim), 0.5 + lim)
    lo_i = max(0, j - back)
    hi = max(W[k]["h"] for k in range(lo_i, j + 1))
    lo = min(W[k]["l"] for k in range(lo_i, j + 1))
    cy = min(max(fy(lo + (hi - lo) * wt), 0.5 - lim), 0.5 + lim)
    return [round(cx, 4), round(cy, 4)]


# ── تعديل الشموع ──
# قصّ الذيل (l = max(l, x)) يرفع القاع فوق الجسم فتُرسم شمعة مستحيلة.
# الإزاحة تحرّك الشمعة كاملة فتبقى o/h/l/c متسقة.
def shift(c, d):
    for k in ("o", "h", "l", "c"):
        c[k] += d

def floor_low(c, v, i=0, rng=0.0, spread=0.055):
    """أدنى نقطة الشمعة لا تنزل تحت v.

    الحدّ الثابت يرفع كل شمعة مخالفة إلى القيمة ذاتها، فتصطف القيعان في خط
    أفقي مسطّح لا يحدث في سوق. التشتيت المشتق من الترتيب يكسر هذا الاصطفاف.
    """
    v = v + rng * spread * (((i * 37) % 11) / 10.0)
    if c["l"] < v: shift(c, v - c["l"])

def set_low(c, v):
    shift(c, v - c["l"])

def cap_high(c, v):
    """أعلى نقطة الشمعة لا تتجاوز v."""
    if c["h"] > v: shift(c, v - c["h"])

def close_above(c, v):
    """جسم الشمعة كاملاً فوق v — أي إغلاق حقيقي لا مجرد اختراق بالذيل."""
    b = min(c["o"], c["c"])
    if b < v: shift(c, v - b)


# ═════════════ النموذج ١ — كنس وإغلاق ═════════════
def m_sweep():
    N, SEED = 30, 8601
    # القاع يتكوّن من الشموع الظاهرة منذ اللقطة الأولى (0–8): لا يُرسم مستوى
    # يستمد قيمته من شمعة لم تُكشف بعد.
    anch = [(0, 14.6), (4, 13.9), (8, 14.4), (11, 14.2), (14, 13.8),
            (17, 15.0), (21, 15.9), (25, 16.9), (29, 17.8)]
    W = gen(anch, N, SEED, wick=0.8)
    rng = max(c["h"] for c in W) - min(c["l"] for c in W)
    LOW = min(W[k]["l"] for k in range(2, 9))           # القاع المحمي
    for j in range(9, 14):                              # لا شيء يكسره قبل الكنس
        floor_low(W[j], LOW + rng * 0.012, j, rng)
    SW = 14                                             # شمعة الكنس
    W[SW].update(l=LOW - rng * 0.075, o=LOW + rng * 0.004,
                 c=LOW + rng * 0.050, h=LOW + rng * 0.065)
    for j in range(SW + 1, N):
        floor_low(W[j], LOW + rng * 0.014, j, rng)
    ENT = W[SW]["c"]                                    # الدخول بعد إغلاق شمعة الكنس
    STP = W[SW]["l"] - rng * 0.014
    TGT = ENT + (ENT - STP) * 2.0
    return dict(W=W, N=N, SEED=SEED, anch=anch, LOW=LOW, SW=SW,
                ENT=ENT, STP=STP, TGT=TGT, rng=rng, pj=(10, 12, 16, 20, 25),
                title='كَنْس القاع<br><span style="color:#43D4DC">ثم الإغلاق فوقه</span>',
                beats=["كيف تدخل بعد كنس السيولة؟",
                       "قاع محمي تحته أوامر إيقاف.",
                       "شمعة تكنسه ثم تُغلق فوقه.",
                       "الدخول بعد إغلاقها، والوقف تحت أدنى نقطة الكنس.",
                       "الإبطال: إغلاق يعود تحت القاع."],
                kw="كنس")

def sweep_svg(D, x, y, slot, fy):
    W, LOW, SW = D["W"], D["LOW"], D["SW"]
    R = x(D["N"] - 1) + slot * .5
    ex = []
    ex.append(line_el(x(2) - slot * .6, y(LOW), R, y(LOW), INK, 2.4, id="lvl"))
    ex.append(f'<g id="lvllbl" opacity="0">{htext(x(6), y(LOW) + 44, "قاع محمي", INK, 26)}</g>')
    ex.append(xmark(x(SW), y(W[SW]["l"]) + 28, id="swp", r=17))
    # الوسم بجانب العلامة لا تحتها: أسفلها حافة الكادر وسطر «لغرض تعليمي»
    ex.append(f'<g id="swplbl" opacity="0">{htext(x(SW) - slot * 2.6, y(W[SW]["l"]) + 37, "كَنْس", RED, 26)}</g>')
    ex.append(line_el(x(SW) - slot * .6, y(D["ENT"]), R, y(D["ENT"]), TEAL_D, 2.4, id="ent"))
    ex.append(f'<g id="entlbl" opacity="0">{htext(x(20), y(D["ENT"]) - 20, "الدخول", TEAL_D, 26)}</g>')
    ex.append(line_el(x(SW) - slot * .6, y(D["STP"]), R, y(D["STP"]), RED, 2.0, dash="8 6", id="stp"))
    # وسم الوقف فوق خطه: تحته حافة الكادر وسطر «لغرض تعليمي»
    ex.append(f'<g id="stplbl" opacity="0">{htext(x(23), y(D["STP"]) - 16, "الوقف", RED, 26)}</g>')
    ex.append(line_el(x(19) - slot * .6, y(D["TGT"]), R, y(D["TGT"]), TEAL_D, 2.2, id="tgt"))
    ex.append(f'<g id="tgtlbl" opacity="0">{htext(x(21), y(D["TGT"]) - 18, "الهدف ٢R", TEAL_D, 25)}</g>')
    ex.append(checkmark(x(25), y(D["TGT"]) - 40, id="ck"))
    return "".join(ex)


# ═════════════ النموذج ٢ — منتصف الفجوة ═════════════
def m_fvg():
    N, SEED = 30, 8602
    # الفجوة حقيقية بتعريفها: بين قمة الشمعة السابقة وقاع اللاحقة، بلا تداخل.
    anch = [(0, 13.2), (3, 13.4), (6, 15.6), (10, 15.5), (14, 14.3),
            (18, 15.9), (23, 17.0), (29, 17.9)]
    W = gen(anch, N, SEED, wick=0.75)
    rng = max(c["h"] for c in W) - min(c["l"] for c in W)
    K = 5                                                # شمعة الاندفاع
    W[K - 1]["h"] = max(W[K - 1]["o"], W[K - 1]["c"])     # بلا ذيل علوي: قمتها حدّ الفجوة
    GL = W[K - 1]["h"]
    GH = GL + rng * 0.150
    W[K].update(o=W[K - 1]["c"], l=W[K - 1]["c"] - rng * 0.02,
                c=GH + rng * 0.09, h=GH + rng * 0.12)
    set_low(W[K + 1], GH)                                # قاع اللاحقة = حدّ الفجوة الأعلى
    CE = (GL + GH) / 2                                   # المنتصف
    for j in range(K + 2, 13):                           # لا يعود إلى الفجوة قبل أوانه
        floor_low(W[j], GH + rng * 0.012, j, rng)
    W[13].update(l=CE - rng * 0.014, o=CE + rng * 0.052,  # الشمعة التي تلمس المنتصف
                 c=CE + rng * 0.030, h=CE + rng * 0.070)
    floor_low(W[14], CE + rng * 0.030)
    for j in range(15, N):
        floor_low(W[j], GH - rng * 0.010, j, rng, 0.075)
    ENT = CE
    STP = GL - rng * 0.022                               # تحت قاع الفجوة
    TGT = ENT + (ENT - STP) * 2.0
    return dict(W=W, N=N, SEED=SEED, anch=anch, GL=GL, GH=GH, CE=CE, K=K,
                ENT=ENT, STP=STP, TGT=TGT, rng=rng, pj=(8, 10, 15, 20, 25),
                title='الفجوة السعرية<br><span style="color:#43D4DC">الدخول من منتصفها</span>',
                beats=["كيف تدخل من الفجوة السعرية؟",
                       "اندفاع يترك فجوة بين ذيلين.",
                       "أمر معلّق عند منتصفها لا عند حافتها.",
                       "الدخول عند المنتصف، والوقف تحت قاع الفجوة.",
                       "الإبطال: إغلاق تحت الفجوة كاملة."],
                kw="منتصف")

def fvg_svg(D, x, y, slot, fy):
    R = x(D["N"] - 1) + slot * .5
    ex = []
    ex.append(zone_el("gap", x(D["K"] - 1) - slot * .6, y(D["GH"]), R, y(D["GL"]),
                      htext(x(17), y(D["GH"]) - 24, "الفجوة", TEAL_D, 26)))
    ex.append(line_el(x(D["K"]) - slot * .6, y(D["CE"]), R, y(D["CE"]), TEAL_D, 2.4, dash="9 6", id="ce"))
    ex.append(f'<g id="celbl" opacity="0">{htext(x(19), y(D["CE"]) - 18, "المنتصف = الدخول", TEAL_D, 26)}</g>')
    ex.append(line_el(x(D["K"]) - slot * .6, y(D["STP"]), R, y(D["STP"]), RED, 2.0, dash="8 6", id="stp"))
    ex.append(f'<g id="stplbl" opacity="0">{htext(x(23), y(D["STP"]) - 16, "الوقف", RED, 26)}</g>')
    ex.append(line_el(x(17) - slot * .6, y(D["TGT"]), R, y(D["TGT"]), TEAL_D, 2.2, id="tgt"))
    ex.append(f'<g id="tgtlbl" opacity="0">{htext(x(20), y(D["TGT"]) - 18, "الهدف ٢R", TEAL_D, 25)}</g>')
    ex.append(checkmark(x(25), y(D["TGT"]) - 40, id="ck"))
    return "".join(ex)


# ═════════════ النموذج ٣ — كسر وعودة ═════════════
def m_bos():
    N, SEED = 30, 8603
    # القمة المرجعية من الشموع الظاهرة أولاً (رقم ٧)، فالكسر والعودة يأتيان بعدها أمام المشاهد.
    anch = [(0, 17.6), (3, 16.5), (7, 17.2), (11, 15.7), (15, 17.7),
            (19, 17.1), (23, 20.4), (29, 22.0)]
    W = gen(anch, N, SEED, wick=0.8)
    rng = max(c["h"] for c in W) - min(c["l"] for c in W)
    LH = W[7]["h"]                                        # آخر قمة هابطة
    for j in range(8, 12):                                # قمم أدنى: لا شيء يتجاوزها
        cap_high(W[j], LH - rng * 0.025)
    ZT, ZB = LH, LH - rng * 0.075                         # منطقة النشأة = القمة المكسورة
    for j in range(12, 16):                               # الكسر بالإغلاق لا بالذيل
        close_above(W[j], LH + rng * 0.030)
    for j in range(16, 20):                               # العودة: قيعان صاعدة داخل المنطقة
        set_low(W[j], ZB + rng * (0.012 + 0.021 * (j - 16)))
    for j in range(20, N):
        floor_low(W[j], ZT - rng * 0.008, j, rng, 0.075)
    ENT = (ZT + ZB) / 2
    STP = ZB - rng * 0.022
    TGT = ENT + (ENT - STP) * 2.0
    return dict(W=W, N=N, SEED=SEED, anch=anch, LH=LH, ZT=ZT, ZB=ZB,
                ENT=ENT, STP=STP, TGT=TGT, rng=rng, pj=(9, 12, 18, 21, 26),
                title='كسر الهيكل<br><span style="color:#43D4DC">ثم العودة إليه</span>',
                beats=["كيف تدخل بعد كسر الهيكل؟",
                       "إغلاق فوق آخر قمة هابطة.",
                       "العودة إلى المنطقة التي صنعت الكسر.",
                       "الدخول من المنطقة، والوقف تحت قاعها.",
                       "الإبطال: إغلاق تحت المنطقة."],
                kw="كسر")

def bos_svg(D, x, y, slot, fy):
    R = x(D["N"] - 1) + slot * .5
    ex = []
    ex.append(line_el(x(4) - slot * .6, y(D["LH"]), R, y(D["LH"]), INK, 2.2, id="lvl"))
    ex.append(f'<g id="lvllbl" opacity="0">{htext(x(10), y(D["LH"]) - 22, "آخر قمة هابطة", INK, 26)}</g>')
    ex.append(zone_el("zn", x(16) - slot * .6, y(D["ZT"]), R, y(D["ZB"]),
                      htext(x(26), y(D["ZT"]) - 16, "منطقة النشأة", TEAL_D, 25)))
    ex.append(line_el(x(16) - slot * .6, y(D["ENT"]), R, y(D["ENT"]), TEAL_D, 2.4, dash="9 6", id="ent"))
    ex.append(f'<g id="entlbl" opacity="0">{htext(x(21), y(D["ENT"]) - 18, "الدخول", TEAL_D, 26)}</g>')
    ex.append(line_el(x(16) - slot * .6, y(D["STP"]), R, y(D["STP"]), RED, 2.0, dash="8 6", id="stp"))
    ex.append(f'<g id="stplbl" opacity="0">{htext(x(21), y(D["STP"]) - 16, "الوقف", RED, 26)}</g>')
    ex.append(line_el(x(20) - slot * .6, y(D["TGT"]), R, y(D["TGT"]), TEAL_D, 2.2, id="tgt"))
    ex.append(f'<g id="tgtlbl" opacity="0">{htext(x(22), y(D["TGT"]) - 18, "الهدف ٢R", TEAL_D, 25)}</g>')
    ex.append(checkmark(x(26), y(D["TGT"]) - 40, id="ck"))
    return "".join(ex)


# fullset = كل عنصر يُحرَّك بوضع غير «draw» — الزون منها؛ إسقاطه يتركه شفافاً للأبد.
MODELS = {
    "sweep": (m_sweep, sweep_svg,
              # وسما القاع والكنس ينسحبان قبل وسم الوقف: الثلاثة تتزاحم أسفل الكادر
              [("lvl", 2.9, 3.4, "draw"), ("lvllbl", 3.45, 3.7, "pop", 9.7, .3),
               ("swp", 6.9, 7.3, "drawx", 11.9, .3), ("swplbl", 7.35, 7.6, "pop", 11.9, .3),
               ("ent", 9.9, 10.4, "draw"), ("entlbl", 10.45, 10.7, "pop"),
               ("stp", 11.6, 12.1, "draw"), ("stplbl", 12.15, 12.4, "pop"),
               ("tgt", 13.9, 14.4, "draw"), ("tgtlbl", 14.45, 14.7, "pop"),
               ("ck", 15.9, 16.2, "pop")],
              ["lvllbl", "swp", "swplbl", "entlbl", "stplbl", "tgtlbl", "ck"],
              ["lvl", "ent", "stp", "tgt"]),
    "fvg":   (m_fvg, fvg_svg,
              [("gap", 2.9, 3.6, "zone"),
               ("ce", 6.9, 7.4, "draw"), ("celbl", 7.45, 7.7, "pop"),
               ("stp", 10.4, 10.9, "draw"), ("stplbl", 10.95, 11.2, "pop"),
               ("tgt", 13.6, 14.1, "draw"), ("tgtlbl", 14.15, 14.4, "pop"),
               ("ck", 15.9, 16.2, "pop")],
              ["gap", "celbl", "stplbl", "tgtlbl", "ck"],
              ["ce", "stp", "tgt"]),
    "bos":   (m_bos, bos_svg,
              [("lvl", 2.9, 3.4, "draw"), ("lvllbl", 3.45, 3.7, "pop", 10.2, .3),
               ("zn", 7.1, 7.8, "zone"),
               ("ent", 10.4, 10.9, "draw"), ("entlbl", 10.95, 11.2, "pop"),
               ("stp", 12.0, 12.5, "draw"), ("stplbl", 12.55, 12.8, "pop"),
               ("tgt", 14.2, 14.7, "draw"), ("tgtlbl", 14.75, 15.0, "pop"),
               ("ck", 16.0, 16.3, "pop")],
              ["lvllbl", "zn", "entlbl", "stplbl", "tgtlbl", "ck"],
              ["lvl", "ent", "stp", "tgt"]),
}

DUR = 19.4                                   # ≤ ٢٠ ثانية

def build(key, out=None):
    mk, svgf, marks, fullset, drawset = MODELS[key]
    D = mk()
    W, N = D["W"], D["N"]
    x, y, slot = geom(W)
    fy = lambda p: y(p) / CVH
    ex = svgf(D, x, y, slot, fy)
    B = D["beats"]; PJ = D["pj"]

    cfg = dict(
        w=W, dark=True, extra_css=BASE_CSS, extra_html=BASE_HTML,
        base=8, openmax=N, open_t=[[N - 1, 0.45]],
        story=[(j, round(2.9 + (j - 9) * 0.42, 2)) for j in range(9, N)],
        extra_svg=ex, marks=marks, fullset=fullset, drawset=drawset,
        dom_marks=[["st1", 2.8, 3.1, 9.6, .3],
                   ["st2", 9.8, 10.1, 15.3, .3],
                   ["st3", 15.5, 15.8, 18.4, .3]],
        preview_a=0.0, preview_b=0.0, res_tease=False, sweep_op=0.0, flash_op=0.0,
        txt=[(f"t{i+1}", a, b, B[i], fs, INK) for i, (a, b, fs) in enumerate(
            [(0.10, 2.75, 48), (2.90, 6.75, 44), (6.90, 9.65, 44),
             (9.85, 15.30, 42), (15.50, 18.40, 42)])],
        chip="", res="", cta_k=f"اكتب «{D['kw']}»", cta_s="ويصلك الشرح كاملاً",
        edu="لغرض تعليمي — مثال تخطيطي",
        dur=DUR, res_t=999, cta_t=18.6,
        flash=(999, 999.1), punch=(999, 999.1, 0.0),
        # wt منخفض في مشاهد الكنس والوقف: وسومها تحت القاع وتُقتطع عند 0.70.
        # النهاية عند 1.06: أي تكبير أعلى يقصّ الهدف وعلامة الصحّ عن الحافة اليمنى.
        cam=[[0.00, 1.42] + pose(W, x, fy, PJ[0], 1.42, wt=0.60),
             [2.80, 1.48] + pose(W, x, fy, PJ[1], 1.48, wt=0.56),
             [6.80, 1.56] + pose(W, x, fy, PJ[2], 1.56, wt=0.48) + ["creep"],
             [9.80, 1.58] + pose(W, x, fy, PJ[3], 1.58, wt=0.46) + ["creep"],
             [13.60, 1.42] + pose(W, x, fy, PJ[4], 1.42, wt=0.52) + ["creep"],
             [15.60, 1.16, .5, .5, "creep"],
             [DUR, 1.06, .5, .5, "creep"]],
    )
    out = out or f"reel25_{key}.html"
    n = build_reel(cfg, os.path.join(HERE, out))
    print(f"{key:<6} {n} bytes | dur {DUR}s | canvas {CVW}×{CVH} = {CVH/1920*100:.1f}% | kw {D['kw']}")
    return D

if __name__ == "__main__":
    import sys
    for k in (sys.argv[1:] or list(MODELS)):
        build(k)
