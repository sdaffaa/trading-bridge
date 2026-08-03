# -*- coding: utf-8 -*-
# تشغيلة المصنع 2 — الأدلة الخمسة: كسر، سيولة (الريلان) + انتقام، يوميات، ستوب (الكاروسيلات)
import json, os
from reel_build import INK, TEAL, TEAL_D, RED, chart, htext, hend
from car_common import dkmap
from guide_build import build_guide
from run2_carousels import escalation, jbars, SK_WRONG, SK_RIGHT, JTABLE

HERE = os.path.dirname(os.path.abspath(__file__))
C = json.load(open(os.path.join(HERE, "sheet_candidates.json")))

def _base(w, Wd, H):
    ymin = min(c["l"] for c in w); ymax = max(c["h"] for c in w)
    pad = (ymax - ymin) * 0.07; ymin -= pad * 1.5; ymax += pad
    return chart(w, Wd, H, ymin, ymax, grid=4, pl=10, pr=14, pt=16, pb=12, body=0.6)

def kasr_static(Wd=880, H=430):
    w = C[10]["w"]; I1, POKE, IOB, IR, RB = 10, 15, 8, 20, 23
    EQ = w[I1]["h"]; ZT, ZB = w[IOB]["o"], w[IOB]["l"]
    svg, x, y, slot = _base(w, Wd, H)
    svg += f'<line x1="{x(I1):.1f}" y1="{y(EQ):.1f}" x2="{x(RB)+slot*0.55:.1f}" y2="{y(EQ):.1f}" stroke="{INK}" stroke-width="1.7"/>'
    svg += hend(x(RB)+slot*0.55, y(EQ), INK)
    svg += htext(x(I1)+slot*1.8, y(EQ)-12, "المستوى", INK, 16)
    r = 11
    svg += (f'<line x1="{x(POKE)-r:.1f}" y1="{y(w[POKE]["h"])-r:.1f}" x2="{x(POKE)+r:.1f}" y2="{y(w[POKE]["h"])+r:.1f}" stroke="{RED}" stroke-width="3.4" stroke-linecap="round"/>'
            f'<line x1="{x(POKE)-r:.1f}" y1="{y(w[POKE]["h"])+r:.1f}" x2="{x(POKE)+r:.1f}" y2="{y(w[POKE]["h"])-r:.1f}" stroke="{RED}" stroke-width="3.4" stroke-linecap="round"/>')
    svg += htext(x(POKE)-slot*0.3, y(w[POKE]["h"])-30, "وهمي — فتيل", RED, 17)
    zx0 = x(IOB)-slot*0.5; zx1 = x(RB)+slot*0.5
    svg += (f'<rect x="{zx0:.1f}" y="{y(ZT):.1f}" width="{zx1-zx0:.1f}" height="{y(ZB)-y(ZT):.1f}" fill="{TEAL}" style="opacity:0.16"/>'
            f'<rect x="{zx0:.1f}" y="{y(ZT):.1f}" width="{zx1-zx0:.1f}" height="{y(ZB)-y(ZT):.1f}" fill="none" stroke="{TEAL_D}" stroke-width="1"/>')
    svg += htext((zx0+zx1)/2, y(ZB)+22, "زون الطلب", TEAL_D, 16)
    svg += htext(x(RB)-slot*0.2, y(max(c["h"] for c in w[RB:]))-14, "حقيقي — جسم", TEAL_D, 17)
    return svg + "</svg>"

def suyula_static(Wd=880, H=430):
    w = C[11]["w"]; I1, I2, IPDL, IOB, IR, RB = 19, 22, 20, 14, 26, 28
    EQ = w[I1]["h"]; PDL = w[IPDL]["l"]; ZT, ZB = w[IOB]["o"], w[IOB]["l"]
    svg, x, y, slot = _base(w, Wd, H)
    SWP = next(j for j in range(I2+1, len(w)) if w[j]["l"] < PDL)
    svg += f'<line x1="{x(I1)-slot*0.6:.1f}" y1="{y(EQ):.1f}" x2="{x(RB)+slot*0.55:.1f}" y2="{y(EQ):.1f}" stroke="{RED}" stroke-width="1.7"/>'
    svg += htext(x((I1+I2)/2), y(max(EQ, w[I2]["h"]))-14, "سيولة القمم", RED, 17)
    svg += f'<line x1="{x(IPDL)-slot*1.2:.1f}" y1="{y(PDL):.1f}" x2="{x(SWP)+slot*0.6:.1f}" y2="{y(PDL):.1f}" stroke="{INK}" stroke-width="1.5" stroke-dasharray="6 5"/>'
    svg += htext(x(IPDL)+slot*0.4, y(PDL)+24, "سيولة القاع (PDL)", INK, 15)
    zx0 = x(IOB)-slot*0.5; zx1 = x(min(IR+3, len(w)-1))+slot*0.5
    svg += (f'<rect x="{zx0:.1f}" y="{y(ZT):.1f}" width="{zx1-zx0:.1f}" height="{y(ZB)-y(ZT):.1f}" fill="{TEAL}" style="opacity:0.16"/>'
            f'<rect x="{zx0:.1f}" y="{y(ZT):.1f}" width="{zx1-zx0:.1f}" height="{y(ZB)-y(ZT):.1f}" fill="none" stroke="{TEAL_D}" stroke-width="1"/>')
    svg += htext((zx0+zx1)/2, y(ZB)+22, "زون الطلب", TEAL_D, 16)
    svg += f'<circle cx="{x(IR):.1f}" cy="{y(w[IR]["l"]):.1f}" r="11" fill="none" stroke="{RED}" stroke-width="2.4"/>'
    return svg + "</svg>"

