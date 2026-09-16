# -*- coding: utf-8 -*-
"""جارتات تشغيلة ٧١ — ثلاثُ وحداتٍ على سوقٍ حقيقي واثنتان تخطيطيتان.

المخزون كان قد نفد صباح اليوم (صفر نافذةٍ حرّةٍ نظيفة من اثنتين وسبعين،
والستُّ الحرّة كلُّها موسومة `bad`)، فأُعيد ملؤه بمسحٍ جديد داخل الصندوق:
واحدٌ وخمسون مرشّحاً، ثمانٍ وعشرون منها حرّةٌ بفحص السجل، أُدخلت ستٌّ
المخزونَ بالفهارس ٧٢–٧٧. ووُزّعت ثلاثٌ منها على وحدات اليوم:

    دمج  ← ٧٣ · الأفالانش  · ساعة · 2026-08-30 · ٤٣ شمعة · consol
    لمسة ← ٧٤ · الريبل     · ساعة · 2025-10-27 · ٤٠ شمعة · sweep
    صدفة ← ٧٢ · التشين لينك · ساعة · 2025-10-03 · ٤٤ شمعة · chan

والنافذةُ لكلِّ وحدةٍ اختيرت **بعد القياس لا قبله**: قِيست دعوى كلِّ درسٍ
على النوافذ الستِّ كلِّها، وأُعطي كلُّ درسٍ النافذةَ التي يصدق عليها.
وسقط في هذا القياس موضوعٌ كامل (#152 «ميلاد») لأن دعواه توزيعٌ على ثلاث
جلسات، والنافذة الواحدة تعطي ثمانيةَ مستوياتٍ مختبَرة فتصير الحصّة خمسةً
وثلاثةً وصفراً — وصفرُ نيويورك أثرُ حافّة النافذة لا حكمُ سوق. وسقطت معه
دعوى «الفجوة بين المناطق فراغ»: الإغلاقات فيها ١٦ من ٤٣ أي ثلثُ الوقت،
فحلّت محلَّها لوحةُ العتبة `d_thr` وهي مقيسةٌ صادقة.

والوحدتان الباقيتان بقاعدة §11 البديلة: شارة «مثال تخطيطي» · كلُّ ادّعاءٍ
مقيسٌ بـ`assert` · أعدادٌ ونِسبٌ لا أسعار.

    python3 run71_charts.py
"""
import random
import statistics as st

from reel_build import INK, TEAL, TEAL_D, RED, htext
from run15_charts import hl, badge, frame
import run31_charts as RC
from run58_charts import ar, rt, sm, band, mark
from run59_charts import spanx, vspan, xr

MUTE = "#93A2A8"
CREAM = "#F2EEE7"


def _fs(v):
    """حجمُ حرفٍ يتبع مقياسَ اللوحة — الصفحةُ البطلة تُرسم بـ1.45."""
    return round(v * RC._SC[0])


def _sw_hi(W, k=2):
    return [i for i in range(k, len(W) - k)
            if all(W[i]["h"] > W[j]["h"] for j in range(i - k, i + k + 1) if j != i)]


def _sw_lo(W, k=2):
    return [i for i in range(k, len(W) - k)
            if all(W[i]["l"] < W[j]["l"] for j in range(i - k, i + k + 1) if j != i)]


def dot(x, y, col=INK, r=5.0):
    """نقطةٌ مجوّفة — تُعلّم طرفاً دون أن تحجب الشمعة تحتها."""
    return (f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{CREAM}" '
            f'stroke="{col}" stroke-width="2"/>')


def _blank(Wd, H):
    """لوحةٌ بلا شموع — للوحدات التي درسُها حسابٌ لا سعر.

    الوحداتُ الحسابية (الصرف وحجم العينة) لا سلسلةَ أسعارٍ لها أصلاً،
    فرسمُ شموعٍ تحتها تزويقٌ يوهم بسوقٍ ليس في الدرس. وحدودُ مساحة الرسم
    هي نفسُها حدودُ `frame` كي تتّسق اللوحات."""
    return (f'<svg class="chartsvg" viewBox="0 0 {Wd} {H}" width="{Wd}" '
            f'height="{H}" xmlns="http://www.w3.org/2000/svg">')


def bar(x0, y0, w, h, col, op=1.0):
    return (f'<rect x="{x0:.1f}" y="{y0:.1f}" width="{w:.1f}" '
            f'height="{h:.1f}" fill="{col}" opacity="{op}"/>')


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
D_GAP = [(D_LV[k + 1][1] - D_LV[k][1]) / D_MED for k in range(len(D_LV) - 1)]


def _group(thr):
    g = [[D_LV[0]]]
    for k in range(1, len(D_LV)):
        if D_GAP[k - 1] >= thr:
            g.append([])
        g[-1].append(D_LV[k])
    return g


D_THR = 0.5                      # عتبةُ الدمج بوحدة وسيط مدى الشمعة
D_GRP = _group(D_THR)
D_GRP1 = _group(1.0)             # وبعتبةِ وسيطٍ كامل: النافذةُ كتلةٌ واحدة
assert [len(g) for g in D_GRP] == [1, 3, 5, 1], [len(g) for g in D_GRP]
assert len(D_GRP1) == 1, [len(g) for g in D_GRP1]
D_EATEN = len(D_LV) - len(D_GRP)
assert D_EATEN == 6, D_EATEN


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

D_NEAR = min(D_GAP)
D_FAR = max(D_GAP)
assert D_NEAR <= 0.10, D_NEAR
assert D_FAR >= 0.80, D_FAR

# 🔒 دعوى «الفجوة بين المناطق فراغٌ لا يقف فيه السعر» **سقطت بالقياس**
# (2026-09-16): الإغلاقات الواقعة في الفجوات ١٦ من ٤٣ = ٣٧٪، والتوزيعُ
# الكامل ٥٣٪ داخل منطقة و٣٧٪ في الفجوات و٩٪ فوق الكلّ أو تحته. وكان
# المحرّك يعدّها بشرط اكتمال المنطقتين فيخرج ٣ — لكن مقامَها ٣٧ فرصةً لا
# ٤٣ شمعة، فكتابة «٣ من ٤٣» بسطٌ مشروطٌ على مقامٍ غير مشروط. فحلّت محلَّها
# لوحةُ العتبة، وهي تقول شيئاً صادقاً: العتبةُ نفسُها نصفُ الدرس.
D_INGAP = sum(1 for j in range(D_N)
              if any(max(p for _, p in D_GRP[k]) < WD[j]["c"]
                     < min(p for _, p in D_GRP[k + 1])
                     for k in range(len(D_GRP) - 1)))
assert D_INGAP == 16, D_INGAP


def _gd(Wd, H):
    return frame(WD, Wd, H, pad=0.08, pb=64)


