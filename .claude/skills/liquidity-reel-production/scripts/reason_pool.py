# -*- coding: utf-8 -*-
"""بنك أسباب الدخول — كل ريل ينطق بمجموعة مختلفة، وكلّها مقيسة.

🔒 أمر فهد 2026-08-07: «غيّر أسباب الدخول بالفيديو ولا تجعله متكرّراً بكل
فيديو». كانت الريلات كلها تنطق بالعناوين الخمسة نفسها بالترتيب نفسه، فصار
كل فيديو نسخةً من سابقه وإن اختلفت أرقامه.

**البوابة لم تتغيّر**: `topdown.build` يبقى شرط القبول — خمس طبقات كلها
واجبة، وما لا يجتازها لا يُبنى منه ريل. الذي تغيّر هو ما **يُروى**: لكل
طبقة هنا عدّة قراءات مقيسة على الشموع نفسها، فيُختار منها واحدة في كل
تشغيلة. القراءة التي لا تتحقّق على النافذة تُسقَط ولا تُذكر — فلا يُنطَق
إلا بما تثبته الشموع.

الاختيار ليس عشوائياً: يُفضَّل ما لم يُستعمل في الريلات السابقة (سجل
`used_reasons.json`)، ويُحسَم التعادل ببصمة النافذة كي يبقى البناء
معاداً للإنتاج — النافذة نفسها تعطي الرواية نفسها دائماً.
"""
import hashlib, json, os

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "used_reasons.json")


def _load():
    if os.path.exists(LOG):
        with open(LOG, encoding="utf-8") as f:
            return json.load(f)
    return {"_readme": "أي مفتاح سبب استُعمل في أي ريل — كي لا تتكرّر الرواية",
            "runs": []}


def used_counts():
    """كم مرّة نُطق بكل مفتاح سبب، وفي أي تشغيلة آخر مرّة.

    العدد وحده لا يكفي: حين تتساوى الأعداد يعود الاختيار إلى الترتيب
    الثابت فتتكرّر المجموعة نفسها على نافذتين متتاليتين. فيُضاف موضع آخر
    استعمال — والأقدم استعمالاً يتقدّم على الأحدث."""
    runs = _load()["runs"]
    c, last = {}, {}
    for i, r in enumerate(runs):
        for k in r.get("keys", []):
            c[k] = c.get(k, 0) + 1
            last[k] = i
    return c, last


def register(tag, keys):
    d = _load()
    d["runs"] = [r for r in d["runs"] if r.get("tag") != tag]
    d["runs"].append({"tag": tag, "keys": list(keys)})
    with open(LOG, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=1)


# ═══════════ السجلّ يقول ما نُشر لا ما بُني ═══════════
# كان البناء نفسه يسجّل، فكل تجربة — إعادة بناء لفحص إطار، أو تشغيل على
# نافذة لاختبار الكود — تُدخل تشغيلةً لم تُنشر وتزيح العدّاد. فيصير السجلّ
# يصف ما جرّبناه لا ما سمعه الناس، والدوران يبني على رقمٍ كاذب.
# فالبناء **يودِع** المفاتيح جانباً، و`scan_setups.py claim` — ولا يُنادى
# إلا على ريلٍ سُلّم — هو الذي يُدخلها السجلّ.
PEND = os.path.join(HERE, "reasons_pending")


def stage(tag, keys):
    os.makedirs(PEND, exist_ok=True)
    with open(os.path.join(PEND, tag + ".json"), "w", encoding="utf-8") as f:
        json.dump(list(keys), f, ensure_ascii=False)


def register_staged(tag):
    """يُدخل السجلَّ مفاتيحَ ريلٍ نُشر. يُرجع المفاتيح أو None إن لم تُودَع."""
    p = os.path.join(PEND, tag + ".json")
    if not os.path.exists(p):
        return None
    with open(p, encoding="utf-8") as f:
        keys = json.load(f)
    register(tag, keys)
    os.remove(p)
    return keys


# ═══════════ القراءات المقيسة ═══════════
# كل دالّة تُرجع (عنوان، تفصيل) أو None إن لم تتحقّق على هذه النافذة.
# الرقم في التفصيل يخرج من الشموع لا من التقدير.

def _slot_4h(D, LAY, PLAN, M5, DP):
    L = LAY[0]
    w = D["4H"]["w"][:D["4H"]["anchor"] + 1]
    out = {}
    out["ma_gap"] = ("اتجاه صاعد على الأربع ساعات", L["detail"])

    # إغلاقات متتالية فوق المتوسط: تُحسب على المتوسط المتحرّك نفسه لا على
    # متوسط اللحظة، وإلا قِيست شمعةٌ قديمة بمتوسطٍ لم يكن موجوداً بعد.
    run = 0
    for i in range(len(w) - 1, 18, -1):
        seg = w[:i + 1]
        ma = sum(c["c"] for c in seg[-20:]) / 20
        if seg[-1]["c"] > ma:
            run += 1
        else:
            break
    if run >= 3:
        out["ma_run"] = ("الاتجاه لم ينكسر على الأربع ساعات",
                         f'{run} شمعات متتالية أغلقت فوق متوسط ٢٠ ({L["ma"]:,.{DP}f})')

    # مدى الأربع ساعات الأخيرة مقابل مدى ما قبلها: توسّعٌ أم انكماش
    if len(w) >= 6:
        r1 = max(c["h"] for c in w[-3:]) - min(c["l"] for c in w[-3:])
        r0 = max(c["h"] for c in w[-6:-3]) - min(c["l"] for c in w[-6:-3])
        if r0 > 0 and r1 > r0 * 1.15:
            out["expand_4h"] = ("توسّع المدى على الأربع ساعات",
                                f'مدى آخر ٣ شمعات {r1:,.{DP}f} مقابل {r0:,.{DP}f} قبلها '
                                f'— اتساع {(r1/r0-1)*100:.0f}٪')
    return out


