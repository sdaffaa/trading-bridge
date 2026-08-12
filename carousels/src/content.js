// Liquidity State — batch content. 5 carousels × 6 pages. All charts = educational illustrations.
export const HANDLE = '@liquidity.state';

export const carousels = [
// ══════════════════════════════════ 1 — FOOTPRINT: ABSORPTION (Lesson / Type A)
{
  idx:'01', slug:'absorption-footprint', type:'درس تعليمي',
  kw:'امتصاص', domains:'Footprint · Order Flow',
  title:'الامتصاص في الفوت برنت',
  hookAlts:[
    'حجم بيع ضخم… والسعر ما نزل. ليش؟',
    'الدلتا سالبة… بس السوق طالع. شنو صاير؟',
    'كل البائعين ضاربين… وما تحرك. وين راحوا؟'],
  sources:[
    'ATAS — Footprint & Delta documentation',
    'Sierra Chart — Numbers Bars / Order Flow docs',
    'Anna Coulling — A Complete Guide to Volume Price Analysis',
    'Wyckoff — Effort vs Result principle'],
  slides:[
    {kind:'cover', kicker:'FOOTPRINT · ORDER FLOW',
     hook:'حجم بيع ضخم…\nوالسعر ((ما نزل)).', subq:'الجهد كبير… والنتيجة صفر. هذا هو الامتصاص.',
     tag:'رسم توضيحي'},
    {kind:'content', eyebrow:'التعريف', chip:'Absorption',
     h1:'الامتصاص = جهد كبير بلا نتيجة',
     lead:'أوامر ليمت ضخمة تبتلع التنفيذ العدواني، فيبقى السعر ثابتًا رغم موجة البيع.',
     chart:{type:'candles', volume:[
       {v:30},{v:34},{v:40},{v:52},{v:70},{v:120,hl:1},{v:60},{v:48},{v:44}],
       candles:[
        {o:2418,h:2420,l:2412,c:2414},{o:2414,h:2416,l:2407,c:2409},{o:2409,h:2410,l:2401,c:2403},
        {o:2403,h:2405,l:2396,c:2398},{o:2398,h:2399,l:2388,c:2391},{o:2391,h:2393,l:2385,c:2390},
        {o:2390,h:2396,l:2389,c:2395},{o:2395,h:2401,l:2394,c:2400},{o:2400,h:2406,l:2399,c:2405}],
       levels:[{p:2387,label:'دعم / سيولة',color:'#0B2635'}],
       notes:[{i:5,p:2386,text:'حجم قياسي… ورفض النزول',tx:520,ty:150,anchor:'end'}]},
     illus:true},
    {kind:'content', eyebrow:'كيف يتكوّن؟',
     h1:'ثلاثة شروط لازمة',
     rows:[
       {i:'١',b:'جهد واضح',s:'دلتا أو حجم مرتفع بشكل غير اعتيادي.'},
       {i:'٢',b:'موقع منطقي',s:'عند مستوى مهم: دعم/مقاومة أو سيولة.'},
       {i:'٣',b:'نتيجة غائبة',s:'السعر يرفض التقدم في اتجاه الضغط.'}],
     note:'غياب أي شرط = ليس امتصاصًا، بل حركة عادية.'},
    {kind:'content', eyebrow:'مثال بالفوت برنت',
     h1:'بيع عدواني… ابتلعه المشتري',
     chart:{type:'footprint', cols:[
       {label:'قبل', delta:-280, cells:[
         {bid:80,ask:70},{bid:120,ask:60,imb:'bid'},{bid:150,ask:40,imb:'bid'},{bid:90,ask:30,imb:'bid'},{bid:60,ask:20}]},
       {label:'الامتصاص', delta:-310, cells:[
         {bid:50,ask:60},{bid:70,ask:80},{bid:90,ask:70},{bid:200,ask:60,imb:'bid',absorb:1},{bid:240,ask:70,imb:'bid',absorb:1}]},
       {label:'الاستجابة', delta:250, cells:[
         {bid:60,ask:140,imb:'ask'},{bid:50,ask:120,imb:'ask'},{bid:40,ask:90},{bid:30,ask:60},{bid:20,ask:40}]}]},
     lead:'دلتا سالبة قوية عند القاع (بيع مكثّف)، لكن السعر لم ينكسر — ثم استجابة شراء.',
     illusNum:true},
    {kind:'content', eyebrow:'أخطاء القراءة', chip:'Checklist',
     h1:'لا تقرأ الدلتا وحدها',
     checklist:[
       {t:'خطأ: دلتا سالبة = إشارة بيع مباشرة',bad:true},
       {t:'خطأ: تجاهل موقع الحدث على الشارت',bad:true},
       {t:'فحص: هل الجهد كبير فعلًا؟'},
       {t:'فحص: هل السعر رفض التقدم؟'},
       {t:'فحص: هل الموقع عند سيولة حقيقية؟'}]},
    {kind:'cta', eyebrow:'خلاصة الدرس',
     h1:'الامتصاص يُقرأ بالجهد والنتيجة والموقع — لا بلون واحد.',
     keyword:'امتصاص',
     reasons:[
       {ic:'📌',t:'احفظه كتعريف مرجعي للفوت برنت.'},
       {ic:'📤',t:'أرسله لمن يقرأ الدلتا كإشارة مباركة.'}]},
  ]
},

// ══════════════════════════════════ 2 — ICT + VOLUME PROFILE: FVG DISCOUNT ENTRY (Entry / Type B)
{
  idx:'02', slug:'ict-fvg-discount-entry', type:'خطوات دخول صفقة',
  kw:'فجوة', domains:'ICT · Volume Profile',
  title:'دخول من فجوة FVG في الخصم',
  hookAlts:[
    'كل الفجوات مو فرص… وحدة بس تستاهل. أيها؟',
    'دخلت من الفجوة… وطلعت غلط. وين الشرط؟',
    'FVG في الخصم مع البروفايل… كيف تدخل صح؟'],
  sources:[
    'Inner Circle Trader — Liquidity, Displacement & Fair Value Gap concepts',
    'ICT — Premium/Discount (Equilibrium) & OTE',
    'TradingView — Volume Profile / Value Area (VAL, VAH, POC) documentation',
    'James Dalton — Mind Over Markets (Value Area concept)'],
  slides:[
    {kind:'cover', kicker:'ICT · VOLUME PROFILE',
     hook:'كل الفجوات مو فرص…\n((وحدة)) بس تستاهل.', subq:'الشرط مو الفجوة نفسها — الشرط وين تكوّنت.',
     tag:'لغرض تعليمي · رسم توضيحي'},
    {kind:'content', eyebrow:'الخطوة ١ — السياق',
     h1:'اتجاه صاعد يصحّح للخصم',
     lead:'الفريم الأكبر صاعد. ننتظر التصحيح إلى منطقة الخصم (تحت خط التوازن 50%).',
     chart:{type:'candles',
       candles:[
        {o:2362,h:2368,l:2360,c:2366},{o:2366,h:2376,l:2364,c:2374},{o:2374,h:2386,l:2372,c:2384},
        {o:2384,h:2398,l:2382,c:2396},{o:2396,h:2421,l:2395,c:2418},{o:2418,h:2419,l:2404,c:2406},
        {o:2406,h:2408,l:2394,c:2397},{o:2397,h:2399,l:2390,c:2392}],
       zones:[{p1:2360,p2:2390,label:'الخصم Discount',color:'#20939E',fill:0.10},
              {p1:2390,p2:2421,label:'العلاوة Premium',color:'#DF7573',fill:0.08}],
       levels:[{p:2390,label:'التوازن 50%',color:'#6A7B84',style:'solid',side:'left'}]},
     illus:true},
    {kind:'content', eyebrow:'الخطوة ٢ — موقع السيولة',
     h1:'سيولة أسفل القاع + قيمة سفلى',
     lead:'تحت القاع سيولة بيع (SSL) تتقاطع مع الحد السفلي للقيمة (VAL) من البروفايل.',
     chart:{type:'volprofile',
       candles:[
        {o:2408,h:2410,l:2404,c:2406},{o:2406,h:2408,l:2394,c:2397},{o:2397,h:2399,l:2390,c:2392},
        {o:2392,h:2394,l:2384,c:2387},{o:2387,h:2389,l:2379,c:2384},{o:2384,h:2392,l:2383,c:2390}],
       va:{vah:2404,val:2386},
       profile:[
        {p:2408,v:22},{p:2404,v:40},{p:2400,v:62},{p:2396,v:90,poc:1},{p:2392,v:70,hvn:1},
        {p:2388,v:48},{p:2386,v:38},{p:2382,v:20}],
       notes:[{i:4,p:2379,text:'سحب سيولة SSL',tx:300,ty:150,anchor:'end'}]},
     illus:true},
    {kind:'content', eyebrow:'الخطوة ٣ — دليل التنفيذ',
     h1:'إزاحة صاعدة تُخلّف فجوة',
     lead:'بعد السحب: Displacement صاعد بحجم متوسّع يترك فجوة FVG سليمة — هذا التأكيد.',
     chart:{type:'candles', volume:[{v:40},{v:44,c:0},{v:110,c:1,hl:1},{v:70,c:1},{v:50,c:0}],
       candles:[
        {o:2390,h:2392,l:2383,c:2384},{o:2384,h:2390,l:2383,c:2389},{o:2389,h:2412,l:2388,c:2410},
        {o:2410,h:2414,l:2400,c:2403},{o:2403,h:2409,l:2401,c:2407}],
       boxes:[{i1:1,i2:3,p1:2390,p2:2400,label:'FVG',color:'#257A93',dash:'0'}],
       notes:[{i:2,p:2411,text:'Displacement + توسّع حجم',tx:640,ty:60,anchor:'end'}]},
     illus:true},
    {kind:'content', eyebrow:'الخطوة ٤ — الدخول والإبطال والهدف',
     h1:'خطة تعليمية كاملة',
     chart:{type:'candles',
       candles:[
        {o:2397,h:2399,l:2390,c:2392},{o:2392,h:2394,l:2379,c:2384},{o:2384,h:2390,l:2383,c:2389},
        {o:2389,h:2412,l:2388,c:2410},{o:2410,h:2414,l:2398,c:2401},{o:2401,h:2419,l:2400,c:2416},{o:2416,h:2423,l:2414,c:2421}],
       boxes:[{i1:2,i2:4,p1:2390,p2:2400,label:'FVG',color:'#257A93'}],
       markers:[{i:4,p:2398,type:'entry'},{i:1,p:2378,type:'sl',label:'إبطال'},{i:6,p:2422,type:'target',label:'هدف BSL'}]},
     lead:'الدخول عند اختبار حد الفجوة داخل الخصم فوق VAL — الإبطال تحت قاع السحب — الهدف سيولة القمة.',
     note:'نموذج تعليمي لتوضيح التسلسل — ليس توصية ولا صفقة مضمونة.'},
    {kind:'cta', eyebrow:'خلاصة النموذج',
     h1:'الفجوة تُتداول بالسياق: خصم + سيولة + إزاحة — لا وحدها.',
     keyword:'فجوة',
     reasons:[
       {ic:'📌',t:'احفظه كقائمة خطوات قبل الدخول.'},
       {ic:'📤',t:'أرسله لمن يدخل كل فجوة بلا سياق.'}]},
  ]
},

// ══════════════════════════════════ 3 — VWAP + VOLUME: LOSS ANATOMY (Type C)
{
  idx:'03', slug:'vwap-touch-loss', type:'تشريح خسارة',
  kw:'فيواب', domains:'VWAP · Volume',
  title:'لمس VWAP… وخسارة',
  hookAlts:[
    'السعر فوق VWAP… ومع ذلك خسر. ليش؟',
    'لمس المتوسط ودخل… وانعكس عليه. وين الغلط؟',
    'ارتداد أكيد من VWAP… طلع فخ. شنو فاته؟'],
  sources:[
    'TradingView — VWAP & Anchored VWAP documentation',
    'TradingView — VWAP Bands / standard deviation',
    'Anna Coulling — Volume Price Analysis (Volume Dry-Up)',
    'Wyckoff — Acceptance vs Rejection'],
  slides:[
    {kind:'cover', kicker:'VWAP · VOLUME',
     hook:'السعر فوق VWAP…\nومع ذلك ((خسر)).', subq:'اللمسة شكلها ارتداد… والحقيقة غير.',
     tag:'رسم توضيحي'},
    {kind:'content', eyebrow:'لماذا بدت صحيحة؟',
     h1:'VWAP صاعد والسعر فوقه',
     lead:'اتجاه صاعد، أول عودة للمتوسط. القراءة السريعة: ارتداد كلاسيكي من VWAP.',
     chart:{type:'candles',
       candles:[
        {o:2372,h:2380,l:2370,c:2378},{o:2378,h:2388,l:2376,c:2386},{o:2386,h:2396,l:2384,c:2394},
        {o:2394,h:2400,l:2390,c:2392},{o:2392,h:2394,l:2385,c:2387},{o:2387,h:2390,l:2384,c:2386}],
       vwap:[{i:0,p:2374},{i:1,p:2378},{i:2,p:2382},{i:3,p:2384},{i:4,p:2385},{i:5,p:2386}],
       notes:[{i:5,p:2384,text:'لمسة أولى للمتوسط',tx:560,ty:70,anchor:'end'}]},
     illus:true},
    {kind:'content', eyebrow:'العلامة المتجاهلة', chip:'Dry-Up',
     h1:'الحجم ينكمش عند كل اقتراب',
     lead:'كلما اقترب السعر من VWAP، تبخّر الحجم. لا مشترين — فقط توقف بيع.',
     chart:{type:'candles', volume:[{v:100},{v:88},{v:64},{v:40},{v:26,hl:1},{v:22,hl:1}],
       candles:[
        {o:2372,h:2380,l:2370,c:2378},{o:2378,h:2388,l:2376,c:2386},{o:2386,h:2396,l:2384,c:2394},
        {o:2394,h:2400,l:2390,c:2392},{o:2392,h:2394,l:2385,c:2387},{o:2387,h:2390,l:2384,c:2386}],
       vwap:[{i:0,p:2374},{i:1,p:2378},{i:2,p:2382},{i:3,p:2384},{i:4,p:2385},{i:5,p:2386}],
       notes:[{i:4,p:2394,text:'Volume Dry-Up',tx:560,ty:60,anchor:'end'}]},
     illus:true},
    {kind:'content', eyebrow:'لحظة تغيّر السيناريو',
     h1:'إغلاق وقبول تحت VWAP',
     lead:'شمعة تغلق تحت المتوسط، ثم قبول (شمعتان) أسفله — رفض للمتوسط، لا ارتداد.',
     chart:{type:'candles',
       candles:[
        {o:2392,h:2394,l:2385,c:2387},{o:2387,h:2390,l:2384,c:2386},{o:2386,h:2387,l:2378,c:2380},
        {o:2380,h:2383,l:2374,c:2376},{o:2376,h:2379,l:2369,c:2371}],
       vwap:[{i:0,p:2385},{i:1,p:2386},{i:2,p:2386},{i:3,p:2385},{i:4,p:2385}],
       markers:[{i:2,p:2386,type:'sl',label:'رفض VWAP'}],
       notes:[{i:3,p:2374,text:'قبول تحت المتوسط',tx:640,ty:210,anchor:'end'}]},
     illus:true},
    {kind:'content', eyebrow:'كيف تمنع الخطأ؟', chip:'Checklist',
     h1:'اللمس ليس دخولًا',
     checklist:[
       {t:'اطلب توسّع حجم عند اللمس، لا انكماشه'},
       {t:'انتظر رفضًا واضحًا (فتيل/إغلاق) لا لمسة فقط'},
       {t:'فرّق: ارتداد للمتوسط أم قبول تحته؟'},
       {t:'اقرأ الاتجاه: استمرار أم انعكاس؟'}]},
    {kind:'cta', eyebrow:'خلاصة التشريح',
     h1:'VWAP مرجع للقيمة — لا زر دخول عند كل لمسة.',
     keyword:'فيواب',
     reasons:[
       {ic:'📌',t:'احفظه كقاعدة قبل استخدام VWAP.'},
       {ic:'📤',t:'أرسله لمن يدخل على مجرّد لمسة المتوسط.'}]},
  ]
},

// ══════════════════════════════════ 4 — SMC + FOOTPRINT: INDUCEMENT (Chart hidden story / Type D)
{
  idx:'04', slug:'smc-inducement-choch', type:'خفايا الشارت',
  kw:'استدراج', domains:'SMC · Footprint',
  title:'الاستدراج قبل تغيّر الطابع',
  hookAlts:[
    'كسر القمة… وانعكس فجأة. شنو صار؟',
    'اخترق فوق… ونزل على طول. مين اصطاد مين؟',
    'الكل شارى الكسر… والسوق طيّحهم. ليش؟'],
  sources:[
    'Smart Money Concepts — BOS / CHoCH / Inducement (community definitions, cross-checked)',
    'ICT — Buy-Side / Sell-Side Liquidity & Liquidity Sweep',
    'Sierra Chart / ATAS — Delta divergence & absorption at highs',
    'Note: SMC terminology varies between schools — definitions unified here'],
  slides:[
    {kind:'cover', kicker:'SMC · FOOTPRINT',
     hook:'كسر القمة…\nوانعكس ((فجأة)).', subq:'اللي شفته كسر… واللي صار حصاد سيولة.',
     tag:'رسم توضيحي'},
    {kind:'content', eyebrow:'الشارت قبل المارك أب',
     h1:'يبدو اختراقًا صاعدًا',
     lead:'قمة فرعية تُكسر لأعلى. القراءة السطحية: بريك آوت — ندخل مع الكسر.',
     chart:{type:'candles',
       candles:[
        {o:2400,h:2406,l:2398,c:2404},{o:2404,h:2412,l:2402,c:2410},{o:2410,h:2413,l:2401,c:2403},
        {o:2403,h:2411,l:2401,c:2409},{o:2409,h:2416,l:2408,c:2412},{o:2412,h:2418,l:2405,c:2407},
        {o:2407,h:2409,l:2398,c:2400}],
       notes:[{i:4,p:2417,text:'كسر فوق القمة',tx:600,ty:60,anchor:'end'}]},
     illus:true},
    {kind:'content', eyebrow:'تحديد السيولة',
     h1:'القمة كانت طُعمًا (Inducement)',
     lead:'فوق القمة الفرعية تجمّعت سيولة شراء (BSL): ستوبات بائعين + دخول كاسري الاختراق.',
     chart:{type:'candles',
       candles:[
        {o:2400,h:2406,l:2398,c:2404},{o:2404,h:2412,l:2402,c:2410},{o:2410,h:2413,l:2401,c:2403},
        {o:2403,h:2411,l:2401,c:2409},{o:2409,h:2416,l:2408,c:2412},{o:2412,h:2418,l:2405,c:2407},
        {o:2407,h:2409,l:2398,c:2400}],
       levels:[{p:2413,label:'قمة فرعية · طُعم',color:'#DF7573'}],
       zones:[{p1:2413,p2:2418,label:'سيولة شراء BSL',color:'#DF7573',fill:0.12}],
       notes:[{i:5,p:2417,text:'سحب السيولة فوق الطُعم',tx:620,ty:55,anchor:'end'}]},
     illus:true},
    {kind:'content', eyebrow:'ما كشفه التدفّق',
     h1:'شراء عدواني… تم امتصاصه',
     lead:'عند الاختراق: أوامر شراء ضخمة على الـAsk بلا تقدم (امتصاص)، ثم دلتا سالبة → CHoCH هابط.',
     chart:{type:'footprint', cols:[
       {label:'الاختراق', delta:260, cells:[
         {bid:60,ask:210,imb:'ask',absorb:1},{bid:70,ask:190,imb:'ask',absorb:1},{bid:80,ask:90},{bid:70,ask:60},{bid:50,ask:40}]},
       {label:'التوقف', delta:-70, cells:[
         {bid:120,ask:80,imb:'bid'},{bid:100,ask:70},{bid:90,ask:80},{bid:70,ask:70},{bid:50,ask:60}]},
       {label:'CHoCH', delta:-450, cells:[
         {bid:70,ask:50},{bid:110,ask:60,imb:'bid'},{bid:170,ask:50,imb:'bid'},{bid:210,ask:60,imb:'bid'},{bid:150,ask:40,imb:'bid'}]}]},
     illusNum:true},
    {kind:'content', eyebrow:'القاعدة المستخلصة', chip:'Rule',
     h1:'الكسر ليس تأكيدًا',
     rows:[
       {i:'١',b:'اسأل عن السيولة',s:'أي سيولة يلاحقها السعر قبل أن تصدّق الكسر؟'},
       {i:'٢',b:'انتظر تغيّر الطابع',s:'CHoCH + إزاحة يؤكدان النية الحقيقية.'},
       {i:'٣',b:'اقرأ التنفيذ',s:'امتصاص عند القمة = كسر مستدرَج غالبًا.'}]},
    {kind:'cta', eyebrow:'خلاصة الخفايا',
     h1:'أغلب الاختراقات طُعم — القصة تحت السطح لا في الشمعة.',
     keyword:'استدراج',
     reasons:[
       {ic:'📌',t:'احفظه كفلتر قبل تداول أي كسر.'},
       {ic:'📤',t:'أرسله لمن يطارد الاختراقات.'}]},
  ]
},

// ══════════════════════════════════ 5 — PSYCHOLOGY: MOVING THE STOP (Type E)
{
  idx:'05', slug:'psych-moving-stop', type:'علم نفس التداول',
  kw:'انضباط', domains:'علم النفس · إدارة المخاطر',
  title:'تحريك وقف الخسارة',
  hookAlts:[
    'نقلت الستوب… لأنك ما تقبّلت الخسارة؟',
    'خطأ ١R… صار ٣R. شنو اللي وسّعه؟',
    'وسّعت الستوب مرتين… ومن ضيّعك؟'],
  sources:[
    'Kahneman & Tversky — Prospect Theory (Loss Aversion)',
    'Mark Douglas — Trading in the Zone',
    'Behavioral finance — Disposition Effect',
    'Risk management — fixed-R execution model'],
  slides:[
    {kind:'cover', kicker:'PSYCHOLOGY · RISK',
     hook:'نقلت الستوب…\nلأنك ((ما تقبّلت)) الخسارة؟', subq:'الخسارة مو المشكلة — تحريك الستوب هو المشكلة.',
     tag:'سلوك تنفيذي'},
    {kind:'content', eyebrow:'تعريف الانحياز', chip:'Loss Aversion',
     h1:'نفور الخسارة',
     lead:'ألم الخسارة أقوى من متعة ربح مماثل، فنؤجّل الاعتراف بها — ونوسّع الستوب لتجنّب تحقّقها.',
     rows:[
       {i:'⚠',b:'خطأ فني؟ لا',s:'الدخول قد يكون سليمًا والخسارة طبيعية.'},
       {i:'✓',b:'خطأ تنفيذي',s:'توسيع الستوب قرار انضباط، لا قراءة سوق.'}]},
    {kind:'content', eyebrow:'كيف يظهر في التنفيذ؟',
     h1:'ثلاث علامات أثناء الصفقة',
     rows:[
       {i:'١',b:'تسحب الستوب',s:'عند اقتراب السعر منه، تنزله «شوي بس».'},
       {i:'٢',b:'تلغيه',s:'تقنع نفسك أن السوق «راح يرجع».'},
       {i:'٣',b:'تضيف للخاسرة',s:'Averaging down لتقليل متوسط الخسارة.'}]},
    {kind:'content', eyebrow:'مثال على الشارت',
     h1:'خطأ ١R تحوّل إلى ٣R',
     chart:{type:'candles',
       candles:[
        {o:2410,h:2412,l:2404,c:2406},{o:2406,h:2408,l:2398,c:2400},{o:2400,h:2402,l:2392,c:2394},
        {o:2394,h:2396,l:2386,c:2388},{o:2388,h:2390,l:2380,c:2382},{o:2382,h:2384,l:2374,c:2376}],
       markers:[{i:0,p:2410,type:'entry',label:'دخول شراء'},
                {i:0,p:2400,type:'sl',label:'ستوب أولي'}],
       levels:[{p:2390,label:'ستوب مُحرّك',color:'#DF7573',style:'solid'},
               {p:2378,label:'خروج فعلي',color:'#0B2635',side:'left'}],
       notes:[{i:3,p:2387,text:'كل مرة يوسّع الستوب',tx:640,ty:120,anchor:'end'}]},
     illus:true},
    {kind:'content', eyebrow:'بروتوكول التصحيح', chip:'Protocol',
     h1:'خمس خطوات عملية',
     checklist:[
       {t:'قاعدة قبل الدخول: حدّد ١R واكتبه'},
       {t:'سؤال فحص: أنقل الستوب بدليل بنيوي أم خوفًا؟'},
       {t:'حد مخاطرة: ١R ثابت لكل صفقة'},
       {t:'شرط إلغاء: ممنوع توسيع الستوب أبدًا'},
       {t:'بعد الخسارة: سجّلها وتوقّف صفقة واحدة'}]},
    {kind:'cta', eyebrow:'خلاصة السلوك',
     h1:'الصفقة الخاسرة قرار جيد نفّذته. المشكلة أن تلغي القرار.',
     keyword:'انضباط',
     reasons:[
       {ic:'📌',t:'احفظه كبروتوكول قبل كل صفقة.'},
       {ic:'📤',t:'أرسله لمن يحرّك ستوبه دائمًا.'}]},
  ]
},
];