def _zones(svg, x, y, slot, groups, col=TEAL, op=0.16):
    for g in groups:
        b, t, _ = _zone(g)
        yb, yt = y(b), y(t)
        if abs(yb - yt) < 6.0:                # مجموعةٌ من خطٍّ واحدٍ لا ارتفاع لها
            mid = (yb + yt) / 2
            yb, yt = mid + 3.0, mid - 3.0
        svg += band(x(0) - slot * .5, x(D_N - 1) + slot * .5, yt, yb, col, op)
    return svg


def d_ten(r=None, Wd=880, H=250):
    """١ · عشرةُ مستوياتٍ صحيحةٍ كلُّها — والشاشةُ لم تعد تُقرأ."""
    svg, x, y, slot = _gd(Wd, H)
    for i, p in D_LV:
        svg += hl(x(0) - slot * .5, x(D_N - 1) + slot * .5, y(p), INK, 1.5)
    svg += RC._title(Wd, rt(f'{ar(len(D_LV))} مستوياتٍ على نافذةٍ وحدة'))
    svg += RC._why(Wd, H, f'كلُّ واحدٍ منها قمّةٌ أو قاعٌ حقيقي — '
                          f'والمشكلة إنها {ar(len(D_LV))}، مو إنها غلط', INK)
    svg += sm(Wd, H, "شنو اللي تشتغل عليه من بينها؟")
    return svg + "</svg>"


def d_unit(r=None, Wd=880, H=250):
    """٢ · المسافةُ بين الخطوط تُقاس بوسيط المدى لا بالنظر."""
    svg, x, y, slot = _gd(Wd, H)
    k = D_GAP.index(D_NEAR)
    for i, p in D_LV:
        svg += hl(x(0) - slot * .5, x(D_N - 1) + slot * .5, y(p), MUTE, 1.2)
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


def d_four(r=None, Wd=880, H=250):
    """٣ · عشرةُ خطوطٍ تصير أربعَ مناطق."""
    svg, x, y, slot = _gd(Wd, H)
    svg = _zones(svg, x, y, slot, D_GRP)
    for i, p in D_LV:
        svg += hl(x(0) - slot * .5, x(D_N - 1) + slot * .5, y(p), TEAL_D, 1.0, "4 4")
    svg += vspan(x(D_N - 6) + slot * .6, y(D_BOT), y(D_TOP),
                 rt(f'{xr(D_WIDE)} وسيط المدى'), TEAL_D, 16, H)
    svg += RC._title(Wd, rt(f'{ar(len(D_LV))} مستوياتٍ ← {ar(len(D_GRP))} مناطق'))
    svg += RC._why(Wd, H, f'بعتبةِ نصفِ وسيطِ المدى ابتلع الدمجُ '
                          f'{ar(D_EATEN)} خطوطٍ من {ar(len(D_LV))}، وأوسعُ منطقةٍ '
                          f'{ar(len(D_BIG))} خطوطٍ عرضُها {xr(D_WIDE)}', TEAL_D)
    svg += sm(Wd, H, "ما حذفت مستوى — جمعتهم")
    return svg + "</svg>"


def d_touch(r=None, Wd=880, H=250):
    """٤ · المنطقةُ ترى القصّة كاملة، والخطُّ المنفرد نصفَها."""
    svg, x, y, slot = _gd(Wd, H)
    svg += band(x(D_BORN) + slot * .5, x(D_N - 1) + slot * .5,
                y(D_TOP), y(D_BOT), TEAL, 0.16)
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


def d_thr(r=None, Wd=880, H=250):
    """٥ · العتبةُ نصفُ الدرس: نصفُ الوسيط يميّز، والوسيطُ الكامل يمسح."""
    svg, x, y, slot = _gd(Wd, H)
    b1, t1, _ = _zone(D_GRP1[0])
    svg += band(x(0) - slot * .5, x(D_N - 1) + slot * .5, y(t1), y(b1), RED, 0.10)
    svg = _zones(svg, x, y, slot, D_GRP)
    svg += vspan(x(3) + slot * .6, y(b1), y(t1), rt("عتبةُ الوسيط الكامل"), RED, 16, H)
    svg += RC._title(Wd, rt("بوسيطٍ كامل: النافذة منطقةٌ وحدة"))
    svg += RC._why(Wd, H, f'نصفُ الوسيط يعطيك {ar(len(D_GRP))} مناطق تتداولها، '
                          f'والوسيطُ الكامل يبلع العشرة في كتلةٍ وحدة', RED)
    svg += sm(Wd, H, "العتبة مو تفصيل — هي الدرس")
    return svg + "</svg>"


# ═════════════════════════════════════════════════════════════════
# ٢ · «لمسة» — الخطُّ اللي ترسمه، چم شمعة قبل أول لمسة؟ (الموضوع ١٥٣)
#     الريبل · ساعة · 2025-10-27 · ٤٠ شمعة · سوقٌ حقيقي
# ═════════════════════════════════════════════════════════════════
L_WIN = 74
RL = RC.win(L_WIN)
WL = RL["w"]
L_N = len(WL)
L_MED = st.median(c["h"] - c["l"] for c in WL)

#: لا يُحسب مستوىً لم يبقَ بعده عشرُ شمعاتٍ تختبره: حافّةُ النافذة تصنع
#: «مستوياتٍ لم تُلمس» لا علاقة لها بالسوق — وهي عينُ العلّة التي رحّلت
#: موضوعَ «ميلاد» اليوم.
L_ROOM = 10
L_LV = []
for _i, _p in sorted([(i, WL[i]["h"]) for i in _sw_hi(WL)]
                     + [(i, WL[i]["l"]) for i in _sw_lo(WL)]):
    if L_N - 1 - _i < L_ROOM:
        continue
    _t = next((j for j in range(_i + 3, L_N)
               if WL[j]["l"] <= _p <= WL[j]["h"]), None)
    L_LV.append(dict(i=_i, p=_p, t=_t, age=None if _t is None else _t - _i))

assert len(L_LV) == 8, len(L_LV)
L_TST = [e for e in L_LV if e["t"] is not None]
L_NEV = [e for e in L_LV if e["t"] is None]
assert len(L_TST) == 7 and len(L_NEV) == 1
L_AGES = sorted(e["age"] for e in L_TST)
assert L_AGES == [3, 5, 5, 8, 10, 11, 15], L_AGES
L_MEDAGE = st.median(L_AGES)
assert L_MEDAGE == 8, L_MEDAGE
L_FAST = [e for e in L_TST if e["age"] <= 5]
assert len(L_FAST) == 3, len(L_FAST)
L_QUICK = min(L_TST, key=lambda e: e["age"])
L_LATE = max(L_TST, key=lambda e: e["age"])
assert L_QUICK["age"] == 3 and L_LATE["age"] == 15
L_CUT = int(L_MEDAGE * 2)        # قاعدةُ الانتهاء: ضِعفُ الوسيط
assert L_CUT == 16


