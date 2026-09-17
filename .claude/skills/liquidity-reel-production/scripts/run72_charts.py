# -*- coding: utf-8 -*-
"""جارتات تشغيلة ٧٢ — وحدتان على سوقٍ حقيقي وثلاثٌ جداولُ عدّ.

    تسلسل ← ٧٦ · السولانا · ساعة · 2025-12-09 · ٥٢ شمعة · sweep
    جهتين ← ٧٧ · النحاس   · ٣٠ دقيقة · 2026-09-04 · ٤٤ شمعة · consol

و«مساومة» و«صياغة» قياسٌ على **ستّ نوافذ** لا على نافذةٍ بعينها، فلوحاتُهما
جداولُ عدٍّ بلا شموع — ورسمُ شموعٍ تحت عدٍّ يشمل ستّ أدواتٍ يوهم القارئ أن
الرقم من النافذة التي يراها. و«سلّم» محاكاةٌ ببذرةٍ معلنة، فعليها وحدها
شارةُ «مثال تخطيطي».

🔒 **درسُ اليوم، وهو شرطٌ على كلِّ قياسٍ بعده:** الشمعةُ الواحدة قد تحمل
الحدثين معاً — الوقفَ والهدف — ولا تقول أيَّهما سبق. وكان محرّكُ القياس
يحدّث أقصى التحرّك المواتي ثم يفحص الوقفَ ثم الهدف، فالشمعةُ الجامعة
تُسجَّل «وقفاً بلغ هدفَه». وُلد من ذلك صنفُ خطأٍ كامل («إدارة»، ثمانُ
صفقات) لا وجودَ له: ثمانٍ من ثمانٍ بلغت الهدفَ في شمعة الوقف نفسِها،
وأقصى تحرّكها بين ٣.٦ و٢١.٣ ضِعفَ المخاطرة — وهي شمعةٌ واحدةٌ تبلع كلَّ
شيء. فالاصطلاحُ الآن معلَن: **الشمعةُ الجامعة تُعدّ وقفاً — القراءةَ
الأسوأ — ويُذكر عددُها**، والملتبسُ يخرج من أيِّ تصنيفٍ يُبنى على الترتيب.

    python3 run72_charts.py
"""
import random
import statistics as st

from reel_build import INK, TEAL, TEAL_D, RED, htext
from run15_charts import hl, badge, frame
import run31_charts as RC
from run58_charts import ar, rt, sm, band, mark
from run59_charts import spanx, vspan, xr
from run71_charts import (MUTE, CREAM, _fs, _blank, bar, dot, _cols, _steps,
                          _sw_hi, _sw_lo)

WINSET = (75, 76, 77, 72, 73, 74)     # الستُّ التي يُقاس عليها


# ═════════════════════════════════════════════════════════════════
#  القياسُ المشترك: الدخلةُ الناقصةُ شرطاً على النوافذ الستّ
# ═════════════════════════════════════════════════════════════════
def _entries(mult_stop=1.0, tgt_mult=2.0):
    """كلُّ دخلةٍ في النوافذ الستّ، ومعها وسمُ الالتباس وأقصى تحرّكٍ مواتٍ.

    `amb` ترفع الرايةَ حين تحمل شمعةٌ واحدة الوقفَ والهدفَ معاً: تُحسم
    وقفاً (القراءةُ الأسوأ) ولا تدخل تصنيفاً يقوم على الترتيب. و`pre`
    يُحسب من الشمعات **قبل** شمعة الحسم وحدها، فلا يلوّثه مدىً جامع.
    """
    out = []
    for idx in WINSET:
        r = RC.win(idx)
        W = r["w"]
        n = len(W)
        med = st.median(c["h"] - c["l"] for c in W)
        sl = _sw_lo(W)
        for i in range(3, n - 6):
            pl = [j for j in sl if j < i - 1]
            if not pl:
                continue
            lvl = W[pl[-1]]["l"]
            if W[i]["l"] >= lvl:
                continue
            ent = W[i]["c"]
            base = W[i]["l"] - med * 0.05
            if ent <= base:
                continue
            rr = ent - base
            stp = ent - mult_stop * rr
            tgt = ent + tgt_mult * rr
            res, amb, pre = None, False, 0.0
            for j in range(i + 1, n):
                hs, ht = W[j]["l"] <= stp, W[j]["h"] >= tgt
                if hs and ht:
                    res, amb = -mult_stop, True
                    break
                if hs:
                    res = -mult_stop
                    break
                if ht:
                    res = tgt_mult
                    break
                pre = max(pre, (W[j]["h"] - ent) / rr)
            if res is None:
                res = 0.0
            out.append(dict(win=idx, i=i, res=res, amb=amb, pre=round(pre, 4)))
    return out


TIGHT = _entries(1.0)
WIDE = _entries(2.0)
N_TR = len(TIGHT)
assert N_TR == 50 == len(WIDE), N_TR

T_WIN = sum(1 for x in TIGHT if x["res"] > 0)
W_WIN = sum(1 for x in WIDE if x["res"] > 0)
T_NET = sum(x["res"] for x in TIGHT)
W_NET = sum(x["res"] for x in WIDE)
T_AMB = sum(1 for x in TIGHT if x["amb"])
W_AMB = sum(1 for x in WIDE if x["amb"])
FLAT = sum(1 for x in TIGHT if x["res"] == 0)
assert (T_WIN, W_WIN) == (13, 22), (T_WIN, W_WIN)
assert T_NET == W_NET == -10.0, (T_NET, W_NET)
assert (T_AMB, W_AMB, FLAT) == (8, 7, 1), (T_AMB, W_AMB, FLAT)
#: ٥٠ = ١٣ رابحة + ٣٦ موقوفة + واحدةٌ خرجت بصفر (لم تبلغ هدفاً ولا وقفاً).
STOPPED = [x for x in TIGHT if x["res"] < 0]
assert len(STOPPED) == 36
SAVED = W_WIN - T_WIN
assert SAVED == 9

#: ونسبةُ الربح وحدها تقفز، والصافي لا يتحرّك — هذا قلبُ «مساومة».
T_RATE, W_RATE = T_WIN / N_TR, W_WIN / N_TR
assert (round(T_RATE * 100), round(W_RATE * 100)) == (26, 44)


# ═════════════════════════════════════════════════════════════════
# ١ · «تسلسل» — عُدَّ الأزواجَ قبل أن تسمّي (الموضوع ١٥٦)
#     السولانا · ساعة · 2025-12-09 · ٥٢ شمعة · سوقٌ حقيقي
# ═════════════════════════════════════════════════════════════════
S_WIN = 76
RS = RC.win(S_WIN)
WS = RS["w"]
S_N = len(WS)
S_MED = st.median(c["h"] - c["l"] for c in WS)
S_END = sorted([(i, WS[i]["h"], "H") for i in _sw_hi(WS)]
               + [(i, WS[i]["l"], "L") for i in _sw_lo(WS)])
