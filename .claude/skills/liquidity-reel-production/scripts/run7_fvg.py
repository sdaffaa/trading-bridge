# -*- coding: utf-8 -*-
# run7 — وحدة «الفجوة السعرية العادلة (FVG)» وفق MASTER PROMPT V2
# غلاف داكن واحد + 7 صفحات أوف وايت (بما فيها CTA) — كل النصوص فصحى
import os
from reel_build import (INK, TEAL, TEAL_D, TEAL_L, BULL, BEAR, RED, GREY, MUTE,
                        CARDBD, chart, gen, htext, GEM)
from car_common import CW, brandbar, counter, swipe, dots, cover_slide, build_carousel, dkmap, CYAN
import chart_registry

HERE = os.path.dirname(os.path.abspath(__file__))
VIDEO = "run7-fvg-unit"

# ---------- تشكيل فجوة نظيفة على شموع مولدة ----------
def force_impulse(W_, k, size, up=True):
    o = W_[k-1]["c"]
    c = o + size if up else o - size
    W_[k].update(o=o, c=c, h=max(o, c) + size*0.14, l=min(o, c) - size*0.10)

def mk_fvg(W_, k, bot=0.30, top=0.62):
    """يضبط الشمعتين 1 و3 حول شمعة الاندفاع k بحيث تبقى مسافة حقيقية بين الذيلين.
    يرجع (قاع الفجوة، قمة الفجوة) — لفجوة صاعدة."""
    o, c = W_[k]["o"], W_[k]["c"]
    lo = o + (c - o) * bot
    hi = o + (c - o) * top
    p, n = W_[k-1], W_[k+1]
    for key in ("h", "o", "c"):
        p[key] = min(p[key], lo)
    p["l"] = min(p["l"], min(p["o"], p["c"]))
    for key in ("l", "o", "c"):
        n[key] = max(n[key], hi)
    n["h"] = max(n["h"], max(n["o"], n["c"]))
    return lo, hi

def keep_above(W_, rng_, hi, lo, i0, i1, ret=None):
    """يمنع الشموع بعد التكوّن من دخول الفجوة إلا بنافذة العودة ret=(a,b)."""
    for j in range(i0, i1):
        in_ret = ret and ret[0] <= j <= ret[1]
        floor = lo + (hi - lo) * 0.18 if in_ret else hi + rng_ * 0.012
        W_[j]["l"] = max(W_[j]["l"], floor)
        W_[j]["o"] = max(W_[j]["o"], W_[j]["l"])
        W_[j]["c"] = max(W_[j]["c"], W_[j]["l"])
        W_[j]["h"] = max(W_[j]["h"], max(W_[j]["o"], W_[j]["c"]))
        if in_ret:  # العودة تلمس المنطقة فعلاً
            W_[j]["l"] = min(W_[j]["l"], hi - (hi - lo) * 0.25)

def zone_rect(x0, x1, ytop, ybot, label="", fs=19, lx=None):
    s = (f'<rect x="{x0:.1f}" y="{ytop:.1f}" width="{x1-x0:.1f}" height="{ybot-ytop:.1f}"'
         f' fill="{TEAL}" opacity="0.10"/>'
         f'<rect x="{x0:.1f}" y="{ytop:.1f}" width="{x1-x0:.1f}" height="{ybot-ytop:.1f}"'
         f' fill="none" stroke="{TEAL_D}" stroke-width="1.1" opacity="0.85"/>')
    if label:
        s += htext(lx if lx else (x0+x1)/2, (ytop+ybot)/2 + 7, label, TEAL_D, fs)
    return s

# ---------- الجارتات (بذور جديدة — تُسجَّل بنهاية الملف) ----------
CHARTS = []

def _fresh(seed, anch, label):
    chart_registry.assert_fresh_synthetic(seed, anch, label=label)
    CHARTS.append((seed, anch, label))

def hero_chart():
    """غلاف داكن: صعود باندفاع يترك فجوة"""
    seed, N, k = 4600, 26, 14
    anch = [(0, 13.2), (5, 14.6), (9, 13.9), (13, 14.5), (16, 17.4), (20, 18.2), (25, 19.6)]
    _fresh(seed, anch, "غلاف FVG")
    W_ = gen(anch, N, seed, wick=0.8)
    force_impulse(W_, k, 2.3)
    lo, hi = mk_fvg(W_, k)
    rng_ = max(c["h"] for c in W_) - min(c["l"] for c in W_)
    keep_above(W_, rng_, hi, lo, k+2, N)
    ymin = min(c["l"] for c in W_) - rng_*0.06
    ymax = max(c["h"] for c in W_) + rng_*0.08
    svg, x, y, slot = chart(W_, 880, 360, ymin, ymax, pr=20)
    svg += zone_rect(x(k-1)-slot*0.45, x(N-1)+slot*0.5, y(hi), y(lo), "FVG", 21, lx=x(N-3))
    return dkmap(svg + "</svg>")

