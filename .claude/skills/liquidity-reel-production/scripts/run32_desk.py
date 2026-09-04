# -*- coding: utf-8 -*-
"""تشغيلة ٣٢ — ريل «جلسة متداول»: كأن أحدهم فتح المنصّة وجهّز الصفقة بيده.

🔒 أمر فهد 2026-08-06: «اريد الفيديو ان يكون كأنك متداول فتح جارت تريدنق
   فيو و يقوم بتجهيز الست اب لدخول الصفقة» — والثلاثة معاً: واجهة منصّة
   كاملة، ومؤشر فأرة يرسم، وتذكرة أمر تُضغط.
🔒 أمر فهد 2026-08-06 (الثاني): «عممه على كل ريلات المصنع» — فهذا المحرّك
   بديل `run31_reel` لكل وحدة `media=="reel"`.
🔒 وشرطه على التعميم: «تنوّع أسباب الدخول واستراتيجيات الدخول… الشرط ألّا
   يكون تحليلاً بسيطاً مثل كسر ثم أوردر بلوك فقط.»

لذلك ليس هنا سردٌ واحد بل **أربعة أنماط دخول** تُختار بحسب فئة النافذة،
ولكلٍّ فهارسه ووسومه ومسار مؤشره — فريلان من فئتين لا يتشابهان بصرياً:

    sweep  → قمّتان متساويتان تُكنَسان ثم انعكاس   (i1 · i2 · ipdl)
    consol → نطاق تجميع يُكسَر ثم يُعاد اختباره     (ca · cb · rt · rb)
    chan   → قناة هابطة تُخترَق                     (chi · clo)
    zone   → كسر هيكل ثم منطقة الأصل                (iH · bk · iob · ir)

وقبل التذكرة تمرّ **لوحة أسباب** من `confluence.build_desk`: كل سبب رقم
مقيس على الشموع، وما لا يتحقق لا يُعرض. ولا يُبنى ريل بأقلّ من ثلاثة
أسباب متحقّقة — دونها يسقط النمط ويُجرَّب غيره على النافذة نفسها.

الفرق عن `run31_reel`: هناك الوسوم تنبثق جاهزة، وهنا **تُرسم**. المؤشر
يمسك الأداة من الشريط، يسحب المنطقة فتنمو تحته، يفتح التذكرة، ثم يضغط
«شراء». الكاميرا مجمّدة (`cam=[]`) لأن تسجيل الشاشة لا يتنفّس.

النتيجة أولاً (§7) تُنفَّذ بـ`preview_a/preview_b` مع `openmax`: قبل
`preview_b` تكون كل الشموع مكشوفة وكل الماركب مكتملاً، ثم يتلاشى الكل
ويبدأ الريبلاي من الصفر — رجوعٌ حقيقي لا بطاقة نصّية تدّعيه.

كل رقم في التذكرة مشتقّ من الشموع، عدا رأس المال ونسبة المخاطرة —
وهذان **مطبوعان على الشاشة** بوصفهما افتراضاً لا واقعاً.

    python3 run32_desk.py <slug> [<slug> ...]
    python3 run32_desk.py --preflight all      # نافذة × نمط × الأسباب
"""
import json, os, sys

from reel_build import INK, TEAL, TEAL_D, RED, GREY, htext
from reel_sfx_kit import (build_reel, line_el, zone_drag_el, ring, pos_box,
                          checkmark, xmark, set_canvas, set_pad)
import tv_chart
import confluence
import run31_charts as RC
import tv_shell as TV

HERE = os.path.dirname(os.path.abspath(__file__))
CONT = os.path.normpath(os.path.join(HERE, "..", "content"))

# ═══ تخطيط الطرفية: الجارت 996×1300 داخل إطار 1080×1920 ═══
CX, CY = 84, 160                       # ركن الجارت في إحداثيات #stage
CVW, CVH = 996, 1300
set_canvas(CVW, CVH)
set_pad(18, 118, 84, 60)
PL, PR, PT, PB = 18, 118, 84, 60
PW, PH = CVW - PL - PR, CVH - PT - PB
DUR = 22.4                             # سقف skip-rate (§12)
tv_chart.set_theme("light")

# الخانات العشرية وقيمة النقطة لكل أداة (§4 + مواصفات العقود العامة)
DEC = {"GC=F": 1, "NQ=F": 0, "YM=F": 0, "USDJPY=X": 3,
       "AUDUSD=X": 5, "GBPUSD=X": 5, "EURUSD=X": 5,
       # منزلة العرض تتبع الأداة لا العادة: عقد الفرنك بأربع منازل، ولو
       # عُرض بمنزلتين صار وقفٌ عند 1.2582 يُكتب «1.26» فتنتفخ المخاطرة
       # من ١٣ نقطة إلى ١٠٠ على الورق.
       "AUDJPY=X": 3, "NG=F": 3, "ES=F": 2, "ETH-USD": 2,
       "SPY": 2, "IWM": 2, "SLV": 2, "LTC-USD": 2,
       "RB=F": 4, "KC=F": 2, "6S=F": 4, "6A=F": 4, "6J=F": 7}