assert len(S_END) == 11, len(S_END)
S_PAIR = ["↑" if S_END[k + 1][1] > S_END[k][1] else "↓"
          for k in range(len(S_END) - 1)]
assert len(S_PAIR) == 10
S_UP = S_PAIR.count("↑")
S_DN = S_PAIR.count("↓")
assert (S_UP, S_DN) == (4, 6), (S_UP, S_DN)
S_FLIP = [k for k in range(len(S_PAIR) - 1) if S_PAIR[k] != S_PAIR[k + 1]]
assert len(S_FLIP) == 8, len(S_FLIP)

#: أطولُ سلسلةٍ متجانسة — وطولُها بالشمعات فرقُ فهرسَي طرفيها.
_runs, _cur, _st = [], 1, 0
for k in range(1, len(S_PAIR)):
    if S_PAIR[k] == S_PAIR[k - 1]:
        _cur += 1
    else:
        _runs.append((_st, _cur))
        _st, _cur = k, 1
_runs.append((_st, _cur))
S_RUN = max(_runs, key=lambda t: t[1])
assert S_RUN[1] == 2, S_RUN
S_RA, S_RB = S_END[S_RUN[0]][0], S_END[S_RUN[0] + S_RUN[1]][0]
assert (S_RA, S_RB) == (19, 32), (S_RA, S_RB)
S_SPAN = S_RB - S_RA
S_SHARE = S_SPAN / S_N
assert S_SPAN == 13 and abs(S_SHARE - 0.25) < 0.005, (S_SPAN, S_SHARE)


def _gs(Wd, H):
    return frame(WS, Wd, H, pad=0.08, pb=64)


def _zig(x, y, a=0, b=None, col=INK, w=2.0, dash=None):
    b = len(S_END) - 1 if b is None else b
    pts = " ".join(f'{x(S_END[k][0]):.1f},{y(S_END[k][1]):.1f}'
                   for k in range(a, b + 1))
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<polyline points="{pts}" fill="none" stroke="{col}" '
            f'stroke-width="{w}" stroke-linejoin="round"{d}/>')


def t_edge(r=None, Wd=880, H=250):
    """١ · الطرفُ يُعدّ بشرطٍ لا يُرى بالعين."""
    svg, x, y, slot = _gs(Wd, H)
    k = 2
    e = S_END[2]
    for j in range(e[0] - k, e[0] + k + 1):
        if j != e[0]:
            svg += mark(x(j), slot, y(WS[j]["h"]), y(WS[j]["l"]), MUTE, 0.22)
    svg += mark(x(e[0]), slot, y(WS[e[0]]["h"]), y(WS[e[0]]["l"]), TEAL, 0.30)
    svg += dot(x(e[0]), y(e[1]), TEAL_D, 5.4)
    svg += spanx(x(e[0] - k), x(e[0] + k), y(e[1]) - 34,
                 rt("شمعتان من كل جهة"), TEAL_D)
    svg += RC._title(Wd, rt("الطرف شرطٌ مكتوب لا نظرة"))
    svg += RC._why(Wd, H, 'قمّةٌ تتفوّق على شمعتين من كلِّ جهة — عدٌّ '
                          'يُعيده غيرُك فيطلع نفس الرقم', TEAL_D)
    svg += sm(Wd, H, "وبنفس الشرط نعدّ الباقي")
    return svg + "</svg>"


def t_pairs(r=None, Wd=880, H=250):
    """٢ · أحدَ عشرَ طرفاً تعني عشرةَ أزواج."""
    svg, x, y, slot = _gs(Wd, H)
    svg += _zig(x, y, col=INK, w=2.0)
    for i, p, k2 in S_END:
        svg += dot(x(i), y(p), INK, 4.6)
    svg += RC._title(Wd, rt(f'{ar(len(S_END))} طرفاً = '
                            f'{ar(len(S_PAIR))} أزواج'))
    svg += RC._why(Wd, H, 'كلُّ ضلعٍ بين طرفين زوجٌ يُصنَّف صاعداً أو '
                          'هابطاً بمقارنة سعرَيه — بلا رأيٍ ولا عين', INK)
    svg += sm(Wd, H, "خلّنا نصنّفهم")
    return svg + "</svg>"


def t_split(r=None, Wd=880, H=250):
    """٣ · أربعةٌ صاعدة وستّةٌ هابطة."""
    svg, x, y, slot = _gs(Wd, H)
    for k in range(len(S_PAIR)):
        svg += _zig(x, y, k, k + 1, TEAL_D if S_PAIR[k] == "↑" else RED, 3.0)
    for i, p, k2 in S_END:
        svg += dot(x(i), y(p), INK, 4.2)
    svg += RC._title(Wd, rt(f'{ar(S_UP)} صاعدة و{ar(S_DN)} هابطة'))
    svg += RC._why(Wd, H, 'لا أغلبيةَ تكفي لتسمية اتجاه — والفرقُ بينهما '
                          'زوجان في اثنتين وخمسين شمعة', RED)
    svg += sm(Wd, H, "شنو تسمّي هالنافذة؟")
    return svg + "</svg>"


def t_flip(r=None, Wd=880, H=250):
    """٤ · والتصنيفُ انقلب ثماني مرّات."""
    svg, x, y, slot = _gs(Wd, H)
    svg += _zig(x, y, col=MUTE, w=1.8)
    for k in S_FLIP:
        i, p, _ = S_END[k + 1]
        svg += dot(x(i), y(p), RED, 6.2)
    svg += RC._title(Wd, rt(f'التصنيف انقلب {ar(len(S_FLIP))} مرّات'))
    svg += RC._why(Wd, H, f'كلُّ نقطةٍ حمراء زوجٌ عاكس الذي قبله — '
                          f'{ar(len(S_FLIP))} انقلاباً على تسع مجاورات', RED)
    svg += sm(Wd, H, "يعني تسعة قرارات، ثمانية منهن تغيير")
    return svg + "</svg>"


def t_run(r=None, Wd=880, H=250):
    """٥ · وأطولُ صمود: زوجان = ربعُ النافذة."""
    svg, x, y, slot = _gs(Wd, H)
    svg += _zig(x, y, col=MUTE, w=1.8)
    svg += _zig(x, y, S_RUN[0], S_RUN[0] + S_RUN[1], RED, 3.4)
    svg += band(x(S_RA) - slot * .5, x(S_RB) + slot * .5,
                y(max(c["h"] for c in WS)), y(min(c["l"] for c in WS)),
                TEAL, 0.10)
    svg += spanx(x(S_RA), x(S_RB), y(max(c["h"] for c in WS)) - 22,
                 rt(f'{ar(S_SPAN)} شمعة من {ar(S_N)}'), TEAL_D)
    svg += RC._title(Wd, rt(f'أطولُ صمود {ar(S_RUN[1])} زوجين = '
                            f'{ar(int(round(S_SHARE * 100)))}٪'))
    svg += RC._why(Wd, H, f'ما صمد تصنيفٌ واحدٌ أكثرَ من {ar(S_SPAN)} شمعة — '
                          f'ربعُ النافذة، والباقي تقلّب', RED)
    svg += sm(Wd, H, "عدّ قبل لا تسمّي")
    return svg + "</svg>"


