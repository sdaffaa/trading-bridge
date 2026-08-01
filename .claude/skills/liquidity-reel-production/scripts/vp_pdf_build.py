# -*- coding: utf-8 -*-
# "10 Volume Profile Trades" PDF — 13 pages, all permanent Liquidity State rules.
import os, json
from reel_build import (CREAM, CREAM2, INK, TEAL, TEAL_D, TEAL_L, BULL, BEAR, RED, GREY, MUTE,
                        LINE, CARDBD, CYAN, CYANG, FONT_CSS, GEM, chart, htext, hend)
from reel_vp_build import profile, vp_bars, IPRO, IENT
from reel_build import IUP
HERE = os.path.dirname(os.path.abspath(__file__))
TRADES = json.load(open(os.path.join(HERE, "vp10_trades.json")))
NP = 13

META = {
 "A": dict(title="كسر القيمة والرجعة — شراء", side="شراء",
           cond="إغلاق فوق قمة الرينج ← رجعة تختبر VAH ← دخول مع الاتجاه"),
 "B": dict(title="كسر القيمة والرجعة — بيع", side="بيع",
           cond="إغلاق تحت قاع الرينج ← رجعة تختبر VAL ← بيع مع الاتجاه"),
 "C": dict(title="ارتداد من قاع القيمة VAL", side="شراء",
           cond="لمسة VAL داخل رينج متوازن ← ارتداد نحو POC"),
 "D": dict(title="رفض من قمة القيمة VAH", side="بيع",
           cond="لمسة VAH داخل رينج متوازن ← رفض ونزول نحو POC"),
 "E": dict(title="قاعدة الـ80% — عبور القيمة", side="شراء",
           cond="رجوع السعر داخل القيمة بعد خروج ← عبور متوقع للطرف الثاني"),
 "F": dict(title="فشل الكسر — بيع للعودة", side="بيع",
           cond="كسر فوق القيمة يفشل ويرجع داخلها ← بيع نحو VAL"),
}

