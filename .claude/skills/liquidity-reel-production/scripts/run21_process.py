# -*- coding: utf-8 -*-
"""بوستر واحد 1080×1350 — «التداول عمليةٌ لا إشارة».
الفكرة مستوحاة من منشور إنفوجرافيك أجنبي (منهج مكوّن من طبقات ثم مسار تكرار)،
لكن التصميم والنصوص والرسوم كلها من الصفر بهوية Liquidity State،
والطبقات الخمس مقصورة على مجالات تخصصنا (نطاق topics_backlog.scope):
الهيكل، السيولة، مناطق القيمة، تدفّق الأوامر، الجلسات.
"""
import os, math
from reel_build import GEM
from car_common import CW, build_carousel

HERE = os.path.dirname(os.path.abspath(__file__))

CY = "#43D4DC"; LN = "#D8E5EB"; MU = "#7F97A1"; DIM = "#5E7A88"; RD = "#E05656"

def t(x, y, txt, col, fs, w=800):
    return (f'<text x="{x:.1f}" y="{y:.1f}" fill="{col}" font-size="{fs}" font-family="Tajawal" '
            f'font-weight="{w}" text-anchor="middle">{txt}</text>')

def poly(pts, col, w=2.4, dash=None):
    p = " ".join(f"{a:.1f},{b:.1f}" for a, b in pts)
    d = f' stroke-dasharray="{dash}"' if dash else ''
    return (f'<polyline points="{p}" fill="none" stroke="{col}" stroke-width="{w}"{d} '
            f'stroke-linecap="round" stroke-linejoin="round"/>')

def hline(x0, x1, y, col, w=1.6, dash="5 4"):
    return (f'<line x1="{x0}" y1="{y}" x2="{x1}" y2="{y}" stroke="{col}" stroke-width="{w}" '
            f'stroke-dasharray="{dash}"/>')

def dot(x, y, col, r=3.2):
    return f'<circle cx="{x}" cy="{y}" r="{r}" fill="{col}"/>'

def panel(inner, w=182, h=220):
    return f'<svg viewBox="0 0 {w} {h}" width="{w}" height="{h}" xmlns="http://www.w3.org/2000/svg">{inner}</svg>'

# ───────────────────────── الطبقة ١ — هيكل السوق ─────────────────────────
def c_structure():
    P = [(12,178),(34,132),(54,156),(76,100),(96,126),(118,66),(138,110),(160,150)]
    s = [poly(P, LN)]
    s.append(hline(90, 172, 126, RD))
    for x, y in [(54,156),(96,126),(76,100),(118,66)]:
        s.append(dot(x, y, CY))
    s.append(f'<circle cx="147" cy="126" r="5.5" fill="none" stroke="{RD}" stroke-width="2.2"/>')
    s.append(t(91, 204, "كسر أول قاع محمي", RD, 14, 700))
    return panel("".join(s))

# ───────────────────────── الطبقة ٢ — مناطق السيولة ─────────────────────────
def c_liquidity():
    P = [(12,160),(36,64),(58,120),(82,66),(100,112),(124,44),(142,104),(166,176)]
    s = [hline(24, 172, 65, RD), poly(P, LN)]
    s.append(f'<circle cx="124" cy="44" r="6" fill="none" stroke="{RD}" stroke-width="2.2"/>')
    s.append(t(59, 50, "قمم متساوية", MU, 13, 700))
    s.append(t(139, 26, "كَنْس", RD, 14, 900))
    s.append(t(91, 204, "الأوامر خلف القمم", MU, 14, 700))
    return panel("".join(s))

