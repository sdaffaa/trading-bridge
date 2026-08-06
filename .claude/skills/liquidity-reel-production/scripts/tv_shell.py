# -*- coding: utf-8 -*-
"""واجهة المنصّة — الشكل الذي يجعل الريل تسجيلَ جلسة لا ريلاً.

🔒 أمر فهد 2026-08-06: «اريد الجارت وكأني داخل تريدنق فيو وأقوم بماركب،
   وليس كريلز». والقرار في الجلسة نفسها: **تخطيط تريدنق فيو بألوان الهوية**
   (كريمي/تركوازي) لا الغامق ولا الأبيض.

كانت هذه الواجهة محبوسة في `run32_desk` وحده. هنا تُنتزع كي تخدم ريلات
الجارت كلها، ويبقى في كل ريل ما يخصّه (تذكرة الأمر · لوحة الباك تست).

القاعدة التي تحكم الملف — من مهارة `tradingview-platform-pov`:
**لا تُرسم أداةٌ قبل أن تُنقَر**، ولا يطفو على الشاشة عنصرٌ لا يحتويه
تسجيل شاشة حقيقي. فـ`click_tool` تُرجع نقرة المؤشر وتوهّج الزرّ معاً حتى
لا يُنسى أحدهما، والنصوص تُكتب `note_el` كملاحظات على الجارت لا كعناوين
فوقه.

    التخطيط الموحّد داخل إطار 1080×1920:
      شريط علوي   0 → 96
      صفّ فريمات  96 → 160
      الجارت      160 → 1660   (996×1500 عند x=84)
      شريط سفلي   1660 → 1730
"""
from reel_build import INK, TEAL_D, htext

# ═══ التخطيط ═══
FRAME_W, FRAME_H = 1080, 1920
CX, CY = 84, 160                    # ركن الجارت في إحداثيات #stage
BAR_H, TFROW_H = 96, 64
FOOT_TOP = 1660

TOOLS = ["سهم", "خط", "أفقي", "مربع", "صفقة", "نص"]
TOOL_X = 42
TOOL_TOP = [320, 412, 504, 596, 688, 780]
TOOL_H = 76
# فهارس الأدوات بأسمائها — كي يقرأ النداء نفسه لا رقماً مبهماً
ARROW, TREND, HLINE, RECT, TRADE, TEXT = range(6)

TF_AR = {"3m": "٣د", "5m": "٥د", "15m": "١٥د", "30m": "٣٠د", "1h": "١س", "4H": "٤س", "1D": "يومي"}
TF_ORDER = ["5m", "15m", "30m", "1h", "4H", "1D"]


def tool_xy(i):
    """مركز زرّ الأداة في إحداثيات الإطار — مقصد المؤشر."""
    return TOOL_X, TOOL_TOP[i] + TOOL_H // 2


def tf_xy(tf, tfs=None):
    """مركز شريحة الفريم في صفّ الفريمات — تبديل الإطار يبدأ بنقرها."""
    tfs = tfs or TF_ORDER
    i = tfs.index(tf) if tf in tfs else 0
    # الصفّ يبدأ من اليمين (rtl): أول شريحة عند الحافة اليمنى
    return FRAME_W - 26 - 46 - i * 104, BAR_H + TFROW_H // 2


# ═══ HTML ═══
def shell_html(sym, tf_on, clock="--:--", tfs=None, foot=""):
    """الشريط العلوي وصفّ الفريمات وعمود الأدوات والشريط السفلي."""
    tfs = tfs or TF_ORDER
    # حالة «الفريم المختار» عنصرٌ مستقلّ لا صنف CSS: `dom_marks` تحرّك
    # الشفافية ولا تبدّل الأصناف، فالتبديل يقع بإظهار قرص وإخفاء آخر.
    on = 'style="opacity:1"'
    chips = "".join(
        f'<span class="tf" id="tfc{i}">'
        f'<span class="tfon" id="tfo{i}" {on if k == tf_on else ""}></span>'
        # قرص ثانٍ احتياطي: الفريم التنفيذي يُضاء مرّتين (قبل جولة الفريمات
        # وبعد العودة منها)، و`dom_marks` لا تحتمل معرّفاً مكرّراً.
        f'<span class="tfon" id="tfq{i}"></span>'
        f'<span class="tfl">{TF_AR.get(k, k)}</span></span>'
        for i, k in enumerate(tfs))
    tools = "".join(
        f'<div class="tb" style="top:{TOOL_TOP[i]}px" id="tb{i}">'
        f'<span class="tglow" id="tg{i}"></span><span class="tl">{t}</span></div>'
        for i, t in enumerate(TOOLS))
    return (f'<div id="topbar"><span class="sym">{sym}</span>'
            f'<span class="dot"></span><span class="mk">السوق مفتوح</span>'
            f'<span class="cd" id="cdown">{clock}</span></div>'
            f'<div id="tfrow">{chips}</div>'
            f'<div id="tools">{tools}</div>'
            f'<div id="foot"><span class="fl">{foot}</span>'
            f'<span class="fr" id="fclock">—</span></div>')


