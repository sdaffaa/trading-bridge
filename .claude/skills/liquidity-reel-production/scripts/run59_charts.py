# -*- coding: utf-8 -*-
"""جارتات تشغيلة ٥٩ — قياسُ الوقت لا قياسُ الصفقة.

وحدتا هذه التشغيلة الكاروسيليّتان درسان عن **الساعة**: أيّ ساعةٍ تستحقّ
أن تُفتح لها الشاشة، وكم ساعةً تُنتظَر قبل أن يظهر شيء. فلا يصلح لهما
أيٌّ من نماذج `run31_charts` السبعة — تلك كلّها دخولٌ ووقفٌ وهدف، ووضعُها
تحت درسٍ عن الوقت يقول للمتابع شيئاً لم يقله النصّ (درس ٥٨: الجارت يتبع
درسَ الوحدة لا محرّكها).

فالمرسوم هنا **مدى الشمعة منسوباً إلى وسيط النافذة**: عمودٌ شفّاف يضيء
ساعةً بعينها، وقوسٌ يقيس مدىً زمنياً — ولا خطَّ دخولٍ ولا وقفَ ولا هدف.

والقاعدة قائمة: ما لا تُثبته الشموع لا يُرسم. كل دالة تتحقّق من رقمها
بـ`assert` قبل أن تُخرج SVG.

    python3 run59_charts.py        # يطبع أرقام الوحدتين
"""
import statistics as st

from reel_build import INK, TEAL, TEAL_D, RED, GREY, htext
from run15_charts import zbox, tick, hl, badge, frame
import run31_charts as RC
from run58_charts import ar, dd, rt, why, sm, band, mark, span, i_of, ranges

BULL = "#2E8CA6"


def _g(r, Wd, H):
    return frame(r["w"], Wd, H)


def xr(v):
    """نسبةٌ إلى الوسيط داخل نصّ عربي — معزولة كي لا ينقلب «×»."""
    return f'⁦{v:.2f}⁩×'


def _pt():
    """أعلى مساحة الشموع — بنفس صيغة `run15_charts.frame`."""
    s = RC._SC[0]
    return round(58 * s) + (round(46 * s) if s > 1.15 else 0)


def tag(xx, ytop, ybot, txt, col):
    """وسمُ رقمٍ فوق الشمعة — وتحتها إن كان ما فوقها شريطَ العنوان.

    الشمعة الأعنف كثيراً ما تلامس سقف مساحة الرسم، فوسمُها المعلّق فوقها
    يدوس العنوان الموسَّط (وقع في `q_all`: «×2.72» فوق «النافذة كاملة»)."""
    s = RC._SC[0]
    up = ytop - round(24 * s)
    if up >= _pt() + round(15 * s):
        return htext(xx, up, txt, col, round(17 * s))
    return htext(xx, ybot + round(30 * s), txt, col, round(17 * s))


def spanx(x0, x1, ytop, txt, col=INK):
    """قوسٌ زمني مُنزَّلٌ تحت شريط العنوان إن لزم — لا يعلوه."""
    s = RC._SC[0]
    return span(x0, x1, max(ytop - 26, _pt() + round(26 * s)), txt, col)


# ═════════════════ ١ · ميتة — الفضة الآجلة · ساعة ═════════════════
# النافذة ٤٩: SI=F 1h · 2026-07-21 07:00 → 2026-07-22 19:00 بتوقيت الكويت

DEAD = ("22:00", "23:00", "01:00", "02:00")


