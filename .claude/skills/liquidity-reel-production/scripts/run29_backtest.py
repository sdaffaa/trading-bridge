# -*- coding: utf-8 -*-
"""تشغيلة ٢٩ — الصفقة كما تُعرض في باك تست تريدنق فيو: جارت ثابت، بلا زوم.

🔒 أمر فهد 2026-08-06: «اظهار الصفقة كأنها صفقة باك تست بتريدنق فيو بدون
   زومات عالجارت».

فُرِّغ `cam` كلياً — لا تكبير ولا تدوير ولا اهتزاز. الجارت كامل في الإطار
من أول ثانية إلى آخرها، كما يراه من يفتح المنصّة. الحركة تأتي من تكشّف
الشموع ومن ظهور الوسوم في وقتها، لا من عدسة تتجوّل.

لوحة الباك تست تُطبع من `backtest_stats.json` وحده — وهي مخرَج
`backtest.py` الذي يسجّل كل إشارة تجتاز الطبقات الخمس، الخاسرة قبل
الرابحة. لا يُكتب في هذه اللوحة رقمٌ باليد: نسبة ربحٍ مُختارة من الصفقات
الرابحة وحدها تصف المصفاة لا السوق.

بقيّة البناء (الطبقات، لوحات الفريمات، ماركب الخمس دقائق) مستوردة من
`run28_cinema` كما هي — نسخُها هنا يخلق مصدرين للحقيقة نفسها.
"""
import json, os

import run28_cinema as R
import tv_shell as TV
from reel_build import INK, TEAL_D, RED, htext
from reel_sfx_kit import build_reel
import tv_chart

HERE = os.path.dirname(os.path.abspath(__file__))
D, LAY, PLAN, M5 = R.D, R.LAY, R.PLAN, R.M5
FILL, HIT, DP, DK = R.FILL, R.HIT, R.DP, R.DK
TAG, THEME, CVW, CVH = R.TAG, R.THEME, R.CVW, R.CVH
X5, Y5, SLOT5 = R.X5, R.Y5, R.SLOT5
DUR = 30.0

BT = json.load(open(os.path.join(HERE, "backtest_stats.json"), encoding="utf-8"))
AR = {"GC=F": "ذهب", "SI=F": "فضة", "CL=F": "نفط", "BZ=F": "برنت",
      "NG=F": "غاز", "HG=F": "نحاس", "BTC-USD": "بتكوين", "ETH-USD": "إيثيريوم"}


# ═════════ وسوم الصفقة بأسلوب الباك تست ═════════
def trade_marks():
    """مثلّثا الدخول والخروج تحت الشمعتين — كما يرسمهما مُختبِر الاستراتيجية."""
    t = 15
    xe, ye = X5(FILL), Y5(M5[FILL]["l"])
    xx, yx = X5(HIT), Y5(PLAN["TGT"])
    # «شراء» يُسند إلى المثلّث نفسه، و«كَنْس» أُبعد يساراً في m5_svg — بلا
    # زوم كل الوسوم تتقارب، فالفصل يجب أن يكون في الإحداثيات لا في العدسة.
    # ووسم الخروج يُزاح يساراً كي لا يخرج من حدود الرسم عند الحافّة اليمنى.
    lx = min(xx, CVW - R.PR - 96)
    g = [f'<g id="btin" opacity="0">'
         f'<path d="M {xe:.1f} {ye+16:.1f} L {xe-t*.8:.1f} {ye+16+t:.1f} '
         f'L {xe+t*.8:.1f} {ye+16+t:.1f} Z" fill="{TEAL_D}"/>'
         + htext(xe + SLOT5 * 2.6, ye + 16 + t + 22, "شراء", TEAL_D, 23,
                 anchor="middle") + '</g>',
         f'<g id="btout" opacity="0">'
         f'<path d="M {xx:.1f} {yx-16:.1f} L {xx-t*.8:.1f} {yx-16-t:.1f} '
         f'L {xx+t*.8:.1f} {yx-16-t:.1f} Z" fill="{TEAL_D}"/>'
         + htext(lx, yx - 16 - t - 16, "خروج ٢R", TEAL_D, 23, anchor="middle") + '</g>']
    return "".join(g)