def _slot_1d(D, LAY, PLAN, M5, DP):
    L = LAY[1]
    out = {"pd_mid": ("انحياز اليوم صاعد", L["detail"])}

    day = D["anchor_utc"][:10]
    today = [c for c in M5[:PLAN["fill"] + 1] if c["d"][:10] == day]
    if today:
        lo = min(c["l"] for c in today)
        if lo > L["pdl"]:
            out["pd_low"] = ("قاع الأمس لم يُلمس اليوم",
                             f'أدنى ما بلغه اليوم {lo:,.{DP}f} فوق قاع الأمس '
                             f'{L["pdl"]:,.{DP}f} بفارق {lo - L["pdl"]:,.{DP}f}')
    rng = L["pdh"] - L["pdl"]
    px = M5[PLAN["fill"]]["c"]
    if rng > 0 and px < L["pdh"]:
        pos = (px - L["pdl"]) / rng
        out["pd_room"] = ("الدخول دون قمة الأمس",
                          f'السعر عند {pos*100:.0f}٪ من مدى الأمس — '
                          f'وقمّته {L["pdh"]:,.{DP}f} لم تُلمس بعد')
    return out


def _slot_1h(D, LAY, PLAN, M5, DP):
    L = LAY[2]
    w = D["1h"]["w"]
    out = {"struct": ("هيكل استمراري على الساعة", L["detail"])}

    hi = w[L["hi"]]["h"]
    if hi > PLAN["TGT"]:
        out["room"] = ("مساحة الهدف مفتوحة على الساعة",
                       f'قمة الساعة {hi:,.{DP}f} فوق الهدف {PLAN["TGT"]:,.{DP}f} — '
                       f'الطريق إليه بلا عائق قريب')
    lo = w[L["lo"]]["l"]
    if lo > L["prev_lo"]:
        out["hl"] = ("قاعٌ أعلى من سابقه على الساعة",
                     f'{lo:,.{DP}f} فوق {L["prev_lo"]:,.{DP}f} بفارق '
                     f'{lo - L["prev_lo"]:,.{DP}f} — البائع لم يستعد قاعه')
    return out


def _slot_sweep(D, LAY, PLAN, M5, DP):
    L = LAY[3]
    sw, lvl = L["sw"], L["lvl"]
    out = {"sweep": ("سحب السيولة", L["detail"])}

    depth = lvl - M5[sw]["l"]
    risk = PLAN["ENT"] - PLAN["STP"]
    if depth > 0 and risk > 0:
        out["depth"] = ("عمق السحب أصغر من المخاطرة",
                        f'نزل {depth:,.{DP}f} تحت المستوى، والمخاطرة '
                        f'{risk:,.{DP}f} — أي {depth/risk*100:.0f}٪ منها')
    if len(L["eq"]) >= 2:
        out["pool"] = ("سيولة مكدّسة تحت مستوى واحد",
                       f'{len(L["eq"])} قيعان عند {lvl:,.{DP}f} — كلما كثرت '
                       f'القيعان زادت الأوامر تحتها')
    return out


def _slot_signal(D, LAY, PLAN, M5, DP):
    L = LAY[4]
    sw = LAY[3]["sw"]
    c = M5[sw]
    rg = c["h"] - c["l"]
    out = {"wick": ("إشارة الانعكاس", L["detail"])}

    if rg > 0:
        pos = (c["c"] - c["l"]) / rg
        if pos >= 0.6:
            out["close_top"] = ("الإغلاق في أعلى الشمعة",
                                f'أغلقت عند {pos*100:.0f}٪ من مداها — المشتري '
                                f'أنهى الشمعة وهو ممسك بها')
    prev = M5[max(0, sw - 10):sw]
    if prev and rg > 0:
        avg = sum(x["h"] - x["l"] for x in prev) / len(prev)
        if avg > 0 and rg > avg * 1.2:
            out["range"] = ("شمعة أوسع من جاراتها",
                            f'مداها {rg:,.{DP}f} مقابل متوسط {avg:,.{DP}f} '
                            f'لعشر شمعات قبلها — دخل حجمٌ جديد')
    return out


SLOTS = [("4H", _slot_4h), ("1D", _slot_1d), ("1h", _slot_1h),
         ("sweep", _slot_sweep), ("signal", _slot_signal)]


def pick(D, LAY, PLAN, M5, DP, tag):
    """قراءة واحدة لكل طبقة — الأقلّ استعمالاً أولاً، والتعادل ببصمة النافذة.

    تُرجع قائمة من خمس (مفتاح، عنوان، تفصيل) بترتيب الطبقات."""
    counts, last = used_counts()
    seed = int(hashlib.sha1(tag.encode()).hexdigest()[:8], 16)
    out = []
    for n, (name, fn) in enumerate(SLOTS):
        opts = fn(D, LAY, PLAN, M5, DP)
        keys = sorted(opts)                      # ترتيب ثابت قبل الترجيح
        # الأقلّ استعمالاً أولاً، ثم الأقدم استعمالاً، ثم دوران من النافذة
        best = min(keys, key=lambda k: (counts.get(f"{name}.{k}", 0),
                                        last.get(f"{name}.{k}", -1),
                                        (seed + n * 7 + keys.index(k)) % len(keys)))
        t, d = opts[best]
        out.append((f"{name}.{best}", t, d))
    return out
