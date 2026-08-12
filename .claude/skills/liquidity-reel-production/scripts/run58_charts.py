# -*- coding: utf-8 -*-
"""جارتات تشغيلة ٥٨ — رسومُ قياسٍ لا رسومُ صفقات.

`run31_charts.CASES` السبع كلها **نماذج دخول**: زون ودخول ووقف وهدف. وهي
تصلح للوحدات الفنيّة، ولا تصلح لوحدات هذه التشغيلة الثلاث — نفسية
وأساسية ومالية. وضعُها عليها يخلق تناقضاً مرئياً: صفحةٌ عنوانها «الشارت
اللي تشوفه بالفيد ما عاش» وتحتها شارتٌ مكتوبٌ عليه «هني الدخلة الصح».

فبُنيت هنا جارتاتٌ **لا تدّعي صفقة**: كل واحدة تُعلّم على الشموع الرقمَ
الذي يقوله نصّ الوحدة نفسه — عدد الصاعدة والهابطة، أعرض خمس شمعات،
الشمعات التي غيّرت الهيكل، عمر المستوى… ولا دخول ولا وقف ولا هدف.

والقاعدة نفسها قائمة: **ما لا تُثبته الشموع لا يُرسم**. كل دالة تتحقّق من
رقمها بـ`assert` قبل أن تُخرج SVG، فإن اختلّ رقمٌ سقطت الدالةُ ولم تُجمَّل.

    python3 run58_charts.py        # يطبع أرقام الوحدات الثلاث
"""
import statistics as st

from reel_build import INK, TEAL, TEAL_D, RED, GREY, htext
from run15_charts import zbox, tick, hl, badge, frame
import run31_charts as RC

BULL = "#2E8CA6"

# ═════════════════ أوليات القياس ═════════════════


def _g(r, Wd, H):
    return frame(r["w"], Wd, H)


def ar(n):
    """أرقام عربية-هندية للأعداد والنِّسب داخل نصّ عربي — والأسعار تبقى لاتينية."""
    return str(n).translate(str.maketrans("0123456789", "٠١٢٣٤٥٦٧٨٩"))


def dd(d):
    """تاريخ معزول اتجاهياً: بلا العزل يقلب RTL شطرَي `MM-DD` فيصير ٢٣-٠٩."""
    return "\u2066" + d + "\u2069"


def rt(s):
    """سطرٌ عربي معزول باتجاه RTL.

    عنصر `<text>` في SVG اتجاهه الأصلي LTR، فالسطر المختلط (عربي + تاريخ
    لاتيني) تُرتَّب مقاطعُه من اليسار: «من ٠٢-٠٣ إلى…» تسبق ذيلَ الجملة
    بدل أن تليه. وعزل RLI…PDI يجعل السطر كلَّه مقطعاً واحداً اتجاهه RTL،
    فيصحّ ترتيب المقاطع ويبقى التاريخ داخله بترتيبه هو."""
    return "\u2067" + s + "\u2069"


def why(Wd, H, txt, col=INK):
    return RC._why(Wd, H, rt(txt), col)


def sm(Wd, H, txt, col=INK):
    return RC._sum(Wd, H, rt(txt), col)


def band(x0, x1, y0, y1, col=TEAL, op=0.13):
    return (f'<rect x="{x0:.1f}" y="{min(y0,y1):.1f}" width="{x1-x0:.1f}" '
            f'height="{abs(y1-y0):.1f}" fill="{col}" opacity="{op}"/>')


def mark(x, slot, ytop, ybot, col=TEAL_D, op=0.20):
    """عمودٌ شفّاف يضيء شمعةً بعينها — بلا حدٍّ يوهم بمستوى سعري."""
    return (f'<rect x="{x-slot*.46:.1f}" y="{ytop-6:.1f}" width="{slot*.92:.1f}" '
            f'height="{ybot-ytop+12:.1f}" fill="{col}" opacity="{op}"/>')


