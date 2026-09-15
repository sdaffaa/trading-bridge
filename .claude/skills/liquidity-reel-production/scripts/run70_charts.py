# -*- coding: utf-8 -*-
"""جارتات تشغيلة ٧٠ — وحدةٌ على سوقٍ حقيقي والباقي تخطيطي.

    مهلة ← النافذة ٧٠ · الكاردانو/دولار · ساعة · 2025-10-03 · فئة `chan`

وهي **النافذة الحرّة الوحيدة** في المخزون كلِّه (٧٢ مرشّحاً، قِيس فراغُها
بالدالّة التي تحرسه: `run31_charts._span` ثم `assert_fresh_real`). وكانت
قد سُجِّلت في تشغيلة ٦٩ ثم أُلغي قيدُها حين أُسقطت وحدةُ «ترند» لخروجها
عن النطاق — فعادت حرّة، وتُبنى اليوم على الموضوع ١٥٠ «مهلة»: كم شمعةً
بين سحب السيولة وكسر الهيكل؟

والباقي بقاعدة §11 البديلة: شارة «مثال تخطيطي» على كل لوحة · كلُّ ادّعاءٍ
مقيسٌ بـ`assert` · أعدادٌ ونِسبٌ لا أسعار.

    python3 run70_charts.py
"""
import statistics as st

from reel_build import INK, TEAL, TEAL_D, RED, gen
from run15_charts import hl, badge, frame
import run31_charts as RC
from run58_charts import ar, rt, sm, band, mark
from run59_charts import spanx, vspan, xr


def _real(W, n):
    """حارسُ §4 — **للسلاسل المولّدة وحدها**.

    هو اختبارُ واقعيةٍ يقيس المولَّد على إحصاء السوق، فلا يُدار على نافذةٍ
    حقيقية: السوق هو المرجع الذي عُوير به الحارس، ولا يُحاكَم بحاكيه.
    (قِيس: نافذة الكاردانو الحقيقية وسيطُ مداها ١٫٧٠ وسيطَ جسمها — تحت
    أرضية ١٫٩ الموضوعة للمولَّد. فلو أُديرَ عليها لأسقط سوقاً صادقاً.)
    ولذلك تناديه تشغيلتا ٦٨ و٦٩ على السلاسل المولّدة فقط."""
    R = [c["h"] - c["l"] for c in W]
    B = [abs(c["c"] - c["o"]) for c in W]
    dn = sum(1 for c in W if c["c"] < c["o"])
    med, bod = st.median(R), st.median(B)
    assert st.pstdev(R) / st.mean(R) >= 0.45, st.pstdev(R) / st.mean(R)
    assert dn >= n * 0.30, f"الهابطة {dn} من {n} — سلّمٌ لا سوق"
    assert 1.9 <= med / bod <= 3.1, f"وسيط المدى {med/bod:.2f} وسيطَ الجسم"
    assert max(R) / med <= 3.6, f"أطول شمعة {max(R)/med:.2f}× — تسحق اللوحة"


def dot(x, y, col=INK, r=5.0):
    """نقطةٌ مجوّفة — تُعلّم طرفاً دون أن تحجب الشمعة تحتها."""
    return (f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="#F2EEE7" '
            f'stroke="{col}" stroke-width="2"/>')


# ═════════════════════════════════════════════════════════════════
# ١ · «مهلة» — كم شمعة بين السحب وكسر الهيكل؟
#     (فنية · ريل · سوقٌ حقيقي — الموضوع ١٥٠)
#     الكاردانو/دولار · ساعة · 2025-10-03 · ٤٢ شمعة
# ═════════════════════════════════════════════════════════════════
H_WIN = 70
RH = RC.win(H_WIN)
WH = RH["w"]
H_N = len(WH)
H_MED = st.median(c["h"] - c["l"] for c in WH)
H_BOD = st.median(abs(c["c"] - c["o"]) for c in WH)


def _sw_lo(W, k=2):
    return [i for i in range(k, len(W) - k)
            if all(W[i]["l"] < W[j]["l"] for j in range(i - k, i + k + 1) if j != i)]


def _sw_hi(W, k=2):
    return [i for i in range(k, len(W) - k)
            if all(W[i]["h"] > W[j]["h"] for j in range(i - k, i + k + 1) if j != i)]


H_SL, H_SH = _sw_lo(WH), _sw_hi(WH)

# حدثُ السحب: شمعةٌ تخرق قاعَ سوينقٍ سابقاً ثم **تغلق فوقه**. والمهلة =
# عددُ الشمعات حتى أول إغلاقٍ يكسر آخر قمّة سوينق قبل السحب.
H_EV = []
for _i in range(3, H_N - 1):
    _pl = [j for j in H_SL if j < _i - 1]
    if not _pl:
        continue
    _lvl = WH[_pl[-1]]["l"]
    if not (WH[_i]["l"] < _lvl and WH[_i]["c"] > _lvl):
        continue
    _ph = [j for j in H_SH if j < _i]
    if not _ph:
        continue
    _top = WH[_ph[-1]]["h"]
    _brk = next((j for j in range(_i + 1, H_N) if WH[j]["c"] > _top), None)
    _end = _brk if _brk else H_N - 1
    _adv = (WH[_i]["c"] - min(WH[j]["l"] for j in range(_i, _end + 1))) / H_MED
    H_EV.append({"sw": _i, "lvl": _lvl, "ti": _ph[-1], "top": _top,
                 "brk": _brk, "gap": (_brk - _i) if _brk else None,
                 "adv": _adv})

