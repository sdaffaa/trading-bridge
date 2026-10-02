# -*- coding: utf-8 -*-
import os, glob
from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out_car3")
os.makedirs(OUT, exist_ok=True)
for f in glob.glob(os.path.join(OUT, "*.png")): os.remove(f)

CHROME = glob.glob("/opt/pw-browsers/chromium-*/chrome-linux/chrome")[0]
names = ["01-cover", "02-stakes", "03-what-is-fvg", "04-strong-fvg",
         "05-how-to-trade", "06-real-nasdaq", "07-quote", "08-cta"]

with sync_playwright() as p:
    b = p.chromium.launch(executable_path=CHROME, args=["--no-sandbox", "--force-color-profile=srgb"])
    pg = b.new_page(viewport={"width": 1080, "height": 1350}, device_scale_factor=2)
    pg.goto("file://" + os.path.join(HERE, "carousel3.html"))
    pg.wait_for_timeout(700)
    slides = pg.query_selector_all(".slide")
    print("found", len(slides), "slides")
    for i, s in enumerate(slides):
        out = os.path.join(OUT, f"{names[i]}.png")
        s.screenshot(path=out)
        print("saved", out)
    b.close()
print("done")