def span(x0, x1, yy, txt, col=INK, fs=16):
    """قوسٌ أفقي بطرفين — يقيس مدىً زمنياً لا سعرياً، فيُرسم فوق الشموع."""
    return (f'<line x1="{x0:.1f}" y1="{yy:.1f}" x2="{x1:.1f}" y2="{yy:.1f}" '
            f'stroke="{col}" stroke-width="1.6"/>'
            f'<line x1="{x0:.1f}" y1="{yy-7:.1f}" x2="{x0:.1f}" y2="{yy+7:.1f}" '
            f'stroke="{col}" stroke-width="2.4"/>'
            f'<line x1="{x1:.1f}" y1="{yy-7:.1f}" x2="{x1:.1f}" y2="{yy+7:.1f}" '
            f'stroke="{col}" stroke-width="2.4"/>'
            + htext((x0 + x1) / 2, yy - 11, rt(txt), col, round(fs * RC._SC[0])))


def num(x, y, n, col=TEAL_D):
    """شارة رقم لاتينية مائلة (§5) — مربّعة بزوايا صفر."""
    s = round(13 * RC._SC[0])
    return (f'<rect x="{x-s:.1f}" y="{y-s:.1f}" width="{2*s}" height="{2*s}" '
            f'fill="#EAF3F5" stroke="{col}" stroke-width="1.4"/>'
            + htext(x, y + s * 0.42, str(n), col, round(17 * RC._SC[0]), italic=True))


def i_of(W, d):
    return next(i for i, b in enumerate(W) if b["d"] == d)


def ranges(W):
    rg = [b["h"] - b["l"] for b in W]
    return rg, st.median(rg)


# ═════════════════ ١ · مقارنة — SPY يومي ═════════════════


def m_count(r, Wd=880, H=250):
    """١٩ صاعدة و١٨ هابطة، ومع ذلك النتيجة موجبة: رقمان من نافذة واحدة."""
    W = r["w"]
    up = sum(1 for b in W if b["c"] > b["o"])
    dn = sum(1 for b in W if b["c"] < b["o"])
    assert up == 19 and dn == 18 and up + dn == len(W), f"{up}/{dn}/{len(W)}"
    net = (W[-1]["c"] / W[0]["c"] - 1) * 100
    assert 3.9 <= net <= 4.0, f"الصافي {net:.2f}٪"
    svg, x, y, slot = _g(r, Wd, H)
    svg += hl(x(0) - slot * .5, x(len(W) - 1) + slot * .5, y(W[0]["c"]), GREY, 1.6, "6 6")
    svg += hl(x(0) - slot * .5, x(len(W) - 1) + slot * .5, y(W[-1]["c"]), TEAL_D, 1.8)
    svg += band(x(0) - slot * .5, x(len(W) - 1) + slot * .5,
                y(W[0]["c"]), y(W[-1]["c"]), TEAL, 0.10)
    svg += RC._title(Wd, rt("نفس النافذة تعطيك رقمين"))
    svg += why(Wd, H, f'{ar(up)} شمعة صاعدة · {ar(dn)} هابطة — أي ٥١٪', INK)
    svg += sm(Wd, H, f'ومع ذلك من أول إغلاق لآخر إغلاق: ⁦{net:+.2f}⁩٪', TEAL_D)
    return svg + badge(Wd, "قياس على الشموع", True) + "</svg>"


def m_top5(r, Wd=880, H=250):
    """أكبر خمس شمعات تحمل ٢٨٪ من مدى النافذة — وهي وحدها التي تُنشر."""
    W = r["w"]
    rg, med = ranges(W)
    top = sorted(range(len(W)), key=lambda k: -rg[k])[:5]
    share = 100 * sum(rg[k] for k in top) / sum(rg)
    assert 27 <= share <= 29, f"الحصة {share:.1f}٪"
    svg, x, y, slot = _g(r, Wd, H)
    for k in sorted(top):
        svg += mark(x(k), slot, y(W[k]["h"]), y(W[k]["l"]))
    svg += RC._title(Wd, rt("خمس شمعات من ٣٧"))
    svg += why(Wd, H, "المضاءة هي أعرض خمس شمعات في النافذة", TEAL_D)
    svg += sm(Wd, H, f'وتحمل وحدها {ar(round(share))}٪ من مجموع المدى')
    return svg + badge(Wd, "أعرض خمس شمعات", True) + "</svg>"


