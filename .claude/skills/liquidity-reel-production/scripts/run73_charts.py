# -*- coding: utf-8 -*-
"""جارتات تشغيلة ٧٣ — نافذتان حقيقيتان وثلاثُ جداولِ عدّ.

    نصيب  ← ٧٨ · فول الصويا · ساعة · 2025-09-24 · ٤٤ شمعة · zone
    كثافة ← ٧٥ · البي إن بي · ساعة · 2025-11-07 · ٤٠ شمعة

و«تأجيل» و«خمول» و«بند» حسابٌ محضٌ بافتراضاتٍ معلنة، فلوحاتُها جداولُ
عدٍّ بلا شموع وعليها وحدَها شارةُ «مثال تخطيطي» (قاعدة ٧١).

🔒 اصطلاحُ «فوق ضِعف الوسيط» معلَنٌ هنا لا مضمَر: العتبةُ `>` حرفياً.
شمعةٌ واحدة في النافذة ٧٨ مداها **ضِعفُ الوسيط بالضبط**، فبـ`>=` يصير
العددُ ثمانياً لا سبعاً — والفرقُ اصطلاحُ كاتبه لا خبرُ السوق، فيُعلن.

    python3 run73_charts.py
"""
import statistics as st

from reel_build import INK, TEAL, TEAL_D, RED, htext
from run15_charts import hl, badge, frame
import run31_charts as RC
from run58_charts import ar, rt, sm, band, mark
from run59_charts import spanx, vspan, xr
from run71_charts import (MUTE, CREAM, _fs, _blank, bar, dot, _cols, _steps,
                          _sw_hi, _sw_lo)
from run72_charts import _bars, _sg