# ───────────────────────── الطبقة ٣ — مناطق القيمة ─────────────────────────
def c_value():
    s = []
    y0, st, n, poc = 42, 13, 11, 5
    for i in range(n):
        y = y0 + i * st
        w = 22 + 98 * math.exp(-((i - poc) ** 2) / 7.0)
        col = CY if i == poc else DIM
        op = "0.95" if i == poc else "0.60"
        s.append(f'<rect x="{158-w:.1f}" y="{y-4.5:.1f}" width="{w:.1f}" height="9" '
                 f'fill="{col}" opacity="{op}"/>')
    s.append(hline(16, 168, y0 + 2 * st - 7, MU, 1.2, "4 4"))
    s.append(hline(16, 168, y0 + 8 * st + 7, MU, 1.2, "4 4"))
    s.append(t(20, y0 + 2 * st - 11, "VAH", MU, 11))
    s.append(t(20, y0 + poc * st + 4, "POC", CY, 11))
    s.append(t(20, y0 + 8 * st + 20, "VAL", MU, 11))
    s.append(t(91, 204, "أين قَبِل السوق", MU, 14, 700))
    return panel("".join(s))

# ───────────────────────── الطبقة ٤ — تدفّق الأوامر ─────────────────────────
def c_flow():
    BID = [156, 198, 245, 312, 365, 298, 256]
    ASK = [143, 167, 232, 278, 310, 329, 254]
    PRC = [23560, 23555, 23550, 23545, 23540, 23535, 23530]
    HL = 4
    s = [t(40, 34, "BID", MU, 13, 700), t(142, 34, "ASK", MU, 13, 700)]
    for x in (66, 116):
        s.append(f'<line x1="{x}" y1="42" x2="{x}" y2="188" stroke="{MU}" '
                 f'stroke-width="1" opacity="0.22"/>')
    for i in range(7):
        y = 56 + i * 20
        if i == HL:
            s.append(f'<rect x="10" y="{y-14}" width="162" height="21" fill="{CY}" opacity="0.12"/>')
            s.append(f'<rect x="124" y="{y-14}" width="36" height="21" fill="none" '
                     f'stroke="{CY}" stroke-width="1.4"/>')
        s.append(t(40, y, str(BID[i]), LN if i != HL else CY, 15, 700))
        s.append(t(91, y, str(PRC[i]), MU, 14, 600))
        s.append(t(142, y, str(ASK[i]), LN if i != HL else CY, 15, 700))
    s.append(t(91, 204, "اختلال عند السعر", MU, 14, 700))
    return panel("".join(s))

# ───────────────────────── الطبقة ٥ — الجلسات ─────────────────────────
def c_sessions():
    s = []
    for i, (a, b) in enumerate([(12, 64), (64, 116), (116, 168)]):
        on = i == 1
        s.append(f'<rect x="{a}" y="40" width="{b-a}" height="120" '
                 f'fill="{CY if on else "#ffffff"}" opacity="{0.09 if on else 0.03}"/>')
        s.append(f'<rect x="{a}" y="40" width="{b-a}" height="120" fill="none" '
                 f'stroke="{CY if on else MU}" stroke-width="1" opacity="{0.45 if on else 0.20}"/>')
    P = [(14,124),(26,116),(38,126),(50,118),(62,122),
         (74,130),(84,96),(96,106),(106,66),(116,74),
         (128,60),(140,70),(152,52),(166,58)]
    s.append(poly(P, LN, 2.2))
    for x, lab, col in [(38, "آسيا", MU), (90, "لندن", CY), (142, "نيويورك", MU)]:
        s.append(t(x, 182, lab, col, 15, 900))
    return panel("".join(s))

# ───────────────────────── أيقونات المسار ─────────────────────────
def i_knowledge():
    s = []
    for i, (x, w) in enumerate([(8, 48), (12, 40), (16, 32)]):
        s.append(f'<rect x="{x}" y="{40-i*13}" width="{w}" height="9" rx="2" fill="none" '
                 f'stroke="{CY}" stroke-width="2.2"/>')
    return panel("".join(s), 64, 56)

