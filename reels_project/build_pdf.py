#!/usr/bin/env python3
# Build the "Liquidity" lead-magnet PDF (Arabic RTL, Liquidity State brand) as HTML.
import base64, pathlib

FDIR = pathlib.Path("fonts")
def b64(name):
    return base64.b64encode((FDIR / name).read_bytes()).decode()

FONTS_CSS = f"""
@font-face {{ font-family:'Tajawal'; font-weight:400; src:url(data:font/ttf;base64,{b64('Tajawal-Regular.ttf')}) format('truetype'); }}
@font-face {{ font-family:'Tajawal'; font-weight:500; src:url(data:font/ttf;base64,{b64('Tajawal-Medium.ttf')}) format('truetype'); }}
@font-face {{ font-family:'Tajawal'; font-weight:700; src:url(data:font/ttf;base64,{b64('Tajawal-Bold.ttf')}) format('truetype'); }}
@font-face {{ font-family:'Tajawal'; font-weight:800; src:url(data:font/ttf;base64,{b64('Tajawal-ExtraBold.ttf')}) format('truetype'); }}
@font-face {{ font-family:'Tajawal'; font-weight:900; src:url(data:font/ttf;base64,{b64('Tajawal-Black.ttf')}) format('truetype'); }}
"""

CSS = FONTS_CSS + """
* { margin:0; padding:0; box-sizing:border-box; -webkit-print-color-adjust:exact; print-color-adjust:exact; }
@page { size: A4 portrait; margin:0; }
html,body { font-family:'Tajawal',sans-serif; }
:root{
  --bg:#05080e; --bg2:#080d16; --teal:#4fd0e0; --red:#ff5b6a; --green:#39d98a;
  --tx:#e9f2f6; --mut:#8fa6b3; --line:rgba(79,208,224,.16);
}
.page{
  position:relative; width:210mm; height:297mm; overflow:hidden;
  background:
    radial-gradient(120% 60% at 50% -8%, rgba(19,52,66,.55), rgba(5,8,14,0) 60%),
    linear-gradient(180deg,#05080e,#070c15);
  color:var(--tx); padding:20mm 16mm 16mm; page-break-after:always;
}
.page:last-child{ page-break-after:auto; }
.grid-bg{ position:absolute; inset:0; opacity:.5;
  background-image:linear-gradient(rgba(79,208,224,.045) 1px,transparent 1px),linear-gradient(90deg,rgba(79,208,224,.045) 1px,transparent 1px);
  background-size:26px 26px;
  -webkit-mask-image:radial-gradient(80% 70% at 50% 30%,#000 25%,transparent 80%); }
.hdr{ position:absolute; top:11mm; left:16mm; right:16mm; display:flex; align-items:center; justify-content:space-between; }
.chip{ font-size:10.5pt; letter-spacing:4px; color:#cfe6ee; border:1px solid var(--line); padding:5px 16px; border-radius:5px; background:rgba(6,12,20,.4); }
.chip .d{ color:var(--teal); }
.pglabel{ font-size:10pt; color:var(--mut); letter-spacing:1px; }
.ftr{ position:absolute; bottom:10mm; left:16mm; right:16mm; display:flex; align-items:center; justify-content:space-between; font-size:9pt; color:var(--mut); border-top:1px solid var(--line); padding-top:6px; }
.ftr .pg{ color:var(--teal); font-weight:700; direction:ltr; unicode-bidi:isolate; }
.content{ position:relative; z-index:2; }

h2.sec{ font-size:27pt; font-weight:900; line-height:1.2; margin-bottom:5mm; }
h2.sec .ac{ color:var(--teal); }
.acc{ width:70px; height:5px; border-radius:3px; background:linear-gradient(90deg,var(--teal),rgba(79,208,224,0)); margin-bottom:7mm; }
p{ font-size:12.5pt; line-height:1.95; color:#d6e3ea; font-weight:500; margin-bottom:4mm; }
p .hl{ color:var(--teal); font-weight:800; }
p .rd{ color:var(--red); font-weight:800; }
p .gr{ color:var(--green); font-weight:800; }
.lead{ font-size:14pt; color:#eaf5f8; }
.card{ background:linear-gradient(180deg,rgba(12,20,30,.9),rgba(8,13,20,.7)); border:1px solid var(--line); border-radius:14px; padding:6mm 7mm; margin-bottom:5mm; }
.card h3{ font-size:15pt; font-weight:800; color:#f2fbfd; margin-bottom:2mm; }
.card p{ font-size:11.5pt; margin-bottom:0; color:#c7d6de; }
.num-row{ display:flex; gap:6mm; align-items:flex-start; margin-bottom:5mm; }
.num{ flex:0 0 auto; width:16mm; height:16mm; border-radius:12px; border:2px solid var(--teal); background:radial-gradient(circle at 30% 25%,rgba(79,208,224,.3),rgba(8,20,28,.9)); color:#eafcff; font-size:20pt; font-weight:900; display:flex; align-items:center; justify-content:center; box-shadow:0 0 16px rgba(79,208,224,.25); }
.num.rd{ border-color:var(--red); color:#ffd7db; box-shadow:0 0 16px rgba(255,91,106,.25); }
.num-row .tx h3{ font-size:15.5pt; font-weight:800; color:#f2fbfd; margin-bottom:1mm; }
.num-row .tx p{ font-size:11.5pt; margin-bottom:0; }
.callout{ border-radius:14px; padding:6mm 7mm; margin-top:4mm; }
.callout.teal{ background:rgba(79,208,224,.08); border:1px solid rgba(79,208,224,.4); }
.callout.red{ background:rgba(255,91,106,.07); border:1px solid rgba(255,91,106,.35); }
.callout b{ color:var(--teal); }
.callout.red b{ color:var(--red); }
.chk{ display:flex; gap:5mm; align-items:center; padding:4mm 5mm; background:rgba(10,18,28,.7); border:1px solid var(--line); border-radius:12px; margin-bottom:3.5mm; }
.chk .bx{ flex:0 0 auto; width:9mm; height:9mm; border-radius:6px; border:2px solid var(--teal); display:flex; align-items:center; justify-content:center; }
.chk .bx svg{ width:6mm; height:6mm; }
.chk .t{ font-size:12.5pt; font-weight:700; color:#e9f2f6; }
.chk .t span{ color:var(--mut); font-weight:500; font-size:11pt; }
</style>
"""