H_DONE = [e for e in H_EV if e["brk"]]
H_GAPS = [e["gap"] for e in H_DONE]
H_ONE = [e for e in H_DONE if e["gap"] == 1]
H_LONG = [e for e in H_DONE if e["gap"] >= 4]
H_MAXADV = max(e["adv"] for e in H_DONE)
H_MEDGAP = st.median(H_GAPS)
H_FAST = min(H_DONE, key=lambda e: (e["gap"], e["sw"]))
H_SLOW = max(H_DONE, key=lambda e: (e["gap"], -e["sw"]))

assert len(H_EV) == 8, len(H_EV)
assert len(H_DONE) == 8, len(H_DONE)
assert len(H_ONE) == 3, len(H_ONE)
assert len(H_LONG) == 5, len(H_LONG)
assert len(H_ONE) + len(H_LONG) == len(H_DONE), "حدثٌ خارج الفئتين"
assert H_SLOW["gap"] == 8, H_SLOW["gap"]
assert 2.4 <= H_MAXADV <= 2.7, H_MAXADV


def _gh(Wd, H):
    return frame(WH, Wd, H, pad=0.08, pb=64)


def _ev(svg, x, y, slot, e, col=TEAL):
    """يرسم مستوى السحب وقمّة الهيكل وشمعتَي الحدث."""
    svg += hl(x(0) - slot * .5, x(H_N - 1) + slot * .5, y(e["lvl"]), INK, 1.7)
    svg += hl(x(e["ti"]) - slot * .5, x(H_N - 1) + slot * .5, y(e["top"]),
              INK, 1.5, "5 5")
    svg += mark(x(e["sw"]), slot, y(WH[e["sw"]]["h"]), y(WH[e["sw"]]["l"]),
                RED, 0.24)
    if e["brk"]:
        svg += mark(x(e["brk"]), slot, y(WH[e["brk"]]["h"]), y(WH[e["brk"]]["l"]),
                    col, 0.24)
    return svg


def h_sweep(r=None, Wd=880, H=250):
    """١ · ما هو السحب: خرقٌ للقاع ثم إغلاقٌ فوقه."""
    e = H_SLOW
    svg, x, y, slot = _gh(Wd, H)
    svg += hl(x(0) - slot * .5, x(H_N - 1) + slot * .5, y(e["lvl"]), INK, 1.7)
    svg += mark(x(e["sw"]), slot, y(WH[e["sw"]]["h"]), y(WH[e["sw"]]["l"]),
                RED, 0.26)
    svg += spanx(x(e["sw"]) - slot * 2.2, x(e["sw"]) + slot * 2.2,
                 y(e["lvl"]) + 36, rt("خرقٌ ثم إغلاقٌ فوق"), RED)
    svg += RC._title(Wd, rt("السحب: ينزل تحت القاع ويغلق فوقه"))
    svg += RC._why(Wd, H, 'هذي اللحظة اللي يقول عندها الكل «انقلب» — '
                          'والهيكل لِحدّ الحين ما انكسر', RED)
    svg += sm(Wd, H, "والفرق بين الاثنين هو كل الدرس")
    return svg + "</svg>"


def h_fast(r=None, Wd=880, H=250):
    """٢ · أسرعُ حدث: شمعةٌ واحدة بين السحب والكسر."""
    e = H_FAST
    svg, x, y, slot = _gh(Wd, H)
    svg = _ev(svg, x, y, slot, e)
    svg += spanx(x(e["sw"]), x(e["brk"]), y(e["top"]) - 30,
                 rt(f'{ar(e["gap"])} شمعة'), TEAL_D)
    svg += RC._title(Wd, rt("أحياناً شمعة وحدة وخلاص"))
    svg += RC._why(Wd, H, f'السحب ثم كسرُ القمّة بعده بشمعة — '
                          f'{ar(len(H_ONE))} من {ar(len(H_DONE))} أحداثٍ كذلك',
                   TEAL_D)
    svg += sm(Wd, H, "وهذي اللي تخلّيك تتوقّع إنها دايماً سريعة")
    return svg + "</svg>"


def h_slow(r=None, Wd=880, H=250):
    """٣ · أبطأُ حدث: ثمان شمعات، وتحرّكٌ ضدّك في أثنائها."""
    e = H_SLOW
    svg, x, y, slot = _gh(Wd, H)
    svg = _ev(svg, x, y, slot, e)
    _lo = min(range(e["sw"], e["brk"] + 1), key=lambda k: WH[k]["l"])
    svg += band(x(e["sw"]) - slot * .5, x(e["brk"]) + slot * .5,
                y(WH[e["sw"]]["c"]), y(WH[_lo]["l"]), RED, 0.13)
    svg += spanx(x(e["sw"]), x(e["brk"]), y(e["top"]) - 30,
                 rt(f'{ar(e["gap"])} شمعات'), RED)
    svg += RC._title(Wd, rt("وأحياناً ثمان — وتنزف وانت تنتظر"))
    svg += RC._why(Wd, H, f'وفي أثنائها نزل ضدّ الفكرة {xr(e["adv"])} '
                          f'وسيطَ المدى قبل ما ينكسر الهيكل', RED)
    svg += sm(Wd, H, "لو دخلت على السحب وحده، هالثمان يطلعونك")
    return svg + "</svg>"