def i_conviction():
    """درع فيه علامة صح — الثقة بالمنهج، لا سهم آخر يشبه أيقونة الاتّساق."""
    s = [f'<path d="M32 6 L52 14 V30 C52 42 42 49 32 52 C22 49 12 42 12 30 V14 Z" fill="none" '
         f'stroke="{CY}" stroke-width="2.2" stroke-linejoin="round"/>',
         f'<polyline points="23,29 30,36 43,21" fill="none" stroke="{CY}" stroke-width="2.6" '
         f'stroke-linecap="round" stroke-linejoin="round"/>']
    return panel("".join(s), 64, 56)

def i_execution():
    s = [f'<circle cx="28" cy="32" r="19" fill="none" stroke="{CY}" stroke-width="2.2" opacity="0.55"/>',
         f'<circle cx="28" cy="32" r="10" fill="none" stroke="{CY}" stroke-width="2.2"/>',
         f'<circle cx="28" cy="32" r="3.6" fill="{CY}"/>',
         f'<line x1="54" y1="6" x2="34" y2="26" stroke="{CY}" stroke-width="2.2" stroke-linecap="round"/>',
         f'<polyline points="54,16 54,6 44,6" fill="none" stroke="{CY}" stroke-width="2.2" '
         f'stroke-linecap="round" stroke-linejoin="round"/>']
    return panel("".join(s), 64, 56)

def i_consistency():
    s = []
    for i, h in enumerate([12, 19, 26, 34]):
        s.append(f'<rect x="{9+i*13}" y="{48-h}" width="8" height="{h}" fill="{CY}" '
                 f'opacity="{0.35+i*0.2:.2f}"/>')
    s.append(f'<polyline points="8,26 22,18 36,20 54,6" fill="none" stroke="{CY}" '
             f'stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>')
    s.append(f'<polyline points="46,6 54,6 54,14" fill="none" stroke="{CY}" stroke-width="2.2" '
             f'stroke-linecap="round" stroke-linejoin="round"/>')
    return panel("".join(s), 64, 56)

# ───────────────────────── البوستر ─────────────────────────
COLS = [("هيكل السوق",    "اقرأ من يقود.",     c_structure),
        ("مناطق السيولة", "حدّد أين الوقود.",  c_liquidity),
        ("مناطق القيمة",  "اعرف أين القبول.",  c_value),
        ("تدفّق الأوامر",  "نفّذ على دليل.",    c_flow),
        ("الجلسات",       "تحرّك في وقته.",    c_sessions)]

STEPS = [("معرفة",  "ابنِ حافّتك.",   i_knowledge),
         ("قناعة",  "ثِق بمنهجك.",    i_conviction),
         ("تنفيذ",  "التزم بالخطة.",  i_execution),
         ("اتّساق",  "كرّر وحسّن.",     i_consistency)]