def m_quiet(r, Wd=880, H=250):
    """أهدأ يوم مقابل أعنف يوم — الأول لا صورة له تُنشر."""
    W = r["w"]
    rg, med = ranges(W)
    lo = min(range(len(W)), key=lambda k: rg[k])
    hi = max(range(len(W)), key=lambda k: rg[k])
    assert W[lo]["d"] == "01-21" and rg[lo] / med < 0.45
    assert rg[hi] / med > 2.9
    svg, x, y, slot = _g(r, Wd, H)
    svg += mark(x(lo), slot, y(W[lo]["h"]), y(W[lo]["l"]), GREY, 0.22)
    svg += mark(x(hi), slot, y(W[hi]["h"]), y(W[hi]["l"]), TEAL_D, 0.22)
    svg += htext(x(lo), y(W[lo]["h"]) - 22, f'⁦{rg[lo]/med:.0%}⁩', GREY,
                 round(17 * RC._SC[0]))
    svg += htext(x(hi), y(W[hi]["h"]) - 22, f'⁦{rg[hi]/med:.2f}⁩×', TEAL_D,
                 round(17 * RC._SC[0]))
    svg += RC._title(Wd, rt("يومٌ يُنشر ويومٌ لا أحد يذكره"))
    svg += why(Wd, H, f'أهدأ يوم {dd(W[lo]["d"])} · أعنف يوم {dd(W[hi]["d"])}', INK)
    svg += sm(Wd, H, f'وسيط المدى اليومي ⁦{med:.2f}⁩ نقطة — والنسب منسوبة إليه')
    return svg + badge(Wd, "الهادئ والصاخب", True) + "</svg>"


def m_dd(r, Wd=880, H=250):
    """الهبوط الداخلي ‎−٥٫٦٣٪ داخل نافذةٍ انتهت رابحة — الوسط المحذوف."""
    W = r["w"]
    pk = max(range(len(W)), key=lambda k: W[k]["h"])
    pk = max((k for k in range(len(W)) if W[k]["d"] == "02-16"), default=None)
    lo = min(range(pk, len(W)), key=lambda k: W[k]["l"])
    drop = (W[pk]["h"] - W[lo]["l"]) / W[pk]["h"] * 100
    assert 5.5 <= drop <= 5.7 and W[lo]["d"] == "03-04", f"{drop:.2f}٪ عند {W[lo]['d']}"
    svg, x, y, slot = _g(r, Wd, H)
    svg += band(x(pk) - slot * .5, x(lo) + slot * .5, y(W[pk]["h"]), y(W[lo]["l"]),
                RED, 0.10)
    svg += hl(x(pk) - slot * .5, x(lo) + slot * .5, y(W[pk]["h"]), RED, 1.8)
    svg += hl(x(pk) - slot * .5, x(lo) + slot * .5, y(W[lo]["l"]), RED, 1.8, "7 6")
    svg += RC._title(Wd, rt("الوسط الذي يُحذف من الملخّص"))
    svg += why(Wd, H, f'من قمّة {dd(W[pk]["d"])} إلى قاع {dd(W[lo]["d"])}: '
                          f'‎⁦−{drop:.2f}⁩٪', RED)
    svg += sm(Wd, H, "داخل نافذةٍ انتهت رابحة — وهذا ما لا تشوفه في الملخّص")
    return svg + badge(Wd, "الهبوط الداخلي", False) + "</svg>"