def trade_chart(tr):
    w = [dict(c) for c in tr["w"]]
    year = w[0]["d"][:4]
    for c in w: c["d"] = c["d"][5:]
    rngN = tr["rngN"]; jr = tr["jr"]; bk = tr.get("bk")
    prof = profile(w[:rngN])
    Wr, Hr = 980, 540
    ymin = min(c["l"] for c in w); ymax = max(c["h"] for c in w)
    pad = (ymax - ymin) * 0.06; ymin -= pad; ymax += pad*1.6
    svg, x, y, slot = chart(w, Wr, Hr, ymin, ymax, price_axis=True, dates=True, grid=5,
                            pt=46, pb=38, pl=12, pr=74)
    plotL = 12; rend = x(rngN-1) + slot*0.5
    vah, val, pocp = prof["vah"], prof["val"], prof["pocp"]
    # value band + bars over the profiled region
    svg += (f'<rect x="{plotL}" y="{y(vah):.2f}" width="{rend-plotL:.2f}" '
            f'height="{y(val)-y(vah):.2f}" fill="{TEAL}" opacity="0.10"/>')
    svg += vp_bars(prof, x, y, plotL, (rend-plotL)*0.36)
    # lines: interacted line extends to its candle (stop-at-candle rule)
    vah_end = x(jr)+slot*0.5 if tr["t"] in ("A","D","F") else rend
    val_end = x(jr)+slot*0.5 if tr["t"] in ("B","C","E") else rend
    svg += f'<line x1="{plotL}" y1="{y(pocp):.2f}" x2="{rend:.2f}" y2="{y(pocp):.2f}" stroke="{INK}" stroke-width="1.7" stroke-dasharray="7 6"/>'
    svg += f'<line x1="{plotL}" y1="{y(vah):.2f}" x2="{vah_end:.2f}" y2="{y(vah):.2f}" stroke="{INK}" stroke-width="1.7"/>'
    svg += f'<line x1="{plotL}" y1="{y(val):.2f}" x2="{val_end:.2f}" y2="{y(val):.2f}" stroke="{MUTE}" stroke-width="1.5"/>'
    svg += hend(max(vah_end,val_end), y(vah if tr["t"] in ("A","D","F") else val), INK)
    svg += htext(x(1), y(vah)-11, "VAH", INK, 16, weight=800)
    svg += htext(x(rngN-4), y(pocp)-11, "POC", INK, 16, weight=800)
    svg += htext(x(1), y(val)+23, "VAL", MUTE, 15, weight=800)
    # breakout arrow (gap rule) for breakout types
    if bk is not None:
        up = tr["t"] == "A"
        lvl = vah if tr["t"] in ("A","F") else val
        ax = x(bk) + slot*0.55
        if up or tr["t"]=="F":
            y0 = y(w[bk]["l"]) + 24 if up else y(w[bk]["h"]) - 24
        else:
            y0 = y(w[bk]["h"]) - 24
        if tr["t"] in ("A",):
            svg += (f'<line x1="{ax:.2f}" y1="{y0:.2f}" x2="{ax:.2f}" y2="{y(lvl)+3:.2f}" stroke="{TEAL_D}" stroke-width="2.4"/>'
                    f'<polygon points="{ax:.2f},{y(lvl)+3:.2f} {ax-6:.2f},{y(lvl)+13:.2f} {ax+6:.2f},{y(lvl)+13:.2f}" fill="{TEAL_D}"/>')
        elif tr["t"] == "B":
            svg += (f'<line x1="{ax:.2f}" y1="{y0:.2f}" x2="{ax:.2f}" y2="{y(lvl)-3:.2f}" stroke="{RED}" stroke-width="2.4"/>'
                    f'<polygon points="{ax:.2f},{y(lvl)-3:.2f} {ax-6:.2f},{y(lvl)-13:.2f} {ax+6:.2f},{y(lvl)-13:.2f}" fill="{RED}"/>')
        else:  # F: failed breakout marker
            svg += htext(x(bk)-10, y(w[bk]["h"])-40, "كسر فاشل", RED, 16, "end")
    # entry / stop / target
    e_col = TEAL_D if META[tr["t"]]["side"]=="شراء" else RED
    svg += (f'<circle cx="{x(jr):.2f}" cy="{y(tr["entry"]):.2f}" r="9" fill="none" stroke="{e_col}" stroke-width="2.4"/>'
            f'<polyline points="{x(jr)-4:.2f},{y(tr["entry"]):.2f} {x(jr)-1:.2f},{y(tr["entry"])+3.5:.2f} {x(jr)+5:.2f},{y(tr["entry"])-4:.2f}" '
            f'fill="none" stroke="{e_col}" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/>')
    svg += htext(x(jr), y(w[jr]["l"]) + 30, "دخول", e_col, 17)
    svg += (f'<line x1="{x(max(0,jr-3)):.2f}" y1="{y(tr["stop"]):.2f}" x2="{x(min(29,jr+4)):.2f}" y2="{y(tr["stop"]):.2f}" '
            f'stroke="{RED}" stroke-width="1.6" stroke-dasharray="5 5"/>')
    svg += htext(x(min(29,jr+4))+10, y(tr["stop"])+6, "ستوب", RED, 14, "start")
    svg += (f'<line x1="{x(jr):.2f}" y1="{y(tr["tgt"]):.2f}" x2="{x(29)+slot*0.5:.2f}" y2="{y(tr["tgt"]):.2f}" '
            f'stroke="{TEAL_D}" stroke-width="1.8" stroke-dasharray="6 5"/>')
    svg += hend(x(29)+slot*0.5, y(tr["tgt"]), TEAL_D)
    svg += htext(x(25), y(tr["tgt"])-13, f'الهدف  +{tr["pips"]} نقطة', TEAL_D, 18, weight=800)
    return svg + "</svg>", year

# ---------- page scaffolding (guide-style) ----------
def pcount(i, dark=False):
    col = CYAN if dark else TEAL_D
    return f'<div class="pcount" style="color:{col};border-color:{col}"><b>{i}</b><i>/</i><b>{NP}</b></div>'
def header(i):
    return (f'{pcount(i)}<div class="hd"><div class="hgem">{GEM}</div>'
            f'<div class="hwm"><span class="hln"></span><span class="hwmt">LIQUIDITY STATE</span><span class="hln"></span></div></div>')
def pbar(i): return f'<div class="pbar"><i style="width:{i/NP*100:.1f}%"></i></div>'
def eyebrow(t): return f'<div class="eyeb"><span class="dsh"></span>{t}<span class="dsh"></span></div>'

