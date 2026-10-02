# -*- coding: utf-8 -*-
"""يُخرج الجارت الأصلي نظيفاً — بلا ماركب ولا تحليل — لكل فريم على حدة.

الغاية أن يُرى ما بُني عليه الريل كما هو: شموع السوق وحدها. أي وسم في
الريل يجب أن يُقابَل على هذه الصور فيُرى أنه مطابق للحركة لا مضاف إليها.

المصدر مكتوب على كل صورة: الرمز، الفريم، النافذة الزمنية، وعدد الشموع.
"""
import glob, os, subprocess, sys
from playwright.sync_api import sync_playwright
import topdown, tv_chart

HERE = os.path.dirname(os.path.abspath(__file__))
CHROME = glob.glob("/opt/pw-browsers/chromium-*/chrome-linux/chrome")[0]
W, H = 1400, 900
PL, PR, PT, PB = 20, 130, 96, 80
PW, PH = W - PL - PR, H - PT - PB
tv_chart.set_theme("light")
T = tv_chart.T
BULL, BEAR = "#2E8CA6", "#122F3E"

D = topdown.load()
SETS = [("1D", D["1D"]["w"], "يومي"), ("4H", D["4H"]["w"][-34:], "٤ ساعات"),
        ("1h", D["1h"]["w"], "ساعة"), ("5m", D["5m"]["w"][:48], "٥ دقائق")]


def chart(w, tf):
    lo = min(c["l"] for c in w); hi = max(c["h"] for c in w)
    pad = (hi - lo) * 0.08
    ymin, ymax = lo - pad * 1.7, hi + pad
    slot = PW / len(w)
    x = lambda i: PL + slot * i + slot / 2
    y = lambda p: PT + (ymax - p) / (ymax - ymin) * PH
    o = [f'<svg viewBox="0 0 {W} {H}" width="{W}" height="{H}" xmlns="http://www.w3.org/2000/svg">',
         f'<rect x="0" y="0" width="{W}" height="{H}" fill="{T["BG"]}"/>']
    st = tv_chart._step(ymax - ymin, 7)
    v = (int(ymin / st) + 1) * st
    while v < ymax:
        yy = y(v)
        o.append(f'<line x1="{PL}" y1="{yy:.1f}" x2="{W-PR}" y2="{yy:.1f}" '
                 f'stroke="{T["GRID"]}" stroke-width="1.3"/>'
                 f'<text x="{W-PR+10}" y="{yy+7:.1f}" fill="{T["AXTX"]}" font-size="21" '
                 f'font-weight="600" font-family="system-ui" direction="ltr">{v:,.2f}</text>')
        v += st
    step = max(1, len(w) // 8)
    for i in range(0, len(w), step):
        xx = x(i)
        if xx < PL + 46 or xx > W - PR - 40:
            continue
        lab = w[i]["d"][11:] if tf != "1D" else w[i]["d"][5:10]
        o.append(f'<line x1="{xx:.1f}" y1="{PT}" x2="{xx:.1f}" y2="{H-PB}" '
                 f'stroke="{T["GRID"]}" stroke-width="1.3"/>'
                 f'<text x="{xx:.1f}" y="{H-PB+32:.1f}" fill="{T["AXTX"]}" font-size="21" '
                 f'font-weight="600" text-anchor="middle" font-family="system-ui" '
                 f'direction="ltr">{lab}</text>')
    o.append(f'<line x1="{W-PR}" y1="{PT}" x2="{W-PR}" y2="{H-PB}" stroke="{T["AXBD"]}" stroke-width="1.6"/>'
             f'<line x1="{PL}" y1="{H-PB}" x2="{W-PR}" y2="{H-PB}" stroke="{T["AXBD"]}" stroke-width="1.6"/>')
    bw = slot * 0.62
    for i, c in enumerate(w):
        cx = x(i); col = BULL if c["c"] >= c["o"] else BEAR
        top, bot = y(max(c["o"], c["c"])), y(min(c["o"], c["c"]))
        o.append(f'<line x1="{cx:.1f}" y1="{y(c["h"]):.1f}" x2="{cx:.1f}" y2="{y(c["l"]):.1f}" '
                 f'stroke="{col}" stroke-width="2.2"/>'
                 f'<rect x="{cx-bw/2:.1f}" y="{top:.1f}" width="{bw:.1f}" '
                 f'height="{max(bot-top,2.2):.1f}" fill="{col}" rx="1"/>')
    o.append(f'<text x="{PL+4}" y="{PT-52}" fill="{T["LEGT"]}" font-size="30" font-weight="800" '
             f'font-family="system-ui" direction="ltr">{D["sym"]}  ·  {tf}</text>')
    o.append(f'<text x="{PL+4}" y="{PT-20}" fill="{T["AXTX"]}" font-size="20" font-weight="600" '
             f'font-family="system-ui" direction="ltr">{w[0]["d"]} → {w[-1]["d"]}  ·  {len(w)} bars  ·  UTC</text>')
    o.append(f'<text x="{W-PR}" y="{H-18}" fill="{T["AXTX"]}" font-size="18" font-weight="600" '
             f'text-anchor="end" font-family="Tajawal">جارت أصلي بلا ماركب — @liquidity.state</text>')
    o.append("</svg>")
    return "".join(o)


if __name__ == "__main__":
    out = []
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=CHROME, args=["--no-sandbox", "--force-color-profile=srgb"])
        pg = b.new_page(viewport={"width": W, "height": H}, device_scale_factor=2)
        for tf, w, ar in SETS:
            html = ('<html><head><meta charset="utf-8">'
                    '<link href="https://fonts.googleapis.com/css2?family=Tajawal:wght@600;800&display=swap" rel="stylesheet">'
                    '<style>body{margin:0}</style></head><body>' + chart(w, tf) + '</body></html>')
            f = os.path.join(HERE, f"_orig_{tf}.html")
            open(f, "w", encoding="utf-8").write(html)
            pg.goto("file://" + f); pg.wait_for_timeout(600)
            png = os.path.join(HERE, f"chart_orig_{tf}.png")
            pg.screenshot(path=png)
            os.remove(f)
            out.append(png)
            print(f'{tf:>3} · {ar:<8} {len(w):>3} شمعة | {w[0]["d"]} → {w[-1]["d"]}')
        b.close()
    print("\n".join(out))