def m_streak(r, Wd=880, H=250):
    """أطول سلسلة بنفس اللون في النافذة كلها: ثلاث شمعات لا أكثر."""
    W = r["w"]
    sq = [1 if b["c"] > b["o"] else -1 for b in W]
    best = cur = 1
    end = 0
    for k in range(1, len(sq)):
        cur = cur + 1 if sq[k] == sq[k - 1] else 1
        if cur > best:
            best, end = cur, k
    assert best == 3, f"أطول سلسلة {best}"
    a = end - best + 1
    svg, x, y, slot = _g(r, Wd, H)
    for k in range(a, end + 1):
        svg += mark(x(k), slot, y(W[k]["h"]), y(W[k]["l"]), RED, 0.18)
    ytop = min(y(W[k]["h"]) for k in range(a, end + 1)) - 26
    svg += span(x(a) - slot * .5, x(end) + slot * .5, ytop,
                f'{ar(best)} شمعات — وهي الأطول', RED)
    svg += RC._title(Wd, rt("ولا سلسلة أسطورية"))
    svg += why(Wd, H, f'أطول تتابع بنفس اللون ينتهي {dd(W[end]["d"])}', RED)
    svg += sm(Wd, H, "على أداةٍ من أكثر أدوات العالم تداولاً — ثلاث فقط")
    return svg + badge(Wd, "أطول سلسلة", False) + "</svg>"


# ═════════════════ ٢ · مصادر — عقد S&P الآجل يومي ═════════════════


def s_four(r, Wd=880, H=250):
    """أربع شمعات من ٤٤ غيّرت الهيكل — والباقي لم ينقل مستوى."""
    W = r["w"]
    iob, bk, ir = r["iob"], r["bk"], r["ir"]
    pk = max(range(bk, ir), key=lambda k: W[k]["h"])
    ks = [iob, bk, pk, ir]
    assert ks == sorted(ks) and len(set(ks)) == 4
    assert [W[k]["d"] for k in ks] == ["09-23", "10-08", "10-12", "10-28"], \
        [W[k]["d"] for k in ks]
    svg, x, y, slot = _g(r, Wd, H)
    for n, k in enumerate(ks, 1):
        svg += mark(x(k), slot, y(W[k]["h"]), y(W[k]["l"]))
        svg += num(x(k), y(W[k]["h"]) - round(24 * RC._SC[0]), n)
    svg += RC._title(Wd, rt("أربع شمعات من ٤٤"))
    svg += why(Wd, H, "١ المنطقة · ٢ الكسر · ٣ قمّة الاندفاع · ٤ اللمسة", TEAL_D)
    svg += sm(Wd, H, f'أي {ar(round(100*4/len(W)))}٪ من النافذة — والباقي لم ينقل مستوى')
    return svg + badge(Wd, "ما غيّر الهيكل", True) + "</svg>"


def s_life(r, Wd=880, H=250):
    """المستوى المرسوم ٢٣ سبتمبر ظلّ مرجعاً ٢٥ شمعة — خمس أسابيع."""
    W = r["w"]
    iob, ir = r["iob"], r["ir"]
    zt, zb = W[iob]["h"], W[iob]["l"]
    assert W[ir]["l"] <= zt, "اللمسة لم تدخل المستوى"
    life = ir - iob
    assert life == 25, f"العمر {life} شمعة"
    svg, x, y, slot = _g(r, Wd, H)
    svg += zbox(x(iob) - slot * .6, y(zt), x(ir) + slot * .5, y(zb),
                "مستوى ٢٣ سبتمبر")
    svg += span(x(iob) - slot * .5, x(ir) + slot * .5,
                min(y(W[k]["h"]) for k in range(iob, ir + 1)) - 24,
                f'{ar(life)} شمعة — خمس أسابيع', TEAL_D)
    svg += RC._title(Wd, rt("معلومة واحدة عاشت خمس أسابيع"))
    svg += why(Wd, H, f'رُسم {dd(W[iob]["d"])} · وما زال مرجعاً {dd(W[ir]["d"])}', TEAL_D)
    svg += sm(Wd, H, "وبنفس المدّة مرّ عليك مئات العناوين — كلٌّ عمره ساعات")
    return svg + badge(Wd, "عمر المعلومة", True) + "</svg>"


