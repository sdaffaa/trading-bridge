# -*- coding: utf-8 -*-
# رندر كاروسيل عام: python3 car_render.py file.html outdir [names,comma,separated]
import os, sys, glob
from playwright.sync_api import sync_playwright

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


def render(html_path, outdir, names=None):
    os.makedirs(outdir, exist_ok=True)
    for f in glob.glob(os.path.join(outdir, "*.png")): os.remove(f)
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=CHROME, args=["--no-sandbox", "--force-color-profile=srgb"])
        pg = b.new_page(viewport={"width": 1080, "height": 1350}, device_scale_factor=2)
        pg.goto("file://" + os.path.abspath(html_path))
        pg.wait_for_timeout(700)
        pg.evaluate(FIT_JS)   # مُلائمة تلقائية: لا صفحة تتجاوز حدودها
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