def hdr(label):
    return f'<div class="hdr"><div class="chip">LIQUIDITY<span class="d">&nbsp;•&nbsp;</span>STATE</div><div class="pglabel">{label}</div></div>'

def ftr(pg):
    return f'<div class="ftr"><div>دليل السيولة — كيف تقرأ ما خلف الشارت</div><div class="pg">{pg} / 8</div></div>'

def check_svg():
    return '<svg viewBox="0 0 24 24" fill="none"><path d="M5 12.5 L10 17.5 L19 6.5" stroke="#4fd0e0" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/></svg>'

# ---- diagrams (inline SVG) ----
def diag_sweep():
    # downtrend -> sweep -> rally, with stop line
    bars=[358,356,352,354,349,346,348,343,340,342,338,336,334,339,345,352,360,366]
    sweep=12; pmin=330;pmax=369; W=470;H=180; x0=8; cw=16; gap=8
    def y(p): return 12+((pmax-p)/(pmax-pmin))*(H-24)
    s=f'<svg viewBox="0 0 {W} {H}" style="width:100%">'
    sy=y(333)
    s+=f'<line x1="0" y1="{sy:.0f}" x2="{W}" y2="{sy:.0f}" stroke="#ff5b6a" stroke-width="1.6" stroke-dasharray="7 6"/>'
    s+=f'<rect x="0" y="{sy:.0f}" width="{W}" height="{H-sy:.0f}" fill="#ff5b6a" opacity="0.06"/>'
    for i,c in enumerate(bars):
        o=bars[i-1] if i>0 else c+2
        x=x0+i*(cw+gap); up=c>=o
        col= '#ff5b6a' if i==sweep else ('#39d98a' if up else '#9fb0ba')
        top=y(max(o,c)); bot=y(min(o,c)); lo=y(min(o,c)-2 if i!=sweep else 331); hi=y(max(o,c)+2)
        s+=f'<line x1="{x+cw/2:.0f}" y1="{hi:.0f}" x2="{x+cw/2:.0f}" y2="{lo:.0f}" stroke="{col}" stroke-width="1.6"/>'
        s+=f'<rect x="{x:.0f}" y="{top:.0f}" width="{cw}" height="{max(2,bot-top):.0f}" rx="2" fill="{col}"/>'
    s+=f'<text x="{x0+sweep*(cw+gap)+cw/2:.0f}" y="{sy+16:.0f}" text-anchor="middle" font-family="Tajawal" font-size="11" font-weight="700" fill="#ff8c95" direction="rtl">الستوبات</text>'
    s+='</svg>'
    return s