PCSS = '''
.pw{position:absolute;inset:0;padding:0}
.phd{position:absolute;top:44px;left:0;right:0;display:flex;flex-direction:column;
  align-items:center;gap:9px}
.phd .g{width:46px;height:46px}
.phd .g svg{width:100%;height:100%;filter:drop-shadow(0 0 16px rgba(67,212,220,0.40))}
.phd .w{font-weight:700;font-size:16px;letter-spacing:8px;color:#9FB4BD}
.pey{position:absolute;top:164px;left:0;right:0;text-align:center;color:#43D4DC;
  font-weight:800;font-size:25px;letter-spacing:1px}
.ph1{position:absolute;top:202px;left:0;right:0;text-align:center;font-size:72px;font-weight:900;
  line-height:1.14;letter-spacing:-1px;
  background:linear-gradient(180deg,#ffffff,#C4D4DB 60%,#8FA6AF);
  -webkit-background-clip:text;background-clip:text;color:transparent;
  filter:drop-shadow(0 0 24px rgba(67,212,220,0.20))}
.pbar{position:absolute;top:386px;left:325px;width:430px;height:3px;
  background:linear-gradient(90deg,transparent,#43D4DC,transparent)}
.psub{position:absolute;top:404px;left:0;right:0;text-align:center;color:#9FB4BD;
  font-size:29px;font-weight:600}

.pgrid{position:absolute;top:486px;left:56px;right:56px;display:flex;gap:14px;justify-content:center}
.pcol{width:182px}
.pt{font-size:25px;font-weight:900;color:#ECF3F6;text-align:center;white-space:nowrap}
.pu{width:40px;height:3px;margin:9px auto 13px;background:#43D4DC;opacity:.8}
.pbox{background:transparent;border:0;
  height:232px;display:flex;align-items:center;justify-content:center}
.pbox svg{display:block}
.pcap{margin-top:14px;font-size:22px;font-weight:700;color:#9FB4BD;text-align:center;white-space:nowrap}

.psep{position:absolute;top:872px;left:150px;right:150px;height:1px;
  background:linear-gradient(90deg,transparent,rgba(67,212,220,0.35),transparent)}
.pey2{position:absolute;top:896px;left:0;right:0;text-align:center;color:#7F97A1;
  font-size:24px;font-weight:700;letter-spacing:.5px}

.prow{position:absolute;top:962px;left:70px;right:70px;display:flex;align-items:flex-start;
  justify-content:space-between}
.pstep{width:196px;text-align:center}
.pstep .ic{height:58px;display:flex;align-items:center;justify-content:center}
.pstep h3{margin-top:10px;font-size:32px;font-weight:900;color:#ECF3F6}
.pstep p{margin-top:6px;font-size:22px;font-weight:600;color:#8FA6AF}
.parr{width:34px;color:#43D4DC;font-size:30px;font-weight:900;opacity:.55;
  line-height:58px;text-align:center}

.pfoot{position:absolute;top:1150px;left:120px;right:120px;text-align:center;
  border:1px solid rgba(67,212,220,0.35);background:rgba(67,212,220,0.05);
  padding:17px 0;font-size:31px;font-weight:900;color:#ECF3F6}
.pmeta{position:absolute;bottom:44px;left:0;right:0;text-align:center;color:#5E7A88;
  font-size:21px;font-weight:600;letter-spacing:.3px}
.ltr{direction:ltr;unicode-bidi:isolate;display:inline-block}
'''

def build(out="poster_process.html"):
    cols = "".join(
        f'<div class="pcol"><div class="pt">{ti}</div><div class="pu"></div>'
        f'<div class="pbox">{fn()}</div><div class="pcap">{cap}</div></div>'
        for ti, cap, fn in COLS)
    steps = []
    for i, (nm, sub, fn) in enumerate(STEPS):
        if i:
            steps.append('<div class="parr">←</div>')
        steps.append(f'<div class="pstep"><div class="ic">{fn()}</div>'
                     f'<h3>{nm}</h3><p>{sub}</p></div>')
    slide = f'''<div class="slide dark" {CW}>
  <div class="pw">
    <div class="phd"><div class="g">{GEM}</div><div class="w">LIQUIDITY STATE</div></div>
    <div class="pey">المنهج</div>
    <h1 class="ph1">التداول عمليةٌ،<br>لا إشارة.</h1>
    <div class="pbar"></div>
    <p class="psub">خمس طبقات تُقرأ بالترتيب — ثم يُبنى الاتّساق.</p>
    <div class="pgrid">{cols}</div>
    <div class="psep"></div>
    <div class="pey2">ثم تتحوّل المعرفة إلى عادة</div>
    <div class="prow">{"".join(steps)}</div>
    <div class="pfoot">أتقن العملية قبل أن تطلب النتيجة.</div>
    <div class="pmeta">رسوم تخطيطية لغرض تعليمي · <span class="ltr">@liquidity.state</span></div>
  </div>
</div>'''
    p = os.path.join(HERE, out)
    n = build_carousel([slide], "التداول عملية — بوستر", p, extra_css=PCSS)
    print("poster:", p, n)
    return p

if __name__ == "__main__":
    build()
