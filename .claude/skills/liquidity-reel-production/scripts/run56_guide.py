# -*- coding: utf-8 -*-
"""تشغيلة ٥٦ — قائمة فحص «ستوب»: الملف الذي يَعِد به نداء الفعل.

البريف يقول: «إذا لم تكن قائمة الفحص جاهزة للتسليم، استبدل CTA الأساسي».
فبدل استبدال النداء، صُنِعت القائمة — أربع صفحات بهوية الدفعة نفسها،
وأرقامها من نافذة الريل نفسها لا من أمثلة عامّة.

    python3 run56_guide.py
"""
import glob, os

import img2pdf
from PIL import Image

import run55_page as P
from run55_kit import num, dnum
from run56_stop import plan, NAME, TF, RANGE_A, RANGE_Z
import car_render

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out56")

p = plan()
B = p["B"]

# القائمة كلها اشتراطات قابلة للفحص قبل الضغط على الزرّ — لا نصائح عامّة.
CHECKS_A = [
    "هل النطاق واضح؟ آخر ست شمعات أغلقت داخل منطقة القيمة.",
    "هل حدود البروفايل معلَنة؟ اكتب تاريخ بدايته ونهايته على الشارت.",
    "هل تعرف VAH و POC و VAL بالأرقام لا بالنظر؟",
]
CHECKS_B = [
    "الخروج فوق VAH: هل أغلقت شمعة فوقه — أم مجرّد ذيل تجاوزه؟",
    "العودة: هل أغلق السعر <b>داخل</b> القيمة؟ الذيل وحده لا يكفي.",
    "الوقف: فوق قمّة الخروج + هامش تذبذب/سبريد — لا ملاصقاً للفتيل.",
    "الهدف: POC أولاً ثم VAL — والR يُحسب قبل الدخول لا بعده.",
    "لو الوقف أوسع من مخاطرتك المسموحة: قلّل الحجم أو اترك الصفقة.",
]


def pages():
    # لا أيقونات جاهزة على الغلاف (§٧ يمنعها) — المستويات الثلاثة نفسها
    # هي العنصر البصري.
    hero = (
        '<svg viewBox="0 0 620 230" width="620" height="230" '
        'xmlns="http://www.w3.org/2000/svg">'
        '<line x1="40" y1="42" x2="580" y2="42" stroke="#20939E" '
        'stroke-width="3"/><text x="580" y="30" fill="#20939E" font-size="26" '
        'font-weight="700" font-family="PlexAr" text-anchor="start" '
        'direction="rtl">VAH</text>'
        '<line x1="40" y1="118" x2="580" y2="118" stroke="#D9A441" '
        'stroke-width="3"/><text x="580" y="106" fill="#D9A441" font-size="26" '
        'font-weight="700" font-family="PlexAr" text-anchor="start" '
        'direction="rtl">POC</text>'
        '<line x1="40" y1="194" x2="580" y2="194" stroke="#20939E" '
        'stroke-width="3" stroke-dasharray="9 6"/><text x="580" y="182" '
        'fill="#20939E" font-size="26" font-weight="700" font-family="PlexAr" '
        'text-anchor="start" direction="rtl">VAL</text></svg>')
    s1 = P.cover(["قائمة فحص", "الستوب"],
                 'وين يروح الستوب؟<br><b>خمس خانات</b> قبل الدخول.',
                 'قائمة الفحص المرافقة لريل «ستوب» — بأرقام النافذة نفسها، '
                 'لا بأمثلة عامّة.',
                 hero, f'{NAME} · {TF} · {dnum(RANGE_A)} → {dnum(RANGE_Z)}')

    s2 = P.page(2, "قبل ما ترسم أي شيء", "أولاً: هل عندك نطاق أصلاً؟",
                'منطقة القيمة تُقرأ داخل نطاق. بلا نطاق واضح، الأرقام الثلاثة '
                '<b>تفقد معناها</b>.',
                P.checks(CHECKS_A),
                'حدود البروفايل تُعلَن دائماً — بروفايل بلا مدى معلَن رقمٌ بلا مرجع.')

    s3 = P.page(3, "لحظة القرار", "خمس خانات لا تُتجاوز",
                'كل خانة سؤال بجواب <b>نعم أو لا</b> — لا تقدير ولا انطباع.',
                P.checks(CHECKS_B))

    s4 = P.page(4, "مثال مقيس", "نفس القائمة على نافذة الريل",
                f'{NAME} · {TF} — والأرقام من الشموع لا من الذاكرة.',
                P.plan_table([
                    ("نطاق البروفايل",
                     f'{dnum(RANGE_A[5:])} → {dnum(RANGE_Z[5:])}', "ar"),
                    ("VAH · سقف القيمة", num(p["vah"]), "t"),
                    ("POC · أكثر سعر تداولاً", num(p["poc"]), ""),
                    ("VAL · قاع القيمة", num(p["val"]), "t"),
                    ("قمّة الخروج", num(p["ex_high"]), ""),
                    ("الدخول — إغلاق داخل القيمة", num(p["ent"]), "t"),
                    ("الوقف — القمّة + ⁦0.15⁩٪", num(p["sl"]), "r"),
                    ("الهدف ١ — POC", f'⁦{p["r1"]:.2f}⁩R', ""),
                    ("الهدف ٢ — VAL", f'⁦{p["r2"]:.2f}⁩R', ""),
                ]),
                'حالة واحدة على نافذة واحدة — <b>تعليمية لا توصية</b>، '
                'ولا تُقرأ كقاعدة إحصائية.', tone="warn")
    return [s1, s2, s3, s4]


if __name__ == "__main__":
    P.TOTAL = 4          # قبل بناء الصفحات: العدّاد يُقرأ وقت التركيب
    sl = pages()
    html = os.path.join(OUT, "guide_stop.html")
    P.build(sl, "قائمة فحص الستوب", html)
    d = os.path.join(OUT, "guide_png")
    car_render.render(html, d)
    pngs = []
    for f in sorted(glob.glob(os.path.join(d, "*.png"))):
        im = Image.open(f).convert("RGB").resize((1080, 1350), Image.LANCZOS)
        g = f.replace(".png", "_1080.png")
        im.save(g, "PNG", optimize=True)
        pngs.append(g)
    dst = os.path.join(OUT, "LiquidityState_checklist_stop.pdf")
    lay = img2pdf.get_layout_fun((img2pdf.px_to_pt(1080, 72),
                                  img2pdf.px_to_pt(1350, 72)))
    open(dst, "wb").write(img2pdf.convert(
        pngs, layout_fun=lay, title="Liquidity State — قائمة فحص الستوب",
        author="Liquidity State",
        subject="VAH · POC · VAL — أين يوضع وقف الخسارة"))
    print("✓", dst, len(pngs), "صفحات")