def k_four(r, Wd=880, H=250):
    """أربع ساعاتٍ ميتة مجموعُ مداها أقلّ من ساعةٍ نشطة واحدة."""
    W = r["w"]
    rg, med = ranges(W)
    ks = [i_of(W, d) for d in DEAD]
    assert ks == list(range(ks[0], ks[0] + 4)), f"الساعات الأربع غير متتالية {ks}"
    b = i_of(W, "04:00")
    tot = sum(rg[k] for k in ks)
    assert tot < rg[b], f"مجموع الأربع {tot:.3f} ليس أقلّ من {rg[b]:.3f}"
    trav = max(W[k]["h"] for k in ks) - min(W[k]["l"] for k in ks)
    assert trav / med < 0.85, f"مسير الأربع {trav/med:.2f} من الوسيط"
    svg, x, y, slot = _g(r, Wd, H)
    for k in ks:
        svg += mark(x(k), slot, y(W[k]["h"]), y(W[k]["l"]), GREY, 0.26)
    svg += mark(x(b), slot, y(W[b]["h"]), y(W[b]["l"]), TEAL_D, 0.22)
    top = min(y(W[k]["h"]) for k in ks) - 26
    svg += spanx(x(ks[0]) - slot * .5, x(ks[-1]) + slot * .5, top + 26,
                 f'⁦{tot:.3f}⁩', GREY)
    svg += tag(x(b), y(W[b]["h"]), y(W[b]["l"]), f'⁦{rg[b]:.3f}⁩', TEAL_D)
    svg += RC._title(Wd, rt("أربع ساعات… وساعة واحدة"))
    svg += why(Wd, H, f'من {dd("٢٢:٠٠")} إلى {dd("٠٢:٠٠")} — أربع ساعات مجموعها ⁦{tot:.3f}⁩', GREY)
    svg += sm(Wd, H, f'وساعة ٠٤:٠٠ وحدها ⁦{rg[b]:.3f}⁩ — أكبر من الأربع مجتمعة', TEAL_D)
    return svg + badge(Wd, "مدى الساعة", True) + "</svg>"


def k_quiet(r, Wd=880, H=250):
    """أهدأ ساعة في النافذة: أقلّ من نصف الوسيط."""
    W = r["w"]
    rg, med = ranges(W)
    lo = min(range(len(W)), key=lambda k: rg[k])
    assert W[lo]["d"] == "02:00", f"أهدأ ساعة {W[lo]['d']}"
    assert rg[lo] / med < 0.5, f"{rg[lo]/med:.2f}"
    svg, x, y, slot = _g(r, Wd, H)
    svg += mark(x(lo), slot, y(W[lo]["h"]), y(W[lo]["l"]), GREY, 0.28)
    svg += tag(x(lo), y(W[lo]["h"]), y(W[lo]["l"]), f'⁦{rg[lo]/med:.0%}⁩', GREY)
    svg += RC._title(Wd, rt("أهدأ ساعة في النافذة"))
    svg += why(Wd, H, f'الساعة ٠٢:٠٠ — مداها ⁦{rg[lo]:.3f}⁩', INK)
    svg += sm(Wd, H, f'أي {ar(round(rg[lo]/med*100))}٪ من وسيط الساعة — والنموذج فيها لا يُنفَّذ')
    return svg + badge(Wd, "أهدأ ساعة", False) + "</svg>"


def k_gap(r, Wd=880, H=250):
    """لا شمعة ٠٠:٠٠ أصلاً — البورصة نفسها تغلق ساعة."""
    W = r["w"]
    a = i_of(W, "23:00")
    assert W[a + 1]["d"] == "01:00", f"بعد ٢٣:٠٠ تأتي {W[a+1]['d']}"
    assert not any(b["d"] == "00:00" for b in W), "توجد شمعة ٠٠:٠٠"
    svg, x, y, slot = _g(r, Wd, H)
    gx = (x(a) + x(a + 1)) / 2
    svg += (f'<line x1="{gx:.1f}" y1="14" x2="{gx:.1f}" y2="{H-46}" '
            f'stroke="{RED}" stroke-width="1.8" stroke-dasharray="7 6"/>')
    svg += mark(x(a), slot, y(W[a]["h"]), y(W[a]["l"]), GREY, 0.22)
    svg += mark(x(a + 1), slot, y(W[a + 1]["h"]), y(W[a + 1]["l"]), GREY, 0.22)
    svg += RC._title(Wd, rt("ساعةٌ ما لها شمعة"))
    svg += why(Wd, H, "النافذة تقفز من ٢٣:٠٠ إلى ٠١:٠٠ مباشرة", RED)
    svg += sm(Wd, H, "السوق نفسه يقفل ساعة — وانت قاعد تراقب")
    return svg + badge(Wd, "استراحة البورصة", False) + "</svg>"