SHELL_CSS = f"""
#topbar{{position:absolute;top:0;left:0;right:0;height:{BAR_H}px;display:flex;align-items:center;
  gap:16px;padding:0 26px;background:#FBF9F5;border-bottom:1.5px solid rgba(15,46,60,.14);z-index:8}}
#topbar .sym{{font-size:32px;font-weight:900;color:{INK};direction:ltr}}
#topbar .dot{{width:11px;height:11px;border-radius:50%;background:#3FA96A}}
#topbar .mk{{font-size:22px;font-weight:700;color:#6B7C84}}
#topbar .cd{{margin-right:auto;font-size:27px;font-weight:800;color:{TEAL_D};direction:ltr;
  background:rgba(46,125,150,.10);padding:5px 14px;border:1.4px solid rgba(30,98,122,.30)}}
#tfrow{{position:absolute;top:{BAR_H}px;left:0;right:0;height:{TFROW_H}px;display:flex;
  align-items:center;gap:10px;padding:0 26px;background:#FBF9F5;
  border-bottom:1.5px solid rgba(15,46,60,.10);z-index:8}}
#tfrow .tf{{position:relative;font-size:23px;font-weight:800;color:#8C9BA2;padding:5px 15px;
  min-width:46px;text-align:center}}
#tfrow .tfon{{position:absolute;inset:0;opacity:0;background:rgba(46,125,150,.12);
  border:1.4px solid rgba(30,98,122,.34)}}
#tfrow .tfl{{position:relative;z-index:2}}
#tools{{position:absolute;top:0;left:0;width:{CX}px;height:{FRAME_H}px;z-index:9}}
.tb{{position:absolute;left:10px;width:64px;height:{TOOL_H}px;
  border:1.4px solid rgba(15,46,60,.16);background:#FBF9F5;display:flex;align-items:center;
  justify-content:center;overflow:hidden}}
.tb .tl{{font-size:19px;font-weight:800;color:#6B7C84;position:relative;z-index:2}}
.tglow{{position:absolute;inset:0;background:rgba(46,125,150,.30);opacity:0}}
#chartclip{{top:{CY}px;left:{CX}px}}
#chip{{display:none}} #res{{display:none}} #endlogo{{display:none}}
"""

# شريط الحالة السفلي وإخفاء العنوان العائم — يخصّان ريلات التحليل التي
# تملأ فيها المنصّة الإطار كلّه. ريل الجلسة يبقي بيتاته تحت اللوحة.
FOOT_CSS = f"""
#foot{{position:absolute;top:{FOOT_TOP}px;left:0;right:0;height:70px;display:flex;
  align-items:center;justify-content:space-between;padding:0 30px;background:#FBF9F5;
  border-top:1.5px solid rgba(15,46,60,.12);z-index:8}}
#foot .fl{{font-size:21px;font-weight:700;color:#6B7C84}}
#foot .fr{{font-size:22px;font-weight:800;color:#8C9BA2;direction:ltr}}
.hl{{display:none}}
"""

# ملاحظة على الجارت — بديل العنوان العائم. الصندوق بخلفية اللوحة وحدٍّ
# رفيع كأنه كائن نصّ في المنصّة، وخيطٌ رابط إلى ما يصفه فلا يتيه الوسم عن
# موضوعه. تُحرَّك بوسم `pop` كبقية الماركب.
NOTE_CSS = """
.nt{position:absolute;z-index:7;opacity:0;background:rgba(251,249,245,.96);
  border:1.5px solid rgba(30,98,122,.34);border-right:4px solid #1E627A;
  padding:12px 18px 13px;max-width:640px;box-shadow:0 6px 20px rgba(15,46,60,.10)}
.nt b{display:block;font-size:30px;font-weight:900;color:#0F2E3C;line-height:1.2}
.nt span{display:block;margin-top:5px;font-size:25px;font-weight:600;color:#5C6C73;line-height:1.35}
.ntl{position:absolute;z-index:6;opacity:0;background:rgba(30,98,122,.42)}
/* مؤشّر الكتابة: خطٌّ رفيع على حافة النصّ يومض ما دامت الأداة تكتب */
.nt.typing::after{content:"";position:absolute;left:14px;bottom:14px;width:3px;height:30px;
  background:#1E627A;animation:cbl .5s steps(1) infinite}
@keyframes cbl{0%,49%{opacity:1}50%,100%{opacity:0}}
"""


