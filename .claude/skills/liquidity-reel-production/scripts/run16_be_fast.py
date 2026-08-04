# -*- coding: utf-8 -*-
"""إعادة مونتاج ريل «التعادل» — نسخة سريعة 12.4ث برفع الاحتفاظ.
النتيجة أولاً ← رجوع بصري ← الدخول ← القرار ← السبب ← الضربة والانطلاق ← الخلاصة ← CTA.
حركة السعر مطابقة 100% لريل التعادل الأصلي (البذرة والمراسي نفسها، بلا شمعة واحدة مضافة
أو محذوفة). ما تغيّر هو الكاميرا والقطع والتجميد والوسوم فقط.
"""
import os
from reel_build import INK, TEAL, TEAL_D, RED, GREY, htext, gen
from reel_sfx_kit import build_reel, geom, line_el, xmark, checkmark, zone_el

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

# ── النصوص (فصحى — دستور V2) ──
L = ["خرجت عند التعادل… ثم انطلق السعر.",
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

    cfg = dict(
        w=W, dark=True,
        base=N, openmax=N, open_t=[], story=[],      # الشارت كامل من الفريم صفر
        extra_svg="".join(ex),
        marks=[
            # م1 — الصدمة
            # قيم سالبة متعمّدة: الهوك والوسم مكتملان في الفريم صفر بلا أي ظهور تدريجي
            ["be0",  -0.20, -0.05, "pop",  1.28, 0.22],
            ["hit0", -0.20,  0.10, "drawx", 1.02, 0.20],
            ["run0",  0.52,  0.70, "pop",  1.02, 0.20],
            # م3 — الدخول (يبدأ الخط أثناء الرجوع حتى لا تبقى لقطة خالية)
            ["ent",   1.50, 1.90, "draw"],
            ["entlbl", 1.95, 2.15, "pop", 4.30, 0.30],
            # م4 — القرار
            ["be",    3.25, 3.50, "pop"],
            # م5 — السبب
            ["cz",    4.70, 5.05, "zone", 8.15, 0.35],
            # م6 — الضربة والانطلاق
            ["hit",   6.55, 6.80, "drawx"],
            ["hitlbl", 6.85, 7.05, "pop", 8.15, 0.35],
            ["trail", 7.25, 7.60, "pop"],
            ["ck",    7.80, 8.00, "pop"],
        ],
        fullset=["be0", "hit0", "run0", "entlbl", "be", "cz", "hit", "hitlbl", "trail", "ck"],
        drawset=["ent"],
        preview_a=0.0, preview_b=0.0,   # نافذة معاينة الفريم-0 (لريلات 22ث) مُعطّلة هنا
        res_tease=False,          # تمهيد الخلاصة عند الثانية 1.3 مصمَّم لريل 22ث — يُطفأ هنا
        sweep_op=0.20,            # كنسة الضوء خافتة حتى لا تغطي الشموع
        txt=[(f"t{i+1}", a, b, L[i], fs, INK) for i, (a, b, fs) in enumerate(
            [(-0.25, 0.90, 52), (0.95, 1.65, 50), (1.75, 3.05, 48),
             (3.15, 4.45, 48), (4.55, 6.25, 46), (6.40, 8.05, 50)])],
        chip="التعادل · لغرض تعليمي",
        res=RES, cta_k="اكتب «تعادل»", cta_s=CTA_S,
        edu="لغرض تعليمي — مثال تخطيطي",
        dur=12.4, res_t=8.15, cta_t=10.0,
        flash=(6.55, 6.95), punch=(6.50, 7.30, 0.055), punch_origin="55% 50%",
        rflash=6.60,
        cam=[
            # م1: تكبير حاد على لحظة ضرب الوقف ثم تجميد قصير
            # ملاحظة: الكاميرا مقيَّدة بحدود الجارت (lim=(cs-1)/2cs)، فمركز اللقطة
            # يُختار بحيث تقع الضربة داخل الكادر لا خارجه
            [0.00, 1.95, fx(24), HITY],
            [0.55, 1.99, fx(26), fy(W[26]["c"]), "creep"],
            [0.88, 1.97, fx(26), fy(W[26]["c"]), "ss"],
            # م2: رجوع بصري سريع إلى الدخول
            [1.60, 1.85, fx(12), HITY, "whip", 0.8],
            # م3: زوم دقيق على الدخول
            [3.00, 1.62, fx(15), HITY, "creep"],
            # م4: توسيع بسيط ليظهر امتداد خط التعادل
            [4.45, 1.45, fx(18), HITY, "ramp"],
            # م5: اقتراب تدريجي مع اقتراب السعر من الوقف
            [6.35, 1.92, HITX, HITY, "anticip"],
            # م6: تتبع الانطلاق
            [6.95, 1.86, HITX, HITY, "ss"],
            [8.05, 1.42, fx(28), fy(W[28]["c"]), "whip", -0.9],
            # م7: خلاصة
            [9.90, 1.12, .5, .48, "creep"],
            # م8: CTA ثم عودة نحو لقطة البداية لإغلاق الحلقة
            [11.30, 1.20, fx(24), HITY, "creep"],
            [12.40, 1.95, HITX, HITY, "creep"],
        ],
    )
    n = build_reel(cfg, os.path.join(HERE, out))
    print("be-fast reel:", n, "| dur", cfg["dur"], "| cta", cfg["cta_t"])
    return cfg

if __name__ == "__main__":
    build()
