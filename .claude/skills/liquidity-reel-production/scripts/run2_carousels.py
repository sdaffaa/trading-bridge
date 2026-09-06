# -*- coding: utf-8 -*-
# تشغيلة المصنع 2 — 3 كاروسيلات: انتقام (نفسية) · يوميات (أساسية) · ستوب (مالية)
import os
from car_common import (CW, brandbar, counter, swipe, dots, eyebrow, cover_slide, quote_slide,
                        cta_slide, sk, dkmap, build_carousel, htext, hend,
                        INK, TEAL, TEAL_D, TEAL_L, RED, GREY, MUTE)
from run1_carousels import numbered, problem, rules, W

HERE = os.path.dirname(os.path.abspath(__file__))

# ---------- مرئيات ----------
def escalation(Wd=880, H=380):
    """تصاعد الانتقام: -1R ثم -2R ثم -4R."""
    seq = [("صفقة عادية", 1), ("«أعوّض» — ضاعفت", 2), ("«آخر مرة» — كبّرت", 4)]
    zero = H*0.30; unit = H*0.14
    xs = [Wd*0.22, Wd*0.5, Wd*0.78]
    s = [f'<svg viewBox="0 0 {Wd} {H}" width="{Wd}" height="{H}" xmlns="http://www.w3.org/2000/svg">']
    s.append(f'<line x1="40" y1="{zero:.0f}" x2="{Wd-40}" y2="{zero:.0f}" stroke="{MUTE}" stroke-width="1.4"/>')
    for (lab, r), cx in zip(seq, xs):
        h = r*unit
        s.append(f'<rect x="{cx-34:.0f}" y="{zero:.0f}" width="68" height="{h:.0f}" fill="{RED}" opacity="0.85" rx="1"/>')
        s.append(htext(cx, zero+h+34, f"-{r}R", RED, 22))
        s.append(htext(cx, zero-16, lab, INK, 19))
    s.append(htext(Wd*0.5, H-14, "ثلاث صفقات غضب = ‎-7R‎ بجلسة وحدة", RED, 21))
    return "".join(s)+"</svg>"

def jbars(Wd=880, H=360):
    """نمط الغلط المتكرر: صفقات الأسبوع بأسبابها."""
    seq = [("سيت أب", 2, TEAL_D), ("ملل", -1, RED), ("سيت أب", 2, TEAL_D),
           ("ملل", -1, RED), ("أخبار", -1, RED), ("سيت أب", 2, TEAL_D)]
    zero = H*0.52; unit = H*0.13
    s = [f'<svg viewBox="0 0 {Wd} {H}" width="{Wd}" height="{H}" xmlns="http://www.w3.org/2000/svg">']
    s.append(f'<line x1="40" y1="{zero:.0f}" x2="{Wd-40}" y2="{zero:.0f}" stroke="{MUTE}" stroke-width="1.4"/>')
    for i, (lab, v, col) in enumerate(seq):
        cx = 80 + i*(Wd-160)/5; h = abs(v)*unit
        y0 = zero-h if v > 0 else zero
        s.append(f'<rect x="{cx-26:.0f}" y="{y0:.0f}" width="52" height="{h:.0f}" fill="{col}" opacity="0.85" rx="1"/>')
        s.append(htext(cx, zero+(h+30 if v < 0 else 30), lab, col, 18))
    s.append(htext(Wd*0.5, H-12, "اليوميات كشفت: كل الخسائر «ملل وأخبار» — مو سيت أب", INK, 20))
    return "".join(s)+"</svg>"

SK_WRONG = sk(
    pts=[(0,4.5),(0.9,6.5),(1.7,4.0),(2.6,8.4),(3.3,7.2),(4.0,9.6),(4.7,8.5),(5.3,9.0),(5.9,7.9),(6.6,10.8),(7.4,9.7),(8.2,12.4)],
    W=880, H=360,
    lines=[{"p":[(4.9,8.05),(6.9,8.05)],"c":RED,"dash":"8 7","w":2.2}],
    circle=(5.9,8.05),
    texts=[(5.9,7.0,"ستوب بالضجيج — انطق",RED,19),(7.8,12.0,"وراح بدونك",TEAL_D,18)])
SK_RIGHT = sk(
    pts=[(0,4.6),(0.9,6.6),(1.7,4.1),(2.6,8.5),(3.3,7.3),(4.0,9.7),(4.7,8.6),(5.3,9.1),(5.9,8.0),(6.6,10.9),(7.4,9.8),(8.2,12.5)],
    W=880, H=360, zone=[(1.4,6.2),(4.6,3.6)],
    lines=[{"p":[(1.4,3.1),(6.9,3.1)],"c":RED,"dash":"8 7","w":2.2}],
    texts=[(4.2,2.4,"الستوب تحت الهيكل والزون — بأمان",TEAL_D,19)])

