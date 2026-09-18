# -*- coding: utf-8 -*-
"""ريل تعليمي أكاديمي — «متى يُنقل الوقف إلى التعادل؟» (22ث · سبعة مشاهد).
منهج ملاحظة ← تفسير ← قاعدة: الشارت يتكشّف ببطء أمام المشاهد، ولافتة المرحلة
تخبره أين هو من الشرح. لا وميض ولا اهتزاز ولا مطاردة — الحركة تخدم الفهم فقط.
حركة السعر هي نفسها صفقة التعادل (البذرة 6301 والمراسي نفسها).
"""
import os
from reel_build import INK, TEAL, TEAL_D, RED, GREY, MUTE, htext, gen
from reel_sfx_kit import build_reel, geom, line_el, xmark, checkmark, zone_el, set_canvas
from car_common import GEM

CVW, CVH = 1080, 1300
set_canvas(CVW, CVH)

HERE = os.path.dirname(os.path.abspath(__file__))
SEED, N = 6301, 34
ANCH = [(0, 13.4), (4, 12.2), (8, 11.6), (11, 12.0), (15, 13.4), (18, 12.9),
        (21, 13.7), (25, 15.0), (33, 16.6)]
IENT, IDIP = 11, 20

def be_data():
    W = gen(ANCH, N, SEED, wick=0.8)
    rng = max(c["h"] for c in W) - min(c["l"] for c in W)
    ENT = W[IENT]["c"]
    for j in range(IENT + 1, IDIP):
        W[j]["l"] = max(W[j]["l"], ENT + rng * 0.015)
        W[j]["o"] = max(W[j]["o"], W[j]["l"]); W[j]["c"] = max(W[j]["c"], W[j]["l"])
        W[j]["h"] = max(W[j]["h"], max(W[j]["o"], W[j]["c"]) + rng * 0.01)
    LOW2 = ENT + rng * 0.055
    W[IDIP - 1]["l"] = LOW2
    W[IDIP - 1]["c"] = max(W[IDIP - 1]["c"], LOW2 + rng * 0.01)
    W[IDIP].update(o=W[IDIP - 1]["c"], c=ENT - rng * 0.012,
                   h=W[IDIP - 1]["c"] + rng * 0.01, l=ENT - rng * 0.03)
    prev = W[IDIP]["c"]
    for i, j in enumerate(range(IDIP + 1, N)):
        step = rng * (0.085 if i < 5 else 0.03)
        W[j].update(o=prev, c=prev + step, h=prev + step + rng * 0.02, l=prev - rng * 0.012)
        prev = W[j]["c"]
    return W, ENT, LOW2, rng

# ── سبعة مشاهد: سطر واحد لكل مشهد، فكرة واحدة، أقل من ثانية ونصف قراءةً ──
L = ["متى يُنقل الوقف إلى التعادل؟",
     "صفقة شراء تحركت لصالحك.",
     "فنقلت الوقف إلى سعر الدخول.",
     "لكن السعر لم ينعكس… بل صحّح.",
     "التصحيح مرّ بدخولك ثم واصل الاتجاه.",
     "القاعدة: انقله خلف قاع أعلى."]
RES = ("التعادل قرار هيكلي،<br>"
       "<span class='rs2'>لا مكافأة على ربح بسيط.</span>")
CTA_S = "ويصلك الشرح كاملاً"

