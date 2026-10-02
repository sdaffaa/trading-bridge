# -*- coding: utf-8 -*-
# run8 — إعادة تصميم بوستات اليوم (كاروسيلات run4 الثلاثة) وفق MASTER PROMPT V2
# نفس الصفقات والجارتات (الوحدة نفسها تُستبدل) — النصوص فصحى بالكامل + هوية الغلاف الداكن/المحتوى الأوف وايت
import os
from car_common import (CW, brandbar, counter, swipe, dots, cover_slide, dkmap,
                        build_carousel, INK, TEAL, TEAL_D, RED, GREY, MUTE)
from reel_build import gen, chart, htext

HERE = os.path.dirname(os.path.abspath(__file__))
N = 30

# ---------- قصص الجارتات (مطابقة لـ run4 — نفس البذور، بلا تسجيل جديد) ----------
def _story(kind, v):
    if kind == "chase":
        a = [(0, 10.0), (4, 10.8 + v*0.5), (8, 10.2), (14, 17.5 + v*0.8), (16, 17.0),
             (20, 14.4 - v*0.3), (23, 15.2), (29, 21.5 + v*0.9)]
        return a, dict(xe=14, stop=20, cont=29)
    if kind == "retest":
        a = [(0, 10.0), (5, 9.4 + v*0.4), (9, 10.1), (14, 16.8 + v*0.6), (17, 14.6),
             (21, 10.7 + v*0.2), (23, 11.6), (29, 19.8 + v*1.0)]
        return a, dict(iz=8, xe=14, ie=21, tgt=29)
    if kind == "skip":
        a = [(0, 10.0), (6, 10.6), (10, 11.0 - v*0.3), (16, 16.2), (21, 17.8), (29, 22.6 + v*0.7)]
        return a, dict(iz=9, top=16)
    if kind == "loss":
        a = [(0, 18.0), (5, 18.6), (9, 17.2), (13, 17.9 - v*0.3), (18, 13.8), (23, 12.4), (29, 13.6)]
        return a, dict(ie=12, brk=18)
    raise ValueError(kind)

def _zone_from(w, i):
    seg = w[max(0, i-1):i+2]
    return max(max(c["o"], c["c"]) for c in seg), min(c["l"] for c in seg)

