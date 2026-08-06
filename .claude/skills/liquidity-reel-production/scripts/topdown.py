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

# منزلة العرض للأداة الجارية. `build` يضبطها من دقّة الشموع نفسها قبل أن
# تُصاغ أي طبقة، فلا تُطبع أسعار النحاس والغاز منزلتين فتتساوى ظاهرياً.
DP = 2


def load_dict(d):
    """يحوّل نافذةً خاماً إلى الشكل الذي تقرأه الطبقات — من الذاكرة لا القرص.

    الباك تست يفحص آلاف النوافذ فلا يكتبها كلها ملفات."""
    out = {"sym": d["sym"], "anchor_utc": d["anchor_utc"], "src": d["src"]}
    for tf in ("1D", "4H", "1h", "5m"):
        out[tf] = dict(anchor=d[tf]["anchor"],
                       w=[dict(d=r[0], o=r[1], h=r[2], l=r[3], c=r[4])
                          for r in d[tf]["rows"]])
    return out


def load(name=FILE):
    return load_dict(json.load(
        open(os.path.join(HERE, "raw_windows", name), encoding="utf-8")))


def rng_to(w, i):
    """مدى الشموع حتى الشمعة i — ما كان معلوماً لحظة الدخول لا بعده.

    كان المدى يُحسب على النافذة كلها، وفيها تسع عشرة شمعة **بعد** الدخول.
    فيها يدخل السعر الذي لم يقع بعد في تحديد عتبة تساوي القيعان وفي مسافة
    الوقف. الفرق صغير (وقف الذهب 4,116.90 مقابل 4,116.96) لكنه يُبطل أي
    باك تست: صفقةٌ وقفُها مشتقٌّ من المستقبل ليست صفقة يمكن تنفيذها."""
    seg = w[:i + 1]
    return max(c["h"] for c in seg) - min(c["l"] for c in seg)


def swing_lows(w, k=2):
    """قيعان تأرجح: أدنى من k شمعات على كل جانب."""
    return [j for j in range(k, len(w) - k)
            if all(w[j]["l"] <= w[j + s]["l"] for s in range(-k, k + 1) if s)]


# ═══════ ١ — الاتجاه العام (٤ ساعات) ═══════
def htf_trend(D, k=3):
    """اتجاه صاعد على الأربع ساعات: السعر فوق متوسط عشرين شمعة.

    🔒 أمر فهد 2026-08-06: «الغِ إغلاقات الأربع ساعات». كان الشرط ثلاث
       إغلاقات متتالية صاعدة، وهو أضيق ما في النموذج: ردّ ١١٣ من ١٤٤
       مرشّحاً. ثلاث إغلاقات صاعدة تصف اندفاعةً قصيرة لا اتجاهاً، وكثيراً
       ما تكتمل عند قمّة الحركة لا في بدايتها. بقي المتوسط وحده: موقع
       السعر منه يصف الاتجاه دون أن يشترط تسلسلاً بعينه.

    جُرِّبت قبله «قيعان تأرجح صاعدة» فرفضها الفحص: آخر قاعين 4,076.40 ثم
    4,074.00 — هابطان."""
    w = D["4H"]["w"]; a = D["4H"]["anchor"]
    seg = w[:a + 1]                               # شموع مغلقة فقط
    ma = sum(c["c"] for c in seg[-20:]) / min(20, len(seg))
    px = seg[-1]["c"]
    assert px > ma, f"الإغلاق تحت المتوسط: {px} ≤ {ma:.2f}"
    gap = (px - ma) / ma
    return dict(tf="4H", title="اتجاه صاعد على الأربع ساعات",
                detail=f"السعر {px:,.{DP}f} فوق متوسط ٢٠ ({ma:,.{DP}f}) "
                       f"بفارق {gap*100:.2f}٪",
                # يُخزَّن المتوسط بدقّته كاملة: تقريبه إلى منزلتين هنا كان
                # يجعل اللوحة تقول 58.010 والكابشن 58.005 عن الرقم نفسه.
                closes=[c["c"] for c in seg[-k:]], ma=ma,
                gap=gap, px=px, n=len(seg))


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
                detail=f"السعر فوق منتصف مدى الأمس ({mid:,.{DP}f}) وقاعُه "
                       f"{pdl:,.{DP}f} لم يُلمس",
                pdh=pdh, pdl=pdl, mid=mid)


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
                detail=f"قمة {seg[hi]['h']:,.{DP}f} ثم قاعٌ أعلى {seg[lo]['l']:,.{DP}f} "
                       f"فوق {prev_lo:,.{DP}f}",
                hi=off + hi, lo=off + lo, prev_lo=prev_lo)


