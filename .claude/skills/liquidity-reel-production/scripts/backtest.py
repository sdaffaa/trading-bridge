# -*- coding: utf-8 -*-
"""باك تست حقيقي للنموذج ذي الطبقات الخمس — يعدّ الخاسرة كما يعدّ الرابحة.

`scan_setups.py` يبحث عن صفقةٍ **تصلح للنشر**، فيشترط بلوغ ٢R قبل الوقف.
هذا الشرط صحيح للاختيار وكاذبٌ للإحصاء: لو حُسبت نسبة الربح من مخرجاته
لخرجت ١٠٠٪، وهي نسبة لا تصف السوق بل تصف المصفاة. لذلك يُلغى الشرط هنا:
كل إشارة تجتاز الطبقات الخمس تُسجَّل، ثم تُحلّ بما فعله السعر بعدها.

القواعد التي تجعل الرقم قابلاً للتصديق:
  ١) **لا استشراف**: كل طبقة ومسافة الوقف تُحسب من شموع أُغلقت عند الدخول
     أو قبله (انظر `topdown.rng_to`).
  ٢) **الشمعة الغامضة تُحسب خسارة**: إن لمست شمعةٌ واحدة الوقف والهدف معاً
     فلا نعرف أيهما أولاً من بيانات الخمس دقائق. تُعدّ خسارة. الافتراض
     المعاكس يشتري نسبة ربح من الجهل.
  ٣) **الصفقة التي لم تُحسم** خلال MAXBARS تُغلق على آخر إغلاق، بربحها أو
     خسارتها كما هي، لا تُحذف. حذفُها يخفي الصفقات الميتة.

الأرقام التي يُخرجها هي وحدها ما يجوز عرضه في لوحة الباك تست في الريل.
"""
import topdown

MAXBARS = 60            # خمس ساعات على فريم الخمس دقائق
TP_R = 2.0


def signals(m5, mk_window):
    """كل إشارة تجتاز الطبقات الخمس، بصرف النظر عن نتيجتها.

    `mk_window` دالّة تبني نافذة الفريمات الأربع حول شمعة الدخول — تأتي
    من `sandbox_scan.window` كي لا يُكتب بناء النافذة مرتين."""
    # `topdown.rng_to` يمسح من البداية في كل نداء، وهنا آلاف الشموع لكل
    # أداة — فيصير المسح تربيعياً. يُحسب المدى تراكمياً مرة واحدة، وقيمته
    # مطابقة تماماً لما تُرجعه الدالّة.
    hi = lo = None
    pre = []
    for c in m5:
        hi = c["h"] if hi is None else max(hi, c["h"])
        lo = c["l"] if lo is None else min(lo, c["l"])
        pre.append(hi - lo)
    out = []
    for sw in range(40, len(m5) - 1):
        R = pre[sw]
        if R <= 0:
            continue
        lb = m5[sw - 16:sw]
        base = min(c["l"] for c in lb)
        c0 = m5[sw]
        if not (c0["l"] < base - R * 0.001 and c0["c"] > base):
            continue
        if len([c for c in lb if abs(c["l"] - base) <= R * 0.015]) < 2:
            continue
        rg = c0["h"] - c0["l"]
        if not rg or (min(c0["o"], c0["c"]) - c0["l"]) / rg < 0.30:
            continue
        w = mk_window(sw)
        if not w:
            continue
        try:                       # الطبقات ١-٣ بكود `topdown` نفسه
            D = topdown.load_dict(w)
            S = topdown.sweep(D)
            topdown.htf_trend(D)
            topdown.daily_bias(D, S["sw"])
            topdown.mtf_structure(D)
            topdown.ltf_signal(D, S["sw"])
        except Exception:
            continue
        ent = c0["c"]
        stp = c0["l"] - R * 0.006
        if (ent - stp) <= 0 or (ent - stp) / ent < 0.0006:
            continue
        out.append(dict(i=sw, d=c0["d"], ent=ent, stp=stp,
                        tgt=ent + (ent - stp) * TP_R))
    return out


def resolve(m5, t):
    """ما فعله السعر بعد الدخول: هدف، وقف، أو إغلاق عند نفاد المهلة."""
    risk = t["ent"] - t["stp"]
    for j in range(t["i"] + 1, min(len(m5), t["i"] + 1 + MAXBARS)):
        c = m5[j]
        hit_s, hit_t = c["l"] <= t["stp"], c["h"] >= t["tgt"]
        if hit_s:                      # الغموض يُحسم ضدّ الصفقة — القاعدة ٢
            return dict(r=-1.0, bars=j - t["i"], how="وقف", amb=hit_t)
        if hit_t:
            return dict(r=TP_R, bars=j - t["i"], how="هدف", amb=False)
    j = min(len(m5) - 1, t["i"] + MAXBARS)
    return dict(r=(m5[j]["c"] - t["ent"]) / risk, bars=j - t["i"],
                how="مهلة", amb=False)


def stats(rows):
    n = len(rows)
    if not n:
        return dict(n=0)
    wins = [r for r in rows if r["r"] > 0]
    loss = [r for r in rows if r["r"] <= 0]
    gp = sum(r["r"] for r in wins)
    gl = -sum(r["r"] for r in loss)
    run = best = 0
    for r in rows:
        run = run + 1 if r["r"] <= 0 else 0
        best = max(best, run)
    return dict(n=n, wins=len(wins), loss=len(loss),
                to=len([r for r in rows if r["how"] == "مهلة"]),
                amb=len([r for r in rows if r.get("amb")]),
                wr=len(wins) / n, gp=gp, gl=gl,
                pf=(gp / gl if gl else float("inf")),
                exp=sum(r["r"] for r in rows) / n,
                net=sum(r["r"] for r in rows),
                maxdd=best, bars=sum(r["bars"] for r in rows) / n)


def report(s):
    if not s.get("n"):
        return "لا إشارات"
    pf = "∞" if s["pf"] == float("inf") else f'{s["pf"]:.2f}'
    return (f'صفقات {s["n"]} · رابحة {s["wins"]} · خاسرة {s["loss"]} '
            f'(منها {s["to"]} بالمهلة، {s["amb"]} غامضة حُسبت خسارة)\n'
            f'نسبة الربح {s["wr"]:.0%} · عامل الربح {pf} · التوقّع '
            f'{s["exp"]:+.2f}R · الصافي {s["net"]:+.1f}R\n'
            f'أطول سلسلة خسائر {s["maxdd"]} · متوسط عمر الصفقة '
            f'{s["bars"]:.0f} شمعة')