# قيمة وحدة النقطة للوت الواحد بالدولار: الذهب ١٠٠ أونصة/عقد فـ0.1$ = 10$،
# الناسداك 20$/نقطة، الداو 5$/نقطة، والفوركس لوت قياسي 100k فالبِب = 10$.
POINT_VALUE = {"GC=F": 10.0, "NQ=F": 20.0, "YM=F": 5.0,
               "AUDUSD=X": 10.0, "GBPUSD=X": 10.0, "EURUSD=X": 10.0,
               "USDJPY=X": 9.0,
               # الغاز ١٠٬٠٠٠ وحدة/عقد فحركة 0.001$ = 10$، وإس آند بي
               # المصغّر 50$ للنقطة، والصناديق سهمٌ للنقطة، والبُنّ ٣٧٥٠٠
               # رطل/عقد، وعقود العملات قياسية.
               "NG=F": 10.0, "ES=F": 50.0, "AUDJPY=X": 9.0, "ETH-USD": 1.0,
               "SPY": 1.0, "IWM": 1.0, "SLV": 1.0, "LTC-USD": 1.0,
               "RB=F": 4.2, "KC=F": 18.75, "6S=F": 12.5,
               "6A=F": 10.0, "6J=F": 6.25}
ACCOUNT, RISK_PCT = 10000.0, 0.01      # افتراض مُعلَن على الشاشة
MIN_RISK_BP = 0.0006                   # أرضية `scan_setups` — دونها السبريد يبتلع
MIN_REASONS = 3                        # شرط فهد: لا تحليل بسيط
TF_SECONDS = {"5m": 300, "15m": 900, "30m": 1800, "1h": 3600}
TF_AR = {"5m": "٥د", "15m": "١٥د", "30m": "٣٠د", "1h": "١س"}
TOOLS = ["سهم", "خط", "أفقي", "مربع", "صفقة", "نص"]
TOOL_TOP = [320, 412, 504, 596, 688, 780]
TOOL_X = 42


def tool_xy(i):
    return TOOL_X, TOOL_TOP[i] + 38


def geo(W):
    lo = min(c["l"] for c in W); hi = max(c["h"] for c in W)
    pad = (hi - lo) * 0.08
    ymin, ymax = lo - pad * 1.7, hi + pad
    slot = PW / len(W)
    return (lambda i: PL + slot * i + slot / 2,
            lambda p: PT + (ymax - p) / (ymax - ymin) * PH, slot)


def plan_numbers(r):
    """أرقام الصفقة من الشموع وحدها — بلا استشراف: المدى حتى شمعة الدخول.

    الوقف تحت **أدنى قاع دافعت عنه المنطقة** بين شمعة الأصل وشمعة الدخول،
    لا تحت قاع الشمعة الأصل وحدها: القاع الأدنى وقع قبل التنفيذ فهو معلوم،
    ووقفٌ فوقه يكون داخل مدى تحرّك السعر لا خارجه."""
    W = r["w"]; iob, ir = r["iob"], r["ir"]
    seg = W[:ir + 1]
    rng = max(c["h"] for c in seg) - min(c["l"] for c in seg)
    dp = DEC.get(r["sym"], 2)
    ent = round(W[ir]["c"], dp)
    stp = round(min(W[j]["l"] for j in range(iob, ir + 1)) - rng * 0.006, dp)
    tgt = round(ent + (ent - stp) * 2.0, dp)
    pip = RC.PIP.get(r["sym"], 1.0)
    pts = (ent - stp) / pip
    pv = POINT_VALUE.get(r["sym"], 10.0)
    risk_usd = ACCOUNT * RISK_PCT
    lot = risk_usd / max(pts * pv, 1e-9)
    # شمعة بلوغ الهدف: أول شمعة تلامس ٢R بعد الدخول — لا أعلى قمة في
    # النافذة. الأمر يُغلق عند هدفه، فإعلان قمة السوق كلها ربحاً كذب.
    hit = next((j for j in range(ir + 1, len(W)) if W[j]["h"] >= tgt), None)
    assert stp < ent < tgt, "ترتيب الوقف/الدخول/الهدف غير سليم"
    assert (ent - stp) / ent >= MIN_RISK_BP, \
        f"المخاطرة {(ent-stp)/ent*1e4:.1f} نقطة أساس — داخل السبريد"
    assert hit is not None, "السعر لم يبلغ هدف ٢R في هذه النافذة"
    assert lot >= 0.01, "الحجم المحسوب أصغر من أدنى لوت"
    return dict(ent=ent, stp=stp, tgt=tgt, dp=dp, pts=pts, lot=lot,
                risk=risk_usd, reward=risk_usd * 2, top_i=hit,
                result_pts=int(round(pts * 2)))


# ═══════════ أربعة أنماط دخول ═══════════
# كل نمط يُرجع: عناصر SVG بمعرّفات ثابتة (`A1`/`A1L`/`A2`/`A2L`/`zn`)،
# وإحداثيات ما يُرسم كي يتبعه المؤشر، والأداة التي يمسكها من الشريط.
# ولا يُرجع شيئاً قبل أن تثبت ادّعاءاته بـ`assert` على الشموع نفسها.

def _lbl(id_, x, y, txt, col, fs=25):
    return f'<g id="{id_}" opacity="0">{htext(x, y, txt, col, fs)}</g>'


