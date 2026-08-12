# -*- coding: utf-8 -*-
"""تشغيلة ٥٨ — الرندر والتغليف: صور الكاروسيل ١٠٨٠×١٣٥٠ وأدلة PDF بلا فقد.

الرندر يجري بضعف الدقة ثم يُصغَّر بـLANCZOS، والـPDF يُبنى بـ`img2pdf`
لا بمسار Pillow — لأن الأخير يمرّ بـJPEG فيترك أثراً على حواف الحروف
(قيس في تشغيلة ٥٥: أقصى فرق ١٠٤ بمسار Pillow، و**صفر** بـimg2pdf).

    python3 run58_pack.py
"""
import glob, os, zipfile

import img2pdf
from PIL import Image

import car_render

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out58")
UNITS = {"muqarana": ("مقارنة", "المقارنة بالآخرين"),
         "masader": ("مصادر", "نظام المعلومات"),
         "tabyeet": ("تبييت", "تكلفة التبييت")}


def shrink(paths):
    """٢١٦٠×٢٧٠٠ → ١٠٨٠×١٣٥٠ مع تأكيد المقاس قبل وبعد."""
    out = []
    for f in paths:
        im = Image.open(f).convert("RGB")
        assert im.size == (2160, 2700), f"{f}: {im.size}"
        g = f.replace(".png", "_1080.png")
        im.resize((1080, 1350), Image.LANCZOS).save(g, "PNG", optimize=True)
        assert Image.open(g).size == (1080, 1350)
        out.append(g)
    return out


def pdf(pngs, dst, title, subject):
    lay = img2pdf.get_layout_fun((img2pdf.px_to_pt(1080, 72),
                                  img2pdf.px_to_pt(1350, 72)))
    with open(dst, "wb") as f:
        f.write(img2pdf.convert(pngs, layout_fun=lay, title=title,
                                author="Liquidity State", subject=subject))


def main():
    os.makedirs(OUT, exist_ok=True)
    for slug, (kw, name) in UNITS.items():
        d = os.path.join(OUT, f"car_{slug}")
        car_render.render(os.path.join(HERE, f"car58_{slug}.html"), d)
        pngs = shrink(sorted(glob.glob(os.path.join(d, "??.png"))))
        z = os.path.join(OUT, f"LiquidityState_{slug}_carousel.zip")
        with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as zf:
            for i, p in enumerate(pngs):
                zf.write(p, f"{i+1:02d}.png")

        g = os.path.join(OUT, f"guide_{slug}")
        car_render.render(os.path.join(HERE, f"guide58_{slug}.html"), g)
        gp = shrink(sorted(glob.glob(os.path.join(g, "??.png"))))
        dst = os.path.join(OUT, f"LiquidityState_guide_{slug}.pdf")
        pdf(gp, dst, f"Liquidity State — دليل «{kw}»", name)
        print(f'{slug:<9} كاروسيل {len(pngs)} صفحات · دليل {len(gp)} صفحة · '
              f'{os.path.getsize(dst)//1024} ك.ب')


if __name__ == "__main__":
    main()
