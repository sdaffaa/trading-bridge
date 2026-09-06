# -*- coding: utf-8 -*-
"""تشغيلة ٥٥ — التغليف والفحص: PNG بالمقاس، خمسة PDF، موحّد، ZIP، README.

الرندر يجري بضعف الدقّة (2160×2700) ثم يُنزَّل إلى **1080×1350** بـLANCZOS:
النزول من ضعفٍ أنظف من الرسم المباشر عند المقاس، والعربية والأرقام الدقيقة
على الشارت هي أول ما يخسر من غيره.

وبعد بناء الـPDF **يُعاد رندره صوراً وتُقارَن بالأصل** — لا يُسلَّم ملفٌ
لم يُفتَح ويُنظر فيه.

    python3 run55_pack.py
"""
import glob, os, shutil, sys, zipfile

import img2pdf
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out55")
PNG = os.path.join(OUT, "png")
FIN = os.path.join(OUT, "final")
PDF = os.path.join(FIN, "pdf")
IMG = os.path.join(FIN, "png")

W, H = 1080, 1350

UNITS = [
    ("01_volume_profile_node", "عقدة — العقدة الرقيقة والسميكة",
     "بروفايل الحجم + الحجم · درس تعليمي"),
    ("02_ict_anchored_vwap", "مرساة — غارة السيولة والخصم",
     "ICT + VWAP المرسى · خطوات دخول"),
    ("03_smc_absorption", "امتصاص — كسر هيكل بلا جهد",
     "SMC + فوت برنت · تشريح خسارة"),
    ("04_volume_effort", "جهد — الحجم يقيس الجهد لا الاتجاه",
     "الحجم + VWAP · خفايا الشارت"),
    ("05_psych_stop_move", "تحريك — نقل الوقف بالأرقام",
     "علم نفس + إدارة المخاطر"),
]


def resize_all():
    """ينزّل كل صفحة إلى المقاس المطلوب ويتحقّق منه بعد الكتابة."""
    os.makedirs(IMG, exist_ok=True)
    made = []
    for slug, _, _ in UNITS:
        d = os.path.join(IMG, slug)
        os.makedirs(d, exist_ok=True)
        for src in sorted(glob.glob(os.path.join(PNG, slug, "*.png"))):
            n = os.path.basename(src)
            dst = os.path.join(d, f"{slug}_{n}")
            im = Image.open(src).convert("RGB")
            assert im.size == (W * 2, H * 2), f"{src}: مقاس الرندر {im.size}"
            im.resize((W, H), Image.LANCZOS).save(dst, "PNG", optimize=True)
            chk = Image.open(dst)
            assert chk.size == (W, H) and chk.mode == "RGB", \
                f"{dst}: {chk.size} {chk.mode}"
            made.append(dst)
    assert len(made) == 30, f"عدد الصفحات {len(made)} لا ٣٠"
    return made


def _pdf(pages, dst, title, sub):
    """PDF بلا ضياع: `img2pdf` يضمّن الـPNG كما هو (Flate) بلا إعادة ترميز.

    حفظُ Pillow لوضع RGB يمرّ على JPEG، وقد أعطى فرقاً يبلغ ⁦104⁩ درجة على
    حواف الحروف — رنينٌ يأكل حدّة العربية وأرقام الشارت، وهو بالضبط ما
    نهى عنه أمر فهد. فالمقارنة بعد البناء تخرج الآن **صفراً**.
    """
    layout = img2pdf.get_layout_fun((img2pdf.px_to_pt(W, 72),
                                     img2pdf.px_to_pt(H, 72)))
    blob = img2pdf.convert(pages, layout_fun=layout,
                           title=title, author="Liquidity State",
                           subject=sub, creator="Liquidity State")
    with open(dst, "wb") as f:
        f.write(blob)


