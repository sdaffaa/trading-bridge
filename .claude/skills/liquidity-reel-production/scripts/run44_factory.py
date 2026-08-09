# -*- coding: utf-8 -*-
"""تشغيلة ٤٤ — مصنع المحتوى اليومي (§11): كاروسيلات + أدلة PDF.

كل وحدة ملفٌّ واحد في `content/run44_*.json` يحمل نصّ الكاروسيل ونصّ
الدليل معاً، فلا ينفصل الاثنان ولا تختلف كلمتُهما.

الوحدة قد تحمل نافذة حقيقية (`window`) فتُرسم جارتاتها من
`run31_charts`، وقد لا تحمل — ودروس الانضباط والمخاطر لا تحتاج جارتاً
أصلاً، فإقحامُه فيها زينةٌ تكذب لا شرحٌ يوضّح.

    python3 run44_factory.py [slug ...]
"""
import json, os, sys

from car_common import (CW, brandbar, counter, swipe, dots, cover_slide,
                        build_carousel, dkmap, INK, TEAL_D, GEM)
from guide_build import build_guide
from run15_build import X15
import run15_charts as RC15
import run31_charts as RC

HERE = os.path.dirname(os.path.abspath(__file__))
CONT = os.path.normpath(os.path.join(HERE, "..", "content"))
RUN_ID = "run44-factory-2026-08-09"
UNITS = ["ashr", "muraja", "tarabut", "barkatain"]
# وحدةٌ بلا نافذة لا جارت لها — ودروس الانضباط والمخاطر من هذا الصنف.
# ووحدة الريل تأخذ نافذتها للدليل وحده (`guide_only`)، فالفيديو مبنيٌّ
# في `run44_reel.py` ولا يُبنى لها كاروسيل.
WINDOWS = {"barkatain": 27}

X44 = f'''
.cont.d7{{position:absolute;top:150px;left:64px;right:64px;bottom:132px;
  display:flex;flex-direction:column;justify-content:center;gap:18px}}
.ttl7{{font-size:50px;font-weight:900;color:{INK};line-height:1.16;text-align:center;letter-spacing:-.5px}}
.ttl7 b{{color:{TEAL_D}}}
.lead7{{font-size:31px;line-height:1.54;color:#5C6C73;font-weight:600;text-align:center}}
.lead7 b{{color:{INK};font-weight:900}}
.bl7{{display:flex;flex-direction:column;gap:14px;margin-top:4px}}
.bl7 p{{display:flex;gap:14px;align-items:flex-start;text-align:right;
  font-size:29px;font-weight:700;color:#3F5561;line-height:1.44}}
.bl7 i{{flex:none;width:10px;height:10px;margin-top:14px;border-radius:50%;background:{TEAL_D}}}
.rule7{{display:flex;gap:18px;align-items:center;background:#FBF9F5;border:1px solid #DED8CC;
  padding:22px 26px;box-shadow:0 12px 30px rgba(15,46,60,0.07)}}
.rule7 span{{flex:none;width:52px;height:52px;display:flex;align-items:center;justify-content:center;
  border-radius:50%;background:{TEAL_D};color:#fff;font-size:26px;font-weight:900}}
.rule7 p{{font-size:29px;font-weight:800;color:{INK};line-height:1.4;text-align:right}}
/* بلا جارت يبقى النصف السفلي فارغاً، فيُوسَّط الغلاف على ما بين الترويسة
   وزرّ السحب بدل تثبيته أعلى الصفحة. */
.dcover.notx{{top:190px;bottom:200px;justify-content:center}}
.dcover.notx .dbig{{font-size:96px}}
.dcover.notx .dtag{{margin-top:34px;font-size:36px}}
'''


def dk(svg):
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
    raise RuntimeError(f"الحالة {name} لا تثبت: " + ", ".join(f.__name__ for f in ok))


def cover_notx(eyeb, title, tag, total):
    """غلاف بلا جارت — للدروس التي لا شارت لها. لا فراغ يُملأ بزينة."""
    return f'''<div class="slide dark" {CW}>
  {counter(1, total)}
  <div class="dhd"><div class="hgem">{GEM}</div><div class="hwm"><span class="hln"></span>LIQUIDITY STATE<span class="hln" style="transform:scaleX(-1)"></span></div></div>
  <div class="dcover notx">
    <div class="deyeb"><span class="dsh"></span>{eyeb}<span class="dsh"></span></div>
    <h1 class="dbig">{title}</h1>
    <div class="tbar"></div>
    <p class="dtag">{tag}</p>
  </div>
  {swipe(True)}{dots(1, total, dark=True)}
</div>'''


