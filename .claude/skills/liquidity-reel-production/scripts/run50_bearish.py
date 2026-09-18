# -*- coding: utf-8 -*-
"""تشغيلة ٥٠ — «نموذج الدخول البيعي» بألوان الحساب.

🔒 أمر فهد 2026-08-09: أرسل بوستره القديم (شعاره ومعرّفه عليه) وطلب
تحويله إلى ألوانه. البوستر الأصلي بأخضر/أحمر عامّين وخلفية كحلية عامّة —
وهي ألوان أي منصّة، لا ألوان الحساب. فأُعيد بناؤه كلّه بلوحة §1 الداكنة:

  خلفية    radial  #0C2029 → #08131C → #04090F
  العنوان  «BEARISH» أحمر §1 (`#E05656`) — والأحمر عندنا **للهبوط
           والانعكاس حصراً**، فاستعماله هنا دلالةٌ لا زينة —
           و«ENTRY» بتدرّج معدني أبيض→فضي كما في أغلفة الحساب.
  الشموع   صاعدة `#43D4DC` وهابطة `#5E7A88` (الوضع الداكن) بدل
           الأخضر/الأحمر العامّين.
  الهيكل   الهابط أحمر، والهدف سيان، والإمبالانس بالحيادي `#D8E5EB`.

والشموع مولَّدة (درسٌ مفاهيمي لا صفقة: لا دخول ولا وقف ولا هدف بأرقام)،
مبصومة في `used_charts.json` بالبذرة والمرتكزات فلا تتكرّر. وكل وسمٍ
**يُقاس من السلسلة** بعد توليدها لا يُرسم بالتقدير: القمّة المكنوسة
والقاعان المكسوران والفجوة الحقيقية — فإن تغيّرت البذرة تغيّرت المواضع
أو سقط البناء.

    python3 run50_bearish.py && python3 car_render.py bear50.html out50
"""
import json, math, os

from reel_build import gen, FONT_CSS, GEM
import chart_registry

HERE = os.path.dirname(os.path.abspath(__file__))
RUN_ID = "run50-bearish-entry"

# لوحة §1 الداكنة
BG0, BG1, BG2 = "#0C2029", "#08131C", "#04090F"
CYAN, RED = "#43D4DC", "#E05656"
UPC, DNC = "#43D4DC", "#5E7A88"
TXT, SUB, MUTE = "#D8E5EB", "#8FA6AF", "#6B7C84"

# ── السلسلة: تراكم ← صعود ← كنس القمّة ← تغيّر الطابع ← ارتداد ← كسر ← هدف ──
# المستويات تُباعَد عمداً والضجيج يُخفَّض: المحاولة الأولى فرضت قاعاً عند
# ٢٤ فحفره المولّد إلى ١٤٫٧٦ — أعمقَ من الساق الهابطة كلّها — فلم يُكسر
# «تغيّر الطابع» إلا عند الشمعة ٤٣ فازدحمت القصّة في آخر الرسم. الفصل بين
# أيّ مستويين هنا ≥ ٤ وحدات، وسعة الضجيج ±٠٫٥ — فلا ينقلب ترتيبها.
# ولا تُفرض قيعان: تُفرض القمّتان فقط ليصحّ الكنس، والقيعان تتشكّل وحدها.
SEED = 5023
ANCH = [(0, 10.5), (10, 11.0), (20, 24.0), (24, 19.0), (27, 26.0),
        (33, 14.0), (38, 20.0), (46, 9.5)]
SWINGS = [(20, 'H'), (27, 'H')]
N = 47
chart_registry.assert_fresh_synthetic(SEED, ANCH, label="نموذج الدخول البيعي")
W = gen(ANCH, N, SEED, wick=0.55, bn=0.35, swings=SWINGS)

# ═════════ كل وسمٍ يُقاس من السلسلة ═════════
SPAN = max(c["h"] for c in W) - min(c["l"] for c in W)

TOP = max(range(N), key=lambda i: W[i]["h"])          # القمّة المكنوسة — السيولة العليا
PRE = max(range(0, 24), key=lambda i: W[i]["h"])      # القمّة السابقة عليها
assert W[TOP]["h"] > W[PRE]["h"], "القمّة الثانية لم تتجاوز الأولى — لا كنس"