# ═════════════════════════════════════════════════════════════════
# ٢ · «جهتين» — المستوى الذي رُدَّ من الجهتين (الموضوع ١٥٩)
#     النحاس · ٣٠ دقيقة · 2026-09-04 · ٤٤ شمعة · سوقٌ حقيقي
# ═════════════════════════════════════════════════════════════════
J_WIN = 77
RJ = RC.win(J_WIN)
WJ = RJ["w"]
J_N = len(WJ)
J_MED = st.median(c["h"] - c["l"] for c in WJ)
J_END = sorted([(i, WJ[i]["h"], "H") for i in _sw_hi(WJ)]
               + [(i, WJ[i]["l"], "L") for i in _sw_lo(WJ)])
assert len(J_END) == 9, len(J_END)
#: شمعةٌ واحدة (٢١) هي قمّةُ سوينقٍ وقاعُه معاً — صحيحٌ بالقاعدة، فتُعدّ مرّتين.
assert sum(1 for i, _, _ in J_END if i == 21) == 2

J_HOR = 5                     # أفقُ قياس الابتعاد — معلَنٌ لا مضمر
J_LV = []
for _i, _p, _k in J_END:
    _hits = [j for j in range(_i + 3, J_N) if WJ[j]["l"] <= _p <= WJ[j]["h"]]
    _side = {j: (WJ[j]["c"] > _p) for j in _hits}
    _up = sum(1 for v in _side.values() if v)
    _dn = len(_hits) - _up
    J_LV.append(dict(i=_i, p=_p, k=_k, hits=_hits, up=_up, dn=_dn))
J_NONE = [e for e in J_LV if not e["hits"]]
J_BOTH = [e for e in J_LV if e["up"] and e["dn"]]
assert len(J_NONE) == 3 and len(J_BOTH) == 6, (len(J_NONE), len(J_BOTH))
#: وكلُّ طرفٍ بلغه السعرُ لُمس من الجهتين — ستٌّ من ستّ، لا ستٌّ من تسع.
assert len(J_BOTH) == len(J_LV) - len(J_NONE)
assert [(e["up"], e["dn"]) for e in J_BOTH] == [(5, 6), (5, 6), (2, 5),
                                                (3, 5), (4, 5), (1, 2)]
J_TOT = [e["up"] + e["dn"] for e in J_BOTH]
assert (max(J_TOT), min(J_TOT)) == (11, 3)

for _e in J_BOTH:
    _t2 = _e["hits"][1]
    _end = min(J_N - 1, _t2 + J_HOR)
    _e["t2"] = _t2
    _e["away"] = max(abs(WJ[j]["c"] - _e["p"])
                     for j in range(_t2, _end + 1)) / J_MED
    _e["cross"] = any(WJ[j]["c"] > _e["p"] for j in range(_t2, J_N)) and \
        any(WJ[j]["c"] < _e["p"] for j in range(_t2, J_N))
J_AWAY = st.median(e["away"] for e in J_BOTH)
assert 1.10 <= J_AWAY <= 1.12, J_AWAY
J_CROSS = sum(1 for e in J_BOTH if e["cross"])
assert J_CROSS == 6, J_CROSS


def _gj(Wd, H):
    return frame(WJ, Wd, H, pad=0.08, pb=64)


def _jl(svg, x, y, slot, e, col, w=1.7):
    return svg + hl(x(e["i"]) - slot * .5, x(J_N - 1) + slot * .5,
                    y(e["p"]), col, w)


def j_both(r=None, Wd=880, H=250):
    """١ · «من الجهتين» تعريفٌ يُعدّ لا وصفٌ يُقال."""
    e = J_BOTH[2]
    svg, x, y, slot = _gj(Wd, H)
    svg = _jl(svg, x, y, slot, e, INK, 2.0)
    up = next(j for j in e["hits"] if WJ[j]["c"] > e["p"])
    dn = next(j for j in e["hits"] if WJ[j]["c"] < e["p"])
    for j, col, t in ((up, TEAL, "أغلقت فوق"), (dn, RED, "أغلقت تحت")):
        svg += mark(x(j), slot, y(WJ[j]["h"]), y(WJ[j]["l"]), col, 0.30)
        svg += dot(x(j), y(WJ[j]["c"]), col, 4.6)
    svg += spanx(x(min(up, dn)) - slot * 1.4, x(max(up, dn)) + slot * 1.4,
                 y(e["p"]) - 34, rt("إغلاقٌ فوق وإغلاقٌ تحت"), INK)
    svg += RC._title(Wd, rt("شرطان: مدىً يبلغه وإغلاقان يحيطانه"))
    svg += RC._why(Wd, H, 'المستوى «من الجهتين» = شمعةٌ أغلقت فوقه وأخرى '
                          'أغلقت تحته، ومدى كلٍّ منهما يبلغ سعرَه', INK)
    svg += sm(Wd, H, "تعريفٌ تقدر تعدّه، مو انطباع")
    return svg + "</svg>"


def j_six(r=None, Wd=880, H=250):
    """٢ · كلُّ مستوىً بلغه السعر لُمس من الجهتين."""
    svg, x, y, slot = _gj(Wd, H)
    for e in J_NONE:
        svg = _jl(svg, x, y, slot, e, MUTE, 1.2)
    for e in J_BOTH:
        svg = _jl(svg, x, y, slot, e, TEAL_D, 1.9)
        svg += dot(x(e["hits"][0]), y(e["p"]), TEAL_D, 4.2)
    svg += RC._title(Wd, rt(f'{ar(len(J_BOTH))} من {ar(len(J_BOTH))} — '
                            f'وثلاثةٌ ما وصلهن السعر'))
    svg += RC._why(Wd, H, f'تسعةُ أطراف: {ar(len(J_NONE))} ما بلغها السعرُ '
                          f'أصلاً، و{ar(len(J_BOTH))} بلغها — وكلُّها لُمست '
                          f'من جهتيها', TEAL_D)
    svg += sm(Wd, H, "ما في مستوىً لُمس من جهةٍ وحدة")
    return svg + "</svg>"