G_KASR = dict(
  eyebrow="دليل — هيكل السوق", title="الكسر الحقيقي<br>vs الوهمي", keyword="كسر",
  subtitle="فتيل بلا إغلاق… مجرد زيارة", hero=dkmap(kasr_static(760, 360)),
  pages=[
    dict(title="المستوى انلمس مرتين",
         lead="السعر جرّب المستوى مرتين: مرة طلع الفتيل ورجع الإغلاق تحته، ومرة سكّر الجسم فوقه كامل. الأولى صادت ستوبات… والثانية فتحت الطريق.",
         svg=kasr_static()),
    dict(title="بصمات الكسر الوهمي",
         rules=[dict(t="الفتيل برا المستوى… والإغلاق داخله", bad=True),
                dict(t="جسم هزيل — ما فيه قوة دفع", bad=True),
                dict(t="يطلع بنهاية موجة تعبانة… مو ببدايتها", bad=True)]),
    dict(title="بصمات الكسر الحقيقي",
         rules=[dict(t="شمعة تسكّر بجسمها كامل فوق المستوى"),
                dict(t="دفعة واضحة بجسم عريض وحجم"),
                dict(t="يجي عقب رجعة وتجميع… بنفس جديد")]),
    dict(title="خطة التعامل",
         rules=[dict(t="خل الشمعة تسكّر قبل أي قرار"),
                dict(t="طق ستوبك بفيك؟ لا تلحق — انتظر الرجعة"),
                dict(t="عقب الكسر الحقيقي… الريتيست فرصة ثانية")],
         note="القرار حق الإغلاق — مو حق الفتيل."),
  ],
  outro_title="خل الإغلاق يتكلم", outro_items=[
    "«انكسر» ما تنقال قبل ما تسكّر الشمعة",
    "الفيك خبر مفيد: السيولة اللي فوق انسحبت",
    "أقوى الكسرات… اللي تجي عقب فيك"])

G_SUYULA = dict(
  eyebrow="دليل — السيولة", title="أنواع تجمعات<br>السيولة", keyword="سيولة",
  subtitle="الستوبات المتجمعة… عشا السوق", hero=dkmap(suyula_static(760, 360)),
  pages=[
    dict(title="خريطة التجمعات",
         rules=[dict(t="قمتين بنفس السعر؟ فوقهم ستوبات البايعين"),
                dict(t="قاعين متطابقين؟ تحتهم ستوبات الشارين"),
                dict(t="ترند لاين شايفه الكل… عليه ستوبات الكل")],
         note="وضوح المستوى يعني زحمة ستوبات عنده."),
    dict(title="شوفها عالجارت", ticker="الناسداك · 30 دقيقة · 2026-06-18",
         lead="قمم متطابقة فوق وPDL تحت — غطس السوق سحب ستوبات القاع، ارتد من زون الطلب، وقصد ستوبات القمم.",
         svg=suyula_static()),
    dict(title="الاستخدام الصح",
         rules=[dict(t="علّم التجمعات قبل لا تبدأ جلستك"),
                dict(t="خل السحب يصير أول… دخولك عقبه"),
                dict(t="الارتداد من الزون بعد السحب = إشارتك")]),
    dict(title="فخوخ تنتبه لها",
         rules=[dict(t="ستوبك بنفس مكان ستوبات القطيع", bad=True),
                dict(t="دخول لحظة السحب بدون أي تأكيد", bad=True),
                dict(t="تتعامل مع التجمع كمقاومة… وهو هدف", bad=True)]),
  ],
  outro_title="اقرأ الخريطة قبل ما تتحرك", outro_items=[
    "أول سؤال بجلستك: وين أقرب تجمع؟",
    "كل حركة قوية… وراها ستوبات انسحبت",
    "ابعد ستوبك عن الأماكن المزدحمة"])