def strong_ctx_chart():
    """صفحة 04: هبوط → سحب سيولة → كسر هيكل → اندفاع يترك فجوة"""
    seed, N, k = 4601, 34, 20
    anch = [(0, 19.5), (4, 17.8), (8, 16.6), (12, 17.3), (15, 15.9), (18, 16.4),
            (21, 19.0), (25, 20.2), (29, 19.6), (33, 21.3)]
    _fresh(seed, anch, "سياق الفجوة القوية")
    W_ = gen(anch, N, seed, wick=0.85)
    force_impulse(W_, k, 2.1)
    lo, hi = mk_fvg(W_, k)
    rng_ = max(c["h"] for c in W_) - min(c["l"] for c in W_)
    keep_above(W_, rng_, hi, lo, k+2, N)
    IH = max(range(10, 15), key=lambda j: W_[j]["h"])     # القمة المكسورة
    BOSv = W_[IH]["h"]
    IL = min(range(14, 19), key=lambda j: W_[j]["l"])     # قاع سحب السيولة
    ymin = min(c["l"] for c in W_) - rng_*0.07
    ymax = max(c["h"] for c in W_) + rng_*0.09
    svg, x, y, slot = chart(W_, 880, 340, ymin, ymax, pr=20)
    svg += (f'<line x1="{x(IH)-slot*0.6:.1f}" y1="{y(BOSv):.1f}" x2="{x(k)+slot*0.4:.1f}" y2="{y(BOSv):.1f}"'
            f' stroke="{INK}" stroke-width="1.8"/>')
    svg += htext(x(IH)+slot*2.0, y(BOSv)-11, "كسر الهيكل (BOS)", INK, 19)
    svg += (f'<circle cx="{x(IL):.1f}" cy="{y(W_[IL]["l"]):.1f}" r="15" fill="none"'
            f' stroke="{TEAL_D}" stroke-width="2.2"/>')
    svg += htext(x(IL), y(W_[IL]["l"])+34, "سحب سيولة", TEAL_D, 19)
    svg += zone_rect(x(k-1)-slot*0.45, x(N-1)+slot*0.5, y(hi), y(lo), "FVG", 19, lx=x(N-3))
    svg += htext(x(k)+slot*0.1, y(W_[k]["h"])-12, "اندفاع", TEAL_D, 19)
    return svg + "</svg>"

def mini_chart(seed, anch, N, k, size, label_zone="FVG", H=300, ret=None, brk=None):
    _fresh(seed, anch, f"مصغر {seed}")
    W_ = gen(anch, N, seed, wick=0.8)
    force_impulse(W_, k, size)
    lo, hi = mk_fvg(W_, k)
    rng_ = max(c["h"] for c in W_) - min(c["l"] for c in W_)
    if brk is None:
        keep_above(W_, rng_, hi, lo, k+2, N, ret=ret)
    else:  # سيناريو الفشل: من brk ينزل السعر ويخترق الفجوة
        keep_above(W_, rng_, hi, lo, k+2, brk)
        for j in range(brk, N):
            W_[j]["c"] = min(W_[j]["c"], lo - rng_*0.05 - (j-brk)*rng_*0.04)
            W_[j]["l"] = min(W_[j]["l"], W_[j]["c"] - rng_*0.02)
            W_[j]["o"] = min(W_[j]["o"], hi + rng_*0.02)
            W_[j]["h"] = max(W_[j]["o"], W_[j]["c"]) + rng_*0.015
    ymin = min(c["l"] for c in W_) - rng_*0.08
    ymax = max(c["h"] for c in W_) + rng_*0.10
    svg, x, y, slot = chart(W_, 620, H, ymin, ymax, pr=16, pl=10)
    svg += zone_rect(x(k-1)-slot*0.45, x(N-1)+slot*0.5, y(hi), y(lo), label_zone, 17, lx=x(N-3))
    return svg, x, y, slot, W_, lo, hi, rng_

