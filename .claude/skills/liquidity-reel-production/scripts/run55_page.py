# -*- coding: utf-8 -*-
"""تشغيلة ٥٥ — هياكل الصفحات الست وCSS الدفعة.

ست صفحات لكل كاروسيل: غلافٌ غامق ثم أربع صفحات محتوى ثم نداء الفعل.
البنية الداخلية لكل نوع (درس · دخول · خسارة · خفايا · نفس) تأتي من §10 في
أمر فهد، والمكوّنات هنا هي الأدوات التي تبنيها.

قواعد ملزَمة في الشكل: عنوان واحد لكل صفحة، سطران تفسير كحدٍّ أقصى،
هوامش ٨٠ بكسل، زوايا حادة، وخطّان لا أكثر.
"""
import math, os

from gem import build_gem
from run55_kit import (BG, DK_BG, DK_2, DK_TX, FOCUS, INK, EDU, SUB, CARD,
                       LINE, RED, GRN, FONT_CSS)

# اللوقو: المجسّم العشريني المحسوب (§2) — ممنوع المبسّط
GEM = build_gem(math.radians(54.0), 0.0, 0.0, size=52, gid="g55")
TOTAL = 6


# ═════════════════════ خريطة الغلاف الغامق ═════════════════════
def dk(s):
    """يحوّل ألوان رسمٍ فاتح إلى لوحة الغلاف الغامق بلا إعادة بناء."""
    for a, b in (("#257A93", FOCUS), ("#0B2635", "#5E7A88"),
                 ("#F9F6F1", DK_BG), ("#6A7B84", "#8FA6AF"),
                 ("#B4C8CC", "#28454F"), ("#D9E3E3", "#12303C"),
                 ("rgba(11,38,53,0.07)", "rgba(255,255,255,0.06)")):
        s = s.replace(a, b)
    return s


# ═════════════════════ مكوّنات مشتركة ═════════════════════
def _head(dark=False):
    cls = "hd dk" if dark else "hd"
    return (f'<div class="{cls}"><div class="gem">{GEM}</div>'
            f'<div class="wm"><i></i><span>LIQUIDITY STATE</span><i></i></div></div>')


def _counter(i, dark=False):
    return (f'<div class="cnt{" dk" if dark else ""}">'
            f'<b>{i}</b><i>/</i><b>{TOTAL}</b></div>')


def _dots(i, dark=False):
    d = "".join(f'<span class="{"on" if k == i else ""}"></span>'
                for k in range(1, TOTAL + 1))
    return f'<div class="dots{" dk" if dark else ""}">{d}</div>'


def _swipe(dark=False):
    return f'<div class="sw{" dk" if dark else ""}">اسحب&nbsp;&nbsp;←</div>'


def _foot(i, dark=False, swipe=True):
    return (_swipe(dark) if swipe else "") + _dots(i, dark)


# ═════════════════════ ١ · الغلاف ═════════════════════
def cover(tags, hook, sub, hero_svg, source=""):
    tg = "".join(f'<span>{x}</span>' for x in tags)
    src = f'<div class="csrc">{source}</div>' if source else ""
    return f'''<div class="slide dark">
  {_counter(1, True)}{_head(True)}
  <div class="cont cover">
    <div class="tags">{tg}</div>
    <h1 class="hook">{hook}</h1>
    <div class="rule"></div>
    <p class="sub">{sub}</p>
    <div class="hero">{dk(hero_svg)}</div>
    {src}
  </div>
  {_foot(1, True)}
</div>'''


# ═════════════════════ ٢–٥ · صفحات المحتوى ═════════════════════
def page(i, kicker, title, lead, block, note="", tone=""):
    """صفحة محتوى: تنويه · عنوان واحد · سطرا تفسير · كتلة بصرية · هامش."""
    nt = f'<div class="note {tone}">{note}</div>' if note else ""
    return f'''<div class="slide">
  {_counter(i)}{_head()}
  <div class="cont">
    <div class="kick">{kicker}</div>
    <h1 class="ttl">{title}</h1>
    <p class="lead">{lead}</p>
    <div class="block">{block}</div>
    {nt}
  </div>
  {_foot(i)}
</div>'''


def cards(items):
    """بطاقات فحصٍ أو خطوات — الرقم لاتيني مائل داخل مربّع حادّ."""
    out = []
    for k, (h, b) in enumerate(items, 1):
        out.append(f'<div class="card"><span class="n">{k}</span>'
                   f'<div><b>{h}</b><p>{b}</p></div></div>')
    return f'<div class="cards">{"".join(out)}</div>'


def checks(items, bad=False):
    ic = "✕" if bad else "✓"
    cls = "chk bad" if bad else "chk"
    out = "".join(f'<div class="{cls}"><span>{ic}</span><p>{x}</p></div>'
                  for x in items)
    return f'<div class="checks">{out}</div>'