PAGES = []
def page(html, dark=False, tag=None):
    i = len(PAGES) + 1
    t = f'<div class="tag">{tag}</div>' if tag else ''
    if dark: PAGES.append(f'<div class="slide dark">{html}{t}{pbar(i)}</div>')
    else: PAGES.append(f'<div class="slide">{header(i)}{html}{t}{pbar(i)}</div>')

TOT = sum(t["pips"] for t in TRADES)
# P1 cover
page(f'''{pcount(1, True)}<div class="ptag">الدليل العملي</div>
<div class="pmid">
  <div class="pgem">{GEM}</div>
  <div class="pwm"><span class="pln l"></span><span class="pwmt">LIQUIDITY STATE</span><span class="pln r"></span></div>
  <div class="pdivg"><span></span><i></i><span></span></div>
  <h1 class="ptitle">10 صفقات<br>فوليوم بروفايل</h1>
  <div class="pdivg"><span></span><i></i><span></span></div>
  <div class="peyeb">مجموع النتائج: +{TOT:,} نقطة</div>
  <div class="psub">صفقات حقيقية موثقة من EUR/USD — بستة أنماط مختلفة من منطقة القيمة، خطوة بخطوة</div>
  <div class="ppill">10 صفقات · 6 أنماط · بيانات حقيقية</div>
  <div class="prow">
    <div class="pi"><div class="pic">{IPRO}</div><span>قيمة</span></div><div class="pv"></div>
    <div class="pi"><div class="pic">{IUP}</div><span>كسر</span></div><div class="pv"></div>
    <div class="pi"><div class="pic">{IENT}</div><span>دخول</span></div>
  </div>
</div>''', dark=True)

# P2 legend
page(f'''<div class="body">
{eyebrow("قبل ما تبدأ")}
<h2 class="ttl">كيف تقرأ الصفقات؟</h2>
<div class="steps">
  <div class="stp"><span class="num">P</span><p><b>POC</b> — أكثر سعر تداول عنده السوق (الخط المتقطع الكحلي). مغناطيس السعر.</p></div>
  <div class="stp"><span class="num">V</span><p><b>VAH / VAL</b> — قمة وقاع منطقة القيمة (70% من التداول). حدود القرار.</p></div>
  <div class="stp"><span class="num">✓</span><p><b>الدائرة</b> = الدخول · <span class="tr">الأحمر المتقطع</span> = الستوب · <b class="tt">التركواز المتقطع</b> = الهدف.</p></div>
</div>
<p class="capt">كل صفقة على <b>30 شمعة حقيقية</b> — الأسعار والنتائج كما حصلت بالضبط. لا تنسخ الصفقات — <b>افهم النمط</b>.</p>
</div>''', tag="لغرض تعليمي")

# P3..P12 trades
for n, tr in enumerate(TRADES, 1):
    m = META[tr["t"]]
    svgc, year = trade_chart(tr)
    rr = abs(tr["tgt"]-tr["entry"]) / max(abs(tr["entry"]-tr["stop"]), 1e-9)
    side_cls = "tt" if m["side"]=="شراء" else "tr"
    page(f'''<div class="body">
<div class="realh"><div class="numrow"><span class="num">{n}</span><h2 class="ttl2">{m["title"]}</h2></div>
<span class="tick">EUR/USD يومي · {year}</span></div>
<p class="rule">{m["cond"]}</p>
<div class="chartw">{svgc}</div>
<div class="statrow">
  <div class="stc"><span>الاتجاه</span><b class="{side_cls}">{m["side"]}</b></div>
  <div class="stc"><span>الدخول</span><b>{tr["entry"]:.5f}</b></div>
  <div class="stc"><span>الستوب</span><b>{tr["stop"]:.5f}</b></div>
  <div class="stc"><span>الهدف</span><b>{tr["tgt"]:.5f}</b></div>
  <div class="stc hi"><span>النتيجة</span><b>+{tr["pips"]} نقطة</b></div>
  <div class="stc"><span>R:R</span><b>1:{rr:.1f}</b></div>
</div>
</div>''', tag="لغرض تعليمي · بيانات حقيقية")