def a_zone(r, W, x, y, slot, P):
    """كسر هيكل ثم منطقة الأصل — النمط الأساسي، متاح لكل نافذة."""
    iH, bk, iob, ir = r["iH"], r["bk"], r["iob"], r["ir"]
    lv = W[iH]["h"]
    assert W[bk]["c"] > lv, "شمعة الكسر لم تُغلق فوق القمة"
    zt, zb = W[iob]["o"], W[iob]["l"]
    assert zt > zb, "الشمعة الأصل ليست هابطة"
    l1 = (x(iH) - slot * .6, y(lv), x(bk) + slot * .55, y(lv))
    zn = (x(iob) - slot * .6, y(zt), x(min(ir + 3, len(W) - 1)) + slot * .5, y(zb))
    els = [line_el(*l1, INK, 2.4, id="A1"),
           _lbl("A1L", x(iH) + slot * 1.9, y(lv) - 16, "كسر الهيكل", INK)]
    return dict(key="zone", name="منطقة طلب بعد كسر هيكل", tool1=2,
                els=els, l1=l1, l2=None, zn=zn,
                zn_lbl=htext(x(iob) + slot * 3.2, y(zb) + 32, "منطقة الطلب", TEAL_D, 24),
                S=dict(LH=lv, ZT=zt, iob=iob, bk=bk))


def a_sweep(r, W, x, y, slot, P):
    """سحب سيولة: قمّتان متساويتان تحدّان التصحيح، ثم قاعٌ يُكنَس قبل الانعكاس."""
    i1, i2, ipdl = r["i1"], r["i2"], r["ipdl"]
    iob, ir, bk = r["iob"], r["ir"], r["bk"]
    rng = max(c["h"] for c in W[:ir + 1]) - min(c["l"] for c in W[:ir + 1])
    hi = max(W[i1]["h"], W[i2]["h"])
    assert abs(W[i1]["h"] - W[i2]["h"]) <= rng * 0.04, "القمّتان غير متساويتين"
    assert i2 > i1 and ir > i2, "ترتيب القمّتين والدخول غير سليم"
    # الكنس يجب أن يقع فعلاً: قاعٌ أدنى من قاع `ipdl` قبل التنفيذ أو عنده
    low0 = W[ipdl]["l"]
    sw = next((j for j in range(ipdl + 1, ir + 1) if W[j]["l"] < low0), None)
    assert sw is not None, "لم يُكنَس القاع قبل الدخول — القصّة ليست سحب سيولة"
    zt, zb = W[iob]["o"], W[iob]["l"]
    l1 = (x(i1) - slot * .6, y(hi), x(i2) + slot * .8, y(hi))
    l2 = (x(ipdl) - slot * .6, y(low0), x(ir) + slot * .6, y(low0))
    zbot = min(zb, W[sw]["l"])
    zn = (x(min(ipdl, iob)) - slot * .6, y(zt), x(min(ir + 2, len(W) - 1)) + slot * .5,
          y(zbot))
    # وسوم السيولة تحت المنطقة لا فوقها: فوقها يقع بوكس الصفقة لاحقاً،
    # وقد كان الوسم يجلس على «الدخول» وعلى شريط السعر الأخير معاً.
    els = [line_el(*l1, INK, 2.4, id="A1"),
           _lbl("A1L", x(i1) + slot * 2.2, y(hi) - 16, "قمّتان متساويتان", INK),
           line_el(*l2, RED, 2.2, dash="8 7", id="A2"),
           _lbl("A2L", x(ipdl) + slot * 2.2, y(zbot) + 64, "قاعٌ مكنوس", RED),
           xmark(x(sw), y(W[sw]["l"]) + 46, id="A3", r=15)]
    return dict(key="sweep", name="سحب سيولة ثم انعكاس", tool1=2,
                els=els, l1=l1, l2=l2, zn=zn, extra_mark=("A3", 9.05, 9.45, "drawx"),
                fade=["A2", "A2L", "A3"],
                zn_lbl=htext(x(iob) + slot * 3.4, y(zbot) + 30, "منطقة التنفيذ", TEAL_D, 24),
                S=dict(i1=i1, i2=i2, ipdl=ipdl, bk=bk, ZT=zt, iob=iob, LH=W[r["iH"]]["h"]))


def a_consol(r, W, x, y, slot, P):
    """نطاق تجميع: انضغاط ← كسر السقف بإغلاق ← عودة لاختباره."""
    ca, cb, bk, ir, iob = r["ca"], r["cb"], r["bk"], r["ir"], r["iob"]
    assert cb > ca + 3, "النطاق أقصر من أن يُسمّى نطاقاً"
    assert cb < bk, "النطاق لم ينتهِ قبل الكسر"
    rt = max(W[k]["h"] for k in range(ca, cb + 1))
    rb = min(W[k]["l"] for k in range(ca, cb + 1))
    rng = max(c["h"] for c in W[:ir + 1]) - min(c["l"] for c in W[:ir + 1])
    assert (rt - rb) <= rng * 0.42, "النطاق أوسع من أن يُعدّ انضغاطاً"
    assert W[bk]["c"] > rt, "الكسر لم يُغلق فوق سقف النطاق"
    l1 = (x(ca) - slot * .6, y(rt), x(min(ir + 2, len(W) - 1)) + slot * .5, y(rt))
    zn = (x(ca) - slot * .6, y(rt), x(cb) + slot * .5, y(rb))
    els = [line_el(*l1, INK, 2.4, id="A1"),
           _lbl("A1L", x(cb) + slot * 1.4, y(rt) - 16, "سقف النطاق", INK)]
    return dict(key="consol", name="نطاق تجميع يُكسَر ويُختبَر", tool1=2,
                els=els, l1=l1, l2=None, zn=zn,
                zn_lbl=htext((x(ca) + x(cb)) / 2, y(rb) + 32, "نطاق التجميع", TEAL_D, 24),
                S=dict(ca=ca, cb=cb, bk=bk, ZT=W[iob]["o"], iob=iob))


