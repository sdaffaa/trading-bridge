# -*- coding: utf-8 -*-
# تشغيلة المصنع 1 (2026-08-03) — 3 كاروسيلات: هدوء (نفسية) · توقيت (أساسية) · ريسك (مالية)
import os
from car_common import (CW, brandbar, counter, swipe, dots, eyebrow, cover_slide, quote_slide,
                        cta_slide, sk, dkmap, build_carousel, htext, hend,
                        INK, TEAL, TEAL_D, TEAL_L, RED, GREY, MUTE, CREAM)

HERE = os.path.dirname(os.path.abspath(__file__))

# ================= المرئيات المخصصة =================
def eq_compare(W=880, H=400):
    """منحنيا حساب: أوفر تريدنق ينزل vs 3 صفقات يصعد."""
    over = [(0,10),(0.7,10.6),(1.3,9.5),(2.0,10.1),(2.6,8.8),(3.3,9.3),(4.0,7.9),(4.7,8.5),
            (5.4,7.0),(6.1,7.6),(6.8,6.1),(7.5,6.6),(8.2,5.0),(8.9,5.4),(9.6,4.2)]
    calm = [(0,10),(1.2,10.4),(2.4,11.3),(3.6,11.0),(4.8,12.1),(6.0,12.9),(7.2,12.6),(8.4,13.8),(9.6,14.6)]
    x0,x1,y0,y1 = 0,9.6,3.4,15.4
    mx = lambda v: 24+(v-x0)/(x1-x0)*(W-48); my = lambda v: 18+(y1-v)/(y1-y0)*(H-54)
    s = [f'<svg viewBox="0 0 {W} {H}" width="{W}" height="{H}" xmlns="http://www.w3.org/2000/svg">']
    s.append(f'<line x1="24" y1="{my(10):.1f}" x2="{W-24}" y2="{my(10):.1f}" stroke="{MUTE}" stroke-width="1.2" stroke-dasharray="4 6" opacity="0.6"/>')
    for pts,col,wd in ((over,RED,2.6),(calm,TEAL_D,3.0)):
        p = " ".join(f"{mx(a):.1f},{my(b):.1f}" for a,b in pts)
        s.append(f'<polyline points="{p}" fill="none" stroke="{col}" stroke-width="{wd}" stroke-linecap="round" stroke-linejoin="round"/>')
    s.append(hend(mx(9.6), my(4.2), RED)); s.append(hend(mx(9.6), my(14.6), TEAL_D))
    s.append(htext(mx(7.0), my(4.6), "15 صفقة باليوم", RED, 19))
    s.append(htext(mx(6.9), my(15.15), "3 صفقات مدروسة", TEAL_D, 19))
    s.append(htext(mx(0.9), my(9.3), "نفس الحساب", MUTE, 15))
    return "".join(s)+"</svg>"

def timeline_kw(W=880, H=380):
    """خط اليوم بتوقيت الكويت مع صناديق الجلسات."""
    mx = lambda h: 30+(h/24)*(W-60)
    bar_y, bar_h = H*0.52, 46
    s = [f'<svg viewBox="0 0 {W} {H}" width="{W}" height="{H}" xmlns="http://www.w3.org/2000/svg">']
    s.append(f'<rect x="30" y="{bar_y:.0f}" width="{W-60}" height="{bar_h}" fill="rgba(15,46,60,0.06)"/>')
    for h in range(0,25,4):
        s.append(f'<line x1="{mx(h):.1f}" y1="{bar_y-6:.0f}" x2="{mx(h):.1f}" y2="{bar_y+bar_h+6:.0f}" stroke="{MUTE}" stroke-width="1" opacity="0.5"/>')
        s.append(f'<text x="{mx(h):.1f}" y="{bar_y+bar_h+34:.0f}" fill="{MUTE}" font-size="17" font-family="Tajawal" font-weight="700" font-style="italic" text-anchor="middle">{h:02d}</text>')
    boxes = [(3,10,"آسيا ‎03–10‎ — رينج",TEAL,0.16,-96),(9,12,"كيل زون لندن ‎09–12‎",TEAL_D,0.42,-52),(14,17,"كيل زون نيويورك ‎14–17‎",TEAL_D,0.30,-96)]
    for h0,h1,lab,col,op,dy in boxes:
        s.append(f'<rect x="{mx(h0):.1f}" y="{bar_y:.0f}" width="{mx(h1)-mx(h0):.1f}" height="{bar_h}" fill="{col}" opacity="{op}"/>')
        s.append(f'<rect x="{mx(h0):.1f}" y="{bar_y:.0f}" width="{mx(h1)-mx(h0):.1f}" height="{bar_h}" fill="none" stroke="{TEAL_D}" stroke-width="1"/>')
        s.append(f'<line x1="{(mx(h0)+mx(h1))/2:.1f}" y1="{bar_y+dy+10:.0f}" x2="{(mx(h0)+mx(h1))/2:.1f}" y2="{bar_y-4:.0f}" stroke="{TEAL_D}" stroke-width="1" opacity="0.5"/>')
        s.append(htext((mx(h0)+mx(h1))/2, bar_y+dy, lab, TEAL_D, 19))
    s.append(htext(W/2, H-14, "الساعات بتوقيت الكويت — بالشتاء تتأخر لندن ونيويورك ساعة", MUTE, 16))
    return "".join(s)+"</svg>"

