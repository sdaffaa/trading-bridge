# -*- coding: utf-8 -*-
"""تشغيلة ٢٦ — النماذج الثلاثة نفسها، لكن على شاشة منصة وبيانات سوق حقيقية.

🔒 أمر فهد 2026-08-05: «الماركب والتحليل كأنني بمنصة تريدنق فيو، جارت حقيقي
   على أحد فريمات ساعة · ١٥ دقيقة · ٣٠ دقيقة · ٥ دقيقة».

ما تغيّر عن تشغيلة ٢٥:
  • الشموع بيانات حقيقية من السوق (الذهب GC=F) لا سلاسل مولّدة.
  • أثاث الشاشة: محور سعر يميناً بأرقام حقيقية · محور وقت أسفل · شبكة ·
    شريط الرمز والفريم وقيم OHLC · لصيقة السعر الحي على المحور.
  • الماركب صار أداة الصفقة: صندوق ربح أخضر فوق الدخول وصندوق مخاطرة أحمر
    تحته، بالأسعار الفعلية.
  • الكاميرا ثابتة: الشاشة لا تتجوّل، والحركة كلها من تكشّف الشموع والماركب.

الفهارس كلها مكشوفة بالمسح في real_setups.json ومُتحقَّق منها بالحساب،
لا مكتوبة بالنظر: لا مستوى ولا فجوة ولا كسر يُرسم ما لم تثبته الشموع.
"""
import json, os
from reel_build import INK, TEAL, TEAL_D, RED, GREY, htext, MUTE
from reel_sfx_kit import (build_reel, geom, line_el, zone_el, xmark, checkmark,
                          pos_box, set_canvas, set_pad, plot_box)
import tv_chart
from car_common import GEM

# الهوية: جسم الشرح أوف-وايت. الشاشة الداكنة للغلاف والافتتاحية فقط.
THEME = os.environ.get("LS_THEME", "light")
tv_chart.set_theme(THEME)
DARKMODE = THEME == "dark"

HERE = os.path.dirname(os.path.abspath(__file__))
CVW, CVH = 1080, 1400              # ٧٢٫٩٪ من ارتفاع الريل
set_canvas(CVW, CVH)
set_pad(18, 122, 92, 66)           # حزام محور السعر يميناً ومحور الوقت أسفل
DUR = 19.4
REVEAL = (3.0, 11.5)               # نافذة تكشّف الشموع

BASE_CSS = """
.hl{top:120px;left:56px;right:56px;line-height:1.22}
#chartwrap{top:360px;left:0}
#chip{display:none} #endlogo{display:none} #res{display:none}
#cta{top:1786px}
#cta .k{font-size:44px;padding:9px 30px}
#cta .s{margin-top:8px;font-size:26px}
#edu{bottom:22px;font-size:19px;opacity:.55}
#brand{position:absolute;top:40px;left:0;right:0;text-align:center;z-index:7;opacity:.7}
#brand .g{width:28px;margin:0 auto} #brand .g svg{width:28px;height:auto}
#brand .w{margin-top:4px;font-size:13px;font-weight:800;letter-spacing:6px;color:__SUB__}
.hl b{display:block;font-size:46px;font-weight:900;line-height:1.18}
.hl .why{display:block;margin-top:10px;font-size:31px;font-weight:600;color:__SUB__;line-height:1.34}
.hl .why em{font-style:normal;font-weight:800;color:__ACC__}
.cfw{display:block;margin-top:12px}
.cf{display:flex;align-items:baseline;gap:10px;margin-top:9px;font-size:27px;
  font-weight:800;color:__TXT__;line-height:1.3}
.cf i{font-style:normal;font-weight:900;color:__ACC__;font-size:25px}
.cf b{font-weight:600;color:__SUB__;font-size:25px}
#steps{position:absolute;top:272px;left:56px;right:56px;z-index:7;
  display:flex;gap:9px;justify-content:space-between}
.sp{position:relative;flex:1;height:52px}
.sp .f{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;
  border-radius:9px;font-size:23px;font-weight:800;letter-spacing:.3px}
.sp .b{background:__PILLBG__;color:__SUB__}
.sp .a{background:__ACC__;color:__PILLTX__;opacity:0}
""".replace("__SUB__", "#7F97A1" if DARKMODE else "#6B7C84") \
   .replace("__ACC__", "#43D4DC" if DARKMODE else "#1E627A") \
   .replace("__PILLBG__", "rgba(255,255,255,0.07)" if DARKMODE else "rgba(15,46,60,0.075)") \
   .replace("__PILLTX__", "#08131C" if DARKMODE else "#FBF9F5") \
   .replace("__TXT__", "#ECF3F6" if DARKMODE else "#0F2E3C")
