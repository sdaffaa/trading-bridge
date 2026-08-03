# -*- coding: utf-8 -*-
# مكونات الكاروسيل المشتركة (مصنع المحتوى اليومي) — مستخلصة من carousel3_build.py
# الاستخدام: from car_common import *  ثم build_carousel(SLIDES_HTML_LIST, title, out)
import math, os
from reel_build import (CREAM, INK, TEAL, TEAL_D, TEAL_L, BULL, BEAR, RED, MUTE, GREY,
                        FONT_CSS, chart, htext, hend, GEM)

HERE = os.path.dirname(os.path.abspath(__file__))
CARDBD = "#DED8CC"; DK_BG = "#08131C"; CYAN = "#43D4DC"
CW = 'data-canvas-width="1080" data-canvas-height="1350"'

def brandbar(compact=False):
    sz = 44 if compact else 54; ws = 22 if compact else 26
    return f'''<div class="brand">
      <div class="gem" style="width:{sz}px;height:{sz}px">{GEM}</div>
      <div class="wm"><span class="ln"></span><span class="wmt" style="font-size:{ws}px">LIQUIDITY STATE</span><span class="ln"></span></div>
    </div>'''
def counter(i, total=8):
    return f'<div class="counter"><b>{i}</b><i>/</i><b>{total}</b></div>'
def swipe(dark=False):
    return f'<div class="swipe {"dk" if dark else ""}"><span>اسحب&nbsp;&nbsp;→</span></div>'
def dots(active, total=8, dark=False):
    return f'<div class="dots {"dk" if dark else ""}">' + ''.join(
        f'<span class="dot {"on" if i == active else ""}"></span>' for i in range(1, total+1)) + '</div>'
def eyebrow(t):
    return f'<div class="eyebrow"><span class="dash"></span>{t}<span class="dash"></span></div>'

def cover_slide(eyeb, title_html, tag_html, hero_svg, total=8):
    return f'''<div class="slide dark" {CW}>
  {counter(1, total)}
  <div class="dhd"><div class="hgem">{GEM}</div><div class="hwm"><span class="hln"></span>LIQUIDITY STATE<span class="hln" style="transform:scaleX(-1)"></span></div></div>
  <div class="dcover">
    <div class="deyeb"><span class="dsh"></span>{eyeb}<span class="dsh"></span></div>
    <h1 class="dbig">{title_html}</h1>
    <div class="tbar"></div>
    <p class="dtag">{tag_html}</p>
    <div class="dchart">{hero_svg}</div>
  </div>
  {swipe(True)}{dots(1, total, dark=True)}
</div>'''

def quote_slide(idx, big_html, tag_html, total=8):
    return f'''<div class="slide" {CW}>
  {counter(idx, total)}
  {brandbar(True)}
  <div class="quote">
    <div class="qm">”</div>
    <h1 class="big2">{big_html}</h1>
    <p class="tag2 center">{tag_html}</p>
  </div>
  {swipe()}{dots(idx, total)}
</div>'''

def cta_slide(idx, keyword, share_line, promise_line, total=8):
    return f'''<div class="slide" {CW}>
  {counter(idx, total)}
  {brandbar()}
  <div class="cta">
    <h1 class="big2">خلّ الدرس معاك</h1>
    <div class="checkbox">
      <div class="ci"><span class="ck">✓</span><p>احفظ المنشور يرجع لك وقت التحليل</p></div>
      <div class="ci"><span class="ck">✓</span><p>{share_line}</p></div>
      <div class="ci"><span class="ck">✓</span><p>علّق كلمة <b class="tt">«{keyword}»</b> ويوصلك {promise_line}</p></div>
    </div>
    <p class="tag2 center">أرسلك الشرح كامل بملف PDF 📩</p>
  </div>
  <div class="botmeta">لغرض تعليمي</div>{dots(idx, total)}
</div>'''

