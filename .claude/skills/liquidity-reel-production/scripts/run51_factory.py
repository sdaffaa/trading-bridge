# -*- coding: utf-8 -*-
"""تشغيلة ٥١ — مصنع المحتوى اليومي (§11): ثلاثة كاروسيلات وخمسة أدلة.

البنية كما أقرّها فهد 2026-08-05: الكاروسيل **ثلاث صفحات** (غلاف داكن ·
الجارت البطل 1000×950 · نداء الفعل)، والشرح المكثّف في دليل PDF بكلمته.
والريلان يُبنيان في `run32_desk.py` على نافذتيهما، ولهما هنا **أدلّتهما**
وحدها — فالوحدة الواحدة تصميمٌ ودليلٌ معاً أياً كانت صيغة التصميم.

كل نافذة يومية حقيقية من `sheet_candidates.json` (الفهارس ٢٨–٣٥، مسحُ
`daily_scan.py`)، وتُفحص حرّيتها بالسجل قبل البناء وتُقيَّد بعده.

    python3 run51_factory.py [slug ...]
"""
import json, os, sys

from car_common import (CW, brandbar, counter, dots, cover_slide,
                        build_carousel, dkmap)
from guide_build import build_guide
from run15_build import X15
from run31_build import X_HERO, dk
import run15_charts as RC15
import run31_charts as RC

HERE = os.path.dirname(os.path.abspath(__file__))
CONT = os.path.normpath(os.path.join(HERE, "..", "content"))
RUN_ID = "run51-factory-2026-08-10"
TOTAL = 3
TEAL_D = "#1E627A"

# الوحدة → (فهرس النافذة، صيغة التصميم). الريلان يأخذان نافذتيهما هنا
# للدليل، وفيديوهما يُبنى في `run32_desk` على النافذة نفسها — §12 يجيز
# مشاركة نافذة الوحدة بين تصميمها ودليلها.
UNITS = {}


def _units():
    """يقرأ ملفات `content/run51_*.json` — الوحدة تُعلن نافذتها وصيغتها."""
    out = {}
    for fn in sorted(os.listdir(CONT)):
        if not (fn.startswith("run51_") and fn.endswith(".json")):
            continue
        slug = fn[len("run51_"):-len(".json")]
        with open(os.path.join(CONT, fn), encoding="utf-8") as f:
            out[slug] = json.load(f)
    return out


def hero_page(idx, body):
    return (f'<div class="slide" {CW}>{counter(idx, TOTAL)}'
            f'<div class="hwm2">LIQUIDITY STATE</div>'
            f'<div class="cont hero">{body}</div>{dots(idx, TOTAL)}</div>')


def cta_page(cta, title_html):
    """صفحة نداء الفعل — تقبل صيغتَي النصّ: المقتبَسة والمسطورة.

    الملفات القديمة تكتب `quote_a`/`quote_b`/`items`، والجديدة تكتب `line`
    وحدها. فمن لم يكتب اقتباساً يأخذ عنوان الوحدة عنواناً، ومن لم يكتب
    بنوداً لا يُرسَم له صندوقٌ فارغ."""
    qa = cta.get("quote_a")
    head = (f'{qa}<br><span style="color:{TEAL_D}">{cta.get("quote_b","")}</span>'
            if qa else title_html)
    items = "".join(f'<div class="cti"><span class="ck8">{i+1}</span><p>{t}</p></div>'
                    for i, t in enumerate(cta.get("items", [])))
    box = f'<div class="ctabox">{items}</div>' if items else ""
    tag = cta.get("tag") or cta.get("line", "")
    return f'''<div class="slide" {CW}>{counter(TOTAL, TOTAL)}{brandbar(True)}
      <div class="cta"><h1 class="big2">{head}</h1>
      <p class="tag2 center" style="margin-top:8px">{tag}</p>
      {box}
      <div class="kwbox"><span>اكتب في التعليقات</span><b>«{cta["keyword"]}»</b></div>
      <p class="tag2 center">{cta["promise"]}</p>
      <p class="tag2 center" style="opacity:.75">{cta["share"]}</p></div>
      <div class="botmeta">لغرض تعليمي · <span dir="ltr">@liquidity.state</span></div>{dots(TOTAL, TOTAL)}</div>'''


def pick(ok, name):
    for f in ok:
        if f.__name__ == name:
            return f
    raise RuntimeError(f"الحالة {name} لا تثبت على هذه النافذة: "
                       + ", ".join(f.__name__ for f in ok))