def _gl(Wd, H):
    return frame(WL, Wd, H, pad=0.08, pb=64)


def _lline(svg, x, y, slot, e, col=INK, w=1.7, upto=None):
    """الخطُّ يبدأ من شمعته وينتهي عند لمستها — لا يُمدّ لآخر اللوحة."""
    end = L_N - 1 if upto is None else upto
    svg += hl(x(e["i"]) - slot * .5, x(end) + slot * .5, y(e["p"]), col, w)
    return svg


def l_draw(r=None, Wd=880, H=250):
    """١ · ثمانيةُ مستوياتٍ بشرطين مكتوبين."""
    svg, x, y, slot = _gl(Wd, H)
    for e in L_LV:
        svg = _lline(svg, x, y, slot, e, INK, 1.4)
        svg += dot(x(e["i"]), y(e["p"]), INK, 4.2)
    svg += RC._title(Wd, rt(f'{ar(len(L_LV))} مستوياتٍ على النافذة'))
    svg += RC._why(Wd, H, f'الشرط الأول: شمعتان من كل جهة تحته. والثاني: '
                          f'يبقى بعده {ar(L_ROOM)} شمعاتٍ تتّسع لاختباره', INK)
    svg += sm(Wd, H, "خلّنا نعدّ")
    return svg + "</svg>"


def l_seven(r=None, Wd=880, H=250):
    """٢ · سبعةٌ من ثمانيةٍ وصلهم السعر."""
    svg, x, y, slot = _gl(Wd, H)
    for e in L_TST:
        svg = _lline(svg, x, y, slot, e, TEAL_D, 1.5, e["t"])
        svg += dot(x(e["t"]), y(e["p"]), TEAL_D, 4.4)
    svg = _lline(svg, x, y, slot, L_NEV[0], MUTE, 1.2)
    svg += RC._title(Wd, rt(f'{ar(len(L_TST))} من {ar(len(L_LV))} لمسها السوق'))
    svg += RC._why(Wd, H, 'كلُّ دائرةٍ هني أولُ شمعةٍ بلغ مداها سعرَ المستوى — '
                          'والرمادي وحده ما جاه السعر', TEAL_D)
    svg += sm(Wd, H, "الخطّ اللي ترسمه بينختبر")
    return svg + "</svg>"


def l_ages(r=None, Wd=880, H=250):
    """٣ · من ثلاثِ شمعاتٍ إلى خمسَ عشرة."""
    svg, x, y, slot = _gl(Wd, H)
    for e, col in ((L_QUICK, TEAL_D), (L_LATE, INK)):
        svg = _lline(svg, x, y, slot, e, col, 1.9, e["t"])
        svg += mark(x(e["i"]), slot, y(WL[e["i"]]["h"]), y(WL[e["i"]]["l"]),
                    INK, 0.20)
        svg += mark(x(e["t"]), slot, y(WL[e["t"]]["h"]), y(WL[e["t"]]["l"]),
                    TEAL, 0.26)
    svg += spanx(x(L_QUICK["i"]), x(L_QUICK["t"]),
                 y(L_QUICK["p"]) - 32, rt(f'{ar(L_QUICK["age"])} شمعات'), TEAL_D)
    svg += spanx(x(L_LATE["i"]), x(L_LATE["t"]),
                 y(L_LATE["p"]) + 44, rt(f'{ar(L_LATE["age"])} شمعة'), INK)
    svg += RC._title(Wd, rt("من ثلاثِ شمعاتٍ إلى خمسَ عشرة"))
    svg += RC._why(Wd, H, f'الأعمار كلُّها: {"، ".join(ar(a) for a in L_AGES)} — '
                          f'الفرقُ بين أسرعها وأبطئها خمسُ أضعاف', INK)
    svg += sm(Wd, H, "والاثنين وصلوا")
    return svg + "</svg>"


def l_median(r=None, Wd=880, H=250):
    """٤ · الوسيطُ ثمانُ شمعات، وثلاثةٌ خلال خمس."""
    svg, x, y, slot = _gl(Wd, H)
    for e in L_TST:
        fast = e["age"] <= 5
        svg = _lline(svg, x, y, slot, e, TEAL_D if fast else MUTE,
                     1.9 if fast else 1.2, e["t"])
        if fast:
            svg += spanx(x(e["i"]), x(e["t"]), y(e["p"]) - 30,
                         rt(f'{ar(e["age"])}'), TEAL_D)
    svg += RC._title(Wd, rt(f'وسيطُ العمر {ar(int(L_MEDAGE))} شمعات'))
    svg += RC._why(Wd, H, f'{ar(len(L_FAST))} من {ar(len(L_TST))} لُمست خلال '
                          f'خمس شمعاتٍ من ميلادها — لا فوريّةٌ ولا بعيدة', TEAL_D)
    svg += sm(Wd, H, "بعد " + ar(L_CUT) + " شمعة، شيلِ الخطّ")
    return svg + "</svg>"


def l_never(r=None, Wd=880, H=250):
    """٥ · واحدٌ فقط ما رجع له السوق أبداً."""
    e = L_NEV[0]
    svg, x, y, slot = _gl(Wd, H)
    for o in L_TST:
        svg = _lline(svg, x, y, slot, o, MUTE, 1.2, o["t"])
    svg = _lline(svg, x, y, slot, e, RED, 1.9)
    svg += mark(x(e["i"]), slot, y(WL[e["i"]]["h"]), y(WL[e["i"]]["l"]), RED, 0.24)
    svg += RC._title(Wd, rt("واحدٌ من ثمانيةٍ ما رجع له"))
    svg += RC._why(Wd, H, f'بقيت بعده {ar(L_N - 1 - e["i"])} شمعةً ولا واحدةٌ '
                          f'منها بلغت سعرَه — وهذا اللي ياكل وقتك بالانتظار', RED)
    svg += sm(Wd, H, "واحد بس — والباقي جاهم السعر")
    return svg + "</svg>"


# ═════════════════════════════════════════════════════════════════
# ٣ · «صدفة» — ربحت وانت غلطان (الموضوع ١٤٣)
#     التشين لينك · ساعة · 2025-10-03 · ٤٤ شمعة · سوقٌ حقيقي
# ═════════════════════════════════════════════════════════════════
S_WIN = 72
RS = RC.win(S_WIN)
WS = RS["w"]
S_N = len(WS)
S_MED = st.median(c["h"] - c["l"] for c in WS)


