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
 cover_slide("درس — نفسية التداول", "أخطر صفقة…<br>اللي بعد الخسارة", "صفقة الانتقام — شلون توقفها قبل ما تبدأ", dkmap(escalation(700, 320))),
 problem(2, "تخسر… وتفتح المنصة", "مو عشان فرصة جديدة — عشان ترد الصداع. هذي مو صفقة… <b class=\"tr\">هذا انتقام</b>.", W(ESC)),
 numbered(3, "1", "شلون تبدأ؟", None, rules([
    ("تكبّر اللوت — «أعوّض أسرع»", True),
    ("تدخل عكس السوق بعناد", True),
    ("تلغي الستوب — «أكيد بيرجع»", True)]),
    "ثلاث قرارات… ولا واحد منهم من خطتك."),
 numbered(4, "2", "وين توصلك؟", "الغضب يضاعف الحجم، والحجم يضاعف الخسارة — <b>-1R صارت -7R بجلسة وحدة</b>.", W(ESC), None),
 numbered(5, "3", "شلون توقفها؟", None, rules([
    ("خسرتين ورا بعض؟ صكّر المنصة اليوم", False),
    ("اكتب الخسارة بيومياتك قبل أي صفقة", False),
    ("اللوت ثابت — ما يتغير بعد خسارة", False)]), None),
 numbered(6, "4", "قاعدة الجلسة الجديدة", "أي صفقة تجي ببالك بعد خسرتين — تنتظر <b>جلسة جديدة</b>. السوق ما يهرب… حسابك اللي يهرب.", None,
    "الانتظار مو ضعف — الانتظار خطة."),
 quote_slide(7, "السوق ما ياخذ منك…<br><span class=\"tt\">انت اللي تعطيه.</span>", "الانتقام قرار — والقرار بيدك."),
 cta_slide(8, "انتقام", "شاركه مع متداول يطارد خسارته", "ملف إيقاف صفقة الانتقام كامل"),
]
build_carousel(SL, "صفقة الانتقام — Liquidity State", os.path.join(HERE, "car_intiqam.html"))

# ================= 2) كاروسيل «يوميات» (أساسية) =================
JB = jbars()
SL = [
 cover_slide("درس — أساسيات", "ليش تعيد<br>نفس الغلط؟", "يوميات التداول — السجل اللي يوريك غلطك المتكرر", dkmap(jbars(720, 310))),
 problem(2, "كل خسارة لها سبب", "بس انت ما تشوفه — لأنك ما تسجل. الذاكرة تنسى… <b>والسجل ما ينسى</b>.", W(JB)),
 numbered(3, "1", "شنو تسجل؟", None, rules([
    ("قبل الدخول: السبب — ليش هالصفقة؟", False),
    ("بعد الخروج: النتيجة وشعورك وقتها", False),
    ("سكرين شوت للجارت لحظة الدخول", False)]), None),
 numbered(4, "2", "شكل السجل", "أربع خانات تكفي — والعبرة بخانة <b>السبب</b>:", JTABLE,
    "شوف الصفقتين الحمر — نفس السبب. هذا اللي تدور عليه."),
 numbered(5, "3", "المراجعة الأسبوعية", None, rules([
    ("كل جمعة: افرز صفقاتك حسب السبب", False),
    ("احسب: چم وحدة كانت سيت أب صح؟", False),
    ("غلط تكرر 3 مرات = قاعدة جديدة بخطتك", False)]), None),
 numbered(6, "4", "عاداتك", None, rules([
    ("دفتر أو ملف — المهم مكان واحد ثابت", False),
    ("سجل قبل ما تنام — التفاصيل تطير", False),
    ("راجع سجلك قبل ما تفتح الجلسة الجاية", False)]), None),
 quote_slide(7, "حسابك يتحسن…<br><span class=\"tt\">يوم تقرأ أخطاءك.</span>", "اللي ما يسجل — يعيد."),
 cta_slide(8, "يوميات", "شاركه مع متداول يعيد نفس الغلط", "قالب يوميات التداول جاهز"),
]
build_carousel(SL, "يوميات التداول — Liquidity State", os.path.join(HERE, "car_yawmiyat.html"))

# ================= 3) كاروسيل «ستوب» (مالية) =================
SL = [
 cover_slide("درس — إدارة المخاطر", "ليش ستوبك ينطق…<br>والسعر يكمل؟", "الستوب لوز — وين يتحط صح ووين يتحط غلط", dkmap(SK_WRONG.replace('width="880"','width="700"'))),
 problem(2, "الستوب مو رقم عشوائي", "تحطه قريب عشان «تقلل الخسارة»… فيطق بأي ذبذبة. المشكلة مو السوق — <b>مكان الستوب</b>.", W(SK_WRONG)),
 numbered(3, "1", "الغلط: بالضجيج", "تحت آخر شمعة أو آخر قاع صغير — داخل حركة السوق الطبيعية.", W(SK_WRONG),
    "فتيل واحد يكفي يطقه — وبعدها السعر يروح حق هدفك بدونك."),
 numbered(4, "2", "الصح: تحت الهيكل", "تحت <b>قاع الهيكل</b> أو تحت <b>الزون</b> — المكان اللي لو وصله السعر، فكرتك فعلًا غلطت.", W(SK_RIGHT),
    "الستوب حماية من فشل الفكرة — مو من ذبذبة السعر."),
 numbered(5, "3", "القياس الصح", None, rules([
    ("حدد مكان الستوب أول — من الهيكل", False),
    ("بعدين احسب اللوت على مسافته", False),
    ("ستوب أبعد = لوت أصغر — نفس المخاطرة", False)]),
    "المخاطرة تجي من اللوت… مو من مسافة الستوب."),
 numbered(6, "4", "ممنوعات", None, rules([
    ("توسيعه بعد الدخول — «شوي بس»", True),
    ("رقم ثابت لكل الصفقات بدون نظر للهيكل", True),
    ("إلغاؤه لما يقرب السعر — «أكيد يرتد»", True)]), None),
 quote_slide(7, "الستوب الصح…<br><span class=\"tt\">مكان يثبت إن فكرتك غلطت.</span>", "مو مكان يخوفك السوق منه."),
 cta_slide(8, "ستوب", "شاركه مع متداول ينطق ستوبه كل يوم", "دليل مكان الستوب الصح كامل"),
]
build_carousel(SL, "الستوب لوز — Liquidity State", os.path.join(HERE, "car_stop.html"))
print("built 3 carousels (run2)")