def diag_wall():
    return '''<svg viewBox="0 0 470 180" style="width:100%">
    <defs><linearGradient id="rg" x1="0" x2="1"><stop offset="0" stop-color="#ff5b6a" stop-opacity="0"/><stop offset="1" stop-color="#ff5b6a" stop-opacity=".8"/></linearGradient></defs>
    <rect x="225" y="16" width="26" height="150" rx="3" fill="#5b6a72"/>
    <rect x="225" y="16" width="26" height="150" rx="3" fill="url(#rg)" opacity=".25"/>
    ''' + ''.join(f'<g><line x1="20" y1="{35+i*24}" x2="205" y2="{35+i*24}" stroke="url(#rg)" stroke-width="6"/><polygon points="205,{28+i*24} 222,{35+i*24} 205,{42+i*24}" fill="#ff5b6a"/></g>' for i in range(6)) + ''.join(f'<rect x="{258+ (i%4)*11}" y="{30+i*8}" width="8" height="8" rx="1" fill="#4fd0e0" opacity="{.3+.5*((i*37%10)/10):.2f}"/>' for i in range(14)) + '''
    <text x="115" y="176" text-anchor="middle" font-family="Tajawal" font-size="12" font-weight="700" fill="#ff8c95">بيع عدواني</text>
    <text x="360" y="176" text-anchor="middle" font-family="Tajawal" font-size="12" font-weight="700" fill="#4fd0e0">مشتري يمتص</text>
    </svg>'''

def diag_foot():
    rows=[(2340,45,62,0),(2339,51,121,0),(2338,60,211,0),(2337,72,356,1),(2336,85,489,1),(2335,96,631,1),(2334,168,604,1)]
    mx=631; W=470; rh=22
    s=f'<svg viewBox="0 0 {W} {len(rows)*rh+6}" style="width:100%" font-family="Tajawal">'
    for i,(p,b,se,z) in enumerate(rows):
        y=i*rh+3; cy=y+rh/2; cx=W/2
        sw=(se/mx)*(cx-70); bw=(b/mx)*(cx-70)
        op= .85 if z else .4
        s+=f'<rect x="{cx-58-sw:.0f}" y="{y+3:.0f}" width="{sw:.0f}" height="{rh-6}" rx="2" fill="#ff5b6a" opacity="{op}"/>'
        s+=f'<text x="{cx-62:.0f}" y="{cy+4:.0f}" text-anchor="end" font-size="11" font-weight="{800 if z else 600}" fill="{"#ff9aa4" if z else "#e0989e"}">{se}</text>'
        s+=f'<rect x="{cx-48:.0f}" y="{y+2:.0f}" width="96" height="{rh-4}" rx="4" fill="rgba(10,18,28,.85)" stroke="rgba(120,150,170,.25)"/>'
        s+=f'<text x="{cx:.0f}" y="{cy+4:.0f}" text-anchor="middle" font-size="11" font-weight="700" fill="#dfe9ee">{p}</text>'
        s+=f'<rect x="{cx+58:.0f}" y="{y+3:.0f}" width="{bw:.0f}" height="{rh-6}" rx="2" fill="#39d98a" opacity=".5"/>'
        s+=f'<text x="{cx+62:.0f}" y="{cy+4:.0f}" text-anchor="start" font-size="11" font-weight="600" fill="#9be6b0">{b}</text>'
    s+=f'<rect x="1" y="{3*rh+2:.0f}" width="{W-2}" height="{4*rh:.0f}" rx="7" fill="none" stroke="#ff5b6a" stroke-opacity=".55" stroke-width="1.6"/>'
    s+='</svg>'
    return s