def strong_mini():
    svg, *_ = mini_chart(4602, [(0, 14.2), (3, 13.6), (6, 14.2), (9, 16.6), (14, 17.3), (19, 18.5)],
                         20, 8, 1.9, H=430)
    return svg + "</svg>"

def weak_mini():
    svg, x, y, slot, W_, lo, hi, rng_ = mini_chart(
        4603, [(0, 15.0), (3, 15.8), (6, 14.9), (9, 15.7), (12, 15.0), (15, 15.8), (19, 15.1)],
        20, 10, 0.75, H=430)
    svg += htext(x(4), y(max(c["h"] for c in W_)) + 2, "تذبذب بلا اتجاه", MUTE, 17)
    return svg + "</svg>"

def fail_mini():
    """✗: فجوة ضد الاتجاه — العودة تخترقها"""
    svg, x, y, slot, W_, lo, hi, rng_ = mini_chart(
        4605, [(0, 18.8), (4, 17.2), (8, 16.2), (11, 17.6), (14, 16.9), (19, 14.9)],
        20, 11, 1.1, H=430, brk=14)
    bx, by = x(16), y(lo)
    svg += (f'<g stroke="{RED}" stroke-width="3" stroke-linecap="round">'
            f'<line x1="{bx-11:.1f}" y1="{by-11:.1f}" x2="{bx+11:.1f}" y2="{by+11:.1f}"/>'
            f'<line x1="{bx-11:.1f}" y1="{by+11:.1f}" x2="{bx+11:.1f}" y2="{by-11:.1f}"/></g>')
    return svg + "</svg>"

def confirm_mini():
    """✓: عودة داخل المنطقة + تأكيد + استمرار"""
    svg, x, y, slot, W_, lo, hi, rng_ = mini_chart(
        4606, [(0, 13.8), (4, 14.9), (7, 14.3), (10, 16.3), (13, 15.2), (16, 16.0), (19, 17.2)],
        20, 9, 1.8, H=430, ret=(12, 14))
    cx, cy = x(16), y(W_[16]["h"]) - 26
    svg += (f'<polyline points="{cx-10},{cy} {cx-3},{cy+8} {cx+12},{cy-10}" fill="none"'
            f' stroke="{TEAL_D}" stroke-width="3.4" stroke-linecap="round" stroke-linejoin="round"/>')
    return svg + "</svg>"

def entry_chart():
    """صفحة 06: نموذج الدخول — عودة + دخول/وقف/هدف"""
    seed, N, k = 4604, 36, 15
    anch = [(0, 13.4), (5, 14.8), (9, 14.2), (13, 14.8), (16, 17.6), (21, 18.8),
            (26, 16.9), (29, 17.5), (35, 20.4)]
    _fresh(seed, anch, "نموذج دخول الفجوة")
    W_ = gen(anch, N, seed, wick=0.8)
    force_impulse(W_, k, 2.4)
    lo, hi = mk_fvg(W_, k)
    rng_ = max(c["h"] for c in W_) - min(c["l"] for c in W_)
    RETA, RETB = 24, 28
    keep_above(W_, rng_, hi, lo, k+2, N, ret=(RETA, RETB))
    SL = lo - (hi - lo) * 0.55
    assert all(c["l"] > SL for c in W_[RETA:N]), "شمعة لامست الستوب!"
    TGT = max(c["h"] for c in W_[30:]) + rng_*0.015
    ymin = min(min(c["l"] for c in W_), SL) - rng_*0.07
    ymax = max(max(c["h"] for c in W_), TGT) + rng_*0.07
    svg, x, y, slot = chart(W_, 880, 330, ymin, ymax, pr=20)
    svg += zone_rect(x(k-1)-slot*0.45, x(N-1)+slot*0.5, y(hi), y(lo), "FVG", 18, lx=x(k+3))
    x0e = x(RETA-2)-slot*0.5; x1e = x(N-1)+slot*0.5
    svg += f'<line x1="{x0e:.1f}" y1="{y(hi):.1f}" x2="{x1e:.1f}" y2="{y(hi):.1f}" stroke="{INK}" stroke-width="2" opacity="0.9"/>'
    svg += f'<line x1="{x0e:.1f}" y1="{y(SL):.1f}" x2="{x1e:.1f}" y2="{y(SL):.1f}" stroke="{RED}" stroke-width="1.6" opacity="0.75"/>'
    svg += f'<line x1="{x0e:.1f}" y1="{y(TGT):.1f}" x2="{x1e:.1f}" y2="{y(TGT):.1f}" stroke="{TEAL}" stroke-width="1.6" opacity="0.85"/>'
    svg += htext(x1e-62, y(hi)+24, "الدخول", INK, 18)
    svg += htext(x1e-60, y(SL)+22, "الوقف", RED, 18)
    svg += htext(x0e+56, y(TGT)-9, "الهدف", TEAL_D, 18)
    return svg + "</svg>"

