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
.step{position:absolute;top:244px;right:56px;z-index:7;opacity:0;
  color:__ACC__;font-size:25px;font-weight:800;letter-spacing:.5px}
.step i{font-style:normal;color:__SUB__;margin-left:10px}
""".replace("__SUB__", "#7F97A1" if DARKMODE else "#6B7C84") \
   .replace("__ACC__", "#43D4DC" if DARKMODE else "#1E627A")
BASE_HTML = (f'<div id="brand"><div class="g">{GEM}</div>'
             f'<div class="w">LIQUIDITY STATE</div></div>'
             '<div class="step" id="st1"><i>١</i>الشرط</div>'
             '<div class="step" id="st2"><i>٢</i>الدخول</div>'
             '<div class="step" id="st3"><i>٣</i>الإبطال</div>')

TFN = {"5m": "٥ دقائق", "15m": "١٥ دقيقة", "30m": "٣٠ دقيقة", "1h": "ساعة"}

with open(os.path.join(HERE, "real_setups.json"), encoding="utf-8") as f:
    SETUPS = {s["key"]: s for s in json.load(f)}


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
    return dict(S=S, base=8, T=T, t_lvl=t_lvl, t_sig=t_sig,
                beats=["كيف تدخل بعد كنس السيولة؟",
                       "قاع محمي تحته أوامر إيقاف.",
                       "شمعة تكنسه ثم تُغلق فوقه.",
                       f"الدخول {S['ENT']:,.2f} والوقف {S['STP']:,.2f} تحت أدنى نقطة الكنس.",
                       "الإبطال: إغلاق يعود تحت القاع."],
                kw="كنس")

def sweep_svg(D, x, y, slot):
    S = D["S"]; W = S["w"]; i = S["i"]; LOW = S["LOW"]
    _, pr, _, _, _, _ = plot_box(); R = CVW - pr
    ex = [line_el(x(2), y(LOW), R, y(LOW), tv_chart.T["LVL"], 2.2, id="lvl"),
          f'<g id="lvllbl" opacity="0">{htext(x(6), y(LOW) + 40, f"قاع محمي {LOW:,.2f}", tv_chart.T["LVL"], 25)}</g>',
          xmark(x(i), y(W[i]["l"]) + 26, id="swp", r=16),
          f'<g id="swplbl" opacity="0">{htext(x(i) + slot * 2.8, y(W[i]["l"]) + 34, "كَنْس", RED, 25)}</g>']
    return ex


# ═════════ النموذج ٢ — منتصف الفجوة · الذهب ساعة ═════════
def m_fvg():
    S = SETUPS["fvg"]; k, tap = S["k"], S["tap"]
    T = times(S, 18)
    return dict(S=S, base=18, T=T,
                t_lvl=round(T[k + 1] + 0.25, 2),    # الفجوة تكتمل بظهور الشمعة اللاحقة
                t_sig=round(T[tap] + 0.20, 2),      # بعد الشمعة التي لمست المنتصف
                beats=["كيف تدخل من الفجوة السعرية؟",
                       "اندفاع يترك فجوة بين ذيلين.",
                       "أمر معلّق عند منتصفها لا عند حافتها.",
                       f"الدخول {S['ENT']:,.2f} والوقف {S['STP']:,.2f} تحت قاع الفجوة.",
                       "الإبطال: إغلاق تحت الفجوة كاملة."],
                kw="منتصف")

def fvg_svg(D, x, y, slot):
    S = D["S"]; k = S["k"]; GL, GH = S["GL"], S["GH"]
    _, pr, _, _, _, _ = plot_box(); R = CVW - pr
    gl = htext(x(k + 6), y(GH) - 22, f"فجوة {GH - GL:,.2f}$", TEAL_D, 25)
    ex = [zone_el("gap", x(k - 1) - slot * .6, y(GH), x(S["fill"]) + slot * 1.6, y(GL), ""),
          f'<g id="gaplbl" opacity="0">{gl}</g>',
          line_el(x(k) - slot * .6, y(S["ENT"]), R, y(S["ENT"]), TEAL_D, 2.2, dash="9 6", id="ce"),
          f'<g id="celbl" opacity="0">{htext(x(k + 6), y(S["ENT"]) - 18, "المنتصف", TEAL_D, 25)}</g>']
    return ex


# ═════════ النموذج ٣ — كسر وعودة · الذهب ٥ دقائق ═════════
def m_bos():
    S = SETUPS["bos"]; p, brk, fill = S["p"], S["brk"], S["fill"]
    T = times(S, 8)
    return dict(S=S, base=8, T=T,
                t_lvl=round(T[p] + 0.25, 2),        # بعد ظهور القمة نفسها
                t_sig=round(T[fill] + 0.20, 2),     # بعد الشمعة التي ارتدّت من المستوى
                t_brk=round(T[brk] + 0.15, 2),
                beats=["كيف تدخل بعد كسر الهيكل؟",
                       "إغلاق فوق آخر قمة هابطة.",
                       "العودة إلى المستوى المكسور نفسه.",
                       f"الدخول {S['ENT']:,.2f} والوقف {S['STP']:,.2f} تحت قاع شمعة النشأة.",
                       "الإبطال: إغلاق تحت المنطقة."],
                kw="كسر")

def bos_svg(D, x, y, slot):
    S = D["S"]; p = S["p"]; LH = S["LH"]; org = S["org"]
    _, pr, _, _, _, _ = plot_box(); R = CVW - pr
    lbl = htext(x(p + 6), y(LH) - 18, f"قمة هابطة {LH:,.2f}", tv_chart.T["LVL"], 25)
    ex = [line_el(x(p - 5), y(LH), R, y(LH), tv_chart.T["LVL"], 2.2, id="lvl"),
          f'<g id="lvllbl" opacity="0">{lbl}</g>',
          # المنطقة هي شمعة النشأة نفسها — آخر شمعة هابطة قبل الكسر — لا مربع مفترض
          zone_el("zn", x(org) - slot * .6, y(S["ZT"]), x(S["fill"]) + slot * 1.6, y(S["ZB"]), ""),
          f'<g id="znlbl" opacity="0">{htext(x(org + 7), y(S["ZB"]) + 34, "شمعة النشأة", TEAL_D, 24)}</g>']
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
    ex.append(checkmark(x(S["hit"]), y(S["TGT"]) - 40, id="ck"))
    fullset = fullset + ["box", "ck"]

    t_lvl, t_sig = D["t_lvl"], D["t_sig"]
    t_box = round(max(t_sig + 1.3, 10.2), 2)
    t_ck = 16.0
    marks = [(drawset[0], t_lvl, t_lvl + 0.5, "draw")]
    if key == "sweep":
        marks += [("lvllbl", t_lvl + 0.55, t_lvl + 0.8, "pop"),
                  ("swp", t_sig, t_sig + 0.4, "drawx"),
                  ("swplbl", t_sig + 0.45, t_sig + 0.7, "pop", t_box - 0.2, .3)]
    elif key == "fvg":
        marks = [("gap", t_lvl, t_lvl + 0.7, "zone"),
                 ("gaplbl", t_lvl + 0.75, t_lvl + 1.0, "pop", t_box - 0.2, .3),
                 ("ce", t_sig, t_sig + 0.5, "draw"),
                 ("celbl", t_sig + 0.55, t_sig + 0.8, "pop", t_box - 0.2, .3)]
    else:
        marks += [("lvllbl", t_lvl + 0.55, t_lvl + 0.8, "pop", t_sig - 0.2, .3),
                  ("zn", t_sig, t_sig + 0.7, "zone"),
                  ("znlbl", t_sig + 0.75, t_sig + 1.0, "pop", t_box - 0.2, .3)]
    marks += [("box", t_box, t_box + 1.5, "posbox"), ("ck", t_ck, t_ck + 0.3, "pop")]

    # نصوص البيتات تتبع أزمان الشموع، بحدّ أدنى للقراءة.
    # ربط بداية البيت الثاني بزمن رسم المستوى تركه ٠٫٦٥ ثانية على الشاشة في
    # نموذج الكنس — لا تُقرأ. النص يبدأ قبل الماركب ويبقى بعده.
    b2s = round(max(2.2, min(3.4, t_sig - 2.2)), 2)
    b_ = [(0.10, b2s - 0.15, 46), (b2s, t_sig - 0.15, 42),
          (t_sig, t_box - 0.15, 42), (t_box, 15.30, 40), (15.50, 18.40, 40)]
    assert all(b - a >= 1.7 for a, b, _ in b_[:4]), f"بيت أقصر من حدّ القراءة: {b_}"
    B = D["beats"]

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
        dom_marks=[["st1", b2s, b2s + 0.3, t_box - 0.3, .3],
                   ["st2", t_box, t_box + 0.3, 15.3, .3],
                   ["st3", 15.5, 15.8, 18.4, .3]],
        preview_a=0.0, preview_b=0.0, res_tease=False, sweep_op=0.0, flash_op=0.0,
        txt=[(f"t{i+1}", a, b, B[i], fs, INK) for i, (a, b, fs) in enumerate(b_)],
        chip="", res="", cta_k=f"اكتب «{D['kw']}»", cta_s="ويصلك الشرح كاملاً",
        edu=f'{S["sym"]} · {TFN[S["tf"]]} · {S["date"]} — لغرض تعليمي',
        dur=DUR, res_t=999, cta_t=18.6,
        flash=(999, 999.1), punch=(999, 999.1, 0.0),
        # الكاميرا ثابتة: شاشة المنصة لا تتجوّل، وأي تكبير يقصّ محور السعر
        cam=[[0.00, 1.0, .5, .5], [DUR, 1.0, .5, .5]],
    )
    out = out or f"reel26_{key}_{THEME}.html"
    n = build_reel(cfg, os.path.join(HERE, out))
    print(f'{key:<6} {S["sym"]} {S["tf"]:<4} {S["date"]} | شموع {N} | '
          f'بيتات {[round(a,2) for a,_,_ in b_]} | مستوى {t_lvl}s إشارة {t_sig}s | {n} bytes')
    return D


if __name__ == "__main__":
    import sys
    for k in (sys.argv[1:] or list(MODELS)):
        build(k)
