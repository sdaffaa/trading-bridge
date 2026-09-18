# -*- coding: utf-8 -*-
"""إعادة مونتاج ريل «التعادل» — نسخة سريعة 12.4ث برفع الاحتفاظ.
النتيجة أولاً ← رجوع بصري ← الدخول ← القرار ← السبب ← الضربة والانطلاق ← الخلاصة ← CTA.
حركة السعر مطابقة 100% لريل التعادل الأصلي (البذرة والمراسي نفسها، بلا شمعة واحدة مضافة
أو محذوفة). ما تغيّر هو الكاميرا والقطع والتجميد والوسوم فقط.
"""
import os
from reel_build import INK, TEAL, TEAL_D, RED, GREY, htext, gen
from reel_sfx_kit import build_reel, geom, line_el, xmark, checkmark, zone_el, set_canvas
from car_common import GEM

# مساحة رسم أطول: الجارت يشغل ~68% من الشاشة بدل 43% (الفراغ السفلي كان يقتل الافتتاحية)
CVW, CVH = 1080, 1300
set_canvas(CVW, CVH)

HERE = os.path.dirname(os.path.abspath(__file__))

# ── بيانات الصفقة: نسخة طبق الأصل من day3_build._be_data (بلا تسجيل جديد،
#    لأن إعادة الاستعمال المتعمّدة للصفقة نفسها هي شرط البريف لا مخالفة له) ──
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

# ── النصوص ──
# الهوك بنص فهد الحرفي (كويتي، مُعتمد في البريف للغلاف والافتتاحية معاً)
HOOK = 'تأمينك للصفقة<br><span style="color:#43D4DC">أخرجك</span> بدري.'
L = [HOOK,
     "لنعد إلى البداية.",
     "دخلت، وتحرك السعر لصالحك.",
     "فنقلت الوقف إلى التعادل.",
     "لكن وقفك كان داخل التصحيح الطبيعي.",
     "أخرجك… ثم أكمل الاتجاه."]
RES = "لا تنقل الوقف لمجرد ربح بسيط.<br><span class='rs2'>اربطه بشرط واضح في خطتك.</span>"
CTA_S = "ويصلك الشرح كاملاً"

