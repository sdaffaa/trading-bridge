# -*- coding: utf-8 -*-
"""جارتات تشغيلة ٣١ — نوافذ حقيقية من `sheet_candidates.json` لا رسوم مولّدة.

كل وحدة تأخذ **نافذة واحدة حقيقية**، وتُروى داخلها خمس حالات متمايزة (§12
يجيز مشاركة النافذة إذا تمايزت الحالات الخمس). كل مستوى مثبّت على OHLC
فعلي: الزون على فتيل الشمعة، الوقف على قاعها، والهدف على قمة وصلها السعر.

القاعدة التي تحكم الملف: **ما لا تُثبته الشموع لا يُرسم**. كل حالة تتحقق
من ادّعائها بـ`assert` قبل أن تُخرج SVG — «الوقف ضُرب» لا تُكتب إلا إذا
هبطت شمعة تحته فعلاً، و«الهدف تحقق» لا تُكتب إلا إذا بلغته قمة لاحقة.
الحالة التي لا تثبت تُسقط ويُعلَن ذلك، ولا تُجمَّل.
"""
import json, os

from reel_build import INK, TEAL, TEAL_D, RED, GREY, htext
from run15_charts import zbox, xm, tick, hl, badge, frame, head, note, foot
import chart_registry

HERE = os.path.dirname(os.path.abspath(__file__))
CAND = json.load(open(os.path.join(HERE, "sheet_candidates.json"), encoding="utf-8"))

AR_SYM = {"GC=F": "الذهب", "NQ=F": "الناسداك", "YM=F": "الداو جونز",
          "AUDUSD=X": "الأسترالي/الدولار", "GBPUSD=X": "الجنيه/الدولار",
          "EURUSD=X": "اليورو/الدولار", "USDJPY=X": "الدولار/ين"}
AR_TF = {"15m": "١٥ دقيقة", "30m": "٣٠ دقيقة", "1h": "ساعة"}
# وحدة النقطة لكل أداة (§4): فوركس 0.0001، ين 0.01، ذهب 0.1، مؤشرات 1.0
PIP = {"GC=F": 0.1, "NQ=F": 1.0, "YM=F": 1.0,
       "AUDUSD=X": 0.0001, "GBPUSD=X": 0.0001, "EURUSD=X": 0.0001}


def win(idx):
    """نافذة مرشّحة بفهرسها، مع شريحة التعريف بالعربي.

    المدخل الموسوم بـ`bad` (من `fix_candidates.py`) يُرفض هنا لا يُصمت
    عنه: فهارسه خارج مصفوفة الشموع، فأي رسم عليه يكذب."""
    r = CAND[idx]
    if r.get("bad"):
        raise ValueError(f'النافذة {idx} فاسدة: {" · ".join(r["bad"])}')
    r = dict(r)
    r["slug"] = f'{AR_SYM.get(r["sym"], r["sym"])} · {AR_TF.get(r["tf"], r["tf"])} · {r["date"]}'
    return r


def claim_fresh(r, label):
    w = r["w"]
    chart_registry.assert_fresh_real(r["sym"], r["tf"],
                                     f'{r["date"]} {w[0]["d"]}',
                                     f'{r["date"]} {w[-1]["d"]}', label=label)


def register(video, r, label):
    w = r["w"]
    chart_registry.register_real(video, r["sym"], r["tf"],
                                 f'{r["date"]} {w[0]["d"]}',
                                 f'{r["date"]} {w[-1]["d"]}', label=label)


# ═══════════ أدوات القياس على الشموع الحقيقية ═══════════
def hit_below(W, i0, lvl, i1=None):
    """أول شمعة بعد i0 هبط قاعها تحت المستوى — أو None."""
    for j in range(i0 + 1, i1 or len(W)):
        if W[j]["l"] <= lvl:
            return j
    return None


def hit_above(W, i0, lvl, i1=None):
    for j in range(i0 + 1, i1 or len(W)):
        if W[j]["h"] >= lvl:
            return j
    return None


def pips(r, a, b):
    return int(round(abs(a - b) / PIP.get(r["sym"], 1.0)))