JTABLE = '''<table class="tblx" style="border-collapse:collapse;width:100%;background:#FBF9F5;border:1px solid #DED8CC">
<tr><th style="background:#1E627A;color:#fff;font-size:25px;font-weight:800;padding:12px">الصفقة</th><th style="background:#1E627A;color:#fff;font-size:25px;font-weight:800;padding:12px">السبب</th><th style="background:#1E627A;color:#fff;font-size:25px;font-weight:800;padding:12px">النتيجة</th><th style="background:#1E627A;color:#fff;font-size:25px;font-weight:800;padding:12px">الدرس</th></tr>
<tr><td style="font-size:25px;padding:11px;text-align:center;border-top:1px solid #EDE7DB;color:#5C6C73">الذهب</td><td style="font-size:25px;padding:11px;text-align:center;border-top:1px solid #EDE7DB;color:#0F2E3C;font-weight:800">ريتيست زون</td><td style="font-size:25px;padding:11px;text-align:center;border-top:1px solid #EDE7DB;color:#1E627A;font-weight:800">+2R</td><td style="font-size:25px;padding:11px;text-align:center;border-top:1px solid #EDE7DB;color:#5C6C73">الصبر دفع</td></tr>
<tr><td style="font-size:25px;padding:11px;text-align:center;border-top:1px solid #EDE7DB;color:#5C6C73">الناسداك</td><td style="font-size:25px;padding:11px;text-align:center;border-top:1px solid #EDE7DB;color:#D24B4B;font-weight:800">ملل</td><td style="font-size:25px;padding:11px;text-align:center;border-top:1px solid #EDE7DB;color:#D24B4B;font-weight:800">-1R</td><td style="font-size:25px;padding:11px;text-align:center;border-top:1px solid #EDE7DB;color:#5C6C73">مو سيت أب</td></tr>
<tr><td style="font-size:25px;padding:11px;text-align:center;border-top:1px solid #EDE7DB;color:#5C6C73">GBP/USD</td><td style="font-size:25px;padding:11px;text-align:center;border-top:1px solid #EDE7DB;color:#D24B4B;font-weight:800">ملل</td><td style="font-size:25px;padding:11px;text-align:center;border-top:1px solid #EDE7DB;color:#D24B4B;font-weight:800">-1R</td><td style="font-size:25px;padding:11px;text-align:center;border-top:1px solid #EDE7DB;color:#5C6C73">نفس الغلط!</td></tr>
</table>'''

# ================= 1) كاروسيل «انتقام» (نفسية) =================
ESC = escalation()
SL = [
 cover_slide("درس — نفسية التداول", "تبي تعوّض خسارتك…<br>بنفس الجلسة؟", "صفقة الانتقام — وقّفها قبل لا تكلفك حسابك", dkmap(escalation(700, 320))),
 problem(2, "الغضب فتح المنصة", "الفرصة ما نادتك — الضيقة اللي نادتك. وهذي ما تنسمى صفقة… <b class=\"tr\">هذا رد فعل</b>.", W(ESC)),
 numbered(3, "1", "أول علاماتها", None, rules([
    ("لوت مضاعف — «أرجّع خسارتي بضربة»", True),
    ("عكس الاتجاه… بس عشان تثبت رأيك", True),
    ("بدون ستوب — «ما بغلط مرتين»", True)]),
    "ثلاثتها قرارات حرارة — مالها علاقة بخطتك."),
 numbered(4, "2", "النهاية معروفة", "كل دخلة أكبر من اللي قبلها — <b>-1R تحولت -7R قبل نهاية اليوم</b>.", W(ESC), None),
 numbered(5, "3", "الفرامل", None, rules([
    ("بعد خسارتين… التداول وقف لباجر", False),
    ("دوّن شعورك أول — الكتابة تطفي الحرارة", False),
    ("حجم العقد ما يدري إنك خسران — خله ثابت", False)]), None),
 numbered(6, "4", "أجّل… لا تلغي", "الفكرة اللي طرأت بعد خسارتين — موعدها <b>الجلسة الجاية</b>. الفرص تتجدد كل يوم… الحساب ما يتجدد.", None,
    "التأجيل قوة — مو خوف."),
 quote_slide(7, "اللي تطارده ما يرجع…<br><span class=\"tt\">واللي بيدك يروح.</span>", "خسارة وحدة أرخص من ثلاث."),
 cta_slide(8, "انتقام", "دزه حق متداول يعوّض على حرارة", "بروتوكول فرملة صفقة الغضب كامل"),
]
build_carousel(SL, "صفقة الانتقام — Liquidity State", os.path.join(HERE, "car_intiqam.html"))