def a_chan(r, W, x, y, slot, P):
    """قناة هابطة: قمم وقيعان متدرّجة معاً، ثم اختراق السقف بإغلاق."""
    hi, lo = r["chi"], r["clo"]
    bk, ir, iob = r["bk"], r["ir"], r["iob"]
    assert len(hi) == 2 and len(lo) == 2, "القناة تحتاج قمّتين وقاعين"
    assert W[hi[1]]["h"] < W[hi[0]]["h"], "القمم لم تتدرّج هبوطاً"
    assert W[lo[1]]["l"] < W[lo[0]]["l"], "القيعان لم تتدرّج هبوطاً"
    assert W[bk]["c"] > W[hi[1]]["h"], "الاختراق لم يُغلق فوق آخر قمة"
    l1 = (x(hi[0]), y(W[hi[0]]["h"]), x(hi[1]), y(W[hi[1]]["h"]))
    l2 = (x(lo[0]), y(W[lo[0]]["l"]), x(lo[1]), y(W[lo[1]]["l"]))
    zt, zb = W[iob]["o"], W[iob]["l"]
    zn = (x(iob) - slot * .6, y(zt), x(min(ir + 3, len(W) - 1)) + slot * .5, y(zb))
    els = [line_el(*l1, INK, 2.4, id="A1"),
           _lbl("A1L", x(hi[0]) + slot * 2.4, y(W[hi[0]]["h"]) - 16, "سقف القناة", INK),
           line_el(*l2, INK, 2.2, id="A2"),
           _lbl("A2L", x(lo[0]) + slot * 2.4, y(W[lo[0]]["l"]) + 34, "قاع القناة", INK)]
    return dict(key="chan", name="قناة هابطة تُخترَق", tool1=1,
                els=els, l1=l1, l2=l2, zn=zn,
                zn_lbl=htext(x(iob) + slot * 3.2, y(zb) + 32, "منطقة الأصل", TEAL_D, 24),
                S=dict(chi=hi, clo=lo, bk=bk, ZT=zt, iob=iob))


ARCH = {"sweep": a_sweep, "consol": a_consol, "chan": a_chan, "zone": a_zone}


def archetypes_for(r, W, x, y, slot, P):
    """الأنماط الصالحة على هذه النافذة مرتّبةً: فئتها أولاً ثم الأساسي.

    كل نمط يمرّ باختبارين: أن تُثبت الشموع ادّعاءاته، وأن تتحقّق منه
    ثلاثة أسباب مقيسة فأكثر. والساقط يُعاد بسببه لا يُبتلع."""
    ok, bad = [], []
    order = [r["cls"]] + [k for k in ("zone",) if k != r["cls"]]
    for key in order:
        fn = ARCH.get(key)
        if fn is None:
            continue
        try:
            A = fn(r, W, x, y, slot, P)
        except (AssertionError, KeyError, IndexError) as e:
            bad.append((key, f"{type(e).__name__}: {e}")); continue
        S = dict(A["S"], w=W, fill=r["ir"], cls=key,
                 ENT=P["ent"], STP=P["stp"], TGT=P["tgt"])
        try:
            reasons, rr_row = confluence.build_desk(S)
        except (KeyError, IndexError) as e:
            bad.append((key, f"أسباب: {type(e).__name__}: {e}")); continue
        if len(reasons) < MIN_REASONS:
            bad.append((key, f"{len(reasons)} أسباب فقط — الحدّ {MIN_REASONS}")); continue
        A["reasons"], A["rr"] = reasons[:3], rr_row
        ok.append(A)
    return ok, bad


def preflight(idx):
    """تقرير نافذة واحدة: الأرقام، والأنماط الصالحة، والساقط بسببه."""
    r = RC.win(idx)
    W = r["w"]; x, y, slot = geo(W)
    P = plan_numbers(r)
    ok, bad = archetypes_for(r, W, x, y, slot, P)
    return r, P, ok, bad


# ═══════════ واجهة المنصّة (HTML + CSS) ═══════════
def chrome_html(r, P, A):
    d = P["dp"]
    rows = "".join(
        f'<div class="rs" id="rs{i+1}"><b>{q["t"]}</b><span>{q["d"]}</span></div>'
        for i, q in enumerate(A["reasons"]))
    reasons = f'''<div id="reasons">
  <div class="rsh">أسباب الدخول — كلٌّ منها مقيس على الشموع</div>{rows}
  <div class="rs rsr" id="rs4"><b>{A["rr"]["t"]}</b><span>{A["rr"]["d"]}</span></div>
</div>'''
    ticket = f'''<div id="ticket">
  <div class="tkh"><b>أمر شراء</b><span>{r["sym"]} · سوق</span></div>
  <div class="tkg">
    <div class="tkf" id="tf1"><span>السعر</span><b>{P["ent"]:,.{d}f}</b></div>
    <div class="tkf" id="tf2"><span>وقف الخسارة</span><b class="dn">{P["stp"]:,.{d}f}</b></div>
    <div class="tkf" id="tf3"><span>جني الأرباح</span><b class="up">{P["tgt"]:,.{d}f}</b></div>
    <div class="tkf" id="tf4"><span>الحجم</span><b>{P["lot"]:.2f}</b></div>
    <div class="tkf" id="tf5"><span>المخاطرة</span><b class="dn">−{P["risk"]:,.0f}$</b></div>
    <div class="tkf" id="tf6"><span>العائد · ٢R</span><b class="up">+{P["reward"]:,.0f}$</b></div>
  </div>
  <div class="tkb" id="tkbuy">شراء {P["lot"]:.2f}</div>
  <div class="tkn">مثال: حساب 10,000$ · مخاطرة ١٪ — الحجم مشتقّ منهما</div>
</div>'''
    # الشريط العلوي وصفّ الفريمات وعمود الأدوات صارت في `tv_shell`
    # المشتركة (أمر التعميم 2026-08-06) — ويبقى هنا ما يخصّ هذا الريل.
    return TV.shell_html(r["sym"], r["tf"]) + reasons + ticket


