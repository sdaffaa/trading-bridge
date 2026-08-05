# -*- coding: utf-8 -*-
"""تحليل هابط متعدد الفريمات — الدخول لعدة أسباب لا لسبب واحد.

🔒 أمر فهد 2026-08-05: الاتجاه العام ← انحياز اليوم ← هيكل استمراري على
   الفريم المتوسط ← سحب سيولة ← إشارة انعكاس على الفريم الصغير.

قاعدتان تحكمان كل طبقة:
  ١) **لا نظر إلى المستقبل**: كل طبقة تُحسب من شموع أُغلقت قبل شمعة الدخول.
     الشمعة الجارية وقت الدخول لا تُستعمل في أي مستوى.
  ２) **سلسلة واحدة**: الفريمات الأعلى مُجمَّعة من نفس بيانات الساعة والخمس
     دقائق. شموع Yahoo اليومية لعقود الذهب تستعمل تعريف جلسة مختلفاً —
     قالت إن قمة 08-03 هي 4,083.50 بينما بيانات الساعة تقول 4,134.70،
     فخلطُهما يبني تحليلاً على سلسلتين متناقضتين.

ما لا يتحقق شرطه يرفع خطأً بدل أن يُروى كأنه تحقّق.
"""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
FILE = "gc_td2_2026-08-04.json"


def load(name=FILE):
    d = json.load(open(os.path.join(HERE, "raw_windows", name), encoding="utf-8"))
    out = {"sym": d["sym"], "anchor_utc": d["anchor_utc"], "src": d["src"]}
    for tf in ("1D", "4H", "1h", "5m"):
        out[tf] = dict(anchor=d[tf]["anchor"],
                       w=[dict(d=r[0], o=r[1], h=r[2], l=r[3], c=r[4])
                          for r in d[tf]["rows"]])
    return out


def swing_lows(w, k=2):
    """قيعان تأرجح: أدنى من k شمعات على كل جانب."""
    return [j for j in range(k, len(w) - k)
            if all(w[j]["l"] <= w[j + s]["l"] for s in range(-k, k + 1) if s)]


# ═══════ ١ — الاتجاه العام (٤ ساعات) ═══════
def htf_trend(D, k=3):
    """زخم صاعد مقيس على الأربع ساعات: إغلاقات متتالية صاعدة فوق متوسط ٢٠.

    جُرِّبت «قيعان تأرجح صاعدة» فرفضها الفحص: آخر قاعين على الأربع ساعات
    4,076.40 ثم 4,074.00 — هابطان. السوق في تعافٍ من هبوط لا في اتجاه
    صاعد ناضج، فتُروى الطبقة كما هي: زخم، لا اتجاه."""
    w = D["4H"]["w"]; a = D["4H"]["anchor"]
    seg = w[:a + 1]                               # شموع مغلقة فقط
    cl = [c["c"] for c in seg[-k:]]
    assert all(cl[i] < cl[i + 1] for i in range(len(cl) - 1)), \
        f"الإغلاقات ليست صاعدة: {cl}"
    ma = sum(c["c"] for c in seg[-20:]) / min(20, len(seg))
    assert seg[-1]["c"] > ma, f"الإغلاق تحت المتوسط: {seg[-1]['c']} ≤ {ma:.2f}"
    return dict(tf="4H", title="زخم صاعد على الأربع ساعات",
                detail=f"{k} إغلاقات صاعدة: " + " ← ".join(f"{v:,.2f}" for v in cl)
                       + f"، فوق متوسط ٢٠ ({ma:,.2f})",
                closes=cl, ma=round(ma, 2), n=len(seg))


# ═══════ ٢ — انحياز اليوم (ICT) ═══════
def daily_bias(D, fill):
    """موقع السعر من مدى الأمس: النصف الأعلى بلا لمس قاع الأمس = انحياز صاعد."""
    dw = D["1D"]["w"]; pd = dw[D["1D"]["anchor"]]      # آخر يوم مكتمل
    pdh, pdl = pd["h"], pd["l"]
    mid = (pdh + pdl) / 2
    m5 = D["5m"]["w"]; a5 = fill          # حتى شمعة الدخول لا بعدها
    day = D["anchor_utc"][:10]            # يُقرأ من النافذة لا يُثبَّت
    today = [c for c in m5[:a5 + 1] if c["d"][:10] == day]
    assert today, "لا شموع لليوم الجاري"
    lo_today = min(c["l"] for c in today)
    px = m5[a5]["c"]
    assert lo_today > pdl, f"قاع الأمس لُمس: {lo_today} ≤ {pdl}"
    assert px > mid, f"السعر تحت منتصف مدى الأمس: {px} ≤ {mid:.2f}"
    return dict(tf="1D", title="انحياز اليوم صاعد",
                detail=f"السعر فوق منتصف مدى الأمس ({mid:,.2f}) وقاعُه "
                       f"{pdl:,.2f} لم يُلمس",
                pdh=pdh, pdl=pdl, mid=round(mid, 2))


