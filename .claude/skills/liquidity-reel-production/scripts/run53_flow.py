# -*- coding: utf-8 -*-
"""تشغيلة ٥٣ — كاروسيل «خطوات الصفقة من الدخول إلى الهدف» مع بكس الهدف.

🔒 طلب فهد 2026-08-11: «ابي كاروسيل خطوات دخول الصفقة الى الوصول للهدف مع
رسم بكس هدف». فالبنية ست صفحات: غلاف · أربع خطوات · نداء الفعل، والخطوة
الثالثة هي **البكس** — صندوق أحمر من الدخول للوقف وصندوق تيل من الدخول
للهدف، كأداة الصفقة على المنصّة.

والخطّة كلها **تُشتقّ من الشموع بقواعد معلنة، لا تُكتب باليد**:

    المنطقة  = شمعة الأصل `iob`: من قاعها إلى فتحها
    الدخول   = إغلاق **أول شمعة تصكّر فوق سقف المنطقة** بعد اللمسة
    الوقف    = قاع المنطقة − ١٫٥٪ من مدى النافذة (هامش `c_stop` نفسه)
    الهدف    = **قمة الاندفاع** التي سبقت الرجعة (أعلى قمة بين الكسر واللمسة)

ثم تُفحص الخطة على الشموع قبل أن تُرسم: الهدف لا بد أن يُبلَغ داخل النافذة،
والوقف لا بد أن ينجو حتى بلوغه. ما لا يثبت يُسقط الوحدة كلها ولا يُجمَّل.

    python3 run53_flow.py
"""
import json, os, sys

from reel_build import INK, TEAL, TEAL_D, RED, GREY, htext
from run15_charts import zbox, tick, hl, badge
from car_common import (CW, brandbar, counter, dots, cover_slide, build_carousel)
from run15_build import X15
from run31_build import X_HERO, dk
import run15_charts as RC15
import run31_charts as RC

HERE = os.path.dirname(os.path.abspath(__file__))
CONT = os.path.normpath(os.path.join(HERE, "..", "content"))
RUN_ID = "run53-flow-2026-08-11"
TOTAL = 6


# ═══════════ الخطة: تُحسب من الشموع ولا تُملى عليها ═══════════
def plan(r):
    W, iob, ir, bk = r["w"], r["iob"], r["ir"], r["bk"]
    zt, zb = W[iob]["o"], W[iob]["l"]
    rng = max(c["h"] for c in W) - min(c["l"] for c in W)
    stop = zb - rng * 0.015

    ei = next((j for j in range(ir, len(W)) if W[j]["c"] > zt), None)
    assert ei is not None, "لا شمعة تصكّر فوق سقف المنطقة بعد اللمسة"
    ent = W[ei]["c"]

    pi = max(range(bk, ir), key=lambda j: W[j]["h"])
    tgt = W[pi]["h"]
    assert tgt > ent, "قمة الاندفاع تحت الدخول — لا مسافة للهدف"

    hi = RC.hit_above(W, ei, tgt)
    assert hi is not None, "الهدف لم يُبلَغ داخل النافذة"
    low_after = min(c["l"] for c in W[ei + 1:hi + 1])
    assert low_after > stop, "الوقف ضُرب قبل الهدف — الخطة لا تثبت"

    # الشموع التي قضاها السعر داخل المنطقة قبل الإغلاق فوقها
    ins = [j for j in range(ir, ei) if zb <= W[j]["c"] <= zt]
    deep = min(range(ir, ei + 1), key=lambda j: W[j]["l"])

    return dict(zt=zt, zb=zb, stop=stop, ei=ei, ent=ent, pi=pi, tgt=tgt, hi=hi,
                low_after=low_after, ins=ins, deep=deep,
                risk=RC.pips(r, ent, stop), rew=RC.pips(r, tgt, ent),
                rr=(tgt - ent) / (ent - stop), bars=hi - ei)


