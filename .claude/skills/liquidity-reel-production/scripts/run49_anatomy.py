# -*- coding: utf-8 -*-
"""تشغيلة ٤٩ — صورة «تشريح حركة السيولة» بهوية الحساب.

🔒 أمر فهد 2026-08-09: أرسل لقطةً من منشور حساب آخر — جارت USDCAD دقيقة
موسوماً بالإسبانية (Stop Hunt · Major BSL · Bearish OB · CISD · Liquidity
Void…) — وطلب الصورة بهويته. فلم تُنسخ صورتُهم ولا تحليلُهم ولا أرقامُهم:
المصطلحات اصطلاحاتُ سوقٍ عامّة، والباقي بُني من جديد على **نافذتنا**
بوسومٍ **تُقاس من شموعها** لا تُنقل عنهم. ولا رمزَهم ولا فريمَهم ولا
ترتيبَ وسومهم — حتى الأداة اختيرت غير أداتهم عمداً.

النافذة: الأسترالي/الدولار · يومي · 2023-08-21 → 2023-10-31 (٥٢ شمعة).
اختيرت بالقياس: قمّتان متساويتان (فرق ٠٫٥٥٪ من المدى)، وشمعة صيدٍ تأخذهما
وتغلق تحتهما بذيلٍ علويّ ٤٧٪ من مداها، ثم اندفاعٌ جسمه ٣٣٪ من مدى النافذة،
ثم هبوطٌ يبلغ ٨٦٪ منه.

    python3 run49_anatomy.py         # يكتب anat49.html
    python3 car_render.py anat49.html out49
"""
import json, math, os

from reel_build import (CREAM, INK, TEAL, TEAL_D, TEAL_L, RED, GREY, MUTE,
                        RBULL, RBEAR, htext, GEM)
from car_common import CW, brandbar, build_carousel
import chart_registry

HERE = os.path.dirname(os.path.abspath(__file__))
RUN_ID = "run49-anatomy-2026-08-09"
WIN_FILE = "daily_windows/audusd_1d_2023-08-21.json"

with open(os.path.join(HERE, WIN_FILE), encoding="utf-8") as f:
    R = json.load(f)
W = R["w"]; N = len(W)
NAME = {"AUDUSD=X": "الأسترالي/الدولار", "GBPUSD=X": "الجنيه/الدولار"}[R["sym"]]
TF = {"1d": "يومي"}[R["tf"]]
DP = 5

# ═════════ التشريح يُقرأ من الشموع ═════════
SPAN = max(c["h"] for c in W) - min(c["l"] for c in W)


def _equal_highs():
    """قمّتان متساويتان — السيولة فوق. ثلاث شمعات بينهما على الأقلّ."""
    hi = sorted(range(N), key=lambda i: -W[i]["h"])[:7]
    best = None
    for a in range(len(hi)):
        for b in range(a + 1, len(hi)):
            i, j = sorted((hi[a], hi[b]))
            if j - i < 3:
                continue
            d = abs(W[i]["h"] - W[j]["h"])
            if d <= SPAN * 0.03 and (best is None or d < best[2]):
                best = (i, j, d)
    return best


_e = _equal_highs()
assert _e, "النافذة لا تحمل قمّتين متساويتين"
H1, H2, DH = _e
POOL = max(W[H1]["h"], W[H2]["h"])

# الصيد: تتجاوز القمّتين وتغلق تحتهما — التجاوز وحده ليس صيداً
HUNT = next((k for k in range(H2 + 1, N) if W[k]["h"] > POOL and W[k]["c"] < POOL), None)
assert HUNT is not None, "لا شمعة تأخذ السيولة وترتدّ"
_h = W[HUNT]
HW = (_h["h"] - POOL) / (_h["h"] - _h["l"])

# الاندفاع: أكبر جسمٍ هابط في الشمعات التسع التالية للصيد
DISP = max(range(HUNT, min(HUNT + 9, N)), key=lambda k: W[k]["o"] - W[k]["c"])
BODY = (W[DISP]["o"] - W[DISP]["c"]) / SPAN
assert BODY >= 0.07, f"لا اندفاع يُذكر ({BODY:.0%})"
# بلوك الأوامر: آخر شمعة صاعدة قبل الاندفاع
OB = next((k for k in range(DISP - 1, HUNT - 1, -1) if W[k]["c"] > W[k]["o"]), None)
assert OB is not None, "لا شمعة صاعدة قبل الاندفاع — لا بلوك"
OB_HI, OB_LO = max(W[OB]["o"], W[OB]["c"]), min(W[OB]["o"], W[OB]["c"])

LOW = min(range(DISP, N), key=lambda k: W[k]["l"])
assert LOW > DISP, "لا امتداد بعد الاندفاع"
DROP = (POOL - W[LOW]["l"]) / SPAN
assert H2 < HUNT <= OB < DISP < LOW, "ترتيب التشريح غير متسلسل"

chart_registry.assert_fresh_real(R["sym"], R["tf"], R["start"], R["end"], label="run49-anatomy")