# ست خطوات مرقّمة ظاهرة طوال الريل: المشاهد يعرف أين هو ومَ بقي.
STEP_NAMES = ["الشرط", "الإشارة", "التنفيذ", "الأسباب", "الهدف", "الإبطال"]
AR_NUM = "١٢٣٤٥٦"

def steps_html():
    o = []
    for k, nm in enumerate(STEP_NAMES):
        o.append(f'<div class="sp"><div class="f b">{AR_NUM[k]} {nm}</div>'
                 f'<div class="f a" id="sa{k+1}">{AR_NUM[k]} {nm}</div></div>')
    return '<div id="steps">' + "".join(o) + '</div>'

BASE_HTML = (f'<div id="brand"><div class="g">{GEM}</div>'
             f'<div class="w">LIQUIDITY STATE</div></div>' + steps_html())

TFN = {"5m": "٥ دقائق", "15m": "١٥ دقيقة", "30m": "٣٠ دقيقة", "1h": "ساعة"}

with open(os.path.join(HERE, "real_setups.json"), encoding="utf-8") as f:
    SETUPS = {s["key"]: s for s in json.load(f)}


def exec_mark(xc, yc, price, dec=2, col="#1E627A"):
    """ماركب مكان التنفيذ: مثلّث عند الشمعة التي نُفِّذ عندها الأمر وسعرُه.

    بلا هذا الوسم يرى المشاهد صندوق صفقة معلّقاً في الهواء، ولا يعرف
    أي شمعة بالضبط فُتحت عندها الصفقة."""
    t = 13
    return (f'<g id="ex" opacity="0">'
            f'<path d="M {xc - t*2.2:.1f} {yc - t:.1f} L {xc - t*0.5:.1f} {yc:.1f} '
            f'L {xc - t*2.2:.1f} {yc + t:.1f} Z" fill="{col}"/>'
            f'<circle cx="{xc:.1f}" cy="{yc:.1f}" r="5.5" fill="{col}"/>'
            + htext(xc - t*2.6, yc - 20, "تنفيذ", col, 24, anchor="start")
            + '</g>')


def conf_html(S):
    """أسباب الدخول مجتمعة — محسوبة من الشموع، تُعرض بأرقامها لا بوصفها."""
    # ثلاثة فقط: الرابع يتجاوز المسافة حتى شريط الخطوات فيركبه.
    # نسبة العائد للمخاطرة تُعرض في الخطوة ٥ فلا تُكرَّر هنا.
    spec = [r for r in S["conf"] if r["t"] != "عائد مقابل مخاطرة"]
    rr = [r for r in S["conf"] if r["t"] == "عائد مقابل مخاطرة"]
    top = (spec + rr)[:3]          # الأدلة المحددة أولاً، والنسبة تكمل الثلاثة
    return "".join(f'<span class="cf"><i>✓</i>{r["t"]}<b>{r["d"]}</b></span>'
                   for r in top)


def times(S, base):
    """زمن ظهور كل شمعة — الماركب يتبع الشمعة التي تسبّبت فيه لا العكس."""
    N = len(S["w"])
    idx = list(range(base + 1, N))
    a, b = REVEAL
    st = (b - a) / max(1, len(idx) - 1)
    return {j: round(a + i * st, 2) for i, j in enumerate(idx)}