def _entries(W, med):
    """الدخلةُ الناقصةُ شرطاً: شمعةٌ تخرق قاعَ سوينقٍ سابقاً **ولا تغلق فوقه**.

    الشرطُ المفقود هو الإغلاقُ العائد وحده؛ ما عداه مطابقٌ للدخلة الصحيحة.
    والوقفُ تحت قاع شمعة الخرق، والهدفُ ضعفُ المخاطرة."""
    n = len(W)
    sl = _sw_lo(W)
    out = []
    for i in range(3, n - 6):
        pl = [j for j in sl if j < i - 1]
        if not pl:
            continue
        lvl = W[pl[-1]]["l"]
        if W[i]["l"] >= lvl or W[i]["c"] > lvl:
            continue
        ent = W[i]["c"]
        stp = W[i]["l"] - med * 0.05
        if ent <= stp:
            continue
        rr = ent - stp
        tgt = ent + 2 * rr
        res, end = None, n - 1
        for j in range(i + 1, n):
            if W[j]["l"] <= stp:
                res, end = -1.0, j
                break
            if W[j]["h"] >= tgt:
                res, end = 2.0, j
                break
        if res is None:
            res = round((W[n - 1]["c"] - ent) / rr, 2)
        out.append(dict(i=i, lvl=lvl, ent=ent, stp=stp, tgt=tgt, r=res, end=end))
    return out


S_TR = _entries(WS, S_MED)
assert len(S_TR) == 15, len(S_TR)
S_WINS = [t for t in S_TR if t["r"] > 0]
S_LOSS = [t for t in S_TR if t["r"] <= 0]
assert len(S_WINS) == 2, len(S_WINS)
S_RATE = len(S_WINS) / len(S_TR)
assert 0.12 <= S_RATE <= 0.14, S_RATE
S_AVG = st.mean(t["r"] for t in S_TR)
assert -0.72 <= S_AVG <= -0.66, S_AVG
S_BEST = max(S_TR, key=lambda t: t["r"])
assert S_BEST["r"] == 2.0
#: خاسرةٌ تشبه الرابحةَ شبهاً تامّاً: نفسُ الشرط الناقص ونفسُ البناء.
S_TWIN = min(S_LOSS, key=lambda t: abs(t["i"] - S_BEST["i"]))
assert S_TWIN["r"] == -1.0
assert abs(S_TWIN["i"] - S_BEST["i"]) == 2

#: التجميعُ على الأدوات الست — ومنه الفخّ: نافذةٌ كاملةٌ أربعٌ من أربع.
#: يُحسب من النوافذ نفسِها لا من أرقامٍ منقولةٍ باليد، فإن تغيّر تعريفُ
#: الدخلة تغيّر الجدولُ معه ولا يبقى رقمٌ يتيمٌ في نصٍّ لا يعرف مصدره.
S_SIX = []
for _wi in (73, 72, 74, 75, 76, 77):
    _r = RC.win(_wi)
    _w = _r["w"]
    _tr = _entries(_w, st.median(c["h"] - c["l"] for c in _w))
    S_SIX.append(dict(win=_wi, sym=_r["sym"],
                      nm=RC.AR_SYM.get(_r["sym"], _r["sym"]),
                      n=len(_tr), w=sum(1 for t in _tr if t["r"] > 0),
                      rs=[t["r"] for t in _tr]))
S_TOT = sum(d["n"] for d in S_SIX)
S_TOTW = sum(d["w"] for d in S_SIX)
assert (S_TOT, S_TOTW) == (44, 14), (S_TOT, S_TOTW)
S_SIXAVG = st.mean(r for d in S_SIX for r in d["rs"])
assert S_SIXAVG < 0, S_SIXAVG
#: نسبةُ التعادل عند هدفٍ ضعفِ المخاطرة: p·٢ = (١−p)·١ ⇐ p = الثلث.
S_BE = int(round(100 / 3))
assert S_BE == 33
assert S_TOTW / S_TOT < S_BE / 100, "النسبة فوق التعادل — فلا درس"
S_TRAP = max(S_SIX, key=lambda d: (d["w"] / d["n"], d["n"]))
assert S_TRAP["n"] == S_TRAP["w"] == 4, S_TRAP


def _gs(Wd, H):
    return frame(WS, Wd, H, pad=0.08, pb=64)


def _str(svg, x, y, slot, t, col):
    svg += hl(x(max(0, t["i"] - 6)) - slot * .5, x(t["end"]) + slot * .5,
              y(t["lvl"]), INK, 1.7)
    svg += mark(x(t["i"]), slot, y(WS[t["i"]]["h"]), y(WS[t["i"]]["l"]), col, 0.26)
    return svg


def s_rule(r=None, Wd=880, H=250):
    """١ · ما هي الدخلة الناقصة: خرقٌ بلا إغلاقٍ عائد."""
    t = S_TWIN
    svg, x, y, slot = _gs(Wd, H)
    svg = _str(svg, x, y, slot, t, RED)
    # والقوسُ أعرضُ من نصّه، وإلا مرّ خطُّه تحت الحروف فبدا شاطباً لها.
    svg += spanx(x(t["i"]) - slot * 5.5, x(t["i"]) + slot * 5.5,
                 y(WS[t["i"]]["l"]) + 40, rt("خرقٌ بلا إغلاقٍ فوق"), RED)
    svg += RC._title(Wd, rt("شرطٌ واحدٌ ناقص، لا غير"))
    svg += RC._why(Wd, H, 'الشمعة نزلت تحت القاع وسكّرت تحته — '
                          'والدخلة الصحيحة تبي إغلاقاً فوقه', RED)
    svg += sm(Wd, H, "كل شي ثاني مطابق")
    return svg + "</svg>"


def s_fifteen(r=None, Wd=880, H=250):
    """٢ · خمسَ عشرةَ دخلةً ورابحتان."""
    svg, x, y, slot = _gs(Wd, H)
    for t in S_TR:
        win = t["r"] > 0
        svg += mark(x(t["i"]), slot, y(WS[t["i"]]["h"]), y(WS[t["i"]]["l"]),
                    TEAL if win else RED, 0.30 if win else 0.16)
    for t in S_WINS:
        svg += dot(x(t["i"]), y(WS[t["i"]]["h"]) - 16, TEAL_D, 5.0)
    svg += RC._title(Wd, rt(f'{ar(len(S_WINS))} من {ar(len(S_TR))} = '
                            f'{ar(int(round(S_RATE * 100)))}٪'))
    svg += RC._why(Wd, H, f'كلُّ عمودٍ هني دخلةٌ بنفس الشرط الناقص — والمتوسط '
                          f'ناقص {ar(f"{abs(S_AVG):.2f}")} من المخاطرة', RED)
    svg += sm(Wd, H, "الرابحة اللي تذكرها، وحدة من خمسطعش")
    return svg + "</svg>"