def h_spread(r=None, Wd=880, H=250):
    """٤ · توزيع الأحداث الثمانية."""
    svg, x, y, slot = _gh(Wd, H)
    for e in H_DONE:
        svg += mark(x(e["sw"]), slot, y(WH[e["sw"]]["h"]), y(WH[e["sw"]]["l"]),
                    TEAL if e["gap"] == 1 else RED, 0.20)
    svg += RC._title(Wd, rt("ثمان كنسات، ثلاث سريعة وخمس بطيئة"))
    svg += RC._why(Wd, H, f'{ar(len(H_ONE))} حُسمن بالشمعة التالية، '
                          f'و{ar(len(H_LONG))} احتجن أربعاً فأكثر — '
                          f'والوسيط {ar(int(H_MEDGAP))} شمعات ونصف', INK)
    svg += sm(Wd, H, "يعني الغالب بطيء، مو سريع")
    return svg + "</svg>"


def h_all(r=None, Wd=880, H=250):
    """٥ · الخلاصة: الإشارة هي الكسر لا السحب."""
    svg, x, y, slot = _gh(Wd, H)
    e = H_SLOW
    svg = _ev(svg, x, y, slot, e)
    svg += spanx(x(e["sw"]), x(e["brk"]), y(e["top"]) - 30,
                 rt("المهلة"), INK)
    svg += RC._title(Wd, rt("السحب يفتح الباب، والكسر هو الدخول"))
    svg += RC._why(Wd, H, f'أقصى ما تحرّك ضدّ الفكرة في المهلة '
                          f'{xr(H_MAXADV)} وسيطَ المدى — فوقفُك لازم يحتملها '
                          f'أو تنتظر الكسر', TEAL_D)
    svg += sm(Wd, H, "تنتظر شمعة زيادة أرخص من إنك تنضرب وتشوفها تطلع")
    return svg + "</svg>"


# ═════════════════════════════════════════════════════════════════
# ٢ · «ضجيج» — أكثرُ الشمعات لا تقول شيئاً (نفسية · كاروسيل · تخطيطي)
# ═════════════════════════════════════════════════════════════════
G_SEED = 713
G_ANCH = [(0, 100.0), (9, 100.9), (18, 99.8), (27, 100.6), (39, 101.5)]
G_N = 40
G_OPEN = 12                                # الحدّان يُرسمان من أول ١٢ شمعة
WG = gen(G_ANCH, G_N, G_SEED, wick=0.6, bn=0.5)
RG = {"sym": "SCHEMATIC-G", "slug": "مثال تخطيطي — ضجيج", "w": WG}
G_MED = st.median(c["h"] - c["l"] for c in WG)
G_HI = max(c["h"] for c in WG[:G_OPEN])
G_LO = min(c["l"] for c in WG[:G_OPEN])
G_TOT = G_N - G_OPEN
G_QUIET = [i for i in range(G_OPEN, G_N)
           if (WG[i]["h"] - WG[i]["l"]) < G_MED
           and WG[i]["h"] < G_HI and WG[i]["l"] > G_LO]
G_MOVED = [i for i in range(G_OPEN, G_N) if WG[i]["c"] > G_HI or WG[i]["c"] < G_LO]
G_SHARE = len(G_QUIET) / G_TOT

_real(WG, G_N)
assert len(G_QUIET) == 17, len(G_QUIET)
assert len(G_MOVED) == 2, len(G_MOVED)
assert 0.55 <= G_SHARE <= 0.72, G_SHARE


def _gg(Wd, H):
    return frame(WG, Wd, H, pad=0.10, pb=66)


def _bounds(svg, x, y, slot):
    svg += hl(x(0) - slot * .5, x(G_N - 1) + slot * .5, y(G_HI), INK, 1.6)
    svg += hl(x(0) - slot * .5, x(G_N - 1) + slot * .5, y(G_LO), INK, 1.6)
    return svg


def g_draw(r=None, Wd=880, H=250):
    """١ · حدّان مرسومان من أول اثنتي عشرة شمعة."""
    svg, x, y, slot = _gg(Wd, H)
    svg = _bounds(svg, x, y, slot)
    svg += band(x(0) - slot * .5, x(G_OPEN - 1) + slot * .5, y(G_HI), y(G_LO),
                TEAL_D, 0.10)
    svg += badge(Wd, "مثال تخطيطي", True)
    svg += RC._title(Wd, rt("حدّان وبس — هذا كل اللي رسمته"))
    svg += RC._why(Wd, H, f'قمّةُ أول {ar(G_OPEN)} شمعة وقاعُها — '
                          f'وكلُّ اللي بعدهن يُقاس عليهن', INK)
    svg += sm(Wd, H, "الحدّ مرجع، والباقي إمّا يلمسه أو ما يلمسه")
    return svg + "</svg>"


