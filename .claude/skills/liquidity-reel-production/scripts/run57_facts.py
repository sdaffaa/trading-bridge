# -*- coding: utf-8 -*-
"""تشغيلة ٥٧ — قياس نموذج VWAP على الذهب الآجل، وإعادة التحقّق محلياً.

**اختيار الطبقات** (وحدة المناهج، أمر فهد 2026-08-12):

    PRIMARY_TOPIC      = VWAP
    STRUCTURE_METHOD   = NONE
    CONTEXT_LAYER      = NONE
    CONFIRMATION_LAYER = VOLUME

طبقتان لا أكثر، وكلٌّ تجيب سؤالاً مختلفاً: الـVWAP يقول **وين القيمة**،
والحجم يقول **منو يدفع**. ولم تُضف SMC ولا ICT لأنهما يجيبان سؤالاً لا
يحتاجه هذا الدرس — والقاعدة: «إذا لم تضف الأداة معلومة جديدة، احذفها».

**المصدر** (وضع B — إعادة بناء من بيانات سوق حقيقية):

    الأداة    GC=F — عقد الذهب الآجل، بورصة COMEX (مجموعة CME)
    المزوّد   Yahoo Finance
    الفريم    ١٥ دقيقة
    المدى     2026-08-06 15:15 → 2026-08-10 14:00 (توقيت غرينتش)
    الجلسة    Globex — إعادة الضبط 23:00 UTC
    الحجم     حجم بورصة حقيقي للعقد الأمامي، لا Tick Volume

الجلب جرى في `sandbox_exec` (ياهو محجوب من بوابة الحاوية)، والنافذة نُقلت
مضغوطةً بحارس md5، ثم **أُعيد حساب كل رقم هنا من الشموع** — الـVWAP
والانحراف والباندات وجفاف الحجم — فلا رقم يُصدَّق لأنه جاء من الصندوق.

    python3 run57_facts.py
"""
import datetime as dt
import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
WIN = os.path.normpath(os.path.join(HERE, "..", "..", "..", "..",
                                    "content", "run57_gc_vwap.json"))

SESSION_RESET_H = 23        # Globex: اليوم يبدأ 23:00 UTC


def load():
    d = json.load(open(WIN, encoding="utf-8"))
    B = [dict(d=r[0], o=r[1], h=r[2], l=r[3], c=r[4], v=r[5]) for r in d["b"]]
    for b in B:
        assert b["l"] <= min(b["o"], b["c"]) and b["h"] >= max(b["o"], b["c"]), \
            f'{b["d"]}: تسلسل OHLC غير منطقي'
        assert b["h"] > b["l"] and b["v"] > 0, f'{b["d"]}: مدى أو حجم صفري'
    ds = [b["d"] for b in B]
    assert ds == sorted(ds) and len(ds) == len(set(ds)), "الزمن غير مرتّب أو مكرّر"
    # الفريم ١٥د: كل فجوة أكبر يجب أن تكون حدَّ جلسة أو عطلة، لا نقصاً
    return B, d


def sid(b):
    x = dt.datetime.strptime(b["d"], "%Y-%m-%d %H:%M")
    return (x - dt.timedelta(hours=SESSION_RESET_H)).date()


def vwap(B, idx):
    """VWAP الجلسة وانحرافه المرجّح بالحجم — محسوبان من الشمعة نفسها.

    السعر النموذجي (h+l+c)/3 هو التعريف القياسي على الشموع، والحساب
    تراكمي من أول شمعة في الجلسة. وهذا حسابٌ **مبني على الشموع**
    (bar-based) لا على التِك — ويُكتب على الشاشة كما يفرض البريف.
    """
    pv = vv = s2 = 0.0
    out = {}
    for i in idx:
        b = B[i]
        tp = (b["h"] + b["l"] + b["c"]) / 3
        pv += tp * b["v"]; vv += b["v"]; s2 += tp * tp * b["v"]
        m = pv / vv
        out[i] = (m, math.sqrt(max(0.0, s2 / vv - m * m)))
    return out