def _geo(W, Wd, H):
    return frame(W, Wd, H)


# `head`/`note`/`foot` في run15_charts مضبوطة على عرض ٨٨٠ وترسو على طرفٍ
# واحد: عند ١٠٠٠ يخرج العنوان من حافة اللوحة، ويجلس السطران السفليان على
# السطر نفسه فيتراكبان. هنا تُوسَّط الثلاثة وتُفصل رأسياً.
def _mini():
    """وضع الغلاف: الجارت مصغّر تحت عنوان كبير، فأي نص عليه يصير حشواً."""
    import run15_charts as R15
    return R15.MINIMAL


def _title(Wd, txt, col=INK, fs=19):
    if _mini(): return ""
    # في الجارت البطل تتسع الشارة اليسرى فيدوس عليها العنوان الموسَّط —
    # يُنزَّل سطراً كاملاً تحتها كما يفعل `head` في run15_charts.
    y = round(34 * _SC[0]) if _SC[0] <= 1.15 else round(20 + 60 * _SC[0])
    return htext(Wd / 2, y, txt, col, round(fs * _SC[0]))


def _why(Wd, H, txt, col=INK, fs=17):
    if _mini(): return ""
    return htext(Wd / 2, H - round(40 * _SC[0]), txt, col, round(fs * _SC[0]))


def _sum(Wd, H, txt, col=INK, fs=18):
    if _mini(): return ""
    return htext(Wd / 2, H - round(13 * _SC[0]), txt, col, round(fs * _SC[0]))


_SC = [1.0]


def set_scale(k):
    """يتبع مقياس وسوم run15_charts كي تكبر النصوص مع الجارت البطل."""
    import run15_charts as R15
    R15.set_scale(k); _SC[0] = k


# ═══════════ الحالات الخمس ═══════════
def c_correct(r, Wd=880, H=250):
    """١ · الدخول الصحيح: الزون على الشمعة الأصل، والدخول عند العودة إليه."""
    W = r["w"]; iob, ir = r["iob"], r["ir"]
    zt, zb = W[iob]["o"], W[iob]["l"]
    tgt_i = max(range(ir, len(W)), key=lambda j: W[j]["h"])
    assert W[tgt_i]["h"] > zt, "السعر لم يتجاوز الزون بعد العودة"
    svg, x, y, slot = _geo(W, Wd, H)
    svg += zbox(x(iob) - slot * .6, y(zt), x(min(ir + 3, len(W) - 1)) + slot * .5, y(zb),
                "منطقة الطلب")
    svg += f'<circle cx="{x(ir):.1f}" cy="{y(W[ir]["l"]):.1f}" r="12" fill="none" ' \
           f'stroke="{TEAL_D}" stroke-width="3"/>'
    svg += hl(x(ir) - slot * .6, x(tgt_i) + slot * .5, y(W[tgt_i]["h"]), TEAL_D, 1.8, "7 6")
    svg += tick(x(tgt_i), y(W[tgt_i]["h"]) - 18)
    svg += _title(Wd, "الدخول من حافة المنطقة لا من وسط الحركة")
    svg += _why(Wd, H, "هني الدخلة الصح — لأن السعر رجع للمنطقة نفسها", TEAL_D)
    svg += _sum(Wd, H, f'من العودة إلى القمة: {pips(r, W[tgt_i]["h"], W[ir]["l"])} نقطة')
    return svg + badge(Wd, "الحالة الصحيحة", True) + "</svg>"