CH_L = min(range(PRE, TOP), key=lambda i: W[i]["l"])  # القاع الذي كسرُه = تغيّر الطابع
CH_B = next((k for k in range(TOP + 1, N) if W[k]["c"] < W[CH_L]["l"]), None)
assert CH_B is not None, "لم يُكسر القاع بعد القمّة — لا تغيّر طابع"
# ويقع في الثلثين الأولين وإلا ازدحمت القصّة كلها في طرف الرسم الأيمن
assert CH_B <= N * 0.72, f"تغيّر الطابع متأخّر ({CH_B}/{N}) — القصّة تزدحم"

# الهدف أولاً (أدنى قاعٍ في السلسلة)، ثم يُستخرج ما بينه وبين الكسر:
# قمّة الارتداد ثم قاع الساق الأولى. عكسُ الترتيب يجعل «قاع الساق الأولى»
# هو القاع النهائي نفسه، فلا يبقى بعده ارتدادٌ يُقاس (أمسكه `assert`).
END = min(range(CH_B, N), key=lambda i: W[i]["l"])    # الهدف: السيولة السفلى
RET = max(range(CH_B + 2, END), key=lambda i: W[i]["h"])   # قمّة الارتداد — منطقة الدخول
LOW1 = min(range(CH_B, RET), key=lambda i: W[i]["l"])      # قاع الساق الأولى
assert CH_B < LOW1 < RET < END, "تتابع الساقين غير صحيح"
BOS_B = next((k for k in range(RET + 1, N) if W[k]["c"] < W[LOW1]["l"]), None)
assert BOS_B is not None, "لم يُكسر قاع الساق الأولى — لا كسر هيكل"
assert W[END]["l"] < W[LOW1]["l"], "الهدف ليس تحت قاع الساق الأولى"

# منطقة الدخول: من قمّة الارتداد إلى أعلى جسمٍ فيها — مقيسة لا مرسومة
RZ_HI = W[RET]["h"]
RZ_LO = max(W[RET]["o"], W[RET]["c"])
assert RZ_HI > RZ_LO, "قمّة الارتداد بلا فتيل — لا منطقة"

# الفجوة (IMB): ثلاث شمعات لا يلامس فيها فتيل الأولى فتيلَ الثالثة
IMB = None
for k in range(11, max(12, PRE - 1)):
    if W[k + 1]["l"] > W[k - 1]["h"]:
        g = W[k + 1]["l"] - W[k - 1]["h"]
        if IMB is None or g > IMB[1]:
            IMB = (k, g)
assert IMB, "لا فجوة حقيقية في الساق الصاعدة"
IMB_I, IMB_G = IMB
assert 11 <= IMB_I < PRE, "الفجوة خارج ساق الصعود"

# ═════════ الرسم ═════════
GW, GH = 1000, 880
gl, gr, gt, gb = 40, 40, 40, 78
gw, gh = GW - gl - gr, GH - gt - gb
_lo = min(c["l"] for c in W); _hi = max(c["h"] for c in W)
pad = SPAN * 0.07
ymin, ymax = _lo - pad, _hi + pad
slot = gw / N; bw = slot * 0.56
def x(i): return gl + slot * i + slot / 2
def y(p): return gt + (ymax - p) / (ymax - ymin) * gh


def lab(cx, cy, t, col, fs=19, anchor="middle", ls=2.4):
    return (f'<text x="{cx:.1f}" y="{cy:.1f}" fill="{col}" font-size="{fs}" '
            f'font-family="Tajawal" font-weight="800" letter-spacing="{ls}" '
            f'text-anchor="{anchor}" direction="ltr">{t}</text>')


s = [f'<svg viewBox="0 0 {GW} {GH}" width="{GW}" height="{GH}" xmlns="http://www.w3.org/2000/svg">']

# منطقة الدخول — خلفها الشموع فتُرسم أولاً
# المنطقة تبدأ من قمّة الارتداد لا من القمّة الكبرى: الارتداد لا يبلغ
# نطاق مصدر الهبوط (قِيس: 20.27 مقابل 25.45)، فنسبتُها إليه ادّعاءٌ على
# الرسم. ووسمُها فوقها لا داخلها — داخلها شموع.
s.append(f'<rect x="{x(RET)-slot*2.2:.1f}" y="{y(RZ_HI):.1f}" '
         f'width="{GW-gr-x(RET)+slot*2.2:.1f}" height="{y(RZ_LO)-y(RZ_HI):.1f}" '
         f'fill="{RED}" fill-opacity=".18" stroke="{RED}" stroke-width="1.3" stroke-opacity=".5"/>')
