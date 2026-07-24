# كاروسيل انستقرام — شمعة الـ Pin Bar (Liquidity State)

كاروسيل تعليمي من 7 صفحات بهوية @liquidity.state، يشرح إن شمعة الـ Pin Bar
نموذج انعكاس مبالغ فيه ونسبة نجاحها لا تتعدى 37%.

## المخرجات النهائية (`out/`) — 1080×1350 (4:5)
| # | الملف | الدور |
|---|---|---|
| 1 | `01-cover.png` | الغلاف / الهوك — «تبي تعرف الشمعة اللي تاخذ فلوسك؟» |
| 2 | `02-stakes.png` | المشكلة — ربح صغير مقابل خسارة كبيرة |
| 3 | `03-what.png` | التعريف — تشريح الـ Pin Bar (ذيل طويل + جسم صغير) |
| 4 | `04-trap.png` | الفخ — الباك تست والانحياز الإدراكي |
| 5 | `05-stat.png` | الحقيقة بالأرقام — 37% نسبة النجاح |
| 6 | `06-examples.png` | أمثلة فاشلة — قمة كاذبة وقاع كاذب (شارت بستايل البراند) |
| 7 | `07-cta.png` | CTA — احفظ الدرس + تابع البوست القادم |

الكابشن المقترح في `caption.txt`.

## الهوية المطبّقة
- الخلفية: تدرّج تيل غامق `#0E1E24 → #12262E` + خطوط كوكبية خفيفة.
- الشموع: أخضر تيل `#2ECC9A` (صاعد) / أحمر ناعم `#E15A5A` (هابط) — لا سكرين شوت بألوان غريبة.
- الخط: Tajawal (Black للعناوين، Regular للنص) مضمّن base64.
- اللوقو: أيقونة الجوهرة الفضية، صغيرة أسفل/أعلى كل صفحة.
- «لغرض تعليمي» على كل صفحة.

## إعادة الإنتاج
```bash
# 1) الخطوط (تُحمّل مرة واحدة إلى fonts/ ثم تُضمّن في fonts.css)
python3 - <<'PY'  # يبني fonts.css من ملفات fonts/*.ttf
import base64,pathlib
w={"Tajawal-Regular":400,"Tajawal-Medium":500,"Tajawal-Bold":700,"Tajawal-ExtraBold":800,"Tajawal-Black":900}
css=[f"@font-face{{font-family:'Tajawal';font-weight:{v};font-display:block;src:url(data:font/ttf;base64,{base64.b64encode(pathlib.Path(f'fonts/{k}.ttf').read_bytes()).decode()}) format('truetype')}}" for k,v in w.items()]
pathlib.Path("fonts.css").write_text("\n".join(css))
PY

# 2) الرندر إلى out/*.png ثم التصغير إلى 1080×1350
NODE_PATH=/opt/node22/lib/node_modules node render.js
python3 -c "from PIL import Image;import glob;[Image.open(f).resize((1080,1350),Image.LANCZOS).save(f) for f in glob.glob('out/*.png')]"
```

## الملفات
- `carousel.html` — الصفحات السبع (SVG للشموع/اللوقو، CSS للهوية).
- `render.js` — لقطات Playwright لكل صفحة بدقة 2x.
- `fonts/` — خطوط Tajawal، `fonts.css` — نسخة base64 مضمّنة.
