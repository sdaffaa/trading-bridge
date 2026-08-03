# -*- coding: utf-8 -*-
# رندر كاروسيل عام: python3 car_render.py file.html outdir [names,comma,separated]
import os, sys, glob
from playwright.sync_api import sync_playwright

CHROME = glob.glob("/opt/pw-browsers/chromium-*/chrome-linux/chrome")[0]

def render(html_path, outdir, names=None):
    os.makedirs(outdir, exist_ok=True)
    for f in glob.glob(os.path.join(outdir, "*.png")): os.remove(f)
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=CHROME, args=["--no-sandbox", "--force-color-profile=srgb"])
        pg = b.new_page(viewport={"width": 1080, "height": 1350}, device_scale_factor=2)
        pg.goto("file://" + os.path.abspath(html_path))
        pg.wait_for_timeout(700)
        slides = pg.query_selector_all(".slide")
        outs = []
        for i, s in enumerate(slides):
            nm = names[i] if names and i < len(names) else f"{i+1:02d}"
            out = os.path.join(outdir, f"{i+1:02d}-{nm}.png" if names else f"{i+1:02d}.png")
            s.screenshot(path=out); outs.append(out)
        b.close()
    return outs

if __name__ == "__main__":
    names = sys.argv[3].split(",") if len(sys.argv) > 3 else None
    outs = render(sys.argv[1], sys.argv[2], names)
    print(len(outs), "slides ->", sys.argv[2])