# ═════════ النموذج ١ — كنس وإغلاق · الذهب ١٥ دقيقة ═════════
def m_sweep():
    S = SETUPS["sweep"]; W = S["w"]; i = S["i"]
    T = times(S, 8)
    t_lvl = round(T[i - 2] + 0.25, 2)          # بعد اكتمال الشموع التي صنعت القاع
    t_sig = round(T[i] + 0.20, 2)              # بعد إغلاق شمعة الكنس
    U = S["ENT"] - S["STP"]
    return dict(S=S, base=8, T=T, t_lvl=t_lvl, t_sig=t_sig,
                hook="كسر القاع ليس بيعاً.<br>تعرف لماذا؟",
                steps=[
                 (f'قاع محمي عند {S["LOW"]:,.2f}',
                  "القيعان الواضحة تتكدّس تحتها أوامر الإيقاف، فهي وقود لا حاجز."),
                 ("اختراق ثم إغلاق فوقه",
                  "الإغلاق فوق القاع رفضٌ للسعر الأدنى، لا كسراً للهيكل."),
                 (f'الدخول عند إغلاق تلك الشمعة {S["ENT"]:,.2f}',
                  "قبل الإغلاق يبقى الكسر احتمالاً قائماً، فالانتظار جزء من الطريقة."),
                 (f'الوقف تحت أدنى نقطة الكنس {S["STP"]:,.2f}',
                  "نزول السعر تحتها يعني أن الرفض لم يكن رفضاً."),
                 (f'الهدف ٢R عند {S["TGT"]:,.2f}',
                  f'مخاطرة {U:,.2f} مقابل {U*2:,.2f} دولاراً على العقد نفسه.'),
                 ("الإبطال: إغلاق يعود تحت القاع",
                  "ما رُفض صار مقبولاً، فتسقط الفكرة كلها لا الصفقة وحدها."),
                ], kw="كنس")

def sweep_svg(D, x, y, slot):
    S = D["S"]; W = S["w"]; i = S["i"]; LOW = S["LOW"]
    _, pr, _, _, _, _ = plot_box(); R = CVW - pr
    ex = [line_el(x(2), y(LOW), R, y(LOW), tv_chart.T["LVL"], 2.2, id="lvl"),
          f'<g id="lvllbl" opacity="0">{htext(x(4), y(LOW) - 14, f"قاع محمي {LOW:,.2f}", tv_chart.T["LVL"], 25)}</g>',
          xmark(x(i), y(W[i]["l"]) + 26, id="swp", r=16),
          f'<g id="swplbl" opacity="0">{htext(x(i) - slot * 2.4, y(W[i]["l"]) + 34, "كَنْس", RED, 25)}</g>']
    return ex


# ═════════ النموذج ٢ — منتصف الفجوة · الذهب ساعة ═════════
def m_fvg():
    S = SETUPS["fvg"]; k, tap = S["k"], S["tap"]
    T = times(S, 18)
    U = S["ENT"] - S["STP"]
    return dict(S=S, base=18, T=T,
                t_lvl=round(T[k + 1] + 0.25, 2),    # الفجوة تكتمل بظهور الشمعة اللاحقة
                t_sig=round(T[tap] + 0.20, 2),      # بعد الشمعة التي لمست المنتصف
                hook="الفجوة ليست منطقة دخول.<br>أين الخطأ؟",
                steps=[
                 (f'فجوة {S["GH"] - S["GL"]:,.2f} دولاراً بين ذيلين',
                  "اندفاع مرّ بسرعة فترك سعراً لم يُتداول عليه في الاتجاهين."),
                 ("عودة تلمس منتصف الفجوة",
                  "المنتصف أعدل نقطة بين حافتيها، وعنده يتوازن ما فات."),
                 (f'الدخول بأمر معلّق عند {S["ENT"]:,.2f}',
                  "الحافة العليا مبكّرة تُدخلك بلا تأكيد، والسفلى نادراً تُلمس."),
                 (f'الوقف تحت قاع الفجوة {S["STP"]:,.2f}',
                  "ملء الفجوة كاملة يلغي السبب الذي دخلت من أجله."),
                 (f'الهدف ٢R عند {S["TGT"]:,.2f}',
                  f'مخاطرة {U:,.2f} مقابل {U*2:,.2f} دولاراً على العقد نفسه.'),
                 ("الإبطال: إغلاق تحت الفجوة كاملة",
                  "الاختلال امتُصّ ولم يعد مرجعاً يُبنى عليه."),
                ], kw="منتصف")

