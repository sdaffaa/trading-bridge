# -*- coding: utf-8 -*-
"""تشغيلة ٤٣ — كاروسيل كامل بالنظام القديم، بلغة بسيطة.

سبع صفحات: غلاف داكن · أربع حالات لكل واحدة جارتها · خلاصة · نداء الفعل.
البناء على `car_common` و`run31_charts` — النظام نفسه قبل فيديوهات المرجع.

الحالة تُربَط بالصفحة بالاسم لا بالترتيب: نافذةٌ تسقط منها حالة تُعلن
الخطأ بدل أن تُزحزح الجارتات صفحةً فتصير الصورة تشرح درساً غير درسها.

    python3 run43_carousel.py [slug]
"""
import json, os, sys

from car_common import (CW, brandbar, counter, swipe, dots, cover_slide,
                        build_carousel, dkmap, INK, TEAL_D)
from run15_build import X15
import run15_charts as RC15
import run31_charts as RC

HERE = os.path.dirname(os.path.abspath(__file__))
CONT = os.path.normpath(os.path.join(HERE, "..", "content"))
RUN_ID = "run43-carousel-2026-08-09"
WINDOWS = {"mata": 23}
TOTAL = 7

X43 = f'''
.cont.d7{{position:absolute;top:150px;left:64px;right:64px;bottom:132px;
  display:flex;flex-direction:column;justify-content:center;gap:16px}}
.ttl7{{font-size:48px;font-weight:900;color:{INK};line-height:1.16;text-align:center;letter-spacing:-.5px}}
.ttl7 b{{color:{TEAL_D}}}
.lead7{{font-size:30px;line-height:1.52;color:#5C6C73;font-weight:600;text-align:center}}
.lead7 b{{color:{INK};font-weight:900}}
.bl7{{display:flex;flex-direction:column;gap:12px;margin-top:2px}}
.bl7 p{{display:flex;gap:14px;align-items:flex-start;text-align:right;
  font-size:28px;font-weight:700;color:#3F5561;line-height:1.44}}
.bl7 i{{flex:none;width:10px;height:10px;margin-top:13px;border-radius:50%;background:{TEAL_D}}}
.rule7{{display:flex;gap:18px;align-items:center;background:#FBF9F5;border:1px solid #DED8CC;
  padding:22px 26px;box-shadow:0 12px 30px rgba(15,46,60,0.07)}}
.rule7 span{{flex:none;width:52px;height:52px;display:flex;align-items:center;justify-content:center;
  border-radius:50%;background:{TEAL_D};color:#fff;font-size:26px;font-weight:900}}
.rule7 p{{font-size:29px;font-weight:800;color:{INK};line-height:1.4;text-align:right}}
'''


def dk(svg):
    """dkmap لا يغطي خلفيات البطاقات، فتبقى فاتحة فوق الغلاف الداكن."""
    svg = dkmap(svg)
    for a, b in [("#FBF9F5", "#08131C"),
                 ("#EAF3F5", "rgba(67,212,220,0.10)"),
                 ("#F8ECEC", "rgba(224,86,86,0.14)")]:
        svg = svg.replace(a, b)
    return svg


def pick(ok, name):
    for f in ok:
        if f.__name__ == name:
            return f
    raise RuntimeError(f"الحالة {name} لا تثبت على هذه النافذة: "
                       + ", ".join(f.__name__ for f in ok))


def page(idx, body):
    return (f'<div class="slide" {CW}>{counter(idx, TOTAL)}{brandbar(True)}'
            f'<div class="cont d7">{body}</div>{swipe()}{dots(idx, TOTAL)}</div>')


def build(slug):
    with open(os.path.join(CONT, f"run43_{slug}.json"), encoding="utf-8") as f:
        C = json.load(f)["car"]
    r, ok, dropped = RC.unit_charts(WINDOWS[slug])
    RC.claim_fresh(r, f"run43-{slug}")

    RC15.set_minimal(True)
    cover = dk(pick(ok, C["pages"][0]["case"])(r, 700, 300))
    RC15.set_minimal(False)
    slides = [cover_slide(C["eyebrow"], C["title"], C["tag"], cover, total=TOTAL)]

    for i, pg in enumerate(C["pages"]):
        body = f'<h1 class="ttl7">{pg["title"]}</h1><p class="lead7">{pg["lead"]}</p>'
        if pg.get("case"):
            RC.set_no_title(True)      # العنوان في <h1> الصفحة — لا يُكرَّر داخل الرسم
            body += f'<div class="chartwrap">{pick(ok, pg["case"])(r, 900, 300)}</div>'
            RC.set_no_title(False)
        if pg.get("bullets"):
            body += ('<div class="bl7">'
                     + "".join(f'<p><i></i>{t}</p>' for t in pg["bullets"][:2]) + '</div>')
        if pg.get("rules"):
            body += "".join(f'<div class="rule7"><span>{n+1}</span><p>{t}</p></div>'
                            for n, t in enumerate(pg["rules"]))
        slides.append(page(2 + i, body))

    cta = C["cta"]
    items = "".join(f'<div class="cti"><span class="ck8">{i+1}</span><p>{t}</p></div>'
                    for i, t in enumerate(cta["items"]))
    slides.append(f'''<div class="slide" {CW}>{counter(TOTAL, TOTAL)}{brandbar(True)}
      <div class="cta"><h1 class="big2">{cta["quote_a"]}<br><span style="color:{TEAL_D}">{cta["quote_b"]}</span></h1>
      <p class="tag2 center" style="margin-top:8px">{cta["tag"]}</p>
      <div class="ctabox">{items}</div>
      <div class="kwbox"><span>اكتب في التعليقات</span><b>«{cta["keyword"]}»</b></div>
      <p class="tag2 center">{cta["promise"]}</p>
      <p class="tag2 center" style="opacity:.75">{cta["share"]}</p></div>
      <div class="botmeta">لغرض تعليمي · <span dir="ltr">@liquidity.state</span></div>{dots(TOTAL, TOTAL)}</div>''')

    assert len(slides) == TOTAL, f"{len(slides)} صفحة والمعلن {TOTAL}"
    build_carousel(slides, f'{cta["keyword"]} — Liquidity State',
                   os.path.join(HERE, f"car43_{slug}.html"), extra_css=X15 + X43)
    RC.register(RUN_ID, r, f"run43-{slug}")
    print(f'{slug:<8} كاروسيل {len(slides)} صفحات · جارتات {len(ok)}/7 · نافذة {r["slug"]}'
          + ("" if not dropped else f' · سقط {len(dropped)}'))


def _unregister():
    p = os.path.join(HERE, "used_charts.json")
    d = json.load(open(p, encoding="utf-8"))
    for k in ("synthetic", "real"):
        d[k] = [e for e in d[k] if e.get("video") != RUN_ID]
    json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    _unregister()
    for s in (sys.argv[1:] or list(WINDOWS)):
        build(s)