def build_carousel_unit(slug, C, r, ok):
    car = C["car"]
    total = len(car["pages"]) + 2
    if r is None:
        slides = [cover_notx(car["eyebrow"], car["title"], car["tag"], total)]
    else:
        RC15.set_minimal(True)
        hero = dk(pick(ok, car["pages"][0]["case"])(r, 700, 300))
        RC15.set_minimal(False)
        slides = [cover_slide(car["eyebrow"], car["title"], car["tag"], hero, total=total)]

    for i, pg in enumerate(car["pages"]):
        body = f'<h1 class="ttl7">{pg["title"]}</h1><p class="lead7">{pg["lead"]}</p>'
        if pg.get("case") and r is not None:
            RC.set_no_title(True)
            body += f'<div class="chartwrap">{pick(ok, pg["case"])(r, 900, 300)}</div>'
            RC.set_no_title(False)
        if pg.get("bullets"):
            body += ('<div class="bl7">'
                     + "".join(f'<p><i></i>{t}</p>' for t in pg["bullets"][:2]) + '</div>')
        if pg.get("rules"):
            body += "".join(f'<div class="rule7"><span>{n+1}</span><p>{t}</p></div>'
                            for n, t in enumerate(pg["rules"]))
        slides.append(f'<div class="slide" {CW}>{counter(2 + i, total)}{brandbar(True)}'
                      f'<div class="cont d7">{body}</div>{swipe()}{dots(2 + i, total)}</div>')

    cta = car["cta"]
    items = "".join(f'<div class="cti"><span class="ck8">{i+1}</span><p>{t}</p></div>'
                    for i, t in enumerate(cta["items"]))
    slides.append(f'''<div class="slide" {CW}>{counter(total, total)}{brandbar(True)}
      <div class="cta"><h1 class="big2">{cta["quote_a"]}<br><span style="color:{TEAL_D}">{cta["quote_b"]}</span></h1>
      <p class="tag2 center" style="margin-top:8px">{cta["tag"]}</p>
      <div class="ctabox">{items}</div>
      <div class="kwbox"><span>اكتب في التعليقات</span><b>«{cta["keyword"]}»</b></div>
      <p class="tag2 center">{cta["promise"]}</p>
      <p class="tag2 center" style="opacity:.75">{cta["share"]}</p></div>
      <div class="botmeta">لغرض تعليمي · <span dir="ltr">@liquidity.state</span></div>{dots(total, total)}</div>''')

    assert len(slides) == total, f"{len(slides)} != {total}"
    build_carousel(slides, f'{cta["keyword"]} — Liquidity State',
                   os.path.join(HERE, f"car44_{slug}.html"), extra_css=X15 + X44)
    return total


def build_guide_unit(slug, C, r, ok):
    gd = C["guide"]
    pages, tk = [], 0
    slots = []
    if r is not None and ok:
        n = len(gd["pages"])
        slots = ([round(2 + i * (n - 4) / max(1, len(ok) - 1)) for i in range(len(ok))]
                 if len(ok) > 1 else [2])
    for i, p_ in enumerate(gd["pages"]):
        p = dict(title=p_["title"], paras=p_.get("paras", []))
        if p_.get("note"):
            p["note"] = p_["note"]
        if p_.get("rules"):
            p["rules"] = [dict(t=x["t"], bad=bool(x.get("bad"))) for x in p_["rules"]]
        if tk < len(slots) and i == slots[tk]:
            p["svg"] = ok[tk](r, 880, 330); tk += 1
        pages.append(p)
    if r is None:
        ghero = ('<div style="height:150px"></div>')     # غلاف الدليل بلا جارت كذلك
    else:
        RC15.set_minimal(True); ghero = dk(ok[0](r, 700, 320)); RC15.set_minimal(False)
    cfg = dict(eyebrow="دليل — " + C["car"]["eyebrow"], title=C["car"]["title"],
               keyword=C["keyword"], subtitle=gd["subtitle"], hero=ghero, pages=pages,
               outro_title=gd["outro_title"], outro_items=gd["outro_items"])
    return build_guide(cfg, os.path.join(HERE, f"guide44_{slug}.html")), tk


def build(slug):
    with open(os.path.join(CONT, f"run44_{slug}.json"), encoding="utf-8") as f:
        C = json.load(f)
    r = ok = None
    if slug in WINDOWS:
        r, ok, _ = RC.unit_charts(WINDOWS[slug])
        RC.claim_fresh(r, f"run44-{slug}")
    ns = 0 if C.get("guide_only") else build_carousel_unit(slug, C, r, ok)
    ng, tk = build_guide_unit(slug, C, r, ok)
    if r is not None:
        RC.register(RUN_ID, r, f"run44-{slug}")
    print(f'{slug:<9} [{C["cat"]}] ' + (f'كاروسيل {ns} صفحات · ' if ns else 'ريل · ') + f'دليل {ng} صفحة · '
          f'كلمة «{C["keyword"]}»' + ('' if r is None else f' · نافذة {r["slug"]}'))


def _unregister():
    p = os.path.join(HERE, "used_charts.json")
    d = json.load(open(p, encoding="utf-8"))
    for k in ("synthetic", "real"):
        d[k] = [e for e in d[k] if e.get("video") != RUN_ID]
    json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    _unregister()
    for s in (sys.argv[1:] or UNITS):
        try:
            build(s)
        except Exception as e:
            print(f"✗ {s}: {type(e).__name__}: {e}")