def g_quiet(r=None, Wd=880, H=250):
    """٢ · سبعَ عشرة شمعة لا لمست حدّاً ولا بلغت وسيطَ المدى."""
    svg, x, y, slot = _gg(Wd, H)
    svg = _bounds(svg, x, y, slot)
    for i in G_QUIET:
        svg += mark(x(i), slot, y(WG[i]["h"]), y(WG[i]["l"]), INK, 0.14)
    svg += badge(Wd, "مثال تخطيطي", True)
    svg += RC._title(Wd, rt("سبعَ عشرة منهن ما سوّن شي"))
    svg += RC._why(Wd, H, f'{ar(len(G_QUIET))} من {ar(G_TOT)} — مداها تحت '
                          f'وسيط المدى ولا لمست حدّاً: {ar(round(G_SHARE*100))}٪',
                   INK)
    svg += sm(Wd, H, "وكل وحدة منهن كتبت لها سبباً برأسك")
    return svg + "</svg>"


def g_moved(r=None, Wd=880, H=250):
    """٣ · شمعتان فقط أغلقتا خارج الحدّين."""
    svg, x, y, slot = _gg(Wd, H)
    svg = _bounds(svg, x, y, slot)
    for i in G_MOVED:
        svg += mark(x(i), slot, y(WG[i]["h"]), y(WG[i]["l"]), TEAL, 0.26)
    svg += badge(Wd, "مثال تخطيطي", True)
    svg += RC._title(Wd, rt("وثنتين غيّرن الصورة"))
    svg += RC._why(Wd, H, f'{ar(len(G_MOVED))} فقط أغلقتا خارج الحدّين — '
                          f'وهما وحدهما اللتان تستحقّان قراءة', TEAL_D)
    svg += sm(Wd, H, "الباقي حركة داخل الغرفة، مو خروج منها")
    return svg + "</svg>"


def g_ratio(r=None, Wd=880, H=250):
    """٤ · النسبة جنباً إلى جنب."""
    svg, x, y, slot = _gg(Wd, H)
    svg = _bounds(svg, x, y, slot)
    for i in G_QUIET:
        svg += mark(x(i), slot, y(WG[i]["h"]), y(WG[i]["l"]), INK, 0.12)
    for i in G_MOVED:
        svg += mark(x(i), slot, y(WG[i]["h"]), y(WG[i]["l"]), TEAL, 0.26)
    svg += badge(Wd, "مثال تخطيطي", True)
    svg += RC._title(Wd, rt("سبعَ عشرة مقابل ثنتين"))
    svg += RC._why(Wd, H, f'{ar(len(G_QUIET))} هادئة و{ar(len(G_MOVED))} '
                          f'فاعلة من {ar(G_TOT)} — والعين تعطيهن الوزن نفسه', INK)
    svg += sm(Wd, H, "وهني يجيك التعب: تقرأ سبعَ عشرة مرّة بلا داعي")
    return svg + "</svg>"


def g_all(r=None, Wd=880, H=250):
    """٥ · الخلاصة: انتظر الحدّ لا الشمعة."""
    svg, x, y, slot = _gg(Wd, H)
    svg = _bounds(svg, x, y, slot)
    for i in G_MOVED:
        svg += mark(x(i), slot, y(WG[i]["h"]), y(WG[i]["l"]), TEAL, 0.26)
        svg += spanx(x(i) - slot * 2.0, x(i) + slot * 2.0, y(G_HI) - 30,
                     rt("هني تقرأ"), TEAL_D)
    svg += badge(Wd, "مثال تخطيطي", True)
    svg += RC._title(Wd, rt("خلّ الحدّ ينادي، لا تنادي أنت"))
    svg += RC._why(Wd, H, f'انتظارُ لمسة الحدّ يوفّر عليك {ar(len(G_QUIET))} '
                          f'قراءة من {ar(G_TOT)}', TEAL_D)
    svg += sm(Wd, H, "ما تحتاج تفسّر السوق، تحتاج تعرف متى يتكلم")
    return svg + "</svg>"


# ═════════════════════════════════════════════════════════════════
# ٣ · «فرز» — خمس أدوات ورقمان يشطبان ثلاثاً (أساسية · كاروسيل · تخطيطي)
# ═════════════════════════════════════════════════════════════════
F_N = 30
F_ANCH = [(0, 100.0), (10, 101.2), (20, 100.1), (29, 101.8)]
F_SEEDS = [62, 69, 17, 24, 625]            # خمسُ «أدوات»: بذرةٌ لكل واحدة
F_NAMES = ["الأولى", "الثانية", "الثالثة", "الرابعة", "الخامسة"]
F_SER, F_M = [], []
for _s in F_SEEDS:
    _W = gen(F_ANCH, F_N, _s, wick=0.6, bn=0.5)
    _real(_W, F_N)
    _med = st.median(c["h"] - c["l"] for c in _W)
    _rng = max(c["h"] for c in _W) - min(c["l"] for c in _W)
    _lvl = max(c["h"] for c in _W[:8])
    _tol = 0.15 * _med
    _tch = sum(1 for i in range(8, F_N)
               if abs(_W[i]["h"] - _lvl) <= _tol or abs(_W[i]["l"] - _lvl) <= _tol)
    F_SER.append(_W)
    F_M.append({"med": _med, "rng": _rng, "lvl": _lvl,
                "steps": _rng / _med, "touch": _tch})
F_WIN = {"sym": "SCHEMATIC-F", "slug": "مثال تخطيطي — فرز", "w": F_SER[0]}
F_KEEP = [i for i, m in enumerate(F_M) if m["steps"] >= 4.0 and m["touch"] > 0]
F_CUT_S = [i for i, m in enumerate(F_M) if m["steps"] < 4.0]
F_CUT_T = [i for i, m in enumerate(F_M) if m["touch"] == 0 and m["steps"] >= 4.0]