s.append(lab(GW - gr - 8, y(RZ_HI) - 16, "ENTRY ZONE", TXT, 20, "end", 3.2))

for i, c in enumerate(W):
    cx = x(i); up = c["c"] >= c["o"]; col = UPC if up else DNC
    top, bot = y(max(c["o"], c["c"])), y(min(c["o"], c["c"]))
    s.append(f'<line x1="{cx:.1f}" y1="{y(c["h"]):.1f}" x2="{cx:.1f}" y2="{y(c["l"]):.1f}" '
             f'stroke="{col}" stroke-width="2.2"/>'
             f'<rect x="{cx-bw/2:.1f}" y="{top:.1f}" width="{bw:.1f}" '
             f'height="{max(bot-top,2.4):.1f}" fill="{col}" rx="1"/>')

# ① السيولة العليا المكنوسة
s.append(f'<line x1="{x(PRE)-slot*.8:.1f}" y1="{y(W[PRE]["h"]):.1f}" '
         f'x2="{x(TOP)+slot*.8:.1f}" y2="{y(W[PRE]["h"]):.1f}" '
         f'stroke="{RED}" stroke-width="2"/>')
s.append(lab(x(PRE) - slot * 1.8, y(W[PRE]["h"]) + 7, "$", RED, 26, "middle", 0))

# ② تغيّر الطابع
s.append(f'<line x1="{x(CH_L)-slot*.8:.1f}" y1="{y(W[CH_L]["l"]):.1f}" '
         f'x2="{x(CH_B)+slot*1.2:.1f}" y2="{y(W[CH_L]["l"]):.1f}" '
         f'stroke="{RED}" stroke-width="2"/>')
s.append(lab(x(CH_B) + slot * 1.2, y(W[CH_L]["l"]) + 30, "CH", RED, 20, "start", 3))

# ③ كسر الهيكل
s.append(f'<line x1="{x(LOW1)-slot*.8:.1f}" y1="{y(W[LOW1]["l"]):.1f}" '
         f'x2="{x(BOS_B)+slot*1.2:.1f}" y2="{y(W[LOW1]["l"]):.1f}" '
         f'stroke="{RED}" stroke-width="2"/>')
s.append(lab(x(BOS_B) + slot * 1.4, y(W[LOW1]["l"]) + 30, "BOS", RED, 20, "start", 3))

# ④ الفجوة
_gy = (W[IMB_I - 1]["h"] + W[IMB_I + 1]["l"]) / 2
s.append(f'<line x1="{x(IMB_I)-slot*.9:.1f}" y1="{y(W[IMB_I-1]["h"]):.1f}" '
         f'x2="{x(IMB_I)+slot*.9:.1f}" y2="{y(W[IMB_I-1]["h"]):.1f}" '
         f'stroke="{TXT}" stroke-width="1.4" stroke-opacity=".6"/>'
         f'<line x1="{x(IMB_I)-slot*.9:.1f}" y1="{y(W[IMB_I+1]["l"]):.1f}" '
         f'x2="{x(IMB_I)+slot*.9:.1f}" y2="{y(W[IMB_I+1]["l"]):.1f}" '
         f'stroke="{TXT}" stroke-width="1.4" stroke-opacity=".6"/>'
         f'<rect x="{x(IMB_I)-slot*.9:.1f}" y="{y(W[IMB_I+1]["l"]):.1f}" '
         f'width="{slot*1.8:.1f}" height="{y(W[IMB_I-1]["h"])-y(W[IMB_I+1]["l"]):.1f}" '
         f'fill="{TXT}" fill-opacity=".10"/>')
s.append(f'<line x1="{x(IMB_I)-slot*1.0:.1f}" y1="{y(_gy):.1f}" '
         f'x2="{x(IMB_I)-slot*3.4:.1f}" y2="{y(_gy):.1f}" stroke="{TXT}" '
         f'stroke-width="1.2" stroke-opacity=".55"/>')
