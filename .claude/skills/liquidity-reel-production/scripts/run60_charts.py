# -*- coding: utf-8 -*-
"""جارتات تشغيلة ٦٠ — ثلاثة قياسات: انحرافٌ ومسافةٌ زمنية وحجمُ مخاطرة.

الوحدات الثلاث الكاروسيلية ليست دروسَ دخول، فلا تُرسم لها نماذجُ
`run31_charts` السبعة (درس ٥٨). ومقاييسها هنا ثلاثة مختلفة عمداً كي لا
تتشابه الوحدات: **انحرافٌ** بعد الدخول يُقاس بأجزاء المخاطرة · **مسافةٌ
زمنية** بين رسم المستوى واستعماله · و**حجمُ المخاطرة** منسوباً إلى الشمعة
وإلى مدى النافذة.

وكلّ دالّة تتحقّق من رقمها بـ`assert` قبل أن تُخرج SVG.

    python3 run60_charts.py
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


# ═════════ ١ · شخصي — عقد الجنيه الآجل · ساعة (النافذة ٥٨) ═════════


def p_mae(r, Wd=880, H=250):
    """أبعد ما ذهب السعر ضدّك: ثلاثون بالمئة من مخاطرتك، لا أكثر."""
    W = r["w"]; ir = r["ir"]
    ent, stp, risk = _plan(W, r)
    hit = _hit(W, r, ent, risk)
    j = min(range(ir + 1, hit + 1), key=lambda k: W[k]["l"])
    frac = (ent - W[j]["l"]) / risk
    assert 0.28 <= frac <= 0.32, f"{frac:.2f}"
    svg, x, y, slot = _g(r, Wd, H)
    svg += hl(x(0) - slot * .5, x(len(W) - 1) + slot * .5, y(ent), TEAL_D, 1.8)
    svg += hl(x(0) - slot * .5, x(len(W) - 1) + slot * .5, y(stp), RED, 1.6, "6 6")
    svg += mark(x(j), slot, y(W[j]["h"]), y(W[j]["l"]), GREY, 0.26)
    svg += vspan(x(j), y(ent), y(W[j]["l"]), f'{ar(round(frac*100))}٪', GREY, H=H)
    svg += RC._title(Wd, rt("أبعد ما ذهب ضدّك"))
    svg += why(Wd, H, f'بعد الدخول نزل إلى ⁦{W[j]["l"]:.5f}⁩ — و{ar(round(frac*100))}٪ من مخاطرتك', GREY)
    svg += sm(Wd, H, "ولا مرّة لمس وقفك — الحركة ضدّك كانت أصغر ممّا شعرت", TEAL_D)
    return svg + badge(Wd, "انحراف مقيس", True) + "</svg>"


def p_hold(r, Wd=880, H=250):
    """ست ساعات بين الدخول والنتيجة — والشعور فيها ليس معلومة."""
    W = r["w"]; ir = r["ir"]
    ent, stp, risk = _plan(W, r)
    hit = _hit(W, r, ent, risk)
    assert hit - ir == 6, f"{hit-ir}"
    svg, x, y, slot = _g(r, Wd, H)
    svg += mark(x(ir), slot, y(W[ir]["h"]), y(W[ir]["l"]), TEAL_D, 0.22)
    svg += mark(x(hit), slot, y(W[hit]["h"]), y(W[hit]["l"]), TEAL_D, 0.22)
    top = min(y(W[k]["h"]) for k in range(ir, hit + 1))
    svg += spanx(x(ir) - slot * .5, x(hit) + slot * .5, top, f'{ar(hit-ir)} ساعات', TEAL_D)
    svg += RC._title(Wd, rt("بين القرار ونتيجته"))
    svg += why(Wd, H, f'{ar(hit-ir)} ساعات — والسعر خلالها لم يلمس وقفك', TEAL_D)
    svg += sm(Wd, H, "وكل ما جرى فيها من قلقٍ لم يظهر على الشارت")
    return svg + badge(Wd, "زمن الانتظار", True) + "</svg>"


def p_against(r, Wd=880, H=250):
    """كم شمعة كانت ضدّك فعلاً: اثنتان من ستّ — لا الست ولا العشر."""
    W = r["w"]; ir = r["ir"]
    ent, stp, risk = _plan(W, r)
    hit = _hit(W, r, ent, risk)
    dn = [j for j in range(ir + 1, hit + 1) if W[j]["c"] < W[j]["o"]]
    tot = hit - ir
    assert len(dn) == 2 and tot == 6, f"{len(dn)}/{tot}"
    svg, x, y, slot = _g(r, Wd, H)
    for j in dn:
        svg += mark(x(j), slot, y(W[j]["h"]), y(W[j]["l"]), RED, 0.16)
    svg += hl(x(0) - slot * .5, x(len(W) - 1) + slot * .5, y(ent), TEAL_D, 1.6)
    svg += RC._title(Wd, rt("كم شمعة كانت ضدّك"))
    svg += why(Wd, H, f'من {ar(tot)} شمعات بعد الدخول، {ar(len(dn))} فقط أغلقت هابطة', RED)
    svg += sm(Wd, H, "والباقي معك — لكن الذاكرة تحتفظ بالاثنتين", TEAL_D)
    return svg + badge(Wd, "شمعات ضدّك", True) + "</svg>"


def p_quiet(r, Wd=880, H=250):
    """أهدأ ساعة في النافذة — والسوق فيها لا يقصد أحداً."""
    W = r["w"]
    rg, med = ranges(W)
    lo = min(range(len(W)), key=lambda k: rg[k])
    frac = rg[lo] / med
    assert frac < 0.5, f"{frac:.2f}"
    svg, x, y, slot = _g(r, Wd, H)
    svg += mark(x(lo), slot, y(W[lo]["h"]), y(W[lo]["l"]), GREY, 0.28)
    svg += tag(x(lo), y(W[lo]["h"]), y(W[lo]["l"]), f'⁦{frac:.0%}⁩', GREY)
    svg += RC._title(Wd, rt("ساعةٌ بلا نيّة"))
    svg += why(Wd, H, f'أهدأ ساعة — {ar(round(frac*100))}٪ من وسيط الشمعة', INK)
    svg += sm(Wd, H, "السوق لا يعرفك ولا يعرف حسابك — هذي ساعةٌ مثل غيرها")
    return svg + badge(Wd, "أهدأ ساعة", False) + "</svg>"


def p_all(r, Wd=880, H=250):
    """النافذة كاملة — مرجع كل رقم في الوحدة."""
    W = r["w"]
    rg, med = ranges(W)
    assert len(W) == 33, len(W)
    svg, x, y, slot = _g(r, Wd, H)
    svg += hl(x(0) - slot * .5, x(len(W) - 1) + slot * .5, y(W[0]["c"]), GREY, 1.4, "5 6")
    svg += RC._title(Wd, rt("النافذة كاملة"))
    svg += why(Wd, H, f'{ar(len(W))} شمعة ساعة · من {dd(W[0]["d"])} إلى {dd(W[-1]["d"])}', INK)
    svg += sm(Wd, H, f'وسيط الشمعة ⁦{med:.5f}⁩ — وإليه تُنسب النسب كلّها')
    return svg + badge(Wd, "حدود النافذة", True) + "</svg>"


# ═════════ ٢ · روتين — البلاتين · ساعة (النافذة ٥٩) ═════════


def t_origin(r, Wd=880, H=250):
    """المستوى الذي دخلتَ عليه رُسم قبل دخولك بخمس عشرة ساعة."""
    W = r["w"]; iob, ir = r["iob"], r["ir"]
    assert ir - iob == 15, f"{ir-iob}"
    svg, x, y, slot = _g(r, Wd, H)
    svg += mark(x(iob), slot, y(W[iob]["h"]), y(W[iob]["l"]), TEAL_D, 0.24)
    svg += mark(x(ir), slot, y(W[ir]["h"]), y(W[ir]["l"]), TEAL_D, 0.20)
    svg += hl(x(iob) - slot * .5, x(ir) + slot * .5, y(W[iob]["o"]), TEAL_D, 1.8)
    top = min(y(W[k]["h"]) for k in range(iob, ir + 1))
    svg += spanx(x(iob) - slot * .5, x(ir) + slot * .5, top, f'{ar(ir-iob)} ساعة', TEAL_D)
    svg += RC._title(Wd, rt("رُسم قبل أن يُستعمل بيوم"))
    svg += why(Wd, H, f'الشمعة الأصل {dd(W[iob]["d"])} وحدّها ⁦{W[iob]["o"]:.2f}⁩', TEAL_D)
    svg += sm(Wd, H, f'والدخول بعدها بـ{ar(ir-iob)} ساعة — على المستوى نفسه')
    return svg + badge(Wd, "عمر المستوى", True) + "</svg>"


def t_break(r, Wd=880, H=250):
    """والكسر نفسه سبق الدخول بإحدى عشرة ساعة."""
    W = r["w"]; bk, ir = r["bk"], r["ir"]
    assert ir - bk == 11, f"{ir-bk}"
    svg, x, y, slot = _g(r, Wd, H)
    svg += mark(x(bk), slot, y(W[bk]["h"]), y(W[bk]["l"]), TEAL_D, 0.24)
    top = min(y(W[k]["h"]) for k in range(bk, ir + 1))
    svg += spanx(x(bk) - slot * .5, x(ir) + slot * .5, top, f'{ar(ir-bk)} ساعة', GREY)
    svg += RC._title(Wd, rt("ولا الكسر كان مفاجأة"))
    svg += why(Wd, H, f'الكسر {dd(W[bk]["d"])} والدخول بعده بـ{ar(ir-bk)} ساعة', INK)
    svg += sm(Wd, H, "من قرأ الشارت مساءً وجد الاثنين مرسومَين قبل نومه")
    return svg + badge(Wd, "زمن الكسر", True) + "</svg>"


def t_fast(r, Wd=880, H=250):
    """والنتيجة بعد ساعتين — العمل كلّه كان قبلها."""
    W = r["w"]; ir = r["ir"]
    ent, stp, risk = _plan(W, r)
    hit = _hit(W, r, ent, risk)
    assert hit - ir == 2, f"{hit-ir}"
    svg, x, y, slot = _g(r, Wd, H)
    svg += mark(x(ir), slot, y(W[ir]["h"]), y(W[ir]["l"]), TEAL_D, 0.22)
    svg += mark(x(hit), slot, y(W[hit]["h"]), y(W[hit]["l"]), TEAL_D, 0.22)
    top = min(y(W[k]["h"]) for k in range(ir, hit + 1))
    svg += spanx(x(ir) - slot * .5, x(hit) + slot * .5, top, f'{ar(hit-ir)} ساعتان', TEAL_D)
    svg += RC._title(Wd, rt("والنتيجة في ساعتين"))
    svg += why(Wd, H, f'من الدخول إلى الهدف {ar(hit-ir)} ساعتان فقط', TEAL_D)
    svg += sm(Wd, H, "والخمس عشرة ساعة قبلها هي التي صنعتهما")
    return svg + badge(Wd, "زمن النتيجة", True) + "</svg>"


def t_held(r, Wd=880, H=250):
    """عشر شمعات من عشر بقيت فوق المستوى — لم يُختبَر مرّةً ويسقط."""
    W = r["w"]; iob, bk, ir = r["iob"], r["bk"], r["ir"]
    lvl = W[iob]["o"]
    span_ = list(range(bk + 1, ir))
    held = [j for j in span_ if W[j]["l"] > lvl]
    assert len(held) == len(span_) == 10, f"{len(held)}/{len(span_)}"
    svg, x, y, slot = _g(r, Wd, H)
    svg += hl(x(bk) - slot * .5, x(ir) + slot * .5, y(lvl), TEAL_D, 1.8)
    for j in held:
        svg += mark(x(j), slot, y(W[j]["h"]), y(W[j]["l"]), TEAL_D, 0.13)
    svg += RC._title(Wd, rt("مستوىً لم يُخترق مرّة"))
    svg += why(Wd, H, f'{ar(len(held))} شمعات من {ar(len(span_))} قاعُها فوق ⁦{lvl:.2f}⁩', TEAL_D)
    svg += sm(Wd, H, "من قرأه مساءً وجده صامداً صباحاً — ولم يحتج متابعةً بينهما")
    return svg + badge(Wd, "صمود المستوى", True) + "</svg>"


def t_all(r, Wd=880, H=250):
    """النافذة كاملة — خمس وأربعون ساعة."""
    W = r["w"]
    rg, med = ranges(W)
    assert len(W) == 45, len(W)
    svg, x, y, slot = _g(r, Wd, H)
    svg += hl(x(0) - slot * .5, x(len(W) - 1) + slot * .5, y(W[0]["c"]), GREY, 1.4, "5 6")
    svg += RC._title(Wd, rt("النافذة كاملة"))
    svg += why(Wd, H, f'{ar(len(W))} شمعة ساعة · من {dd(W[0]["d"])} إلى {dd(W[-1]["d"])}', INK)
    svg += sm(Wd, H, f'وسيط الشمعة ⁦{med:.2f}⁩ — وإليه تُنسب النسب')
    return svg + badge(Wd, "حدود النافذة", True) + "</svg>"


# ═════════ ٣ · إيداع — الناسداك · ١٥ دقيقة (النافذة ٦٢) ═════════


def d_risk(r, Wd=880, H=250):
    """مسافة المخاطرة بالنقاط وبنقاط الأساس — وحدةُ قياس حجمك."""
    W = r["w"]
    ent, stp, risk = _plan(W, r)
    bp = risk / ent * 1e4
    assert 37 < bp < 40, f"{bp:.1f}"
    svg, x, y, slot = _g(r, Wd, H)
    svg += hl(x(0) - slot * .5, x(len(W) - 1) + slot * .5, y(ent), TEAL_D, 1.8)
    svg += hl(x(0) - slot * .5, x(len(W) - 1) + slot * .5, y(stp), RED, 1.8, "6 6")
    svg += band(x(0) - slot * .5, x(len(W) - 1) + slot * .5, y(ent), y(stp), TEAL, 0.10)
    lo_, hi_ = 4, len(W) - 7
    clear = max(range(lo_, hi_), key=lambda j: W[j]["l"] - ent)
    assert W[clear]["l"] > ent, "لا موضع خالٍ للقوس"
    svg += vspan(x(clear), y(ent), y(stp), f'⁦{risk:.0f}⁩ نقطة', TEAL_D, H=H)
    svg += RC._title(Wd, rt("المسافة التي تحدّد حجمك"))
    svg += why(Wd, H, f'من ⁦{ent:,.0f}⁩ إلى ⁦{stp:,.0f}⁩ — ⁦{risk:.0f}⁩ نقطة', INK)
    svg += sm(Wd, H, f'أي ⁦{bp:.1f}⁩ نقطة أساس — وعليها يُحسب اللوت لا على رصيدك')
    return svg + badge(Wd, "مسافة المخاطرة", True) + "</svg>"


def d_med(r, Wd=880, H=250):
    """المخاطرة مقابل شمعةٍ اعتيادية."""
    W = r["w"]
    rg, med = ranges(W)
    _, _, risk = _plan(W, r)
    k = risk / med
    assert 1.5 < k < 1.9, f"{k:.2f}"
    mid = min(range(len(W)), key=lambda j: abs(rg[j] - med))
    svg, x, y, slot = _g(r, Wd, H)
    svg += mark(x(mid), slot, y(W[mid]["h"]), y(W[mid]["l"]), GREY, 0.26)
    svg += tag(x(mid), y(W[mid]["h"]), y(W[mid]["l"]), f'⁦{med:.0f}⁩', GREY)
    svg += RC._title(Wd, rt("شمعة اعتيادية… ومخاطرتك"))
    svg += why(Wd, H, f'وسيط الشمعة ⁦{med:.0f}⁩ نقطة والمخاطرة ⁦{risk:.0f}⁩', INK)
    svg += sm(Wd, H, f'أي {xr(k)} الشمعة — ومن هنا يبدأ حساب ما تودعه', TEAL_D)
    return svg + badge(Wd, "المخاطرة بالشمعات", True) + "</svg>"


def d_span(r, Wd=880, H=250):
    """مدى النافذة كلّه أربع مخاطرات — لا أربعين."""
    W = r["w"]
    _, _, risk = _plan(W, r)
    tot = max(c["h"] for c in W) - min(c["l"] for c in W)
    k = tot / risk
    assert 3.7 < k < 4.1, f"{k:.2f}"
    svg, x, y, slot = _g(r, Wd, H)
    hi = max(range(len(W)), key=lambda j: W[j]["h"])
    lo = min(range(len(W)), key=lambda j: W[j]["l"])
    svg += hl(x(0) - slot * .5, x(len(W) - 1) + slot * .5, y(W[hi]["h"]), GREY, 1.4, "5 6")
    svg += hl(x(0) - slot * .5, x(len(W) - 1) + slot * .5, y(W[lo]["l"]), GREY, 1.4, "5 6")
    svg += RC._title(Wd, rt("مدى النافذة بمخاطراتك"))
    svg += why(Wd, H, f'من القاع إلى القمة ⁦{tot:.0f}⁩ نقطة', INK)
    svg += sm(Wd, H, f'أي {xr(k)} مخاطرتك — والسوق لا يعطيك أكثر ممّا فيه', TEAL_D)
    return svg + badge(Wd, "مدى النافذة", True) + "</svg>"


def d_fast(r, Wd=880, H=250):
    """ساعة ونصف بين الدخول والهدف."""
    W = r["w"]; ir = r["ir"]
    ent, stp, risk = _plan(W, r)
    hit = _hit(W, r, ent, risk)
    assert hit - ir == 6, f"{hit-ir}"
    svg, x, y, slot = _g(r, Wd, H)
    svg += mark(x(ir), slot, y(W[ir]["h"]), y(W[ir]["l"]), TEAL_D, 0.22)
    svg += mark(x(hit), slot, y(W[hit]["h"]), y(W[hit]["l"]), TEAL_D, 0.22)
    top = min(y(W[k]["h"]) for k in range(ir, hit + 1))
    svg += spanx(x(ir) - slot * .5, x(hit) + slot * .5, top, "ساعة ونصف", TEAL_D)
    svg += RC._title(Wd, rt("زمن التعرّض"))
    svg += why(Wd, H, f'{ar(hit-ir)} شمعات ١٥ دقيقة — ساعة ونصف', TEAL_D)
    svg += sm(Wd, H, "وهذي المدّة وحدها كان رأس مالك فيها معرَّضاً")
    return svg + badge(Wd, "زمن التعرّض", True) + "</svg>"


def d_all(r, Wd=880, H=250):
    """النافذة كاملة — ثمانٍ وثلاث أرباع ساعة."""
    W = r["w"]
    rg, med = ranges(W)
    assert len(W) == 35, len(W)
    svg, x, y, slot = _g(r, Wd, H)
    svg += hl(x(0) - slot * .5, x(len(W) - 1) + slot * .5, y(W[0]["c"]), GREY, 1.4, "5 6")
    svg += RC._title(Wd, rt("النافذة كاملة"))
    svg += why(Wd, H, f'{ar(len(W))} شمعة ١٥ دقيقة · من {dd(W[0]["d"])} إلى {dd(W[-1]["d"])}', INK)
    svg += sm(Wd, H, f'وسيط الشمعة ⁦{med:.0f}⁩ نقطة — وإليه تُنسب النسب')
    return svg + badge(Wd, "حدود النافذة", True) + "</svg>"


SETS = {"shakhsi": [p_mae, p_hold, p_against, p_quiet, p_all],
        "routine": [t_origin, t_break, t_fast, t_held, t_all],
        "iidaa":   [d_risk, d_med, d_span, d_fast, d_all]}
WIN = {"shakhsi": 58, "routine": 59, "iidaa": 62}


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
        r, ok, dr = unit_charts(slug)
        print(f'{slug:<9} {r["slug"]:<40} ثابتة {len(ok)}/{len(SETS[slug])}'
              + ("" if not dr else " · سقط " + ", ".join(f"{a}: {b}" for a, b in dr)))
