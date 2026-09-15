# -*- coding: utf-8 -*-
"""جارتات تشغيلة ٦١ — ثلاثة قياسات لا يتشابه منها اثنان.

الوحدات الثلاث الكاروسيلية هنا ليست دروسَ دخول (درس ٥٨)، فمقاييسها
مستقلّة عن نماذج `run31_charts` السبعة: **مخاطرةٌ بحجم شمعة** على عقد
الجنيه · **وقفٌ يُقاس بالشمعة لا بالنقطة** على النيوزيلندي · و**ساعةٌ
تُقاس بما دفعته من انتظار** على البتكوين.

وكلّ دالّة تتحقّق من رقمها بـ`assert` قبل أن تُخرج SVG — والنافذة التي
لا يثبت عليها الرقم تكسر البناء ولا تُروى.

    python3 run61_charts.py
"""
import statistics as st

from reel_build import INK, TEAL, TEAL_D, RED, GREY, htext
from run15_charts import zbox, tick, hl, badge, frame
import run31_charts as RC
from run58_charts import ar, dd, rt, why, sm, band, mark, span, i_of, ranges
from run59_charts import tag, spanx, vspan, xr, _pt

BULL = "#2E8CA6"


def _g(r, Wd, H):
    return frame(r["w"], Wd, H)


def _plan(W, r):
    """الدخول والوقف بنفس حساب `run32_desk.plan_numbers` — لا حساباً آخر."""
    iob, ir = r["iob"], r["ir"]
    seg = W[:ir + 1]
    rng = max(c["h"] for c in seg) - min(c["l"] for c in seg)
    ent = W[ir]["c"]
    stp = min(W[j]["l"] for j in range(iob, ir + 1)) - rng * 0.006
    return ent, stp, ent - stp


def _hit(W, r, ent, risk):
    tgt = ent + 2 * risk
    return next((j for j in range(r["ir"] + 1, len(W)) if W[j]["h"] >= tgt), None)


def _clear(W, ent, lo_=4, hi_=7, pad=2):
    """عمودٌ لا تعبره شمعة فوق الدخول — موضعُ القوس الرأسي.

    والخلوّ يُقاس على **الجوار** لا على العمود وحده: الوسم أعرض من سلوت
    واحد (نحو خمسة)، فعمودٌ خالٍ بين عمودين مشغولين يضع الرقم فوق شمعة
    (رُصد 2026-09-06 على «١٫٠٢× الشمعة»). فيُختار العمود الذي أدنى قيعان
    جواره أبعد ما يكون فوق الدخول."""
    def clear_at(k):
        a, b = max(0, k - pad), min(len(W), k + pad + 1)
        return min(W[j]["l"] for j in range(a, b)) - ent
    j = max(range(lo_, len(W) - hi_), key=clear_at)
    assert clear_at(j) > 0, "لا موضع خالٍ للقوس وجواره"
    return j


# ═════════ ١ · مبلغ — عقد الجنيه الآجل · ساعة (النافذة ٥٥) ═════════


def m_risk(r, Wd=880, H=250):
    """مخاطرة الصفقة بحجم شمعةٍ واحدة — لا بحجم هدفك الشهري."""
    W = r["w"]
    ent, stp, risk = _plan(W, r)
    rg, med = ranges(W)
    k = risk / med
    assert 0.98 <= k <= 1.10, f"{k:.2f}"
    svg, x, y, slot = _g(r, Wd, H)
    svg += hl(x(0) - slot * .5, x(len(W) - 1) + slot * .5, y(ent), TEAL_D, 1.8)
    svg += hl(x(0) - slot * .5, x(len(W) - 1) + slot * .5, y(stp), RED, 1.8, "6 6")
    svg += band(x(0) - slot * .5, x(len(W) - 1) + slot * .5, y(ent), y(stp), TEAL, 0.10)
    svg += vspan(x(_clear(W, ent)), y(ent), y(stp), f'{xr(k)} الشمعة', TEAL_D, H=H)
    svg += RC._title(Wd, rt("مخاطرتك بحجم شمعة"))
    svg += why(Wd, H, f'من ⁦{ent:.5f}⁩ إلى ⁦{stp:.5f}⁩ — {xr(k)} وسيط الشمعة', INK)
    svg += sm(Wd, H, "وهذي المسافة يحدّدها السوق، لا الرقم الذي كتبته لنفسك", TEAL_D)
    return svg + badge(Wd, "مخاطرة بالشمعة", True) + "</svg>"