# ---------- PAGES ----------
pages=[]

# 1 COVER
pages.append(f'''
<div class="page">
  <div class="grid-bg"></div>
  <div class="content" style="height:100%; display:flex; flex-direction:column;">
    <div style="display:flex; justify-content:center; margin-top:6mm;">
      <div class="chip" style="font-size:11pt;">LIQUIDITY<span class="d">&nbsp;•&nbsp;</span>STATE</div>
    </div>
    <div style="flex:1; display:flex; flex-direction:column; justify-content:center; text-align:center;">
      <div style="font-size:13pt; color:var(--teal); font-weight:800; letter-spacing:2px; margin-bottom:6mm;">دليل مجاني</div>
      <div style="font-size:52pt; font-weight:900; line-height:1.12;">السيولة</div>
      <div style="font-size:24pt; font-weight:800; color:#cfe6ee; margin-top:3mm;">كيف تقرأ ما يحدث <span style="color:var(--teal)">خلف الشارت</span></div>
      <div style="max-width:150mm; margin:8mm auto 0; font-size:13.5pt; color:var(--mut); line-height:1.9;">
        الستوب هنت، الامتصاص، وقراءة الفوت برنت لحظة كسر السيولة — بأسلوب عملي مبسّط.
      </div>
      <div style="margin:10mm auto 0; width:80%;">{diag_sweep()}</div>
    </div>
    <div style="text-align:center; color:var(--mut); font-size:10pt; letter-spacing:2px;">© LIQUIDITY STATE — للأغراض التعليمية فقط</div>
  </div>
</div>''')

# 2 INTRO — market business model
pages.append(f'''
<div class="page">{hdr('مقدمة')}<div class="grid-bg"></div>
  <div class="content">
    <h2 class="sec">ما كان <span class="ac">حظ سيء</span></h2><div class="acc"></div>
    <p class="lead">أغلب الخسائر ما تجي لأنك غلطان في الاتجاه… تجي لأنك دخلت في <span class="hl">المكان الواضح</span> اللي يعرفه الجميع — وتحته بالضبط تتجمّع الستوبات.</p>
    <p>السوق يحتاج <span class="hl">سيولة</span> عشان تدخل الأوامر الكبيرة. وأكبر تجمّع سيولة يكون تحت القيعان الواضحة وفوق القمم الواضحة، لأن هناك يحط الجميع ستوباتهم. لما يُكسر القاع، تُنفَّذ آلاف أوامر البيع (ستوباتك)… وهذي بالضبط السيولة اللي كان ينتظرها المشتري الكبير.</p>
    <div class="callout red"><p><b>الخلاصة:</b> انضراب ستوبك مو صدفة — هو <b>نموذج عمل</b>. الفرق بينك وبين اللي يقرأ التدفق: إنه يشوف الامتصاص لحظة حدوثه، قبل ما ينفجر السعر.</p></div>
    <p style="margin-top:6mm;">في هذا الدليل رح تتعلّم كيف تفرّق بين <span class="rd">كسر حقيقي</span> و<span class="gr">سويب + امتصاص</span>، وكيف تقرأ الفوت برنت والدلتا لحظة الكسر، ومتى الأفضل تبتعد عن الشارت تماماً.</p>
  </div>{ftr(2)}</div>''')