def j_counts(r=None, Wd=880, H=250):
    """٣ · اللمسات: من إحدى عشرةَ إلى ثلاث."""
    svg, x, y, slot = _gj(Wd, H)
    for e in J_BOTH:
        svg = _jl(svg, x, y, slot, e, TEAL_D, 1.6)
        for j in e["hits"]:
            svg += dot(x(j), y(e["p"]),
                       TEAL_D if WJ[j]["c"] > e["p"] else RED, 3.6)
        svg += htext(x(e["i"]) - slot * 1.6, y(e["p"]) - 12,
                     f'{ar(e["up"] + e["dn"])}', INK, _fs(19))
    svg += RC._title(Wd, rt(f'من {ar(max(J_TOT))} لمسةً إلى {ar(min(J_TOT))}'))
    svg += RC._why(Wd, H, f'مجموعُ لمسات الستّة {ar(sum(J_TOT))} لمسة — '
                          f'الرقمُ عند كل مستوىً عددُ لمساته', TEAL_D)
    svg += sm(Wd, H, "التركوازي فوق والأحمر تحت")
    return svg + "</svg>"


def j_move(r=None, Wd=880, H=250):
    """٤ · وبعد اللمسة الثانية بخمس شمعات."""
    e = max(J_BOTH, key=lambda z: z["away"])
    svg, x, y, slot = _gj(Wd, H)
    svg = _jl(svg, x, y, slot, e, INK, 1.9)
    end = min(J_N - 1, e["t2"] + J_HOR)
    svg += band(x(e["t2"]) - slot * .5, x(end) + slot * .5,
                y(max(c["h"] for c in WJ)), y(min(c["l"] for c in WJ)),
                TEAL, 0.10)
    svg += mark(x(e["t2"]), slot, y(WJ[e["t2"]]["h"]), y(WJ[e["t2"]]["l"]),
                TEAL, 0.28)
    svg += spanx(x(e["t2"]), x(end), y(max(c["h"] for c in WJ)) - 22,
                 rt(f'{ar(J_HOR)} شمعات'), TEAL_D)
    svg += RC._title(Wd, rt(f'وسيطُ الابتعاد {xr(J_AWAY)} وسيط المدى'))
    svg += RC._why(Wd, H, f'أكبرُ ابتعادٍ بالإغلاق خلال {ar(J_HOR)} شمعاتٍ من '
                          f'اللمسة الثانية — والأفقُ يُكتب مع الرقم', TEAL_D)
    svg += sm(Wd, H, "بلا أفق، الرقم ما يعني شي")
    return svg + "</svg>"


def j_cross(r=None, Wd=880, H=250):
    """٥ · والنهاية: الستّةُ كلُّها عُبرت بإغلاق."""
    svg, x, y, slot = _gj(Wd, H)
    for e in J_BOTH:
        svg = _jl(svg, x, y, slot, e, MUTE, 1.3)
        j = next((j for j in range(e["t2"], J_N)
                  if (WJ[j]["c"] > e["p"]) != (WJ[e["t2"]]["c"] > e["p"])), None)
        if j is not None:
            svg += dot(x(j), y(e["p"]), RED, 5.2)
    svg += RC._title(Wd, rt(f'{ar(J_CROSS)} من {ar(len(J_BOTH))} عُبرت بإغلاق'))
    svg += RC._why(Wd, H, 'ولا واحدٌ منها صمد — واللمسُ من الجهتين علامةُ '
                          'ترددٍ لا علامةُ قوّة', RED)
    svg += sm(Wd, H, "العبور جا بعد اللمسة الثانية")
    return svg + "</svg>"


# ═════════════════════════════════════════════════════════════════
# ٣ · «مساومة» — وسّعتَ وقفَك فارتفعت نسبتُك (الموضوع ١٦١)
#     قياسٌ على النوافذ الستّ — جداولُ عدٍّ لا شموع
# ═════════════════════════════════════════════════════════════════
M_ROWS = [dict(nm="وقفٌ ثابت", n=N_TR, w=T_WIN),
          dict(nm="وقفٌ موسَّع", n=N_TR, w=W_WIN)]


def _sg(v, unit=""):
    """العددُ بإشارته كلمةً — «-» قبل رقمٍ عربي-هندي يقع في آخر السطر
    فيُقرأ شرطةً لاحقةً لا سالباً (رُئي في رندر ٧٢)."""
    w = "ناقص " if v < 0 else ("زائد " if v > 0 else "")
    return w + ar(f"{abs(v):g}") + unit


def _bars(Wd, H, items, title, why, foot, tag="قياسٌ على ستّ نوافذ",
          col=RED, neg=False, unit=""):
    """أعمدةٌ حرّة — لكلِّ عمودٍ قيمةٌ ووسمٌ، وقد تكون سالبة."""
    svg = _blank(Wd, H)
    pl, pr = 40, 40
    pt, pb = max(96, int(H * 0.11)), max(110, int(H * 0.15))
    pw, ph = Wd - pl - pr, H - pt - pb
    n = len(items)
    step = pw / n
    bw = min(step * 0.46, Wd * 0.12)
    top = max(abs(v) for _, v, _ in items) or 1.0
    # الخطُّ الصفري في أعلى اللوحة حين تكون القيمُ سالبة، والأعمدةُ تتدلّى
    # منه. وكان وسمُ القيمة يوضع تحت طرف عمودِه ووسمُ الاسم عند قاع
    # اللوحة، فيلتقيان في اللوحة القصيرة حرفاً فوق حرف (رُئي في دليل ٧٢):
    # فصارت القيمةُ فوق الخط الصفري والاسمُ تحت أطول عمود.
    y0 = pt + ph if not neg else pt + ph * 0.16
    mh = ph * (0.82 if neg else 1.0)
    for k, (nm, v, on) in enumerate(items):
        cx = pl + pw - (step * k + step / 2)
        hh = mh * (abs(v) / top)
        ytop = y0 - hh if v >= 0 else y0
        svg += bar(cx - bw / 2, ytop, bw, hh,
                   TEAL if v >= 0 else RED, 0.85 if on else 0.45)
        if on:
            svg += (f'<rect x="{cx - bw / 2 - 5:.1f}" y="{ytop - 5:.1f}" '
                    f'width="{bw + 10:.1f}" height="{hh + 10:.1f}" fill="none" '
                    f'stroke="{TEAL_D if v >= 0 else RED}" stroke-width="2.6"/>')
        svg += htext(cx, (y0 - _fs(14)) if neg else (ytop - _fs(14)),
                     _sg(v, unit), TEAL_D if v >= 0 else RED, _fs(21))
        svg += htext(cx, (y0 + mh + _fs(28)) if neg else (pt + ph + _fs(26)),
                     nm, INK if on else MUTE, _fs(16))
    if neg:
        svg += (f'<line x1="{pl}" y1="{y0:.1f}" x2="{pl + pw}" y2="{y0:.1f}" '
                f'stroke="rgba(15,46,60,0.20)" stroke-width="1.4"/>')
    svg += badge(Wd, tag, True)
    svg += RC._title(Wd, rt(title))
    svg += RC._why(Wd, H, why, col)
    svg += sm(Wd, H, foot)
    return svg + "</svg>"