assert len(F_KEEP) == 2, [round(m["steps"], 2) for m in F_M]
assert len(F_CUT_S) == 2, F_CUT_S
assert len(F_CUT_T) == 1, F_CUT_T


def _gf(idx, Wd, H):
    return frame(F_SER[idx], Wd, H, pad=0.10, pb=66)


def _fpanel(idx, Wd, H, title, why, col, note):
    W = F_SER[idx]
    m = F_M[idx]
    svg, x, y, slot = _gf(idx, Wd, H)
    svg += hl(x(0) - slot * .5, x(F_N - 1) + slot * .5, y(m["lvl"]), INK, 1.8)
    svg += badge(Wd, "مثال تخطيطي", True)
    svg += RC._title(Wd, rt(title))
    svg += RC._why(Wd, H, why, col)
    svg += sm(Wd, H, note)
    return svg + "</svg>"


def f_keep1(r=None, Wd=880, H=250):
    """١ · أداةٌ تُبقى: خطواتٌ كافية ولمساتٌ على الحدّ."""
    m = F_M[F_KEEP[0]]
    return _fpanel(F_KEEP[0], Wd, H, "الأداة الأولى: تمشي وتلمس",
                   f'مداها {xr(m["steps"])} وسيطَ شمعتها — أي {ar(int(m["steps"]))} '
                   f'خطوات، ولمست الحدّ {ar(m["touch"])} مرّات', TEAL_D,
                   "خطواتٌ تكفي لهدف، وحدٌّ يحترمه السعر")


def f_keep2(r=None, Wd=880, H=250):
    """٢ · أداةٌ ثانية تُبقى."""
    m = F_M[F_KEEP[1]]
    return _fpanel(F_KEEP[1], Wd, H, "والثانية مثلها",
                   f'{xr(m["steps"])} وسيطَ شمعتها و{ar(m["touch"])} لمسات — '
                   f'تعدّي الشرطين', TEAL_D,
                   "ثنتين من خمس، وهذا طبيعي")


def f_slow(r=None, Wd=880, H=250):
    """٣ · تُشطب: المدى لا يتّسع لهدف."""
    m = F_M[F_CUT_S[0]]
    return _fpanel(F_CUT_S[0], Wd, H, "وهذي تمشي بخطوة ونص",
                   f'مداها {xr(m["steps"])} وسيطَ شمعتها فقط — أقلّ من أربع '
                   f'خطوات، فالهدفُ فيها أبعدُ من طاقتها', RED,
                   "تتعب الشمعة وما توصل — اشطبها من الشاشة")


def f_slow2(r=None, Wd=880, H=250):
    """٤ · تُشطب أيضاً لقلّة الخطوات."""
    m = F_M[F_CUT_S[1]]
    return _fpanel(F_CUT_S[1], Wd, H, "وهذي زيّها",
                   f'{xr(m["steps"])} وسيطَ شمعتها — ولو لمست الحدّ '
                   f'{ar(m["touch"])} مرّات، المسافة ما تكفي', RED,
                   "اللمسة بلا مسافة ما تنفع")


def f_deaf(r=None, Wd=880, H=250):
    """٥ · تُشطب: تمشي لكنها لا تسمع الحدّ."""
    m = F_M[F_CUT_T[0]]
    return _fpanel(F_CUT_T[0], Wd, H, "وهذي تمشي بس ما تسمع",
                   f'{xr(m["steps"])} وسيطَ شمعتها — مسافةٌ ممتازة، لكن '
                   f'لمسات الحدّ صفر: ما تحترم المستوى', RED,
                   "أداةٌ تتحرّك بلا مرجع = مخاطرة بلا خريطة")


# ═════════════════════════════════════════════════════════════════
# ٤ · «نمو» — الـR ليست نسبةَ حساب (مالية · كاروسيل · تخطيطي)
# ═════════════════════════════════════════════════════════════════
M_SEED = 2279
M_ANCH = [(0, 100.0), (11, 101.1), (22, 100.3), (33, 101.4), (45, 102.3)]
M_N = 46
M_AT = (6, 14, 22, 30, 38)
M_RISK = 0.5                               # نسبةُ المخاطرة لكل صفقة (٪)
WM = gen(M_ANCH, M_N, M_SEED, wick=0.6, bn=0.5)
RM = {"sym": "SCHEMATIC-M", "slug": "مثال تخطيطي — نمو", "w": WM}
M_MED = st.median(c["h"] - c["l"] for c in WM)
M_TR = []
for _e in M_AT:
    _ent = WM[_e]["c"]
    _stp = _ent - 1.5 * M_MED
    _tgt = _ent + 2 * (_ent - _stp)
    _res = None
    for _j in range(_e + 1, min(_e + 8, M_N)):
        if WM[_j]["l"] <= _stp:
            _res = -1.0
            break
        if WM[_j]["h"] >= _tgt:
            _res = 2.0
            break
    if _res is None:
        _res = (WM[min(_e + 7, M_N - 1)]["c"] - _ent) / (_ent - _stp)
    M_TR.append({"i": _e, "ent": _ent, "stp": _stp, "tgt": _tgt,
                 "r": round(_res, 2)})