# 3 Liquidity & Stop Hunt
pages.append(f'''
<div class="page">{hdr('السيولة والستوب هنت')}<div class="grid-bg"></div>
  <div class="content">
    <h2 class="sec">أين تجلس <span class="ac">السيولة</span>؟</h2><div class="acc"></div>
    <p>السيولة = أوامر معلّقة بكثافة. مكانها متوقّع:</p>
    <div class="card"><h3>تحت القيعان الواضحة</h3><p>ستوبات المشترين + أوامر بيع بريك آوت. وقود جاهز لأي حركة هابطة سريعة.</p></div>
    <div class="card"><h3>فوق القمم الواضحة</h3><p>ستوبات البائعين + أوامر شراء بريك آوت. وقود لأي دفعة صاعدة.</p></div>
    <p style="margin-top:4mm;">حركة «الستوب هنت» هي دفعة سريعة تكسر المستوى، <span class="rd">تحصد السيولة</span>، ثم ينعكس السعر. بالعين المجرّدة تبدو كسر… لكن التدفق يكشف الحقيقة.</p>
    <div style="margin:5mm auto 0; width:100%;">{diag_sweep()}</div>
    <div class="callout teal"><p><b>قاعدة:</b> لا يوجد كسر «نظيف» بلا حجم يؤكّده. كسر بلا حجم = فخ سيولة محتمل.</p></div>
  </div>{ftr(3)}</div>''')

# 4 Absorption
pages.append(f'''
<div class="page">{hdr('الامتصاص')}<div class="grid-bg"></div>
  <div class="content">
    <h2 class="sec">هذا هو <span class="ac">الامتصاص</span></h2><div class="acc"></div>
    <p class="lead">تخيّل واحد يدزّ جدار… يدزّ ويدزّ والجدار ما يتحرك. هذا بالضبط الامتصاص.</p>
    <p>أوامر بيع ضخمة تنزل على المستوى — الفوت برنت يوريك حجم البيع عالي جداً — <span class="rd">لكن السعر ما ينزل</span>. معناها فيه <span class="gr">مشتري كبير</span> واقف هناك، يستقبل كل البيع وما يتزحزح.</p>
    <div style="margin:4mm auto; width:100%;">{diag_wall()}</div>
    <div class="callout teal"><p><b>الفكرة المحورية:</b> الحجم العالي وحده لا يكفي. المهم <b>ردّة فعل السعر</b> على الحجم. حجم بيع ضخم + سعر ثابت = يد كبيرة تمتص. هذا <b>مو دعم عادي… هذا امتصاص</b>.</p></div>
  </div>{ftr(4)}</div>''')

# 5 Three signs
pages.append(f'''
<div class="page">{hdr('٣ علامات')}<div class="grid-bg"></div>
  <div class="content">
    <h2 class="sec">٣ علامات <span class="ac">تكشف الامتصاص</span></h2><div class="acc"></div>
    <div class="num-row"><div class="num">1</div><div class="tx"><h3>حجم عالٍ عند المستوى</h3><p>الفوت برنت يطبع حجم بيع ضخم عند نفس المنطقة — أضعاف الطبيعي.</p></div></div>
    <div class="num-row"><div class="num">2</div><div class="tx"><h3>دلتا سالبة قوية… والشمعة ما تكسر</h3><p>البائعون يضربون العرض بعنف (دلتا سالبة كبيرة)، ومع ذلك جسم الشمعة يرفض إغلاق تحت المستوى.</p></div></div>
    <div class="num-row"><div class="num">3</div><div class="tx"><h3>ذيل سفلي واضح + رفض للنزول</h3><p>الشمعة تُغلق بذيل طويل من الأسفل، والسعر يرفض الاستمرار هبوطاً — بصمة استقبال.</p></div></div>
    <div class="callout teal"><p><b>اقرأ السلوك… مو بس الاتجاه.</b> ثلاث علامات مجتمعة أقوى من أي واحدة لحالها.</p></div>
  </div>{ftr(5)}</div>''')

# 6 Reading footprint
pages.append(f'''
<div class="page">{hdr('قراءة الفوت برنت')}<div class="grid-bg"></div>
  <div class="content">
    <h2 class="sec">الفوت برنت <span class="ac">لحظة السويب</span></h2><div class="acc"></div>
    <p>كل صف = مستوى سعري، وفيه حجم <span class="rd">البيع (يمين الطلب)</span> و<span class="gr">الشراء (الطلب على العرض)</span>. عند منطقة الستوبات لاحظ الآتي:</p>
    <div style="margin:4mm auto; width:88%;">{diag_foot()}</div>
    <p>البيع ضخم في المنطقة المحدّدة (٣٥٦ ← ٦٣١)… لكن عند القاع تماماً يقفز الشراء (١٦٨) والسعر يثبت. الدلتا كانت سالبة بعنف، ثم تنقلب لصالح المشتري.</p>
    <div class="callout teal"><p><b>الترجمة:</b> «بيع ضخم يُمتَص عند المنطقة» — <b>الدلتا تنقلب = امتصاص واكتمال السويب</b>. هنا تبدأ الحركة الحقيقية.</p></div>
  </div>{ftr(6)}</div>''')