# ═══════ ٣ — هيكل استمراري (ساعة) ═══════
def mtf_structure(D):
    """قمة ثم قاع أعلى على الساعة: استمرار الصعود لا انعكاسه."""
    w = D["1h"]["w"]; a = D["1h"]["anchor"]
    seg = w[max(0, a - 14):a + 1]; off = max(0, a - 14)   # الشمعة a مغلقة هنا
    hi = max(range(len(seg) - 1), key=lambda j: seg[j]["h"])
    after = seg[hi + 1:]
    assert after, "لا شموع بعد القمة"
    lo = hi + 1 + min(range(len(after)), key=lambda j: after[j]["l"])
    prev_lo = min(seg[j]["l"] for j in range(hi))
    assert seg[lo]["l"] > prev_lo, \
        f"القاع بعد القمة ليس أعلى: {seg[lo]['l']} ≤ {prev_lo}"
    return dict(tf="1h", title="هيكل استمراري",
                detail=f"قمة {seg[hi]['h']:,.2f} ثم قاعٌ أعلى {seg[lo]['l']:,.2f} "
                       f"فوق {prev_lo:,.2f}",
                hi=off + hi, lo=off + lo, prev_lo=prev_lo)


# ═══════ ٤ — سحب السيولة (٥ دقائق) ═══════
def sweep(D, tol=0.35):
    """قيعان متساوية تُكنس ثم يُغلق فوقها."""
    w = D["5m"]["w"]; a = D["5m"]["anchor"]
    # يُبحث عن شمعة الكنس نفسها ثم يُشتقّ المستوى من قيعان ما قبلها —
    # لا العكس. البحث من المستوى أولاً يفوّت الحالة التي يكون فيها
    # المستوى أقدم من نافذة البحث.
    for sw in range(a, max(0, a - 8), -1):
        lb = list(range(max(0, sw - 16), sw))
        if len(lb) < 6:
            continue
        base = min(w[j]["l"] for j in lb)
        if not (w[sw]["l"] < base - 0.05):
            continue
        if w[sw]["c"] <= base:
            continue
        eq = [j for j in lb if abs(w[j]["l"] - base) <= tol]
        if len(eq) < 2:
            continue
        return dict(tf="5m", title="سحب سيولة",
                    detail=f"{len(eq)} قيعان عند {base:,.2f} كُنست إلى "
                           f"{w[sw]['l']:,.2f} ثم إغلاق {w[sw]['c']:,.2f} فوقها",
                    lvl=base, eq=eq, sw=sw)
    raise AssertionError("لا قيعان متساوية مكنوسة قبل الدخول")


# ═══════ ٥ — إشارة الانعكاس (٥ دقائق) ═══════
def ltf_signal(D, sw):
    """ذيل رفض مقيس على شمعة الكنس نفسها."""
    w = D["5m"]["w"]; c = w[sw]
    rg = c["h"] - c["l"]
    assert rg > 0
    wick = (min(c["o"], c["c"]) - c["l"]) / rg
    assert wick >= 0.30, f"الذيل السفلي ضعيف: {wick:.0%}"
    return dict(tf="5m", title="إشارة انعكاس",
                detail=f"ذيل سفلي {wick:.0%} من مدى الشمعة — البائع فقد السيطرة",
                wick=wick)


def plan(D, S):
    """الدخول عند إغلاق شمعة الكنس، والوقف تحت أدنى نقطتها."""
    w = D["5m"]["w"]; sw = S["sw"]
    R = max(c["h"] for c in w) - min(c["l"] for c in w)
    ENT = w[sw]["c"]
    STP = round(w[sw]["l"] - R * 0.006, 2)
    TGT = round(ENT + (ENT - STP) * 2.0, 2)
    hit = None
    for j in range(sw + 1, len(w)):
        if w[j]["l"] < STP:
            break
        if w[j]["h"] >= TGT:
            hit = j; break
    assert hit is not None, "الصفقة لم تبلغ ٢R قبل الوقف"
    return dict(fill=sw, ENT=ENT, STP=STP, TGT=TGT, hit=hit, R=round(ENT - STP, 2))


def build(name=None):
    D = load(name or os.environ.get("LS_SET", FILE))
    L4 = sweep(D)
    L = [htf_trend(D), daily_bias(D, L4["sw"]), mtf_structure(D), L4,
         ltf_signal(D, L4["sw"])]
    return D, L, plan(D, L4)


if __name__ == "__main__":
    import sys
    D, L, P = build(sys.argv[1] if len(sys.argv) > 1 else None)
    print(f'{D["sym"]} · مرساة {D["anchor_utc"]}\n{D["src"]}\n')
    for n, x in enumerate(L, 1):
        print(f'  {n}) [{x["tf"]:>3}] {x["title"]:<18} {x["detail"]}')
    print(f'\n  ← الدخول {P["ENT"]:,.2f} · الوقف {P["STP"]:,.2f} · هدف ٢R '
          f'{P["TGT"]:,.2f} · مخاطرة {P["R"]:,.2f} · تحقق بعد '
          f'{P["hit"] - P["fill"]} شمعات')