M_SUM = round(sum(t["r"] for t in M_TR), 2)
M_WIN = sum(1 for t in M_TR if t["r"] > 0)
M_GROW = M_SUM * M_RISK

_real(WM, M_N)
assert M_WIN == 4, M_WIN
assert abs(M_SUM - 2.86) < 0.01, M_SUM
assert any(t["r"] == 2.0 for t in M_TR), "لا صفقةَ بلغت الهدف"
assert any(t["r"] == -1.0 for t in M_TR), "لا صفقةَ ضربت الوقف"


def _gm(Wd, H):
    return frame(WM, Wd, H, pad=0.10, pb=66)


def _tr_mark(svg, x, y, slot, t, col):
    svg += hl(x(t["i"]) - slot * .5, x(min(t["i"] + 7, M_N - 1)) + slot * .5,
              y(t["ent"]), INK, 1.5)
    svg += band(x(t["i"]) - slot * .5, x(min(t["i"] + 7, M_N - 1)) + slot * .5,
                y(t["ent"]), y(t["stp"]), RED, 0.12)
    svg += mark(x(t["i"]), slot, y(WM[t["i"]]["h"]), y(WM[t["i"]]["l"]), col, 0.24)
    return svg


def m_five(r=None, Wd=880, H=250):
    """١ · خمسُ صفقات على النافذة."""
    svg, x, y, slot = _gm(Wd, H)
    for t in M_TR:
        svg = _tr_mark(svg, x, y, slot, t, TEAL if t["r"] > 0 else RED)
    svg += badge(Wd, "مثال تخطيطي", True)
    svg += RC._title(Wd, rt("خمسُ صفقات، أربعٌ رابحة"))
    svg += RC._why(Wd, H, f'وقفُ كلِّ واحدةٍ وسيطُ مدى ونصف، وهدفُها ضعفا '
                          f'مخاطرتها — والنتيجة تُقرأ من الشموع بعدها', INK)
    svg += sm(Wd, H, "أربع من خمس — نسبةٌ يحبّها أي واحد")
    return svg + "</svg>"


def m_best(r=None, Wd=880, H=250):
    """٢ · الصفقة التي بلغت الهدف."""
    t = next(t for t in M_TR if t["r"] == 2.0)
    svg, x, y, slot = _gm(Wd, H)
    svg = _tr_mark(svg, x, y, slot, t, TEAL)
    svg += hl(x(t["i"]) - slot * .5, x(min(t["i"] + 7, M_N - 1)) + slot * .5,
              y(t["tgt"]), TEAL_D, 1.6, "5 5")
    svg += badge(Wd, "مثال تخطيطي", True)
    svg += RC._title(Wd, rt("وحدةٌ بلغت الهدف كامل"))
    svg += RC._why(Wd, H, 'ضعفا المخاطرة — ٢R، وهي أفضلُ ما في النافذة',
                   TEAL_D)
    svg += sm(Wd, H, "وهذي اللي تتذكّرها وتحكي عنها")
    return svg + "</svg>"


def m_worst(r=None, Wd=880, H=250):
    """٣ · الصفقة التي ضربت الوقف."""
    t = next(t for t in M_TR if t["r"] == -1.0)
    svg, x, y, slot = _gm(Wd, H)
    svg = _tr_mark(svg, x, y, slot, t, RED)
    svg += badge(Wd, "مثال تخطيطي", True)
    svg += RC._title(Wd, rt("ووحدةٌ راحت كاملة"))
    svg += RC._why(Wd, H, 'ناقص ١R — والباقياتُ الثلاث خرجن بين الطرفين',
                   RED)
    svg += sm(Wd, H, "وهذي اللي تنساها بسرعة")
    return svg + "</svg>"


def m_sum(r=None, Wd=880, H=250):
    """٤ · المجموع بالـR."""
    svg, x, y, slot = _gm(Wd, H)
    for t in M_TR:
        svg += mark(x(t["i"]), slot, y(WM[t["i"]]["h"]), y(WM[t["i"]]["l"]),
                    TEAL if t["r"] > 0 else RED, 0.22)
    svg += badge(Wd, "مثال تخطيطي", True)
    svg += RC._title(Wd, rt("المجموع ‎+٢٫٨٦R"))
    svg += RC._why(Wd, H, 'اثنان زائد، ناقص واحد، وثلاثُ جزئيات — '
                          'والمحصّلة ‎+٢٫٨٦ مخاطرة', TEAL_D)
    svg += sm(Wd, H, "لين هني كل شي حلو — والغلط يبدأ بالسطر الجاي")
    return svg + "</svg>"


def m_grow(r=None, Wd=880, H=250):
    """٥ · الخلاصة: الـR تُضرب في نسبة المخاطرة لا تُقرأ نسبةَ حساب."""
    svg, x, y, slot = _gm(Wd, H)
    for t in M_TR:
        svg += mark(x(t["i"]), slot, y(WM[t["i"]]["h"]), y(WM[t["i"]]["l"]),
                    TEAL if t["r"] > 0 else RED, 0.18)
    svg += badge(Wd, "مثال تخطيطي", True)
    svg += RC._title(Wd, rt("بس حسابك زاد ‎١٫٤٣٪ لا ‎٢٫٨٦٪"))
    svg += RC._why(Wd, H, 'المخاطرة نصفُ بالمئة للصفقة: ‎٢٫٨٦ × ‎٠٫٥ = '
                          '‎١٫٤٣٪ — والـR وحدةُ مخاطرة لا وحدةُ حساب', TEAL_D)
    svg += sm(Wd, H, "اللي يخلط بينهن يحسب نفسه تضاعف وهو ما تحرّك")
    return svg + "</svg>"