# ═════════ لوحة مُختبِر الاستراتيجية ═════════
def tester():
    pf = "∞" if BT["pf"] is None else f'{BT["pf"]:.2f}'
    cells = [("صافي الربح", f'+{BT["net"]:.2f}R', True),
             ("الصفقات المغلقة", f'{BT["n"]}', None),
             ("نسبة الربح", f'{BT["wr"]*100:.1f}%', None),
             ("عامل الربح", pf, BT["pf"] and BT["pf"] > 1),
             ("أطول سلسلة خسائر", f'{BT["maxdd"]}', False)]
    a, b = BT["span"][0][:10], BT["span"][1][:10]
    syms = [s for s, v in BT["per"].items() if v[0]]
    row = "".join(
        f'<div class="tc"><span>{k}</span>'
        f'<b class="{"up" if g else ("dn" if g is False else "")}">{v}</b></div>'
        for k, v, g in cells)
    return (f'<div id="tester"><div class="th">مُختبِر الاستراتيجية '
            f'<i>· نموذج الطبقات الخمس</i></div>'
            f'<div class="tr">{row}</div>'
            f'<div class="tn">{BT["n"]} صفقة على {len(syms)} أدوات · '
            f'<span dir="ltr">{a} → {b}</span> · كل إشارة مُسجَّلة، '
            f'رابحةً كانت أو خاسرة</div></div>')


SUB = "#8FA6AF" if DK else "#6B7C84"
PANEL = "#101E27" if DK else "#FBF9F5"
BD = "rgba(143,166,175,.30)" if DK else "rgba(15,46,60,.18)"

CSS = R.BASE_CSS + f"""
/* مُختبِر الاستراتيجية دوكٌ أسفل اللوحة كما في المنصّة — لا بطاقة عائمة. */
#tester{{position:absolute;top:1400px;left:{R.CX}px;right:0;opacity:0;z-index:9;background:{PANEL};border-top:2px solid {BD};box-shadow:0 -18px 44px rgba(0,0,0,{.34 if DK else .07});
     padding:18px 34px 20px}}
#tester .th{{font-size:25px;font-weight:800;color:{"#DCE9EE" if DK else "#0F2E3C"};margin-bottom:14px}}
#tester .th i{{font-style:normal;font-weight:600;font-size:21px;color:{SUB}}}
#tester .tr{{display:flex;justify-content:space-between;gap:10px}}
#tester .tc{{flex:1;text-align:center}}
#tester .tc span{{display:block;font-size:18px;font-weight:600;color:{SUB};margin-bottom:5px;line-height:1.25}}
#tester .tc b{{display:block;font-size:34px;font-weight:900;letter-spacing:-.4px;
           direction:ltr;color:{"#DCE9EE" if DK else "#0F2E3C"}}}
#tester .tc b.up{{color:{"#43D4DC" if DK else "#1E627A"}}}
#tester .tc b.dn{{color:{RED}}}
#tester .tn{{margin-top:15px;padding-top:12px;border-top:1px solid {BD};
         font-size:18px;font-weight:600;color:{SUB};line-height:1.5}}
"""

# 🔒 أمر فهد 2026-08-06: «كأني داخل تريدنق فيو أقوم بماركب، وليس كريلز».
# فالعناوين العائمة صارت ملاحظات على الجارت، ولوحة المُختبِر صارت دوكاً
# أسفل المنصّة كما هو مُختبِر الاستراتيجية فيها فعلاً.
XR = R.CX + R.CVW - R.PR - 18
_NT = [("القاع الذي انكسر لم يكن كسراً", "قاعان متساويان تحتهما أوامر إيقاف"),
       ("١ · اتجاه صاعد على الأربع ساعات", LAY[0]["detail"]),
       ("٢ · انحياز اليوم صاعد", LAY[1]["detail"]),
       ("٣ · هيكل استمراري على الساعة", LAY[2]["detail"]),
       ("٤ · سحب السيولة", LAY[3]["detail"]),
       ("٥ · إشارة الانعكاس", LAY[4]["detail"]),
       (f'الدخول {PLAN["ENT"]:,.{DP}f}',
        f'الوقف {PLAN["STP"]:,.{DP}f} · المخاطرة {PLAN["R"]:,.{DP}f} · '
        f'الهدف {PLAN["TGT"]:,.{DP}f}'),
       (f'الهدف ٢R تحقّق بعد {HIT-FILL} شمعات',
        "وهذه نتيجة النموذج نفسه على كل إشاراته")]
