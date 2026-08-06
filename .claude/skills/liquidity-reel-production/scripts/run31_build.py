# -*- coding: utf-8 -*-
"""تشغيلة ٣١ — مصنع المحتوى اليومي: ٣ كاروسيلات + ٢ ريلات، ولكل وحدة دليل PDF.

البنية تتبع §11 و§12 و§184: الكاروسيل **ثلاث صفحات** (غلاف داكن · الجارت
البطل · نداء الفعل)، والشرح المكثّف كله في دليل من ١٦ صفحة. الريل ≤22.4
ثانية بمؤثرات فقط من `assets/sfx` (§12) — لا كلام منطوق ولا ريل صامت.

الجارتات كلها **نوافذ حقيقية** من `sheet_candidates.json` عبر
`run31_charts` — نافذة واحدة لكل وحدة، والحالات داخلها متمايزة ومُثبَتة
بـ`assert` على الشموع نفسها. الحالة التي لا تثبت تُسقط ويُعلَن عددها.

    python3 run31_build.py            # كل الوحدات
    python3 run31_build.py <slug> ... # وحدات بعينها
"""
import json, os, sys

from car_common import (CW, brandbar, counter, dots, cover_slide, build_carousel,
                        dkmap, INK, TEAL_D)
from guide_build import build_guide
from run15_build import X15
import run15_charts as RC15
import run31_charts as RC
import chart_registry

HERE = os.path.dirname(os.path.abspath(__file__))
CONT = os.path.normpath(os.path.join(HERE, "..", "content"))
RUN_ID = "run31-daily-2026-08-06"
TOTAL = 3

X_HERO = '''
.ttl9{font-size:44px;font-weight:900;color:#0F2E3C;line-height:1.14;text-align:center;letter-spacing:-.5px}
.ttl9 b{color:#1E627A}
.hpt{font-size:25px;font-weight:700;color:#5C6C73;text-align:center;line-height:1.4;margin-top:2px}
.hpt b{color:#0F2E3C;font-weight:900}
.hwm2{position:absolute;top:64px;right:80px;z-index:6;font-size:20px;font-weight:700;
  letter-spacing:5px;color:#1E627A;opacity:.72}
'''


def dk(svg):
    """dkmap لا يغطي خلفيات البطاقات، فتبقى فاتحة فوق الغلاف الداكن."""
    svg = dkmap(svg)
    for a, b in [("#FBF9F5", "#08131C"),
                 ("#EAF3F5", "rgba(67,212,220,0.10)"),
                 ("#F8ECEC", "rgba(224,86,86,0.14)")]:
        svg = svg.replace(a, b)
    return svg


def hero_page(idx, body):
    return (f'<div class="slide" {CW}>{counter(idx, TOTAL)}'
            f'<div class="hwm2">LIQUIDITY STATE</div>'
            f'<div class="cont hero">{body}</div>{dots(idx, TOTAL)}</div>')


# نافذة حقيقية واحدة لكل وحدة (فهارس `sheet_candidates.json`) — اختيرت بعد
# فحص كم حالة تثبت على كل نافذة، ولا تتكرر أداة/فريم/تاريخ بين وحدتين.
WINDOWS = {}
MEDIA = {}


def load(slug):
    """يقرأ ملف المحتوى ويشتق الحقول التشغيلية منه بدل تكرارها يدوياً."""
    with open(os.path.join(CONT, f"run31_{slug}.json"), encoding="utf-8") as f:
        C = json.load(f)
    C.setdefault("kw", C["car"]["cta"]["keyword"])
    C.setdefault("gtitle", C["car"]["title"])
    C.setdefault("geyebrow", "دليل — " + C["car"]["eyebrow"])
    C.setdefault("window", WINDOWS[slug])
    C.setdefault("media", MEDIA.get(slug, "reel" if C.get("reel") else "carousel"))
    return C


def charts_for(C):
    """الحالات الصالحة على نافذة الوحدة — مرتّبة، وما سقط يُعاد مع السبب."""
    r, ok, dropped = RC.unit_charts(C["window"])
    return r, ok, dropped