def w_one(r=None, Wd=880, H=250):
    """١ · بندٌ واحدٌ تغيّر والباقي ثابت."""
    return _steps(Wd, H,
                  [(ar(N_TR), "دخلة وحدة"), ("×١", "وقفٌ ثابت"),
                   ("×٢", "وقفٌ موسَّع")],
                  "نفسُ الدخلات — والوقفُ وحده يتغيّر",
                  f'نفسُ {ar(N_TR)} دخلةٍ ونفسُ النوافذ ونفسُ الهدف — '
                  f'ولا يتغيّر إلا بُعدُ الوقف',
                  "والملتبسُ يُعدّ وقفاً — القراءةَ الأسوأ", hi=2,
                  tag="قياسٌ على ستّ نوافذ")


def w_tight(r=None, Wd=880, H=250):
    """٢ · الوقفُ الثابت: ثلاثَ عشرةَ رابحة."""
    return _cols(Wd, H, M_ROWS[:1], M_ROWS[0],
                 f'{ar(T_WIN)} رابحة من {ar(N_TR)} = '
                 f'{ar(round(T_RATE * 100))}٪',
                 f'وقفٌ عند قاع شمعة الدخول وهدفٌ ضعفَ المخاطرة — '
                 f'و{ar(T_AMB)} حالاتٍ جامعةٍ عُدّت وقفاً',
                 "الرقمُ الذي تراه أول ما تفتح دفترك", col=RED)


def w_wide(r=None, Wd=880, H=250):
    """٣ · الموسَّع: اثنتان وعشرون — وتسعٌ أُنقذن."""
    return _cols(Wd, H, M_ROWS, M_ROWS[1],
                 f'{ar(W_WIN)} رابحة من {ar(N_TR)} = '
                 f'{ar(round(W_RATE * 100))}٪',
                 f'{ar(SAVED)} صفقاتٍ كانت ستُوقف فعادت — ربعُ الموقوفات. '
                 f'والنسبةُ قفزت {ar(round(W_RATE * 100) - round(T_RATE * 100))} '
                 f'نقطة',
                 "وهني تقول: ضبطتها", col=TEAL_D)


def w_net(r=None, Wd=880, H=250):
    """٤ · والصافي؟ ناقص عشرة في الحالتين."""
    return _bars(Wd, H,
                 [("وقفٌ ثابت", T_NET, False), ("وقفٌ موسَّع", W_NET, True)],
                 f'الصافي ناقص {ar(int(abs(T_NET)))}R في الاثنين',
                 'نفسُ العمود ونفسُ الرقم — النسبةُ وحدها تحرّكت، '
                 'والذي يدخل حسابَك لم يتحرّك',
                 "نفسُ الفلوس بنسبتين مختلفتين", col=RED, neg=True, unit="R")


def w_buy(r=None, Wd=880, H=250):
    """٥ · أنت ما اشتريت أرباحاً — اشتريت شعورَ الصح."""
    return _steps(Wd, H,
                  [(f'{ar(round(T_RATE * 100))}٪ ← {ar(round(W_RATE * 100))}٪',
                    "النسبة"),
                   (_sg(T_NET, "R"), "الصافي قبل"),
                   (_sg(W_NET, "R"), "الصافي بعد")],
                  "الرقمُ الذي تراه تحسّن، والذي يعيشك ثابت",
                  'توسيعُ الوقف يشتري نسبةً لا نقوداً — ولو قِست بالنسبة '
                  'وحدها لقلت إنك تحسّنت',
                  "قِس الصافي، مو النسبة", hi=0,
                  tag="قياسٌ على ستّ نوافذ")


# ═════════════════════════════════════════════════════════════════
# ٤ · «سلّم» — تنزيلُ المخاطرة بعد سلسلة خسارة (الموضوع ١٦٦)
#     محاكاةٌ ببذورٍ معلنة — مثالٌ تخطيطي
# ═════════════════════════════════════════════════════════════════
D_SEEDS = (31, 77, 404)
D_N, D_P, D_BASE, D_RISK, D_CUT, D_RUN = 200, 0.40, 100.0, 1.0, 0.5, 3


def _ladder(seed):
    rnd = random.Random(seed)
    res = [2.0 if rnd.random() < D_P else -1.0 for _ in range(D_N)]
    out = {}
    for mode in ("ثابتة", "سلّم"):
        eq, risk, run = D_BASE, D_RISK, 0
        for x in res:
            eq += eq * risk / 100 * x
            if x < 0:
                run += 1
                if mode == "سلّم" and run >= D_RUN:
                    risk = D_CUT
            else:
                run = 0
                if mode == "سلّم":
                    risk = D_RISK
        out[mode] = round(eq, 1)
    return out


D_RES = {s: _ladder(s) for s in D_SEEDS}
assert [D_RES[s]["ثابتة"] for s in D_SEEDS] == [191.0, 125.7, 133.5]
assert [D_RES[s]["سلّم"] for s in D_SEEDS] == [179.6, 113.7, 134.6]
D_LOSS = sum(1 for s in D_SEEDS if D_RES[s]["سلّم"] < D_RES[s]["ثابتة"])
assert D_LOSS == 2


def d_rule(r=None, Wd=880, H=250):
    """١ · القاعدةُ التي جُرّبت — مكتوبةً بالضبط."""
    return _steps(Wd, H,
                  [(ar(D_RUN), "خسائرَ متتالية"),
                   (ar(f"{D_CUT:g}") + "٪", "تنزل المخاطرة"),
                   ("أول رابحة", "ترجع كما كانت")],
                  "القاعدة مكتوبةً لا موصوفة",
                  f'مخاطرةٌ {ar(f"{D_RISK:g}")}٪، تنزل إلى '
                  f'{ar(f"{D_CUT:g}")}٪ بعد {ar(D_RUN)} خسائرَ متتالية '
                  f'وترجع بأوّل رابحة',
                  "وبدونها ما في شي ينقاس", hi=1)


def d_runs(r=None, Wd=880, H=250):
    """٢ · ثلاثُ بذورٍ — والنتيجةُ سالبة."""
    items = []
    for s in D_SEEDS:
        items.append((f'بذرة {ar(s)}', D_RES[s]["سلّم"] - D_RES[s]["ثابتة"],
                      D_RES[s]["سلّم"] < D_RES[s]["ثابتة"]))
    return _bars(Wd, H, items,
                 f'السلّم خسر في {ar(D_LOSS)} من {ar(len(D_SEEDS))}',
                 'الفرقُ بين رأس المال بالسلّم وبالثابتة — سالبٌ في '
                 'اثنتين ونقطةٌ في الثالثة',
                 "والنقطةُ الواحدة ما هي تقدّماً", tag="مثال تخطيطي", neg=True)


def d_why(r=None, Wd=880, H=250):
    """٣ · ليش نزل: الصفقةُ ما تعرف التي قبلها."""
    return _steps(Wd, H,
                  [("٣ خسائر", "تنزل حجمك"),
                   ("الرابحة الجاية", "بنصف حجمك"),
                   ("ترجع", "بعد ما فات")],
                  "تنزل قبل التعافي، فتأخذ نصفَه",
                  'الصفقاتُ مستقلّة، والخسائرُ الثلاث لا تخبرك عن '
                  'الرابعة — والسلّمُ يقصّ حجمَك بعدها',
                  "القصُّ يقع على الجهة الغلط", tag="مثال تخطيطي", hi=1)