def s_event(r, Wd=880, H=250):
    """يوم الحدث المعلوم مسبقاً كان عادياً، واليوم التالي هو الأعنف."""
    W = r["w"]
    rg, med = ranges(W)
    a, b = i_of(W, "11-03"), i_of(W, "11-04")
    assert b == a + 1 and rg[b] == max(rg), "٤ نوفمبر ليس الأعنف"
    ra, rb = rg[a] / med, rg[b] / med
    assert ra < 1.25 < 2.3 < rb, f"{ra:.2f} / {rb:.2f}"
    svg, x, y, slot = _g(r, Wd, H)
    svg += mark(x(a), slot, y(W[a]["h"]), y(W[a]["l"]), GREY, 0.24)
    svg += mark(x(b), slot, y(W[b]["h"]), y(W[b]["l"]), TEAL_D, 0.22)
    svg += htext(x(a), y(W[a]["h"]) - 24, f'⁦{ra:.2f}⁩×', GREY, round(17 * RC._SC[0]))
    svg += htext(x(b), y(W[b]["h"]) - 24, f'⁦{rb:.2f}⁩×', TEAL_D, round(17 * RC._SC[0]))
    svg += RC._title(Wd, rt("الحدث معلوم… والحركة بعده"))
    svg += why(Wd, H, "٣ نوفمبر ٢٠٢٠ تاريخ يعرفه العالم من سنة", INK)
    svg += sm(Wd, H, "أنت ما تتداول الخبر — تتداول رد الفعل عليه", TEAL_D)
    return svg + badge(Wd, "يوم الحدث وما بعده", True) + "</svg>"


def s_quiet(r, Wd=880, H=250):
    """أهدأ يوم في النافذة: نصف الحركة المعتادة وصفرُ تغيّر في الهيكل."""
    W = r["w"]
    rg, med = ranges(W)
    lo = min(range(len(W)), key=lambda k: rg[k])
    assert W[lo]["d"] == "10-23" and rg[lo] / med < 0.5
    svg, x, y, slot = _g(r, Wd, H)
    svg += mark(x(lo), slot, y(W[lo]["h"]), y(W[lo]["l"]), GREY, 0.26)
    svg += htext(x(lo), y(W[lo]["h"]) - 24, f'⁦{rg[lo]/med:.0%}⁩', GREY,
                 round(17 * RC._SC[0]))
    svg += RC._title(Wd, rt("يومٌ ما صار فيه شيء"))
    svg += why(Wd, H, f'{dd(W[lo]["d"])} — أهدأ يوم في النافذة', INK)
    svg += sm(Wd, H, "ومع ذلك أنتج كل مصدرٍ محتواه — لأن هذي مهنته")
    return svg + badge(Wd, "أهدأ يوم", False) + "</svg>"


def s_noise(r, Wd=880, H=250):
    """الضجيج بالعدد: كم شمعة تجاوزت الوسيط ولم تغيّر شيئاً."""
    W = r["w"]
    rg, med = ranges(W)
    iob, bk, ir = r["iob"], r["bk"], r["ir"]
    pk = max(range(bk, ir), key=lambda k: W[k]["h"])
    ks = {iob, bk, pk, ir}
    loud = [k for k in range(len(W)) if rg[k] > med and k not in ks]
    assert len(loud) > 12, f"الصاخبة {len(loud)}"
    svg, x, y, slot = _g(r, Wd, H)
    for k in loud:
        svg += mark(x(k), slot, y(W[k]["h"]), y(W[k]["l"]), GREY, 0.16)
    svg += RC._title(Wd, rt("شمعات صاخبة… وبلا أثر"))
    svg += why(Wd, H, f'{ar(len(loud))} شمعة تجاوزت الوسيط ولم تغيّر مستوى', GREY)
    svg += sm(Wd, H, "العنف ليس معلومة — المعلومة ما ينقل مستوىً على شارتك")
    return svg + badge(Wd, "ضجيج مقيس", False) + "</svg>"