CHROME_CSS = TV.SHELL_CSS + f"""
#reasons{{position:absolute;top:1010px;left:84px;width:996px;height:450px;padding:22px 30px;
  background:#FBF9F5;border-top:2.5px solid rgba(15,46,60,.30);
  box-shadow:0 -20px 46px rgba(15,46,60,.10);z-index:10;opacity:0}}
#reasons .rsh{{font-size:24px;font-weight:800;color:#6B7C84;margin-bottom:14px}}
#reasons .rs{{opacity:0;border-right:3px solid {TEAL_D};padding:7px 15px 7px 10px;margin-bottom:11px}}
#reasons .rs b{{display:block;font-size:27px;font-weight:900;color:{INK};margin-bottom:2px}}
#reasons .rs span{{display:block;font-size:21px;font-weight:600;color:#6B7C84;line-height:1.35}}
#reasons .rsr{{border-right-color:#B9C6CB}}
#ticket{{position:absolute;top:1010px;left:84px;width:996px;height:450px;
  padding:24px 30px 26px;
  background:#FBF9F5;border-top:2.5px solid {TEAL_D};box-shadow:0 -20px 46px rgba(15,46,60,.13);
  z-index:11;opacity:0}}
#ticket .tkh{{display:flex;align-items:baseline;gap:14px;margin-bottom:18px}}
#ticket .tkh b{{font-size:30px;font-weight:900;color:{INK}}}
#ticket .tkh span{{font-size:21px;font-weight:700;color:#6B7C84;direction:ltr}}
#ticket .tkg{{display:grid;grid-template-columns:1fr 1fr 1fr;gap:14px 18px}}
.tkf{{border:1.4px solid rgba(15,46,60,.15);padding:10px 14px;opacity:0}}
.tkf span{{display:block;font-size:19px;font-weight:700;color:#6B7C84;margin-bottom:3px}}
.tkf b{{display:block;font-size:31px;font-weight:900;color:{INK};direction:ltr}}
.tkf b.up{{color:{TEAL_D}}} .tkf b.dn{{color:{RED}}}
#ticket .tkb{{margin-top:20px;background:{TEAL_D};color:#FBF9F5;font-size:33px;font-weight:900;
  text-align:center;padding:16px;direction:ltr}}
#ticket .tkn{{margin-top:12px;font-size:19px;font-weight:600;color:#8C9BA2;text-align:center}}
.hl{{top:1486px;left:70px;right:70px}}
.hl b{{display:block;font-size:46px;font-weight:900;line-height:1.16;letter-spacing:-.5px}}
.hl .why{{display:block;margin-top:9px;font-size:27px;font-weight:600;color:#6B7C84}}
#chartclip{{top:{CY}px;left:{CX}px}}
#chip{{display:none}} #res{{display:none}} #endlogo{{display:none}}
#cta{{top:1706px}} #cta .k{{font-size:42px;padding:8px 28px}} #cta .s{{margin-top:7px;font-size:25px}}
#edu{{bottom:26px;font-size:19px;opacity:.55}}
"""

# عدّاد إغلاق الشمعة: العنصر الوحيد «الحي» في الواجهة. يُحدَّث بتغليف
# `window.__setFrame` بعد التحميل — لا يحتاج تعديل المحرّك، والتغليف يقع
# بعد تعريف الدالة لأن `load` يلي تنفيذ سكربت المحرّك.
COUNTDOWN_JS = """<script>
window.addEventListener('load', () => {
  const base = window.__setFrame, TOT = __TOT__, START = __START__;
  const el = document.getElementById('cdown');
  window.__setFrame = t => {
    base(t);
    const left = Math.max(0, START - t);
    const m = Math.floor(left / 60), s = Math.floor(left % 60);
    el.textContent = String(m).padStart(2,'0') + ':' + String(s).padStart(2,'0');
  };
});
</script>"""


# ═══════════ الأطوار: الكاتب يكتب المعنى، والمحرّك يملك الزمن ═══════════
# كان الكاتب يضع `t` بيده على شبكة زمنية، فأي تغيير في الإيقاع يكسر كل
# ملفات المحتوى. الآن يكتب `phase` والمحرّك يضع البيت في نافذة طوره.
PHASE_T = {
    "result":    (0.10, 2.45),
    "structure": (2.70, 5.90),
    "setup":     (6.00, 9.30),
    "wait":      (9.40, 12.30),
    "ticket":    (12.40, 16.30),
    "press":     (16.45, 19.60),
    "outcome":   (19.70, 21.90),
}
PHASES = list(PHASE_T)