# ---------- كلوز أب الشموع الثلاث (تخطيطي) ----------
def _cndl(cx, o, c, h, l, w=84):
    top, bot = min(o, c), max(o, c)
    return (f'<line x1="{cx}" y1="{h}" x2="{cx}" y2="{l}" stroke="{BULL}" stroke-width="2.4"/>'
            f'<rect x="{cx-w/2}" y="{top}" width="{w}" height="{bot-top}" fill="{BULL}" rx="1.5"/>')

def closeup(kind):
    Z_T, Z_B = 148, 238   # قمة الفجوة (ذيل 3) وقاعها (ذيل 1)
    s = ['<svg viewBox="0 0 880 430" width="880" height="430" xmlns="http://www.w3.org/2000/svg">']
    s.append(f'<rect x="150" y="{Z_T}" width="580" height="{Z_B-Z_T}" fill="{TEAL}" opacity="0.12"/>')
    s.append(f'<rect x="150" y="{Z_T}" width="580" height="{Z_B-Z_T}" fill="none" stroke="{TEAL_D}" stroke-width="1.2"/>')
    s.append(_cndl(250, 300, 255, Z_B, 322))
    s.append(_cndl(440, 285, 100, 88, 297))
    s.append(_cndl(630, 130, 78, 62, Z_T))
    if kind == "def":
        s.append(htext(440, 200, "الفجوة السعرية العادلة (FVG)", TEAL_D, 24))
    else:
        for i, cx in ((1, 250), (2, 440), (3, 630)):
            s.append(f'<circle cx="{cx}" cy="386" r="21" fill="none" stroke="{TEAL}" stroke-width="2.4"/>')
            s.append(htext(cx, 394, str(i), TEAL_D, 22))
        s.append(f'<line x1="250" y1="{Z_B}" x2="800" y2="{Z_B}" stroke="{GREY}" stroke-width="1.3" stroke-dasharray="4 6"/>')
        s.append(f'<line x1="630" y1="{Z_T}" x2="800" y2="{Z_T}" stroke="{GREY}" stroke-width="1.3" stroke-dasharray="4 6"/>')
        s.append(f'<line x1="790" y1="{Z_T+6}" x2="790" y2="{Z_B-6}" stroke="{INK}" stroke-width="2"/>')
        for yy, d in ((Z_T+6, 1), (Z_B-6, -1)):
            s.append(f'<polygon points="790,{yy} 784,{yy+8*d} 796,{yy+8*d}" fill="{INK}"/>')
        s.append(htext(440, 200, "المسافة بين ذيل 1 وذيل 3", TEAL_D, 23))
    return "".join(s) + "</svg>"

# ---------- الصفحات ----------
def page(idx, body, total=8):
    return (f'<div class="slide" {CW}>{counter(idx, total)}{brandbar(True)}'
            f'<div class="cont dense">{body}</div>{swipe()}{dots(idx, total)}</div>')

def rule_row(n, html, x=False):
    return f'<div class="rulerow"><span class="rn {"x" if x else ""}">{n}</span><p>{html}</p></div>'

def wrap(svg): return f'<div class="chartwrap">{svg}</div>'

def duo(good_svg, bad_svg, good_cap, bad_cap, good_lbl="قوية ✓", bad_lbl="ضعيفة ✗"):
    return (f'<div class="duo">'
            f'<div class="col"><span class="badge ok">{good_lbl}</span><div class="chartwrap">{good_svg}</div><p class="cap">{good_cap}</p></div>'
            f'<div class="col"><span class="badge no">{bad_lbl}</span><div class="chartwrap">{bad_svg}</div><p class="cap">{bad_cap}</p></div>'
            f'</div>')

SEQ = ["اتجاه واضح", "كسر الهيكل (BOS)", "سحب سيولة", "اندفاع يترك فجوة",
       "انتظار العودة", "تأكيد داخل المنطقة", "تنفيذ بوقف وهدف"]

HERO = hero_chart()