# ═════════════════════════════════════════════════════════════════
# ٥ · «تصفية» — شرطُ الجوار يغيّر عددَ القمم (فنية · ريل · تخطيطي)
#     الموضوع ١٤٩
# ═════════════════════════════════════════════════════════════════
T_SEED = 1021
T_ANCH = [(0, 100.0), (10, 101.3), (20, 100.2), (30, 101.1), (39, 100.4)]
T_N = 40
WT = gen(T_ANCH, T_N, T_SEED, wick=0.6, bn=0.5)
RT_ = {"sym": "SCHEMATIC-T", "slug": "مثال تخطيطي — تصفية", "w": WT}
T_MED = st.median(c["h"] - c["l"] for c in WT)


def _tops(W, k):
    """قمّةٌ مؤهَّلة بشرط جوار: أعلى من `k` شمعات على كلِّ جانب."""
    return [i for i in range(k, len(W) - k)
            if all(W[i]["h"] > W[j]["h"] for j in range(i - k, i + k + 1) if j != i)]


def _swept(W, idxs):
    """القمم التي تجاوزها السعرُ لاحقاً داخل النافذة."""
    return [i for i in idxs if any(W[j]["h"] > W[i]["h"] for j in range(i + 1, len(W)))]


T_K = (1, 2, 5)
T_SETS_ = {k: _tops(WT, k) for k in T_K}
T_SW = {k: _swept(WT, T_SETS_[k]) for k in T_K}
T_TOP2 = sorted(T_SETS_[5], key=lambda i: -WT[i]["h"])[:2]
T_DIST = abs(WT[T_TOP2[0]]["h"] - WT[T_TOP2[1]]["h"]) / T_MED

_real(WT, T_N)
T_RATE = {k: len(T_SW[k]) / len(T_SETS_[k]) for k in T_K}

assert [len(T_SETS_[k]) for k in T_K] == [14, 7, 3], [len(T_SETS_[k]) for k in T_K]
assert [len(T_SW[k]) for k in T_K] == [9, 3, 0], [len(T_SW[k]) for k in T_K]
assert len(T_SETS_[1]) > len(T_SETS_[2]) > len(T_SETS_[5]), "الشرطُ لا يصفّي"
# الدرسُ كلُّه في اطّراد النسبة: كلّما شُدّ الشرطُ قلّت القممُ المسحوبة.
# ولو لم تطّرد لما جاز أن يُقال «الرخيصة تنكسر» — فتُقاس لا تُفترض.
assert T_RATE[1] > T_RATE[2] > T_RATE[5], T_RATE
assert T_DIST >= 1.0, T_DIST


def _gt(Wd, H):
    return frame(WT, Wd, H, pad=0.10, pb=66)


def _tpanel(k, Wd, H, title, why, col, note, only=None):
    svg, x, y, slot = _gt(Wd, H)
    for i in (only if only is not None else T_SETS_[k]):
        svg += mark(x(i), slot, y(WT[i]["h"]), y(WT[i]["l"]), col, 0.20)
        svg += dot(x(i), y(WT[i]["h"]) - 12, col, 4.0)
    svg += badge(Wd, "مثال تخطيطي", True)
    svg += RC._title(Wd, rt(title))
    svg += RC._why(Wd, H, why, col)
    svg += sm(Wd, H, note)
    return svg + "</svg>"


def t_one(r=None, Wd=880, H=250):
    """١ · شرطُ شمعةٍ واحدة: أربعَ عشرة قمّة."""
    return _tpanel(1, Wd, H, "بشرط شمعة وحدة: أربعَ عشرة قمّة",
                   f'كلُّ شمعةٍ أعلى من جارتيها تصير قمّة — '
                   f'{ar(len(T_SETS_[1]))} من {ar(T_N)} شمعة', INK,
                   "وهذي اللي ترسمها لمّا تفتح الشارت بسرعة")


def t_two(r=None, Wd=880, H=250):
    """٢ · شرطُ شمعتين: سبع."""
    return _tpanel(2, Wd, H, "وبشرط شمعتين: سبع",
                   f'شدّيت الشرط شمعةً وحدة فنزل العدد من '
                   f'{ar(len(T_SETS_[1]))} إلى {ar(len(T_SETS_[2]))}', TEAL_D,
                   "نص القمم راحت، والسوق ما تغيّر")


def t_five(r=None, Wd=880, H=250):
    """٣ · شرطُ خمس: ثلاث."""
    return _tpanel(5, Wd, H, "وبشرط خمس: ثلاث بس",
                   f'{ar(len(T_SETS_[5]))} قمم من {ar(T_N)} شمعة — '
                   f'وهذي اللي يشوفها السوق فعلاً', TEAL,
                   "ثلاثة مستويات تنقرأ، مو أربعَ عشرة")