# ═════════════════ ٣ · تبييت — عقد البنزين يومي ═════════════════


def t_nights(r, Wd=880, H=250):
    """٢٧ شمعة على الشارت بين تكوّن المنطقة واللمسة — و٤٠ ليلة على التقويم."""
    W = r["w"]
    iob, ir = r["iob"], r["ir"]
    bars = ir - iob
    assert bars == 27 and W[iob]["d"] == "02-03" and W[ir]["d"] == "03-15"
    svg, x, y, slot = _g(r, Wd, H)
    top = min(y(W[k]["h"]) for k in range(iob, ir + 1))
    # طرفا المدّة يضاءان وحدهما: تظليل السبعة والعشرين كلّها يبتلع الشموع
    for k in (iob, ir):
        svg += mark(x(k), slot, y(W[k]["h"]), y(W[k]["l"]))
    svg += span(x(iob) - slot * .5, x(ir) + slot * .5, top - 22,
                f'{ar(bars)} شمعة على الشارت', TEAL_D)
    svg += RC._title(Wd, rt("الشارت يعدّ جلسات وحسابك يعدّ ليالي"))
    svg += why(Wd, H, f'من {dd(W[iob]["d"])} إلى {dd(W[ir]["d"])}: {ar(bars)} شمعة… '
                          f'و⁦٤٠⁩ يوماً على التقويم', TEAL_D)
    svg += sm(Wd, H, "الفرق ⁦١٣⁩ يوماً لا تُرسم لها شموع — وتُحتسب عليك")
    return svg + badge(Wd, "٢٧ شمعة و٤٠ ليلة", True) + "</svg>"


def t_zone(r, Wd=880, H=250):
    """منطقة الأصل ٣ فبراير واللمسة ١٥ مارس — طرفا المدّة المدفوعة."""
    W = r["w"]
    iob, ir = r["iob"], r["ir"]
    zt, zb = W[iob]["o"], W[iob]["l"]
    assert W[ir]["l"] <= zt and W[ir]["c"] > zb, "اللمسة لم تدخل المنطقة"
    svg, x, y, slot = _g(r, Wd, H)
    svg += zbox(x(iob) - slot * .6, y(zt), x(ir) + slot * .5, y(zb), "منطقة الأصل")
    svg += mark(x(ir), slot, y(W[ir]["h"]), y(W[ir]["l"]), TEAL_D, 0.20)
    svg += RC._title(Wd, rt("طرفا المدّة التي تُدفع"))
    svg += why(Wd, H, f'المنطقة ⁦{zb:.3f}–{zt:.3f}⁩ · واللمسة {dd(W[ir]["d"])}', TEAL_D)
    svg += sm(Wd, H, "بينهما ⁦٤٠⁩ ليلة تقويمية — و≈⁦٥٠⁩ محسوبة بعد الأربعاء الثلاثي")
    return svg + badge(Wd, "من المنطقة إلى اللمسة", True) + "</svg>"


