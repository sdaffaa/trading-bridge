# -*- coding: utf-8 -*-
# رندر دليل HTML → PDF (سكرينشوت كل صفحة بدقة 2x ثم دمج PIL)
# python3 guide_render.py guide_x.html out.pdf
import os, sys, glob
from playwright.sync_api import sync_playwright
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
CHROME = glob.glob("/opt/pw-browsers/chromium-*/chrome-linux/chrome")[0]

FIT_JS = """() => {
  document.querySelectorAll('.slide .cont').forEach(c => {
    const st = getComputedStyle(c);
    const gap = parseFloat(st.rowGap || st.gap || 0) || 0;
    let h = 0, n = 0;
    c.querySelectorAll(':scope > *').forEach(e => { h += e.getBoundingClientRect().height; n++; });
    h += gap * Math.max(0, n - 1);
    const avail = c.clientHeight;
    if (h > avail + 2) {
      const k = Math.max(0.60, (avail - 4) / h);
      c.style.justifyContent = 'flex-start';
      c.style.transformOrigin = 'top center';
      c.style.transform = 'scale(' + k.toFixed(4) + ')';
      c.style.width = (100 / k) + '%';
      c.style.marginLeft = (-(100 / k - 100) / 2) + '%';
    }
  });
  return true;
}"""


def render(html_path, pdf_path, scale=2):
    tmpdir = pdf_path + ".pages"
    os.makedirs(tmpdir, exist_ok=True)
    for f in glob.glob(os.path.join(tmpdir, "*.png")): os.remove(f)
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=CHROME, args=["--no-sandbox", "--force-color-profile=srgb"])
        pg = b.new_page(viewport={"width": 1080, "height": 1350}, device_scale_factor=scale)
        pg.goto("file://" + os.path.abspath(html_path))
        pg.wait_for_timeout(700)
        pg.evaluate(FIT_JS)   # مُلائمة تلقائية: لا صفحة تتجاوز حدودها
        slides = pg.query_selector_all(".slide")
        paths = []
        for i, s in enumerate(slides):
            out = os.path.join(tmpdir, f"p{i:02d}.png")
            s.screenshot(path=out); paths.append(out)
        b.close()
    imgs = [Image.open(x).convert("RGB") for x in paths]
    imgs[0].save(pdf_path, save_all=True, append_images=imgs[1:], resolution=180)
    for x in paths: os.remove(x)
    os.rmdir(tmpdir)
    return len(imgs)

if __name__ == "__main__":
    n = render(sys.argv[1], sys.argv[2])
    print("pdf pages:", n, "->", sys.argv[2])