# ---------- تخطيطي zigzag عام (نفس carousel3) ----------
def sk(pts, W=880, H=400, lines=(), zone=None, zlabel="", circle=None, arrow=None,
       texts=(), bos=None, fs0=18):
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    for seg in lines: xs += [q[0] for q in seg["p"]]; ys += [q[1] for q in seg["p"]]
    x0, x1 = min(xs), max(xs); y0, y1 = min(ys), max(ys)
    mx = lambda v: 20 + (v-x0)/(x1-x0)*(W-40)
    my = lambda v: 18 + (y1-v)/(y1-y0)*(H-50)
    s = [f'<svg viewBox="0 0 {W} {H}" width="{W}" height="{H}" xmlns="http://www.w3.org/2000/svg">']
    if zone:
        (za, zb2), (zt, zbo) = zone
        s.append(f'<rect x="{mx(za):.1f}" y="{my(zt):.1f}" width="{mx(zb2)-mx(za):.1f}" height="{my(zbo)-my(zt):.1f}" fill="{TEAL}" style="opacity:0.16"/>')
        s.append(f'<rect x="{mx(za):.1f}" y="{my(zt):.1f}" width="{mx(zb2)-mx(za):.1f}" height="{my(zbo)-my(zt):.1f}" fill="none" stroke="{TEAL_D}" stroke-width="1"/>')
        if zlabel: s.append(htext((mx(za)+mx(zb2))/2, (my(zt)+my(zbo))/2+6, zlabel, TEAL_D, fs0-1))
    for seg in lines:
        p = " ".join(f"{mx(a):.1f},{my(b):.1f}" for a, b in seg["p"])
        d = f' stroke-dasharray="{seg["dash"]}"' if seg.get("dash") else ''
        s.append(f'<polyline points="{p}" fill="none" stroke="{seg["c"]}" stroke-width="{seg.get("w",1.8)}"{d}/>')
    p = " ".join(f"{mx(a):.1f},{my(b):.1f}" for a, b in pts)
    s.append(f'<polyline points="{p}" fill="none" stroke="{INK}" stroke-width="2.8" stroke-linecap="round" stroke-linejoin="round"/>')
    if bos:
        (bx0, bx1, bv) = bos
        s.append(f'<line x1="{mx(bx0):.1f}" y1="{my(bv):.1f}" x2="{mx(bx1):.1f}" y2="{my(bv):.1f}" stroke="{INK}" stroke-width="1.6"/>')
        s.append(f'<polygon points="{mx(bx1):.1f},{my(bv)-4:.1f} {mx(bx1):.1f},{my(bv)+4:.1f} {mx(bx1)+8:.1f},{my(bv):.1f}" fill="{INK}"/>')
        s.append(htext(mx(bx0)+18, my(bv)-9, "BOS", INK, fs0-2))
    if circle:
        s.append(f'<circle cx="{mx(circle[0]):.1f}" cy="{my(circle[1]):.1f}" r="13" fill="none" stroke="{RED}" stroke-width="2.6"/>')
    if arrow:
        (a0, a1) = arrow
        ax0, ay0, ax1, ay1 = mx(a0[0]), my(a0[1]), mx(a1[0]), my(a1[1])
        ang = math.atan2(ay1-ay0, ax1-ax0)
        s.append(f'<line x1="{ax0:.1f}" y1="{ay0:.1f}" x2="{ax1:.1f}" y2="{ay1:.1f}" stroke="{INK}" stroke-width="2.8"/>')
        for da in (ang+2.65, ang-2.65):
            s.append(f'<line x1="{ax1:.1f}" y1="{ay1:.1f}" x2="{ax1+13*math.cos(da):.1f}" y2="{ay1+13*math.sin(da):.1f}" stroke="{INK}" stroke-width="2.8" stroke-linecap="round"/>')
    for (tx, tv, txt, col, fs) in texts:
        s.append(htext(mx(tx), my(tv), txt, col, fs))
    return "".join(s) + "</svg>"

def dkmap(svg):
    for a, b in [("#2E8CA6", "#43D4DC"), ("#122F3E", "#5E7A88"), ("#0F2E3C", "#D8E5EB"),
                 ("#F2EEE7", DK_BG), ("#1E627A", "#3AAFC0"), ("#D24B4B", "#E05656"),
                 ("#5C6C73", "#8FA6AF"), ("rgba(15,46,60,0.06)", "rgba(255,255,255,0.06)")]:
        svg = svg.replace(a, b)
    return svg

