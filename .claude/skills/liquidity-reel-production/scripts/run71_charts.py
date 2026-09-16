# -*- coding: utf-8 -*-
"""جارتات تشغيلة ٧١ — ثلاثُ وحداتٍ على سوقٍ حقيقي واثنتان تخطيطيتان.

المخزون كان قد نفد صباح اليوم (صفر نافذةٍ حرّةٍ نظيفة من اثنتين وسبعين،
والستُّ الحرّة كلُّها موسومة `bad`)، فأُعيد ملؤه بمسحٍ جديد داخل الصندوق:
واحدٌ وخمسون مرشّحاً، ثمانٍ وعشرون منها حرّةٌ بفحص السجل، أُدخلت ستٌّ
المخزونَ بالفهارس ٧٢–٧٧. ووُزّعت ثلاثٌ منها على وحدات اليوم:

    دمج  ← ٧٣ · الأفالانش  · ساعة · 2026-08-30 · ٤٣ شمعة · consol
    عمر  ← ٧٤ · الريبل     · ساعة · 2025-10-27 · ٤٠ شمعة · sweep
    صدفة ← ٧٢ · التشين لينك · ساعة · 2025-10-03 · ٤٤ شمعة · chan

والنافذةُ لكلِّ وحدةٍ اختيرت **بعد القياس لا قبله**: قِيست دعوى كلِّ درسٍ
على النوافذ الستِّ كلِّها، وأُعطي كلُّ درسٍ النافذةَ التي يصدق عليها.
وسقط في هذا القياس موضوعٌ كامل (#152 «ميلاد») لأن دعواه توزيعٌ على ثلاث
جلسات، والنافذة الواحدة تعطي ثمانيةَ مستوياتٍ مختبَرة فتصير الحصّة خمسةً
وثلاثةً وصفراً — وصفرُ نيويورك أثرُ حافّة النافذة لا حكمُ سوق.

والوحدتان الباقيتان بقاعدة §11 البديلة: شارة «مثال تخطيطي» · كلُّ ادّعاءٍ
مقيسٌ بـ`assert` · أعدادٌ ونِسبٌ لا أسعار.

    python3 run71_charts.py
"""
import statistics as st

from reel_build import INK, TEAL, TEAL_D, RED
from run15_charts import hl, badge, frame
import run31_charts as RC
from run58_charts import ar, rt, sm, band, mark
from run59_charts import spanx, vspan, xr


def _sw_hi(W, k=2):
    return [i for i in range(k, len(W) - k)
            if all(W[i]["h"] > W[j]["h"] for j in range(i - k, i + k + 1) if j != i)]


def _sw_lo(W, k=2):
    return [i for i in range(k, len(W) - k)
            if all(W[i]["l"] < W[j]["l"] for j in range(i - k, i + k + 1) if j != i)]


def dot(x, y, col=INK, r=5.0):
    """نقطةٌ مجوّفة — تُعلّم طرفاً دون أن تحجب الشمعة تحتها."""
    return (f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="#F2EEE7" '
            f'stroke="{col}" stroke-width="2"/>')


# ═════════════════════════════════════════════════════════════════
# ١ · «دمج» — ستّةُ خطوطٍ والسوقُ يرى منطقتين (الموضوع ١٥١)
#     الأفالانش · ساعة · 2026-08-30 · ٤٣ شمعة · سوقٌ حقيقي
# ═════════════════════════════════════════════════════════════════
D_WIN = 73
RD = RC.win(D_WIN)
WD = RD["w"]
D_N = len(WD)
D_MED = st.median(c["h"] - c["l"] for c in WD)

#: المستوى = طرفُ سوينق، مرتَّبةً بالسعر لا بالزمن — فالدمج جوارٌ سعري.
D_LV = sorted([(i, WD[i]["h"]) for i in _sw_hi(WD)]
              + [(i, WD[i]["l"]) for i in _sw_lo(WD)], key=lambda t: t[1])
assert len(D_LV) == 10, len(D_LV)

D_THR = 0.5                      # عتبةُ الدمج بوحدة وسيط مدى الشمعة
D_GAP = [(D_LV[k + 1][1] - D_LV[k][1]) / D_MED for k in range(len(D_LV) - 1)]

