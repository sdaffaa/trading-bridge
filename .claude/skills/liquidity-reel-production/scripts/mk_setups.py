# -*- coding: utf-8 -*-
"""يبني real_setups.json من بيانات سوق حقيقية ويتحقق من كل شرط بالحساب.

القاعدة الحاكمة: لا رقم يُرسم على الشاشة ما لم تثبته الشموع.
  • المستوى والفجوة والمنطقة تُشتقّ من الشموع لا تُكتب بالنظر.
  • **الدخول يجب أن يُنفَّذ فعلاً**: لا بدّ من شمعة قاعها ≤ سعر الدخول.
    (كان هذا خطأً في أول نسخة: أداة الصفقة رسمت دخولاً لم يلمسه السعر.)
  • الصفقة تُحسم بأول ما يقع بعد التنفيذ: الوقف أو الهدف ٢R — لا شيء بعده.

المصدر: Yahoo Finance عبر صندوق رمل معزول. النوافذ محفوظة داخل المستودع
فالنتيجة قابلة لإعادة التوليد بلا شبكة.
"""
import json, os
import confluence

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "raw_windows")


def rng(w):
    return max(c["h"] for c in w) - min(c["l"] for c in w)


def resolve(w, fill, STP, TGT):
    """أول ما يقع بعد التنفيذ: الوقف أم الهدف؟ يعيد فهرس شمعة الهدف أو None."""
    for j in range(fill, len(w)):
        if w[j]["l"] < STP:
            return None
        if w[j]["h"] >= TGT:
            return j
    return None


def rows(name):
    d = json.load(open(os.path.join(RAW, name), encoding="utf-8"))
    return [dict(d=r[0][11:], o=r[1], h=r[2], l=r[3], c=r[4]) for r in d]


def build():
    out = []
    sw = json.load(open(os.path.join(HERE, "real_sweeps.json"), encoding="utf-8"))

    # ── ١) كنس وإغلاق · الذهب ١٥ دقيقة ──
    e = sw[0]; w = e["w"]; R = rng(w); i = 13
    LOW = min(w[k]["l"] for k in range(max(0, i - 10), i - 1))
    assert w[i]["l"] < LOW, "الشمعة لم تكنس القاع"
    assert w[i]["c"] > LOW, "الشمعة لم تُغلق فوق القاع"
    ENT, STP = w[i]["c"], round(w[i]["l"] - R * 0.006, 4)   # الدخول = إغلاق شمعة الكنس، فهو منفَّذ حتماً
    TGT = round(ENT + (ENT - STP) * 2.0, 4)
    assert resolve(w, i + 1, STP, TGT) is not None, "الصفقة لم تبلغ ٢R قبل الوقف"
    out.append(dict(key="sweep", sym="GC=F", tf="15m", dec=2, date=e["date"], w=w,
                    i=i, LOW=LOW, ENT=ENT, STP=STP, TGT=TGT,
                    fill=i, hit=resolve(w, i + 1, STP, TGT)))

    # ── ٢) منتصف الفجوة · الذهب ساعة ──
    e = sw[3]; w = e["w"]; R = rng(w); k, tap = 21, 24
    GL, GH = w[k - 1]["h"], w[k + 1]["l"]
    assert GL < GH, "لا فجوة: قمة السابقة فوق قاع اللاحقة"
    CE = (GL + GH) / 2
    assert not any(w[j]["l"] <= CE for j in range(k + 2, tap)), "المنتصف لُمس قبل الشمعة المرصودة"
    assert w[tap]["l"] <= CE, "الدخول عند المنتصف لم يُنفَّذ"
    ENT, STP = CE, round(GL - R * 0.006, 4)
    TGT = round(ENT + (ENT - STP) * 2.0, 4)
    hit = resolve(w, tap, STP, TGT)
    assert hit is not None, "الصفقة لم تبلغ ٢R قبل الوقف"
    out.append(dict(key="fvg", sym="GC=F", tf="1h", dec=2, date=e["date"], w=w,
                    k=k, tap=tap, GL=GL, GH=GH, ENT=ENT, STP=STP, TGT=TGT,
                    fill=tap, hit=hit))

    # ── ٣) كسر وعودة · الذهب ٥ دقائق ──
    # الدخول عند ارتداد المستوى المكسور نفسه لا عند منتصف المنطقة: منتصف
    # المنطقة نادراً ما يُلمس، فأمر عنده يبقى معلّقاً ولا يصير صفقة.
    W = rows("gc_5m_2026-08-03.json")
    a, b = 12, 61
    w = W[a:b]; R = rng(w)
    p, brk, org, fill = 23 - a, 33 - a, 29 - a, 44 - a
    LH = w[p]["h"]
    assert LH >= max(w[j]["h"] for j in range(max(0, p - 4), p + 5)), "ليست قمة تأرجح"
    assert all(min(w[j]["o"], w[j]["c"]) <= LH for j in range(p + 1, brk)), "أُغلق فوق القمة قبل شمعة الكسر"
    assert min(w[brk]["o"], w[brk]["c"]) > LH, "الكسر ليس بإغلاق"
    assert w[org]["c"] < w[org]["o"], "شمعة النشأة ليست هابطة"
    ZT, ZB = w[org]["h"], w[org]["l"]
    ENT = ZT
    assert all(w[j]["l"] > ENT for j in range(brk + 1, fill)), "لُمس المستوى قبل الشمعة المرصودة"
    assert w[fill]["l"] <= ENT, "الدخول لم يُنفَّذ"
    STP = round(ZB - R * 0.008, 4)
    TGT = round(ENT + (ENT - STP) * 2.0, 4)
    hit = resolve(w, fill, STP, TGT)
    assert hit is not None, "الصفقة لم تبلغ ٢R قبل الوقف"
    out.append(dict(key="bos", sym="GC=F", tf="5m", dec=2, date="2026-08-03", w=w,
                    p=p, brk=brk, org=org, ret=fill, LH=LH, ZT=ZT, ZB=ZB,
                    ENT=ENT, STP=STP, TGT=TGT, fill=fill, hit=hit))

    for s in out:
        s["conf"] = confluence.build(s)
        assert len(s["conf"]) >= 3, f'أسباب أقل من ثلاثة: {s["key"]}'
        U = s["ENT"] - s["STP"]; R = rng(s["w"])
        print(f'{s["key"]:<6} {s["sym"]} {s["tf"]:<4} {s["date"]} شموع={len(s["w"]):<3} '
              f'دخول={s["ENT"]:,.2f} وقف={s["STP"]:,.2f} هدف٢R={s["TGT"]:,.2f} | '
              f'مخاطرة={U:.2f} = {U / R * 100:.0f}٪ من مدى الشاشة | '
              f'تنفيذ عند الشمعة {s["fill"]} وهدف عند {s["hit"]} | أسباب {len(s["conf"])}')
    json.dump(out, open(os.path.join(HERE, "real_setups.json"), "w", encoding="utf-8"),
              ensure_ascii=False)
    print("كُتب real_setups.json — كل الشروط تحقّقت")


if __name__ == "__main__":
    build()