# ═════════════════════════════════════════════════════════════════
# ١ · «نصيب» — توزيعُ مجموعِ المدى على النافذة (الموضوع ١٧٦)
#     المرجع: الفتيل (أعلى ناقص أدنى) · النافذة: كاملةً · التعادل: الأقدمُ أولاً
# ═════════════════════════════════════════════════════════════════
N_WIN = 78
RN = RC.win(N_WIN)
WN = RN["w"]
N_N = len(WN)
N_RNG = [(c["h"] - c["l"], i) for i, c in enumerate(WN)]
N_MED = st.median(v for v, _ in N_RNG)
N_TOT = sum(v for v, _ in N_RNG)
#: مرتَّبةٌ تنازلياً، والمتساويتان بالأقدم أولاً فلا يتغيّر النصيبُ بترتيبٍ عشوائي.
N_SRT = sorted(N_RNG, key=lambda t: (-t[0], t[1]))
N_TOP3 = [i for _, i in N_SRT[:3]]
N_S3 = sum(v for v, _ in N_SRT[:3]) / N_TOT
#: العتبةُ `>` حرفياً — وشمعةٌ واحدة تقع عليها بالضبط فتخرج، وهذا معلَن.
N_BIG = [i for v, i in N_RNG if v > 2 * N_MED]
N_EQ = [i for v, i in N_RNG if abs(v - 2 * N_MED) < 1e-9]
N_SBIG = sum(WN[i]["h"] - WN[i]["l"] for i in N_BIG) / N_TOT
N_QUIET = [i for _, i in N_SRT[N_N // 2:]]
N_SQ = sum(WN[i]["h"] - WN[i]["l"] for i in N_QUIET) / N_TOT
N_MAX = N_SRT[0][0] / N_MED
N_MIN = N_SRT[-1][0] / N_MED
N_SPAN = (max(c["h"] for c in WN) - min(c["l"] for c in WN)) / N_MED
N_WALK = N_TOT / N_MED
assert N_N == 44 and abs(N_MED - 2.5) < 1e-9, (N_N, N_MED)
assert len(N_BIG) == 7 and len(N_EQ) == 1, (N_BIG, N_EQ)
assert round(N_S3 * 100) == 22 and round(N_SBIG * 100) == 37, (N_S3, N_SBIG)
assert round(N_SQ * 100) == 26 and len(N_QUIET) == 22, (N_SQ, len(N_QUIET))
assert round(N_MAX, 1) == 5.7 and round(N_MIN, 1) == 0.3, (N_MAX, N_MIN)
assert round(N_SPAN, 1) == 6.6 and round(N_WALK, 1) == 61.9, (N_SPAN, N_WALK)


def _gn(Wd, H):
    return frame(WN, Wd, H, pad=0.08, pb=64)


def _dim(svg, x, y, slot, keep):
    """كلُّ ما ليس في `keep` يُطفأ — فالعينُ تقع على المقيس لا على الباقي."""
    for j in range(N_N):
        if j not in keep:
            svg += mark(x(j), slot, y(WN[j]["h"]), y(WN[j]["l"]), MUTE, 0.16)
    return svg


def n_med(r=None, Wd=880, H=250):
    """١ · الوحدةُ وسيطُ المدى — فلا يُطبع سعر."""
    svg, x, y, slot = _gn(Wd, H)
    big, sml = N_SRT[0][1], N_SRT[-1][1]
    svg = _dim(svg, x, y, slot, {big, sml})
    svg += mark(x(big), slot, y(WN[big]["h"]), y(WN[big]["l"]), TEAL, 0.34)
    svg += mark(x(sml), slot, y(WN[sml]["h"]), y(WN[sml]["l"]), RED, 0.34)
    svg += htext(x(big), y(WN[big]["h"]) - _fs(16), xr(N_MAX), TEAL_D, _fs(26))
    svg += htext(x(sml), y(WN[sml]["l"]) + _fs(30), xr(N_MIN), RED, _fs(24))
    svg += badge(Wd, "سوقٌ حقيقي", True)
    svg += RC._title(Wd, rt("وسيطُ المدى وحدةُ القياس"))
    svg += RC._why(Wd, H, 'أصغرُ شمعةٍ ٠.٣× الوسيط وأكبرُها ٥.٧× — '
                          'تسعةَ عشرَ ضِعفاً بينهما', TEAL_D)
    svg += sm(Wd, H, "الوحدةُ وسيطُ المدى لا سعرٌ مطبوع")
    return svg + "</svg>"


def n_three(r=None, Wd=880, H=250):
    """٢ · أكبرُ ثلاثٍ — سبعةٌ بالمئة من الشمعات واثنتان وعشرون من المدى."""
    svg, x, y, slot = _gn(Wd, H)
    svg = _dim(svg, x, y, slot, set(N_TOP3))
    for i in N_TOP3:
        svg += mark(x(i), slot, y(WN[i]["h"]), y(WN[i]["l"]), TEAL, 0.34)
    svg += htext(x(sum(N_TOP3) / 3), y(max(WN[i]["h"] for i in N_TOP3)) - _fs(18),
                 f'{ar(3)} شمعات = {ar(round(N_S3 * 100))}٪ من المدى',
                 TEAL_D, _fs(25))
    svg += badge(Wd, "سوقٌ حقيقي", True)
    svg += RC._title(Wd, rt(f'أكبرُ ثلاثٍ: {ar(round(N_S3 * 100))}٪ من المجموع'))
    svg += RC._why(Wd, H, 'أكبرُ ثلاثٍ ٧٪ من الشمعات و٢٢٪ من المدى — '
                          'والهادئاتُ نصفُ النافذة', TEAL_D)
    svg += sm(Wd, H, "مرتَّبةٌ تنازلياً والأقدمُ أوّلاً")
    return svg + "</svg>"


def n_big(r=None, Wd=880, H=250):
    """٣ · سبعٌ فوق ضِعف الوسيط — سُدسُ النافذة وثلثُ مداها (البطل)."""
    svg, x, y, slot = _gn(Wd, H)
    svg = _dim(svg, x, y, slot, set(N_BIG))
    for i in N_BIG:
        svg += mark(x(i), slot, y(WN[i]["h"]), y(WN[i]["l"]), TEAL, 0.32)
        svg += dot(x(i), y(WN[i]["h"]) - _fs(10), TEAL_D, _fs(4))
    svg += htext(Wd * 0.30, y(max(c["h"] for c in WN)) + _fs(10),
                 f'{ar(len(N_BIG))} من {ar(N_N)} = {ar(round(N_SBIG * 100))}٪',
                 TEAL_D, _fs(27))
    svg += badge(Wd, "سوقٌ حقيقي", True)
    svg += RC._title(Wd, rt(f'{ar(len(N_BIG))} شمعات نصيبُها '
                            f'{ar(round(N_SBIG * 100))}٪'))
    svg += RC._why(Wd, H, 'سُدسُ النافذة يحمل أكثرَ من ثلثِ مداها لأنّ '
                          'المدى لا يتوزّع بالتساوي', TEAL_D)
    svg += sm(Wd, H, "العتبةُ فوق ضِعف الوسيط حرفياً")
    return svg + "</svg>"


def n_quiet(r=None, Wd=880, H=250):
    """٤ · النصفُ الهادئ: نصفُ الوقت وربعُ الحركة."""
    svg, x, y, slot = _gn(Wd, H)
    svg = _dim(svg, x, y, slot, set(N_QUIET))
    for i in N_QUIET:
        svg += mark(x(i), slot, y(WN[i]["h"]), y(WN[i]["l"]), MUTE, 0.40)
    svg += htext(Wd * 0.32, y(max(c["h"] for c in WN)) + _fs(10),
                 f'{ar(len(N_QUIET))} شمعة = {ar(round(N_SQ * 100))}٪',
                 INK, _fs(27))
    svg += badge(Wd, "سوقٌ حقيقي", True)
    svg += RC._title(Wd, rt("نصفُ الشمعات وربعُ المدى"))
    svg += RC._why(Wd, H, 'اثنتان وعشرون شمعةً هادئةً نصيبُها ٢٦٪ — '
                          'نصفُ الوقت وربعُ الحركة', RED)
    svg += sm(Wd, H, "النصفُ الأدنى مدىً من النافذة")
    return svg + "</svg>"


def n_rule(r=None, Wd=880, H=250):
    """٥ · المسافةُ الممشيّة مقابل المقطوعة."""
    return _bars(Wd, H,
                 [("الممشيّة", round(N_WALK, 1), True),
                  ("المقطوعة", round(N_SPAN, 1), False)],
                 f'مشى {xr(N_WALK)} وانتقل {xr(N_SPAN)}',
                 'مشى ٦١.٩× وانتقل ٦.٦× — فتسعةُ أضعافٍ ذهابٌ وإيابٌ '
                 'لا انتقال',
                 "ونصفُ المجموع من اثنتي عشرةَ شمعة",
                 tag="سوقٌ حقيقي", col=TEAL_D, unit="×")


# ═════════════════════════════════════════════════════════════════
# ٢ · «كثافة» — أطرافُ السوينق لكل عشر شمعات (الموضوع ١٥٨)
#     البي إن بي · ساعة · 2025-11-07 · ٤٠ شمعة · سوقٌ حقيقي
# ═════════════════════════════════════════════════════════════════
K_WIN = 75
RK = RC.win(K_WIN)
WK = RK["w"]
K_N = len(WK)
K_HI, K_LO = _sw_hi(WK), _sw_lo(WK)
K_END = sorted(K_HI + K_LO)
K_P = {i: (WK[i]["h"] if i in K_HI else WK[i]["l"]) for i in K_END}
K_BINS = [(k, sum(1 for e in K_END if k <= e < k + 10)) for k in range(0, K_N - 9, 10)]
K_CNT = [c for _, c in K_BINS]
K_GAP = [K_END[i + 1] - K_END[i] for i in range(len(K_END) - 1)]
#: «اختُبر» = بلغه السعرُ بعد ثلاثِ شمعاتٍ من تكوّنه فأكثر — والرقمُ نفسُه
#: يخرج بالبدء من `i+1` أو `i+2`، فهو غيرُ حسّاسٍ للاصطلاح.
K_TST, K_WAIT = [], []
for e in K_END:
    hit = [j for j in range(e + 3, K_N) if WK[j]["l"] <= K_P[e] <= WK[j]["h"]]
    if hit:
        K_TST.append(e); K_WAIT.append(hit[0] - e)
K_NEV = [e for e in K_END if e not in K_TST]
assert K_N == 40 and len(K_END) == 9, (K_N, K_END)
assert (len(K_HI), len(K_LO)) == (5, 4), (K_HI, K_LO)
assert K_CNT == [2, 4, 2, 1], K_CNT
assert len(K_TST) == 7 and round(len(K_TST) / len(K_END) * 100) == 78
assert (min(K_GAP), max(K_GAP)) == (1, 7) and st.median(K_GAP) == 4, K_GAP
assert st.median(K_WAIT) == 11, K_WAIT
#: والاثنان اللذان لم يُختبرا قاعان، وأحدهما آخرُ طرفٍ في النافذة فلم يبقَ
#: له متّسعٌ للاختبار — غيرُ مختبَرٍ بحكم الحافّة لا بحكم السوق.
assert all(e in K_LO for e in K_NEV), K_NEV


def _gk(Wd, H):
    return frame(WK, Wd, H, pad=0.08, pb=64)


def k_ends(r=None, Wd=880, H=250):
    """١ · تسعةُ أطرافٍ بشرطٍ واحد."""
    svg, x, y, slot = _gk(Wd, H)
    for e in K_END:
        svg += dot(x(e), y(K_P[e]), TEAL_D if e in K_HI else RED, _fs(5.2))
    svg += badge(Wd, "سوقٌ حقيقي", True)
    svg += RC._title(Wd, rt(f'{ar(len(K_END))} أطراف في {ar(K_N)} شمعة'))
    svg += RC._why(Wd, H, 'تسعةُ أطرافٍ في أربعين شمعة: خمسُ قممٍ '
                          'وأربعةُ قيعانٍ بشرطٍ واحد', TEAL_D)
    svg += sm(Wd, H, "شمعتان من كلِّ جهةٍ شرطاً ثابتاً")
    return svg + "</svg>"


def k_ten(r=None, Wd=880, H=250):
    """٢ · التوزيعُ لا العدد — أربعةٌ في عشرٍ وواحدٌ في عشر (البطل)."""
    svg, x, y, slot = _gk(Wd, H)
    top = max(c["h"] for c in WK)
    bot = min(c["l"] for c in WK)
    for k, c in K_BINS:
        a, b = x(k) - slot * .5, x(min(k + 9, K_N - 1)) + slot * .5
        on = c == max(K_CNT)
        svg += band(a, b, y(top), y(bot), TEAL if on else MUTE,
                    0.16 if on else 0.07)
        svg += htext((a + b) / 2, y(top) - _fs(12), ar(c),
                     TEAL_D if on else MUTE, _fs(30))
    for e in K_END:
        svg += dot(x(e), y(K_P[e]), INK, _fs(4.4))
    svg += badge(Wd, "سوقٌ حقيقي", True)
    svg += RC._title(Wd, rt(" ثم ".join(ar(c) for c in K_CNT)))
    svg += RC._why(Wd, H, 'أربعةُ أطرافٍ في عشرِ شمعاتٍ وواحدٌ في عشرٍ '
                          'أخرى — لا متوسّطَ يصفهما', TEAL_D)
    svg += sm(Wd, H, "الأكثفُ أربعةُ أضعافِ الأهدأ")
    return svg + "</svg>"


def k_gap(r=None, Wd=880, H=250):
    """٣ · الفجوةُ بين طرفٍ وطرف: من شمعةٍ إلى سبع."""
    items = [(f'{ar(a)}←{ar(b)}', b - a, (b - a) in (min(K_GAP), max(K_GAP)))
             for a, b in zip(K_END, K_END[1:])]
    return _bars(Wd, H, items,
                 f'من شمعةٍ إلى {ar(max(K_GAP))} — والوسيط {ar(int(st.median(K_GAP)))}',
                 'أقصرُ فجوةٍ شمعةٌ وأطولُها سبع — لأنّ الطرفَ إيقاعٌ '
                 'لا ساعةٌ تدقّ',
                 "ووسيطُ الفجوات أربعُ شمعات",
                 tag="سوقٌ حقيقي", col=TEAL_D)


def k_test(r=None, Wd=880, H=250):
    """٤ · سبعةٌ من تسعةٍ اختُبرن — والباقيان قاعان."""
    svg, x, y, slot = _gk(Wd, H)
    for e in K_END:
        on = e in K_TST
        svg += hl(x(e) - slot * .5, x(K_N - 1) + slot * .5, y(K_P[e]),
                  TEAL_D if on else RED, 2.2 if on else 3.0)
        svg += dot(x(e), y(K_P[e]), TEAL_D if on else RED, _fs(5))
    svg += htext(Wd * 0.28, y(max(c["h"] for c in WK)) + _fs(10),
                 f'{ar(len(K_TST))} من {ar(len(K_END))}', TEAL_D, _fs(28))
    svg += badge(Wd, "سوقٌ حقيقي", True)
    svg += RC._title(Wd, rt(f'{ar(len(K_TST))} من {ar(len(K_END))} اختُبرن'))
    svg += RC._why(Wd, H, 'سبعةٌ من تسعةٍ بلغها السعرُ بعد ثلاث شمعاتٍ '
                          'فأكثرَ من تكوّنها', TEAL_D)
    svg += sm(Wd, H, "ووسيطُ الانتظار إحدى عشرةَ شمعة")
    return svg + "</svg>"


def k_rule(r=None, Wd=880, H=250):
    """٥ · التنبيهُ عند الطرف لا ملاحقتُه."""
    return _steps(Wd, H,
                  [(ar(len(K_END)), "أطرافٌ مخزوناً"),
                   (ar(len(K_TST)), "اختُبرت"),
                   (ar(int(st.median(K_WAIT))), "وسيطُ الانتظار")],
                  "نبّه عند الطرف ولا تلاحقه",
                  'كثيفةُ الأطرافِ بطيئةُ الاختبار — فالتنبيهُ عند الطرفِ '
                  'لا ملاحقتُه',
                  "تسعةٌ مخزوناً وسبعةٌ اختُبرت", hi=2, tag="سوقٌ حقيقي")


# ═════════════════════════════════════════════════════════════════
# ٣ · «تأجيل» — فجوةُ المراجعة (الموضوع ١٦٠) · دفترٌ مصمَّمٌ معلن
# ═════════════════════════════════════════════════════════════════
#: الافتراضاتُ معلنةٌ ولا يُدّعى أنها مقيسةٌ من دفترٍ حقيقي: ستّون صفقةً في
#: اثني عشر أسبوعاً بخمسٍ أسبوعياً، ومراجعتان تغطّي كلٌّ آخرَ تسعِ صفقات.
J_TOT, J_WK, J_PER, J_COVER = 60, 12, 5, 9
J_REV = [(6 * J_PER - J_COVER, 6 * J_PER), (12 * J_PER - J_COVER, 12 * J_PER)]
J_SEEN = sum(b - a for a, b in J_REV)
J_BLIND = [(0, J_REV[0][0]), (J_REV[0][1], J_REV[1][0])]
J_BLK = [b - a for a, b in J_BLIND]
J_ERR = J_TOT // 5
J_IN = 4
J_OUT = J_ERR - J_IN
assert J_SEEN == 18 and round(J_SEEN / J_TOT * 100) == 30
assert J_BLK == [21, 21], J_BLK
assert (J_ERR, J_IN, J_OUT) == (12, 4, 8)


def j_gap(r=None, Wd=880, H=250):
    """١ · كتلتان كلٌّ إحدى وعشرون صفقةً لم تُقرأ."""
    return _bars(Wd, H,
                 [("الكتلة الأولى", J_BLK[0], True),
                  ("الكتلة الثانية", J_BLK[1], True),
                  ("المراجَع", J_SEEN, False)],
                 f'{ar(J_SEEN)} من {ar(J_TOT)} انفتحت — والباقي لا',
                 'كتلتان كلٌّ منهما إحدى وعشرون صفقةً لم تدخلا مراجعةً أصلاً',
                 "ستّون صفقةً ومراجعتان اثنتان", tag="مثال تخطيطي")


def j_repeat(r=None, Wd=880, H=250):
    """٢ · اثنتا عشرةَ نسخةً وصلك منها أربع."""
    # و`_cols` يميّز بالهوية لا بالتساوي (`d is hi`): قاموسٌ جديدٌ بالقيم
    # نفسِها لا يُطابق صفَّه، فيخرج العمودان بلا إبراز (رُئي في هيرو ٧٣).
    inn = dict(nm="داخل المراجَع", n=J_IN, w=J_IN)
    return _cols(Wd, H,
                 [dict(nm="خارج المراجَع", n=J_OUT, w=0), inn], inn,
                 f'{ar(J_ERR)} نسخة — شفت {ar(J_IN)}',
                 'اثنتا عشرةَ نسخةً من غلطٍ واحد، أربعٌ داخل المراجَع '
                 'وثمانٍ خارجه',
                 "واحدةٌ من كلِّ خمسِ صفقات", tag="مثال تخطيطي", col=RED)


def j_cost(r=None, Wd=880, H=250):
    """٣ · المراجعةُ كشفت ولم تُنقص — والنتيجةُ السالبةُ تُنشر."""
    return _steps(Wd, H,
                  [(ar(J_ERR), "نسخةً وقعت"),
                   (ar(J_IN), "دخلت المراجعة"),
                   (ar(J_OUT), "ما انقرأت")],
                  "المراجعةُ تكشف ولا تَعِد بأثر",
                  'المعدّل داخلَ المراجَع وخارجَه متقارب — فالمقيسُ الفجوةُ '
                  'لا الأثر',
                  "والفرقُ بين النصفين نسختان", hi=2, tag="مثال تخطيطي")


def j_batch(r=None, Wd=880, H=250):
    """٤ · الدفعةُ الكبيرةُ تُقرأ ثلثُها."""
    big = dict(nm="دفعةٌ كبيرة", n=30, w=9)
    return _cols(Wd, H, [big], big,
                 f'{ar(9)} من {ar(30)} تُقرأ فعلاً',
                 'تسعٌ تُقرأ من ثلاثين لأنّ حالتَك وقتَ القرار تتبخّر '
                 'قبل الدفعة',
                 "الدفعةُ الكبيرةُ تُقرأ ثلثُها", tag="مثال تخطيطي", col=RED)


def j_rule(r=None, Wd=880, H=250):
    """٥ · راجِع بعددِ صفقاتٍ لا بعددِ أيام."""
    return _steps(Wd, H,
                  [(ar(J_PER), "صفقات"), ("عدّاد", "لا رزنامة"),
                   (ar(4), "أقصى الفجوة")],
                  "عدّادٌ كلَّ خمسِ صفقات",
                  'كلُّ خمسِ صفقاتٍ يجعل أقصى الفجوة أربعاً بدل إحدى وعشرين',
                  "عدّادٌ لا موعدٌ في الرزنامة", hi=2, tag="مثال تخطيطي")


# ═════════════════════════════════════════════════════════════════
# ٤ · «خمول» — رسمُ الخمول بوحدة الصفقات (الموضوع ١٦٥)
# ═════════════════════════════════════════════════════════════════
#: ثلاثةُ افتراضاتٍ معلنة، ولا يُدّعى أنها مقيسةٌ من كشفِ حساب.
X_FEE, X_RISK, X_AVG, X_MO = 0.5, 1.0, 0.25, 10
X_H6 = X_FEE * 6
X_S6 = X_H6 / X_RISK
X_T6 = X_S6 / X_AVG
X_H12 = X_FEE * 12
X_T12 = (X_H12 / X_RISK) / X_AVG
X_SHARE = X_T6 / (6 * X_MO)
assert (X_H6, X_S6, X_T6) == (3.0, 3.0, 12.0)
assert (X_H12, X_T12) == (6.0, 24.0)
assert round(X_SHARE * 100) == 20


def x_draw(r=None, Wd=880, H=250):
    """١ · الرسمُ يُقيَّد بالشهر الذي لم تشتغل فيه."""
    return _steps(Wd, H,
                  [(f'{ar("0.5")}٪', "عن كلِّ شهر"), (ar(6), "أشهرِ غياب"),
                   (f'{ar(3)}٪', "تُقيَّد عليك")],
                  "الفاتورةُ تمشي وانت واقف",
                  'نصفُ بالمئة عن كلِّ شهرٍ بلا صفقةٍ تصير ثلاثةً في نصف '
                  'سنةٍ بالجمع',
                  "افتراضٌ معلن لا رقمٌ مقيس", hi=2, tag="مثال تخطيطي")


def x_stops(r=None, Wd=880, H=250):
    """٢ · ثلاثةٌ بالمئة على مخاطرةٍ واحدة = ثلاثُ وقفات."""
    return _bars(Wd, H,
                 [("رسمُ ستّةِ أشهر", X_H6, False),
                  ("مخاطرةُ الصفقة", X_RISK, False),
                  ("وقفاتٌ كاملة", X_S6, True)],
                 f'{ar(int(X_H6))}٪ على {ar(int(X_RISK))}٪ = '
                 f'{ar(int(X_S6))} وقفات',
                 'ثلاثةٌ بالمئة على مخاطرةٍ واحدةٍ بالمئة تساوي ثلاثَ '
                 'وقفاتٍ كاملة',
                 "الوقفُ وحدةٌ تعرف حجمَها", tag="مثال تخطيطي", col=RED)


def x_trades(r=None, Wd=880, H=250):
    """٣ · وثلاثُ وقفاتٍ على متوسّطِ ربعٍ = اثنتا عشرةَ صفقة (البطل)."""
    return _steps(Wd, H,
                  [(ar(int(X_S6)), "وقفات"),
                   (f'{ar("0.25")}R', "متوسّطُ صفقتك"),
                   (ar(int(X_T6)), "صفقةً وسطية")],
                  f'{ar(int(X_T6))} صفقةً تعوّض غيابَك',
                  'ثلاثُ وقفاتٍ على متوسّطِ ربعِ مخاطرةٍ تساوي اثنتي عشرةَ '
                  'صفقةً وسطية',
                  "وبعشرٍ في الشهر: شهرٌ وربع", hi=2, tag="مثال تخطيطي")


def x_two(r=None, Wd=880, H=250):
    """٤ · حسابان برأس مالٍ واحد — والفاتورةُ تتناسب مع الغياب."""
    return _bars(Wd, H,
                 [("نشطٌ سنةً", 0.0, False),
                  ("نصفُ سنةٍ غياباً", round(X_T6, 0), True)],
                 f'صفرٌ مقابل {ar(int(X_T6))} صفقة',
                 'الفاتورةُ تتناسب مع غيابك لا مع نشاطك فيكبر نصيبُها '
                 'كلّما قلَّ شغلك',
                 "صفرٌ للنشط وعشرون بالمئة للخامل",
                 tag="مثال تخطيطي", col=RED)


def x_rule(r=None, Wd=880, H=250):
    """٥ · قرارُ الغياب يُكتب قبل الغياب."""
    return _steps(Wd, H,
                  [("سحب", "تُقفل الحساب"), ("مبلغٌ صغير", "يُبقيه حيّاً"),
                   ("قبولٌ معلن", "تعرف ثمنَه")],
                  "اكتب قرارَك قبل ما تغيب",
                  'ثلاثةُ خياراتٍ معلنةٍ قبل الغياب: سحبٌ أو مبلغٌ صغيرٌ '
                  'أو قبولُ الفاتورة',
                  "القرارُ يُكتب قبل الانقطاع", hi=2, tag="مثال تخطيطي")


# ═════════════════════════════════════════════════════════════════
# ٥ · «بند» — اختبارُ تعديلٍ ببندٍ واحد (الموضوع ١٧١) · جدولُ عدٍّ معلن
# ═════════════════════════════════════════════════════════════════
#: هدفٌ ضِعفُ المخاطرة، والشمعةُ الجامعة تُعدّ وقفاً — اصطلاحُ ٧٢ مطبَّقٌ
#: على القاعدتين بالتساوي فلا يفرّق بينهما إلا البندُ المقصود.
B_A_N, B_A_W = 80, 30
B_B_N, B_B_W = 53, 23
B_D_N = B_A_N - B_B_N
B_D_W = B_A_W - B_B_W
B_D_L = B_D_N - B_D_W
B_A_NET = B_A_W * 2.0 - (B_A_N - B_A_W) * 1.0
B_B_NET = B_B_W * 2.0 - (B_B_N - B_B_W) * 1.0
B_D_NET = B_D_W * 2.0 - B_D_L * 1.0
assert (B_D_N, B_D_W, B_D_L) == (27, 7, 20)
assert (B_A_NET, B_B_NET, B_D_NET) == (10.0, 16.0, -6.0)
assert B_B_NET - B_A_NET == -B_D_NET
B_A_R = B_A_W / B_A_N
B_B_R = B_B_W / B_B_N
assert (round(B_A_R * 100), round(B_B_R * 100)) == (38, 43)


def b_one(r=None, Wd=880, H=250):
    """١ · بندٌ واحدٌ يختلف والباقي متطابقٌ حرفياً."""
    return _steps(Wd, H,
                  [("قاعدة أ", "لمسُ الحدّ"), ("قاعدة ب", "إغلاقٌ خارجه"),
                   ("الباقي", "متطابقٌ حرفياً")],
                  "بندٌ واحدٌ يفترق والباقي واحد",
                  'قاعدتان متطابقتان إلا في بندٍ واحد: لمسُ الحدِّ مقابل '
                  'إغلاقٍ خارجه',
                  "ثمانون إشارةً مقابل ثلاثٍ وخمسين", hi=1, tag="مثال تخطيطي")


def b_two(r=None, Wd=880, H=250):
    """٢ · نسبةُ «ب» أعلى لأنّ مقامَها أصغر."""
    return _cols(Wd, H,
                 [dict(nm="قاعدة أ", n=B_A_N, w=B_A_W),
                  dict(nm="قاعدة ب", n=B_B_N, w=B_B_W)],
                 dict(nm="قاعدة ب", n=B_B_N, w=B_B_W),
                 f'{ar(round(B_A_R * 100))}٪ ثم {ar(round(B_B_R * 100))}٪',
                 'النسبةُ ارتفعت والبسطُ نزل — لأنّ المقامَ نزل أكثرَ منه',
                 "ثمانيةٌ وثلاثون ثم ثلاثةٌ وأربعون",
                 tag="مثال تخطيطي", col=TEAL_D)


def b_diff(r=None, Wd=880, H=250):
    """٣ · المختلفةُ وحدَها تقيس البند (البطل)."""
    return _bars(Wd, H,
                 [(f'{ar(B_A_N - B_D_N)} متطابقة', 0.0, False),
                  (f'{ar(B_D_N)} مختلفة', B_D_NET, True)],
                 f'{ar(B_D_N)} إشارةً اختلفت وصافيها {_sg(B_D_NET, "R")}',
                 'سبعٌ وعشرون إشارةً اختلفت وحدَها تقيس البند، وصافيها '
                 'ناقص ستّة',
                 "وثلاثٌ وخمسون متطابقةٌ لا تقيس شيئاً",
                 tag="مثال تخطيطي", col=RED, neg=True, unit="R")


def b_count(r=None, Wd=880, H=250):
    """٤ · عيّنتك سبعٌ وعشرون لا ثمانون."""
    all_ = dict(nm="كلُّ الإشارات", n=B_A_N, w=B_D_N)
    return _cols(Wd, H, [all_], all_,
                 f'{ar(B_D_N)} من {ar(B_A_N)} تقيس البند',
                 'نتيجتان تنقلبان فيصير صافي المختلفة صفراً ويختفي '
                 'الفرقُ كلُّه',
                 "حجمُ العيّنة سبعٌ وعشرون لا ثمانون",
                 tag="مثال تخطيطي", col=RED)


def b_rule(r=None, Wd=880, H=250):
    """٥ · بروتوكولُ الاختبار."""
    return _steps(Wd, H,
                  [("اشطب", "المتطابقة"), ("احكم", "على المختلفة"),
                   ("اكتب", "عددَها معها")],
                  "بندٌ واحدٌ في كلِّ جولة",
                  'اشطب المشتركةَ واحكم على المختلفة بالصافي، واكتب عددَها '
                  'مع حكمك',
                  "بندٌ واحدٌ في كلِّ جولة", hi=0, tag="مثال تخطيطي")


# ═════════════════════════════════════════════════════════════════
#  المجموعاتُ والبصماتُ والنوافذ
# ═════════════════════════════════════════════════════════════════
SETS = {"nasib": [n_med, n_three, n_big, n_quiet, n_rule],
        "kathafa": [k_ends, k_ten, k_gap, k_test, k_rule],
        "tajil": [j_gap, j_repeat, j_cost, j_batch, j_rule],
        "khumul": [x_draw, x_stops, x_trades, x_two, x_rule],
        "band": [b_one, b_two, b_diff, b_count, b_rule]}
#: الوحداتُ الثلاثُ حسابٌ محضٌ بافتراضاتٍ معلنة — لا بذرةَ توليدٍ لها ولا
#: سلسلةَ أسعار، فبصمتُها في السجل رقمٌ حرٌّ يميّزها ومرتكزُها افتراضاتُها.
SYN = {"tajil": (7310, [(J_TOT, J_WK, J_PER, J_COVER)]),
       "khumul": (7320, [(X_FEE, X_RISK, X_AVG, X_MO)]),
       "band": (7330, [(B_A_N, B_A_W, B_B_N, B_B_W)])}
REAL = {"nasib": N_WIN, "kathafa": K_WIN}
_NOWIN = {"slug": "مثال تخطيطي — بلا نافذة", "w": [], "sym": "", "tf": ""}
WINS = {"nasib": RN, "kathafa": RK,
        "tajil": _NOWIN, "khumul": _NOWIN, "band": _NOWIN}
assert set(SETS) == set(WINS) and set(REAL) | set(SYN) == set(SETS)
assert all(len(v) == 5 for v in SETS.values())


def unit_charts(slug):
    """تُختبر كلُّ لوحةٍ برسمها فعلاً: ما يسقط بـ`assert` يُترك ويُذكر."""
    r = WINS[slug]
    ok, dropped = [], []
    for f in SETS[slug]:
        try:
            f(r if slug in REAL else None, 880, 250)
            ok.append(f)
        except AssertionError as e:
            dropped.append((f.__name__, str(e)))
    return r, ok, dropped


if __name__ == "__main__":
    print(f'نصيب · {RN["slug"]} · {N_N} شمعة  [سوقٌ حقيقي]')
    print(f'  وسيط المدى {N_MED:g} · المجموع {N_WALK:.1f}× · العرض {N_SPAN:.1f}×')
    print(f'  أكبر ٣ {N_S3:.1%} · فوق الضِعف {len(N_BIG)} ({len(N_BIG)/N_N:.0%})'
          f' نصيبُها {N_SBIG:.1%} · الهادئ {len(N_QUIET)} نصيبُه {N_SQ:.1%}')
    print(f'  الملتبسة عند الضِعف بالضبط: {N_EQ} — بـ>= يصير العدد '
          f'{len(N_BIG)+len(N_EQ)}')

    print(f'\nكثافة · {RK["slug"]} · {K_N} شمعة  [سوقٌ حقيقي]')
    print(f'  أطراف {len(K_END)} {K_END} · لكل عشر {K_CNT}')
    print(f'  اختُبر {len(K_TST)} من {len(K_END)} · وسيط الانتظار '
          f'{st.median(K_WAIT):g} · الفجوات {K_GAP}')

    print(f'\nتأجيل  [تخطيطي]  {J_SEEN}/{J_TOT} مراجَعة · كتلتان {J_BLK} · '
          f'نسخ {J_ERR} ({J_IN} داخل و{J_OUT} خارج)')
    print(f'خمول   [تخطيطي]  {X_H6:g}٪ ← {X_S6:g} وقفات ← {X_T6:g} صفقة · '
          f'سنة {X_T12:g} · النصيب {X_SHARE:.0%}')
    print(f'بند    [تخطيطي]  أ {B_A_W}/{B_A_N} صافي {B_A_NET:+g}R · '
          f'ب {B_B_W}/{B_B_N} صافي {B_B_NET:+g}R · '
          f'المختلفة {B_D_N} صافي {B_D_NET:+g}R')