def build_car(slug, C, r, ok):
    """ثلاث صفحات: غلافٌ يحمل البطل مصغّراً، ثم البطل كبيراً، ثم النداء."""
    car = C["car"]
    ki = min(car.get("key_page", 0), len(car["pages"]) - 1)
    pg = car["pages"][ki]
    hero = pick(ok, pg["case"]) if pg.get("case") else ok[0]

    RC15.set_minimal(True)
    cover = dk(hero(r, 700, 300))
    RC15.set_minimal(False)
    slides = [cover_slide(car["eyebrow"], car["title"], car["tag"], cover, total=TOTAL)]

    RC.set_scale(1.45)
    RC.set_no_title(True)                 # العنوان في <h1> الصفحة لا داخل الرسم
    svg = hero(r, 1000, 950)
    RC.set_no_title(False)
    RC.set_scale(1.0)
    pts = "".join(f'<p class="hpt">{t}</p>' for t in pg.get("bullets", [])[:2])
    slides.append(hero_page(2, f'<h1 class="ttl9">{pg["title"]}</h1>'
                               f'<div class="chartwrap">{svg}</div>{pts}'))

    slides.append(cta_page(car["cta"], car["title"]))
    assert len(slides) == TOTAL, f"{len(slides)} صفحة والمعلن {TOTAL}"
    out = os.path.join(HERE, f"car51_{slug}.html")
    build_carousel(slides, f'{C["keyword"]} — Liquidity State', out,
                   extra_css=X15 + X_HERO)
    return out, len(slides)


def build_gd(slug, C, r, ok):
    """الدليل: جارتٌ باسمه إن سمّته الصفحة، وإلا وُزّعت الحالات بالتساوي."""
    gd = C["guide"]
    named = [p for p in gd["pages"] if p.get("chart")]
    slots = []
    if not named and ok:
        n = len(gd["pages"])
        slots = ([round(2 + i * (n - 4) / max(1, len(ok) - 1)) for i in range(len(ok))]
                 if len(ok) > 1 else [2])
    pages, tk = [], 0
    for i, p_ in enumerate(gd["pages"]):
        p = dict(title=p_["title"], paras=p_.get("paras", []))
        if p_.get("note"):
            p["note"] = p_["note"]
        if p_.get("rules"):
            p["rules"] = [dict(t=x, bad=False) if isinstance(x, str)
                          else dict(t=x["t"], bad=bool(x.get("bad")))
                          for x in p_["rules"]]
        if p_.get("chart"):
            p["svg"] = pick(ok, p_["chart"])(r, 880, 300); tk += 1
        elif tk < len(slots) and i == slots[tk]:
            p["svg"] = ok[tk](r, 880, 300); tk += 1
        pages.append(p)

    RC15.set_minimal(True)
    ghero = dk(ok[0](r, 700, 320))
    RC15.set_minimal(False)
    cfg = dict(eyebrow="دليل — " + C["car"]["eyebrow"], title=C["car"]["title"],
               keyword=C["keyword"], subtitle=gd["subtitle"], hero=ghero,
               pages=pages, outro_title=gd["outro_title"],
               outro_items=gd["outro_items"])
    out = os.path.join(HERE, f"guide51_{slug}.html")
    return out, build_guide(cfg, out), tk


def _unregister():
    """قيود هذه التشغيلة تُمسح قبل إعادة البناء — وإلا صدّت التشغيلةُ نفسَها."""
    p = os.path.join(HERE, "used_charts.json")
    d = json.load(open(p, encoding="utf-8"))
    for k in ("synthetic", "real"):
        d[k] = [e for e in d[k] if e.get("video") != RUN_ID]
    json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


def build(slug, C):
    r, ok, dropped = RC.unit_charts(C["window"])
    RC.claim_fresh(r, f"run51-{slug}")
    ns = 0
    if C.get("media") != "reel":
        _, ns = build_car(slug, C, r, ok)
    gpath, ng, tk = build_gd(slug, C, r, ok)
    RC.register(RUN_ID, r, f"run51-{slug}")
    print(f'{slug:<10} [{C["cat"]}] '
          + (f'كاروسيل {ns} صفحات · ' if ns else 'ريل (فيديوه في run32) · ')
          + f'دليل {ng} صفحة ({tk} جارتات) · كلمة «{C["keyword"]}» · نافذة {r["slug"]}'
          + ("" if not dropped else f' · سقط {len(dropped)} حالة'))


def main(slugs=None):
    units = _units()
    _unregister()
    for slug in (slugs or list(units)):
        try:
            build(slug, units[slug])
        except Exception as e:
            print(f"✗ {slug}: {type(e).__name__}: {e}")


if __name__ == "__main__":
    main(sys.argv[1:] or None)