def m_wait(r, Wd=880, H=250):
    """عشرون ساعة بين الكسر والدخول — والهدف الشهري لا يقصّرها."""
    W = r["w"]; bk, ir = r["bk"], r["ir"]
    assert ir - bk == 20, f"{ir-bk}"
    svg, x, y, slot = _g(r, Wd, H)
    svg += mark(x(bk), slot, y(W[bk]["h"]), y(W[bk]["l"]), TEAL_D, 0.24)
    svg += mark(x(ir), slot, y(W[ir]["h"]), y(W[ir]["l"]), TEAL_D, 0.20)
    top = min(y(W[k]["h"]) for k in range(bk, ir + 1))
    svg += spanx(x(bk) - slot * .5, x(ir) + slot * .5, top, f'{ar(ir-bk)} ساعة', TEAL_D)
    svg += RC._title(Wd, rt("عشرون ساعة انتظار"))
    svg += why(Wd, H, f'الكسر {dd(W[bk]["d"])} والدخول {dd(W[ir]["d"])} — {ar(ir-bk)} ساعة', TEAL_D)
    svg += sm(Wd, H, "ومن يستعجل الرقم يدخل في مكانٍ من هالعشرين لا في آخرها")
    return svg + badge(Wd, "زمن الانتظار", True) + "</svg>"


def m_mae(r, Wd=880, H=250):
    """السوق أخذ تسعة وعشرين بالمئة من الوقف ثم مضى."""
    W = r["w"]; ir = r["ir"]
    ent, stp, risk = _plan(W, r)
    hit = _hit(W, r, ent, risk)
    j = min(range(ir + 1, hit + 1), key=lambda k: W[k]["l"])
    frac = (ent - W[j]["l"]) / risk
    assert 0.27 <= frac <= 0.32, f"{frac:.2f}"
    svg, x, y, slot = _g(r, Wd, H)
    svg += hl(x(0) - slot * .5, x(len(W) - 1) + slot * .5, y(ent), TEAL_D, 1.8)
    svg += hl(x(0) - slot * .5, x(len(W) - 1) + slot * .5, y(stp), RED, 1.6, "6 6")
    svg += mark(x(j), slot, y(W[j]["h"]), y(W[j]["l"]), GREY, 0.26)
    svg += vspan(x(j), y(ent), y(W[j]["l"]), f'{ar(round(frac*100))}٪', GREY, H=H)
    svg += RC._title(Wd, rt("ما أخذه منك السوق"))
    svg += why(Wd, H, f'أبعد نزول ⁦{W[j]["l"]:.5f}⁩ — {ar(round(frac*100))}٪ من مخاطرتك', GREY)
    svg += sm(Wd, H, "والوقف بقي سليماً — الحركة ضدّك أصغر ممّا يقوله الرصيد", TEAL_D)
    return svg + badge(Wd, "انحراف مقيس", True) + "</svg>"