def k_break(r, Wd=880, H=250):
    """ساعةٌ واحدة حملت الحدث كلّه — ٢٫٣٦ ضعف الوسيط."""
    W = r["w"]
    rg, med = ranges(W)
    b = i_of(W, "04:00")
    assert b == r["bk"], f"شمعة الكسر {r['bk']} لا ٠٤:٠٠"
    x_ = rg[b] / med
    assert 2.2 < x_ < 2.5, f"{x_:.2f}"
    svg, x, y, slot = _g(r, Wd, H)
    svg += mark(x(b), slot, y(W[b]["h"]), y(W[b]["l"]), TEAL_D, 0.22)
    svg += tag(x(b), y(W[b]["h"]), y(W[b]["l"]), xr(x_), TEAL_D)
    svg += RC._title(Wd, rt("الحدث كلّه في ساعة"))
    svg += why(Wd, H, f'الساعة ٠٤:٠٠ — {xr(x_)} وسيط الساعة', TEAL_D)
    svg += sm(Wd, H, "من نام عن هذي الساعة ما فاته شيء من الليل كلّه")
    return svg + badge(Wd, "ساعة الحركة", True) + "</svg>"


def k_all(r, Wd=880, H=250):
    """النافذة كاملة بحدودها — مرجعُ كل رقمٍ في الوحدة."""
    W = r["w"]
    rg, med = ranges(W)
    hi = max(range(len(W)), key=lambda k: rg[k])
    assert len(W) == 36 and W[0]["d"] == "07:00" and W[-1]["d"] == "19:00"
    assert W[hi]["d"] == "16:00" and rg[hi] / med > 4, f"{W[hi]['d']} {rg[hi]/med:.2f}"
    svg, x, y, slot = _g(r, Wd, H)
    svg += mark(x(hi), slot, y(W[hi]["h"]), y(W[hi]["l"]), TEAL_D, 0.20)
    svg += tag(x(hi), y(W[hi]["h"]), y(W[hi]["l"]), xr(rg[hi] / med), TEAL_D)
    svg += RC._title(Wd, rt("النافذة كاملة"))
    svg += why(Wd, H, f'{ar(len(W))} ساعة · من ٠٧:٠٠ إلى ١٩:٠٠ بتوقيت الكويت', INK)
    svg += sm(Wd, H, f'وسيط المدى الساعي ⁦{med:.4f}⁩ — وكل نسبةٍ هنا منسوبة إليه')
    return svg + badge(Wd, "حدود النافذة", True) + "</svg>"


# ═════════════════ ٢ · تعلّق — الفضة الآجلة · ساعة ═════════════════
# النافذة ٥٢: SI=F 1h · 2026-08-12 01:00 → 2026-08-13 06:00 بتوقيت الكويت


def q_one(r, Wd=880, H=250):
    """تسعٌ وعشرون ساعة على رمزٍ واحد أعطت موضعاً واحداً."""
    W = r["w"]
    ir = r["ir"]
    assert len(W) == 29 and ir == 18 and W[ir]["d"] == "19:00", f"{len(W)} {ir}"
    svg, x, y, slot = _g(r, Wd, H)
    svg += mark(x(ir), slot, y(W[ir]["h"]), y(W[ir]["l"]), TEAL_D, 0.24)
    svg += RC._title(Wd, rt("موضعٌ واحد في يومٍ كامل"))
    svg += why(Wd, H, f'{ar(len(W))} ساعة على رمزٍ واحد — والموضع ساعة ١٩:٠٠', TEAL_D)
    svg += sm(Wd, H, f'واحدة من {ar(len(W))} — والباقي مراقبة')
    return svg + badge(Wd, "موضع واحد", True) + "</svg>"