# P13 CTA
page(f'''<div class="body ctab">
<h2 class="ttl center">خلّ الملف معاك</h2>
<div class="steps wide">
  <div class="stp"><span class="cnum">✓</span><p><b>احفظ الملف</b> — وارجع له قبل كل جلسة تحليل.</p></div>
  <div class="stp"><span class="cnum">✓</span><p><b>شاركه</b> مع متداول يذبحه مطاردة السعر.</p></div>
  <div class="stp"><span class="cnum">✓</span><p>تابع «<b class="tt">@liquidity.state</b>» — دروس الفوليوم بروفايل تكمل هناك.</p></div>
</div>
<div class="hand">{GEM}<span dir="ltr">@liquidity.state</span></div>
</div>''', tag="لغرض تعليمي — الأداء السابق لا يضمن المستقبل")

assert len(PAGES) == NP, len(PAGES)

CSS = f'''*{{margin:0;padding:0;box-sizing:border-box}}
body{{background:#cfcabf;font-family:'Tajawal',sans-serif}}
.slide{{position:relative;width:1080px;height:1350px;overflow:hidden;direction:rtl;
  background:radial-gradient(120% 90% at 50% 0%, #F7F3EC 0%, {CREAM} 45%, {CREAM2} 100%);color:{INK}}}
.slide.dark{{background:radial-gradient(135% 95% at 50% 24%, #0C2029 0%, #08131C 46%, #04090F 100%)}}
.pcount{{position:absolute;top:54px;left:80px;z-index:6;direction:ltr;display:inline-flex;align-items:center;gap:7px;
  font-weight:800;font-size:27px;padding:5px 20px;border-radius:3px;border:1.5px solid;background:transparent}}
.pcount i{{font-style:normal;opacity:.5;font-weight:600}}
.hd{{position:absolute;top:52px;left:0;right:0;display:flex;flex-direction:column;align-items:center;gap:7px;z-index:5}}
.hgem{{width:46px;height:46px;filter:drop-shadow(0 5px 10px rgba(15,46,60,.16))}}
.hwm{{display:flex;align-items:center;gap:12px}}
.hln{{width:34px;height:2px;background:{TEAL_L};display:inline-block}}
.hwmt{{color:{TEAL_D};font-weight:500;letter-spacing:5px;font-size:20px}}
.pbar{{position:absolute;bottom:0;left:0;right:0;height:6px;background:rgba(15,46,60,0.08)}}
.slide.dark .pbar{{background:rgba(67,212,220,0.12)}}
.pbar i{{display:block;height:100%;background:{TEAL}}}
.slide.dark .pbar i{{background:{CYAN}}}
.tag{{position:absolute;bottom:32px;left:0;right:0;text-align:center;color:{MUTE};font-size:20px;font-weight:600}}
.body{{position:absolute;top:170px;left:80px;right:80px;bottom:92px;display:flex;flex-direction:column;gap:24px;justify-content:center}}
.eyeb{{display:flex;align-items:center;justify-content:center;gap:14px;color:{TEAL};font-weight:800;font-size:26px}}
.dsh{{width:42px;height:3px;background:{TEAL_L};display:inline-block}}
.ttl{{font-size:60px;font-weight:900;line-height:1.12;text-align:center}}
.ttl.center{{text-align:center}}
.ttl2{{font-size:44px;font-weight:900;line-height:1.15;text-align:right}}
.tt{{color:{TEAL_D}!important}} .tr{{color:{RED}!important}}
.rule{{font-size:29px;font-weight:700;color:{GREY};text-align:center;line-height:1.5}}
.chartw{{width:100%}} .chartw svg{{width:100%;height:auto;display:block}}
.capt{{font-size:29px;line-height:1.55;color:{GREY};font-weight:600;text-align:center}}
.capt b{{color:{INK};font-weight:900}}
.realh{{display:flex;align-items:center;justify-content:space-between;gap:14px}}
.numrow{{display:flex;align-items:center;gap:18px}}
.num{{width:64px;height:64px;flex:none;display:flex;align-items:center;justify-content:center;font-size:36px;font-weight:900;
  font-style:italic;color:#fff;background:linear-gradient(135deg,{TEAL},{TEAL_D});border-radius:0}}
.tick{{color:{TEAL_D};font-weight:800;font-size:24px;border:1.5px solid {TEAL_L};border-radius:2px;padding:6px 16px;white-space:nowrap}}
.statrow{{display:flex;gap:0;border:1.5px solid {CARDBD}}}
.stc{{flex:1;text-align:center;padding:16px 6px;border-left:1.5px solid {CARDBD}}}
.stc:last-child{{border-left:none}}
.stc span{{display:block;font-size:20px;color:{MUTE};font-weight:700}}
.stc b{{display:block;font-size:25px;color:{INK};font-weight:900;margin-top:4px;direction:ltr}}
.stc.hi{{background:rgba(46,125,150,0.08)}}
.stc.hi b{{color:{TEAL_D}}}
.steps{{display:flex;flex-direction:column;border:1.5px solid {CARDBD}}}
.stp{{display:flex;align-items:center;gap:22px;padding:26px;border-bottom:1.5px solid {CARDBD}}}
.stp:last-child{{border-bottom:none}}
.stp p{{font-size:31px;font-weight:600;color:{GREY};line-height:1.55;text-align:right}}
.stp p b{{color:{INK};font-weight:900}}
.stp .num{{font-style:normal}}
.cnum{{width:60px;height:60px;flex:none;display:flex;align-items:center;justify-content:center;font-size:32px;
  font-weight:900;color:{TEAL_D};border:2px solid {TEAL_D};border-radius:0}}
.hand{{display:flex;align-items:center;gap:14px;justify-content:center;margin-top:8px}}
.hand svg{{width:52px;height:52px}} .hand span{{font-size:36px;font-weight:800;color:{TEAL_D}}}
.ctab{{justify-content:center}}
.ptag{{position:absolute;top:56px;right:80px;color:{CYAN};border:1.5px solid rgba(67,212,220,.5);border-radius:3px;
  padding:8px 24px;font-size:26px;font-weight:800}}
.pmid{{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;padding:0 90px}}
.pgem{{width:130px;height:130px;filter:drop-shadow(0 0 32px {CYANG})}}
.pwm{{display:flex;align-items:center;gap:14px;margin-top:12px}}
.pln{{width:56px;height:2px}} .pln.l{{background:linear-gradient(90deg,transparent,{CYAN})}} .pln.r{{background:linear-gradient(90deg,{CYAN},transparent)}}
.pwmt{{font-size:34px;font-weight:600;letter-spacing:9px;background:linear-gradient(180deg,#ffffff,#8fa6b0);-webkit-background-clip:text;background-clip:text;color:transparent}}
.pdivg{{display:flex;align-items:center;gap:12px;width:54%;margin:24px 0}}
.pdivg span{{flex:1;height:2px;background:linear-gradient(90deg,transparent,{CYAN},transparent);box-shadow:0 0 12px {CYANG}}}
.pdivg i{{width:10px;height:10px;background:{CYAN};transform:rotate(45deg);box-shadow:0 0 12px {CYAN};flex:none}}
.ptitle{{font-size:112px;font-weight:900;line-height:1.02;letter-spacing:-2px;background:linear-gradient(180deg,#ffffff 0%,#C4D4DB 55%,#7F97A1 100%);-webkit-background-clip:text;background-clip:text;color:transparent;filter:drop-shadow(0 3px 18px rgba(67,212,220,.18))}}
.peyeb{{color:{CYAN};font-size:34px;font-weight:800}}
.psub{{color:#C7D6DC;font-size:30px;font-weight:600;margin-top:12px;line-height:1.5;max-width:780px}}
.ppill{{margin-top:28px;color:#EAF2F5;border:1.5px solid rgba(67,212,220,.5);border-radius:3px;padding:12px 32px;font-size:29px;font-weight:800}}
.prow{{display:flex;align-items:flex-start;gap:26px;margin-top:44px}}
.pi{{display:flex;flex-direction:column;align-items:center;gap:12px;width:130px}}
.pic{{width:54px;height:54px;filter:drop-shadow(0 0 10px rgba(67,212,220,.4))}} .pic svg{{width:100%;height:100%;display:block}}
.pi span{{color:{CYAN};font-size:28px;font-weight:800}}
.pv{{width:1.5px;height:78px;background:linear-gradient(180deg,transparent,rgba(67,212,220,.45),transparent);margin-top:8px}}
'''

HTML = f'''<!DOCTYPE html><html lang="ar" dir="rtl"><head><meta charset="UTF-8">
<title>10 صفقات فوليوم بروفايل | Liquidity State</title>
<style>{FONT_CSS}\n{CSS}</style></head><body>
{''.join(PAGES)}
</body></html>'''
open(os.path.join(HERE, "vp10.html"), "w", encoding="utf-8").write(HTML)
print(f"wrote vp10.html {len(HTML)} bytes, {len(PAGES)} pages, total pips {TOT}")