# نصوص افتراضية **بالفصحى** (قرار 2026-08-06) لكل نمط — يكتب الكاتب فوقها
# ما شاء بحقل `phase`، وما لم يكتبه يبقى على هذه.
_COMMON = {
    "result": ("هذه الصفقة أُغلقت على +{result_pts} نقطة",
               "سأُريكم كيف جُهِّزت من الصفر"),
    "wait": ("ثم أنتظر — لا أُطارد السعر",
             "الأسباب تُحصى قبل الضغطة لا بعدها"),
    "ticket": ("عاد إلى المنطقة… أفتح التذكرة",
               "الوقف تحت ما دافع عنه السعر، والهدف ضعف المخاطرة"),
    "press": ("ثم أضغط شراء",
              "القرار اكتمل قبل الضغطة لا بعدها"),
    "outcome": ("تحقّق الهدف — +{result_pts} نقطة",
                "على المستوى نفسه الذي رُسم في الثانية السادسة"),
}
DEFAULT_BEATS = {
    "zone": dict(_COMMON,
                 structure=("أولاً: أين انكسر الهيكل؟",
                            "أُحدِّد القمة التي أغلق فوقها الجسم لا الفتيل"),
                 setup=("المنطقة تُولَد من الشمعة التي سبقت الكسر",
                        "أسحبها بالمستطيل من فتيلها إلى جسمها")),
    "sweep": dict(_COMMON,
                  structure=("أولاً: أين تجمّعت السيولة؟",
                             "قمّتان متساويتان، وتحت القاع أوامر إيقاف تنتظر"),
                  setup=("كُنِس القاع ثم عاد السعر فوقه",
                         "أُظلّل المنطقة التي وقع فيها الانعكاس")),
    "consol": dict(_COMMON,
                   structure=("أولاً: أين سقف النطاق؟",
                              "الحدّ الذي رُفض عنده السعر مراراً قبل أن يُكسَر"),
                   setup=("أرسم النطاق كاملاً لا خطاً واحداً",
                          "الانضغاط هو الذي صنع الحركة التي تلته")),
    "chan": dict(_COMMON,
                 structure=("أولاً: ما شكل الهبوط؟",
                            "قمم وقيعان تتدرّج معاً — قناة لا هبوط عشوائي"),
                 setup=("ثم أُحدِّد منطقة الأصل بعد الاختراق",
                        "الاختراق وحده لا يكفي: أنتظر العودة إليها")),
}


def beats_for(C, A, P):
    """بيتات الريل: نص المحتوى إن وُجد بطوره، وإلا الافتراضي بالفصحى."""
    src = {}
    for b in (C.get("reel") or {}).get("beats", []):
        if b.get("phase") in PHASE_T:
            src[b["phase"]] = (b.get("title", ""), b.get("sub", ""))
    dflt = DEFAULT_BEATS[A["key"]]
    out = []
    for ph in PHASES:
        t, sub = src.get(ph) or dflt.get(ph) or (None, None)
        if not t:
            continue                       # غياب طور = صمت مسموح
        a, b = PHASE_T[ph]
        body = f'<b>{t.format(**P)}</b>'
        if sub:
            body += f'<span class="why">{sub.format(**P)}</span>'
        out.append((f"t{len(out)+1}", a, b, body, 46, INK))
    return out


# مُحمِّل المحتوى — قابل للتبديل. الافتراضي خطّة `run31_build`، وتشغيلةٌ
# بملفّاتها الخاصّة تضع دالّتها هنا بدل نسخ المحرّك كلّه لأجل مسار ملف.
LOAD = None


