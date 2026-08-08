# -*- coding: utf-8 -*-
"""تشغيلة ٤٢ — كاروسيل **من صفحة واحدة** + دليل PDF لكل وحدة.

النظام هنا هو النظام القديم نفسه قبل فيديوهات المرجع: `car_common` للغلاف
الداكن وقواعده، و`run31_charts` للنوافذ الحقيقية، و`guide_build` +
`guide_render` للدليل. الجديد الوحيد أن الكاروسيل صفحة واحدة، فالغلاف
والدرس ونداء الفعل يجتمعون فيها — ولذلك لا نقاط سحب ولا عدّاد صفحات.

    python3 run42_single.py            # الوحدات الثلاث
    python3 run42_single.py <slug> ...
"""
import json, os, sys

from car_common import (CW, GEM, CYAN, build_carousel, dkmap)
from guide_build import build_guide
import run15_charts as RC15
import run31_charts as RC

HERE = os.path.dirname(os.path.abspath(__file__))
CONT = os.path.normpath(os.path.join(HERE, "..", "content"))
RUN_ID = "run42-single-2026-08-08"

# نافذة حقيقية واحدة لكل وحدة (فهارس `sheet_candidates.json`) — لا تتكرر
# أداة ولا فريم ولا تاريخ بين وحدتين.
WINDOWS = {"omq": 20, "mustahlaka": 22, "amal": 21}

X42 = f'''
.one{{position:absolute;top:194px;left:66px;right:66px;bottom:104px;
  display:flex;flex-direction:column;align-items:center;text-align:center}}
.one .dbig{{margin-top:14px;font-size:68px}}
.one .tbar{{margin-top:16px;width:360px}}
.one .dtag{{margin-top:16px;font-size:32px}}
.one .dchart{{margin-top:14px}}
.one .dchart svg{{width:100%}}
.bl1{{margin-top:18px;width:100%;display:flex;flex-direction:column;gap:12px}}
.bl1 p{{display:flex;gap:14px;align-items:flex-start;text-align:right;
  font-size:29px;font-weight:700;color:#C4D7DF;line-height:1.46}}
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


def dk(svg):
    """dkmap لا يغطي خلفيات البطاقات، فتبقى فاتحة فوق الغلاف الداكن."""
    svg = dkmap(svg)
    for a, b in [("#FBF9F5", "#08131C"),
                 ("#EAF3F5", "rgba(67,212,220,0.10)"),
                 ("#F8ECEC", "rgba(224,86,86,0.14)")]:
        svg = svg.replace(a, b)
    return svg


def load(slug):
    with open(os.path.join(CONT, f"run42_{slug}.json"), encoding="utf-8") as f:
        C = json.load(f)
    C.setdefault("kw", C["car"]["cta"]["keyword"])
    C.setdefault("gtitle", C["car"]["title"])
    C.setdefault("geyebrow", "دليل — " + C["car"]["eyebrow"])
    C.setdefault("window", WINDOWS[slug])
    return C


def pick(ok, name):
    """حالة الوحدة بالاسم — وإن لم تثبت على النافذة، فالخطأ يُعلَن لا يُخفى."""
    for f in ok:
        if f.__name__ == name:
            return f
    raise RuntimeError(f"الحالة {name} لا تثبت على هذه النافذة: "
                       + ", ".join(f.__name__ for f in ok))


def build_card(slug, C, r, hero):
    car = C["car"]
    RC.set_no_title(True)          # العنوان في <h1> الصفحة — لا يُكرَّر داخل الرسم
    svg = dk(hero(r, 900, 340))
    RC.set_no_title(False)
    bl = "".join(f'<p><i></i>{t}</p>' for t in car["bullets"][:2])
    cta = car["cta"]
    slide = f'''<div class="slide dark" {CW}>
  <div class="dhd"><div class="hgem">{GEM}</div><div class="hwm"><span class="hln"></span>LIQUIDITY STATE<span class="hln" style="transform:scaleX(-1)"></span></div></div>
  <div class="one">
    <div class="deyeb"><span class="dsh"></span>{car["eyebrow"]}<span class="dsh"></span></div>
    <h1 class="dbig">{car["title"]}</h1>
    <div class="tbar"></div>
    <p class="dtag">{car["tag"]}</p>
    <div class="dchart">{svg}</div>
    <div class="bl1">{bl}</div>
    <p class="fine">{cta["line"]}</p>
    <div class="kw1"><span>اكتب في التعليقات</span><b>«{cta["keyword"]}»</b></div>
    <p class="fine">{cta["promise"]}</p>
  </div>
  <div class="onefoot">{cta["share"]} · <span dir="ltr">@liquidity.state</span></div>
</div>'''
    build_carousel([slide], f'{C["kw"]} — Liquidity State',
                   os.path.join(HERE, f"car42_{slug}.html"), extra_css=X42)
    return 1


def build_guide_unit(slug, C, r, ok):
    gd = C["guide"]
    # الجارتات تُوزَّع على صفحات المتن بالتساوي بدل ربطها بعنوان بعينه.
    n = len(gd["pages"])
    slots = ([round(2 + i * (n - 4) / max(1, len(ok) - 1)) for i in range(len(ok))]
             if len(ok) > 1 else [2])
    pages, tk = [], 0
    for i, p_ in enumerate(gd["pages"]):
        p = dict(title=p_["title"], paras=p_.get("paras", []))
        if p_.get("note"):
            p["note"] = p_["note"]
        if p_.get("rules"):
            p["rules"] = [dict(t=x["t"], bad=bool(x.get("bad"))) for x in p_["rules"]]
        if tk < len(ok) and i == slots[tk]:
            p["svg"] = ok[tk](r, 880, 330); tk += 1   # أطول من ٢٦٠ ليملأ صفحة `dense`
        pages.append(p)
    RC15.set_minimal(True)
    ghero = dk(ok[0](r, 700, 320))
    RC15.set_minimal(False)
    cfg = dict(eyebrow=C["geyebrow"], title=C["gtitle"], keyword=C["kw"],
               subtitle=gd["subtitle"], hero=ghero, pages=pages,
               outro_title=gd["outro_title"], outro_items=gd["outro_items"])
    return build_guide(cfg, os.path.join(HERE, f"guide42_{slug}.html")), tk


def build_unit(slug):
    C = load(slug)
    r, ok, dropped = RC.unit_charts(C["window"])
    if not ok:
        raise RuntimeError(f"{slug}: لا حالة تثبت على النافذة {C['window']}")
    hero = pick(ok, C["car"]["case"])
    RC.claim_fresh(r, f"run42-{slug}")
    ns = build_card(slug, C, r, hero)
    ng, tk = build_guide_unit(slug, C, r, ok)
    RC.register(RUN_ID, r, f"run42-{slug}")
    print(f'{slug:<12} كاروسيل {ns} صفحة · دليل {ng} صفحة · جارتات {len(ok)}/7 '
          f'(منها {tk} في الدليل) · نافذة {r["slug"]}'
          + ("" if not dropped else f' · سقط {len(dropped)}'))
    return C, r, ok


def _unregister():
    p = os.path.join(HERE, "used_charts.json")
    d = json.load(open(p, encoding="utf-8"))
    for k in ("synthetic", "real"):
        d[k] = [e for e in d[k] if e.get("video") != RUN_ID]
    json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    _unregister()
    for s in (sys.argv[1:] or list(WINDOWS)):
        try:
            build_unit(s)
        except Exception as e:
            print(f"✗ {s}: {type(e).__name__}: {e}")