def trade_chart(kind, seed, outcome, ok, v=0, extra=None, Wd=920, H=430):
    """نسخة V2 — تسميات فصحى. الجارتات نفسها المسجلة لوحدة اليوم (استبدال لا تكرار)."""
    anchors, ix = _story(kind, v)
    w = gen(anchors, N, seed, wick=0.85)
    ymin = min(c["l"] for c in w); ymax = max(c["h"] for c in w)
    pad = (ymax - ymin) * 0.08; ymin -= pad * 1.7; ymax += pad * 1.2
    svg, x, y, slot = chart(w, Wd, H, ymin, ymax, grid=4, pl=12, pr=16, pt=20, pb=14, body=0.6)
    r = 11
    if kind == "chase":
        XE, ST, CO = ix["xe"], ix["stop"], ix["cont"]
        hx, hy = x(XE), y(w[XE]["h"])
        svg += (f'<line x1="{hx-r:.1f}" y1="{hy-r:.1f}" x2="{hx+r:.1f}" y2="{hy+r:.1f}" stroke="{RED}" stroke-width="3.2" stroke-linecap="round"/>'
                f'<line x1="{hx-r:.1f}" y1="{hy+r:.1f}" x2="{hx+r:.1f}" y2="{hy-r:.1f}" stroke="{RED}" stroke-width="3.2" stroke-linecap="round"/>')
        svg += htext(hx, hy - 20, "الملاحقة هنا", RED, 19)
        sl = w[ST]["l"]
        svg += f'<line x1="{x(XE)-slot*0.6:.1f}" y1="{y(sl):.1f}" x2="{x(ST)+slot*0.7:.1f}" y2="{y(sl):.1f}" stroke="{RED}" stroke-width="1.8" stroke-dasharray="7 5"/>'
        svg += htext(x(ST), y(sl) + 26, "أصاب الوقف", RED, 18)
        svg += htext(x(CO)-slot*2.4, max(y(w[CO]["h"]) - 16, 96), "وواصل من دونك", TEAL_D, 18)
    elif kind == "retest":
        IZ, XE, IE, TG = ix["iz"], ix["xe"], ix["ie"], ix["tgt"]
        ZT, ZB = _zone_from(w, IZ)
        zx0 = x(IZ) - slot*0.5; zx1 = x(min(IE+3, N-1)) + slot*0.5
        svg += (f'<rect x="{zx0:.1f}" y="{y(ZT):.1f}" width="{zx1-zx0:.1f}" height="{y(ZB)-y(ZT):.1f}" fill="{TEAL}" style="opacity:0.16"/>'
                f'<rect x="{zx0:.1f}" y="{y(ZT):.1f}" width="{zx1-zx0:.1f}" height="{y(ZB)-y(ZT):.1f}" fill="none" stroke="{TEAL_D}" stroke-width="1.2"/>')
        svg += htext((zx0+zx1)/2, y(ZB) + 24, "منطقة الانطلاق", TEAL_D, 17)
        hx, hy = x(XE), y(w[XE]["h"])
        svg += (f'<line x1="{hx-r:.1f}" y1="{hy-r:.1f}" x2="{hx+r:.1f}" y2="{hy+r:.1f}" stroke="{RED}" stroke-width="3" stroke-linecap="round"/>'
                f'<line x1="{hx-r:.1f}" y1="{hy+r:.1f}" x2="{hx+r:.1f}" y2="{hy-r:.1f}" stroke="{RED}" stroke-width="3" stroke-linecap="round"/>')
        svg += htext(hx, hy - 20, "الإغراء هنا", RED, 18)
        svg += f'<circle cx="{x(IE):.1f}" cy="{y(w[IE]["l"]):.1f}" r="13" fill="none" stroke="{TEAL_D}" stroke-width="3"/>'
        svg += htext(x(IE), y(w[IE]["l"]) + 34, "الدخول الصحيح", TEAL_D, 19)
        if extra and extra.get("stop_pts"):
            sv = w[IE]["l"] - (ymax - ymin) * extra.get("stop_frac", 0.06)
            bx = x(IE) + slot * 1.6
            svg += (f'<line x1="{bx:.1f}" y1="{y(w[IE]["l"]):.1f}" x2="{bx:.1f}" y2="{y(sv):.1f}" stroke="{INK}" stroke-width="1.8"/>'
                    f'<line x1="{bx-6:.1f}" y1="{y(w[IE]["l"]):.1f}" x2="{bx+6:.1f}" y2="{y(w[IE]["l"]):.1f}" stroke="{INK}" stroke-width="1.8"/>'
                    f'<line x1="{bx-6:.1f}" y1="{y(sv):.1f}" x2="{bx+6:.1f}" y2="{y(sv):.1f}" stroke="{INK}" stroke-width="1.8"/>'
                    f'<line x1="{x(IE)-slot*0.6:.1f}" y1="{y(sv):.1f}" x2="{bx+6:.1f}" y2="{y(sv):.1f}" stroke="{RED}" stroke-width="1.6" stroke-dasharray="6 5"/>')
            svg += htext(bx + 14, (y(w[IE]["l"]) + y(sv))/2 + 6, extra["stop_pts"], INK, 18, anchor="start")
        svg += htext(x(TG)-slot*1.6, max(y(w[TG]["h"]) - 16, 96), "الهدف", TEAL_D, 18)
    elif kind == "skip":
        IZ, TP = ix["iz"], ix["top"]
        ZT, ZB = _zone_from(w, IZ)
        zx0 = x(IZ) - slot*0.5; zx1 = x(N-1) + slot*0.5
        svg += (f'<rect x="{zx0:.1f}" y="{y(ZT):.1f}" width="{zx1-zx0:.1f}" height="{y(ZB)-y(ZT):.1f}" fill="{TEAL}" style="opacity:0.14"/>'
                f'<rect x="{zx0:.1f}" y="{y(ZT):.1f}" width="{zx1-zx0:.1f}" height="{y(ZB)-y(ZT):.1f}" fill="none" stroke="{TEAL_D}" stroke-width="1.2" stroke-dasharray="7 5"/>')
        svg += htext((zx0+zx1)/2, y(ZB) + 24, "منطقتك — لم يعد إليها", TEAL_D, 17)
        svg += htext(x(TP), y(w[TP]["h"]) - 18, "فاتت؟ دعها", INK, 19)
    elif kind == "loss":
        IE, BK = ix["ie"], ix["brk"]
        svg += f'<circle cx="{x(IE):.1f}" cy="{y(w[IE]["h"]):.1f}" r="12" fill="none" stroke="{RED}" stroke-width="2.6"/>'
        svg += htext(x(IE), y(w[IE]["h"]) - 20, "دخول شراء", RED, 18)
        svg += f'<line x1="{x(IE)-slot*0.6:.1f}" y1="{y(w[BK]["h"]):.1f}" x2="{x(BK)+slot*0.7:.1f}" y2="{y(w[BK]["h"]):.1f}" stroke="{RED}" stroke-width="1.8" stroke-dasharray="7 5"/>'
        svg += htext(x(BK), y(w[BK]["h"]) - 16, "الوقف — خروج نظيف", RED, 18)
    if outcome:
        col = TEAL_D if ok else RED
        bw = min(Wd - 40, 44 + int(len(outcome) * 12.5))
        svg += (f'<g><rect x="{Wd-16-bw}" y="16" width="{bw}" height="46" fill="{"#EAF3F5" if ok else "#F8ECEC"}" stroke="{col}" stroke-width="1.4"/>'
                + htext(Wd - 16 - bw/2, 47, outcome, col, 21) + '</g>')
    return svg + "</svg>"