def note_el(nid, x, y, title, detail="", anchor=None, w=None, xr=None):
    """ملاحظة نصّية عند (x,y) بإحداثيات الإطار، مع خيط اختياري إلى مرساتها.

    `anchor=(ax, ay)` نقطة على الجارت يصلها خيطٌ رفيع — تُستعمل حين تبعد
    الملاحظة عمّا تصفه. والحجم ≥25px شرطُ قراءتها على الجوال."""
    lead = ""
    if anchor:
        ax, ay = anchor
        top, hgt = (min(y, ay), abs(ay - y))
        lead = (f'<div class="ntl" id="{nid}l" style="left:{ax:.0f}px;top:{top:.0f}px;'
                f'width:2px;height:{hgt:.0f}px"></div>')
    ww = f"width:{w}px;" if w else ""
    # الارتساء بالحافة اليمنى خيار: العربية تُقرأ من اليمين، وركن اللوحة
    # الأيمن العلوي هو الفراغ الوحيد المضمون في كل الفريمات (يسارُه شريحة
    # تعريف اللوحة، وأسفلُه الشموع والوسوم).
    pos = f"right:{FRAME_W - xr:.0f}px;" if xr is not None else f"left:{x:.0f}px;"
    sub = f'<span>{detail}</span>' if detail else ""
    return (f'{lead}<div class="nt" id="{nid}" style="{pos}top:{y:.0f}px;{ww}">'
            f'<b>{title}</b>{sub}</div>')


# ═══ تفاعل المؤشر ═══
def click_tool(i, t, approach=0.42, hold=0.22, until=None):
    """(كيفريمات المؤشر، وسم توهّج الزرّ) لنقرة أداة تقع عند اللحظة t.

    التردّد قبل النقر مقصود: المهارة تنصّ أن الإنسان يبطئ ليصوّب
    (١٥٠–٣٠٠م.ث)، والواجهة وحدها هي الفورية. فالمؤشر يصل عند
    `t - hold` ثم يسكن حتى ينقر."""
    x, y = tool_xy(i)
    cur = [[round(t - approach - hold, 2), x, y, "ramp"],
           [round(t - hold, 2), x, y, "ss"],
           [round(t, 2), x, y, "ss", "down"]]
    # الأداة تبقى مضاءة ما دامت مستعملة — في المنصّة لا ينطفئ التحديد
    # بمجرّد النقر بل حين تُترك الأداة.
    dom = [f"tg{i}", round(t, 2), round(t + 0.18, 2), round(until or t + 0.5, 2), 0.25]
    return cur, dom


def click_tf(tf, t, tfs=None, approach=0.40, hold=0.20):
    """نقرة شريحة فريم — تبديل الإطار يبدأ بها لا يقع تلقائياً."""
    tfs = tfs or TF_ORDER
    x, y = tf_xy(tf, tfs)
    i = tfs.index(tf) if tf in tfs else 0
    cur = [[round(t - approach - hold, 2), x, y, "ramp"],
           [round(t - hold, 2), x, y, "ss"],
           [round(t, 2), x, y, "ss", "down"]]
    dom = [f"tfo{i}", round(t, 2), round(t + 0.16, 2), 0, 0]
    return cur, dom


def draw_path(t0, t1, x0, y0, x1, y1, bow=0.0):
    """كيفريمات رسم مستقيم: البداية بتيسير الوصول ثم سحبٌ خطّي.

    التيسير الخطّي `lin` إلزامي على شقّ السحب — الرسم خطّي في الزمن، فأي
    تنعيم يجعل رأس الخطّ يسبق المؤشر أو يتخلّف عنه (تعلّمناه في سحب الزون)."""
    return [[round(t0, 2), x0, y0, "ramp"], [round(t1, 2), x1, y1, "lin"]]