def stats(items):
    """صفٌّ من الأرقام المقيسة — كل رقم بمسمّاه تحته."""
    out = "".join(f'<div class="st"><b>{v}</b><span>{k}</span></div>'
                  for k, v in items)
    return f'<div class="stats">{out}</div>'


def plan_table(rows):
    out = "".join(f'<tr><td class="k">{k}</td><td class="v {c}">{v}</td></tr>'
                  for k, v, c in rows)
    return f'<table class="plan">{out}</table>'


# ═════════════════════ ٦ · نداء الفعل ═════════════════════
def cta(keyword, save_line, share_line, promise="الملخص"):
    return f'''<div class="slide">
  {_counter(TOTAL)}{_head()}
  <div class="cont cta">
    <h1 class="ttl big">خلّ الدرس معاك</h1>
    <div class="kw">اكتب <b>«{keyword}»</b> بالتعليقات، وأرسل لك {promise}</div>
    <div class="checks">
      <div class="chk"><span>✓</span><p>{save_line}</p></div>
      <div class="chk"><span>✓</span><p>{share_line}</p></div>
    </div>
    <p class="lead center">أرسلك الشرح كامل بملف PDF 📩</p>
  </div>
  <div class="edu">لغرض تعليمي — مو توصية</div>{_dots(TOTAL)}
</div>'''