def q_wait(r, Wd=880, H=250):
    """ثماني عشرة ساعة قبل الموضع — الانتظار هو أطول جزء."""
    W = r["w"]
    ir = r["ir"]
    assert ir == 18, ir
    svg, x, y, slot = _g(r, Wd, H)
    for k in range(ir):
        svg += mark(x(k), slot, y(W[k]["h"]), y(W[k]["l"]), GREY, 0.13)
    top = min(y(W[k]["h"]) for k in range(ir + 1)) - 26
    svg += spanx(x(0) - slot * .5, x(ir) + slot * .5, top + 26,
                 f'{ar(ir)} ساعة انتظار', GREY)
    svg += mark(x(ir), slot, y(W[ir]["h"]), y(W[ir]["l"]), TEAL_D, 0.24)
    svg += RC._title(Wd, rt("ما قبل الموضع"))
    svg += why(Wd, H, f'{ar(ir)} ساعة من ٠١:٠٠ إلى ١٨:٠٠ بلا شيء يُنفَّذ', GREY)
    svg += sm(Wd, H, "والتعلّق بالرمز يخليك تحسب هذي الساعات شغلاً", TEAL_D)
    return svg + badge(Wd, "زمن الانتظار", False) + "</svg>"


def q_after(r, Wd=880, H=250):
    """سبع ساعاتٍ بين الموضع وأبعد ما بلغته الحركة."""
    W = r["w"]
    ir = r["ir"]
    pk = max(range(ir + 1, len(W)), key=lambda k: W[k]["h"])
    assert W[pk]["d"] == "03:00" and pk - ir == 7, f"{W[pk]['d']} {pk-ir}"
    svg, x, y, slot = _g(r, Wd, H)
    svg += mark(x(ir), slot, y(W[ir]["h"]), y(W[ir]["l"]), TEAL_D, 0.22)
    svg += mark(x(pk), slot, y(W[pk]["h"]), y(W[pk]["l"]), TEAL_D, 0.22)
    top = min(y(W[k]["h"]) for k in range(ir, pk + 1)) - 26
    svg += spanx(x(ir) - slot * .5, x(pk) + slot * .5, top + 26,
                 f'{ar(pk-ir)} ساعات', TEAL_D)
    svg += RC._title(Wd, rt("وما بعد الموضع"))
    svg += why(Wd, H, f'{ar(pk-ir)} ساعات حتى بلغت الحركة أبعدها ساعة ٠٣:٠٠', TEAL_D)
    svg += sm(Wd, H, f'ساعة موضع · {ar(pk-ir)} ساعات نتيجة · والباقي انتظار')
    return svg + badge(Wd, "زمن النتيجة", True) + "</svg>"


def q_quiet(r, Wd=880, H=250):
    """أهدأ ساعة: ثلث الوسيط — لا معنى لفتح الشاشة فيها."""
    W = r["w"]
    rg, med = ranges(W)
    lo = min(range(len(W)), key=lambda k: rg[k])
    assert W[lo]["d"] == "02:00" and rg[lo] / med < 0.35, f"{W[lo]['d']} {rg[lo]/med:.2f}"
    svg, x, y, slot = _g(r, Wd, H)
    svg += mark(x(lo), slot, y(W[lo]["h"]), y(W[lo]["l"]), GREY, 0.28)
    svg += tag(x(lo), y(W[lo]["h"]), y(W[lo]["l"]), f'⁦{rg[lo]/med:.0%}⁩', GREY)
    svg += RC._title(Wd, rt("ساعةٌ ما فيها شيء"))
    svg += why(Wd, H, f'الساعة ٠٢:٠٠ — {ar(round(rg[lo]/med*100))}٪ من وسيط الساعة', INK)
    svg += sm(Wd, H, "وانت واقفٌ عليها لأنك ما تعرف غير هذا الرمز")
    return svg + badge(Wd, "أهدأ ساعة", False) + "</svg>"


