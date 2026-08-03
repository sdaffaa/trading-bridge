# -*- coding: utf-8 -*-
# محرك أدلة الـPDF (الليد ماغنت) — صفحات 1080×1350: غلاف غامق + صفحات فاتحة + خاتمة
# الاستخدام: from guide_build import build_guide ; build_guide(cfg, "guide_x.html")
from car_common import (CSS, FONT_CSS, GEM, CW, brandbar, INK, GREY, TEAL, TEAL_D, MUTE, CYAN)

def _cover(cfg, total):
    return f'''<div class="slide dark" {CW}>
  <div class="dhd"><div class="hgem">{GEM}</div><div class="hwm"><span class="hln"></span>LIQUIDITY STATE<span class="hln" style="transform:scaleX(-1)"></span></div></div>
  <div class="dcover">
    <div class="deyeb"><span class="dsh"></span>{cfg["eyebrow"]}<span class="dsh"></span></div>
    <h1 class="dbig">{cfg["title"]}</h1>
    <div class="tbar"></div>
    <p class="dtag">{cfg["subtitle"]}</p>
    <div class="dchart">{cfg["hero"]}</div>
  </div>
  <div class="gfoot dk">ملف «{cfg["keyword"]}» · @liquidity.state</div>
</div>'''

def _page(cfg, i, pg, total):
    rows = "".join(f'<div class="rulerow"><span class="rn{" x" if r.get("bad") else ""}">{"✗" if r.get("bad") else "✓"}</span><p>{r["t"]}</p></div>'
                   for r in pg.get("rules", []))
    svg = f'<div class="chartwrap">{pg["svg"]}</div>' if pg.get("svg") else ""
    note = f'<div class="note">{pg["note"]}</div>' if pg.get("note") else ""
    lead = f'<p class="lead">{pg["lead"]}</p>' if pg.get("lead") else ""
    tick = f'<div class="realhead"><span></span><span class="ticker">{pg["ticker"]}</span></div>' if pg.get("ticker") else ""
    extra = pg.get("html", "")
    return f'''<div class="slide" {CW}>
  {brandbar(True)}
  <div class="cont">
    <div class="numrow"><span class="num">{i}</span><h2 class="ttl">{pg["title"]}</h2></div>
    {lead}{tick}{rows}{svg}{extra}{note}
  </div>
  <div class="gfoot">دليل {cfg["keyword"]} · صفحة {i+1}/{total} · لغرض تعليمي</div>
</div>'''

def _outro(cfg, total):
    items = "".join(f'<div class="ci"><span class="ck">✓</span><p>{t}</p></div>' for t in cfg["outro_items"])
    return f'''<div class="slide" {CW}>
  {brandbar()}
  <div class="cta">
    <h1 class="big2">{cfg["outro_title"]}</h1>
    <div class="checkbox">{items}</div>
    <p class="tag2 center">تابع @liquidity.state — كل يوم درس جديد 📩</p>
  </div>
  <div class="botmeta">لغرض تعليمي</div>
</div>'''

GCSS = f'''
.gfoot{{position:absolute;bottom:54px;left:0;right:0;text-align:center;color:{MUTE};font-size:22px;font-weight:600}}
.gfoot.dk{{color:#7F97A1}}
.tblx{{width:100%;border-collapse:collapse;background:#FBF9F5;border:1px solid #DED8CC}}
.tblx th{{background:{TEAL_D};color:#fff;font-size:27px;font-weight:800;padding:14px}}
.tblx td{{font-size:27px;font-weight:600;color:{GREY};padding:13px;border-top:1px solid #EDE7DB;text-align:center}}
.tblx td b{{color:{INK};font-weight:900}}
'''

def build_guide(cfg, out_path):
    total = len(cfg["pages"]) + 2
    slides = [_cover(cfg, total)]
    for i, pg in enumerate(cfg["pages"], start=1):
        slides.append(_page(cfg, i, pg, total))
    slides.append(_outro(cfg, total))
    html = f'''<!DOCTYPE html><html lang="ar" dir="rtl"><head><meta charset="UTF-8">
<title>{cfg["title"]} — دليل</title>
<style>{FONT_CSS}\n{CSS}\n{GCSS}</style></head><body>
{''.join(slides)}
</body></html>'''
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    return total