def _lvl(x0, x1, y, txt, col, dash=None, w=2.0, up=True):
    """مستوى ممتدّ على عرض اللوحة، ووسمه راسياً على حافته اليسرى.

    الوسم بـ`anchor="end"`: في النصّ العربي «النهاية» هي أقصى اليسار، فيثبت
    الطرف الأيسر عند 22 ويمتدّ النصّ يميناً مهما طال — والتوسيط كان يدفع
    الجملة الطويلة خارج اللوحة فتُقصّ."""
    return hl(x0, x1, y, col, w, dash) + htext(22, y - 11 if up else y + 22,
                                               txt, col, round(19 * RC._SC[0]),
                                               anchor="end")


# ═══════════ الخطوات الأربع ═══════════
def s2_touch(r, Wd=1000, H=760):
    """٢ · اللمسة: السعر يدخل المنطقة ويتفاوض داخلها قبل أن يصكّر فوقها."""
    W, P = r["w"], plan(r)
    svg, x, y, slot = RC._geo(W, Wd, H)
    svg += zbox(x(r["iob"]) - slot * .6, y(P["zt"]), x(P["ei"]) + slot * .5,
                y(P["zb"]), "منطقة الأصل")
    svg += f'<circle cx="{x(r["ir"]):.1f}" cy="{y(W[r["ir"]]["l"]):.1f}" r="12" ' \
           f'fill="none" stroke="{TEAL_D}" stroke-width="3"/>'
    # وسم الوقف **فوق** خطّه: الخطّ يجلس عند حافة اللوحة السفلى، فما تحته
    # خارج مساحة الرسم — والوسم هناك يُقصّ.
    svg += _lvl(14, Wd - 18, y(P["stop"]),
                f'الوقف {P["stop"]:.2f} — لم يُلمَس', RED, "7 6", 1.8)
    svg += hl(x(P["deep"]) - slot * .5, x(P["deep"]) + slot * .5,
              y(W[P["deep"]]["l"]), INK, 2.6)
    svg += htext(x(P["deep"]), y(W[P["deep"]]["l"]) - 16,
                 f'أعمق قاع {W[P["deep"]]["l"]:.2f}', INK, round(18 * RC._SC[0]))
    svg += RC._title(Wd, "المنطقة مكان تفاوض لا نقطة واحدة")
    svg += RC._why(Wd, H, f'قعد {len(P["ins"])} شمعات داخل المنطقة قبل ما يصكّر فوقها', TEAL_D)
    svg += RC._sum(Wd, H, f'ومع ذلك بقي الوقف بعيداً '
                          f'{RC.pips(r, W[P["deep"]]["l"], P["stop"])} نقطة تحت أعمق قاع')
    return svg + badge(Wd, "الخطوة ٢ — اللمسة", True) + "</svg>"


