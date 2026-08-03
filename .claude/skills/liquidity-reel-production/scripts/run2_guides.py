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
  subtitle="أخطر صفقة… اللي بعد الخسارة", hero=dkmap(escalation(700, 320)),
  pages=[
    dict(title="شلون تبدأ؟",
         rules=[dict(t="تكبّر اللوت — «أعوّض أسرع»", bad=True),
                dict(t="تدخل عكس السوق بعناد", bad=True),
                dict(t="تلغي الستوب — «أكيد بيرجع»", bad=True)],
         svg=escalation(880, 330)),
    dict(title="ليش تصير؟",
         rules=[dict(t="الخسارة تنحس كأنها إهانة — والدماغ يبي يرد"),
                dict(t="الغضب يلغي الخطة ويشغل العناد"),
                dict(t="كل خسارة جديدة تزيد الجرعة")],
         note="السوق ما يعرفك… الانتقام معركة مع نفسك."),
    dict(title="بروتوكول الإيقاف",
         rules=[dict(t="خسرتين ورا بعض = المنصة تتصكر اليوم"),
                dict(t="اكتب الخسارة بيومياتك قبل أي قرار"),
                dict(t="اللوت ثابت مهما صار — بدون استثناء")]),
    dict(title="قاعدة الجلسة الجديدة",
         lead="أي صفقة تجي ببالك بعد خسرتين — تنتظر جلسة جديدة. السوق ما يهرب… حسابك اللي يهرب.",
         note="الانتظار مو ضعف — الانتظار خطة."),
  ],
  outro_title="القرار بيدك", outro_items=[
    "السوق ما ياخذ منك — انت اللي تعطيه",
    "أفضل رد على الخسارة: تحليل، مو صفقة",
    "بكرة فيه سوق… بس إذا بقى حساب"])

G_YAWMIYAT = dict(
  eyebrow="دليل — أساسيات", title="يوميات<br>التداول", keyword="يوميات",
  subtitle="السجل اللي يوريك غلطك المتكرر", hero=dkmap(jbars(720, 310)),
  pages=[
    dict(title="ليش تسجل؟",
         lead="كل خسارة لها سبب — بس الذاكرة تنسى وتجمّل. السجل ما ينسى… وأول أسبوع بيوريك نمطك.",
         svg=jbars(880, 330)),
    dict(title="شنو تسجل؟",
         rules=[dict(t="قبل الدخول: السبب — ليش هالصفقة؟"),
                dict(t="بعد الخروج: النتيجة وشعورك وقتها"),
                dict(t="سكرين شوت للجارت لحظة الدخول")]),
    dict(title="شكل السجل", html=JTABLE,
         lead="أربع خانات تكفي — والعبرة بخانة السبب:",
         note="الصفقتين الحمر نفس السبب — هذا اللي تدور عليه."),
    dict(title="المراجعة الأسبوعية",
         rules=[dict(t="كل جمعة: افرز صفقاتك حسب السبب"),
                dict(t="احسب: چم وحدة كانت سيت أب صح؟"),
                dict(t="غلط تكرر 3 مرات = قاعدة جديدة بخطتك")]),
  ],
  outro_title="اللي ما يسجل… يعيد", outro_items=[
    "سجل قبل ما تنام — التفاصيل تطير",
    "راجع سجلك قبل الجلسة الجاية",
    "حسابك يتحسن يوم تقرأ أخطاءك"])

G_STOP = dict(
  eyebrow="دليل — إدارة المخاطر", title="وين يتحط<br>الستوب لوز؟", keyword="ستوب",
  subtitle="ليش ستوبك ينطق… والسعر يكمل بدونك", hero=dkmap(SK_WRONG.replace('width="880"', 'width="700"')),
  pages=[
    dict(title="الغلط: بالضجيج",
         lead="تحت آخر شمعة أو آخر قاع صغير — داخل حركة السوق الطبيعية. فتيل واحد يكفي يطقه.",
         svg=SK_WRONG),
    dict(title="الصح: تحت الهيكل",
         lead="تحت قاع الهيكل أو تحت الزون — المكان اللي لو وصله السعر، فكرتك فعلًا غلطت.",
         svg=SK_RIGHT),
    dict(title="القياس الصح",
         rules=[dict(t="حدد مكان الستوب أول — من الهيكل"),
                dict(t="بعدين احسب اللوت على مسافته"),
                dict(t="ستوب أبعد = لوت أصغر — نفس المخاطرة")],
         note="المخاطرة تجي من اللوت… مو من مسافة الستوب."),
    dict(title="ممنوعات",
         rules=[dict(t="توسيعه بعد الدخول — «شوي بس»", bad=True),
                dict(t="رقم ثابت لكل الصفقات بدون نظر للهيكل", bad=True),
                dict(t="إلغاؤه لما يقرب السعر — «أكيد يرتد»", bad=True)]),
  ],
  outro_title="الستوب حماية", outro_items=[
    "مكانه يثبت إن فكرتك غلطت — مو رقم مريح",
    "ينحدد قبل الدخول وما ينلمس بعده",
    "ستوب ينطق صح أرحم من حساب يروح غلط"])

for cfg, out in [(G_KASR, "guide_kasr.html"), (G_SUYULA, "guide_suyula.html"),
                 (G_INTIQAM, "guide_intiqam.html"), (G_YAWMIYAT, "guide_yawmiyat.html"),
                 (G_STOP, "guide_stop.html")]:
    n = build_guide(cfg, os.path.join(HERE, out))
    print(out, n, "pages")