def q_all(r, Wd=880, H=250):
    """النافذة كاملة وأعنف ساعة فيها — مرجع الأرقام."""
    W = r["w"]
    rg, med = ranges(W)
    hi = max(range(len(W)), key=lambda k: rg[k])
    assert len(W) == 29 and W[0]["d"] == "01:00" and W[-1]["d"] == "06:00"
    assert W[hi]["d"] == "15:00" and rg[hi] / med > 2.5, f"{W[hi]['d']} {rg[hi]/med:.2f}"
    svg, x, y, slot = _g(r, Wd, H)
    svg += mark(x(hi), slot, y(W[hi]["h"]), y(W[hi]["l"]), TEAL_D, 0.20)
    svg += tag(x(hi), y(W[hi]["h"]), y(W[hi]["l"]), xr(rg[hi] / med), TEAL_D)
    svg += RC._title(Wd, rt("النافذة كاملة"))
    svg += why(Wd, H, f'{ar(len(W))} ساعة · من ٠١:٠٠ إلى ٠٦:٠٠ بتوقيت الكويت', INK)
    svg += sm(Wd, H, f'أعنف ساعة ١٥:٠٠ بـ{xr(rg[hi]/med)} الوسيط ⁦{med:.4f}⁩')
    return svg + badge(Wd, "حدود النافذة", True) + "</svg>"



# ═════════════════ ٣ · تكلفة — الداو جونز · ١٥ دقيقة ═════════════════
# النافذة ٥٤: YM=F 15m · 2026-07-15 06:45 → 16:15 بتوقيت الكويت.
# درسُ هذه الوحدة **مسافةٌ سعرية** لا مدىً زمني، فمقياسها عمودي: كم نقطة
# بين الدخول والوقف، وكم تساوي تلك المسافة من شمعةٍ اعتيادية.


def vspan(xx, y0, y1, txt, col=INK, fs=16, H=None):
    """قوسٌ رأسي بطرفين — يقيس مسافةً سعرية، ووسمُه **تحت طرفه الأدنى**.

    كان الوسم في منتصف القوس، فيمرّ خطُّ القوس نفسه في وسط الحروف ويلتقي
    عندها الخطُّ الأفقي الذي يبدأ منه القياس (رُصد 2026-09-05 على «٣٠٪»
    في `p_mae`: القوس والخطّ والشمعة المظللة كلّها على الرقم). وتحت الطرف
    الأدنى فراغٌ في العادة — وهو موضع `tag` نفسه، فيُقرأ الرقم وسمَ شمعة.
    و`H` (ارتفاع اللوحة) يجعل القرار مقيساً: إن لم يبقَ تحت الطرف الأدنى
    ما يسع الوسم قبل الشريط السفلي، رُفع فوق الطرف الأعلى."""
    s = RC._SC[0]
    yl, yh = min(y0, y1), max(y0, y1)
    ly = yh + round(26 * s)
    if H is not None and ly + round(6 * s) > H - round(50 * s):
        ly = yl - round(14 * s)
    return (f'<line x1="{xx:.1f}" y1="{yl:.1f}" x2="{xx:.1f}" y2="{yh:.1f}" '
            f'stroke="{col}" stroke-width="1.6"/>'
            f'<line x1="{xx-7:.1f}" y1="{yl:.1f}" x2="{xx+7:.1f}" y2="{yl:.1f}" '
            f'stroke="{col}" stroke-width="2.4"/>'
            f'<line x1="{xx-7:.1f}" y1="{yh:.1f}" x2="{xx+7:.1f}" y2="{yh:.1f}" '
            f'stroke="{col}" stroke-width="2.4"/>'
            + htext(xx, ly, rt(txt), col, round(fs * s)))