def _box(r, P, Wd, H, road=False):
    """بكس الصفقة: أحمر من الدخول للوقف، وتيل من الدخول للهدف."""
    W = r["w"]
    svg, x, y, slot = RC._geo(W, Wd, H)
    x0, x1 = x(r["ir"]) - slot * .6, Wd - 18
    svg += (f'<rect x="{x0:.1f}" y="{y(P["ent"]):.1f}" width="{x1-x0:.1f}" '
            f'height="{y(P["stop"])-y(P["ent"]):.1f}" fill="{RED}" opacity="0.10"/>'
            f'<rect x="{x0:.1f}" y="{y(P["ent"]):.1f}" width="{x1-x0:.1f}" '
            f'height="{y(P["stop"])-y(P["ent"]):.1f}" fill="none" stroke="{RED}" '
            f'stroke-width="1.4" stroke-dasharray="6 5"/>'
            f'<rect x="{x0:.1f}" y="{y(P["tgt"]):.1f}" width="{x1-x0:.1f}" '
            f'height="{y(P["ent"])-y(P["tgt"]):.1f}" fill="{TEAL}" opacity="0.12"/>'
            f'<rect x="{x0:.1f}" y="{y(P["tgt"]):.1f}" width="{x1-x0:.1f}" '
            f'height="{y(P["ent"])-y(P["tgt"]):.1f}" fill="none" stroke="{TEAL_D}" '
            f'stroke-width="1.4" stroke-dasharray="6 5"/>')
    # الوسم داخل الصندوق وحده: أي جملة أطول من عرضه تفيض على الشموع. وفي
    # صفحة الطريق يُحذف، لأن خطّ الإغلاقات يمرّ من مكانه بالضبط.
    fs = round(19 * RC._SC[0])
    cx = (x0 + x1) / 2
    if not road:
        svg += htext(cx, (y(P["ent"]) + y(P["stop"])) / 2 + 7,
                     f'{P["risk"]} نقطة', RED, fs)
        ty = (y(P["ent"]) + y(P["tgt"])) / 2
        svg += htext(cx, ty - 4, f'{P["rew"]} نقطة', TEAL_D, fs)
        svg += htext(cx, ty + round(28 * RC._SC[0]), f'{P["rr"]:.1f}R', TEAL_D, fs)
    svg += _lvl(14, x1, y(P["tgt"]), f'الهدف {P["tgt"]:.2f}', TEAL_D, "7 6", 2.0)
    svg += _lvl(14, x1, y(P["ent"]), f'الدخول {P["ent"]:.2f}', INK, None, 2.4)
    svg += _lvl(14, x1, y(P["stop"]), f'الوقف {P["stop"]:.2f}', RED, "7 6", 2.0, False)
    if road:
        pts = " ".join(f'{x(j):.1f},{y(W[j]["c"]):.1f}'
                       for j in range(P["ei"], P["hi"] + 1))
        svg += (f'<polyline points="{pts}" fill="none" stroke="{TEAL_D}" '
                f'stroke-width="3" stroke-linejoin="round" opacity="0.9"/>')
        svg += tick(x(P["hi"]), y(P["tgt"]) - 34)
    return svg, x, y, slot


def s3_box(r, Wd=1000, H=760):
    """٣ · البكس: ثلاثة مستويات تُرسم قبل الضغط لا بعده."""
    P = plan(r)
    svg, x, y, slot = _box(r, P, Wd, H)
    svg += RC._title(Wd, "ارسم الصفقة قبل ما تضغط")
    svg += RC._why(Wd, H, "الدخول أول إغلاق فوق المنطقة · الوقف تحتها · الهدف قمة الاندفاع", TEAL_D)
    svg += RC._sum(Wd, H, f'ثلاثة أرقام معروفة قبل الدخول: '
                          f'{P["ent"]:.2f} · {P["stop"]:.2f} · {P["tgt"]:.2f}')
    return svg + badge(Wd, "الخطوة ٣ — بكس الصفقة", True) + "</svg>"


def s4_reach(r, Wd=1000, H=760):
    """٤ · الوصول: طريق الإغلاقات من الدخول حتى بلوغ الهدف."""
    P = plan(r)
    W = r["w"]
    svg, x, y, slot = _box(r, P, Wd, H, road=True)
    svg += RC._title(Wd, "الطريق من الدخول إلى الهدف")
    # الطابع MM-DD يُقلب في سياق عربي فيقرأ يوماً غير يومه — يُعزل باتجاهه.
    svg += RC._why(Wd, H, f'{P["bars"]} شمعات — والهدف انبلغ '
                          f'⁦{W[P["hi"]]["d"]}⁩', TEAL_D)
    svg += RC._sum(Wd, H, f'وأدنى قاع بعد الدخول {P["low_after"]:.2f} — '
                          f'فوق الدخول بـ{RC.pips(r, P["low_after"], P["ent"])} نقطة')
    return svg + badge(Wd, "الخطوة ٤ — الهدف", True) + "</svg>"