def d_cond(r=None, Wd=880, H=250):
    """٤ · ومتى ينفع السلّمُ فعلاً؟"""
    return _steps(Wd, H,
                  [("تتجمّع", "الخسائر"), ("ينفع", "السلّم"),
                   ("يُقاس", "قبل ما تعتمده")],
                  "ينفع لو كانت الخسائرُ تتجمّع",
                  'لو تجمّعت خسائرُك بسببٍ واحد — سوقٌ لا يناسبك أو '
                  'حالةٌ نفسية — فالسلّمُ يحميك',
                  "شرطٌ ما نعرف تحقّقه إلا بالعدّ", tag="مثال تخطيطي", hi=2)


def d_test(r=None, Wd=880, H=250):
    """٥ · الثابتةُ بجانب السلّم — عمودان لكلِّ بذرة.

    كانت أعمدةُ هذي اللوحة نموَّ رأس المال بالسلّم وحده، فتخرج ثلاثةُ
    أعمدةٍ موجبةٍ تحت عنوانٍ يقول «يخسر في اثنتين» — والعينُ تصدّق العمود
    لا السطر (رُئي في الرندر). فصارت كلُّ بذرةٍ عمودين متجاورين، والمؤطَّرُ
    منهما السلّم: يُرى أقصرَ في اثنتين وأطولَ في واحدة."""
    items = []
    for s_ in D_SEEDS:
        items.append((f'{ar(s_)} ثابتة', round(D_RES[s_]["ثابتة"] - D_BASE, 1),
                      False))
        items.append((f'{ar(s_)} سلّم', round(D_RES[s_]["سلّم"] - D_BASE, 1),
                      True))
    return _bars(Wd, H, items,
                 f'الثابتةُ أعلى في {ar(D_LOSS)} من {ar(len(D_SEEDS))}',
                 'نفسُ الصفقات ونفسُ ترتيبها — والفرقُ بندُ الحجم وحده، '
                 'والمؤطَّرُ هو السلّم',
                 "قِس على دفترك قبل ما تعتمده", tag="مثال تخطيطي")


# ═════════════════════════════════════════════════════════════════
# ٥ · «صياغة» — الادّعاءُ الذي لا يُحسم من الشموع (الموضوع ١٧٢)
#     قياسٌ على النوافذ الستّ نفسِها، ولوحةٌ واحدةٌ تخطيطيةٌ تشرح الشمعة
# ═════════════════════════════════════════════════════════════════
#: هذي الوحدةُ هي درسُ اليوم نفسُه مكتوباً درساً: «بلغت هدفَها ثم رجعت»
#: جملةٌ تبدو قابلةً للعدّ ولا تُحسم، لأن الشمعةَ أربعةُ أرقامٍ بلا ترتيب.
Y_AMB = [x for x in STOPPED if x["amb"]]
Y_CLR = [x for x in STOPPED if not x["amb"]]
Y_PRE = sorted(x["pre"] for x in Y_CLR)
Y_ZERO = sum(1 for p in Y_PRE if p == 0)
Y_HALF = sum(1 for p in Y_PRE if p < 0.5)
Y_EXEC = len(Y_PRE) - Y_HALF
Y_MED = st.median(Y_PRE)
Y_NZ = [p for p in Y_PRE if p > 0]
Y_SHARE = len(Y_AMB) / len(STOPPED)
assert (len(Y_AMB), len(Y_CLR)) == (8, 28), (len(Y_AMB), len(Y_CLR))
assert round(Y_SHARE * 100) == 22
assert (Y_ZERO, Y_HALF, Y_EXEC) == (22, 23, 5), (Y_ZERO, Y_HALF, Y_EXEC)
assert Y_MED == 0.0 and len(Y_NZ) == 6, (Y_MED, Y_NZ)
#: ورقمان صادقان لسؤالين: «ما تحرّكت أبداً» ٢٢، و«ما بلغت نصفَ مخاطرتها»
#: ٢٣ — وبينهما صفقةٌ واحدةٌ تحرّكت ٠.٢٥ من مخاطرتها.
assert Y_HALF - Y_ZERO == 1 and Y_NZ[0] == 0.2458, Y_NZ
Y_TOP = 2.0                       # مدى المحور: من الصفر إلى الهدف


def _arr(x, y0, y1, col, w=2.0):
    """سهمٌ رأسيٌّ متقطّع — رأسُه عند `y1` يلامس المستوى ولا يتجاوزه."""
    d = 1 if y1 > y0 else -1
    hd = _fs(9)
    return (f'<line x1="{x:.1f}" y1="{y0:.1f}" x2="{x:.1f}" '
            f'y2="{y1 - d * hd:.1f}" stroke="{col}" stroke-width="{w}" '
            f'stroke-dasharray="6 5"/>'
            f'<polygon points="{x:.1f},{y1:.1f} '
            f'{x - hd * 0.62:.1f},{y1 - d * hd:.1f} '
            f'{x + hd * 0.62:.1f},{y1 - d * hd:.1f}" fill="{col}"/>')


def y_claim(r=None, Wd=880, H=250):
    """١ · جملةٌ تبدو منضبطةً وتُعدّ بالورق."""
    return _steps(Wd, H,
                  [("بلغت الهدف", "الادّعاء"), ("ثم رجعت", "تكملتُه"),
                   ("صنفُ خطأ", "ما يُبنى عليه")],
                  "جملةٌ تبدو قابلةً للعدّ",
                  'تسمعها كلَّ يوم وتحطّها في دفترك خانةً وتعدّها — '
                  'والسؤالُ قبلها: تُحسم من بياناتي؟',
                  "اللي ما ينعدّ ما ينفحص", hi=2, tag="الادّعاء كما يُقال")


