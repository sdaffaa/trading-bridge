# Liquidity State — Carousel Machine 🟢 (Light Edition)

آلة إنتاج كاروسيلات إنستقرام لحساب **@liquidity.state**.
كل كاروسيل = تعبئة نص + شارت في القوالب → رندر PNG بمقاس **1080×1350** → بوابة QA → تسليم.
هذا **ليس** تصميم بوست واحد — هو قالب واحد يُعاد استخدامه لكل كاروسيل قادم (master prompt §14).

النظام **فاتح** (Light Edition). الخلفيات الداكنة ممنوعة هنا (§7). الرموز البصرية في `src/brand.css`.

## شجرة المشروع
```
carousel-machine/
├── content/   brief.md · copy.json        # النص المعتمد لكل كاروسيل
├── data/      chart.csv · sources.md       # بيانات حقيقية + مصادر كل رقم
├── src/       slide-01..07.html · brand.css · fonts.css
├── scripts/   build-fonts.py · render.js · qa.js
├── assets/    fonts/Tajawal-*.ttf
├── out/       01-cover.png … 07-cta.png · caption.txt · qa-report.md
└── content-registry.md                     # سجل منع التكرار (§11)
```

## المتطلبات
- **Node ≥ 18** و **Python 3**.
- **Playwright + Chromium**: توفّرهم البيئة عالمياً. `render.js` يحلّهم تلقائياً
  (محلي أولاً، ثم global fallback على `/opt/node22/lib/node_modules`). لا تشغّل
  `playwright install` — Chromium مثبّت مسبقاً في `PLAYWRIGHT_BROWSERS_PATH`.
- لو شغّلت خارج هذي البيئة: `npm i -D playwright && npx playwright install chromium`.

## خط الإنتاج
```bash
# 1) (مرة واحدة) ابنِ الخط Base64 من الـ TTFs — الخط مضمّن حتى لا يعلّق المتصفح المخفي
python3 scripts/build-fonts.py            # -> src/fonts.css

# 2) رندر كل السلايدات إلى PNG (2x ثم تصغير إلى 1080×1350)
node scripts/render.js                     # كل src/slide-*.html
node scripts/render.js src/slide-05.html   # سلايد واحد

# 3) بوابة الجودة الآلية (تكتب out/qa-report.md)
node scripts/qa.js

# مختصر: رندر + QA
npm run build
```

## صنع كاروسيل جديد (الدورة الافتراضية)
`Brief → موافقة فهد → Copy → موافقة فهد → Design → Render → QA → تسليم`

1. عبّي `content/brief.md` بجدول الإدخال (§2) واعرضه على فهد. **الموضوع من فهد، لا تخترع.**
2. اكتب النص في `content/copy.json` بصوت فهد (skill: `fahad-script-voice`).
3. طابق `content-registry.md` — لو الموضوع/الهوك مكرر، **اسأل فهد** (§11/§12).
4. عدّل نص السلايدات في `src/slide-01..07.html` (ثوابت الهوية في `brand.css`).
5. للشارت الحقيقي: صدّر OHLC إلى `data/chart.csv` وارسمه، **وأزل وسم «توضيحي»**.
   المخططات المرسومة يدوياً تبقى موسومة `توضيحي` (§7.5).
6. سجّل مصدر كل رقم في `data/sources.md`. **صفر أرقام مخترعة** (§4).
7. `node scripts/render.js && node scripts/qa.js`.
8. **الفحص البصري الإلزامي**: افتح كل PNG وتأكد — العربي متصل؟ الأرقام غير معكوسة؟
   ما في نص مقصوص؟ الهوامش مطبّقة؟ (هذا لا يُؤتمت — §8.5).

## قواعد بصرية مثبّتة في القالب
- مقاس **1080×1350**، هوامش آمنة **90px**، آخر **120px** فاضية من النص (واجهة إنستقرام).
- الأرقام **لاتينية** (`$100`, `2R`, `−9.6%`) — §7.3. الترقيم الإطاري فقط عربي-هندي (`١٢٣`).
- كل رقم/معادلة داخل نص عربي يُلفّ بـ `class="num"` (LTR isolate) حتى لا ينعكس (bidi).
- تباين ≥ 4.5:1 لكل نص (يُفحص في `qa.js`).
- شعار الجوهرة + الشريط السفلي + عدّاد `٣/٧` بنفس الموضع في كل سلايد.

## ماذا يفحص qa.js آلياً (§9)
سبع سلايدات · سقف الكلمات لكل سلايد · سطر المخاطر على سلايد الصفقة · اللوحة فاتحة ·
تباين الألوان ≥ 4.5:1 · أبعاد كل PNG = 1080×1350.
> يبقى **الفحص البصري** يدوياً — `qa.js` لا يدّعي نجاح الجزء البصري أبداً.

## القالب الحالي (عرض)
سلايدات `src/` معبّأة بعرض من محور `RISK` (حجم الصفقة الثابت) — أرقامه محسوبة ذاتياً
وموثّقة في `data/sources.md` — لتأكيد خط الإنتاج فقط. استبدل النص/الشارت لكل كاروسيل حقيقي.
