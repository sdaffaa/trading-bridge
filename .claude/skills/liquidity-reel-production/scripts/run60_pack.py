# -*- coding: utf-8 -*-
"""تشغيلة ٦٠ — الرندر والتغليف: صور الكاروسيل ١٠٨٠×١٣٥٠ وأدلة PDF بلا فقد.

الرندر يجري بضعف الدقة ثم يُصغَّر بـLANCZOS، والـPDF يُبنى بـ`img2pdf`
لا بمسار Pillow — لأن الأخير يمرّ بـJPEG فيترك أثراً على حواف الحروف
(قيس في تشغيلة ٥٥: أقصى فرق ١٠٤ بمسار Pillow، و**صفر** بـimg2pdf).

الوحدتان الفنيّتان ريلان: لهما دليلٌ بلا كاروسيل — فالتغليف يقرأ صيغة
كل وحدة من ملفّها بدل أن يفترضها.

    python3 run60_pack.py [slug ...]
"""
import glob, json, os, sys, zipfile

import img2pdf
from PIL import Image

import car_render

HERE = os.path.dirname(os.path.abspath(__file__))
CONT = os.path.normpath(os.path.join(HERE, "..", "content"))
OUT = os.path.join(HERE, "out60")


def units():
    out = {}
    for fn in sorted(os.listdir(CONT)):
        if fn.startswith("run60_") and fn.endswith(".json"):
            with open(os.path.join(CONT, fn), encoding="utf-8") as f:
                out[fn[len("run60_"):-len(".json")]] = json.load(f)
    return out


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


def main(slugs=None):
    os.makedirs(OUT, exist_ok=True)
    U = units()
    for slug in (slugs or list(U)):
        C = U[slug]
        kw = C["keyword"]
        ns = 0
        if C.get("media") != "reel":
            d = os.path.join(OUT, f"car_{slug}")
            car_render.render(os.path.join(HERE, f"car60_{slug}.html"), d)
            pngs = shrink(sorted(glob.glob(os.path.join(d, "??.png"))))
            z = os.path.join(OUT, f"LiquidityState_{slug}_carousel.zip")
            with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as zf:
                for i, p in enumerate(pngs):
                    zf.write(p, f"{i+1:02d}.png")
            ns = len(pngs)

        g = os.path.join(OUT, f"guide_{slug}")
        car_render.render(os.path.join(HERE, f"guide60_{slug}.html"), g)
        gp = shrink(sorted(glob.glob(os.path.join(g, "??.png"))))
        dst = os.path.join(OUT, f"LiquidityState_guide_{slug}.pdf")
        pdf(gp, dst, f"Liquidity State — دليل «{kw}»", C["car"]["eyebrow"])
        print(f'{slug:<9} ' + (f'كاروسيل {ns} صفحات · ' if ns else 'ريل · ')
              + f'دليل {len(gp)} صفحة · {os.path.getsize(dst)//1024} ك.ب')


if __name__ == "__main__":
    main(sys.argv[1:] or None)