def y_bar(r=None, Wd=880, H=250):
    """٢ · شمعةٌ واحدةٌ فيها الوقفُ والهدف — ولا تقول أيَّهما سبق.

    شمعةٌ مرسومةٌ لتوضيح شكل البيانات، لا منتزَعةٌ من نافذة — فعليها
    وحدَها من لوحات الوحدة شارةُ «مثال تخطيطي»."""
    svg = _blank(Wd, H)
    pl, pr = 60, max(150, int(Wd * 0.19))
    pt, pb = max(96, int(H * 0.11)), max(112, int(H * 0.16))
    pw, ph = Wd - pl - pr, H - pt - pb
    cx = pl + pw * 0.46
    bw = min(pw * 0.15, _fs(52))
    y_t, y_e, y_s = pt + ph * 0.14, pt + ph * 0.50, pt + ph * 0.86
    y_hi, y_lo = pt + ph * 0.02, pt + ph * 0.98
    lvl = ((y_t, "هدف", TEAL_D), (y_e, "دخول", INK), (y_s, "وقف", RED))
    for yy, nm, col in lvl:
        svg += (f'<line x1="{pl:.1f}" y1="{yy:.1f}" x2="{pl + pw:.1f}" '
                f'y2="{yy:.1f}" stroke="{col}" stroke-width="1.7"/>')
        svg += htext(pl + pw + pr * 0.42, yy + _fs(7), nm, col, _fs(20))
    # الفتيلُ يتجاوز المستويين معاً، والجسمُ هابطٌ يغطّي ما بينهما.
    svg += (f'<line x1="{cx:.1f}" y1="{y_hi:.1f}" x2="{cx:.1f}" '
            f'y2="{y_lo:.1f}" stroke="{INK}" stroke-width="2.6"/>')
    svg += bar(cx - bw / 2, pt + ph * 0.24, bw, ph * 0.54, INK, 0.88)
    svg += _arr(cx - bw * 1.15, y_e, y_t, TEAL_D)
    svg += _arr(cx + bw * 1.15, y_e, y_s, RED)
    svg += htext(cx - bw * 1.15, y_t - _fs(12), "؟", TEAL_D, _fs(26))
    svg += htext(cx + bw * 1.15, y_s + _fs(28), "؟", RED, _fs(26))
    svg += badge(Wd, "مثال تخطيطي", True)
    svg += RC._title(Wd, rt("شمعةٌ واحدة — وقفٌ وهدفٌ في مداها"))
    svg += RC._why(Wd, H,
                   'الشمعةُ أربعةُ أرقامٍ بلا ترتيب — فأيُّهما وصله '
                   'السعرُ أولاً؟ لا جوابَ في المصدر', RED)
    svg += sm(Wd, H, "ومو نقصٌ بأداتك — هذا شكلُ البيانات نفسها")
    return svg + "</svg>"