NOTES = "".join(TV.note_el(f"n{i}", 0, R.CY + 26, t, d, xr=XR)
                for i, (t, d) in enumerate(_NT))
NOTE_T = [(0.55, 5.90), (6.35, 9.10), (9.55, 12.20), (12.65, 15.45),
          (16.10, 18.90), (19.30, 21.90), (22.30, 25.30), (25.80, 29.40)]

MARKS = [
    ("lvl", 3.00, 3.70, "draw"),
    ("eq0", 3.70, 3.95, "pop"), ("eq1", 3.90, 4.15, "pop"),
    ("lvllbl", 4.20, 4.50, "pop"),
    ("tf4h", 6.05, 6.45, "fade", 9.00, .32),
    ("tf1d", 9.25, 9.65, "fade", 12.10, .32),
    ("tf1h", 12.35, 12.75, "fade", 15.35, .32),
    ("swp", 17.80, 18.20, "drawx"),
    ("swplbl", 18.20, 18.50, "pop"),
    ("wick", 19.20, 19.60, "fade"), ("wicklbl", 19.65, 19.95, "pop"),
    ("btin", 22.05, 22.45, "pop"),
    ("box", 22.25, 24.10, "posbox"),
    ("btout", 25.60, 25.95, "pop"),
]
FULLSET = ["eq0", "eq1", "lvllbl", "tf4h", "tf1d", "tf1h", "swp", "swplbl",
           "wick", "wicklbl", "btin", "box", "btout"]

BASE = FILL - 1
_after = [(FILL, 17.55), (FILL + 1, 19.10), (FILL + 2, 20.30), (HIT, 25.20)]
STORY = sorted({j: t for j, t in _after if j < len(M5)}.items()) + \
        [(j, round(25.70 + (j - HIT - 1) * 0.30, 2)) for j in range(HIT + 1, len(M5))]

cfg = dict(
    w=M5, dark=DK, extra_css=CSS, extra_html=R.BASE_HTML + NOTES + tester(), grid=False,
    pre_svg=tv_chart.furniture(M5, dec=DP, sym=D["sym"], tf="5m",
                               tlabels=[c["d"][11:] for c in M5]),
    lp_pill=True, lp_dec=DP, lp_col=tv_chart.T["PILL"], lp_txt=tv_chart.T["PILLTX"],
    base=BASE, openmax=len(M5), open_t=[[BASE, 0.4]], story=STORY,
    extra_svg=R.EX5 + trade_marks() + R.p_4h() + R.p_1d() + R.p_1h(),
    marks=MARKS, fullset=FULLSET, drawset=["lvl"],
    dom_marks=[[f"n{i}", a, a + 0.32, b, 0.28] for i, (a, b) in enumerate(NOTE_T)]
              + [["tester", 25.45, 25.90, 0, 0]],
    preview_a=0.0, preview_b=0.0, res_tease=False, sweep_op=0.0,
    txt=[],                       # لا عنوان عائم — الملاحظات على الجارت
    chip="", res="", cta_k="اكتب «باك تست»", cta_s="ويصلك سجلّ الصفقات كاملاً",
    edu=f'{D["sym"]} · ٥ دقائق · {D["anchor_utc"][:10]} — مثال تعليمي',
    dur=DUR, res_t=999, cta_t=DUR - 2.4,
    flash=(0.0, 0.0), flash_op=0.0, punch=(0.0, 0.0, 0.0),
    crosshair=True, chart_at=(R.CX, R.CY), tlabels=[c["d"][11:] for c in M5],
    cam=[],                       # ثابت: لا زوم ولا تدوير — أمر فهد
)

if __name__ == "__main__":
    n = build_reel(cfg, os.path.join(HERE, f"reel29_{TAG}_{THEME}.html"))
    print(f'{TAG} | باك تست | {DUR}s | جارت ثابت بلا كاميرا | '
          f'ماركب {len(MARKS)} | {n} bytes')
    print(f'  اللوحة: {BT["n"]} صفقة · ربح {BT["wr"]*100:.1f}٪ · '
          f'عامل {BT["pf"]:.2f} · صافي {BT["net"]:+.1f}R')