def c_trap(r, Wd=880, H=250):
    """٢ · الفخ: دخول مبكر فوق المنطقة قبل أن يعود السعر إليها."""
    W = r["w"]; iob, ir = r["iob"], r["ir"]
    zt = W[iob]["o"]
    ne = max(iob + 1, min(ir - 3, len(W) - 2))
    ent = W[ne]["c"]
    assert ent > zt, "الدخول المبكر ليس فوق المنطقة"
    low_i = min(range(ne + 1, ir + 1), key=lambda j: W[j]["l"])
    assert W[low_i]["l"] < ent, "السعر لم يهبط تحت الدخول المبكر"
    svg, x, y, slot = _geo(W, Wd, H)
    svg += zbox(x(iob) - slot * .6, y(zt), x(min(ir + 3, len(W) - 1)) + slot * .5,
                y(W[iob]["l"]), "المنطقة الحقيقية")
    svg += f'<circle cx="{x(ne):.1f}" cy="{y(ent):.1f}" r="12" fill="none" ' \
           f'stroke="{RED}" stroke-width="3"/>'
    svg += hl(x(ne) - slot * .6, x(low_i) + slot * .5, y(ent), RED, 1.8, "8 7")
    svg += xm(x(low_i), y(W[low_i]["l"]))
    svg += _title(Wd, "الدخول قبل العودة يترك مسافة كاملة تحت السعر")
    svg += _why(Wd, H, "هني أغروك تدخل", RED)
    svg += _sum(Wd, H, f'نزل بعدها {pips(r, ent, W[low_i]["l"])} نقطة قبل أن يرتد')
    return svg + badge(Wd, "الفخ — دخول مبكر", False) + "</svg>"


def c_stop(r, Wd=880, H=250):
    """٣ · الوقف: وقف داخل المنطقة يُضرب، ووقف تحتها ينجو — الفرق مقيس."""
    W = r["w"]; iob, ir = r["iob"], r["ir"]
    zt, zb = W[iob]["o"], W[iob]["l"]
    mid = (zt + zb) / 2
    hitm = hit_below(W, iob, mid)
    assert hitm is not None, "لا شمعة تخترق منتصف المنطقة"
    rng = max(c["h"] for c in W) - min(c["l"] for c in W)
    safe = zb - rng * 0.015
    assert hit_below(W, iob, safe) is None, "الوقف تحت المنطقة ضُرب أيضاً — الحالة لا تثبت"
    svg, x, y, slot = _geo(W, Wd, H)
    svg += zbox(x(iob) - slot * .6, y(zt), x(min(ir + 3, len(W) - 1)) + slot * .5, y(zb))
    svg += hl(x(iob) - slot * .6, x(len(W) - 1), y(mid), RED, 1.8, "8 7")
    svg += xm(x(hitm), y(mid))
    svg += hl(x(iob) - slot * .6, x(len(W) - 1), y(safe), TEAL_D, 1.8, "7 6")
    svg += _title(Wd, "الوقف تحت المنطقة لا في وسطها")
    svg += _why(Wd, H, "وقف الوسط انضرب", RED)
    svg += _sum(Wd, H, f'الفرق بين الوقفين {pips(r, mid, safe)} نقطة — ونجا الثاني')
    return svg + badge(Wd, "مكان الوقف", False) + "</svg>"


def c_retest(r, Wd=880, H=250):
    """٤ · إعادة الاختبار: لمسة ثانية للمنطقة نفسها بعد الارتداد الأول."""
    W = r["w"]; iob, ir = r["iob"], r["ir"]
    zt = W[iob]["o"]
    second = hit_below(W, ir + 2, zt)
    assert second is not None, "لا لمسة ثانية للمنطقة داخل النافذة"
    after = max(range(second, len(W)), key=lambda j: W[j]["h"])
    svg, x, y, slot = _geo(W, Wd, H)
    svg += zbox(x(iob) - slot * .6, y(zt), x(len(W) - 1), y(W[iob]["l"]))
    svg += f'<circle cx="{x(ir):.1f}" cy="{y(W[ir]["l"]):.1f}" r="10" fill="none" ' \
           f'stroke="{GREY}" stroke-width="2.4"/>'
    svg += f'<circle cx="{x(second):.1f}" cy="{y(W[second]["l"]):.1f}" r="12" fill="none" ' \
           f'stroke="{TEAL_D}" stroke-width="3"/>'
    svg += _title(Wd, "اللمسة الثانية أوضح من الأولى")
    svg += _why(Wd, H, "هني الفرصة الثانية — لأن المنطقة صمدت مرتين", TEAL_D)
    svg += _sum(Wd, H, f'من اللمسة الثانية: {pips(r, W[after]["h"], W[second]["l"])} نقطة')
    return svg + badge(Wd, "إعادة اختبار", True) + "</svg>"