def t_swept(r=None, Wd=880, H=250):
    """٤ · كم قمّةٍ من كلِّ مجموعةٍ سُحبت لاحقاً."""
    svg, x, y, slot = _gt(Wd, H)
    for i in T_SETS_[1]:
        svg += mark(x(i), slot, y(WT[i]["h"]), y(WT[i]["l"]),
                    RED if i in T_SW[1] else INK, 0.16)
    for i in T_SETS_[5]:
        svg += mark(x(i), slot, y(WT[i]["h"]), y(WT[i]["l"]),
                    RED if i in T_SW[5] else TEAL, 0.26)
    svg += badge(Wd, "مثال تخطيطي", True)
    svg += RC._title(Wd, rt("وكل ما رخّصت الشرط، زادت اللي تنسحب"))
    svg += RC._why(Wd, H, f'{ar(len(T_SW[1]))} من {ar(len(T_SETS_[1]))} سُحبن '
                          f'بشرط الشمعة، و{ar(len(T_SW[2]))} من {ar(len(T_SETS_[2]))} '
                          f'بشرط الشمعتين، و{ar(len(T_SW[5]))} من {ar(len(T_SETS_[5]))} '
                          f'بشرط الخمس', RED)
    svg += sm(Wd, H, "القمّة الرخيصة تنكسر بسرعة — لأنها مو قمّة أصلاً")
    return svg + "</svg>"


def t_all(r=None, Wd=880, H=250):
    """٥ · الخلاصة: مستويان يفصلهما مدىً حقيقي."""
    svg, x, y, slot = _gt(Wd, H)
    for i in T_TOP2:
        svg += hl(x(0) - slot * .5, x(T_N - 1) + slot * .5, y(WT[i]["h"]), INK, 1.7)
        svg += mark(x(i), slot, y(WT[i]["h"]), y(WT[i]["l"]), TEAL, 0.24)
    svg += vspan(x(max(T_TOP2)) + slot * 2.4, y(WT[T_TOP2[0]]["h"]),
                 y(WT[T_TOP2[1]]["h"]), rt(f'{xr(T_DIST)} وسيط المدى'), TEAL_D, 16, H)
    svg += badge(Wd, "مثال تخطيطي", True)
    svg += RC._title(Wd, rt("مستويان يفصلهما مدىً تقدر تشتغل فيه"))
    svg += RC._why(Wd, H, f'أعلى قمّتين بشرط الخمس بينهما '
                          f'{xr(T_DIST)} وسيطَ المدى — مسافةٌ تتّسع لهدف', TEAL_D)
    svg += sm(Wd, H, "صفّي قممك، بيبقى لك اللي يسوى")
    return svg + "</svg>"


SETS = {"muhla": [h_sweep, h_fast, h_slow, h_spread, h_all],
        "dajij": [g_draw, g_quiet, g_moved, g_ratio, g_all],
        "farz":  [f_keep1, f_keep2, f_slow, f_slow2, f_deaf],
        "numuw": [m_five, m_best, m_worst, m_sum, m_grow],
        "tasfia": [t_one, t_two, t_five, t_swept, t_all]}
SYN = {"dajij": (G_SEED, G_ANCH), "numuw": (M_SEED, M_ANCH),
       "farz": (tuple(F_SEEDS), F_ANCH), "tasfia": (T_SEED, T_ANCH)}
REAL = {"muhla": H_WIN}


WINS = {"muhla": RH, "tasfia": RT_, "dajij": RG, "farz": F_WIN, "numuw": RM}


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
    print(f'مهلة · {RH["slug"]} · {H_N} شمعة  [سوقٌ حقيقي]')
    print(f'  {len(H_EV)} أحداثِ سحبٍ، كلُّها حُسمت داخل النافذة')
    print(f'  الفجوات {H_GAPS} — الوسيط {H_MEDGAP}')
    print(f'  {len(H_ONE)} بشمعةٍ واحدة · {len(H_LONG)} بأربعٍ فأكثر '
          f'(أطولها {H_SLOW["gap"]})')
    print(f'  أقصى تحرّكٍ ضدّ الفكرة في المهلة {H_MAXADV:.2f}× وسيط المدى')

    print(f'\nتصفية · {T_N} شمعة  [تخطيطي]')
    print(f'  القمم بشرط ١ و٢ و٥: {[len(T_SETS_[k]) for k in T_K]}')
    print(f'  المسحوبة منها: {[len(T_SW[k]) for k in T_K]} '
          f'= {[f"{T_RATE[k]:.0%}" for k in T_K]}')
    print(f'  بين أعلى قمّتين {T_DIST:.2f}× وسيط المدى')

    print(f'\nضجيج · {G_N} شمعة  [تخطيطي]')
    print(f'  {len(G_QUIET)} هادئة من {G_TOT} = {G_SHARE:.0%} · '
          f'{len(G_MOVED)} أغلقتا خارج الحدّين')

    print(f'\nفرز · خمس أدوات × {F_N} شمعة  [تخطيطي]')
    for i, m in enumerate(F_M):
        tag = "تُبقى" if i in F_KEEP else "تُشطب"
        print(f'  {F_NAMES[i]}: خطوات {m["steps"]:.2f} · لمسات {m["touch"]} → {tag}')

    print(f'\nنمو · {M_N} شمعة  [تخطيطي]')
    print(f'  النتائج {[t["r"] for t in M_TR]} — المجموع {M_SUM:+.2f}R')
    print(f'  بمخاطرة {M_RISK}٪ للصفقة: نموُّ الحساب {M_GROW:+.2f}٪')