D_GRP = [[D_LV[0]]]
for _k in range(1, len(D_LV)):
    if D_GAP[_k - 1] >= D_THR:
        D_GRP.append([])
    D_GRP[-1].append(D_LV[_k])
assert [len(g) for g in D_GRP] == [1, 3, 5, 1], [len(g) for g in D_GRP]
assert len(D_GRP) == 4


def _zone(g):
    """حدودُ المجموعة وميلادُها = آخرُ خطٍّ فيها وُلد؛ قبله المنطقةُ ناقصة."""
    return (min(p for _, p in g), max(p for _, p in g), max(i for i, _ in g))


D_BIG = max(D_GRP, key=len)
D_BOT, D_TOP, D_BORN = _zone(D_BIG)
D_WIDE = (D_TOP - D_BOT) / D_MED
assert 1.25 <= D_WIDE <= 1.32, D_WIDE
D_LEFT = D_N - 1 - D_BORN
assert D_LEFT == 13, D_LEFT

#: اللمسة = شمعةٌ مداها يبلغ المستوى (أو يدخل المنطقة)، بعد اكتمال المجموعة
#: — فالمقارنةُ بين المنطقة وخطوطها تبدأ من لحظةٍ واحدة، وإلا قيس كلُّ خطٍّ
#: على عمرٍ غير عمر أخيه.
D_ZT = sum(1 for j in range(D_BORN + 1, D_N)
           if WD[j]["l"] <= D_TOP and WD[j]["h"] >= D_BOT)
D_EACH = [sum(1 for j in range(D_BORN + 1, D_N) if WD[j]["l"] <= p <= WD[j]["h"])
          for _, p in D_BIG]
assert D_ZT == 9, D_ZT
assert max(D_EACH) == 5, D_EACH
assert D_ZT > max(D_EACH), "المنطقة لا تزيد على أقوى خطوطها — فلا درس"

#: الإغلاقُ في الفجوة بين منطقتين: الفراغُ الذي لا يقف فيه السعر.
D_INGAP = []
for _k in range(len(D_GRP) - 1):
    _a = max(p for _, p in D_GRP[_k])
    _b = min(p for _, p in D_GRP[_k + 1])
    _bn = max(max(i for i, _ in D_GRP[_k]), max(i for i, _ in D_GRP[_k + 1]))
    D_INGAP.append(sum(1 for j in range(_bn + 1, D_N) if _a < WD[j]["c"] < _b))
D_GAPCL = sum(D_INGAP)
assert D_GAPCL == 3, D_INGAP

D_NEAR = min(D_GAP)
D_FAR = max(D_GAP)
assert D_NEAR <= 0.10, D_NEAR
assert D_FAR >= 0.80, D_FAR


def _gd(Wd, H):
    return frame(WD, Wd, H, pad=0.08, pb=64)


def _dlines(svg, x, y, slot, col=INK, w=1.5):
    for i, p in D_LV:
        svg += hl(x(0) - slot * .5, x(D_N - 1) + slot * .5, y(p), col, w)
    return svg


def d_lines(r=None, Wd=880, H=250):
    """١ · عشرةُ مستوياتٍ صحيحةٍ كلُّها — والشاشةُ لم تعد تُقرأ."""
    svg, x, y, slot = _gd(Wd, H)
    svg = _dlines(svg, x, y, slot)
    svg += RC._title(Wd, rt(f'{ar(len(D_LV))} مستوياتٍ على نافذةٍ وحدة'))
    svg += RC._why(Wd, H, f'كلُّ واحدٍ منها قمّةٌ أو قاعٌ حقيقي — '
                          f'والمشكلة إنها {ar(len(D_LV))}، مو إنها غلط', INK)
    svg += sm(Wd, H, "شنو اللي تشتغل عليه من بينها؟")
    return svg + "</svg>"