def m_span(r, Wd=880, H=250):
    """مدى النافذة كلّها يساوي إحدى عشرة مخاطرة — لا مبلغاً."""
    W = r["w"]
    ent, stp, risk = _plan(W, r)
    lo = min(c["l"] for c in W); hi = max(c["h"] for c in W)
    k = (hi - lo) / risk
    assert 10.5 <= k <= 11.6, f"{k:.2f}"
    svg, x, y, slot = _g(r, Wd, H)
    L = x(0) - slot * .5; Rt = x(len(W) - 1) + slot * .5
    svg += hl(L, Rt, y(hi), INK, 1.6, "5 6") + hl(L, Rt, y(lo), INK, 1.6, "5 6")
    svg += vspan(x(_clear(W, ent)), y(hi), y(lo), f'{xr(k)} المخاطرة', INK, H=H)
    svg += RC._title(Wd, rt("مدى النافذة بالمخاطرة"))
    svg += why(Wd, H, f'من ⁦{lo:.5f}⁩ إلى ⁦{hi:.5f}⁩ — {xr(k)} مسافة وقفك', INK)
    svg += sm(Wd, H, "فالسوق يعطي مضاعفات مخاطرة، والدنانير تجي بعدها", TEAL_D)
    return svg + badge(Wd, "المدى بالمخاطرة", True) + "</svg>"


def m_all(r, Wd=880, H=250):
    """النافذة كاملة — مرجع كل رقم في الوحدة."""
    W = r["w"]
    rg, med = ranges(W)
    assert len(W) == 43, len(W)
    svg, x, y, slot = _g(r, Wd, H)
    svg += hl(x(0) - slot * .5, x(len(W) - 1) + slot * .5, y(W[0]["c"]), GREY, 1.4, "5 6")
    svg += RC._title(Wd, rt("النافذة كاملة"))
    svg += why(Wd, H, f'{ar(len(W))} شمعة ساعة · من {dd(W[0]["d"])} إلى {dd(W[-1]["d"])}', INK)
    svg += sm(Wd, H, f'وسيط الشمعة ⁦{med:.5f}⁩ — وإليه تُنسب النسب كلّها')
    return svg + badge(Wd, "حدود النافذة", True) + "</svg>"


# ═════════ ٢ · وقف — النيوزيلندي/الدولار · ساعة (النافذة ٦٣) ═════════


def w_med(r, Wd=880, H=250):
    """الوقف يُقاس بشمعة أداته: هنا ضعفان ونصف."""
    W = r["w"]
    ent, stp, risk = _plan(W, r)
    rg, med = ranges(W)
    k = risk / med
    assert 2.3 <= k <= 2.7, f"{k:.2f}"
    svg, x, y, slot = _g(r, Wd, H)
    svg += hl(x(0) - slot * .5, x(len(W) - 1) + slot * .5, y(ent), TEAL_D, 1.8)
    svg += hl(x(0) - slot * .5, x(len(W) - 1) + slot * .5, y(stp), RED, 1.8, "6 6")
    svg += band(x(0) - slot * .5, x(len(W) - 1) + slot * .5, y(ent), y(stp), TEAL, 0.10)
    svg += vspan(x(_clear(W, ent)), y(ent), y(stp), f'{xr(k)} الشمعة', TEAL_D, H=H)
    svg += RC._title(Wd, rt("وقفٌ بضعفَي شمعة ونصف"))
    svg += why(Wd, H, f'المخاطرة ⁦{risk:.5f}⁩ ووسيط الشمعة ⁦{med:.5f}⁩ — {xr(k)}', INK)
    svg += sm(Wd, H, "ولو قِسته بالنقاط وحدها ما عرفت أكبير هو أم صغير", TEAL_D)
    return svg + badge(Wd, "الوقف بالشمعة", True) + "</svg>"