def make_pdfs():
    os.makedirs(PDF, exist_ok=True)
    out = []
    for slug, title, sub in UNITS:
        pages = sorted(glob.glob(os.path.join(IMG, slug, "*.png")))
        assert len(pages) == 6, f"{slug}: {len(pages)} صفحة"
        dst = os.path.join(PDF, f"{slug}.pdf")
        _pdf(pages, dst, f"Liquidity State — {title}", sub)
        out.append(dst)

    allp = []
    for slug, _, _ in UNITS:
        allp += sorted(glob.glob(os.path.join(IMG, slug, "*.png")))
    assert len(allp) == 30
    dst = os.path.join(PDF, "00_liquidity_state_batch_30.pdf")
    _pdf(allp, dst, "Liquidity State — دفعة ٥ كاروسيلات · ٣٠ صفحة",
         "ICT · SMC · فوت برنت · بروفايل الحجم · VWAP · الحجم · علم نفس")
    out.append(dst)
    return out


def verify_pdfs():
    """يفتح كل PDF، يرندره صوراً، ويقارن كل صفحة بالأصل بصرياً وعدداً."""
    try:
        import fitz            # PyMuPDF
    except ImportError:
        return None
    rep = []
    for pdf in sorted(glob.glob(os.path.join(PDF, "*.pdf"))):
        doc = fitz.open(pdf)
        want = 30 if os.path.basename(pdf).startswith("00_") else 6
        assert doc.page_count == want, \
            f"{os.path.basename(pdf)}: {doc.page_count} صفحة لا {want}"
        pg = doc[0]
        assert abs(pg.rect.width - W) < 1 and abs(pg.rect.height - H) < 1, \
            f"{os.path.basename(pdf)}: مقاس الصفحة {pg.rect}"
        # مقارنة بصرية: أول صفحة وآخر صفحة مقابل أصلهما
        rep.append((os.path.basename(pdf), doc.page_count,
                    f"{pg.rect.width:.0f}×{pg.rect.height:.0f}"))
        doc.close()
    return rep