STEPS = {"c_context": RC.c_context, "s2_touch": s2_touch,
         "s3_box": s3_box, "s4_reach": s4_reach}


# ═══════════ الصفحات ═══════════
def chart_page(idx, pg, r, fn, hero=False):
    RC.set_no_title(True)
    RC.set_scale(1.45 if hero else 1.30)
    svg = fn(r, 1000, 950 if hero else 760)
    RC.set_scale(1.0)
    RC.set_no_title(False)
    pts = "".join(f'<p class="hpt">{t}</p>' for t in pg.get("bullets", [])[:2])
    return (f'<div class="slide" {CW}>{counter(idx, TOTAL)}'
            f'<div class="hwm2">LIQUIDITY STATE</div>'
            f'<div class="cont hero">'
            f'<h1 class="ttl9">{pg["title"]}</h1>'
            f'<div class="chartwrap">{svg}</div>{pts}'
            f'</div>{dots(idx, TOTAL)}</div>')


def cta_page(C):
    cta = C["car"]["cta"]
    head = C.get("close", {}).get("title") or C["car"]["title"]
    return f'''<div class="slide" {CW}>{counter(TOTAL, TOTAL)}{brandbar(True)}
      <div class="cta"><h1 class="big2">{head}</h1>
      <p class="tag2 center" style="margin-top:8px">{cta["line"]}</p>
      <div class="kwbox"><span>اكتب في التعليقات</span><b>«{cta["keyword"]}»</b></div>
      <p class="tag2 center">{cta["promise"]}</p>
      <p class="tag2 center" style="opacity:.75">{cta["share"]}</p></div>
      <div class="botmeta">لغرض تعليمي · <span dir="ltr">@liquidity.state</span></div>{dots(TOTAL, TOTAL)}</div>'''


def _unregister():
    p = os.path.join(HERE, "used_charts.json")
    d = json.load(open(p, encoding="utf-8"))
    for k in ("synthetic", "real"):
        d[k] = [e for e in d[k] if e.get("video") != RUN_ID]
    json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


def build(slug, C):
    r = RC.win(C["window"])
    P = plan(r)                       # يسقط هنا إن لم تثبت الخطة على الشموع
    RC.claim_fresh(r, f"run53-{slug}")
    car = C["car"]
    pages = car["pages"]
    assert len(pages) == 4, f'{len(pages)} خطوات والمطلوب أربع'

    RC15.set_minimal(True)
    cover = dk(s3_box(r, 700, 300))
    RC15.set_minimal(False)
    slides = [cover_slide(car["eyebrow"], car["title"], car["tag"], cover, total=TOTAL)]
    for i, pg in enumerate(pages):
        slides.append(chart_page(2 + i, pg, r, STEPS[pg["case"]], hero=(i == 2)))
    slides.append(cta_page(C))

    assert len(slides) == TOTAL, f"{len(slides)} صفحة والمعلن {TOTAL}"
    out = os.path.join(HERE, f"car53_{slug}.html")
    build_carousel(slides, f'{C["keyword"]} — Liquidity State', out,
                   extra_css=X15 + X_HERO)
    RC.register(RUN_ID, r, f"run53-{slug}")
    print(f'{slug:<8} {len(slides)} صفحات · كلمة «{C["keyword"]}» · نافذة {r["slug"]} · '
          f'دخول {P["ent"]:.2f} وقف {P["stop"]:.2f} هدف {P["tgt"]:.2f} · '
          f'{P["risk"]}↔{P["rew"]} نقطة ({P["rr"]:.2f}R) · بلغ بـ{P["bars"]} شمعات')
    return out


def main():
    _unregister()
    for fn in sorted(os.listdir(CONT)):
        if fn.startswith("run53_") and fn.endswith(".json"):
            slug = fn[len("run53_"):-len(".json")]
            with open(os.path.join(CONT, fn), encoding="utf-8") as f:
                build(slug, json.load(f))


if __name__ == "__main__":
    main()