def d_near(r=None, Wd=880, H=250):
    """٢ · المسافةُ بين الخطوط تُقاس بوسيط المدى لا بالنظر."""
    svg, x, y, slot = _gd(Wd, H)
    k = D_GAP.index(D_NEAR)
    svg = _dlines(svg, x, y, slot, col="#93A2A8", w=1.2)
    for p in (D_LV[k][1], D_LV[k + 1][1]):
        svg += hl(x(0) - slot * .5, x(D_N - 1) + slot * .5, y(p), TEAL_D, 1.9)
    # ولا قوسَ رأسياً هنا: الفجوة 0.09× وسيطَ المدى، أي بضعةُ بكسلاتٍ على
    # اللوحة، فالقوسُ يصير خطّاً لا يُرى ووسمُه يطفو على الشموع (جُرّب في
    # ثلاثة مواضع، وفي كلٍّ منها إمّا قُصّ عند الحافة أو ركب شمعة). والخطّان
    # الملوّنان يقولانها وحدهما: يُريان خطّاً واحداً — وهذا عينُ الدرس.
    svg += RC._title(Wd, rt("خطّان بينهما أقلُّ من عُشر شمعة"))
    svg += RC._why(Wd, H, f'أقربُ جارَين في النافذة يفصلهما {xr(D_NEAR)} '
                          f'وسيطَ مدى الشمعة — هذا خطٌّ واحد بخطّين', TEAL_D)
    svg += sm(Wd, H, "وأبعدُ جارَين " + xr(D_FAR) + " — الفرق يبين معاك")
    return svg + "</svg>"


def d_zone(r=None, Wd=880, H=250):
    """٣ · خمسةُ خطوطٍ تصير منطقةً واحدة."""
    svg, x, y, slot = _gd(Wd, H)
    svg += band(x(0) - slot * .5, x(D_N - 1) + slot * .5,
                y(D_BOT), y(D_TOP), TEAL, 0.16)
    for i, p in D_BIG:
        svg += hl(x(0) - slot * .5, x(D_N - 1) + slot * .5, y(p), TEAL_D, 1.2, "4 4")
    svg += vspan(x(D_N - 6) + slot * .6, y(D_BOT), y(D_TOP),
                 rt(f'{xr(D_WIDE)} وسيط المدى'), TEAL_D, 16, H)
    svg += RC._title(Wd, rt(f'{ar(len(D_BIG))} خطوطٍ = منطقةٌ وحدة'))
    svg += RC._why(Wd, H, f'بعتبةِ نصفِ وسيطِ المدى تنضمّ خمسةٌ منها في شريطٍ '
                          f'عرضُه {xr(D_WIDE)} — وباقي النافذة {ar(len(D_GRP)-1)} مناطق', TEAL_D)
    svg += sm(Wd, H, "ما حذفت مستوى — جمعتهم")
    return svg + "</svg>"


def d_touch(r=None, Wd=880, H=250):
    """٤ · المنطقةُ ترى القصّة كاملة، والخطُّ المنفرد نصفَها."""
    svg, x, y, slot = _gd(Wd, H)
    svg += band(x(D_BORN) + slot * .5, x(D_N - 1) + slot * .5,
                y(D_BOT), y(D_TOP), TEAL, 0.16)
    best = D_EACH.index(max(D_EACH))
    svg += hl(x(D_BORN) + slot * .5, x(D_N - 1) + slot * .5,
              y(D_BIG[best][1]), TEAL_D, 1.9)
    for j in range(D_BORN + 1, D_N):
        if WD[j]["l"] <= D_TOP and WD[j]["h"] >= D_BOT:
            svg += dot(x(j), y(max(D_BOT, min(D_TOP, WD[j]["c"]))), TEAL_D, 4.4)
    svg += spanx(x(D_BORN) + slot * .5, x(D_N - 1) + slot * .5, y(D_TOP) - 34,
                 rt(f'{ar(D_LEFT)} شمعة بعد اكتمال المنطقة'), INK)
    # «·» بين عددين عربيين يُقرأ صفراً ملتصقاً بما قبله — فالواو أوضح
    svg += RC._title(Wd, rt(f'المنطقة {ar(D_ZT)} لمسات وأقوى خطٍّ {ar(max(D_EACH))}'))
    svg += RC._why(Wd, H, f'نفسُ الشمعات ونفسُ المدّة: المنطقة لمسها السوق '
                          f'{ar(D_ZT)} مرّات وأقوى خطٍّ منفرد {ar(max(D_EACH))}', TEAL_D)
    svg += sm(Wd, H, "الخطّ يشوف نصف القصّة")
    return svg + "</svg>"