def _risk(W, r):
    """مسافة المخاطرة بنفس حساب `run32_desk.plan_numbers` — لا حساباً آخر."""
    iob, ir = r["iob"], r["ir"]
    seg = W[:ir + 1]
    rng = max(c["h"] for c in seg) - min(c["l"] for c in seg)
    ent = round(W[ir]["c"])
    stp = round(min(W[j]["l"] for j in range(iob, ir + 1)) - rng * 0.006)
    return ent, stp, ent - stp


def c_dist(r, Wd=880, H=250):
    """مسافة المخاطرة نفسها: خمس وخمسون نقطة — والتكلفة تُقتطع منها."""
    W = r["w"]
    ent, stp, risk = _risk(W, r)
    assert risk == 55 and ent == 52791, f"{ent}/{stp}/{risk}"
    bp = risk / ent * 1e4
    assert 10.0 < bp < 11.0, f"{bp:.1f}"
    svg, x, y, slot = _g(r, Wd, H)
    svg += hl(x(0) - slot * .5, x(len(W) - 1) + slot * .5, y(ent), TEAL_D, 1.8)
    svg += hl(x(0) - slot * .5, x(len(W) - 1) + slot * .5, y(stp), RED, 1.8, "6 6")
    svg += band(x(0) - slot * .5, x(len(W) - 1) + slot * .5, y(ent), y(stp), TEAL, 0.10)
    # القوس يوضع حيث لا تعبر شمعةٌ الشريطَ: أبعدُ شمعةٍ قاعُها فوق الدخول.
    # وضعُه عند طرف اللوحة كان يحشره في الحافة ويركب على آخر الشموع.
    # ويبقى داخل اللوحة: وسمُه يُوسَّط على موضعه، فطرفُ اللوحة يقصّه.
    lo_, hi_ = 4, len(W) - 7
    clear = max(range(lo_, hi_), key=lambda j: W[j]["l"] - ent)
    assert W[clear]["l"] > ent, "لا موضع خالٍ للقوس فوق الشريط"
    svg += vspan(x(clear), y(ent), y(stp), f'{ar(risk)} نقطة', TEAL_D, H=H)
    svg += RC._title(Wd, rt("المسافة التي تدفع عليها"))
    svg += why(Wd, H, f'من {ent} إلى {stp} — {ar(risk)} نقطة', INK)
    svg += sm(Wd, H, f'أي ⁦{bp:.1f}⁩ نقطة أساس من السعر — وهذي وحدة قياسك')
    return svg + badge(Wd, "مسافة المخاطرة", True) + "</svg>"


def c_med(r, Wd=880, H=250):
    """المخاطرة تساوي شمعةً ونصف — لا عشر شمعات."""
    W = r["w"]
    rg, med = ranges(W)
    _, _, risk = _risk(W, r)
    k = risk / med
    assert 1.4 < k < 1.7, f"{k:.2f}"
    mid = min(range(len(W)), key=lambda j: abs(rg[j] - med))
    svg, x, y, slot = _g(r, Wd, H)
    svg += mark(x(mid), slot, y(W[mid]["h"]), y(W[mid]["l"]), GREY, 0.26)
    svg += tag(x(mid), y(W[mid]["h"]), y(W[mid]["l"]), f'⁦{med:.0f}⁩', GREY)
    svg += RC._title(Wd, rt("شمعة اعتيادية… ومخاطرتك"))
    svg += why(Wd, H, f'وسيط الشمعة ⁦{med:.0f}⁩ نقطة والمخاطرة {ar(risk)}', INK)
    svg += sm(Wd, H, f'أي {xr(k)} الشمعة — ومن هذي المسافة تُقتطع تكلفتك', TEAL_D)
    return svg + badge(Wd, "المخاطرة بالشمعات", True) + "</svg>"


