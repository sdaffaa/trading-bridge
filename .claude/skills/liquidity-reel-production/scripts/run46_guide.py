# -*- coding: utf-8 -*-
"""تشغيلة ٤٦ — إعادة بناء دليل «الوقت المناسب لدخول الصفقة» بهوية الحساب.

الأصل جاء مصمَّماً خارج نظامنا: لوقو مكعّب لا مجسّماً عشرينياً، وغلاف
فاتح بدل الداكن، وزوايا دائرية تخالف §5، وخطّاً غير تجوال، وزخارف
قُطرية وشبكة زرقاء ليست من النظام. وفيه تراكبات فعلية: وسمٌ فوق شارة
الترقيم، ووسمٌ مقصوص على حافّة بطاقة، ووسم عائدٍ فوق خطّ الهدف.

فأُعيد بناؤه كلّه على `guide_build` — غلاف داكن، صفحات فاتحة، تجوال،
زوايا حادّة، ولوحة ألوان §1. والمحتوى محفوظ كما هو، والجارتات نافذةٌ
حقيقية واحدة لا رسوماً تخطيطية.

    python3 run46_guide.py
"""
import json, os, sys

from car_common import dkmap
from guide_build import build_guide
import run15_charts as RC15
import run31_charts as RC

HERE = os.path.dirname(os.path.abspath(__file__))
CONT = os.path.normpath(os.path.join(HERE, "..", "content"))
RUN_ID = "run46-guide-2026-08-09"
SLUG = "dukhool"


def dk(svg):
    svg = dkmap(svg)
    for a, b in [("#FBF9F5", "#08131C"),
                 ("#EAF3F5", "rgba(67,212,220,0.10)"),
                 ("#F8ECEC", "rgba(224,86,86,0.14)")]:
        svg = svg.replace(a, b)
    return svg


def build():
    with open(os.path.join(CONT, f"run46_{SLUG}.json"), encoding="utf-8") as f:
        C = json.load(f)
    r, ok, dropped = RC.unit_charts(C["window"])
    RC.claim_fresh(r, f"run46-{SLUG}")

    gd = C["guide"]
    by_name = {f.__name__: f for f in ok}
    charts = {int(k): v for k, v in C["charts"].items()}
    missing = [v for v in charts.values() if v not in by_name]
    assert not missing, f"حالات لا تثبت على النافذة: {missing}"
    pages, tk = [], 0
    for i, p_ in enumerate(gd["pages"]):
        p = dict(title=p_["title"], paras=p_.get("paras", []))
        if p_.get("note"):
            p["note"] = p_["note"]
        if p_.get("rules"):
            p["rules"] = [dict(t=x["t"], bad=bool(x.get("bad"))) for x in p_["rules"]]
        if i in charts:
            # عنوان الرسم الداخلي يُطفأ: عنوان الصفحة يغني عنه، وإبقاؤه
            # يصطدم بشارة الحالة على يسار الرسم فيُقصّ.
            RC.set_no_title(True)
            p["svg"] = by_name[charts[i]](r, 880, 330)
            RC.set_no_title(False)
            tk += 1
        pages.append(p)

    RC15.set_minimal(True)
    hero = dk(ok[0](r, 700, 320))
    RC15.set_minimal(False)
    cfg = dict(eyebrow=C["eyebrow"], title=C["title"], keyword=C["keyword"],
               subtitle=gd["subtitle"], hero=hero, pages=pages,
               outro_title=gd["outro_title"], outro_items=gd["outro_items"])
    total = build_guide(cfg, os.path.join(HERE, f"guide46_{SLUG}.html"))
    RC.register(RUN_ID, r, f"run46-{SLUG}")
    print(f'{SLUG} · دليل {total} صفحة · جارتات {tk}/{len(ok)} · نافذة {r["slug"]}'
          + ("" if not dropped else f' · سقط {len(dropped)}'))


def _unregister():
    p = os.path.join(HERE, "used_charts.json")
    d = json.load(open(p, encoding="utf-8"))
    for k in ("synthetic", "real"):
        d[k] = [e for e in d[k] if e.get("video") != RUN_ID]
    json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    _unregister()
    build()