G_INTIQAM = dict(
  eyebrow="دليل — نفسية التداول", title="إيقاف صفقة<br>الانتقام", keyword="انتقام",
  subtitle="تبي تعوّض خسارتك… بنفس الجلسة؟", hero=dkmap(escalation(700, 320)),
  pages=[
    dict(title="أول علاماتها",
         rules=[dict(t="لوت مضاعف — «أرجّع خسارتي بضربة»", bad=True),
                dict(t="عكس الاتجاه… بس عشان تثبت رأيك", bad=True),
                dict(t="بدون ستوب — «ما بغلط مرتين»", bad=True)],
         svg=escalation(880, 330)),
    dict(title="من وين تجي؟",
         rules=[dict(t="دماغك يسجل الخسارة ضربة شخصية"),
                dict(t="الحرارة تطفي التحليل وتشغل الرد"),
                dict(t="وكل ضربة جديدة ترفع الحرارة أكثر")],
         note="خصمك بهاللحظة مو الجارت… خصمك مزاجك."),
    dict(title="الفرامل الثلاث",
         rules=[dict(t="بعد خسارتين… التداول وقف لباجر"),
                dict(t="دوّن شعورك أول — الكتابة تطفي الحرارة"),
                dict(t="حجم العقد ما يدري إنك خسران — خله ثابت")]),
    dict(title="أجّل… لا تلغي",
         lead="الفكرة اللي طرأت بعد خسارتين — موعدها الجلسة الجاية. الفرص تتجدد كل يوم… الحساب ما يتجدد.",
         note="التأجيل قوة — مو خوف."),
  ],
  outro_title="آخر كلمة", outro_items=[
    "اللي تطارده ما يرجع… واللي بيدك يروح",
    "رد الاعتبار الصدق: مراجعة هادية مو دخلة حارّة",
    "الأسواق تفتح كل يوم — الحسابات لا"])

G_YAWMIYAT = dict(
  eyebrow="دليل — أساسيات", title="يوميات<br>التداول", keyword="يوميات",
  subtitle="الدفتر اللي يفضح النمط", hero=dkmap(jbars(720, 310)),
  pages=[
    dict(title="الفايدة من أول أسبوع",
         lead="خساراتك لها نمط — بس دماغك يمسح التفاصيل بعد يومين. الدفتر يمسك الخيط… وأسبوع واحد يكفي يبين لك وين تنزف.",
         svg=jbars(880, 330)),
    dict(title="وقت الصفقة",
         rules=[dict(t="قبل ما تضغط: شنو حجتك بهالدخلة؟"),
                dict(t="عقب ما تطلع: النتيجة + حالتك النفسية"),
                dict(t="صورة للجارت وقت القرار — هذا الدليل")]),
    dict(title="الجدول العملي", html=JTABLE,
         lead="جدول بسيط — وكل الشغل بعمود السبب:",
         note="صفقتين حمر بنفس العمود؟ هذا النمط اللي تدور عليه."),
    dict(title="جرد الأسبوع",
         rules=[dict(t="آخر الأسبوع: صنّف صفقاتك على السبب"),
                dict(t="عدّ اللي دخلتها بسيت أب حقيقي"),
                dict(t="سبب خسّرك ثلاث مرات؟ صار قانون بخطتك")]),
  ],
  outro_title="الدفتر ذاكرتك الثانية", outro_items=[
    "التدوين بنفس اليوم — باجر تنسى النص",
    "قبل ما تفتح المنصة… طالع صفحة أمس",
    "أغلى درس عندك مدفون بصفقاتك القديمة"])

G_STOP = dict(
  eyebrow="دليل — إدارة المخاطر", title="وين يتحط<br>الستوب لوز؟", keyword="ستوب",
  subtitle="مين حاط ستوبك… الهيكل ولا خوفك؟", hero=dkmap(SK_WRONG.replace('width="880"', 'width="700"')),
  pages=[
    dict(title="الغلط: داخل التنفس",
         lead="لازق بآخر فتيل — بنص تنفس السعر الطبيعي. ذبذبة عادية تاخذه… والحركة تكمل بدونك.",
         svg=SK_WRONG),
    dict(title="الصح: ورا الهيكل",
         lead="خلف قاع الهيكل أو خلف الزون — نقطة لو انلمست، السيناريو كله سقط.",
         svg=SK_RIGHT),
    dict(title="الترتيب الصح",
         rules=[dict(t="المسافة يحددها الجارت… مو مزاجك"),
                dict(t="اللوت ينحسب بعد المسافة — مو قبلها"),
                dict(t="المسافة بعيدة؟ صغّر العقد — المخاطرة ثابتة")],
         note="اللي يتحكم بحجم خسارتك اللوت… مو قرب الستوب."),
    dict(title="الخطوط الحمر",
         rules=[dict(t="تزحلقه لما يقرب السعر — «فرصة أخيرة»", bad=True),
                dict(t="نفس النقاط لكل صفقة… أي كان الجارت", bad=True),
                dict(t="تشيله كامل وتقول «بيرد أكيد»", bad=True)]),
  ],
  outro_title="درع… مو قيد", outro_items=[
    "الستوب القريب راحة للخاطر ونزيف للحساب",
    "مكانه ينقرر قبل الدخول — وما ينلمس بعده",
    "خسارة محسوبة بمكان صح تحمي رأس المال"])

for cfg, out in [(G_KASR, "guide_kasr.html"), (G_SUYULA, "guide_suyula.html"),
                 (G_INTIQAM, "guide_intiqam.html"), (G_YAWMIYAT, "guide_yawmiyat.html"),
                 (G_STOP, "guide_stop.html")]:
    n = build_guide(cfg, os.path.join(HERE, out))
    print(out, n, "pages")