def c_miss(r, Wd=880, H=250):
    """٥ · الإفلات: انتظار تأكيد زائد يجعل الدخول بعد نصف الحركة."""
    W = r["w"]; ir = r["ir"]
    top_i = max(range(ir, len(W)), key=lambda j: W[j]["h"])
    late = min(top_i, ir + max(2, (top_i - ir) // 2))
    assert top_i > late, "لا مسافة بين الدخول المتأخر والقمة"
    svg, x, y, slot = _geo(W, Wd, H)
    svg += hl(x(ir) - slot * .6, x(top_i) + slot * .5, y(W[top_i]["h"]), INK, 1.8)
    svg += f'<circle cx="{x(ir):.1f}" cy="{y(W[ir]["l"]):.1f}" r="11" fill="none" ' \
           f'stroke="{TEAL_D}" stroke-width="2.6"/>'
    svg += f'<circle cx="{x(late):.1f}" cy="{y(W[late]["c"]):.1f}" r="12" fill="none" ' \
           f'stroke="{RED}" stroke-width="3"/>'
    svg += _title(Wd, "التأكيد الزائد يشتري نصف الحركة")
    svg += _why(Wd, H, "هني دخلت متأخر — لأنك انتظرت تأكيداً بعد التأكيد", RED)
    svg += _sum(Wd, H, f'ضاع {pips(r, W[late]["c"], W[ir]["l"])} نقطة من أصل '
                       f'{pips(r, W[top_i]["h"], W[ir]["l"])}')
    return svg + badge(Wd, "الإفلات — تأخر الدخول", False) + "</svg>"


def c_context(r, Wd=880, H=250):
    """٦ · السياق: كسر الهيكل الذي صنع المنطقة، والحركة التي تلته.

    تُستعمل عوضاً عن حالة سقطت — النافذة التي لا تحوي لمسة ثانية ما زالت
    تحوي قصّتها الأصلية كاملة."""
    W = r["w"]; iH, bk, iob = r["iH"], r["bk"], r["iob"]
    lv = W[iH]["h"]
    assert W[bk]["c"] > lv, "شمعة الكسر لم تغلق فوق القمة"
    top_i = max(range(bk, len(W)), key=lambda j: W[j]["h"])
    svg, x, y, slot = _geo(W, Wd, H)
    svg += hl(x(iH) - slot * .6, x(bk) + slot * .55, y(lv), INK, 2.0)
    svg += htext(x(iH) + slot * 1.6, y(lv) - 14, "كسر الهيكل", INK, 20)
    svg += zbox(x(iob) - slot * .6, y(W[iob]["o"]), x(bk) + slot * .5, y(W[iob]["l"]))
    svg += tick(x(top_i), y(W[top_i]["h"]) - 18)
    svg += _title(Wd, "المنطقة تولد من الشمعة التي سبقت الكسر")
    svg += _why(Wd, H, "هني سكّر فوق القمة — لأن الجسم أغلق لا الفتيل", INK)
    svg += _sum(Wd, H, f'الحركة بعد الكسر: {pips(r, W[top_i]["h"], W[iob]["l"])} نقطة')
    return svg + badge(Wd, "السياق — أصل المنطقة", True) + "</svg>"


def c_sweep(r, Wd=880, H=250):
    """٧ · سحب السيولة: قاعان متساويان يُخترقان ثم يُغلَق فوقهما.

    تعمل على نوافذ الصنف `sweep` وحدها لأنها تقرأ `ipdl`. كل ادّعاء
    مقيس: تساوي القاعين نسبةً إلى مدى النافذة، ووجود شمعة تهبط تحتهما،
    وإغلاقها فوقهما. ما لم يثبت أحدها تسقط الحالة."""
    W = r["w"]
    ip = r.get("ipdl")
    assert ip is not None, "النافذة ليست من صنف سحب السيولة"
    rng = max(c["h"] for c in W) - min(c["l"] for c in W)
    # القاع الثاني: أقرب قاع لاحق يساوي قاع `ipdl` ضمن ١٪ من مدى النافذة
    pair = [j for j in range(ip + 1, min(ip + 4, len(W)))
            if abs(W[j]["l"] - W[ip]["l"]) <= rng * 0.01]
    assert pair, "لا قاع ثانٍ يساوي قاع السيولة"
    i2 = pair[0]
    lvl = min(W[ip]["l"], W[i2]["l"])
    brk = [j for j in range(i2 + 1, len(W)) if W[j]["l"] < lvl]
    assert brk, "لا شمعة تهبط تحت القاعين"
    deep = min(brk, key=lambda j: W[j]["l"])
    # الاسترداد يُقاس من أعمق نزول لا من أول نزول: لو أُخذ الأول لظهر
    # الإغلاق فوق القاعين ثم نزول أعمق بعده — وهذا يكذّب صورة الشمعة.
    back = next((j for j in range(deep, len(W)) if W[j]["c"] > lvl), None)
    assert back is not None, "لا شمعة تغلق فوق القاعين بعد الهبوط تحتهما"
    top_i = max(range(back, len(W)), key=lambda j: W[j]["h"])
    assert W[top_i]["h"] > W[back]["c"], "لا حركة صاعدة بعد الإغلاق"
    svg, x, y, slot = _geo(W, Wd, H)
    svg += hl(x(ip) - slot * .6, x(min(top_i + 1, len(W) - 1)), y(lvl), INK, 2.0)
    for j in (ip, i2):
        svg += f'<circle cx="{x(j):.1f}" cy="{y(W[j]["l"]):.1f}" r="9" fill="none" ' \
               f'stroke="{GREY}" stroke-width="2.2"/>'
    # الوسم يُوسَّط بين القاعين لا يميل نحو شمعة السحب: عند مقاس الدليل
    # (٨٨٠) تضيق الخانة ولا يضيق النص، فأي ميل يلامس علامة السحب.
    svg += htext(x(ip) + slot * 0.5, y(lvl) + round(26 * _SC[0]),
                 "قاعان متساويان", INK, round(19 * _SC[0]))
    svg += xm(x(deep), y(W[deep]["l"]))
    svg += f'<circle cx="{x(back):.1f}" cy="{y(W[back]["c"]):.1f}" r="12" fill="none" ' \
           f'stroke="{TEAL_D}" stroke-width="3"/>'
    svg += tick(x(top_i), y(W[top_i]["h"]) - 18)
    svg += _title(Wd, "الإغلاق فوق القاع يُلغي الكسر الذي تحته")
    svg += _why(Wd, H, "هني أغروك تبيع — لأن الفتيل نزل والإغلاق رجع", TEAL_D)
    svg += _sum(Wd, H, f'سُحب {pips(r, lvl, W[deep]["l"])} نقطة تحت القاعين، '
                       f'ثم صعد {pips(r, W[top_i]["h"], W[back]["c"])} نقطة')
    return svg + badge(Wd, "سحب السيولة", True) + "</svg>"


CASES = [c_correct, c_trap, c_stop, c_retest, c_miss, c_context, c_sweep]


def unit_charts(idx):
    """الحالات الخمس على نافذة واحدة — ما لا يثبت يُستبعد ويُعلَن."""
    r = win(idx)
    ok, dropped = [], []
    for f in CASES:
        try:
            f(r, 880, 250)
            ok.append(f)
        except Exception as e:                 # نافذة تنتهي عند الحدث لا بعده
            dropped.append((f.__name__, str(e)[:46]))
    return r, ok, dropped


if __name__ == "__main__":
    for i in (0, 1, 3, 7, 9, 10, 12, 13, 2, 5, 6, 8):
        r, ok, dr = unit_charts(i)
        print(f'{i:>2} {r["slug"]:<34} صالح {len(ok)}/{len(CASES)}' +
              ("" if not dr else "  ساقط: " + ", ".join(n for n, _ in dr)))