def build(slug, win_idx=None, arch=None):
    import run31_build                       # خطة النوافذ والصيغ لكل وحدة
    C = (LOAD or run31_build.load)(slug)
    r = RC.win(C["window"] if win_idx is None else win_idx)
    iob, ir = r["iob"], r["ir"]
    P = plan_numbers(r)
    # **الرسم ينتهي حيث تنتهي الصفقة.** `geo` يقيس المحور على النافذة
    # كاملةً، والنافذة تمتدّ شمعاتٍ بعد بلوغ الهدف. فإن كان فيها بعده
    # اندفاعٌ كبير سرق المحورَ كلَّه، انضغطت شموع القصّة في أسفل اللوحة
    # ثم غطّتها لوحةُ الأسباب حين تصعد — فتُشاهَد ثوانٍ ببياضٍ لا شمعة
    # فيه (رُصد بصرياً 2026-09-04 على نافذة الأسترالي/الدولار ٥٠: مدى
    # النافذة ٥٣ نقطة ومدى القصّة ١٦، فوقعت الشموع في الربع السفلي).
    # والقصّ عند `top_i` هو ما يقوله `plan_numbers` أصلاً: «الأمر يُغلق
    # عند هدفه، فإعلان قمة السوق كلها ربحاً كذب» — فما بعد الهدف ليس من
    # القصّة أصلاً. ولا فهرسَ من فهارس الماركب بعده: كلها قبل الدخول.
    r = dict(r, w=r["w"][:P["top_i"] + 1])
    W = r["w"]; x, y, slot = geo(W)
    assert max(iob, ir, r["bk"], r["iH"]) < len(W), "فهرس ماركب خارج الرسم بعد القصّ"
    ok, bad = archetypes_for(r, W, x, y, slot, P)
    if arch:
        ok = [a for a in ok if a["key"] == arch]
    if not ok:
        raise RuntimeError(f'{slug}: لا نمط يثبت على النافذة — '
                           + " · ".join(f"{k}: {m}" for k, m in bad))
    A = ok[0]
    top_i = P["top_i"]
    sx = lambda i: CX + x(i)                 # إحداثيات #stage للمؤشر
    sy = lambda p: CY + y(p)

    ex = list(A["els"]) + [
        zone_drag_el("zn", *A["zn"], A["zn_lbl"]),
        ring("ent", x(ir), y(W[ir]["l"]), 15, TEAL_D, ""),
        pos_box("box", x(ir) - slot * .5, CVW - PR, y(P["ent"]), y(P["stp"]), y(P["tgt"]),
                lbl_e=f'الدخول {P["ent"]:,.{P["dp"]}f}',
                lbl_s=f'الوقف {P["stp"]:,.{P["dp"]}f}',
                lbl_t=f'الهدف ٢R {P["tgt"]:,.{P["dp"]}f}', anchor_e="start", col_e=INK),
        checkmark(x(top_i), y(W[top_i]["h"]) - 40, id="ck"),
    ]

    # الرسم: خطٌّ واحد يأخذ الطور كاملاً، وخطّان يقتسمانه
    two = A["l2"] is not None
    d1 = (3.55, 4.40) if two else (3.55, 5.35)
    d2 = (4.60, 5.35)
    marks = [("A1", d1[0], d1[1], "draw"), ("A1L", d1[1] + .10, d1[1] + .40, "pop")]
    if two:
        marks += [("A2", d2[0], d2[1], "draw"), ("A2L", d2[1] + .10, d2[1] + .40, "pop")]
    marks += [("zn", 6.60, 8.90, "zonedrag")]
    if A.get("extra_mark"):
        marks.append(A["extra_mark"])
    marks += [("ent", 11.90, 12.35, "ring"),
              ("box", 17.05, 18.60, "posbox"),
              ("ck", 20.30, 20.70, "pop")]
    # أدوات القياس تنسحب حين يُفتح الأمر: بوكس الصفقة يشغل يمين اللوحة،
    # وإبقاء وسوم السيولة تحته يجعلهما سطراً واحداً على السطر.
    fade = set(A.get("fade", []))
    marks = [(m + (16.80, 0.35)) if m[0] in fade else m for m in marks]
    # حلقة الوسوم في المحرّك تدور على `fullset` وحدها، و`drawset` لا يضبط
    # سوى تقدّم الرسم. فالخطّ الذي يجب أن ينسحب لاحقاً يلزم أن يكون في
    # `fullset` أيضاً، وإلا بقي ظاهراً إلى آخر الريل رغم زمن اختفائه.
    drawn = {"A1", "A2"} - fade
    full = [m[0] for m in marks if m[0] not in drawn]
    drawset = ["A1"] + (["A2"] if two else [])

    # نقرات الأدوات ولوحة الأسباب والتذكرة — كلها عبر dom_marks القائمة
    dom = [[f'tg{A["tool1"]}', 3.30, 3.50, 3.85, 0.25],
           ["tg3", 6.10, 6.30, 6.65, 0.25],          # المستطيل
           ["reasons", 9.50, 9.85, 12.35, 0.30],
           ["tg4", 12.45, 12.65, 13.00, 0.25],       # أداة الصفقة
           ["ticket", 12.70, 13.10, 17.00, 0.35]]
    for i in range(len(A["reasons"]) + 1):           # الأسباب تُحصى سطراً سطراً
        dom.append([f"rs{i+1}", 9.85 + i * 0.46, 10.15 + i * 0.46, 12.30, 0.28])
    for i in range(6):                               # حقول التذكرة تمتلئ تباعاً
        dom.append([f"tf{i+1}", 13.25 + i * 0.42, 13.55 + i * 0.42, 17.00, 0.3])

    # مسار المؤشر — إحداثيات #stage، ورأسه عند رأس ما يُرسَم
    tx, ty = tool_xy(A["tool1"])
    bx, by = tool_xy(3)
    cur = [
        [0.30, 880, 620], [2.70, 880, 620, "creep"],
        [3.20, tx, ty, "ramp"], [3.30, tx, ty, "ss", "down"],
        [d1[0], CX + A["l1"][0], CY + A["l1"][1], "ramp"],
        [d1[1], CX + A["l1"][2], CY + A["l1"][3], "lin"],
    ]
    if two:
        cur += [[d2[0], CX + A["l2"][0], CY + A["l2"][1], "ramp"],
                [d2[1], CX + A["l2"][2], CY + A["l2"][3], "lin"]]
    cur += [
        [6.05, bx, by, "ramp"], [6.15, bx, by, "ss", "down"],
        [6.60, CX + A["zn"][0], CY + A["zn"][1], "ramp"],
        [8.90, CX + A["zn"][2], CY + A["zn"][3], "lin"],
        [10.10, 700, 1180, "creep"],                  # يقرأ لوحة الأسباب
        [12.20, sx(ir), sy(W[ir]["l"]), "creep"],
        [12.40, *tool_xy(4), "whip"], [12.50, *tool_xy(4), "ss", "down"],
        [13.10, 700, 1180, "ramp"],
        [16.55, 560, 1392, "ramp"], [16.90, 560, 1392, "ss", "down"],
        [17.60, 900, 1180, "creep"], [19.40, 940, 700, "creep"],
    ]

    # base صغير ليُرى الريبلاي فعلاً بعد الرجوع، وopenmax=N ليكتمل الجارت
    # في لقطة النتيجة الأولى. الشموع تتكشّف على ثلاث مراحل: حتى الكسر، ثم
    # حتى الدخول، ثم الباقي بعد ضغط «شراء».
    bk = r["bk"]
    base = max(3, min(iob, r.get("ca", iob), r["iH"]) - 3)
    n = len(W)
    story = []
    for j in range(base + 1, bk + 3):
        story.append((j, round(3.10 + (j - base - 1) * 0.16, 2)))
    for j in range(bk + 3, ir + 1):
        story.append((j, round(9.50 + (j - bk - 3) * (2.6 / max(1, ir - bk - 2)), 2)))
    for j in range(ir + 1, n):
        story.append((j, round(18.70 + (j - ir - 1) * (2.2 / max(1, n - ir - 1)), 2)))
    tsec = TF_SECONDS.get(r["tf"], 900)
    js = COUNTDOWN_JS.replace("__TOT__", str(tsec)).replace(
        "__START__", f"{tsec * 0.42:.0f}")

    cfg = dict(
        w=W, dark=False, extra_css=CHROME_CSS,
        extra_html=chrome_html(r, P, A) + js, grid=False,
        pre_svg=tv_chart.furniture(W, dec=P["dp"], sym=r["sym"], tf=r["tf"],
                                   tlabels=[c["d"] for c in W]),
        lp_pill=True, lp_dec=P["dp"], lp_col=tv_chart.T["PILL"],
        lp_txt=tv_chart.T["PILLTX"],
        base=base, openmax=len(W) - 1, open_t=[[len(W) - 1, 0.35]], story=story,
        extra_svg="".join(ex), marks=marks, fullset=full, drawset=drawset,
        dom_marks=dom, cursor=cur,
        # الرجوع الحقيقي: الجارت كامل بصفقته حتى 2.50 ثم يتلاشى ويُعاد بناؤه
        preview_a=2.50, preview_b=2.95, res_tease=False, sweep_op=0.45,
        txt=beats_for(C, A, P), chip="", res="",
        cta_k=f'اكتب «{C["car"]["cta"]["keyword"]}»', cta_s="ويصلك الدليل كاملاً",
        edu=f'{r["slug"]} — لغرض تعليمي · مثال حسابي لا توصية',
        dur=DUR, res_t=999, cta_t=DUR - 2.3,
        flash=(2.50, 2.95), flash_op=0.10, punch=(16.90, 17.30, 0.04),
        cam=[],                     # تسجيل الشاشة لا يتنفّس
    )
    out = os.path.join(HERE, f"reel32_{slug}.html")
    nb = build_reel(cfg, out)
    # التسجيل: نافذة الوحدة يسجّلها `run31_build`، أما نافذةٌ أُسندت لهذا
    # الريل وحده (`win_idx`) فلا يعرفها أحد غيره — فيسجّلها بنفسه.
    if win_idx is not None:
        RC.claim_fresh(r, f"run32-{slug}")
        RC.register(f"run32-{slug}", r, f"run32-{slug}")
    print(f'{slug:<10} {A["name"]:<26} · نافذة {r["slug"]}\n'
          f'  الدخول {P["ent"]:,.{P["dp"]}f} · الوقف {P["stp"]:,.{P["dp"]}f} · '
          f'الهدف {P["tgt"]:,.{P["dp"]}f} · {P["pts"]:.0f} نقطة · '
          f'حجم {P["lot"]:.2f} · النتيجة +{P["result_pts"]} نقطة\n'
          f'  الأسباب: ' + " · ".join(q["t"] for q in A["reasons"]) +
          f' · {nb} bytes')
    return out