def t_break(r, Wd=880, H=250):
    """الكسر ثم قمّة الاندفاع: المسافة التي انتظرها الحساب ليلةً ليلة."""
    W = r["w"]
    bk, ir = r["bk"], r["ir"]
    pk = max(range(bk, ir), key=lambda k: W[k]["h"])
    assert W[bk]["d"] == "03-01" and W[pk]["d"] == "03-07"
    svg, x, y, slot = _g(r, Wd, H)
    svg += mark(x(bk), slot, y(W[bk]["h"]), y(W[bk]["l"]))
    svg += hl(x(bk) - slot * .6, x(pk) + slot * .5, y(W[pk]["h"]), TEAL_D, 1.8, "7 6")
    svg += tick(x(pk), y(W[pk]["h"]) - 18)
    svg += RC._title(Wd, rt("بين الكسر والقمّة عشر شمعات"))
    svg += why(Wd, H, f'الكسر {dd(W[bk]["d"])} · قمّة الاندفاع {dd(W[pk]["d"])} '
                          f'عند {W[pk]["h"]:.3f}', TEAL_D)
    svg += sm(Wd, H, "عشر شمعات على الشارت — أربع عشرة ليلة على الحساب")
    return svg + badge(Wd, "الكسر والقمّة", True) + "</svg>"


def t_range(r, Wd=880, H=250):
    """أعنف يوم وأهدأ يوم — لأن كلفة الليلة لا تتبع حركة اليوم."""
    W = r["w"]
    rg, med = ranges(W)
    hi = max(range(len(W)), key=lambda k: rg[k])
    lo = min(range(len(W)), key=lambda k: rg[k])
    assert W[hi]["d"] == "03-15" and W[lo]["d"] == "03-08"
    svg, x, y, slot = _g(r, Wd, H)
    svg += mark(x(hi), slot, y(W[hi]["h"]), y(W[hi]["l"]), TEAL_D, 0.22)
    svg += mark(x(lo), slot, y(W[lo]["h"]), y(W[lo]["l"]), GREY, 0.26)
    svg += htext(x(hi), y(W[hi]["h"]) - 24, f'⁦{rg[hi]/med:.2f}⁩×', TEAL_D,
                 round(17 * RC._SC[0]))
    svg += htext(x(lo), y(W[lo]["h"]) - 24, f'⁦{rg[lo]/med:.0%}⁩', GREY,
                 round(17 * RC._SC[0]))
    svg += RC._title(Wd, rt("اليوم يتغيّر… والليلة بسعرها"))
    svg += why(Wd, H, f'أعنف يوم {dd(W[hi]["d"])} · أهدأ يوم {dd(W[lo]["d"])}', INK)
    svg += sm(Wd, H, f'وسيط المدى ⁦{med:.4f}⁩ — والسواب لا يسأل عن أيّ منها')
    return svg + badge(Wd, "المدى اليومي", True) + "</svg>"


def t_wed(r, Wd=880, H=250):
    """نافذة الشارت كاملة بحدودها المعلنة — مرجعُ كل رقمٍ في الوحدة."""
    W = r["w"]
    assert len(W) == 46 and W[0]["d"] == "01-25" and W[-1]["d"] == "03-30"
    rg, med = ranges(W)
    svg, x, y, slot = _g(r, Wd, H)
    svg += hl(x(0) - slot * .5, x(len(W) - 1) + slot * .5, y(W[0]["c"]), GREY, 1.4, "5 6")
    svg += RC._title(Wd, rt("النافذة كاملة بحدودها"))
    svg += why(Wd, H, f'{ar(len(W))} شمعة · من {dd(W[0]["d"])} إلى {dd(W[-1]["d"])}', INK)
    svg += sm(Wd, H, f'وسيط المدى اليومي ⁦{med:.4f}⁩ — وكل رقمٍ في الدليل منسوب إليه')
    return svg + badge(Wd, "حدود النافذة", True) + "</svg>"


SETS = {"muqarana": [m_count, m_top5, m_quiet, m_dd, m_streak],
        "masader": [s_four, s_life, s_event, s_quiet, s_noise],
        "tabyeet": [t_nights, t_zone, t_break, t_range, t_wed]}
WIN = {"muqarana": 40, "masader": 29, "tabyeet": 38}


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
        print(f'{slug:<9} {r["slug"]:<38} ثابتة {len(ok)}/{len(SETS[slug])}'
              + ("" if not dr else " · سقط " + ", ".join(f"{a}: {b}" for a, b in dr)))