# ═══════ ٤ — سحب السيولة (٥ دقائق) ═══════
def sweep(D, tol=None):
    """قيعان متساوية تُكنس ثم يُغلق فوقها.

    التساوي يُقاس **نسبةً من مدى النافذة** لا بفرق ثابت. كان الفرق ثابتاً
    (0.35) فصار المعيار يتمدّد أو ينكمش بحسب سعر الأداة: على الذهب يساوي
    ١٫٤٪ من المدى، وعلى النفط ١٥٪ — أي أن قيعاناً متباعدة تُعدّ «متساوية».
    وهذا ما أفسد ريل النفط ٢٠٢٦-٠٧-٢٣: قال «٦ قيعان عند 91.55» وفيها قاع
    يبعد 0.27 (١١٪ من المدى). المتساوي فعلاً اثنان.
    """
    w = D["5m"]["w"]; a = D["5m"]["anchor"]
    tol_of = lambda i: rng_to(w, i) * 0.015 if tol is None else tol
    # يُبحث عن شمعة الكنس نفسها ثم يُشتقّ المستوى من قيعان ما قبلها —
    # لا العكس. البحث من المستوى أولاً يفوّت الحالة التي يكون فيها
    # المستوى أقدم من نافذة البحث.
    for sw in range(a, max(0, a - 8), -1):
        lb = list(range(max(0, sw - 16), sw))
        if len(lb) < 6:
            continue
        R = rng_to(w, sw)
        base = min(w[j]["l"] for j in lb)
        if not (w[sw]["l"] < base - R * 0.001):
            continue
        if w[sw]["c"] <= base:
            continue
        eq = [j for j in lb if abs(w[j]["l"] - base) <= tol_of(sw)]
        if len(eq) < 2:
            continue
        return dict(tf="5m", title="سحب سيولة",
                    detail=f"{len(eq)} قيعان عند {base:,.{DP}f} كُنست إلى "
                           f"{w[sw]['l']:,.{DP}f} ثم إغلاق {w[sw]['c']:,.{DP}f} فوقها",
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


def quote_dp(w):
    """دقّة التسعير كما تظهر في الشموع نفسها، لا رقماً مفروضاً.

    كان التقريب مثبَّتاً على منزلتين — يصحّ على الذهب (4,121.20) والنفط
    (91.57)، ويُتلف النحاس: وقفٌ عند 6.3742 يصير 6.37، فتقفز المخاطرة من
    0.0042 إلى 0.01 ويصبح الهدف المعروض سعراً لم يُحسب. المنزلة تُقرأ من
    الأرقام المعروضة فتوافق كل أداة."""
    dp = 0
    for c in w:
        for k in ("o", "h", "l", "c"):
            s = repr(float(c[k]))
            if "." in s and "e" not in s:
                dp = max(dp, len(s.split(".")[1].rstrip("0")))
    return min(max(dp, 2), 5)


def plan(D, S):
    """الدخول عند إغلاق شمعة الكنس، والوقف تحت أدنى نقطتها."""
    w = D["5m"]["w"]; sw = S["sw"]
    R = rng_to(w, sw)                     # بلا استشراف — انظر rng_to
    dp = quote_dp(w)
    ENT = w[sw]["c"]
    STP = round(w[sw]["l"] - R * 0.006, dp)
    TGT = round(ENT + (ENT - STP) * 2.0, dp)
    hit = None
    for j in range(sw + 1, len(w)):
        if w[j]["l"] < STP:
            break
        if w[j]["h"] >= TGT:
            hit = j; break
    assert hit is not None, "الصفقة لم تبلغ ٢R قبل الوقف"
    return dict(fill=sw, ENT=ENT, STP=STP, TGT=TGT, hit=hit,
                R=round(ENT - STP, dp), dp=dp)


def build(name=None):
    global DP
    D = load(name or os.environ.get("LS_SET", FILE))
    DP = quote_dp(D["5m"]["w"])
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
    print(f'\n  ← الدخول {P["ENT"]:,.{DP}f} · الوقف {P["STP"]:,.{DP}f} · هدف ٢R '
          f'{P["TGT"]:,.{DP}f} · مخاطرة {P["R"]:,.{DP}f} · تحقق بعد '
          f'{P["hit"] - P["fill"]} شمعات')