CSS = f'''
*{{margin:0;padding:0;box-sizing:border-box}}
body{{background:#cfcabf;font-family:'Tajawal',sans-serif}}
.slide{{position:relative;width:1080px;height:1350px;overflow:hidden;direction:rtl;
  background:radial-gradient(120% 90% at 50% 0%, #F7F3EC 0%, {CREAM} 45%, #ECE6DB 100%);color:{INK}}}
.counter{{position:absolute;top:56px;left:80px;z-index:6;direction:ltr;display:inline-flex;align-items:center;
  gap:7px;color:{TEAL_D};font-weight:800;font-size:29px;font-style:italic;padding:5px 20px;border-radius:3px;
  border:1.5px solid {TEAL_L};background:rgba(255,255,255,0.5)}}
.counter i{{font-style:normal;opacity:.5;font-weight:600}}
.slide.dark .counter{{color:{CYAN};border-color:rgba(67,212,220,0.55);background:rgba(255,255,255,0.04)}}
.brand{{position:absolute;top:56px;left:0;right:0;display:flex;flex-direction:column;align-items:center;gap:8px;z-index:5}}
.gem{{filter:drop-shadow(0 6px 12px rgba(15,46,60,0.18))}}
.wm{{display:flex;align-items:center;gap:14px}}
.wm .ln{{width:38px;height:2px;background:{TEAL_L};display:inline-block}}
.wmt{{color:{TEAL_D};font-weight:500;letter-spacing:6px}}
.eyebrow{{display:flex;align-items:center;justify-content:center;gap:16px;color:{TEAL};
  font-weight:800;font-size:27px;letter-spacing:.5px}}
.eyebrow .dash{{width:46px;height:3px;background:{TEAL_L};display:inline-block}}
.tt{{color:{TEAL_D}!important}} .tr{{color:{RED}!important}}
.ttl{{font-size:52px;font-weight:900;color:{INK};line-height:1.12;letter-spacing:-.5px}}
.ttl.big{{font-size:62px;text-align:center}}
.big2{{font-size:82px;font-weight:900;color:{INK};line-height:1.14;letter-spacing:-1px;text-align:center}}
.tag2{{font-size:36px;color:{GREY};font-weight:500;margin-top:22px;line-height:1.5}}
.tag2 b{{color:{TEAL_D};font-weight:800}} .tag2.center{{text-align:center}}
.lead{{font-size:33px;line-height:1.55;color:{GREY};font-weight:500}}
.lead b{{color:{INK};font-weight:800}}
.note{{font-size:29px;font-weight:700;color:{INK};background:rgba(46,125,150,0.09);
  border-right:6px solid {TEAL};border-radius:3px;padding:18px 24px;line-height:1.5}}
.note b{{font-weight:900;color:{TEAL_D}}}
.tiny{{font-size:21px;color:{MUTE};font-weight:600;text-align:center}}
.chartwrap{{width:100%;background:#FBF9F5;border:1px solid {CARDBD};border-radius:3px;
  padding:20px;box-shadow:0 18px 44px rgba(15,46,60,0.10)}}
.chartwrap svg{{width:100%;height:auto;display:block}}
.cont{{position:absolute;top:190px;left:90px;right:90px;bottom:170px;display:flex;flex-direction:column;gap:26px;justify-content:center}}
.numrow{{display:flex;align-items:center;gap:18px}}
.num{{width:66px;height:66px;flex:none;display:flex;align-items:center;justify-content:center;font-size:38px;
  font-weight:900;font-style:italic;color:#fff;background:linear-gradient(135deg,{TEAL},{TEAL_D});
  border-radius:2px;box-shadow:0 10px 22px rgba(46,125,150,0.30)}}
.rulerow{{display:flex;align-items:center;gap:16px;background:#FBF9F5;border:1px solid {CARDBD};
  border-radius:3px;padding:16px 22px}}
.rulerow p{{font-size:30px;font-weight:700;color:{GREY}}}
.rulerow p b{{color:{INK};font-weight:900}}
.rn{{width:44px;height:44px;flex:none;display:flex;align-items:center;justify-content:center;border-radius:50%;
  border:2.5px solid {TEAL};color:{TEAL_D};font-size:22px;font-weight:900}}
.rn.x{{border-color:{RED};color:{RED}}}
.realhead{{display:flex;align-items:center;justify-content:space-between}}
.ticker{{color:{TEAL_D};font-weight:800;font-size:24px;background:rgba(46,125,150,0.10);
  padding:7px 16px;border-radius:2px;border:1px solid {TEAL_L};white-space:nowrap}}
.cards{{display:flex;flex-direction:column;gap:20px}}
.card{{display:flex;gap:20px;background:#FBF9F5;border:1px solid {CARDBD};border-radius:3px;
  padding:24px 26px;box-shadow:0 12px 30px rgba(15,46,60,0.08);align-items:flex-start}}
.card .num{{width:58px;height:58px;font-size:32px;margin-top:4px}}
.cbody{{flex:1;min-width:0}}
.cbody h3{{font-size:36px;font-weight:900;color:{INK};margin-bottom:8px}}
.crow{{display:flex;align-items:baseline;gap:14px;margin-top:6px}}
.clab{{flex:none;font-size:22px;font-weight:900;color:#fff;background:{INK};padding:3px 14px;border-radius:2px}}
.clab.go{{background:{TEAL_D}}}
.crow p{{font-size:27px;font-weight:600;color:{GREY};line-height:1.4}}
.quote{{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;padding:0 110px;text-align:center}}
.qm{{font-size:170px;color:{TEAL_L};line-height:.5;font-weight:900;opacity:.6;margin-bottom:24px}}
.quote .big2{{font-size:72px}} .quote .tag2{{margin-top:34px}}
.cta{{position:absolute;top:210px;left:90px;right:90px;bottom:150px;display:flex;flex-direction:column;
  align-items:center;justify-content:center;gap:40px}}
.checkbox{{width:100%;background:#FBF9F5;border:1px solid {CARDBD};border-radius:3px;padding:14px 26px;
  box-shadow:0 16px 40px rgba(15,46,60,0.10)}}
.ci{{display:flex;align-items:center;gap:18px;padding:22px 4px;border-bottom:1px solid #EDE7DB}}
.ci:last-child{{border-bottom:none}}
.ci p{{font-size:32px;font-weight:700;color:{INK}}} .ci p b{{font-weight:900}}
.ck{{width:48px;height:48px;flex:none;display:flex;align-items:center;justify-content:center;border-radius:50%;
  border:2.5px solid {TEAL};color:{TEAL_D};font-size:26px;font-weight:900}}
.swipe{{position:absolute;bottom:96px;left:0;right:0;display:flex;justify-content:center;z-index:6}}
.swipe span{{color:{TEAL_D};font-weight:800;font-size:28px;padding:10px 34px;
  border:1.5px solid {TEAL_L};border-radius:3px;background:rgba(255,255,255,0.5)}}
.swipe.dk span{{color:{CYAN};border-color:rgba(67,212,220,0.55);background:rgba(255,255,255,0.04)}}
.botmeta{{position:absolute;bottom:100px;left:0;right:0;text-align:center;color:{MUTE};font-size:24px;font-weight:600}}
.dots{{position:absolute;bottom:54px;left:0;right:0;display:flex;gap:10px;justify-content:center;z-index:6}}
.dot{{width:10px;height:10px;border-radius:50%;background:rgba(15,46,60,0.18)}}
.dot.on{{background:{TEAL};width:30px;border-radius:6px}}
.dots.dk .dot{{background:rgba(255,255,255,0.20)}} .dots.dk .dot.on{{background:{CYAN}}}
.slide.dark{{background:radial-gradient(120% 90% at 50% 0%, #0C2029 0%, #08131C 55%, #04090F 100%);color:#ECF3F6}}
.dhd{{position:absolute;top:64px;left:0;right:0;display:flex;flex-direction:column;align-items:center;gap:10px}}
.hgem{{width:58px;height:58px}} .hgem svg{{width:100%;height:100%;filter:drop-shadow(0 0 18px rgba(67,212,220,0.45))}}
.hwm{{display:flex;align-items:center;gap:12px;font-weight:700;font-size:18px;letter-spacing:8px;
  background:linear-gradient(180deg,#ffffff,#C4D4DB 55%,#8FA6AF);-webkit-background-clip:text;background-clip:text;color:transparent}}
.hln{{display:block;width:70px;height:1px;background:linear-gradient(90deg,transparent,rgba(67,212,220,0.7))}}
.dcover{{position:absolute;top:250px;left:80px;right:80px;display:flex;flex-direction:column;align-items:center;text-align:center}}
.deyeb{{display:flex;align-items:center;gap:12px;color:{CYAN};font-weight:800;font-size:27px}}
.dsh{{display:block;width:30px;height:2px;background:{CYAN};box-shadow:0 0 8px rgba(67,212,220,0.5)}}
.dbig{{margin-top:20px;font-size:96px;font-weight:900;line-height:1.12;letter-spacing:-1px;
  background:linear-gradient(180deg,#ffffff,#C4D4DB 60%,#7F97A1);-webkit-background-clip:text;background-clip:text;color:transparent;
  filter:drop-shadow(0 0 26px rgba(67,212,220,0.22))}}
.tbar{{width:430px;height:3px;margin:24px auto 0;
  background:linear-gradient(90deg,transparent,{CYAN},transparent);box-shadow:0 0 10px rgba(67,212,220,0.4)}}
.dtag{{margin-top:24px;font-size:36px;color:#B9CBD3;font-weight:500;line-height:1.5}}
.dtag b{{color:{CYAN};font-weight:800}}
.dchart{{margin-top:44px;width:100%;background:rgba(255,255,255,0.025);border:1px solid rgba(67,212,220,0.28);
  border-radius:3px;padding:22px}}
.dchart svg{{width:78%;height:auto;display:block;margin:0 auto}}
'''

def build_carousel(slides, title, out_path):
    html = f'''<!DOCTYPE html><html lang="ar" dir="rtl"><head><meta charset="UTF-8">
<title>{title}</title>
<meta name="hz:slide-selector" content=".slide">
<meta name="hz:canvas-width" content="1080"><meta name="hz:canvas-height" content="1350">
<style>{FONT_CSS}\n{CSS}</style></head><body>
{''.join(slides)}
</body></html>'''
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    return len(html)