# 7 When to stay away
pages.append(f'''
<div class="page">{hdr('انضباط')}<div class="grid-bg"></div>
  <div class="content">
    <h2 class="sec">متى تبتعد <span class="ac">عن الشارت</span></h2><div class="acc"></div>
    <p>أفضل صفقة أحياناً هي اللي ما دخلتها. ابتعد فوراً إذا:</p>
    <div class="chk"><div class="bx">{check_svg()}</div><div class="t">بعد ٣ خسائر متتالية <span>— تنتقل من التحليل إلى الانتقام.</span></div></div>
    <div class="chk"><div class="bx">{check_svg()}</div><div class="t">دخلت لتعويض الخسارة <span>— هذا Revenge Trading مو فرصة.</span></div></div>
    <div class="chk"><div class="bx">{check_svg()}</div><div class="t">ما في Setup واضح <span>— غياب الوضوح = لا أفضلية الآن.</span></div></div>
    <div class="chk"><div class="bx">{check_svg()}</div><div class="t">تتداول من الملل <span>— الملل يصنع صفقات عشوائية.</span></div></div>
    <div class="chk"><div class="bx">{check_svg()}</div><div class="t">متعب أو مشتّت <span>— قلّة التركيز تقلّل جودة القرار.</span></div></div>
    <div class="chk"><div class="bx">{check_svg()}</div><div class="t">كسرت إدارة المخاطر <span>— أول كسر للقواعد إشارة توقّف، لا دخول.</span></div></div>
  </div>{ftr(7)}</div>''')

# 8 Entry checklist + CTA
pages.append(f'''
<div class="page">{hdr('خطة التنفيذ')}<div class="grid-bg"></div>
  <div class="content">
    <h2 class="sec">تشيك‑ليست <span class="ac">الدخول</span></h2><div class="acc"></div>
    <div class="num-row"><div class="num">1</div><div class="tx"><h3>السويب</h3><p>كسر السيولة أسفل القاع (أو فوق القمة) وحصاد الستوبات.</p></div></div>
    <div class="num-row"><div class="num">2</div><div class="tx"><h3>تأكيد الفوت برنت</h3><p>حجم بيع ضخم يُمتَص + دلتا تنقلب لصالح الاتجاه المعاكس.</p></div></div>
    <div class="num-row"><div class="num">3</div><div class="tx"><h3>الدخول ضد السويب</h3><p>مع أول انعكاس مؤكَّد. الستوب خلف ذيل السويب مباشرة، والهدف السيولة المقابلة.</p></div></div>
    <div class="callout teal" style="margin-top:6mm;"><p style="font-size:14pt;"><b>الصفقة الناجحة لا تبدأ بالدخول… تبدأ بالانتظار.</b></p></div>
    <div style="margin-top:auto; text-align:center; padding-top:14mm;">
      <div style="font-size:15pt; color:#cfe6ee; font-weight:700;">تابع للمزيد</div>
      <div style="display:inline-flex; align-items:center; gap:12px; margin-top:5mm; padding:14px 34px; border:2px solid var(--teal); border-radius:100px; background:rgba(8,14,22,.9);">
        <span style="font-size:16pt; font-weight:900; letter-spacing:6px; color:#eafaff;">LIQUIDITY&nbsp;STATE</span>
      </div>
    </div>
  </div>{ftr(8)}</div>''')

HTML = f'<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8"><style>{CSS}</head><body>{"".join(pages)}</body></html>'
pathlib.Path("pdf_build/liquidity.html").write_text(HTML, encoding="utf-8")
print("wrote pdf_build/liquidity.html", len(HTML), "bytes")