s.append(lab(x(IMB_I) - slot * 3.8, y(_gy) + 6, "IMB", TXT, 19, "end", 3))

# ⑤ الهدف — السيولة السفلى
s.append(f'<line x1="{gl}" y1="{y(W[END]["l"]):.1f}" x2="{GW-gr:.1f}" '
         f'y2="{y(W[END]["l"]):.1f}" stroke="{CYAN}" stroke-width="2"/>')
s.append(lab(gl + 12, y(W[END]["l"]) + 34, "TARGET", CYAN, 20, "start", 3.2))
s.append(lab(x(END) + slot * 1.6, y(W[END]["l"]) - 14, "$", CYAN, 26, "middle", 0))
s.append('</svg>')
CHART = "".join(s)

html = f'''<!DOCTYPE html><html lang="ar" dir="rtl"><head><meta charset="UTF-8">
<title>نموذج الدخول البيعي — Liquidity State</title>
<meta name="hz:slide-selector" content=".slide">
<meta name="hz:canvas-width" content="1080"><meta name="hz:canvas-height" content="1350">
<style>{FONT_CSS}
*{{margin:0;padding:0;box-sizing:border-box}}
.slide{{width:1080px;height:1350px;position:relative;overflow:hidden;font-family:Tajawal;
  background:radial-gradient(120% 90% at 50% 0%, {BG0} 0%, {BG1} 55%, {BG2} 100%)}}
.hd{{position:absolute;top:86px;left:0;right:0;text-align:center}}
.h1{{font-size:82px;font-weight:900;letter-spacing:6px;color:{RED};line-height:1;
  filter:drop-shadow(0 0 26px rgba(224,86,86,.32))}}
.h2{{margin-top:12px;font-size:56px;font-weight:900;letter-spacing:14px;line-height:1;
  background:linear-gradient(180deg,#ffffff 0%,#C4D4DB 55%,#7F97A1 100%);
  -webkit-background-clip:text;background-clip:text;color:transparent;
  filter:drop-shadow(0 0 18px rgba(67,212,220,.20))}}
.h3{{margin-top:26px;font-size:29px;font-weight:700;color:{SUB}}}
.gr{{position:absolute;top:316px;left:40px;width:1000px}}
.gr svg{{width:100%;height:auto;display:block}}
.ft{{position:absolute;bottom:56px;left:0;right:0;display:flex;align-items:center;
  justify-content:center;gap:16px;direction:ltr}}
.ft .gm{{width:42px}} .ft .gm svg{{width:42px;height:auto;
  filter:drop-shadow(0 0 16px rgba(67,212,220,.34))}}
.ft .hn{{font-size:27px;font-weight:800;color:{SUB};letter-spacing:.5px}}
.edu{{position:absolute;bottom:22px;left:0;right:0;text-align:center;
  font-size:19px;font-weight:600;color:{MUTE}}}
</style></head><body>
<div class="slide" data-canvas-width="1080" data-canvas-height="1350">
  <div class="hd">
    <div class="h1">BEARISH</div>
    <div class="h2">ENTRY</div>
    <div class="h3">نموذج الدخول البيعي</div>
  </div>
  <div class="gr">{CHART}</div>
  <div class="ft"><div class="gm">{GEM}</div>
    <div class="hn" dir="ltr">@liquidity.state</div></div>
  <div class="edu">مثال تخطيطي لغرض تعليمي — مو توصية</div>
</div>
</body></html>'''

if __name__ == "__main__":
    with open(os.path.join(HERE, "bear50.html"), "w", encoding="utf-8") as f:
        f.write(html)
    print(f'نموذج الدخول البيعي · شموع {N} · بذرة {SEED}\n'
          f'  السيولة العليا: قمّة {PRE} كُنست عند {TOP}\n'
          f'  تغيّر الطابع: قاع {CH_L} كُسر عند {CH_B}\n'
          f'  منطقة الدخول: ارتداد إلى قمّة {RET}\n'
          f'  كسر الهيكل: قاع {LOW1} كُسر عند {BOS_B}\n'
          f'  الفجوة عند {IMB_I} (اتساعها {IMB_G:.2f}) · الهدف عند {END}')