def rr_diagram(W=880, H=400):
    """سلم الدخول/الستوب/الهدف بنسبة 1:2 — المسافات مرسومة بدقة النسبة."""
    e, st, tg = 8.0, 6.5, 11.0     # 1R = 1.5 ; 2R = 3.0
    y0,y1 = 5.4, 12.2
    my = lambda v: 20+(y1-v)/(y1-y0)*(H-56)
    xL, xR = 90, W-40
    s = [f'<svg viewBox="0 0 {W} {H}" width="{W}" height="{H}" xmlns="http://www.w3.org/2000/svg">']
    zone_y = my(e);
    for val,col,lab in ((tg,TEAL_D,"الهدف"),(e,INK,"الدخول"),(st,RED,"الستوب")):
        s.append(f'<line x1="{xL}" y1="{my(val):.1f}" x2="{xR}" y2="{my(val):.1f}" stroke="{col}" stroke-width="1.8"/>')
        s.append(hend(xR, my(val), col))
        s.append(htext(xL-42, my(val)+7, lab, col, 19))
    bx = W*0.30
    s.append(f'<rect x="{bx-16:.0f}" y="{my(e):.1f}" width="32" height="{my(st)-my(e):.1f}" fill="{RED}" opacity="0.18"/>')
    s.append(f'<rect x="{bx-16:.0f}" y="{my(tg):.1f}" width="32" height="{my(e)-my(tg):.1f}" fill="{TEAL}" opacity="0.20"/>')
    s.append(htext(bx+58, (my(e)+my(st))/2+7, "1R مخاطرة", RED, 19))
    s.append(htext(bx+58, (my(e)+my(tg))/2+7, "2R ربح", TEAL_D, 19))
    s.append(htext(W*0.68, my(tg)-16, "RR = 1:2", TEAL_D, 24))
    return "".join(s)+"</svg>"

def bars10(W=880, H=380):
    """عشر صفقات: 5 خسائر -1R و5 أرباح +2R = ‏+5R صافي."""
    seq = [-1,+2,-1,-1,+2,+2,-1,+2,-1,+2]
    mx = lambda i: 60+i*(W-110)/9
    zero = H*0.62; unit = H*0.16
    s = [f'<svg viewBox="0 0 {W} {H}" width="{W}" height="{H}" xmlns="http://www.w3.org/2000/svg">']
    s.append(f'<line x1="40" y1="{zero:.0f}" x2="{W-30}" y2="{zero:.0f}" stroke="{MUTE}" stroke-width="1.4"/>')
    for i,v in enumerate(seq):
        col = TEAL_D if v>0 else RED; h = abs(v)*unit
        y = zero-h if v>0 else zero
        s.append(f'<rect x="{mx(i)-17:.1f}" y="{y:.1f}" width="34" height="{h:.1f}" fill="{col}" opacity="0.85" rx="1"/>')
        s.append(htext(mx(i), zero+(28 if v>0 else h+28), f'{"+" if v>0 else ""}{v}R', col, 16))
    s.append(htext(W*0.5, H-12, "5 خسائر × 1R − ‏5 أرباح × 2R ← الصافي +5R", INK, 20))
    return "".join(s)+"</svg>"

def numbered(idx, num, ttl, lead, inner, note, total=8):
    leadh = f'<p class="lead">{lead}</p>' if lead else ""
    noteh = f'<div class="note">{note}</div>' if note else ""
    return f'''<div class="slide" {CW}>
  {counter(idx, total)}
  {brandbar(True)}
  <div class="cont">
    <div class="numrow"><span class="num">{num}</span><h2 class="ttl">{ttl}</h2></div>
    {leadh}{inner}{noteh}
  </div>
  {swipe()}{dots(idx, total)}
</div>'''

def problem(idx, ttl, lead, inner, total=8):
    return f'''<div class="slide" {CW}>
  {counter(idx, total)}
  {brandbar(True)}
  <div class="cont">
    {eyebrow("المشكلة")}
    <h2 class="ttl big">{ttl}</h2>
    <p class="lead">{lead}</p>
    {inner}
  </div>
  {swipe()}{dots(idx, total)}
</div>'''