def y_eight(r=None, Wd=880, H=250):
    """٣ · ثمانٍ من ستٍّ وثلاثين بلا جواب — مربّعٌ لكلِّ صفقة."""
    svg = _blank(Wd, H)
    pl = 46
    pt, pb = max(92, int(H * 0.10)), max(96, int(H * 0.15))
    per = 12
    cell = (Wd - pl * 2) / per
    rows = -(-len(STOPPED) // per)
    #: ارتفاعُ الصفّ يتبع المربّع لا اللوحة: بقسمة الارتفاع كلِّه على ثلاثة
    #: صفوفٍ تتناثر ستٌّ وثلاثون في فراغٍ طولُه صفحة (رُئي في رندر ٧٢).
    rowh = min((H - pt - pb) / max(1, rows), cell * 1.18)
    sq = min(cell * 0.60, rowh * 0.62)
    top0 = pt + ((H - pt - pb) - rowh * rows) / 2
    #: الملتبساتُ أولاً في اليمين ليقع البصرُ عليهنّ مجتمعاتٍ لا مبعثرات.
    for k, amb in enumerate([True] * len(Y_AMB) + [False] * len(Y_CLR)):
        cx = pl + (Wd - pl * 2) - (cell * (k % per) + cell / 2)
        cy = top0 + rowh * (k // per) + rowh / 2
        svg += bar(cx - sq / 2, cy - sq / 2, sq, sq,
                   RED if amb else TEAL, 0.85 if amb else 0.34)
    svg += badge(Wd, "قياسٌ على ستّ نوافذ", True)
    svg += RC._title(Wd, rt(f'{ar(len(Y_AMB))} من {ar(len(STOPPED))} = '
                            f'{ar(round(Y_SHARE * 100))}٪ بلا جواب'))
    svg += RC._why(Wd, H,
                   'عدُّها أهدافاً يولّد صنفاً كاملاً، وعدُّها وقفاتٍ '
                   'يمحوه — نفسُ الشموع ورقمان ضدّان', RED)
    svg += sm(Wd, H, "الرقمُ يتغيّر باصطلاحك، مو بالسوق")
    return svg + "</svg>"


def y_clear(r=None, Wd=880, H=250):
    """٤ · والثمانُ والعشرون تُحسم — ومدرَّجٌ لأقصى تحرّكٍ مواتٍ.

    كانت نقطةً لكلِّ صفقة، فصارت الثنتان والعشرون صفراً عموداً أحمرَ
    رفيعاً والستُّ الباقيات ذرّاتٍ لا تُرى في لوحة الدليل القصيرة (رُئي
    في الرندر). والمدرَّجُ يُقرأ في أيِّ ارتفاع، وعددُ الصفر مكتوبٌ عليه."""
    svg = _blank(Wd, H)
    pl, pr = 66, 66
    pt, pb = max(96, int(H * 0.11)), max(118, int(H * 0.17))
    pw, ph = Wd - pl - pr, H - pt - pb
    #: الصفرُ في اليمين والهدفُ في اليسار — فالتقدّمُ نحو الهدف يمشي مع
    #: اتجاه القراءة، ولا يُقرأ المحورُ بالمقلوب.

    def xx(v):
        return pl + pw - pw * (min(v, Y_TOP) / Y_TOP)

    y0 = pt + ph * 0.90
    svg += (f'<line x1="{pl:.1f}" y1="{y0:.1f}" x2="{pl + pw:.1f}" '
            f'y2="{y0:.1f}" stroke="rgba(15,46,60,0.22)" stroke-width="1.5"/>')
    for v, nm, col in ((0.5, "نصفُ المخاطرة", MUTE), (Y_TOP, "الهدف", TEAL_D)):
        svg += (f'<line x1="{xx(v):.1f}" y1="{pt + ph * 0.04:.1f}" '
                f'x2="{xx(v):.1f}" y2="{y0:.1f}" stroke="{col}" '
                f'stroke-width="1.6" stroke-dasharray="5 6"/>')
        svg += htext(xx(v), y0 + _fs(26), nm, col, _fs(16))
    svg += htext(xx(0.0), y0 + _fs(26), "صفر", INK, _fs(16))
    cnt = {v: Y_PRE.count(v) for v in sorted(set(Y_PRE))}
    top = max(cnt.values())
    bw = max(_fs(7), pw * 0.016)
    for v, c in cnt.items():
        # جذرُ النسبة كي يبقى العمودُ الواحد مرئياً بجانب عمودِ اثنين
        # وعشرين، لا شعرةً بنسبة واحدٍ على اثنين وعشرين.
        hh = ph * 0.74 * (c / top) ** 0.5
        svg += bar(xx(v) - bw / 2, y0 - hh, bw, hh,
                   RED if v < 0.5 else TEAL_D, 0.85)
    zh = ph * 0.74
    svg += htext(xx(0.0) - _fs(4), y0 - zh - _fs(12), ar(Y_ZERO), RED, _fs(26))
    svg += badge(Wd, "قياسٌ على ستّ نوافذ", True)
    svg += RC._title(Wd, rt(f'{ar(Y_ZERO)} من {ar(len(Y_CLR))} ما تحرّكت '
                            f'ولا شمعة'))
    svg += RC._why(Wd, H,
                   f'أقصى تحرّكٍ مواتٍ قبل شمعة الوقف: وسيطُه {ar("0.00")}R '
                   f'وأعلاه {ar("1.18")}R — ولا واحدةٌ قاربت الهدف', RED)
    svg += sm(Wd, H, f'{ar(Y_ZERO)} و{ar(Y_HALF)} — رقمان لسؤالين')
    return svg + "</svg>"


def y_fix(r=None, Wd=880, H=250):
    """٥ · الصياغةُ التي تنفع: مرجعٌ ونافذةٌ واصطلاح."""
    return _steps(Wd, H,
                  [("مرجع", "من أيِّ رقم"), ("نافذة", "خلال كم شمعة"),
                   ("اصطلاح", "عند الالتباس")],
                  "ثلاثةُ بنودٍ تحوّل الجملة إلى عدّ",
                  '«بلغت الهدف» ما تنحسم، و«أغلقت شمعةٌ خلف الهدف خلال '
                  'خمس» تنحسم — والفرقُ ثلاثةُ بنود',
                  "اللي ما ينعدّ ما ينفحص", hi=0, tag="قاعدةُ الصياغة")


# ═════════════════════════════════════════════════════════════════
#  المجموعاتُ والبصماتُ والنوافذ
# ═════════════════════════════════════════════════════════════════
SETS = {"tasalsul": [t_edge, t_pairs, t_split, t_flip, t_run],
        "jihatayn": [j_both, j_six, j_counts, j_move, j_cross],
        "musawama": [w_one, w_tight, w_wide, w_net, w_buy],
        "sullam": [d_rule, d_runs, d_why, d_cond, d_test],
        "siyagha": [y_claim, y_bar, y_eight, y_clear, y_fix]}
#: بصمةُ «سلّم» في السجل: بذرتُها الأولى، ومرتكزاها متتاليتان — بارامترات
#: المحاكاة وبذورُها الثلاث — فلو أُعيدت المحاكاةُ ببذرةٍ منها كُشف التكرار.
SYN = {"sullam": (D_SEEDS[0],
                  [(D_N, D_P, D_BASE, D_RISK, D_CUT, D_RUN), D_SEEDS])}
REAL = {"tasalsul": S_WIN, "jihatayn": J_WIN}
#: وحدتا العدّ لا ترسمان سلسلةَ أسعارٍ أصلاً — لا نافذةً سوقيةً ولا
#: مولَّدة — فلا بصمةَ لهما في سجلّ عدم التكرار ولا شيءَ يُحجز. والشمعةُ
#: الواحدة في `y_bar` رسمٌ توضيحيٌّ بأربعة أرقامٍ مكتوبةٍ في الكود، لا
#: نافذةٌ ولا توليد.
COUNT = {"musawama", "siyagha"}
assert COUNT == set(SETS) - set(REAL) - {"sullam"}
#: «سلّم» محاكاةٌ بلا سوق، و«مساومة» و«صياغة» عدٌّ يشمل ستَّ نوافذ — ولا
#: واحدةٌ منهنّ لها نافذةٌ تُسمّى. وإعطاؤها نافذةَ وحدةٍ أخرى يجعل سجلَّ
#: البناء يكذب على نفسه، فالبديلُ سجلٌّ يقول ما هو.
_NOWIN = {"slug": "مثال تخطيطي — بلا نافذة", "w": [], "sym": "", "tf": ""}
_SIXWIN = {"slug": "قياسٌ على ستّ نوافذ — بلا نافذةٍ واحدة",
           "w": [], "sym": "", "tf": ""}
WINS = {"tasalsul": RS, "jihatayn": RJ, "musawama": _SIXWIN,
        "sullam": _NOWIN, "siyagha": _SIXWIN}
assert set(SETS) == set(WINS) and set(REAL) <= set(SETS)
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
    print(f'تسلسل · {RS["slug"]} · {S_N} شمعة  [سوقٌ حقيقي]')
    print(f'  {len(S_END)} طرفاً ← {len(S_PAIR)} زوجاً · '
          f'صاعدة {S_UP} وهابطة {S_DN} · انقلابات {len(S_FLIP)} من '
          f'{len(S_PAIR) - 1}')
    print(f'  أطول سلسلة {S_RUN[1]} زوج · من الشمعة {S_RA} إلى {S_RB} = '
          f'{S_SPAN} شمعة = {S_SHARE:.0%} من النافذة')

    print(f'\nجهتين · {RJ["slug"]} · {J_N} شمعة  [سوقٌ حقيقي]')
    print(f'  {len(J_END)} طرفاً · لم يُبلغ منها {len(J_NONE)} · '
          f'ولُمس من الجهتين {len(J_BOTH)} من {len(J_LV) - len(J_NONE)}')
    print(f'  اللمسات {[(e["up"], e["dn"]) for e in J_BOTH]} · '
          f'المجموع من {min(J_TOT)} إلى {max(J_TOT)}')
    print(f'  الابتعاد بعد اللمسة الثانية بأفق {J_HOR} شمعات على الإغلاقات: '
          f'وسيطُه {J_AWAY:.2f}× المدى · وعبرت {J_CROSS} من {len(J_BOTH)}')

    print(f'\nمساومة  [قياسٌ على ستّ نوافذ]')
    print(f'  {N_TR} دخلة · ثابت {T_WIN} ({T_RATE:.0%}) · '
          f'موسَّع {W_WIN} ({W_RATE:.0%}) · أُنقذت {SAVED}')
    print(f'  الصافي {T_NET:+g}R و{W_NET:+g}R · '
          f'ملتبس {T_AMB} و{W_AMB} · صفرية {FLAT}')

    print(f'\nسلّم · بذور {D_SEEDS}  [تخطيطي]')
    for s in D_SEEDS:
        print(f'    {s:<5} ثابتة {D_RES[s]["ثابتة"]:.1f} · '
              f'سلّم {D_RES[s]["سلّم"]:.1f}')
    print(f'  خسر السلّمُ في {D_LOSS} من {len(D_SEEDS)}')

    print(f'\nصياغة  [قياسٌ على ستّ نوافذ]')
    print(f'  موقوفة {len(STOPPED)} · ملتبسة {len(Y_AMB)} = '
          f'{Y_SHARE:.0%} · واضحة {len(Y_CLR)}')
    print(f'  صفرٌ تماماً {Y_ZERO} · دون نصف المخاطرة {Y_HALF} '
          f'({Y_HALF / len(Y_CLR):.0%}) · تنفيذ {Y_EXEC}')
    print(f'  الوسيط {Y_MED:.2f}R · غيرُ الصفرية {Y_NZ}')