def w_pips(r, Wd=880, H=250):
    """الرقم نفسه بالنقاط وبنقاط الأساس — وحدتان لا تكفي إحداهما."""
    W = r["w"]
    ent, stp, risk = _plan(W, r)
    pip = risk / 0.0001
    bp = risk / ent * 1e4
    assert 18 < pip < 21 and 33 < bp < 36, f"{pip:.1f}/{bp:.1f}"
    svg, x, y, slot = _g(r, Wd, H)
    svg += hl(x(0) - slot * .5, x(len(W) - 1) + slot * .5, y(ent), TEAL_D, 1.8)
    svg += hl(x(0) - slot * .5, x(len(W) - 1) + slot * .5, y(stp), RED, 1.8, "6 6")
    svg += vspan(x(_clear(W, ent)), y(ent), y(stp), f'⁦{pip:.1f}⁩ نقطة', TEAL_D, H=H)
    svg += RC._title(Wd, rt("نقطةٌ ونقطةُ أساس"))
    svg += why(Wd, H, f'⁦{pip:.1f}⁩ نقطة = ⁦{bp:.1f}⁩ نقطة أساس من السعر ⁦{ent:.5f}⁩', INK)
    svg += sm(Wd, H, "والثانية هي التي تُقارَن بها أداةٌ بأداة", TEAL_D)
    return svg + badge(Wd, "وحدة القياس", True) + "</svg>"


def w_range(r, Wd=880, H=250):
    """مدى النافذة كلّها أقلّ من ثلاث مخاطرات."""
    W = r["w"]
    ent, stp, risk = _plan(W, r)
    lo = min(c["l"] for c in W); hi = max(c["h"] for c in W)
    k = (hi - lo) / risk
    assert 2.6 <= k <= 3.1, f"{k:.2f}"
    svg, x, y, slot = _g(r, Wd, H)
    L = x(0) - slot * .5; Rt = x(len(W) - 1) + slot * .5
    svg += hl(L, Rt, y(hi), INK, 1.6, "5 6") + hl(L, Rt, y(lo), INK, 1.6, "5 6")
    svg += vspan(x(_clear(W, ent)), y(hi), y(lo), f'{xr(k)} المخاطرة', INK, H=H)
    svg += RC._title(Wd, rt("المدى كلّه ثلاث مخاطرات"))
    svg += why(Wd, H, f'مدى ⁦{len(W)}⁩ ساعة ⁦{hi-lo:.5f}⁩ — {xr(k)} وقفك', INK)
    svg += sm(Wd, H, "فهدفٌ بأربع مخاطرات يطلب من النافذة أكثر ممّا فيها", TEAL_D)
    return svg + badge(Wd, "المدى بالمخاطرة", True) + "</svg>"


def w_break(r, Wd=880, H=250):
    """وشمعة الحدث نفسها ليست ضخمة — مرّة وخُمس."""
    W = r["w"]; bk = r["bk"]
    rg, med = ranges(W)
    body = abs(W[bk]["c"] - W[bk]["o"])
    k = body / med
    assert 1.05 <= k <= 1.40, f"{k:.2f}"
    svg, x, y, slot = _g(r, Wd, H)
    svg += mark(x(bk), slot, y(W[bk]["h"]), y(W[bk]["l"]), TEAL_D, 0.24)
    svg += tag(x(bk), y(W[bk]["h"]), y(W[bk]["l"]), xr(k), TEAL_D)
    svg += RC._title(Wd, rt("شمعة الكسر بالمقياس"))
    svg += why(Wd, H, f'جسمها ⁦{body:.5f}⁩ — {xr(k)} وسيط الشمعة', TEAL_D)
    svg += sm(Wd, H, "الكسر لا يحتاج شمعةً ضخمة، يحتاج إغلاقاً في مكانه")
    return svg + badge(Wd, "شمعة الكسر", True) + "</svg>"


def w_all(r, Wd=880, H=250):
    """النافذة كاملة — مرجع كل رقم في الوحدة."""
    W = r["w"]
    rg, med = ranges(W)
    assert len(W) == 41, len(W)
    svg, x, y, slot = _g(r, Wd, H)
    svg += hl(x(0) - slot * .5, x(len(W) - 1) + slot * .5, y(W[0]["c"]), GREY, 1.4, "5 6")
    svg += RC._title(Wd, rt("النافذة كاملة"))
    svg += why(Wd, H, f'{ar(len(W))} شمعة ساعة · من {dd(W[0]["d"])} إلى {dd(W[-1]["d"])}', INK)
    svg += sm(Wd, H, f'وسيط الشمعة ⁦{med:.5f}⁩ — وإليه تُنسب النسب كلّها')
    return svg + badge(Wd, "حدود النافذة", True) + "</svg>"