def s_first(r=None, Wd=880, H=250):
    """٣ · الرابحةُ وتوأمُها الخاسر — ما تفرّق بينهما ساعة الدخول."""
    a, b = S_BEST, S_TWIN
    svg, x, y, slot = _gs(Wd, H)
    svg += hl(x(max(0, min(a["i"], b["i"]) - 6)) - slot * .5,
              x(max(a["end"], b["end"])) + slot * .5, y(a["lvl"]), INK, 1.7)
    svg += band(x(a["i"]) - slot * .5, x(a["end"]) + slot * .5,
                y(a["tgt"]), y(a["ent"]), TEAL, 0.14)
    svg += band(x(b["i"]) - slot * .5, x(b["end"]) + slot * .5,
                y(b["ent"]), y(b["stp"]), RED, 0.14)
    svg += mark(x(a["i"]), slot, y(WS[a["i"]]["h"]), y(WS[a["i"]]["l"]), TEAL, 0.30)
    svg += mark(x(b["i"]), slot, y(WS[b["i"]]["h"]), y(WS[b["i"]]["l"]), RED, 0.22)
    svg += spanx(x(min(a["i"], b["i"])) - slot * 1.2,
                 x(max(a["i"], b["i"])) + slot * 1.2,
                 y(max(a["tgt"], WS[a["i"]]["h"])) - 30,
                 rt("شمعتان بينهما"), INK)
    svg += RC._title(Wd, rt("الرابحة وتوأمُها الخاسر"))
    svg += RC._why(Wd, H, 'وحدةٌ بلغت ضعفَ المخاطرة والثانية ضربت الوقف — '
                          'ونفسُ الشرط الناقص في الاثنتين', RED)
    svg += sm(Wd, H, "ما كانت مختلفة قبل الضغطة")
    return svg + "</svg>"


def _cols(Wd, H, rows, hi, title, why, foot, tag="قياسٌ على ستّ نوافذ",
          col=RED):
    """أعمدةُ عدٍّ — لا شموع: العدُّ عبر ستّ أدواتٍ ليس سلسلةَ أسعارٍ واحدة،
    فرسمُ شموعٍ تحته يوهم القارئَ أن الأرقام من نافذةٍ بعينها.

    والعمودُ **قسمان متجاوران لا متراكبان**: رُسم أولاً كاملاً بالأحمر ثم
    غُطّي الرابحُ منه بالتركواز، فاختلط اللونان وخرج رماديٌّ ليس من اللوحة
    (رُئي في الرندر). والترتيب من اليمين لأن القارئ يبدأ من هناك."""
    svg = _blank(Wd, H)
    pl, pr = 40, 40
    pt, pb = max(96, int(H * 0.11)), max(110, int(H * 0.15))
    pw, ph = Wd - pl - pr, H - pt - pb
    n = len(rows)
    step = pw / n
    bw = min(step * 0.46, Wd * 0.12)
    top = max(d["n"] for d in rows)
    for k, d in enumerate(rows):
        cx = pl + pw - (step * k + step / 2)      # من اليمين
        hh = ph * d["n"] / top
        wh = ph * d["w"] / top
        on = d is hi
        svg += bar(cx - bw / 2, pt + ph - hh, bw, hh - wh, RED, 0.24)
        svg += bar(cx - bw / 2, pt + ph - wh, bw, wh, TEAL, 0.85 if on else 0.50)
        if on:
            svg += (f'<rect x="{cx - bw / 2 - 5:.1f}" y="{pt + ph - hh - 5:.1f}" '
                    f'width="{bw + 10:.1f}" height="{hh + 10:.1f}" fill="none" '
                    f'stroke="{TEAL_D}" stroke-width="2.6"/>')
        svg += htext(cx, pt + ph - hh - _fs(14),
                     f'{ar(d["w"])}/{ar(d["n"])}', TEAL_D if on else INK, _fs(19))
        svg += htext(cx, pt + ph + _fs(26), d["nm"], INK if on else MUTE, _fs(16))
    svg += badge(Wd, tag, True)
    svg += RC._title(Wd, rt(title))
    svg += RC._why(Wd, H, why, col)
    svg += sm(Wd, H, foot)
    return svg + "</svg>"


def s_hundred(r=None, Wd=880, H=250):
    """٤ · نافذةٌ وحدة أعطت أربعاً من أربع — وهي الفخّ."""
    return _cols(Wd, H, S_SIX, S_TRAP,
                 f'أداةٌ وحدة: {ar(S_TRAP["w"])} من {ar(S_TRAP["n"])} = '
                 f'{ar(100)}٪',
                 'نفسُ الدخلة الناقصة على ستّ أدوات — وفي وحدةٍ منها '
                 'ما ضربت وقفاً ولا مرّة',
                 "وهذي بالذات اللي تقنعك إنك صح")