# مؤثرات §12: مؤثر واحد لكل حدث، والصمت بينها جزء من الإيقاع.
# النقرات بـ`click` لا `pop` — الأخيرة نغمة حدث لا ضغطة زرّ (§12/الحزمة G).
SFX = [("success", 0.20, -4), ("whoosh", 2.55, -2), ("click", 3.32, -3), ("whoosh", 3.60, -5),
       ("pop", 5.50, -4), ("click", 6.12, -3), ("whoosh", 6.65, -5),
       ("pop", 8.95, -4), ("tick", 10.10, -8), ("tick", 11.00, -8), ("tick", 11.90, -8),
       ("click", 12.47, -3), ("whoosh", 12.75, -6), ("tick", 13.40, -9),
       ("tick", 14.60, -9), ("riser", 15.60, -3), ("click", 16.90, -1), ("impact", 16.98, 0),
       ("tick", 19.20, -8), ("success", 20.90, -2)]


def _preflight_all():
    import run31_charts as _RC
    for i, rec in enumerate(_RC.CAND):
        if rec.get("bad"):
            print(f'{i:>2} ✗ {rec["cls"]:<7} {rec["sym"]:<10} {rec["tf"]:<4} '
                  f'— مخزون فاسد: {rec["bad"][0]}')
            continue
        try:
            r, P, ok, bad = preflight(i)
        except AssertionError as e:
            print(f'{i:>2} ✗ {rec["cls"]:<7} {rec["sym"]:<10} {rec["tf"]:<4} — {e}')
            continue
        names = ", ".join(f'{a["key"]}({len(a["reasons"])})' for a in ok) or "—"
        print(f'{i:>2} {"✓" if ok else "✗"} {rec["cls"]:<7} {rec["sym"]:<10} '
              f'{rec["tf"]:<4} {rec["date"]} · {P["pts"]:.0f} نقطة مخاطرة · '
              f'نتيجة +{P["result_pts"]} · أنماط: {names}'
              + ("" if not bad else "\n     ساقط: " +
                 " | ".join(f"{k}: {m}" for k, m in bad)))


if __name__ == "__main__":
    if "--preflight" in sys.argv:
        _preflight_all()
    else:
        for s in sys.argv[1:]:
            build(s)