# ═════════ ٣ · ساعة — البتكوين · ساعة (النافذة ٥٦) ═════════


def h_hold(r, Wd=880, H=250):
    """ساعتان بين الضغطة والهدف."""
    W = r["w"]; ir = r["ir"]
    ent, stp, risk = _plan(W, r)
    hit = _hit(W, r, ent, risk)
    assert hit - ir == 2, f"{hit-ir}"
    svg, x, y, slot = _g(r, Wd, H)
    svg += mark(x(ir), slot, y(W[ir]["h"]), y(W[ir]["l"]), TEAL_D, 0.22)
    svg += mark(x(hit), slot, y(W[hit]["h"]), y(W[hit]["l"]), TEAL_D, 0.22)
    top = min(y(W[k]["h"]) for k in range(ir, hit + 1))
    svg += spanx(x(ir) - slot * .5, x(hit) + slot * .5, top, f'{ar(hit-ir)} ساعتان', TEAL_D)
    svg += RC._title(Wd, rt("ساعتان من الضغطة للهدف"))
    svg += why(Wd, H, f'الدخول {dd(W[ir]["d"])} والهدف {dd(W[hit]["d"])} — {ar(hit-ir)} ساعة', TEAL_D)
    svg += sm(Wd, H, "وهذي وحدها ليست ساعات شاشتك — اقرأ الجارت الذي بعده")
    return svg + badge(Wd, "زمن الصفقة", True) + "</svg>"


def h_wait(r, Wd=880, H=250):
    """وسبع وعشرون ساعة قبلها لم يكن فيها أمر."""
    W = r["w"]; bk, ir = r["bk"], r["ir"]
    assert ir - bk == 27, f"{ir-bk}"
    svg, x, y, slot = _g(r, Wd, H)
    svg += mark(x(bk), slot, y(W[bk]["h"]), y(W[bk]["l"]), GREY, 0.22)
    svg += mark(x(ir), slot, y(W[ir]["h"]), y(W[ir]["l"]), TEAL_D, 0.22)
    top = min(y(W[k]["h"]) for k in range(bk, ir + 1))
    svg += spanx(x(bk) - slot * .5, x(ir) + slot * .5, top, f'{ar(ir-bk)} ساعة', GREY)
    svg += RC._title(Wd, rt("سبع وعشرون ساعة انتظار"))
    svg += why(Wd, H, f'الكسر {dd(W[bk]["d"])} والدخول {dd(W[ir]["d"])} — {ar(ir-bk)} ساعة', GREY)
    svg += sm(Wd, H, "ومن حسب عائد ساعته على الصفقة وحدها نسي هالساعات", TEAL_D)
    return svg + badge(Wd, "ساعات بلا أمر", True) + "</svg>"


def h_mae(r, Wd=880, H=250):
    """وفي الساعتين نفسهما أخذ منك سبعاً وعشرين بالمئة."""
    W = r["w"]; ir = r["ir"]
    ent, stp, risk = _plan(W, r)
    hit = _hit(W, r, ent, risk)
    j = min(range(ir + 1, hit + 1), key=lambda k: W[k]["l"])
    frac = (ent - W[j]["l"]) / risk
    assert 0.24 <= frac <= 0.30, f"{frac:.2f}"
    svg, x, y, slot = _g(r, Wd, H)
    svg += hl(x(0) - slot * .5, x(len(W) - 1) + slot * .5, y(ent), TEAL_D, 1.8)
    svg += hl(x(0) - slot * .5, x(len(W) - 1) + slot * .5, y(stp), RED, 1.6, "6 6")
    svg += mark(x(j), slot, y(W[j]["h"]), y(W[j]["l"]), GREY, 0.26)
    svg += vspan(x(j), y(ent), y(W[j]["l"]), f'{ar(round(frac*100))}٪', GREY, H=H)
    svg += RC._title(Wd, rt("ساعتان لا تمرّان هيّنتين"))
    svg += why(Wd, H, f'أبعد نزول ⁦{W[j]["l"]:,.0f}⁩ — {ar(round(frac*100))}٪ من مخاطرتك', GREY)
    svg += sm(Wd, H, "فالساعة التي تُحسب لها أجرة فيها ضغطٌ أيضاً", TEAL_D)
    return svg + badge(Wd, "انحراف مقيس", True) + "</svg>"