def s_all(r=None, Wd=880, H=250):
    """٥ · الخلاصة: أربعٌ وأربعون دخلةً، أربعَ عشرةَ رابحة — دون التعادل."""
    svg = _blank(Wd, H)
    pl = 46
    pt, pb = max(92, int(H * 0.10)), max(88, int(H * 0.14))
    per = 15
    cell = (Wd - pl * 2) / per
    rows = -(-S_TOT // per)
    rowh = (H - pt - pb) / max(1, rows)
    sq = min(cell * 0.62, rowh * 0.66)
    res = sorted((r for d in S_SIX for r in d["rs"]), reverse=True)
    for k, v in enumerate(res):
        cx = pl + (Wd - pl * 2) - (cell * (k % per) + cell / 2)
        cy = pt + rowh * (k // per) + sq / 2
        win = v > 0
        svg += bar(cx - sq / 2, cy - sq / 2, sq, sq,
                   TEAL if win else RED, 0.85 if win else 0.22)
    svg += badge(Wd, "قياسٌ على ستّ نوافذ", True)
    svg += RC._title(Wd, rt(f'{ar(S_TOTW)} من {ar(S_TOT)} = '
                            f'{ar(int(round(S_TOTW / S_TOT * 100)))}٪'))
    svg += RC._why(Wd, H, f'وبهدفٍ ضعفِ المخاطرة يحتاج التعادلُ '
                          f'{ar(S_BE)}٪ — فالطريقةُ دون التعادل، لا فوقه', RED)
    svg += sm(Wd, H, "أربع رابحات ورا بعض ما تصحّح طريقة")
    return svg + "</svg>"


# ═════════════════════════════════════════════════════════════════
# ٤ · «صرف» — تحوّل الدينار دولار مرتين (الموضوع ١٤٧)
#     تخطيطي بقاعدة §11 البديلة — حسابٌ محض، لا سلسلةَ أسعارٍ تحته
# ═════════════════════════════════════════════════════════════════
#: الافتراضاتُ معلنةٌ في نصِّ الوحدة، ولا يُدّعى أنها مقيسةٌ من سوق: فرقُ
#: الصرف في الاتجاه الواحد، ومخاطرةُ الصفقة، ومتوسطُ نتيجتها.
V_ONE = 0.35                     # ٪ من رأس المال في الاتجاه الواحد
V_CYC = V_ONE * 2                # الدورة: طلعةٌ ورجعة
V_RISK = 1.0                     # ٪ يُخاطر بها في الصفقة الواحدة
V_AVG = 0.2                      # متوسطُ نتيجة الصفقة بوحدة R
V_YEAR = 4                       # دوراتُ الصرف في السنة
V_INR = V_CYC / V_RISK
V_TRADES = V_INR / V_AVG
V_YCOST = V_CYC * V_YEAR
V_YTRADES = V_YCOST / V_RISK / V_AVG
V_HALF = V_TRADES / 2
assert abs(V_CYC - 0.7) < 1e-9
assert abs(V_INR - 0.7) < 1e-9
assert abs(V_TRADES - 3.5) < 1e-9, V_TRADES
assert abs(V_YCOST - 2.8) < 1e-9
assert abs(V_YTRADES - 14.0) < 1e-9, V_YTRADES
assert abs(V_HALF - 1.75) < 1e-9


def _pc(v):
    """نسبةٌ مئوية بأرقامٍ عربيةٍ ونقطةٍ لاتينية — و`٫` تُرسم مكسورة."""
    s = f"{v:g}"
    return ar(s) + "٪"


def _steps(Wd, H, items, title, why, foot, hi=None):
    """صفٌّ من كتلٍ مرقّمة — الحسابُ يُقرأ خطوةً خطوة لا رسماً بيانياً."""
    svg = _blank(Wd, H)
    pl, pt = 34, max(86, int(H * 0.10))
    pw = Wd - pl * 2
    n = len(items)
    gap = 14
    bwd = (pw - gap * (n - 1)) / n
    avail = H - pt - max(74, int(H * 0.13))
    # الكتلةُ تُقيَّد بعرضها: بلا قيدٍ تصير في الصفحة البطلة عموداً طولُه
    # ضعفا عرضه ونصُّه شريطٌ رفيعٌ في أعلاه (رُئي في رندر الكاروسيل).
    bh = min(avail, bwd * 1.9)
    pt = pt + (avail - bh) / 2
    for k, (big, small) in enumerate(items):
        # الخطوةُ الأولى في اليمين: القارئُ يبدأ من هناك، وكان الترتيبُ
        # مقلوباً فيقرأ النتيجةَ قبل مقدّماتها (رُئي في الرندر).
        x0 = pl + pw - bwd - (bwd + gap) * k
        on = (hi is not None and k == hi)
        # والتظليلُ تركوازٌ خفيف لا حبرٌ باهت: الحبرُ على الكريمي يخرج
        # رمادياً، والهويّةُ لا تعرف الرمادي (§1).
        svg += bar(x0, pt, bwd, bh, TEAL, 0.20 if on else 0.10)
        if on:
            svg += (f'<rect x="{x0:.1f}" y="{pt:.1f}" width="{bwd:.1f}" '
                    f'height="{bh:.1f}" fill="none" stroke="{TEAL_D}" '
                    f'stroke-width="2.4"/>')
        svg += htext(x0 + bwd / 2, pt + bh * 0.48, big,
                     TEAL_D if on else INK, _fs(34))
        svg += htext(x0 + bwd / 2, pt + bh * 0.74, small, MUTE, _fs(17))
    svg += badge(Wd, "مثال تخطيطي", True)
    svg += RC._title(Wd, rt(title))
    svg += RC._why(Wd, H, why, TEAL_D)
    svg += sm(Wd, H, foot)
    return svg + "</svg>"


def f_cycle(r=None, Wd=880, H=250):
    """١ · الدورة مرّتان: طلعةٌ ورجعة."""
    return _steps(Wd, H, [(_pc(V_ONE), "دينار ← دولار"),
                          (_pc(V_ONE), "دولار ← دينار"),
                          (_pc(V_CYC), "الدورة الوحدة")],
                  "تدفعها مرّتين لا مرّة",
                  f'فرقُ الصرف {_pc(V_ONE)} في الاتجاه الواحد، والرحلة '
                  f'ذهابٌ وإياب — فالدورةُ الوحدة {_pc(V_CYC)}',
                  "وهذي قبل ما تفتح صفقة", hi=2)


def f_inR(r=None, Wd=880, H=250):
    """٢ · حوّلها لوحدةٍ تفهمها: وقفٌ كامل."""
    return _steps(Wd, H, [(_pc(V_CYC), "تكلفة الدورة"),
                          (_pc(V_RISK), "مخاطرة الصفقة"),
                          (ar(f"{V_INR:g}") + "R", "من وقفٍ كامل")],
                  "التكلفة بوحدة المخاطرة",
                  f'لأن النسبة وحدها ما تقول لك شي — قسّمها على مخاطرتك '
                  f'{_pc(V_RISK)} تطلع {ar(f"{V_INR:g}")} من وقفٍ كامل',
                  "سبعين بالمية من وقفك، وانت ما دخلت", hi=2)


def f_avg(r=None, Wd=880, H=250):
    """٣ · وبمتوسط صفقتك: ثلاثُ صفقاتٍ ونصف."""
    return _steps(Wd, H, [(ar(f"{V_INR:g}") + "R", "اللي راح"),
                          ("+" + ar(f"{V_AVG:g}") + "R", "متوسط الصفقة"),
                          (ar(f"{V_TRADES:g}"), "صفقة تغطّيها")],
                  "ثلاثُ صفقاتٍ ونصف تشتغلها بلا سوق",
                  f'لأن الصفقة الوحدة تعطيك بالمتوسط {ar(f"{V_AVG:g}")}R — '
                  f'فـ{ar(f"{V_INR:g}")}R تحتاج {ar(f"{V_TRADES:g}")} صفقة',
                  "شغلٌ صحيحٌ نتيجتُه صفر", hi=2)


def f_year(r=None, Wd=880, H=250):
    """٤ · وأربعُ دوراتٍ في السنة."""
    return _steps(Wd, H, [(ar(V_YEAR), "دورة بالسنة"),
                          (_pc(V_YCOST), "من رأس المال"),
                          (ar(f"{V_YTRADES:g}"), "صفقة رابحة")],
                  "أربعُ دوراتٍ = أربعَ عشرةَ صفقة",
                  f'{ar(V_YEAR)} دوراتٍ في السنة تكلفتها {_pc(V_YCOST)} من '
                  f'رأس المال — {ar(f"{V_YTRADES:g}")} صفقةً رابحةً بمتوسطك',
                  "وهذا لو ما زدت ولا دورة", hi=2)


def f_fix(r=None, Wd=880, H=250):
    """٥ · شلون تنزّلها — والنصفُ يعني النصف."""
    return _steps(Wd, H, [(ar(f"{V_TRADES:g}"), "بالتكلفة الحالية"),
                          ("½", "تنزّل الفرق"),
                          (ar(f"{V_HALF:g}"), "صفقة تغطّيها")],
                  "نصّف الفرق، ينصّ العدد",
                  f'العددُ يتبع الفرقَ خطّياً — فنصفُ التكلفة '
                  f'{ar(f"{V_HALF:g}")} صفقة بدل {ar(f"{V_TRADES:g}")}',
                  "والفرق يتفاوض — اسأل قبل ما تحوّل", hi=2)


# ═════════════════════════════════════════════════════════════════
# ٥ · «عينة» — چم صفقة قبل ما تحكم على نظامك؟ (الموضوع ١٥٤)
#     تخطيطي: سلسلةٌ مولّدةٌ ببذرةٍ معلنة، كلُّ رقمٍ فيها يخرج بـ`assert`
# ═════════════════════════════════════════════════════════════════
A_SEED = 20
A_N = 60
A_P = 0.40                       # احتمالُ الرابحة
A_W, A_L = 2.0, -1.0             # الرابحة ضعفُ المخاطرة، والخاسرة وقفٌ كامل
_rnd = random.Random(A_SEED)
A_TR = [A_W if _rnd.random() < A_P else A_L for _ in range(A_N)]
A_WINS = sum(1 for t in A_TR if t > 0)
A_NET = sum(A_TR)
assert (A_WINS, A_NET) == (24, 12.0), (A_WINS, A_NET)
A_EQ = []
_e = 0.0
for _t in A_TR:
    _e += _t
    A_EQ.append(_e)

A_K = 10
A_FIRST = A_TR[:A_K]
assert (sum(1 for t in A_FIRST if t > 0), sum(A_FIRST)) == (2, -4.0)
A_SL = [sum(A_TR[i:i + A_K]) for i in range(A_N - A_K + 1)]
A_NEG = sum(1 for s in A_SL if s < 0)
assert (len(A_SL), A_NEG) == (51, 17), (len(A_SL), A_NEG)


def _negshare(k):
    sl = [sum(A_TR[i:i + k]) for i in range(A_N - k + 1)]
    return sum(1 for s in sl if s < 0), len(sl)


A_G = [(k,) + _negshare(k) for k in (10, 20, 30)]
assert A_G == [(10, 17, 51), (20, 1, 41), (30, 0, 31)], A_G

_run = _best = 0
for _t in A_TR:
    _run = _run + 1 if _t < 0 else 0
    _best = max(_best, _run)
A_STREAK = _best
A_DEEP = min(A_EQ)
assert (A_STREAK, A_DEEP) == (5, -6.0), (A_STREAK, A_DEEP)


def _curve(Wd, H, hi=None, deep=False):
    """منحنى رأس المال — خطٌّ واحد، وهو كلُّ ما في الأمر."""
    svg = _blank(Wd, H)
    pl, pr = 40, 40
    pt, pb = max(80, int(H * 0.10)), max(70, int(H * 0.12))
    pw, ph = Wd - pl - pr, H - pt - pb
    lo, hiv = min(min(A_EQ), 0.0), max(max(A_EQ), 0.0)
    rng = (hiv - lo) or 1.0

    def px(i):
        return pl + pw * i / (A_N - 1)

    def py(v):
        return pt + ph * (hiv - v) / rng

    svg += (f'<line x1="{pl}" y1="{py(0):.1f}" x2="{pl + pw}" y2="{py(0):.1f}" '
            f'stroke="rgba(15,46,60,0.18)" stroke-width="1.2"/>')
    if hi:
        svg += bar(px(hi[0]), pt, max(px(hi[1]) - px(hi[0]), 2.0), ph, RED, 0.12)
    pts = " ".join(f'{px(i):.1f},{py(v):.1f}' for i, v in enumerate(A_EQ))
    svg += (f'<polyline points="{pts}" fill="none" stroke="{TEAL_D}" '
            f'stroke-width="2.6" stroke-linejoin="round"/>')
    if deep:
        k = A_EQ.index(A_DEEP)
        svg += dot(px(k), py(A_DEEP), RED, 6.0)
        # تحت النقطة سطرُ الشرح، وفوقها خطُّ الصفر — جُرّب الموضعان
        # فركب الوسمُ كليهما في الرندر. وعن يمين النقطة المنحنى صاعدٌ
        # فالفراغُ هناك على ارتفاعها هو الموضع الوحيد الخالي.
        svg += htext(px(k) + _fs(92), py(A_DEEP) + _fs(6),
                     rt(f'ناقص {ar(f"{abs(A_DEEP):g}")}R'), RED, _fs(20))
    svg += htext(px(A_N - 1) - _fs(44), py(A_EQ[-1]) - _fs(22),
                 "+" + ar(f"{A_NET:g}") + "R", TEAL_D, _fs(22))
    return svg, px, py


def a_sixty(r=None, Wd=880, H=250):
    """١ · نظامٌ رابحٌ بالورقة كاملة."""
    svg, px, py = _curve(Wd, H)
    svg += badge(Wd, "مثال تخطيطي", True)
    svg += RC._title(Wd, rt(f'{ar(A_N)} صفقة · {ar(A_WINS)} رابحة = '
                            f'{ar(int(A_WINS / A_N * 100))}٪'))
    svg += RC._why(Wd, H, f'الرابحة ضعفُ المخاطرة والخاسرة وقفٌ كامل — '
                          f'فالصافي {"+" + ar(f"{A_NET:g}")}R على الستّين', TEAL_D)
    svg += sm(Wd, H, "هذا نظامٌ تبي تشتغل عليه")
    return svg + "</svg>"


def a_first(r=None, Wd=880, H=250):
    """٢ · وأولُ عشرِ صفقات."""
    svg, px, py = _curve(Wd, H, hi=(0, A_K - 1))
    svg += badge(Wd, "مثال تخطيطي", True)
    svg += RC._title(Wd, rt(f'أولُ {ar(A_K)}: رابحتان و'
                            f'{ar(f"{abs(sum(A_FIRST)):g}")}R تحت الصفر'))
    svg += RC._why(Wd, H, 'نفسُ النظام ونفسُ الصفقات — بس العشرة الأولى منها. '
                          'ومن هني يجي قرارُ «ما يشتغل»', RED)
    svg += sm(Wd, H, "والنظام ما تغيّر ولا حرف")
    return svg + "</svg>"


def a_slices(r=None, Wd=880, H=250):
    """٣ · إحدى وخمسون شريحةً عشرية، سبعَ عشرةَ منها سالبة."""
    svg = _blank(Wd, H)
    pl, pt = 40, max(86, int(H * 0.10))
    per = 17
    cell = (Wd - pl * 2) / per
    nrows = -(-len(A_SL) // per)
    rowh = (H - pt - max(86, int(H * 0.13))) / max(1, nrows)
    sq = min(cell * 0.62, rowh * 0.66)
    for k, v in enumerate(A_SL):
        cx = pl + cell * (k % per) + cell / 2
        cy = pt + rowh * (k // per) + sq / 2
        neg = v < 0
        svg += bar(cx - sq / 2, cy - sq / 2, sq, sq,
                   RED if neg else TEAL, 0.80 if neg else 0.40)
    svg += badge(Wd, "مثال تخطيطي", True)
    svg += RC._title(Wd, rt(f'{ar(A_NEG)} شريحةً سالبة من {ar(len(A_SL))}'))
    svg += RC._why(Wd, H, f'كلُّ مربّعٍ عشرُ صفقاتٍ متتالية — '
                          f'{ar(int(round(A_NEG / len(A_SL) * 100)))}٪ منها تريك '
                          f'نظاماً خاسراً وهو رابح', RED)
    svg += sm(Wd, H, "أي عشرة تختارهن، ثلثهن يكذّب عليك")
    return svg + "</svg>"


def a_grow(r=None, Wd=880, H=250):
    """٤ · كبّرِ الشريحةَ يهدأ الحكم."""
    rows = [dict(nm=f'{ar(k)} صفقة', n=tot, w=tot - neg) for k, neg, tot in A_G]
    return _cols(Wd, H, rows, rows[-1],
                 "عشرة تكذب وثلاثون ما تكذب",
                 f'التركوازيُّ شرائحُ موجبة: عند العشرة '
                 f'{ar(A_G[0][2] - A_G[0][1])} من {ar(A_G[0][2])}، وعند '
                 f'الثلاثين {ar(A_G[2][2])} من {ar(A_G[2][2])} — كلُّها',
                 "كل ما كبّرت الشريحة، قرب الحكم من الحقيقة",
                 tag="مثال تخطيطي", col=TEAL_D)


def a_rule(r=None, Wd=880, H=250):
    """٥ · وخمسُ خسائرَ ورا بعض — متوقَّعة."""
    svg, px, py = _curve(Wd, H, deep=True)
    svg += badge(Wd, "مثال تخطيطي", True)
    svg += RC._title(Wd, rt(f'أطولُ سلسلةِ خسارة {ar(A_STREAK)} — '
                            f'داخل النظام الرابح'))
    svg += RC._why(Wd, H, f'وأعمقُ نقطةٍ مرّ بها الحساب ناقص '
                          f'{ar(f"{abs(A_DEEP):g}")}R قبل ما يطلع — '
                          f'فاعرف رقمَك قبل لا تعيشه', RED)
    svg += sm(Wd, H, "عشر صفقات تحكم على حظك، مو على نظامك")
    return svg + "</svg>"


SETS = {"damj": [d_ten, d_unit, d_four, d_touch, d_thr],
        "lamsa": [l_draw, l_seven, l_ages, l_median, l_never],
        "sudfa": [s_rule, s_fifteen, s_first, s_hundred, s_all],
        "sarf": [f_cycle, f_inR, f_avg, f_year, f_fix],
        "ayyina": [a_sixty, a_first, a_slices, a_grow, a_rule]}
#: بصمةُ الوحدة التخطيطية في السجل: بذرةٌ وقائمةُ مرتكزات، والمرتكزُ
#: الواحد **متتاليةٌ** لا رقم (`assert_fresh_synthetic` يمرّ على كلٍّ منها
#: بـ`list(a)`). ووحدةُ الصرف لا بذرةَ لها أصلاً — حسابٌ محضٌ لا توليد —
#: فأُعطيت رقماً حرّاً يميّزها في السجل ومرتكزُها افتراضاتُها المعلنة.
SARF_SEED = 7110
SYN = {"ayyina": (A_SEED, [(A_N, A_P, A_W)]),
       "sarf": (SARF_SEED, [(V_ONE, V_RISK, V_AVG, V_YEAR)])}
REAL = {"damj": D_WIN, "lamsa": L_WIN, "sudfa": S_WIN}
#: الوحدتان التخطيطيتان لا نافذةَ لهما، ولوحاتُهما تتجاهل `r` أصلاً —
#: فإعطاؤهما نافذةَ وحدةٍ أخرى يجعل سجلَّ البناء يقول «نافذة الأفالانش»
#: عن درسٍ لا سوقَ فيه. والبديلُ سجلٌّ يقول ما هو.
_NOWIN = {"slug": "مثال تخطيطي — بلا نافذة", "w": [], "sym": "", "tf": ""}
WINS = {"damj": RD, "lamsa": RL, "sudfa": RS,
        "sarf": _NOWIN, "ayyina": _NOWIN}


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
          f'(أحجام {[len(g) for g in D_GRP]}) بعتبة {D_THR}× · '
          f'وبعتبة 1.0×: {len(D_GRP1)} منطقة')
    print(f'  أكبر مجموعة {len(D_BIG)} خطوط عرضها {D_WIDE:.2f}× · '
          f'بعد اكتمالها {D_LEFT} شمعة')
    print(f'  المنطقة {D_ZT} لمسات · الخطوط {D_EACH}')
    print(f'  (الدعوى الساقطة: الإغلاق في الفجوات {D_INGAP} من {D_N})')

    print(f'\nلمسة · {RL["slug"]} · {L_N} شمعة  [سوقٌ حقيقي]')
    print(f'  {len(L_LV)} مستوى بمتّسع {L_ROOM} شمعات · اختُبر {len(L_TST)} · '
          f'لم يُلمس {len(L_NEV)}')
    print(f'  الأعمار {L_AGES} · الوسيط {L_MEDAGE} · '
          f'خلال خمس شمعات {len(L_FAST)}')

    print(f'\nصدفة · {RS["slug"]} · {S_N} شمعة  [سوقٌ حقيقي]')
    print(f'  {len(S_TR)} دخلةً ناقصةً شرطاً · رابحة {len(S_WINS)} = {S_RATE:.0%}'
          f' · متوسط {S_AVG:+.2f}R')
    for d in S_SIX:
        print(f'    {d["nm"]:<12} {d["w"]}/{d["n"]}')
    print(f'  المجموع {S_TOTW} من {S_TOT} · المتوسط {S_SIXAVG:+.2f}R')

    print(f'\nصرف  [تخطيطي]')
    print(f'  الدورة {V_CYC:g}٪ = {V_INR:g}R = {V_TRADES:g} صفقة · '
          f'السنة {V_YCOST:g}٪ = {V_YTRADES:g} صفقة')

    print(f'\nعينة · بذرة {A_SEED}  [تخطيطي]')
    print(f'  {A_N} صفقة · {A_WINS} رابحة · صافي {A_NET:+g}R')
    print(f'  أول {A_K}: {sum(1 for t in A_FIRST if t > 0)} رابحة و{sum(A_FIRST):+g}R')
    print(f'  الشرائح السالبة {A_G}')
    print(f'  أطول سلسلة خسارة {A_STREAK} · أعمق نقطة {A_DEEP:+g}R')