BT_TABLE = '''<table style="border-collapse:collapse;width:100%;background:#FBF9F5;border:1px solid #DED8CC">
<tr><th style="background:#1E627A;color:#fff;font-size:26px;font-weight:800;padding:13px">العيّنة</th><th style="background:#1E627A;color:#fff;font-size:26px;font-weight:800;padding:13px">الإصابة</th><th style="background:#1E627A;color:#fff;font-size:26px;font-weight:800;padding:13px">متوسط RR</th><th style="background:#1E627A;color:#fff;font-size:26px;font-weight:800;padding:13px">أطول سلسلة</th><th style="background:#1E627A;color:#fff;font-size:26px;font-weight:800;padding:13px">المحصلة</th></tr>
<tr><td style="font-size:27px;padding:14px;text-align:center;border-top:1px solid #EDE7DB;color:#0F2E3C;font-weight:800">50 صفقة</td><td style="font-size:27px;padding:14px;text-align:center;border-top:1px solid #EDE7DB;color:#1E627A;font-weight:800">45%</td><td style="font-size:27px;padding:14px;text-align:center;border-top:1px solid #EDE7DB;color:#1E627A;font-weight:800">1 : 2</td><td style="font-size:27px;padding:14px;text-align:center;border-top:1px solid #EDE7DB;color:#D24B4B;font-weight:800">5 متتالية</td><td style="font-size:27px;padding:14px;text-align:center;border-top:1px solid #EDE7DB;color:#1E627A;font-weight:900">+35R / 100</td></tr>
</table>'''

