# -*- coding: utf-8 -*-
"""تشغيلة ٤٥ — كاروسيل **صفحة واحدة** (بلا دليل — أمر فهد).

الصفحة الواحدة تجمع الغلاف والدرس ونداء الفعل، فلا نقاط سحب ولا عدّاد.
وحين لا يكون للدرس شارتٌ يشرحه — ودروسُ التنفيذ والتكلفة من هذا الصنف —
يحلّ محلّ الجارت ثلاثُ قواعد مرقّمة، لا صورةٌ تُقحَم لملء الفراغ.

    python3 run45_single.py [slug]
"""
import json, os, sys

from car_common import CW, GEM, CYAN, build_carousel

HERE = os.path.dirname(os.path.abspath(__file__))
CONT = os.path.normpath(os.path.join(HERE, "..", "content"))
UNITS = ["inzilaq"]

X45 = f'''
.one{{position:absolute;top:186px;left:66px;right:66px;bottom:104px;
  display:flex;flex-direction:column;align-items:center;text-align:center}}
.one .dbig{{margin-top:14px;font-size:70px}}
.one .tbar{{margin-top:18px;width:360px}}
.one .dtag{{margin-top:18px;font-size:32px}}
.rl1{{margin-top:30px;width:100%;display:flex;flex-direction:column;gap:14px}}
.rl1 div{{display:flex;gap:16px;align-items:center;text-align:right;
  border:1px solid rgba(67,212,220,0.30);background:rgba(67,212,220,0.05);padding:18px 22px}}
.rl1 span{{flex:none;width:46px;height:46px;display:flex;align-items:center;justify-content:center;
  border-radius:50%;background:{CYAN};color:#062028;font-size:24px;font-weight:900}}
.rl1 p{{font-size:28px;font-weight:800;color:#DCEAF0;line-height:1.4}}
.bl1{{margin-top:22px;width:100%;display:flex;flex-direction:column;gap:12px}}
.bl1 p{{display:flex;gap:14px;align-items:flex-start;text-align:right;
  font-size:28px;font-weight:700;color:#C4D7DF;line-height:1.46}}
.bl1 i{{flex:none;width:11px;height:11px;margin-top:13px;border-radius:50%;
  background:{CYAN};box-shadow:0 0 10px rgba(67,212,220,.55)}}
.kw1{{margin-top:auto;margin-bottom:2px;border:1.5px solid rgba(67,212,220,.55);
  background:rgba(67,212,220,0.08);padding:15px 46px}}
.kw1 span{{display:block;font-size:23px;color:#8FA6AF;font-weight:700}}
.kw1 b{{font-size:42px;color:{CYAN};font-weight:900}}
.one .fine{{margin-top:12px;font-size:25px;color:#A9BFC8;font-weight:600;line-height:1.45}}
.onefoot{{position:absolute;bottom:40px;left:0;right:0;text-align:center;
  color:#7F97A1;font-size:23px;font-weight:600}}
'''


def build(slug):
    with open(os.path.join(CONT, f"run45_{slug}.json"), encoding="utf-8") as f:
        C = json.load(f)
    car, cta = C["car"], C["car"]["cta"]
    rules = "".join(f'<div><span>{i+1}</span><p>{t}</p></div>'
                    for i, t in enumerate(car["rules"]))
    bl = "".join(f'<p><i></i>{t}</p>' for t in car["bullets"][:2])
    slide = f'''<div class="slide dark" {CW}>
  <div class="dhd"><div class="hgem">{GEM}</div><div class="hwm"><span class="hln"></span>LIQUIDITY STATE<span class="hln" style="transform:scaleX(-1)"></span></div></div>
  <div class="one">
    <div class="deyeb"><span class="dsh"></span>{car["eyebrow"]}<span class="dsh"></span></div>
    <h1 class="dbig">{car["title"]}</h1>
    <div class="tbar"></div>
    <p class="dtag">{car["tag"]}</p>
    <div class="rl1">{rules}</div>
    <div class="bl1">{bl}</div>
    <p class="fine">{cta["line"]}</p>
    <div class="kw1"><span>اكتب في التعليقات</span><b>«{cta["keyword"]}»</b></div>
    <p class="fine">{cta["promise"]}</p>
  </div>
  <div class="onefoot">{cta["share"]} · <span dir="ltr">@liquidity.state</span></div>
</div>'''
    build_carousel([slide], f'{C["keyword"]} — Liquidity State',
                   os.path.join(HERE, f"car45_{slug}.html"), extra_css=X45)

    print(f'{slug:<9} [{C["cat"]}] كاروسيل صفحة واحدة · كلمة «{C["keyword"]}»')


if __name__ == "__main__":
    for s in (sys.argv[1:] or UNITS):
        build(s)