def build_carousel_unit(slug, C, r, ok):
    car = C["car"]
    RC15.set_minimal(True)
    cover = dk(ok[0](r, 700, 300))
    RC15.set_minimal(False)
    slides = [cover_slide(car["eyebrow"], car["title"], car["tag"], cover, total=TOTAL)]

    ki = min(car.get("key_page", 0), len(ok) - 1)
    pg = car["pages"][min(car.get("key_page", 0), len(car["pages"]) - 1)]
    RC.set_scale(1.45)
    svg = ok[ki](r, 1000, 950)
    RC.set_scale(1.0)
    pts = "".join(f'<p class="hpt">{t}</p>' for t in pg.get("bullets", [])[:2])
    slides.append(hero_page(2, f'<h1 class="ttl9">{pg["title"]}</h1>'
                               f'<div class="chartwrap">{svg}</div>{pts}'))

    cta = car["cta"]
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
    build_carousel(slides, f'{C["kw"]} — Liquidity State',
                   os.path.join(HERE, f"car31_{slug}.html"), extra_css=X15 + X_HERO)
    return len(slides)


def build_guide_unit(slug, C, r, ok):
    gd = C["guide"]
    # الجارتات تُوزَّع على صفحات المتن بالتساوي بدل ربطها بعنوان بعينه —
    # ربطُها بكلمة «الصفقة» كان يسقط كل الجارتات إذا سمّى الكاتب صفحاته بغيرها.
    n = len(gd["pages"])
    slots = [round(2 + i * (n - 4) / max(1, len(ok) - 1)) for i in range(len(ok))] \
        if len(ok) > 1 else [2]
    pages, tk = [], 0
    for i, p_ in enumerate(gd["pages"]):
        p = dict(title=p_["title"], paras=p_.get("paras", []))
        if p_.get("note"):
            p["note"] = p_["note"]
        if tk < len(ok) and i == slots[tk]:
            p["svg"] = ok[tk](r, 880, 260); tk += 1
        pages.append(p)
    RC15.set_minimal(True)
    ghero = dk(ok[0](r, 700, 320))
    RC15.set_minimal(False)
    cfg = dict(eyebrow=C["geyebrow"], title=C["gtitle"], keyword=C["kw"],
               subtitle=gd["subtitle"], hero=ghero, pages=pages,
               outro_title=gd["outro_title"], outro_items=gd["outro_items"])
    n = build_guide(cfg, os.path.join(HERE, f"guide31_{slug}.html"))
    return n, tk


def build_unit(slug):
    C = load(slug)
    r, ok, dropped = charts_for(C)
    if not ok:
        raise RuntimeError(f"{slug}: لا حالة تثبت على النافذة {C['window']}")
    RC.claim_fresh(r, f"run31-{slug}")
    ns = build_carousel_unit(slug, C, r, ok) if C["media"] == "carousel" else 0
    ng, tk = build_guide_unit(slug, C, r, ok)
    RC.register(RUN_ID, r, f"run31-{slug}")
    print(f'{slug:<10} {C["media"]:<8} كاروسيل {ns} صفحات · دليل {ng} صفحة · '
          f'جارتات {len(ok)}/6 · نافذة {r["slug"]}'
          + ("" if not dropped else f' · سقط {len(dropped)}'))
    return C, r, ok, dropped


def _unregister():
    p = os.path.join(HERE, "used_charts.json")
    d = json.load(open(p, encoding="utf-8"))
    for k in ("synthetic", "real"):
        d[k] = [e for e in d[k] if e.get("video") != RUN_ID]
    json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    _unregister()
    slugs = sys.argv[1:] or [f[7:-5] for f in sorted(os.listdir(CONT))
                             if f.startswith("run31_") and f.endswith(".json")]
    for s in slugs:
        try:
            build_unit(s)
        except Exception as e:
            print(f"✗ {s}: {type(e).__name__}: {e}")