def d_all(r=None, Wd=880, H=250):
    """٥ · الخلاصة: أربعُ مناطق، وفراغٌ لا يقف فيه السعر."""
    svg, x, y, slot = _gd(Wd, H)
    for g in D_GRP:
        b, t, _ = _zone(g)
        # المنطقةُ من قاعها إلى قمّتها؛ والمجموعةُ من خطٍّ واحدٍ لا ارتفاع
        # لها فتُعطى ستَّ بكسلاتٍ موزّعةً على الجهتين لتُرى — ومركزُها
        # سعرُها هو. (كان التوسيطُ على القاع فينزل الشريطُ نصفَ ارتفاعه.)
        yb, yt = y(b), y(t)
        if abs(yb - yt) < 6.0:
            mid = (yb + yt) / 2
            yb, yt = mid + 3.0, mid - 3.0
        svg += band(x(0) - slot * .5, x(D_N - 1) + slot * .5, yt, yb, TEAL, 0.16)
    svg += RC._title(Wd, rt(f'{ar(len(D_LV))} مستوياتٍ ← {ar(len(D_GRP))} مناطق'))
    svg += RC._why(Wd, H, f'وفي الفراغ اللي بينها ما أغلقت إلا '
                          f'{ar(D_GAPCL)} شمعاتٍ من {ar(D_N)} — السعر إمّا بمنطقة أو رايح',
                   TEAL_D)
    svg += sm(Wd, H, "ادمج القريب، بيبقى لك اللي يتشغّل عليه")
    return svg + "</svg>"


# ═════════════════════════════════════════════════════════════════
# ٢ · «عمر» — المستوى اللي ترسمه، يلمسه السوق ولّا لا؟ (موضوعٌ جديد)
#     الريبل · ساعة · 2025-10-27 · ٤٠ شمعة · سوقٌ حقيقي
# ═════════════════════════════════════════════════════════════════
U_WIN = 74
RU = RC.win(U_WIN)
WU = RU["w"]
U_N = len(WU)
U_MED = st.median(c["h"] - c["l"] for c in WU)

#: لا يُحسب مستوىً لم يبقَ بعده عشرُ شمعاتٍ تختبره: حافّةُ النافذة تصنع
#: «مستوياتٍ لم تُلمس» لا علاقة لها بالسوق — وهي عينُ العلّة التي رحّلت
#: موضوعَ «ميلاد» اليوم.
U_ROOM = 10
U_LV = []
for _i, _p in sorted([(i, WU[i]["h"]) for i in _sw_hi(WU)]
                     + [(i, WU[i]["l"]) for i in _sw_lo(WU)]):
    if U_N - 1 - _i < U_ROOM:
        continue
    _t = next((j for j in range(_i + 3, U_N)
               if WU[j]["l"] <= _p <= WU[j]["h"]), None)
    U_LV.append(dict(i=_i, p=_p, t=_t, age=None if _t is None else _t - _i))

assert len(U_LV) == 8, len(U_LV)
U_TST = [e for e in U_LV if e["t"] is not None]
U_NEV = [e for e in U_LV if e["t"] is None]
assert len(U_TST) == 7 and len(U_NEV) == 1
U_AGES = sorted(e["age"] for e in U_TST)
assert U_AGES == [3, 5, 5, 8, 10, 11, 15], U_AGES
U_MEDAGE = st.median(U_AGES)
assert U_MEDAGE == 8, U_MEDAGE
U_FAST = [e for e in U_TST if e["age"] <= 5]
assert len(U_FAST) == 3, len(U_FAST)
U_QUICK = min(U_TST, key=lambda e: e["age"])
U_LATE = max(U_TST, key=lambda e: e["age"])
assert U_QUICK["age"] == 3 and U_LATE["age"] == 15


def _gu(Wd, H):
    return frame(WU, Wd, H, pad=0.08, pb=64)


def _uline(svg, x, y, slot, e, col=INK, w=1.7, upto=None):
    """الخطُّ يبدأ من شمعته وينتهي عند لمستها — لا يُمدّ لآخر اللوحة."""
    end = U_N - 1 if upto is None else upto
    svg += hl(x(e["i"]) - slot * .5, x(end) + slot * .5, y(e["p"]), col, w)
    return svg