def facts():
    B, meta = load()
    S = {}
    for i, b in enumerate(B):
        S.setdefault(sid(b), []).append(i)

    i = meta["i"]                       # شمعة الامتداد
    key = sid(B[i])
    idx = S[key]
    W = vwap(B, idx)
    m, sd = W[i]
    z = (B[i]["c"] - m) / sd
    assert z >= 2.0, f"الامتداد {z:.2f} انحراف — دون العتبة"

    j = max([k for k in idx if i <= k <= i + 4], key=lambda k: B[k]["h"])
    peak = B[j]["h"]
    mj, sdj = W[j]
    ext_pts = peak - mj
    ext_z = ext_pts / sdj

    mv = sum(B[k]["v"] for k in idx) / len(idx)     # متوسط حجم الجلسة
    nx = [k for k in idx if j < k <= j + 3]
    assert len(nx) == 3, "لا ثلاث شمعات بعد الذروة داخل الجلسة"
    dry = sum(B[k]["v"] for k in nx) / 3 / mv
    assert dry <= 0.75, f"حجم الاستمرار {dry:.2f}× — لم يجفّ"
    rel_i = B[i]["v"] / mv

    rec = next((k for k in idx if k > j and B[k]["c"] <= W[k][0]), None)
    assert rec is not None, "لم يستعد الـVWAP داخل الجلسة"
    back = peak - B[rec]["c"]
    assert back > 0, "لم يعد السعر إلى الأسفل"

    # لا دخول ولا وقف ولا هدف: هذا درس قراءة لا صفقة. ما لا يُقاس لا يُكتب.
    return dict(B=B, meta=meta, idx=idx, W=W, i=i, j=j, rec=rec,
                sess=str(key), vwap_i=m, sd_i=sd, z=z, peak=peak,
                vwap_j=mj, sd_j=sdj, ext_pts=ext_pts, ext_z=ext_z,
                mv=mv, dry=dry, rel_i=rel_i, back=back, bars=rec - j,
                vwap_rec=W[rec][0], close_rec=B[rec]["c"],
                i0=max(0, idx[0] - 26), i1=min(len(B) - 1, rec + 10),
                s0=idx[0], s1=idx[-1])


if __name__ == "__main__":
    f = facts()
    B = f["B"]
    print(f'المصدر: {f["meta"]["src"]} · {f["meta"]["tf"]} · '
          f'إعادة ضبط الجلسة {f["meta"]["sess_reset"]}')
    print(f'النافذة: {B[f["i0"]]["d"]} → {B[f["i1"]]["d"]} '
          f'({f["i1"]-f["i0"]+1} شمعة) · الجلسة {f["sess"]} '
          f'({len(f["idx"])} شمعة)')
    print(f'الامتداد {B[f["i"]]["d"]}: إغلاق {B[f["i"]]["c"]:.1f} · '
          f'VWAP {f["vwap_i"]:.2f} · σ {f["sd_i"]:.2f} · z {f["z"]:.2f}')
    print(f'الذروة {B[f["j"]]["d"]}: {f["peak"]:.1f} — '
          f'{f["ext_pts"]:.1f} نقطة فوق الـVWAP ({f["ext_z"]:.2f}σ)')
    print(f'حجم الاستمرار (٣ شمعات بعد الذروة): {f["dry"]:.2f}× متوسط الجلسة '
          f'({f["mv"]:,.0f}) · وحجم شمعة الامتداد {f["rel_i"]:.2f}×')
    print(f'الاستعادة {B[f["rec"]]["d"]}: إغلاق {f["close_rec"]:.1f} ≤ '
          f'VWAP {f["vwap_rec"]:.2f} — رجع {f["back"]:.1f} نقطة في '
          f'{f["bars"]} شمعة')