def c_small(r, Wd=880, H=250):
    """أكثر الشمعات لا تقطع مسافة مخاطرتك أصلاً."""
    W = r["w"]
    rg, med = ranges(W)
    _, _, risk = _risk(W, r)
    small = [j for j in range(len(W)) if rg[j] < risk]
    assert len(small) == 31 and len(W) == 39, f"{len(small)}/{len(W)}"
    svg, x, y, slot = _g(r, Wd, H)
    for j in small:
        svg += mark(x(j), slot, y(W[j]["h"]), y(W[j]["l"]), GREY, 0.15)
    svg += RC._title(Wd, rt("أغلب الشمعات أقصر من وقفك"))
    svg += why(Wd, H, f'{ar(len(small))} شمعة من {ar(len(W))} مداها أقلّ من '
                      f'{ar(risk)} نقطة', GREY)
    svg += sm(Wd, H, f'أي {ar(round(len(small)/len(W)*100))}٪ — والتكلفة تُدفع عليها كلّها')
    return svg + badge(Wd, "شمعات أقصر من الوقف", False) + "</svg>"


def c_big(r, Wd=880, H=250):
    """شمعة واحدة حملت النتيجة — والتكلفة نفسها دُفعت قبلها."""
    W = r["w"]
    rg, med = ranges(W)
    hi = max(range(len(W)), key=lambda j: rg[j])
    k = rg[hi] / med
    assert W[hi]["d"] == "15:30" and 3.5 < k < 4.0, f"{W[hi]['d']} {k:.2f}"
    svg, x, y, slot = _g(r, Wd, H)
    svg += mark(x(hi), slot, y(W[hi]["h"]), y(W[hi]["l"]), TEAL_D, 0.22)
    svg += tag(x(hi), y(W[hi]["h"]), y(W[hi]["l"]), xr(k), TEAL_D)
    svg += RC._title(Wd, rt("شمعة واحدة حملت النتيجة"))
    svg += why(Wd, H, f'الساعة ١٥:٣٠ — مداها ⁦{rg[hi]:.0f}⁩ نقطة', TEAL_D)
    svg += sm(Wd, H, f'{xr(k)} وسيط الشمعة — ومع ذلك التكلفة دُفعت قبلها')
    return svg + badge(Wd, "شمعة النتيجة", True) + "</svg>"


def c_all(r, Wd=880, H=250):
    """النافذة كاملة بحدودها — مرجعُ كل رقمٍ في الوحدة."""
    W = r["w"]
    rg, med = ranges(W)
    tot = max(c["h"] for c in W) - min(c["l"] for c in W)
    assert len(W) == 39 and W[0]["d"] == "06:45" and W[-1]["d"] == "16:15"
    assert 235 < tot < 245, f"{tot:.0f}"
    svg, x, y, slot = _g(r, Wd, H)
    svg += hl(x(0) - slot * .5, x(len(W) - 1) + slot * .5, y(W[0]["c"]), GREY, 1.4, "5 6")
    svg += RC._title(Wd, rt("النافذة كاملة"))
    svg += why(Wd, H, f'{ar(len(W))} شمعة ١٥ دقيقة · من ٠٦:٤٥ إلى ١٦:١٥ بتوقيت الكويت', INK)
    svg += sm(Wd, H, f'مداها ⁦{tot:.0f}⁩ نقطة ووسيط الشمعة ⁦{med:.0f}⁩ — وإليهما تُنسب الأرقام')
    return svg + badge(Wd, "حدود النافذة", True) + "</svg>"


SETS = {"mayta": [k_four, k_quiet, k_gap, k_break, k_all],
        "taalluq": [q_one, q_wait, q_after, q_quiet, q_all],
        "taklifa": [c_dist, c_med, c_small, c_big, c_all]}
WIN = {"mayta": 49, "taalluq": 52, "taklifa": 54}


def unit_charts(slug):
    """يرجع (النافذة، الحالات الثابتة، الساقطة) — بالعقد نفسه في run31."""
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
