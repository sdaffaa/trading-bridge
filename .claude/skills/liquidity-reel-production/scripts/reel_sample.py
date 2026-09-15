# -*- coding: utf-8 -*-
import os, sys
from playwright.sync_api import sync_playwright
HERE=os.path.dirname(os.path.abspath(__file__))
CHROME="/opt/pw-browsers/chromium-1194/chrome-linux/chrome"
times=[float(x) for x in sys.argv[1:]] or [1.5,5.5,9.5,13.0,17.5,20.5,22.5,24.0,25.5,28.0]
os.makedirs(os.path.join(HERE,"sample"),exist_ok=True)
with sync_playwright() as p:
    b=p.chromium.launch(executable_path=CHROME,args=["--no-sandbox","--force-color-profile=srgb"])
    pg=b.new_page(viewport={"width":1080,"height":1920},device_scale_factor=1)
    pg.goto("file://"+os.path.join(HERE,"reel.html")); pg.wait_for_timeout(500)
    st=pg.query_selector("#stage")
    for t in times:
        pg.evaluate("(t)=>window.__setFrame(t)",t)
        pg.wait_for_timeout(30)
        st.screenshot(path=os.path.join(HERE,"sample",f"t{t:05.1f}.png"))
        print("shot",t)
    b.close()
print("done")