def u_lv(r=None, Wd=880, H=250):
    """١ · ثمانيةُ مستوياتٍ رسمتها، ونسيتها."""
    svg, x, y, slot = _gu(Wd, H)
    for e in U_LV:
        svg = _uline(svg, x, y, slot, e, INK, 1.4)
        svg += dot(x(e["i"]), y(e["p"]), INK, 4.2)
    svg += RC._title(Wd, rt(f'{ar(len(U_LV))} مستوياتٍ على النافذة'))
    svg += RC._why(Wd, H, 'كلُّ نقطةٍ هنا قمّةُ سوينقٍ أو قاعُه — '
                          'والسؤال مو شلون ترسمها، السؤال شنو يصير بعدين', INK)
    svg += sm(Wd, H, "خلّنا نعدّ")
    return svg + "</svg>"


def u_fast(r=None, Wd=880, H=250):
    """٢ · أسرعُها: ثلاثُ شمعاتٍ ورجع لها."""
    e = U_QUICK
    svg, x, y, slot = _gu(Wd, H)
    svg = _uline(svg, x, y, slot, e, TEAL_D, 1.9, e["t"])
    svg += mark(x(e["i"]), slot, y(WU[e["i"]]["h"]), y(WU[e["i"]]["l"]), INK, 0.22)
    svg += mark(x(e["t"]), slot, y(WU[e["t"]]["h"]), y(WU[e["t"]]["l"]), TEAL, 0.26)
    svg += spanx(x(e["i"]), x(e["t"]), y(e["p"]) - 34,
                 rt(f'{ar(e["age"])} شمعات'), TEAL_D)
    svg += RC._title(Wd, rt("أسرعُ رجعةٍ: ثلاثُ شمعات"))
    svg += RC._why(Wd, H, f'{ar(len(U_FAST))} من {ar(len(U_TST))} '
                          f'اختُبرت خلال خمس شمعاتٍ من ميلادها', TEAL_D)
    svg += sm(Wd, H, "ما عطتك وقت تفكّر")
    return svg + "</svg>"


def u_slow(r=None, Wd=880, H=250):
    """٣ · وأبطؤها: خمسَ عشرةَ شمعة."""
    e = U_LATE
    svg, x, y, slot = _gu(Wd, H)
    svg = _uline(svg, x, y, slot, e, INK, 1.9, e["t"])
    svg += mark(x(e["i"]), slot, y(WU[e["i"]]["h"]), y(WU[e["i"]]["l"]), INK, 0.22)
    svg += mark(x(e["t"]), slot, y(WU[e["t"]]["h"]), y(WU[e["t"]]["l"]), TEAL, 0.26)
    svg += spanx(x(e["i"]), x(e["t"]), y(e["p"]) - 34,
                 rt(f'{ar(e["age"])} شمعة'), INK)
    svg += RC._title(Wd, rt("وأبطؤها خمسَ عشرةَ شمعة"))
    svg += RC._why(Wd, H, f'وسيطُ العمر حتى أول لمسة {ar(int(U_MEDAGE))} شمعات — '
                          f'لا فوريّةٌ ولا بعيدة', INK)
    svg += sm(Wd, H, "بينهما فرق، لكن الاثنين وصلوا")
    return svg + "</svg>"


def u_never(r=None, Wd=880, H=250):
    """٤ · واحدٌ فقط ما رجع له السوق أبداً."""
    e = U_NEV[0]
    svg, x, y, slot = _gu(Wd, H)
    for o in U_TST:
        svg = _uline(svg, x, y, slot, o, "#93A2A8", 1.2, o["t"])
    svg = _uline(svg, x, y, slot, e, RED, 1.9)
    svg += mark(x(e["i"]), slot, y(WU[e["i"]]["h"]), y(WU[e["i"]]["l"]), RED, 0.24)
    svg += RC._title(Wd, rt("واحدٌ من ثمانيةٍ ما رجع له"))
    svg += RC._why(Wd, H, f'بقيت بعده {ar(U_N - 1 - e["i"])} شمعةً ولا واحدةٌ '
                          f'منها بلغت سعرَه — المستوى الوحيد المهجور', RED)
    svg += sm(Wd, H, "واحد بس")
    return svg + "</svg>"