# ═════════ هندسة اللوحة ═════════
GW, GH = 980, 700
_lo = min(c["l"] for c in W); _hi = max(c["h"] for c in W)
gl, gr, gt, gb = 14, 118, 34, 30
gw, gh = GW - gl - gr, GH - gt - gb
PAD_HI, PAD_LO = 0.13, 0.10          # فوقها وسما السيولة والصيد، وتحتها وسم القاع
ymin, ymax = _lo - SPAN * PAD_LO, _hi + SPAN * PAD_HI
slot = gw / N; bw = slot * 0.60
def x(i): return gl + slot * i + slot / 2
def y(p): return gt + (ymax - p) / (ymax - ymin) * gh


def tw(t, fs): return len(t) * fs * 0.55


def clampx(cx, half): return min(max(cx, gl + half + 4), GW - gr - half - 4)


def lbl(cx, cy, txt, col, fs=21, anchor="middle"):
    return htext(cx, cy, txt, col, fs, anchor=anchor)


s = [f'<svg viewBox="0 0 {GW} {GH}" width="{GW}" height="{GH}" xmlns="http://www.w3.org/2000/svg">',
     f'<rect x="0" y="0" width="{GW}" height="{GH}" fill="{CREAM}"/>']
# محور سعر خفيف يمين — الشاشة تُقرأ كشاشة
for k in range(5):
    gy = gt + gh * k / 4
    pv = ymax - (ymax - ymin) * k / 4
    s.append(f'<line x1="{gl}" y1="{gy:.0f}" x2="{GW-gr}" y2="{gy:.0f}" '
             f'stroke="rgba(15,46,60,0.06)" stroke-width="1.4"/>')
    s.append(f'<text x="{GW-gr+8}" y="{gy+6:.0f}" fill="{MUTE}" font-size="17" font-weight="700" '
             f'font-family="system-ui,sans-serif" direction="ltr">{pv:,.{DP}f}</text>')
for i, c in enumerate(W):
    cx = x(i); up = c["c"] >= c["o"]; col = RBULL if up else RBEAR
    top, bot = y(max(c["o"], c["c"])), y(min(c["o"], c["c"]))
    s.append(f'<line x1="{cx:.1f}" y1="{y(c["h"]):.1f}" x2="{cx:.1f}" y2="{y(c["l"]):.1f}" '
             f'stroke="{col}" stroke-width="2.2"/>'
             f'<rect x="{cx-bw/2:.1f}" y="{top:.1f}" width="{bw:.1f}" '
             f'height="{max(bot-top,2.2):.1f}" fill="{col}" rx="1"/>')

# الوسوم شارات مرقّمة لا جُملاً على الجارت: بخمسين شمعة يصير السلوت
# سبعة عشر بكسلاً، وأي جملة عرضها ٢٠٠–٤٠٠ بكسل تعبر عشرين شمعة فتشطبها.
# فالشارة تجلس على الفراغ المجاور للحدث، والكلامُ في المفتاح تحت الرسم.
def badge(cx, cy, n, col):
    return (f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="15" fill="{col}" '
            f'stroke="{CREAM}" stroke-width="2.5"/>'
            f'<text x="{cx:.1f}" y="{cy+7:.1f}" fill="#fff" font-size="20" font-weight="900" '
            f'text-anchor="middle" font-family="Tajawal">{n}</text>')


BX = GW - gr - 26                      # عمود الشارات على يمين اللوحة حيث الفراغ

# ── ١) السيولة فوق: قمّتان متساويتان ──
s.append(f'<line x1="{x(H1)-slot*.8:.1f}" y1="{y(POOL):.1f}" x2="{GW-gr:.1f}" y2="{y(POOL):.1f}" '
         f'stroke="{INK}" stroke-width="2.4"/>')
for j in (H1, H2):
    s.append(f'<circle cx="{x(j):.1f}" cy="{y(W[j]["h"]):.1f}" r="10" fill="none" '
             f'stroke="{INK}" stroke-width="2.8"/>')
s.append(badge(BX, y(POOL) - 20, "١", INK))

# ── ٢) صيد الأوقاف ──
s.append(f'<rect x="{x(HUNT)-slot*.85:.1f}" y="{y(_h["h"])-6:.1f}" width="{slot*1.7:.1f}" '
         f'height="{y(POOL)-y(_h["h"])+6:.1f}" fill="{RED}" fill-opacity=".16" '
         f'stroke="{RED}" stroke-width="1.2" stroke-opacity=".55"/>')
Y2 = y(_h["h"]) - 24
assert Y2 - 15 >= gt, "شارة الصيد تعلو حدّ اللوحة"
s.append(badge(x(HUNT), Y2, "٢", RED))

# ── ٣) بلوك الأوامر البائع ──
OBR = x(min(N - 1, DISP + 18))
s.append(f'<rect x="{x(OB)-slot*.8:.1f}" y="{y(OB_HI):.1f}" width="{OBR-x(OB)+slot*.8:.1f}" '
         f'height="{max(y(OB_LO)-y(OB_HI),3):.1f}" fill="{RED}" fill-opacity=".13" '
         f'stroke="{RED}" stroke-width="1.4" stroke-opacity=".7"/>')