def rules(rows):
    return "".join(f'<div class="rulerow"><span class="rn{" x" if bad else ""}">{"✗" if bad else "✓"}</span><p>{t}</p></div>' for t, bad in rows)

W = lambda svg: f'<div class="chartwrap">{svg}</div>'

# ================= 1) كاروسيل «هدوء» — الأوفر تريدنق (نفسية) =================
EQ = eq_compare()
SL = [
 cover_slide("درس — نفسية التداول", "چم صفقة<br>خسرتها من الملل؟", "الأوفر تريدنق — العدو الصامت لحسابك", dkmap(eq_compare(680, 330))),
 problem(2, "المشكلة مو استراتيجيتك", "نفس الاستراتيجية، نفس السوق — حساب يكبر وحساب ينحرق. الفرق؟ <b>عدد الصفقات</b>.", W(EQ)),
 numbered(3, "1", "ليش تكثر الصفقات؟", None, rules([
    ("الملل — تدخل عشان «في حركة»", True),
    ("الانتقام — تبي ترد خسارتك بسرعة", True),
    ("الخوف تفوتك الحركة — تلحق السوق", True)]),
    "ثلاثتهم مشاعر… ولا وحدة منهم «سيت أب»."),
 numbered(4, "2", "شنو يصير لحسابك؟", "كل صفقة زايدة تدفع ثمنها مرتين: <b>سبريد وعمولة</b> تاكل الربح، و<b>قرار متعب</b> يقلل تركيزك للصفقة الجاية.", W(sk(
    pts=[(0,10),(1,9.2),(2,9.8),(3,8.6),(4,9.1),(5,7.8),(6,8.2),(7,6.8),(8,7.1),(9,5.9)],
    W=880,H=330, texts=[(4.5,10.9,"كل صفقة زايدة ← قرار أضعف",RED,19)]), ), None),
 numbered(5, "3", "قاعدة الثلاث صفقات", None, rules([
    ("حدد 3 فرص باليوم — الأفضل بس", False),
    ("خلصت الثلاث؟ صكّر المنصة", False),
    ("ما جا سيت أب واضح؟ صفر صفقات = يوم ناجح", False)]),
    "القاعدة: الجودة تربح على الكمية — دايمًا."),
 numbered(6, "4", "روتينك الجديد", None, rules([
    ("قبل الجلسة: حدد زوناتك وانتظرها", False),
    ("بعد كل صفقة: سجلها بيومياتك وقيّمها", False),
    ("آخر اليوم: راجع — صفقاتك ولا مشاعرك؟", False)]), None),
 quote_slide(7, "أحيانًا أفضل صفقة…<br><span class=\"tt\">اللي ما دخلتها.</span>", "السوق يفتح بكرة بعد — حسابك لازم يكون موجود."),
 cta_slide(8, "هدوء", "شاركه مع متداول يعيش على الجارت", "ملف قاعدة الثلاث صفقات كامل"),
]
build_carousel(SL, "الأوفر تريدنق — Liquidity State", os.path.join(HERE, "car_hudou.html"))

# ================= 2) كاروسيل «توقيت» — الكيل زونز (أساسية) =================
TL = timeline_kw()
SL = [
 cover_slide("درس — أساسيات", "ليش تتداول<br>وقت السوق نايم؟", "الكيل زونز بتوقيت الكويت — مواعيد الحركة الحقيقية", dkmap(timeline_kw(720, 330))),
 problem(2, "السوق له مواعيد", "تفتح الجارت الظهر، السعر واقف، تدخل من الملل — <b>ويطق الستوب</b>. المشكلة مو التحليل… المشكلة <b>الساعة</b>.", W(TL)),
 numbered(3, "1", "آسيا ‎03:00–10:00‎", "السوق يبني <b>رينج ضيق</b> — يجمع سيولة فوقه وتحته. هذا مو وقت دخول… هذا وقت <b>تحديد</b>.", None, "حدد قمة وقاع رينج آسيا — هم مفاتيح اليوم."),
 numbered(4, "2", "كيل زون لندن 09:00–12:00", "أول اندفاع حقيقي باليوم. غالبًا يبدأ <b>بسحب سيولة</b> من طرف رينج آسيا… وبعدها الحركة الصادقة بالاتجاه الثاني.", None, "لا تدخل بأول حركة — خلها تسحب السيولة أول."),
 numbered(5, "3", "كيل زون نيويورك 14:00–17:00", "الحركة الثانية: يا تكمل موجة لندن، يا <b>تعكسها</b>. أخطر وقت وأغناه — خصوصًا مع الأخبار الأمريكية.", None, "شوف وين لندن وقفت — نيويورك تتعامل مع مستوياتها."),
 numbered(6, "4", "جدولك اليومي", None, rules([
    ("09:00 — راجع رينج آسيا وحدد زوناتك", False),
    ("‎09:00–12:00‎ و‎14:00–17:00‎ — وقت التنفيذ", False),
    ("باقي اليوم — مراجعة ويوميات… مو تداول", False)]),
    "بالشتاء تتأخر لندن ونيويورك ساعة — عدّل جدولك."),
 quote_slide(7, "التداول مواعيد…<br><span class=\"tt\">مو دوام كامل.</span>", "ساعتين صح أحسن من ثمان ساعات مراقبة."),
 cta_slide(8, "توقيت", "شاركه مع متداول ساهر على الجارت", "جدول الكيل زونز كامل بتوقيت الكويت"),
]
build_carousel(SL, "الكيل زونز بتوقيت الكويت — Liquidity State", os.path.join(HERE, "car_tawqit.html"))