slides = [
  cover_slide("السلسلة التعليمية — مفاهيم السيولة",
              "لماذا يعود السعر<br>إلى الفجوة؟",
              'المسافة بين الذيلين ليست فراغاً…<br>إنها <b>الفجوة السعرية العادلة (FVG)</b>',
              HERO),

  page(2, f'''<h1 class="ttl7">ما <b>الفجوة السعرية العادلة (FVG)</b>؟</h1>
    <p class="lead7">اندفاع قوي في السعر يترك خلفه <b>اختلالاً في توازن التداول</b> —
    منطقة مرّ بها السعر سريعاً دون تداول متكافئ، ويميل إلى العودة إليها لاحقاً.</p>
    {wrap(closeup("def"))}
    <div class="note">تظهر على شكل <b>ثلاث شموع</b>… والمنطقة المحصورة بينها هي الفجوة.</div>'''),

  page(3, f'''<h1 class="ttl7">كيف <b>تتكوّن</b> الفجوة؟</h1>
    {wrap(closeup("form"))}
    {rule_row(1, "<b>الشمعة الأولى</b> — نهاية الحركة السابقة")}
    {rule_row(2, "<b>شمعة الاندفاع</b> — جسم كبير يقطع المسافة بسرعة")}
    {rule_row(3, "<b>الشمعة الثالثة</b> — ذيلها لا يلامس ذيل الأولى… والمسافة بينهما هي الفجوة")}'''),

  page(4, f'''<h1 class="ttl7">متى تكون الفجوة <b>قوية</b>؟</h1>
    {rule_row("١", "تأتي <b>بعد كسر الهيكل (BOS)</b> لا قبله")}
    {rule_row("٢", "ناتجة عن <b>اندفاع واضح</b>… لا عن حركة عادية")}
    {rule_row("٣", "في <b>اتجاه السوق</b> العام لا عكسه")}
    {rule_row("٤", "بعد <b>سحب سيولة</b> من قاع أو قمة واضحة")}
    {wrap(strong_ctx_chart())}'''),

  page(5, f'''<h1 class="ttl7">متى <b>تتجاهلها</b>؟</h1>
    <p class="lead7">فجوة بلا سياق مجرد <b>مسافة على الجارت</b> — لا تُبنى عليها صفقة.</p>
    {duo(strong_mini(), weak_mini(),
         "بعد كسر هيكل واندفاع مع الاتجاه", "داخل تذبذب… بلا كسر هيكل ولا اتجاه")}
    <div class="note">ضد الاتجاه، أو داخل التذبذب، أو من حركة صغيرة = <b>تجاهلها</b>.</div>'''),

  page(6, f'''<h1 class="ttl7">نموذج <b>الدخول</b> — التسلسل السباعي</h1>
    <div class="seq">{''.join(f'<div class="sq"><span class="sn">{i+1}</span><p>{t}</p></div>' for i, t in enumerate(SEQ))}</div>
    {wrap(entry_chart())}
    <div class="note">حدّد <b>الدخول والوقف والهدف قبل التنفيذ</b> — اختراق الفجوة بإغلاق كامل يلغي الفكرة.</div>'''),

  page(7, f'''<h1 class="ttl7">الخطأ <b>الشائع</b></h1>
    {duo(confirm_mini(), fail_mini(),
         "انتظر العودة… ثم التأكيد داخل المنطقة", "دخول أعمى فور الملامسة… وضد الاتجاه",
         good_lbl="الصحيح ✓", bad_lbl="الخطأ ✗")}
    <div class="note">الفجوة تحدد <b>أين</b> تنظر… والتأكيد يحدد <b>متى</b> تدخل.</div>'''),

  # 08_CTA — أوف وايت إلزامياً (V2)
  f'''<div class="slide" {CW}>{counter(8, 8)}{brandbar()}
  <div class="cta">
    <h1 class="big2">الفجوة <b class="tt">أداة</b>…<br>وليست إشارة مستقلة</h1>
    <div class="ctabox">
      <div class="cti"><span class="ck7">١</span><p><b>السياق</b> — اتجاه وكسر هيكل (BOS) أولاً</p></div>
      <div class="cti"><span class="ck7">٢</span><p><b>القوة</b> — اندفاع واضح بعد سحب سيولة</p></div>
      <div class="cti"><span class="ck7">٣</span><p><b>الانتظار</b> — دع السعر يعود إليها بنفسه</p></div>
      <div class="cti"><span class="ck7">٤</span><p><b>التأكيد</b> — لا تنفيذ قبل إشارة داخل المنطقة</p></div>
    </div>
    <p class="tag2 center">احفظ المنشور… وعلّق بكلمة <b>«فجوة»</b> ليصلك الدليل الكامل PDF 📩</p>
  </div>
  <div class="botmeta">لغرض تعليمي</div>{dots(8, 8)}</div>''',
]