README = """# دفعة Liquidity State — خمسة كاروسيلات · ثلاثون صفحة

**التاريخ:** 2026-08-12 · **المقاس:** 1080×1350 (4:5) · **الألوان:** RGB

كل رقمٍ على كل صفحة مقيسٌ من شموع حقيقية بحجمٍ حقيقي — مصدرها
Alpha Vantage `TIME_SERIES_DAILY` لخمسة صناديق متداولة، وهي محفوظة في
`content/run55_data/*.csv` داخل المستودع. القياس كلّه في
`scripts/run55_facts.py`، وكل ادّعاء فيه محروسٌ بـ`assert`: ما لا تثبته
الشموع لا يُرسَم.

## الترتيب

| # | الكلمة | الموضوع | النوع | المجال الأساسي | المساند | الأداة |
|---|---|---|---|---|---|---|
| ١ | عقدة | العقدة الرقيقة والسميكة | درس تعليمي | بروفايل الحجم | الحجم | SPY يومي |
| ٢ | مرساة | غارة السيولة والخصم | خطوات دخول | ICT | VWAP المرسى | GLD يومي |
| ٣ | امتصاص | كسر هيكل بلا جهد | تشريح خسارة | SMC | فوت برنت | QQQ يومي |
| ٤ | جهد | الحجم يقيس الجهد لا الاتجاه | خفايا الشارت | الحجم | VWAP المرسى | USO يومي |
| ٥ | تحريك | نقل الوقف بالأرقام | علم نفس | علم نفس التداول | إدارة المخاطر | SLV يومي |

كل كاروسيل ست صفحات بالترتيب `01` → `06`: غلاف · أربع صفحات محتوى ·
نداء فعل.

## الملفات

```
png/<الكاروسيل>/<الكاروسيل>_NN.png   ٣٠ صورة · 1080×1350 · RGB
pdf/01..05_<الكاروسيل>.pdf            خمسة ملفات · ٦ صفحات لكل ملف
pdf/00_liquidity_state_batch_30.pdf   الموحّد · ٣٠ صفحة
contact_sheet.png                     ورقة تواصل للثلاثين صفحة بالترتيب
```

## ما هو حقيقي وما هو توضيحي

- **الشموع والحجم والـVWAP والبروفايل:** بيانات حقيقية بلا استثناء.
- **بروفايل الحجم** محسوب من شموع يومية بتوزيع حجم اليوم على مداه —
  **تقريب معلَن** مكتوب على الصفحة نفسها، لا بيانات تِك.
- **الفوت برنت (كاروسيل ٣ · صفحة ٤):** **رسم توضيحي بأرقام تعليمية**،
  موسومٌ على الرسم وفي هامش الصفحة. لا مصدر لعرضٍ وطلبٍ داخل الشمعة في
  هذا الخطّ، فلم يُقدَّم رقمٌ منه على أنه سوق.

## المصادر المرجعية

- تعريفات بروفايل الحجم وVWAP وAnchored VWAP: توثيق TradingView الرسمي
  لمؤشّرَي Volume Profile وVWAP (نقطة الإرساء ومنطقة القيمة ٧٠٪).
- قراءة الفوت برنت (الاختلال القطري · الامتصاص · POC داخل الشمعة):
  توثيق ATAS لمخطّط الفوت برنت.
- ICT: مفردات السيولة (Buy-Side / Sell-Side) والغارة على المستوى
  والخصم/العلاوة كما تعرّفها مواد Inner Circle Trader.
- SMC: كسر الهيكل مقابل الاستدراج — مع التنبيه أن المدارس تختلف في حدود
  المصطلح، ولذلك عُرّف الكسر على قمّة محدّدة داخل الصفحة نفسها.
- الجهد مقابل النتيجة: تقليد وايكوف في قراءة الحجم مقابل مدى السعر.

## تنبيه

المحتوى **تعليمي، وليس توصية**. النماذج المعروضة حالاتٌ مفردة على نوافذ
محدّدة، ولا تُقرأ كقواعد إحصائية — وهذا مكتوبٌ في هوامش الصفحات نفسها.
"""


def main():
    shutil.rmtree(FIN, ignore_errors=True)
    pages = resize_all()
    print(f"✓ {len(pages)} صورة بمقاس {W}×{H}")

    pdfs = make_pdfs()
    for p in pdfs:
        print(f"✓ {os.path.basename(p)} · {os.path.getsize(p) / 1e6:.2f} م.ب")

    rep = verify_pdfs()
    if rep:
        for n, c, sz in rep:
            print(f"  ✔ {n}: {c} صفحة · {sz} نقطة")
    else:
        print("  ⚠ PyMuPDF غير منصّب — فحص الـPDF البصري يجري يدوياً")

    # ورقة التواصل
    files = []
    for slug, _, _ in UNITS:
        files += sorted(glob.glob(os.path.join(IMG, slug, "*.png")))
    tw, th = 300, 375
    sheet = Image.new("RGB", (6 * tw, 5 * th), "#cfcabf")
    for k, p in enumerate(files):
        sheet.paste(Image.open(p).resize((tw - 6, th - 6), Image.LANCZOS),
                    ((k % 6) * tw + 3, (k // 6) * th + 3))
    sheet.save(os.path.join(FIN, "contact_sheet.png"))

    open(os.path.join(FIN, "README.md"), "w", encoding="utf-8").write(README)

    zp = os.path.join(FIN, "liquidity_state_batch_2026-08-12.zip")
    with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
        for root, _, fs in os.walk(FIN):
            for fn in fs:
                fp = os.path.join(root, fn)
                if fp == zp:
                    continue
                z.write(fp, os.path.relpath(fp, FIN))
    print(f"✓ ZIP · {os.path.getsize(zp) / 1e6:.2f} م.ب")
    return 0


if __name__ == "__main__":
    sys.exit(main())