# ================= 2) كاروسيل «يوميات» (أساسية) =================
JB = jbars()
SL = [
 cover_slide("درس — أساسيات", "خساراتك…<br>تذكر أسبابها؟", "يوميات التداول — الدفتر اللي يفضح النمط", dkmap(jbars(720, 310))),
 problem(2, "خساراتك لها نمط", "بس ما تشوفه — دماغك يمسح التفاصيل بعد يومين. <b>الدفتر يمسك الخيط اللي يفلت منك</b>.", W(JB)),
 numbered(3, "1", "وقت الصفقة", None, rules([
    ("قبل ما تضغط: شنو حجتك بهالدخلة؟", False),
    ("عقب ما تطلع: النتيجة + حالتك النفسية", False),
    ("صورة للجارت وقت القرار — هذا الدليل", False)]), None),
 numbered(4, "2", "الجدول العملي", "جدول بسيط — وكل الشغل بعمود <b>السبب</b>:", JTABLE,
    "صفقتين حمر بنفس العمود؟ هذا النمط اللي تدور عليه."),
 numbered(5, "3", "جرد الأسبوع", None, rules([
    ("آخر الأسبوع: صنّف صفقاتك على السبب", False),
    ("عدّ اللي دخلتها بسيت أب حقيقي", False),
    ("سبب خسّرك ثلاث مرات؟ صار قانون بخطتك", False)]), None),
 numbered(6, "4", "خلها عادة", None, rules([
    ("مكان واحد ثابت — ورقة أو ملف، المهم يدوم", False),
    ("التدوين بنفس اليوم — باجر تنسى النص", False),
    ("قبل ما تفتح المنصة… طالع صفحة أمس", False)]), None),
 quote_slide(7, "أغلى درس عندك…<br><span class=\"tt\">مدفون بصفقاتك القديمة.</span>", "افتح الدفتر وتلقاه."),
 cta_slide(8, "يوميات", "وصّله حق رفيجك اللي ينسى خساراته", "نموذج دفتر التداول الجاهز"),
]
build_carousel(SL, "يوميات التداول — Liquidity State", os.path.join(HERE, "car_yawmiyat.html"))

# ================= 3) كاروسيل «ستوب» (مالية) =================
SL = [
 cover_slide("درس — إدارة المخاطر", "مين حاط ستوبك…<br>الهيكل ولا خوفك؟", "الستوب لوز — مكانه من الجارت… مو من مزاجك", dkmap(SK_WRONG.replace('width="880"','width="700"'))),
 problem(2, "الستوب القريب يطق أول", "تلزقه بسعر دخولك عشان ترتاح… وأول رجفة تطلعك. <b>السوق ما اصطادك — انت وقفت بطريقه</b>.", W(SK_WRONG)),
 numbered(3, "1", "الغلط: داخل التنفس", "لازق بآخر فتيل — بنص تنفس السعر الطبيعي.", W(SK_WRONG),
    "ذبذبة عادية تاخذه… والحركة تكمل حق الهدف وانت برا."),
 numbered(4, "2", "الصح: ورا الهيكل", "خلف <b>قاع الهيكل</b> أو خلف <b>الزون</b> — نقطة لو انلمست، السيناريو كله سقط.", W(SK_RIGHT),
    "تبي الستوب منفصل عن الضجيج… مو سابح فيه."),
 numbered(5, "3", "الترتيب الصح", None, rules([
    ("المسافة يحددها الجارت… مو مزاجك", False),
    ("اللوت ينحسب بعد المسافة — مو قبلها", False),
    ("المسافة بعيدة؟ صغّر العقد — المخاطرة ثابتة", False)]),
    "اللي يتحكم بحجم خسارتك اللوت… مو قرب الستوب."),
 numbered(6, "4", "الخطوط الحمر", None, rules([
    ("تزحلقه لما يقرب السعر — «فرصة أخيرة»", True),
    ("نفس النقاط لكل صفقة… أي كان الجارت", True),
    ("تشيله كامل وتقول «بيرد أكيد»", True)]), None),
 quote_slide(7, "الستوب القريب…<br><span class=\"tt\">راحة للخاطر ونزيف للحساب.</span>", "حطه وين السيناريو يسقط."),
 cta_slide(8, "ستوب", "دزه حق واحد ستوبه دايم أول الضحايا", "خريطة مكان الستوب الصح كاملة"),
]
build_carousel(SL, "الستوب لوز — Liquidity State", os.path.join(HERE, "car_stop.html"))
print("built 3 carousels (run2)")