s.append(badge(OBR + 22, (y(OB_HI) + y(OB_LO)) / 2, "٣", RED))

# ── ٤) الاندفاع / فراغ السيولة ──
# الاندفاع يُظلَّل على شمعته نفسها لا بجانبها: علامةٌ مجاورة تصف شيئاً
# لا يشير إليه شيء.
s.append(f'<rect x="{x(DISP)-slot*.85:.1f}" y="{y(W[DISP]["o"]):.1f}" width="{slot*1.7:.1f}" '
         f'height="{max(y(W[DISP]["c"])-y(W[DISP]["o"]),3):.1f}" fill="{TEAL_D}" '
         f'fill-opacity=".18" stroke="{TEAL_D}" stroke-width="1.4" stroke-opacity=".65"/>')
s.append(badge(x(DISP) - slot * 2.8, (y(W[DISP]["o"]) + y(W[DISP]["c"])) / 2, "٤", TEAL_D))

# ── ٥) السيولة السفلى ──
s.append(f'<line x1="{gl}" y1="{y(W[LOW]["l"]):.1f}" x2="{GW-gr:.1f}" y2="{y(W[LOW]["l"]):.1f}" '
         f'stroke="{TEAL_D}" stroke-width="2.2" stroke-dasharray="8 6"/>')
Y5 = y(W[LOW]["l"]) + 22
assert Y5 + 15 <= GH - gb, "شارة السيولة السفلى خارج اللوحة"
s.append(badge(BX, Y5, "٥", TEAL_D))
s.append('</svg>')
CHART = "".join(s)

X49 = f'''
.cont49{{position:absolute;top:150px;left:50px;right:50px;bottom:112px;
  display:flex;flex-direction:column;align-items:center}}
.ttl49{{font-size:52px;font-weight:900;color:{INK};line-height:1.16;text-align:center;letter-spacing:-.5px}}
.ttl49 b{{color:{TEAL_D}}}
.sub49{{margin-top:12px;font-size:26px;font-weight:700;color:{GREY};text-align:center}}
.chip49{{margin-top:16px;border:1.6px solid {TEAL_D};color:{TEAL_D};font-weight:800;
  font-size:22px;padding:6px 16px}}
.gr49{{margin-top:18px;width:100%}}
.gr49 svg{{width:100%;height:auto;display:block}}
.key49{{margin-top:20px;width:100%;display:flex;flex-direction:column;gap:9px}}
.key49 p{{display:flex;gap:12px;align-items:flex-start;text-align:right;
  font-size:24px;font-weight:700;color:#3F5561;line-height:1.4}}
.key49 span{{flex:none;width:32px;height:32px;display:flex;align-items:center;justify-content:center;
  border-radius:50%;background:{TEAL_D};color:#fff;font-size:18px;font-weight:900}}
.foot49{{position:absolute;bottom:40px;left:0;right:0;text-align:center;
  color:#7F97A1;font-size:21px;font-weight:600}}
'''

KEY = [
    "قمّتان متساويتان — فوقهما أوقاف المشترين. هذي السيولة.",
    f"شمعة وحدة تاخذها وتغلق تحتها — ذيلها {HW*100:.0f}٪. صيد، مو كسر.",
    "آخر شمعة صاعدة قبل الاندفاع = بلوك البائع.",
    f"اندفاع جسمه {BODY*100:.0f}٪ من مدى النافذة — يترك فراغ سيولة وراه.",
    f"والسعر يمشي للسيولة المقابلة تحت — {DROP*100:.0f}٪ من المدى.",
]
AR = ["١", "٢", "٣", "٤", "٥"]
keys = "".join(f'<p><span>{AR[i]}</span>{t}</p>' for i, t in enumerate(KEY))

slide = f'''<div class="slide" {CW}>
  {brandbar(True)}
  <div class="cont49">
    <h1 class="ttl49">تشريح <b>حركة السيولة</b></h1>
    <p class="sub49">وش صار بالضبط — خطوة خطوة على شموع حقيقية</p>
    <div class="chip49">{NAME} · {TF} · {R["date"]}</div>
    <div class="gr49">{CHART}</div>
    <div class="key49">{keys}</div>
  </div>
  <div class="foot49">لغرض تعليمي — مو توصية · <span dir="ltr">@liquidity.state</span></div>
</div>'''

if __name__ == "__main__":
    build_carousel([slide], "تشريح حركة السيولة — Liquidity State",
                   os.path.join(HERE, "anat49.html"), extra_css=X49)
    print(f'تشريح | {NAME} {TF} {R["date"]} | شموع {N}\n'
          f'  قمّتان {H1},{H2} فرق {DH:.{DP}f} ({DH/SPAN*100:.2f}٪ من المدى)\n'
          f'  صيد عند {HUNT} · ذيل علويّ {HW*100:.0f}٪ من مدى الشمعة\n'
          f'  بلوك عند {OB} · اندفاع عند {DISP} جسمه {BODY*100:.0f}٪ من المدى\n'
          f'  قاع عند {LOW} · الهبوط {DROP*100:.0f}٪ من المدى')