# ---------- النصوص الفصحى (إعادة صياغة V2 لمحتوى اليوم) ----------
COPY = {
 "fomo": dict(
  eyebrow="درس تطبيقي — نفسية التداول",
  title="متى تنتظر الرجعة…<br>ومتى تنساها؟",
  tag="خمس صفقات على قاعدة واحدة",
  trades=[
   dict(label="الصفقة ١ — الملاحقة", title="شمعة اندفاع… ودخول عند قمتها",
        bait="الإغراء: الشراء عند إغلاق شمعة الاندفاع — «السوق منطلق»",
        right="الصواب: التوقف ورسم المنطقة التي انطلقت منها الشمعة",
        because="لأن سعرك عند القمة أبعد نقطة عن الهيكل… وأول تنفّس طبيعي للسعر يمرّ على وقفك",
        outcome="وقف −1% لمن لاحق"),
   dict(label="الصفقة ٢ — الانتظار", title="النمط نفسه… لكن بصبر",
        bait="الإغراء: تكرار الخطأ نفسه — اندفاع جديد ويدك على الزر",
        right="الصواب: تحديد منطقة الانطلاق ووضع تنبيه عليها وإغلاق الشاشة",
        because="لأن السعر عاد فاختبر منطقته قبل أن يواصل… والتنبيه انطلق وأنت هادئ",
        outcome="+150 نقطة من الرجعة"),
   dict(label="الصفقة ٣ — التي لم تعد", title="حركة خبرية مضت بلا رجوع",
        bait="الإغراء: ملاحقتها — «هذا النوع لا يعود، ادخل بأي سعر»",
        right="الصواب: تركها وتدوينها في يومياتك",
        because="لأن دخولاً بلا منطقة ولا وقف منطقي مقامرة… والفرصة الفائتة لا تُحسب خسارة",
        outcome="صفر خسارة — لم ندخل"),
   dict(label="الصفقة ٤ — ملاحقة الكسر", title="دخول بعد الكسر بثمانين نقطة",
        bait="الإغراء: الدخول مع كسر مستوى مشهور… بعد أن قطع السعر 80 نقطة",
        right="الصواب: انتظار عودة السعر لاختبار المستوى المكسور",
        because="لأن إعادة الاختبار تحدث في أغلب الكسور… ومن دخل متأخراً أصابت وقفه ثم واصل السعر من دونه",
        outcome="وقف… وواصلت الحركة من دونه"),
   dict(label="الصفقة ٥ — حساب الرجعة", title="وقف 20 نقطة… وهدف 80",
        bait="الإغراء: تكبير العقد حماسةً عند ملامسة المنطقة",
        right="الصواب: الدخول بالعقد المحسوب — وقف 20 نقطة خلف المنطقة وهدف عند القمة",
        because="لأن الرجعة تمنحك عائداً إلى مخاطرة 1:4… والهدف نفسه بالملاحقة لا يتجاوز 1:1 بوقف أبعد",
        outcome="تحقق 1:4"),
  ],
  quote_a="دخولك ليس لحظة الحماسة…", quote_b="دخولك مكان محسوب.", quote_tag="علاج الفومو (FOMO)",
  share="أرسله لصديقك الذي يشتري من قمة الشمعة",
  promise="علّق «فومو» ليصلك الدليل المفصل — 16 صفحة — على الخاص"),
 "backtest": dict(
  eyebrow="درس تطبيقي — أساسيات التداول",
  title="نظامك رابح أم خاسر…<br>أين الدليل؟",
  tag="عيّنة من 50 صفقة",
  trades=[
   dict(label="الصفقة ١ — الرابحة الأولى", title="أول صفقة في الاختبار… ربحت",
        bait="الإغراء: الحكم فوراً — «النظام ممتاز، إلى الحساب الحقيقي»",
        right="الصواب: تسجيلها في الجدول ومواصلة الاختبار كما بدأ",
        because="لأن صفقة واحدة لا تمثّل النظام… فالعملة إن رميتها مرة وظهرت صورة لا تصبح كلها صورة",
        outcome="+2R — سُجّلت ونواصل"),
   dict(label="الصفقة ٢ — الخاسرة", title="الصفقة الثانية… أصابت الوقف",
        bait="الإغراء: تعديل القواعد فوراً — «لو كان الوقف أبعد قليلاً…»",
        right="الصواب: تسجيلها والمواصلة بالقواعد نفسها حرفياً",
        because="لأن التعديل في منتصف الاختبار يفسد العيّنة… فتختبر في النهاية عشرة أنظمة لا نظاماً واحداً",
        outcome="−1R — سُجّلت ونواصل"),
   dict(label="الصفقة ٣ — السلسلة", title="ثلاث خسائر متتالية",
        bait="الإغراء: حذف النظام كله — «فاشل بوضوح»",
        right="الصواب: المواصلة وتسجيل طول السلسلة رقماً",
        because="لأن لكل نظام سلاسل خسارة… وهذا الرقم تحديداً يهيّئك نفسياً لأسوأ أسبوع في الحساب الحقيقي",
        outcome="−3R متتالية… والاختبار مستمر"),
   dict(label="الصفقة ٤ — الرابحة الكبيرة", title="صفقة حلّقت… +4R",
        bait="الإغراء: الحلم — «لو كانت في الحقيقي بعقد كبير…»",
        right="الصواب: تسجيلها رقماً في الجدول كأي صفقة",
        because="لأن حماسة الربح تُعمي الحكم كما يُعميه خوف الخسارة… والاختبار محكمة لا احتفال",
        outcome="+4R — رقم في الجدول"),
   dict(label="الصفقة ٥ — الحكم", title="بعد 50 صفقة… الأرقام تتكلم",
        bait="الإغراء: الحكم من الذاكرة — «شعرتُ أن النظام جيد»",
        right="الصواب: استخراج الأرقام الثلاثة: إصابة 45% × متوسط 1:2 × أطول سلسلة 5",
        because="لأن الحكم للعيّنة كاملة لا لصفقة… و45 رابحة بضعف الخسارة تُخرج النظام رابحاً رغم خسارة أكثر من النصف",
        outcome="+35R لكل 100 صفقة — نظام رابح"),
  ],
  quote_a="صفقة واحدة لا تحكم…", quote_b="الخمسون هي التي تتكلم.", quote_tag="منطق العيّنة",
  share="أرسله لمن يحكم على استراتيجيته من صفقتين",
  promise="علّق «باكتست» لتصلك خطة الاختبار كاملة PDF على الخاص"),
 "lot": dict(
  eyebrow="درس تطبيقي — إدارة المخاطر",
  title="الوقف يتغير…<br>وعقدك ثابت؟",
  tag="معادلة الحجم (Lot)",
  trades=[
   dict(label="الصفقة ١ — الوقف القريب", title="وقف 20 نقطة",
        bait="الإغراء: الدخول بحجم كبير على المزاج — «الفرصة مضمونة»",
        right="الصواب: الحساب — 10$ مخاطرة ÷ (20 نقطة × 10$) = 0.05 لوت",
        because="لأن الوقف القريب يسمح بعقد أكبر… والمخاطرة نفسها 1% لا تتغير",
        outcome="لوت 0.05 — مخاطرة 1%"),
   dict(label="الصفقة ٢ — الوقف البعيد", title="وقف 100 نقطة",
        bait="الإغراء: الدخول بعقد الأمس نفسه — «جرّبته فنجح»",
        right="الصواب: إعادة الحساب — 10$ ÷ (100 × 10$) = 0.01 لوت",
        because="لأن الوقف البعيد يستلزم تصغير العقد… لتبقى خسارتك القصوى 1% مهما بعُدت المسافة",
        outcome="لوت 0.01 — مخاطرة 1%"),
   dict(label="الصفقة ٣ — الوقف المتوسط", title="وقف 50 نقطة",
        bait="الإغراء: تقريب الوقف قليلاً — «ليكبر العقد»",
        right="الصواب: إبقاء الوقف خلف الهيكل والحساب — 10$ ÷ (50 × 10$) = 0.02 لوت",
        because="لأن مسافة الوقف يحددها الجارت… والعقد هو الذي يتنازل، لا الحماية",
        outcome="لوت 0.02 — مخاطرة 1%"),
   dict(label="الصفقة ٤ — الحجم الثابت", title="العقد نفسه لكل الصفقات… الخطأ",
        bait="الإغراء: الكسل — 0.05 ثابتة في كل صفقة بلا حساب",
        right="الصواب: ملاحظة أن وقف هذه الصفقة 100 نقطة… أي أن 0.05 خطأ فادح",
        because="لأن 0.05 لوت × 100 نقطة × 10$ = خسارة 50$… أي 5% بضربة واحدة — خمسة أضعاف الخطة",
        outcome="وقف −5% — خمسة أضعاف الخطة"),
   dict(label="الصفقة ٥ — المعادلة قبل الزر", title="وقف 40 نقطة… والتقريب للأسفل",
        bait="الإغراء: تقدير الحجم بالعين — «0.03 تقريباً تكفي»",
        right="الصواب: الحساب — 10$ ÷ (40 × 10$) = 0.025 → تقريبها للأسفل 0.02",
        because="لأن التقريب للأعلى يرفع مخاطرتك فوق 1%… والتقريب للأسفل يبقيك داخل الخطة دائماً",
        outcome="لوت 0.02 — الحساب قبل الزر"),
  ],
  quote_a="الوقف يحدد المسافة…", quote_b="والعقد يتبعه.", quote_tag="ترتيب القرار",
  share="أرسله لمن يدخل صفقاته كلها بالعقد نفسه",
  promise="علّق «لوت» ليصلك دليل الحجم صفحة صفحة على الخاص"),
}