def u_all(r=None, Wd=880, H=250):
    """٥ · الخلاصة: سبعةٌ من ثمانية."""
    svg, x, y, slot = _gu(Wd, H)
    for e in U_TST:
        svg = _uline(svg, x, y, slot, e, TEAL_D, 1.5, e["t"])
        svg += dot(x(e["t"]), y(e["p"]), TEAL_D, 4.4)
    svg = _uline(svg, x, y, slot, U_NEV[0], "#93A2A8", 1.2)
    svg += RC._title(Wd, rt(f'{ar(len(U_TST))} من {ar(len(U_LV))} لمسها السوق'))
    svg += RC._why(Wd, H, f'الأعمار {"، ".join(ar(a) for a in U_AGES)} شمعة — '
                          f'وسيطها {ar(int(U_MEDAGE))}', TEAL_D)
    svg += sm(Wd, H, "الخطّ اللي ترسمه بينختبر — كن جاهز له")
    return svg + "</svg>"


# ═════════════════════════════════════════════════════════════════
# ٣ · «صدفة» — ربحت وانت غلطان (الموضوع ١٤٣)
#     التشين لينك · ساعة · 2025-10-03 · ٤٤ شمعة · سوقٌ حقيقي
# ═════════════════════════════════════════════════════════════════
F_WIN_ = 72
RF = RC.win(F_WIN_)
WF = RF["w"]
F_N = len(WF)
F_MED = st.median(c["h"] - c["l"] for c in WF)
F_SL = _sw_lo(WF)

#: الدخلةُ الناقصةُ شرطاً: شمعةٌ تخرق قاعَ سوينقٍ سابقاً **ولا تغلق فوقه**.
#: الشرطُ المفقود هو الإغلاقُ العائد وحده؛ ما عداه مطابقٌ للدخلة الصحيحة.
#: الوقفُ تحت قاع شمعة الخرق، والهدفُ ضعفُ المخاطرة.
F_TR = []
for _i in range(3, F_N - 6):
    _pl = [j for j in F_SL if j < _i - 1]
    if not _pl:
        continue
    _lvl = WF[_pl[-1]]["l"]
    if WF[_i]["l"] >= _lvl or WF[_i]["c"] > _lvl:
        continue
    _ent = WF[_i]["c"]
    _stp = WF[_i]["l"] - F_MED * 0.05
    if _ent <= _stp:
        continue
    _R = _ent - _stp
    _tgt = _ent + 2 * _R
    _out, _end = None, F_N - 1
    for _j in range(_i + 1, F_N):
        if WF[_j]["l"] <= _stp:
            _out, _end = -1.0, _j
            break
        if WF[_j]["h"] >= _tgt:
            _out, _end = 2.0, _j
            break
    if _out is None:
        _out = round((WF[F_N - 1]["c"] - _ent) / _R, 2)
    F_TR.append(dict(i=_i, lvl=_lvl, ent=_ent, stp=_stp, tgt=_tgt,
                     r=_out, end=_end))

assert len(F_TR) == 15, len(F_TR)
F_WINS = [t for t in F_TR if t["r"] > 0]
F_LOSS = [t for t in F_TR if t["r"] <= 0]
assert len(F_WINS) == 2, len(F_WINS)
F_RATE = len(F_WINS) / len(F_TR)
assert 0.12 <= F_RATE <= 0.14, F_RATE
F_AVG = st.mean(t["r"] for t in F_TR)
assert -0.72 <= F_AVG <= -0.66, F_AVG
F_BEST = max(F_TR, key=lambda t: t["r"])
assert F_BEST["r"] == 2.0
#: خاسرةٌ تشبه الرابحةَ شبهاً تامّاً: نفسُ الشرط الناقص ونفسُ البناء.
F_TWIN = min((t for t in F_LOSS), key=lambda t: abs(t["i"] - F_BEST["i"]))
assert F_TWIN["r"] == -1.0

#: التجميعُ على الأدوات الست — ومنه الفخّ: نافذةٌ كاملةٌ أربعٌ من أربع.
F_ALL = [(73, 4, 4), (72, 15, 2), (74, 6, 3), (75, 10, 4), (76, 4, 0), (77, 5, 1)]
F_TOT = sum(n for _, n, _ in F_ALL)
F_TOTW = sum(w for _, _, w in F_ALL)
assert (F_TOT, F_TOTW) == (44, 14), (F_TOT, F_TOTW)
F_TRAP = max(F_ALL, key=lambda t: (t[2] / t[1], t[1]))
assert F_TRAP[1] == F_TRAP[2] == 4, F_TRAP


def _gf(Wd, H):
    return frame(WF, Wd, H, pad=0.08, pb=64)