def fvg_svg(D, x, y, slot):
    S = D["S"]; k = S["k"]; GL, GH = S["GL"], S["GH"]
    _, pr, _, _, _, _ = plot_box(); R = CVW - pr
    gl = htext(x(k - 2), y(GH) - 22, f"فجوة {GH - GL:,.2f}$", TEAL_D, 25)
    ex = [zone_el("gap", x(k - 1) - slot * .6, y(GH), x(S["fill"]) + slot * 1.6, y(GL), ""),
          f'<g id="gaplbl" opacity="0">{gl}</g>',
          line_el(x(k) - slot * .6, y(S["ENT"]), R, y(S["ENT"]), TEAL_D, 2.2, dash="9 6", id="ce"),
          f'<g id="celbl" opacity="0">{htext(x(k - 2), y(S["ENT"]) - 18, "المنتصف", TEAL_D, 25)}</g>']
    return ex


# ═════════ النموذج ٣ — كسر وعودة · الذهب ٥ دقائق ═════════
def m_bos():
    S = SETUPS["bos"]; p, brk, fill = S["p"], S["brk"], S["fill"]
    T = times(S, 8)
    U = S["ENT"] - S["STP"]
    return dict(S=S, base=8, T=T,
                t_lvl=round(T[p] + 0.25, 2),        # بعد ظهور القمة نفسها
                t_sig=round(T[fill] + 0.20, 2),     # بعد الشمعة التي ارتدّت من المستوى
                t_brk=round(T[brk] + 0.15, 2),
                hook="الكسر وحده لا يكفي.<br>ما الذي لم تلاحظه؟",
                steps=[
                 (f'آخر قمة هابطة عند {S["LH"]:,.2f}',
                  "كسرها بإغلاق يقلب قراءة الهيكل من هابط إلى صاعد."),
                 ("إغلاق فوقها ثم عودة إليها",
                  "المستوى المكسور يتحوّل من سقف إلى أرضية، وهذا ما تختبره العودة."),
                 (f'الدخول عند ارتداد المستوى {S["ENT"]:,.2f}',
                  "منتصف المنطقة نادراً يُلمس، فأمر عنده يبقى معلّقاً بلا صفقة."),
                 (f'الوقف تحت قاع شمعة النشأة {S["STP"]:,.2f}',
                  "هي الشمعة التي أطلقت الكسر، وكسر قاعها يُسقط سببه."),
                 (f'الهدف ٢R عند {S["TGT"]:,.2f}',
                  f'مخاطرة {U:,.2f} مقابل {U*2:,.2f} دولاراً على العقد نفسه.'),
                 ("الإبطال: إغلاق تحت المنطقة",
                  "الأرضية الجديدة لم تصمد، فالقلب لم يكتمل."),
                ], kw="كسر")

def bos_svg(D, x, y, slot):
    S = D["S"]; p = S["p"]; LH = S["LH"]; org = S["org"]
    _, pr, _, _, _, _ = plot_box(); R = CVW - pr
    lbl = htext(x(p + 6), y(LH) - 18, f"قمة هابطة {LH:,.2f}", tv_chart.T["LVL"], 25)
    ex = [line_el(x(p - 5), y(LH), R, y(LH), tv_chart.T["LVL"], 2.2, id="lvl"),
          f'<g id="lvllbl" opacity="0">{lbl}</g>',
          # المنطقة هي شمعة النشأة نفسها — آخر شمعة هابطة قبل الكسر — لا مربع مفترض
          zone_el("zn", x(org) - slot * .6, y(S["ZT"]), x(S["fill"]) + slot * 1.6, y(S["ZB"]), ""),
          f'<g id="znlbl" opacity="0">{htext(x(org - 2), y(S["ZB"]) + 34, "شمعة النشأة", TEAL_D, 24)}</g>']
    return ex