PLANS = {
 "fomo":     [("chase", 4101, False, 0, None), ("retest", 4102, True, 0, None),
              ("skip", 4103, True, 0, None),   ("chase", 4104, False, 1, None),
              ("retest", 4105, True, 1, {"stop_pts": "20 نقطة", "stop_frac": 0.045})],
 "backtest": [("retest", 4111, True, 0, None), ("loss", 4112, False, 0, None),
              ("loss", 4113, False, 1, None),  ("retest", 4114, True, 1, None),
              ("table", 0, True, 0, None)],
 "lot":      [("retest", 4121, True, 0, {"stop_pts": "20 نقطة", "stop_frac": 0.04}),
              ("retest", 4122, True, 1, {"stop_pts": "100 نقطة", "stop_frac": 0.13}),
              ("retest", 4123, True, 0, {"stop_pts": "50 نقطة", "stop_frac": 0.075}),
              ("loss", 4124, False, 0, None),
              ("retest", 4125, True, 1, {"stop_pts": "40 نقطة", "stop_frac": 0.06})],
}
KW = {"fomo": "فومو", "backtest": "باكتست", "lot": "لوت"}
TOTAL = 7

def trade_slide(idx, t, chart_svg, inner_html=None):
    body = f'<div class="chartwrap">{chart_svg}</div>' if chart_svg else (inner_html or "")
    return f'''<div class="slide" {CW}>
  {counter(idx, TOTAL)}
  {brandbar(True)}
  <div class="cont dense">
    <div class="tlabel2">{t["label"]}</div>
    <h1 class="ttl7">{t["title"]}</h1>
    {body}
    <div class="rulerow"><span class="rn x">✗</span><p>{t["bait"]}</p></div>
    <div class="rulerow"><span class="rn">✓</span><p>{t["right"]}</p></div>
    <div class="note">{t["because"]}</div>
  </div>
  {swipe()}{dots(idx, TOTAL)}
</div>'''