def _ftr(svg, x, y, slot, t, col):
    svg += hl(x(max(0, t["i"] - 6)) - slot * .5, x(t["end"]) + slot * .5,
              y(t["lvl"]), INK, 1.7)
    svg += mark(x(t["i"]), slot, y(WF[t["i"]]["h"]), y(WF[t["i"]]["l"]), col, 0.26)
    return svg


def f_entry(r=None, Wd=880, H=250):
    """١ · ما هي الدخلة الناقصة: خرقٌ بلا إغلاقٍ عائد."""
    t = F_TWIN
    svg, x, y, slot = _gf(Wd, H)
    svg = _ftr(svg, x, y, slot, t, RED)
    # عند `y(lvl)+38` كان النصُّ يقع على الخطّ نفسه وعلى قوسه (رُئي في
    # الرندر) — فمرجعُه الآن قاعُ شمعة الخرق، وتحته فراغ.
    # والقوسُ أعرضُ من نصّه، وإلا مرّ خطُّه تحت الحروف فبدا شاطباً لها.
    svg += spanx(x(t["i"]) - slot * 5.5, x(t["i"]) + slot * 5.5,
                 y(WF[t["i"]]["l"]) + 40, rt("خرقٌ بلا إغلاقٍ فوق"), RED)
    svg += RC._title(Wd, rt("شرطٌ واحدٌ ناقص، لا غير"))
    svg += RC._why(Wd, H, 'الشمعة نزلت تحت القاع وسكّرت تحته — '
                          'والدخلة الصحيحة تبي إغلاقاً فوقه', RED)
    svg += sm(Wd, H, "كل شي ثاني مطابق")
    return svg + "</svg>"


def f_win(r=None, Wd=880, H=250):
    """٢ · وربحت: بلغت الهدف كاملاً."""
    t = F_BEST
    svg, x, y, slot = _gf(Wd, H)
    svg = _ftr(svg, x, y, slot, t, TEAL)
    svg += band(x(t["i"]) - slot * .5, x(t["end"]) + slot * .5,
                y(t["ent"]), y(t["tgt"]), TEAL, 0.14)
    svg += mark(x(t["end"]), slot, y(WF[t["end"]]["h"]), y(WF[t["end"]]["l"]),
                TEAL, 0.26)
    # القوسُ الرأسي هنا يقع في منتصف اللوحة فيمرّ على الشموع (رُئي في
    # الرندر)؛ والقوسُ الأفقي فوق حافّة الهدف يصف الشريطَ نفسَه في فراغ.
    svg += spanx(x(t["i"]) - slot * .5, x(t["end"]) + slot * .5,
                 y(t["tgt"]) - 30, rt("ضعفُ المخاطرة"), TEAL_D)
    svg += RC._title(Wd, rt("وطلعت رابحة — كاملة"))
    svg += RC._why(Wd, H, 'دخلةٌ ناقصةٌ شرطاً بلغت هدفها بلا ما تلمس الوقف — '
                          'وهنا يبدأ الوهم', TEAL_D)
    svg += sm(Wd, H, "«شفت؟ طريقتي تشتغل»")
    return svg + "</svg>"


def f_twin(r=None, Wd=880, H=250):
    """٣ · وخاسرةٌ تشبهها تماماً."""
    t = F_TWIN
    svg, x, y, slot = _gf(Wd, H)
    svg = _ftr(svg, x, y, slot, t, RED)
    svg += band(x(t["i"]) - slot * .5, x(t["end"]) + slot * .5,
                y(t["ent"]), y(t["stp"]), RED, 0.14)
    svg += mark(x(t["end"]), slot, y(WF[t["end"]]["h"]), y(WF[t["end"]]["l"]),
                RED, 0.26)
    svg += RC._title(Wd, rt("ونفسُ الدخلة، وقفٌ"))
    _d = abs(t["i"] - F_BEST["i"])
    _w = "شمعتين" if _d == 2 else f'{ar(_d)} شمعاتٍ'
    svg += RC._why(Wd, H, f'بينها وبين الرابحة {_w} فقط — '
                          f'وما تقدر تفرّق بينهما ساعة الدخول', RED)
    svg += sm(Wd, H, "نفس الشكل، نفس الشرط الناقص")
    return svg + "</svg>"