def build(out="reel_be_fast.html"):
    W, ENT, LOW2, RNG = be_data()
    x, y, slot = geom(W)
    beX0, beX1 = x(IENT) - slot * 0.6, x(N - 1) + slot * 0.5
    ex = []

    # ── طبقة المشهد الأول: النتيجة ظاهرة من الفريم صفر ثم تختفي عند الرجوع ──
    ex.append(f'<g id="be0" opacity="0">'
              f'<rect x="{beX0:.1f}" y="{y(ENT)-3:.1f}" width="{beX1-beX0:.1f}" height="6" '
              f'fill="{RED}" opacity="0.34"/></g>')
    ex.append(xmark(x(IDIP), y(ENT) + 6, id="hit0", r=17))
    ex.append(f'<g id="run0" opacity="0">{htext(x(29), y(W[29]["h"]) - 30, "ثم انطلق", TEAL_D, 26)}</g>')

    # ── طبقة الشرح ──
    ex.append(line_el(beX0, y(ENT), beX1, y(ENT), INK, 2.4, id="ent"))
    ex.append(f'<g id="entlbl" opacity="0">{htext(x(14), y(ENT) - 20, "نقطة الدخول", INK, 24)}</g>')
    ex.append(f'<g id="be" opacity="0">'
              f'<rect x="{beX0:.1f}" y="{y(ENT)-3:.1f}" width="{beX1-beX0:.1f}" height="6" '
              f'fill="{RED}" opacity="0.34"/>'
              + htext(x(24), y(ENT) - 46, "الوقف = الدخول", RED, 24) + '</g>')
    # منطقة التصحيح الطبيعي: من القاع الأعلى إلى ما تحت خط التعادل بقليل
    ex.append(zone_el("cz", x(IDIP - 4) - slot * 0.6, y(LOW2 + RNG * 0.012),
                      x(IDIP + 1) + slot * 0.6, y(ENT - RNG * 0.035),
                      htext(x(IDIP - 2), y(ENT) + 74, "تصحيح طبيعي", TEAL_D, 24)))
    ex.append(xmark(x(IDIP), y(ENT) + 6, id="hit", r=17))
    ex.append(f'<g id="hitlbl" opacity="0">'
              f'{htext(x(IDIP) - slot * 3.4, y(ENT) + 52, "أخرجك", RED, 25)}</g>')
    ex.append(f'<g id="trail" opacity="0">'
              f'<path d="M {x(22):.0f} {y(W[22]["c"]):.0f} Q {x(27):.0f} {y(W[26]["c"]):.0f} '
              f'{x(32):.0f} {y(W[32]["c"])-14:.0f}" fill="none" stroke="{TEAL_D}" stroke-width="4" '
              f'stroke-linecap="round" opacity="0.85"/>'
              f'<polygon points="{x(32):.0f},{y(W[32]["c"])-20:.0f} {x(32)-16:.0f},{y(W[32]["c"])+2:.0f} '
              f'{x(32)+9:.0f},{y(W[32]["c"])+6:.0f}" fill="{TEAL_D}"/></g>')
    ex.append(checkmark(x(31), y(W[31]["c"]) - 34, id="ck"))

    fx = lambda i: x(i) / 1000
    fy = lambda p: y(p) / 820
    HITX, HITY = fx(IDIP), fy(ENT)
    # مركز اللقطة الافتتاحية = منتصف الشموع الظاهرة فعلاً عند الفريم صفر،
    # لا سعر الوقف — وإلا وقع الكادر تحت الشموع وترك النصف السفلي فارغاً
    def pose(j, cs, back=14, margin=0.055):
        """تأطير «شارت حيّ»: أحدث شمعة مكشوفة قرب الحافة اليمنى، والكادر ممتلئ
        بالشموع المرسومة فعلاً — بلا فراغ يمين ولا فراغ أسفل."""
        lim = (cs - 1) / (2 * cs)
        cx = min(max(x(j) / CVW - lim + margin, 0.5 - lim), 0.5 + lim)
        lo_i = max(0, j - back)
        hi = max(W[k]["h"] for k in range(lo_i, j + 1))
        lo = min(W[k]["l"] for k in range(lo_i, j + 1))
        # الكادر يميل نحو أعلى نطاق السعر: أسفل النافذة أسعار لا شموع فيها
        cy = min(max(fy(lo + (hi - lo) * 0.70), 0.5 - lim), 0.5 + lim)
        return [round(cx, 4), round(cy, 4)]

    EXTRA_CSS = f"""
.hl{{top:132px;left:56px;right:56px;line-height:1.20}}
#chartwrap{{top:300px;left:0}}
#chip{{top:214px;right:44px;font-size:22px;padding:6px 14px;border-width:1.6px}}
#res{{top:1500px;font-size:46px}}
#cta{{top:1676px}}
#cta .k{{font-size:50px;padding:12px 38px}}
#cta .s{{margin-top:12px;font-size:30px}}
#edu{{bottom:38px;font-size:20px;opacity:.62}}
#endlogo{{display:none}}   /* الشعار الدائم أعلى الشاشة يغني عنه */
#brand{{position:absolute;top:52px;left:0;right:0;text-align:center;z-index:7;opacity:.82}}
#brand .g{{width:34px;margin:0 auto}} #brand .g svg{{width:34px;height:auto}}
#brand .w{{margin-top:5px;font-size:15px;font-weight:800;letter-spacing:6px;color:#7F97A1}}
"""
    EXTRA_HTML = f'<div id="brand"><div class="g">{GEM}</div><div class="w">LIQUIDITY STATE</div></div>'

    cfg = dict(
        w=W, dark=True, extra_css=EXTRA_CSS, extra_html=EXTRA_HTML,
        # الحدث يقع أمام العين: 0..17 ظاهرة عند البداية (السعر يقترب من خط التعادل)،
        # ثم 18–19 اقتراب، 20 تلمس الخط، 21–33 الانطلاق — كله ينتهي عند 0.80ث
        base=IDIP - 3, openmax=N, open_t=[[N - 1, 0.30]],
        story=([(18, 0.05), (19, 0.17), (20, 0.29)] +
               [(j, round(0.44 + (j - 21) * 0.030, 3)) for j in range(21, N)]),
        extra_svg="".join(ex),
        marks=[
            # م1 — خط التعادل موجود من الفريم صفر، والعلامة تُرسم لحظة اللمس
            ["be0",  -0.20, -0.05, "pop",  1.45, 0.22],
            ["hit0",  0.31,  0.46, "drawx", 1.30, 0.20],
            ["run0",  0.62,  0.76, "pop",  1.30, 0.20],
            # م3 — الدخول
            ["ent",   1.75, 2.10, "draw"],
            ["entlbl", 2.15, 2.35, "pop", 4.50, 0.30],
            # م4 — القرار
            ["be",    3.45, 3.70, "pop"],
            # م5 — السبب
            ["cz",    4.85, 5.20, "zone", 8.25, 0.35],
            # م6 — الضربة والانطلاق (إعادة اللقطة مع الشرح كاملاً)
            ["hit",   6.60, 6.85, "drawx"],
            ["hitlbl", 6.90, 7.10, "pop", 8.25, 0.35],
            ["trail", 7.30, 7.65, "pop"],
            ["ck",    7.85, 8.05, "pop"],
        ],
        fullset=["be0", "hit0", "run0", "entlbl", "be", "cz", "hit", "hitlbl", "trail", "ck"],
        drawset=["ent"],
        preview_a=0.0, preview_b=0.0,   # نافذة معاينة الفريم-0 (لريلات 22ث) مُعطّلة هنا
        res_tease=False,          # تمهيد الخلاصة عند الثانية 1.3 مصمَّم لريل 22ث — يُطفأ هنا
        sweep_op=0.09, flash_op=0.11,   # الوميض والكنسة خافتان جداً: ممنوع تغطية الشموع
        txt=[(f"t{i+1}", a, b, L[i], fs, INK) for i, (a, b, fs) in enumerate(
            [(-0.25, 1.22, 44), (1.28, 1.92, 44), (2.00, 3.30, 42),
             (3.40, 4.70, 42), (4.80, 6.45, 40), (6.55, 8.15, 44)])],
        chip="التعادل · لغرض تعليمي",
        res=RES, cta_k="اكتب «تعادل»", cta_s=CTA_S,
        edu="لغرض تعليمي — مثال تخطيطي",
        dur=12.4, res_t=8.25, cta_t=10.0,
        flash=(6.60, 7.00), punch=(6.55, 7.35, 0.055), punch_origin="55% 50%",
        # الكاميرا مقيَّدة بحدود الجارت (lim=(cs-1)/2cs)، فمركز كل لقطة يُختار
        # بحيث يقع الحدث داخل الكادر لا خارجه
        cam=[
            # مقاييس مرتفعة عمداً: كلما زاد التكبير اتسع حدّ التمركز lim=(cs-1)/2cs،
            # فيصير بالإمكان إنزال الكادر إلى منطقة الوقف بدل ترك فراغ أسفلها
            [0.00, 2.20] + pose(17, 2.20),                           # اقتراب
            [0.26, 2.24] + pose(20, 2.24) + ["ramp"],                # زوم على منطقة الوقف
            [0.52, 2.18] + pose(25, 2.18) + ["ss"],                  # اللمس ثم أول الانطلاق
            [0.82, 1.95] + pose(33, 1.95) + ["whip", -0.7],          # سناب مع الانطلاق
            [1.22, 1.93] + pose(33, 1.93) + ["ss"],                  # تجميد على النتيجة
            [1.90, 1.98, fx(12), HITY, "whip", 0.8],                 # رجوع إلى الدخول
            [3.25, 1.82, fx(15), HITY, "creep"],
            [4.70, 1.70, fx(18), HITY, "ramp"],
            [6.45, 2.14, HITX, HITY, "anticip"],
            [7.00, 2.08, HITX, HITY, "ss"],
            [8.15, 1.66, fx(28), fy(W[28]["c"]), "whip", -0.9],
            [9.95, 1.34, .5, .54, "creep"],
            [11.35, 1.46, fx(23), HITY, "creep"],
            [12.40, 2.10, fx(21), HITY, "creep"],
        ],
    )
    n = build_reel(cfg, os.path.join(HERE, out))
    print("be-fast reel:", n, "| dur", cfg["dur"], "| cta", cfg["cta_t"])
    return cfg

if __name__ == "__main__":
    build()