X7CSS = f'''
.cont.dense{{top:172px;bottom:150px;gap:22px;justify-content:center}}
.ttl7{{font-size:54px;font-weight:900;color:{INK};line-height:1.15;text-align:center;letter-spacing:-.5px}}
.ttl7 b{{color:{TEAL_D}}}
.lead7{{font-size:31px;line-height:1.55;color:{GREY};font-weight:500;text-align:center}}
.lead7 b{{color:{INK};font-weight:800}}
.seq{{display:flex;flex-wrap:wrap;gap:12px}}
.sq{{width:calc(50% - 6px);display:flex;align-items:center;gap:12px;background:#FBF9F5;
  border:1px solid {CARDBD};border-radius:3px;padding:11px 14px;box-sizing:border-box}}
.sq p{{font-size:25px;font-weight:700;color:{GREY}}} .sq p b{{color:{INK}}}
.sn{{width:40px;height:40px;flex:none;display:flex;align-items:center;justify-content:center;
  border-radius:50%;border:2.5px solid {TEAL};color:{TEAL_D};font-size:20px;font-weight:900}}
.duo{{display:flex;gap:22px;align-items:stretch}}
.duo .col{{flex:1;display:flex;flex-direction:column;gap:13px}}
.badge{{align-self:center;font-size:27px;font-weight:900;padding:7px 26px;border-radius:3px}}
.badge.ok{{background:rgba(46,125,150,0.10);color:{TEAL_D};border:1.5px solid {TEAL_L}}}
.badge.no{{background:rgba(210,75,75,0.08);color:{RED};border:1.5px solid rgba(210,75,75,0.45)}}
.duo .chartwrap{{padding:14px;box-shadow:0 10px 26px rgba(15,46,60,0.08)}}
.duo p.cap{{font-size:26px;font-weight:700;color:{GREY};text-align:center;line-height:1.45}}
.ctabox{{width:100%;background:#FBF9F5;border:1px solid {CARDBD};border-radius:3px;padding:12px 28px;
  box-shadow:0 16px 40px rgba(15,46,60,0.10)}}
.cti{{display:flex;align-items:center;gap:18px;padding:19px 4px;border-bottom:1px solid #EDE7DB}}
.cti:last-child{{border-bottom:none}}
.cti p{{font-size:30px;font-weight:700;color:{GREY}}} .cti p b{{font-weight:900;color:{TEAL_D}}}
.ck7{{width:46px;height:46px;flex:none;display:flex;align-items:center;justify-content:center;
  border-radius:50%;border:2.5px solid {TEAL};color:{TEAL_D};font-size:22px;font-weight:900}}
.poster .dcover{{top:300px}}
.pfoot{{position:absolute;bottom:70px;left:0;right:0;text-align:center;color:#8FA6AF;font-size:24px;font-weight:600}}
'''

n = build_carousel(slides, "الفجوة السعرية العادلة (FVG)", os.path.join(HERE, "car_fvg.html"), extra_css=X7CSS)
print("carousel html:", n)

# البوستر الداكن المستقل (نفس هوية الغلاف بلا عناصر كاروسيل)
poster = f'''<div class="slide dark poster" {CW}>
  <div class="dhd"><div class="hgem">{GEM}</div><div class="hwm"><span class="hln"></span>LIQUIDITY STATE<span class="hln" style="transform:scaleX(-1)"></span></div></div>
  <div class="dcover">
    <div class="deyeb"><span class="dsh"></span>السلسلة التعليمية — مفاهيم السيولة<span class="dsh"></span></div>
    <h1 class="dbig">لماذا يعود السعر<br>إلى الفجوة؟</h1>
    <div class="tbar"></div>
    <p class="dtag">المسافة بين الذيلين ليست فراغاً…<br>إنها <b>الفجوة السعرية العادلة (FVG)</b></p>
    <div class="dchart">{HERO}</div>
  </div>
  <div class="pfoot">لغرض تعليمي — <span dir="ltr">@liquidity.state</span></div>
</div>'''
np = build_carousel([poster], "بوستر الفجوة", os.path.join(HERE, "poster_fvg.html"), extra_css=X7CSS)
print("poster html:", np)

print("charts:", len(CHARTS))
chart_registry.register_synthetic(VIDEO, CHARTS)
print("registered")