def cta_slide(cc, kw):
    return f'''<div class="slide" {CW}>
  {counter(TOTAL, TOTAL)}
  {brandbar(True)}
  <div class="cta">
    <h1 class="big2">{cc["quote_a"]}<br><span style="color:{TEAL_D}">{cc["quote_b"]}</span></h1>
    <p class="tag2 center" style="margin-top:10px">{cc["quote_tag"]}</p>
    <div class="kwbox"><span>اكتب في التعليقات</span><b>«{kw}»</b></div>
    <p class="tag2 center">{cc["promise"]}</p>
    <p class="tag2 center" style="opacity:.75">{cc["share"]}</p>
  </div>
  <div class="botmeta">لغرض تعليمي · <span dir="ltr">@liquidity.state</span></div>
  {dots(TOTAL, TOTAL)}
</div>'''

X8CSS = f'''
.cont.dense{{top:172px;bottom:150px;gap:20px;justify-content:center}}
.ttl7{{font-size:52px;font-weight:900;color:{INK};line-height:1.18;text-align:center;letter-spacing:-.5px}}
.tlabel2{{align-self:center;border:1.5px solid {TEAL_D};color:{TEAL_D};font-size:24px;font-weight:800;
  padding:7px 24px;border-radius:2px}}
.kwbox{{margin:34px auto 18px;border:1.5px solid {TEAL_D};background:#EAF3F5;padding:20px 44px;text-align:center;border-radius:2px}}
.kwbox span{{display:block;font-size:24px;color:{GREY};font-weight:700}}
.kwbox b{{font-size:44px;color:{TEAL_D};font-weight:900}}
'''

for key in ["fomo", "backtest", "lot"]:
    cc = COPY[key]
    plan = PLANS[key]
    hero = trade_chart(plan[0][0], plan[0][1] + 900, None, plan[0][2], plan[0][3], plan[0][4], Wd=700, H=330)
    SL = [cover_slide(cc["eyebrow"], cc["title"], cc["tag"], dkmap(hero), total=TOTAL)]
    for i, (t, pl) in enumerate(zip(cc["trades"], plan)):
        kind, seed, ok, v, extra = pl
        if kind == "table":
            SL.append(trade_slide(2 + i, t, None, inner_html=BT_TABLE))
        else:
            SL.append(trade_slide(2 + i, t, trade_chart(kind, seed, t["outcome"], ok, v, extra)))
    SL.append(cta_slide(cc, KW[key]))
    build_carousel(SL, f'{KW[key]} — Liquidity State V2', os.path.join(HERE, f"car8_{key}.html"), extra_css=X8CSS)
    print(f"car8_{key}.html: {len(SL)} slides")