def build(out="reel_academic.html"):
    W, ENT, LOW2, RNG = be_data()
    x, y, slot = geom(W)
    fx = lambda i: x(i) / CVW
    fy = lambda p: y(p) / CVH
    beX0, beX1 = x(IENT) - slot * 0.6, x(N - 1) + slot * 0.5
    ex = []

    # الدخول
    ex.append(line_el(beX0, y(ENT), beX1, y(ENT), INK, 2.4, id="ent"))
    ex.append(f'<g id="entlbl" opacity="0">{htext(x(14), y(ENT) - 22, "الدخول", INK, 26)}</g>')
    # نقل الوقف إلى الدخول
    ex.append(f'<g id="be" opacity="0">'
              f'<rect x="{beX0:.1f}" y="{y(ENT)-3.5:.1f}" width="{beX1-beX0:.1f}" height="7" '
              f'fill="{RED}" opacity="0.36"/></g>')
    ex.append(f'<g id="belbl" opacity="0">'
              f'{htext(x(16), y(ENT) - 50, "الوقف = الدخول", RED, 26)}</g>')
    # نطاق التصحيح الطبيعي
    ex.append(zone_el("cz", x(IDIP - 5) - slot * 0.6, y(LOW2 + RNG * 0.015),
                      x(IDIP + 1) + slot * 0.6, y(ENT - RNG * 0.04),
                      htext(x(IDIP - 2), y(ENT) + 84, "نطاق التصحيح الطبيعي", TEAL_D, 25)))
    # الخروج
    ex.append(xmark(x(IDIP), y(ENT) + 6, id="hit", r=18))
    ex.append(f'<g id="hitlbl" opacity="0">'
              f'{htext(x(IDIP) - slot * 3.6, y(ENT) + 54, "خروج", RED, 26)}</g>')
    # الاستمرار
    ex.append(f'<g id="cont" opacity="0">{htext(x(28), y(W[28]["h"]) - 34, "ثم واصل", TEAL_D, 26)}</g>')
    # القاعدة: قاع أعلى والوقف خلفه
    ex.append(line_el(x(IDIP - 4) - slot * 0.6, y(LOW2), beX1, y(LOW2), TEAL_D, 2.2,
                      dash="6 6", id="hh"))
    ex.append(f'<g id="hhlbl" opacity="0">'
              f'{htext(x(20), y(LOW2) - 18, "قاع أعلى — الوقف خلفه", TEAL_D, 26)}</g>')
    ex.append(checkmark(x(31), y(W[31]["c"]) - 36, id="ck"))

    def pose(j, cs, back=16, margin=0.06):
        """تأطير هادئ: أحدث شمعة مكشوفة قرب الحافة، والكادر ممتلئ بما رُسم فعلاً."""
        lim = (cs - 1) / (2 * cs)
        cx = min(max(x(j) / CVW - lim + margin, 0.5 - lim), 0.5 + lim)
        lo_i = max(0, j - back)
        hi = max(W[k]["h"] for k in range(lo_i, j + 1))
        lo = min(W[k]["l"] for k in range(lo_i, j + 1))
        cy = min(max(fy(lo + (hi - lo) * 0.70), 0.5 - lim), 0.5 + lim)
        return [round(cx, 4), round(cy, 4)]

    EXTRA_CSS = """
.hl{top:150px;left:60px;right:60px;line-height:1.22}
#chartwrap{top:340px;left:0}
#chip{display:none}
#res{top:1512px;font-size:44px}
#cta{top:1690px}
#cta .k{font-size:48px;padding:11px 36px}
#cta .s{margin-top:11px;font-size:29px}
#edu{bottom:36px;font-size:20px;opacity:.58}
#endlogo{display:none}
#brand{position:absolute;top:50px;left:0;right:0;text-align:center;z-index:7;opacity:.78}
#brand .g{width:32px;margin:0 auto} #brand .g svg{width:32px;height:auto}
#brand .w{margin-top:5px;font-size:14px;font-weight:800;letter-spacing:6px;color:#7F97A1}
.step{position:absolute;top:262px;right:60px;z-index:7;opacity:0;
  border:1.8px solid #3AAFC0;color:#43D4DC;font-size:26px;font-weight:800;
  padding:7px 22px;letter-spacing:.5px;background:rgba(67,212,220,.06)}
.step i{font-style:normal;color:#7F97A1;margin-left:10px}
#prog{position:absolute;top:288px;left:60px;width:190px;height:3px;z-index:7;
  background:rgba(255,255,255,.10)}
#prog b{position:absolute;inset:0 auto 0 0;background:#43D4DC;display:block;width:0}
"""
    EXTRA_HTML = (f'<div id="brand"><div class="g">{GEM}</div>'
                  f'<div class="w">LIQUIDITY STATE</div></div>'
                  '<div class="step" id="st1"><i>١</i>ملاحظة</div>'
                  '<div class="step" id="st2"><i>٢</i>تفسير</div>'
                  '<div class="step" id="st3"><i>٣</i>قاعدة</div>')

    cfg = dict(
        w=W, dark=True, extra_css=EXTRA_CSS, extra_html=EXTRA_HTML,
        # تكشّف بطيء مقصود: المشاهد يرى الصفقة تتكوّن، لا صورة جاهزة
        base=IENT, openmax=N, open_t=[[N - 1, 0.45]],
        story=([(j, round(2.75 + (j - IENT - 1) * 0.30, 2)) for j in range(IENT + 1, IDIP)] +
               [(IDIP, 10.55)] +
               [(j, round(11.35 + (j - IDIP - 1) * 0.135, 2)) for j in range(IDIP + 1, N)]),
        extra_svg="".join(ex),
        marks=[
            ["ent",   2.80, 3.25, "draw"],
            ["entlbl", 3.30, 3.55, "pop", 14.40, 0.30],
            ["be",    7.05, 7.40, "pop"],
            ["belbl", 7.15, 7.45, "pop", 14.40, 0.30],
            ["cz",   10.85, 11.30, "zone", 14.40, 0.35],
            ["hit",  10.60, 10.95, "drawx"],
            ["hitlbl", 11.00, 11.25, "pop", 14.40, 0.30],
            ["cont", 12.90, 13.20, "pop", 14.40, 0.30],   # يختفي قبل مشهد القاعدة حتى لا يُقصّ عند الحافة
            ["hh",   14.70, 15.20, "draw"],
            ["hhlbl", 15.25, 15.55, "pop"],
            ["ck",   16.20, 16.50, "pop"],
        ],
        fullset=["entlbl", "be", "belbl", "cz", "hit", "hitlbl", "cont", "hhlbl", "ck"],
        drawset=["ent", "hh"],
        dom_marks=[["st1", 2.70, 3.00, 10.10, 0.30],     # ملاحظة
                   ["st2", 10.30, 10.60, 14.35, 0.30],   # تفسير
                   ["st3", 14.55, 14.85, 18.10, 0.30]],  # قاعدة
        preview_a=0.0, preview_b=0.0,
        res_tease=False, sweep_op=0.0, flash_op=0.0,
        txt=[(f"t{i+1}", a, b, L[i], fs, INK) for i, (a, b, fs) in enumerate(
            [(0.10, 2.55, 50), (2.70, 6.85, 44), (7.00, 10.15, 44),
             (10.30, 12.75, 44), (12.90, 14.40, 42), (14.55, 18.05, 46)])],
        chip="", res=RES, cta_k="اكتب «تعادل»", cta_s=CTA_S,
        edu="لغرض تعليمي — مثال تخطيطي",
        dur=22.0, res_t=18.15, cta_t=20.0,
        flash=(999, 999.1), punch=(999, 999.1, 0.0),
        cam=[
            [0.00, 1.46] + pose(IENT, 1.46),                    # لقطة سياق واسعة
            [2.60, 1.50] + pose(IENT, 1.50) + ["creep"],
            [5.20, 1.62] + pose(17, 1.62) + ["creep"],          # ملاحظة: الحركة لصالحك
            [7.00, 1.74] + pose(19, 1.74) + ["creep"],          # القرار
            [10.20, 1.92] + pose(19, 1.92) + ["creep"],         # تقريب قبل التصحيح
            [11.10, 1.94] + pose(IDIP, 1.94) + ["ss"],          # لحظة الخروج
            [13.60, 1.66] + pose(29, 1.66) + ["creep"],         # الاستمرار
            [15.00, 1.76] + pose(23, 1.76) + ["creep"],         # القاعدة: القاع الأعلى
            [18.10, 1.40, .5, .54, "creep"],                    # خلاصة
            [20.00, 1.26, .5, .52, "creep"],
            [22.00, 1.30, .5, .52, "creep"],
        ],
    )
    n = build_reel(cfg, os.path.join(HERE, out))
    print("academic reel:", n, "| dur", cfg["dur"], "| cta", cfg["cta_t"])
    return cfg

if __name__ == "__main__":
    build()