def f_count(r=None, Wd=880, H=250):
    """٤ · العدّ: اثنتان من خمسَ عشرة."""
    svg, x, y, slot = _gf(Wd, H)
    for t in F_TR:
        col = TEAL if t["r"] > 0 else RED
        svg += mark(x(t["i"]), slot, y(WF[t["i"]]["h"]), y(WF[t["i"]]["l"]),
                    col, 0.30 if t["r"] > 0 else 0.18)
    for t in F_WINS:
        svg += dot(x(t["i"]), y(WF[t["i"]]["h"]) - 16, TEAL_D, 5.0)
    svg += RC._title(Wd, rt(f'{ar(len(F_WINS))} من {ar(len(F_TR))} = '
                            f'{ar(int(round(F_RATE*100)))}٪'))
    svg += RC._why(Wd, H, f'كلُّ عمودٍ هنا دخلةٌ بنفس الشرط الناقص — '
                          f'الخضر منها اثنتان والباقي وقف', RED)
    svg += sm(Wd, H, "الرابحة اللي تذكرها، وحدة من خمسطعش")
    return svg + "</svg>"


def f_avg(r=None, Wd=880, H=250):
    """٥ · الخلاصة: المتوسط سالب، والفخُّ نافذةٌ رابحةٌ كلُّها."""
    svg, x, y, slot = _gf(Wd, H)
    for t in F_TR:
        col = TEAL if t["r"] > 0 else RED
        svg += mark(x(t["i"]), slot, y(WF[t["i"]]["h"]), y(WF[t["i"]]["l"]),
                    col, 0.26 if t["r"] > 0 else 0.14)
    svg += RC._title(Wd, rt(f'متوسطُ النتيجة: ناقص {ar(f"{abs(F_AVG):.2f}")} '
                            f'من المخاطرة'))
    svg += RC._why(Wd, H, f'وعلى ستّ أدوات: {ar(F_TOTW)} رابحةً من {ar(F_TOT)} — '
                          f'وفيها أداةٌ طلعت أربعٌ من أربعٍ رابحة', RED)
    svg += sm(Wd, H, "وتلك الأداة هي اللي تقنعك إنك صح")
    return svg + "</svg>"


SETS = {"damj": [d_lines, d_near, d_zone, d_touch, d_all],
        "umr": [u_lv, u_fast, u_slow, u_never, u_all],
        "sudfa": [f_entry, f_win, f_twin, f_count, f_avg]}
SYN = {}
REAL = {"damj": D_WIN, "umr": U_WIN, "sudfa": F_WIN_}
WINS = {"damj": RD, "umr": RU, "sudfa": RF}


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
    print(f'دمج · {RD["slug"]} · {D_N} شمعة  [سوقٌ حقيقي]')
    print(f'  {len(D_LV)} مستوى ← {len(D_GRP)} مناطق '
          f'(أحجام {[len(g) for g in D_GRP]}) بعتبة {D_THR}×')
    print(f'  أكبر مجموعة {len(D_BIG)} خطوط عرضها {D_WIDE:.2f}× · '
          f'بعد اكتمالها {D_LEFT} شمعة')
    print(f'  المنطقة {D_ZT} لمسات · الخطوط {D_EACH}')
    print(f'  إغلاقات في الفجوات {D_INGAP} = {D_GAPCL} من {D_N}')

    print(f'\nعمر · {RU["slug"]} · {U_N} شمعة  [سوقٌ حقيقي]')
    print(f'  {len(U_LV)} مستوى بمتّسع {U_ROOM} شمعات · اختُبر {len(U_TST)} · '
          f'لم يُلمس {len(U_NEV)}')
    print(f'  الأعمار {U_AGES} · الوسيط {U_MEDAGE} · '
          f'خلال خمس شمعات {len(U_FAST)}')

    print(f'\nصدفة · {RF["slug"]} · {F_N} شمعة  [سوقٌ حقيقي]')
    print(f'  {len(F_TR)} دخلةً ناقصةً شرطاً · رابحة {len(F_WINS)} = {F_RATE:.0%}')
    print(f'  النتائج {[t["r"] for t in F_TR]}')
    print(f'  متوسط النتيجة {F_AVG:+.2f}R')
    print(f'  على الستّ: {F_TOTW} من {F_TOT} · الفخّ النافذة {F_TRAP}')