# ================= 3) كاروسيل «ريسك» — الريسك ريوورد (مالية) =================
RR = rr_diagram(); BARS = bars10()
SL = [
 cover_slide("درس — إدارة المخاطر", "شلون تربح وانت<br>خسران نص صفقاتك؟", "الريسك ريوورد — الحسبة اللي قبل أي دخول", dkmap(rr_diagram(700, 320))),
 problem(2, "الكل يدور «نسبة نجاح»", "تحسب صفقاتك الرابحة وتنسى الأهم: <b>چم تربح لما تصيب، وچم تخسر لما تغلط؟</b> هذي اهي الحسبة.", W(RR)),
 numbered(3, "1", "شنو الريسك ريوورد؟", "المسافة من دخولك للستوب = <b>1R</b>. الهدف لازم يكون <b>2R أو أكثر</b> — يعني كل غلطة تكلفك وحدة، وكل إصابة تدفع لك ثنتين.", W(RR), None),
 numbered(4, "2", "حسبة العشر صفقات", "خسرت 5 وربحت 5 — بنسبة 1:2 طلعت <b>رابح +5R</b>. النص اللي خسرته ما أثر… لأن الحسبة كانت صح من البداية.", W(BARS), None),
 numbered(5, "3", "وين يجي الخلل؟", None, rules([
    ("توسّع الستوب بعد الدخول — كبّرت الـ1R", True),
    ("تقرّب الهدف بالخوف — صغّرت الـ2R", True),
    ("تطلع يدوي قبل الهدف — كسرت الحسبة كلها", True)]),
    "القاعدة: الحسبة تنحدد <b>قبل</b> الدخول — وما تنلمس بعده."),
 numbered(6, "4", "جدول النجاة", "كل ما كبر الريوورد… قلت نسبة الإصابة اللي تحتاجها عشان تطلع متعادل:", '''<table class="tblx" style="border-collapse:collapse;width:100%;background:#FBF9F5;border:1px solid #DED8CC">
   <tr><th style="background:#1E627A;color:#fff;font-size:27px;font-weight:800;padding:14px">النسبة</th><th style="background:#1E627A;color:#fff;font-size:27px;font-weight:800;padding:14px">تحتاج تصيب</th></tr>
   <tr><td style="font-size:28px;font-weight:700;color:#5C6C73;padding:13px;text-align:center;border-top:1px solid #EDE7DB">1 : 1</td><td style="font-size:28px;padding:13px;text-align:center;border-top:1px solid #EDE7DB;color:#5C6C73"><b style="color:#0F2E3C">50%</b> من صفقاتك</td></tr>
   <tr><td style="font-size:28px;font-weight:700;color:#5C6C73;padding:13px;text-align:center;border-top:1px solid #EDE7DB">1 : 2</td><td style="font-size:28px;padding:13px;text-align:center;border-top:1px solid #EDE7DB;color:#5C6C73"><b style="color:#0F2E3C">34%</b> بس</td></tr>
   <tr><td style="font-size:28px;font-weight:700;color:#5C6C73;padding:13px;text-align:center;border-top:1px solid #EDE7DB">1 : 3</td><td style="font-size:28px;padding:13px;text-align:center;border-top:1px solid #EDE7DB;color:#5C6C73"><b style="color:#0F2E3C">25%</b> بس</td></tr>
 </table>''', None),
 quote_slide(7, "مو لازم تصيب وايد…<br><span class=\"tt\">يكفي تخسر صح.</span>", "الحسبة قبل الدخول — والالتزام بعدها."),
 cta_slide(8, "ريسك", "شاركه مع متداول يطارد نسبة نجاح 90%", "ملف حسبة الريسك ريوورد كامل"),
]
build_carousel(SL, "الريسك ريوورد — Liquidity State", os.path.join(HERE, "car_risk.html"))
print("built 3 carousels")