MODELS = {
    "sweep": (m_sweep, sweep_svg, ["lvl"], ["lvllbl", "swp", "swplbl"]),
    "fvg":   (m_fvg, fvg_svg, ["ce"], ["gap", "gaplbl", "celbl"]),
    "bos":   (m_bos, bos_svg, ["lvl"], ["lvllbl", "zn", "znlbl"]),
}


def build(key, out=None):
    mk, svgf, drawset, fullset = MODELS[key]
    D = mk(); S = D["S"]; W = S["w"]; N = len(W)
    x, y, slot = geom(W)
    _, pr, _, _, _, _ = plot_box()
    ex = svgf(D, x, y, slot)

    # ── أداة الصفقة: صندوق ربح فوق الدخول وصندوق مخاطرة تحته، بالأسعار الفعلية ──
    ent_i = S["fill"]
    ex.append(pos_box("box", x(ent_i) - slot * .6, CVW - pr,
                      y(S["ENT"]), y(S["STP"]), y(S["TGT"]),
                      lbl_e=f'الدخول {S["ENT"]:,.2f}',
                      lbl_s=f'الوقف {S["STP"]:,.2f}',
                      lbl_t=f'الهدف ٢R  {S["TGT"]:,.2f}',
                      anchor_e="start",    # RTL: البداية يميناً فينمو النص يساراً داخل الكادر
                      col_e="#ECF3F6" if DARKMODE else INK))   # أبيض على أوف-وايت = وسم مختفٍ
    # علامة الصحّ على الشمعة التي بلغت الهدف فعلاً، لا في مكان مريح
    ex.append(exec_mark(x(S["fill"]), y(S["ENT"]), S["ENT"], S["dec"],
                        "#43D4DC" if DARKMODE else "#1E627A"))
    ex.append(checkmark(x(S["hit"]), y(S["TGT"]) - 40, id="ck"))
    fullset = fullset + ["ex", "box", "ck"]

    t_lvl, t_sig = D["t_lvl"], D["t_sig"]
    # ── جدول الخطوات الست ──
    # ١ الشرط و٢ الإشارة يتبعان الشموع؛ و٣–٦ توزَّع بالتساوي حتى نهاية الشرح،
    # فتبقى كل خطوة فوق حدّ القراءة ولا تُزاحم التي بعدها.
    s1 = round(max(2.2, min(3.2, t_sig - 2.2)), 2)
    s2 = t_sig
    t_box = round(max(t_sig + 2.2, 9.0), 2)
    END = 18.55
    span = (END - t_box) / 4
    s3, s4, s5, s6 = (round(t_box + k * span, 2) for k in range(4))
    ST = [s1, s2, s3, s4, s5, s6]
    assert all(ST[k + 1] - ST[k] >= 1.7 for k in range(5)), f"خطوة أقصر من حدّ القراءة: {ST}"
    assert s1 - 0.10 >= 1.7, "الهوك أقصر من حدّ القراءة"

    t_ck = round(s5 + 1.1, 2)
    marks = [(drawset[0], t_lvl, t_lvl + 0.5, "draw")]
    if key == "sweep":
        # لا انسحاب: الوسوم هي سبب الدخول المرئي، تبقى مع الصندوق حتى النهاية
        marks += [("lvllbl", t_lvl + 0.55, t_lvl + 0.8, "pop"),
                  ("swp", t_sig, t_sig + 0.4, "drawx"),
                  ("swplbl", t_sig + 0.45, t_sig + 0.7, "pop")]
    elif key == "fvg":
        marks = [("gap", t_lvl, t_lvl + 0.7, "zone"),
                 ("gaplbl", t_lvl + 0.75, t_lvl + 1.0, "pop"),
                 ("ce", t_sig, t_sig + 0.5, "draw"),
                 ("celbl", t_sig + 0.55, t_sig + 0.8, "pop")]
    else:
        marks += [("lvllbl", t_lvl + 0.55, t_lvl + 0.8, "pop"),
                  ("zn", t_sig, t_sig + 0.7, "zone"),
                  ("znlbl", t_sig + 0.75, t_sig + 1.0, "pop")]
    # الصندوق كاملاً من لحظة التنفيذ لا موزَّعاً على خطوات: الصفقة تُفتح مرة واحدة
    marks += [("ex", t_box, t_box + 0.35, "pop"),
              ("box", t_box + 0.15, t_box + 1.75, "posbox"),
              ("ck", t_ck, t_ck + 0.3, "pop")]

    B = [D["hook"]]
    for n, (t, w) in enumerate(D["steps"]):
        if n == 3:      # الخطوة ٤: الأسباب مجتمعة بأرقامها، بلا عنوان
            B.append(f'<span class="cfw">{conf_html(S)}</span>')
        else:
            B.append(f'<b>{t}</b><span class="why"><em>لماذا:</em> {w}</span>')
    b_ = [(0.10, s1 - 0.15, 46)] + [(ST[k], (ST[k + 1] if k < 5 else END) - 0.15, 40)
                                    for k in range(6)]
    dom = [[f"sa{k+1}", ST[k], ST[k] + 0.25,
            (ST[k + 1] if k < 5 else END) - 0.15, .25] for k in range(6)]

    tl = [c["d"] for c in W]
    pre = tv_chart.furniture(W, dec=S["dec"], sym=S["sym"], tf=S["tf"], tlabels=tl)
    ex.insert(0, tv_chart.legend(W, sym=S["sym"], tf=S["tf"], dec=S["dec"]))

    cfg = dict(
        w=W, dark=DARKMODE, extra_css=BASE_CSS, extra_html=BASE_HTML,
        grid=False, pre_svg=pre,
        lp_pill=True, lp_dec=S["dec"], lp_col=tv_chart.T["PILL"], lp_txt=tv_chart.T["PILLTX"],
        base=D["base"], openmax=N, open_t=[[N - 1, 0.45]],
        story=[(j, t) for j, t in D["T"].items()],
        extra_svg="".join(ex), marks=marks, fullset=fullset, drawset=drawset,
        dom_marks=dom,
        preview_a=0.0, preview_b=0.0, res_tease=False, sweep_op=0.0, flash_op=0.0,
        txt=[(f"t{i+1}", a, b, B[i], fs, INK) for i, (a, b, fs) in enumerate(b_)],
        chip="", res="", cta_k=f"اكتب «{D['kw']}»", cta_s="ويصلك الشرح كاملاً",
        edu=f'{S["sym"]} · {TFN[S["tf"]]} · {S["date"]} — لغرض تعليمي',
        dur=DUR, res_t=999, cta_t=18.75,
        flash=(999, 999.1), punch=(999, 999.1, 0.0),
        # الكاميرا ثابتة: شاشة المنصة لا تتجوّل، وأي تكبير يقصّ محور السعر
        cam=[[0.00, 1.0, .5, .5], [DUR, 1.0, .5, .5]],
    )
    out = out or f"reel26_{key}_{THEME}.html"
    n = build_reel(cfg, os.path.join(HERE, out))
    json.dump(dict(dur=DUR, hook=0.10, steps=ST, t_lvl=t_lvl, t_sig=t_sig,
                   t_box=t_box, t_ck=t_ck, end=END, cta=18.75),
              open(os.path.join(HERE, f"reel26_{key}_cues.json"), "w"), indent=1)
    print(f'{key:<6} {S["sym"]} {S["tf"]:<4} {S["date"]} | شموع {N} | '
          f'خطوات {ST} | مستوى {t_lvl}s صندوق {t_box}s | {n} bytes')
    return D


if __name__ == "__main__":
    import sys
    for k in (sys.argv[1:] or list(MODELS)):
        build(k)