def h_risk(r, Wd=880, H=250):
    """والمخاطرة ثلاث شمعات — بها يُحسب الحجم قبل أي أجرة."""
    W = r["w"]
    ent, stp, risk = _plan(W, r)
    rg, med = ranges(W)
    k = risk / med
    assert 2.8 <= k <= 3.3, f"{k:.2f}"
    svg, x, y, slot = _g(r, Wd, H)
    svg += hl(x(0) - slot * .5, x(len(W) - 1) + slot * .5, y(ent), TEAL_D, 1.8)
    svg += hl(x(0) - slot * .5, x(len(W) - 1) + slot * .5, y(stp), RED, 1.8, "6 6")
    svg += band(x(0) - slot * .5, x(len(W) - 1) + slot * .5, y(ent), y(stp), TEAL, 0.10)
    svg += vspan(x(_clear(W, ent)), y(ent), y(stp), f'{xr(k)} الشمعة', TEAL_D, H=H)
    svg += RC._title(Wd, rt("المخاطرة ثلاث شمعات"))
    svg += why(Wd, H, f'⁦{risk:,.0f}⁩ نقطة — {xr(k)} وسيط الشمعة ⁦{med:,.0f}⁩', INK)
    svg += sm(Wd, H, "وهي التي تحدّد حجمك، والأجرة تُقسم عليها لا العكس", TEAL_D)
    return svg + badge(Wd, "مخاطرة بالشمعة", True) + "</svg>"


def h_all(r, Wd=880, H=250):
    """النافذة كاملة — مرجع كل رقم في الوحدة."""
    W = r["w"]
    rg, med = ranges(W)
    assert len(W) == 50, len(W)
    svg, x, y, slot = _g(r, Wd, H)
    svg += hl(x(0) - slot * .5, x(len(W) - 1) + slot * .5, y(W[0]["c"]), GREY, 1.4, "5 6")
    svg += RC._title(Wd, rt("النافذة كاملة"))
    svg += why(Wd, H, f'{ar(len(W))} شمعة ساعة · من {dd(W[0]["d"])} إلى {dd(W[-1]["d"])}', INK)
    svg += sm(Wd, H, f'وسيط الشمعة ⁦{med:,.0f}⁩ — وإليه تُنسب النسب كلّها')
    return svg + badge(Wd, "حدود النافذة", True) + "</svg>"


SETS = {"mablagh": [m_risk, m_wait, m_mae, m_span, m_all],
        "waqf":    [w_med, w_pips, w_range, w_break, w_all],
        "saa":     [h_hold, h_wait, h_mae, h_risk, h_all]}
WIN = {"mablagh": 55, "waqf": 63, "saa": 56}


def unit_charts(slug):
    r = RC.win(WIN[slug])
    ok, dropped = [], []
    for f in SETS[slug]:
        try:
            f(r, 880, 250); ok.append(f)
        except AssertionError as e:
            dropped.append((f.__name__, str(e)))
    return r, ok, dropped


if __name__ == "__main__":
    for slug in SETS:
        r, ok, dropped = unit_charts(slug)
        print(f'{slug:<8} {r["slug"]:<34} ثبت {len(ok)}/{len(SETS[slug])}'
              + ("" if not dropped else " · سقط " + " · ".join(f"{a}: {b}" for a, b in dropped)))