# ═════════════════════ CSS ═════════════════════
CSS = f'''
*{{margin:0;padding:0;box-sizing:border-box}}
body{{background:#cfcabf;font-family:'PlexAr',sans-serif}}
.slide{{position:relative;width:1080px;height:1350px;overflow:hidden;
  direction:rtl;background:{BG};color:{INK}}}
.slide.dark{{background:linear-gradient(178deg,{DK_BG} 0%,{DK_2} 62%,{DK_BG} 100%);
  color:{DK_TX}}}

/* الترويسة */
.hd{{position:absolute;top:52px;left:0;right:0;display:flex;flex-direction:column;
  align-items:center;gap:9px;z-index:5}}
.hd .gem{{width:52px;height:52px;filter:drop-shadow(0 5px 11px rgba(11,38,53,.16))}}
.hd.dk .gem{{filter:drop-shadow(0 0 22px rgba(32,147,158,.45))}}
.wm{{display:flex;align-items:center;gap:13px}}
.wm i{{width:34px;height:1.5px;background:{LINE};display:block}}
.wm span{{color:{EDU};font-weight:500;font-size:21px;letter-spacing:5px;
  font-family:'Inter',sans-serif}}
.hd.dk .wm i{{background:rgba(32,147,158,.55)}}
.hd.dk .wm span{{color:{FOCUS}}}

/* العدّاد */
.cnt{{position:absolute;top:54px;left:80px;z-index:6;direction:ltr;
  display:inline-flex;align-items:center;gap:6px;color:{EDU};font-weight:700;
  font-size:26px;font-style:italic;padding:3px 16px;border:1.5px solid {LINE};
  background:rgba(255,255,255,.55);font-family:'Inter',sans-serif}}
.cnt i{{font-style:normal;opacity:.45;font-weight:500}}
.cnt.dk{{color:{FOCUS};border-color:rgba(32,147,158,.5);background:rgba(255,255,255,.04)}}

/* الجسم */
.cont{{position:absolute;top:186px;left:80px;right:80px;bottom:120px;
  display:flex;flex-direction:column;gap:24px}}
.cont.cover{{align-items:center;text-align:center;gap:0;top:210px}}
.cont.cta{{justify-content:center;align-items:center;text-align:center;gap:34px}}

.tags{{display:flex;gap:12px;align-items:center;justify-content:center}}
.tags span{{color:{FOCUS};font-weight:600;font-size:22px;letter-spacing:.5px;
  border:1.5px solid rgba(32,147,158,.45);padding:5px 16px}}
.hook{{margin-top:26px;font-size:78px;font-weight:700;line-height:1.2;
  letter-spacing:-1px;color:{DK_TX}}}
.hook b{{color:{FOCUS};font-weight:700}}
.rule{{width:360px;height:2px;margin:26px auto 0;
  background:linear-gradient(90deg,transparent,{FOCUS},transparent)}}
.cover .sub{{margin-top:22px;font-size:33px;color:#B4C6CE;font-weight:400;
  line-height:1.55;max-width:840px}}
.cover .sub b{{color:{FOCUS};font-weight:600}}
.hero{{margin-top:34px;width:100%}}
.hero svg{{width:96%;height:auto;display:block;margin:0 auto}}
.csrc{{margin-top:20px;font-size:19px;color:#7E96A0;font-weight:400}}

.kick{{color:{EDU};font-weight:600;font-size:24px;letter-spacing:.5px;
  display:flex;align-items:center;gap:12px}}
.kick::before{{content:"";width:30px;height:2.5px;background:{EDU};display:block}}
.ttl{{font-size:53px;font-weight:700;line-height:1.22;letter-spacing:-.5px;
  color:{INK}}}
.ttl.big{{font-size:76px;text-align:center}}
.lead{{font-size:31px;line-height:1.55;color:{SUB};font-weight:400}}
.lead b{{color:{INK};font-weight:600}}
.lead .t{{color:{EDU};font-weight:600}}
.lead .r{{color:{RED};font-weight:600}}
.lead.center{{text-align:center;font-size:29px}}
.block{{flex:1;display:flex;flex-direction:column;justify-content:center;
  min-height:0}}
.block svg{{width:100%;height:auto;display:block}}
.note{{font-size:24px;color:{SUB};font-weight:500;border-top:1.5px solid {LINE};
  padding-top:16px;line-height:1.45}}
.note b{{color:{INK};font-weight:600}}
.note.warn{{color:{RED}}}
.note.warn b{{color:{RED}}}

/* بطاقات */
.cards{{display:flex;flex-direction:column;gap:15px}}
.card{{display:flex;gap:18px;align-items:flex-start;background:{CARD};
  border:1.5px solid {LINE};padding:19px 22px}}
.card .n{{font-family:'Inter',sans-serif;font-style:italic;font-weight:800;
  font-size:27px;color:{BG};background:{EDU};min-width:44px;height:44px;
  display:flex;align-items:center;justify-content:center;flex:0 0 auto}}
.card b{{font-size:29px;font-weight:600;color:{INK};display:block;
  line-height:1.35}}
.card p{{font-size:25px;color:{SUB};font-weight:400;line-height:1.45;
  margin-top:5px}}

.checks{{display:flex;flex-direction:column;gap:16px}}
.chk{{display:flex;gap:16px;align-items:flex-start}}
.chk span{{width:40px;height:40px;flex:0 0 auto;display:flex;align-items:center;
  justify-content:center;background:{GRN};color:{INK};font-weight:700;
  font-size:24px}}
.chk.bad span{{background:{RED};color:{BG}}}
.chk p{{font-size:28px;line-height:1.45;color:{INK};font-weight:400;
  padding-top:4px}}

.stats{{display:flex;gap:14px}}
.st{{flex:1;background:{CARD};border:1.5px solid {LINE};padding:20px 12px;
  text-align:center}}
.st b{{display:block;font-family:'Inter',sans-serif;font-size:42px;
  font-weight:700;color:{EDU};line-height:1.1;direction:ltr}}
.st span{{display:block;margin-top:8px;font-size:22px;color:{SUB};
  font-weight:500;line-height:1.35}}

.plan{{width:100%;border-collapse:collapse}}
.plan td{{border:1.5px solid {LINE};padding:16px 20px;font-size:28px}}
.plan .k{{color:{SUB};font-weight:500;width:38%;background:{CARD}}}
.plan .v{{color:{INK};font-weight:600;font-family:'Inter',sans-serif;
  direction:ltr;text-align:right}}
.plan .v.r{{color:{RED}}} .plan .v.t{{color:{EDU}}} .plan .v.ar{{
  font-family:'PlexAr',sans-serif;direction:rtl;text-align:right}}

.kw{{font-size:37px;font-weight:500;color:{INK};line-height:1.5;
  border:2px solid {EDU};padding:24px 34px;background:{CARD}}}
.kw b{{color:{EDU};font-weight:700}}

/* التذييل */
.sw{{position:absolute;bottom:74px;left:0;right:0;text-align:center;
  color:{SUB};font-size:25px;font-weight:500;letter-spacing:1px}}
.sw.dk{{color:#8FA6AF}}
.dots{{position:absolute;bottom:44px;left:0;right:0;display:flex;gap:9px;
  justify-content:center}}
.dots span{{width:9px;height:9px;background:{LINE};display:block}}
.dots span.on{{background:{EDU};width:26px}}
.dots.dk span{{background:#28454F}}
.dots.dk span.on{{background:{FOCUS}}}
.edu{{position:absolute;bottom:80px;left:0;right:0;text-align:center;
  color:{SUB};font-size:22px;font-weight:500}}
'''


def build(slides, title, out_path):
    html = f'''<!DOCTYPE html><html lang="ar" dir="rtl"><head><meta charset="UTF-8">
<title>{title}</title>
<meta name="hz:slide-selector" content=".slide">
<meta name="hz:canvas-width" content="1080"><meta name="hz:canvas-height" content="1350">
<style>{FONT_CSS}
{CSS}</style></head><body>
{"".join(slides)}
</body></html>'''
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    return len(html)
