import fs from 'fs';
import path from 'path';
import { chromium } from '/opt/node22/lib/node_modules/playwright/index.mjs';
import sharp from 'sharp';
import { PDFDocument } from 'pdf-lib';
import { renderChart, gemSVG } from './charts.js';

const HANDLE='@liquidity.state';
const FONTS=fs.readFileSync('src/fonts.css','utf8');
const THEME=fs.readFileSync('src/theme.css','utf8');
const S=JSON.parse(fs.readFileSync('../reel/data/scenario_carousel.json','utf8'));
const OUT='out/png-stop'; fs.mkdirSync(OUT,{recursive:true}); fs.mkdirSync('dist',{recursive:true});
const esc=s=>String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
const hl=s=>esc(s).replace(/\(\((.+?)\)\)/g,'<span class="hl">$1</span>');
const hook=s=>hl(s).replace(/\n/g,'<br>');
const dots=(n,t=6)=>{let s='<div class="dots">';for(let i=1;i<=t;i++)s+=`<i class="${i===n?'on':''}"></i>`;return s+'</div>';};

const cndl=S.candles.map(c=>({o:c.o,h:c.h,l:c.l,c:c.c}));
const prof=S.profile.filter(x=>x.p>=410&&x.p<=451).map(x=>({p:x.p,v:x.v,poc:Math.abs(x.p-S.poc)<0.26,hvn:x.p>=S.val&&x.p<=S.vah}));
const SRC=`إعادة رسم من بيانات سوق تاريخية — GLD · Alpha Vantage — ${S.firstDate}→${S.lastDate}`;

const slides=[
 {kind:'cover', kicker:'VOLUME PROFILE · إدارة المخاطر',
  hook:'أقرب ظل\n((مو)) مكان ستوبك.', subq:'الستوب يتحدد بالقيمة والسياق — لا بأقرب ذيل.', tag:'بيانات سوق حقيقية · GLD'},
 {kind:'content', eyebrow:'منطقة القيمة', chip:'Value Area', h1:'VAH فوق · POC وسط · VAL تحت',
  lead:'70% من الحجم يتداول داخل منطقة القيمة: VAH حدّها الأعلى، POC أعلى تنفيذ، VAL حدّها الأدنى.',
  chart:{type:"volprofile", candles:cndl, va:{vah:S.vah,val:S.val}, profile:prof}, src:SRC},
 {kind:'content', eyebrow:'القاعدة', h1:'الستوب فوق بطلان الفكرة',
  rows:[{i:'١',b:'حدّد قمة الخروج',s:'أعلى نقطة في محاولة الاختراق الفاشلة فوق VAH.'},
        {i:'٢',b:'ضعه فوقها + هامش',s:'فوق القمة بهامش تذبذب/سبريد، لا ملاصقًا للذيل.'},
        {i:'٣',b:'ليس أقرب ظل',s:'أقرب ذيل يُضرب بالضجيج، لا ببطلان الفكرة.'}],
  note:'موقع الستوب يقرّره السياق (القيمة والبنية)، لا المسافة لأقرب شمعة.'},
 {kind:'content', eyebrow:'مثال موثّق', chip:'GLD · 1D', h1:'خروج فوق VAH… ثم فشل قبول',
  chart:{type:'candles', candles:cndl,
    // كل خط يبدأ من الشمعة التي أنشأته وينتهي عند آخر امتداد منطقي — لا من حافة إلى حافة
    levels:[{p:S.exitHigh,label:'قمة الخروج',color:'#0B2635',i1:S.exitIdx-1,i2:S.valTargetIdx},
            {p:S.vah,label:'VAH',color:'#257A93',i1:S.rangeI0,i2:S.candles.length-1},
            {p:S.poc,label:'POC',color:'#DF7573',i1:S.rangeI0,i2:S.pocTargetIdx+1,side:'left'},
            {p:S.val,label:'VAL',color:'#257A93',i1:S.rangeI0,i2:S.valTargetIdx+1,side:'left'}],
    markers:[{i:S.failIdx,p:S.entryPrice,type:'entry',label:'دخول '+S.entryPrice,i1:S.failIdx-1,i2:S.valTargetIdx},
             {i:S.exitIdx,p:S.slPrice,type:'sl',label:'ستوب '+S.slPrice,i1:S.exitIdx-1,i2:S.valTargetIdx}],
  },
  lead:'اخترق VAH ثم أغلق داخل القيمة (فشل قبول). الستوب فوق قمة الخروج، والأهداف POC ثم VAL.',
  note:'لغرض تعليمي — ليس توصية · Volume Profile تقديري (حجم يومي حقيقي).'},
 {kind:'content', eyebrow:'قبل وضع الستوب', chip:'Checklist', h1:'أربعة أسئلة',
  checklist:[{t:'هل الستوب فوق بطلان الفكرة (قمة الخروج)؟'},
             {t:'هل أضفت هامش تذبذب أو سبريد؟'},
             {t:'هل ابتعد عن أقرب ذيل ضجيج؟'},
             {t:'هل الهدف مربوط بـPOC/VAL لا رقم عشوائي؟'}]},
 {kind:'cta', eyebrow:'الخلاصة', h1:'الستوب يتحدد بالقيمة والسياق — لا بأقرب ظل.', keyword:'ستوب',
  reasons:[{ic:'📌',t:'احفظه كقائمة قبل وضع أي ستوب.'},{ic:'📤',t:'أرسله لمن يحط ستوبه على أقرب ذيل.'}]},
];

function coverDecor(){let s=`<svg viewBox="0 0 1080 1350" xmlns="http://www.w3.org/2000/svg">`;
 for(let g=0;g<14;g++)s+=`<line x1="0" y1="${g*100}" x2="1080" y2="${g*100}" stroke="#20939E" stroke-width="1" opacity="0.25"/>`;
 const base=1050;let x=90;const seq=[[40,120],[60,150],[30,90],[70,180],[50,140],[80,210],[45,120],[65,170],[35,100],[75,200],[55,150],[85,220]];
 seq.forEach((c,i)=>{const h=c[1],top=base-(i*46)-c[0];s+=`<line x1="${x+22}" y1="${top-30}" x2="${x+22}" y2="${top+h+30}" stroke="#20939E" stroke-width="2"/><rect x="${x}" y="${top}" width="44" height="${h}" fill="none" stroke="#20939E" stroke-width="2"/>`;x+=80;});
 return s+`</svg>`;}
function frameHead(pn){return `<div class="topbar"><div class="brand"><div style="width:44px;height:44px">${gemSVG('#F7FAFB','#20939E')}</div><span class="wm">Liquidity State</span></div><span class="counter num">0${pn} / 06</span></div>`;}
function footer(pn){return `<div class="footer"><span>محتوى تعليمي · ليس توصية</span>${dots(pn)}<span class="num">${HANDLE}</span></div>`;}
// رأس الشارت: الرمز · الفريم · المنطقة الزمنية — وتذييل: المصدر والفترة (متطلّب §9 الإفصاح)
function chartCard(s){return `<div class="visual"><div class="chartcard">`+
 `<div class="chhead"><span class="chsym num">GLD · 1D · ET (NYSE Arca)</span><span class="chnote">${esc(s.headnote||'إعادة رسم من بيانات سوق تاريخية')}</span></div>`+
 `<div dir="ltr">${renderChart(s.chart)}</div>`+
 `<div class="cap"><span class="illus">${esc(s.src||'')}</span><span class="num">VA 70%</span></div></div></div>`;}
function rows(r){return `<div class="rows">`+r.map(x=>`<div class="row"><div class="idx num">${esc(x.i)}</div><div class="rtx"><b>${esc(x.b)}</b><span>${esc(x.s)}</span></div></div>`).join('')+`</div>`;}
function checks(items){return `<div class="checklist">`+items.map(it=>`<div class="check"><span class="bx">✓</span><span>${esc(it.t)}</span></div>`).join('')+`</div>`;}

function body(s,pn){
 if(s.kind==='cover') return `<div class="slide cover"><div class="cov-chart">${coverDecor()}</div><div class="frame">${frameHead(pn)}<div class="kicker en">${esc(s.kicker)}</div><div class="hook">${hook(s.hook)}</div><div class="subq">${esc(s.subq)}</div><div class="swipe">اسحب <span class="num">←</span></div><div class="tag">${esc(s.tag)}</div><div class="footer"><span class="num">${HANDLE}</span>${dots(pn)}<span></span></div></div></div>`;
 if(s.kind==='cta') return `<div class="slide cta"><div class="frame">${frameHead(pn)}<div class="stage"><div class="eyebrow">${esc(s.eyebrow)}</div><div class="h1">${hl(s.h1)}</div><div class="ctabox"><div class="kw">اكتب «<span class="word">${esc(s.keyword)}</span>» بالتعليقات، وأرسل لك الملخص.</div><div class="sub">تعليقك يفتح لك ملخص الكاروسيل مباشرة في الخاص.</div></div><div class="reasons">${s.reasons.map(r=>`<div class="reason"><span class="ic">${r.ic}</span><span>${esc(r.t)}</span></div>`).join('')}</div><div class="handle"><div style="width:34px;height:34px">${gemSVG('#0B2635','#257A93')}</div><span class="en">${HANDLE}</span></div></div>${footer(pn)}</div></div>`;
 let inner=`<div class="eyebrow">${esc(s.eyebrow)}${s.chip?`<span class="chip en">${esc(s.chip)}</span>`:''}</div><div class="h1">${hl(s.h1)}</div>`;
 if(s.lead&&!s.chart) inner+=`<div class="lead">${esc(s.lead)}</div>`;
 if(s.chart){inner+=chartCard(s); if(s.lead) inner+=`<div class="lead" style="margin-top:18px">${esc(s.lead)}</div>`;}
 if(s.rows) inner+=rows(s.rows);
 if(s.checklist) inner+=checks(s.checklist);
 if(s.note) inner+=`<div class="small" style="margin-top:20px">${esc(s.note)}</div>`;
 return `<div class="slide content"><div class="frame">${frameHead(pn)}<div class="stage">${inner}</div>${footer(pn)}</div></div>`;
}
const page=b=>`<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8"><style>${FONTS}\n${THEME}</style></head><body>${b}</body></html>`;

const browser=await chromium.launch();
const pg=await browser.newPage({viewport:{width:1080,height:1350},deviceScaleFactor:2});
const files=[];
for(let i=0;i<slides.length;i++){const pn=i+1;
 await pg.setContent(page(body(slides[i],pn)),{waitUntil:'networkidle'});
 await pg.evaluate(()=>document.fonts.ready);
 const buf=await pg.screenshot({clip:{x:0,y:0,width:1080,height:1350}});
 const fp=path.join(OUT,`stop_0${pn}.png`);
 await sharp(buf).resize(1080,1350,{kernel:'lanczos3'}).png({compressionLevel:9}).toFile(fp);
 files.push(fp); process.stdout.write(`✓ ${fp}\n`);
}
await browser.close();
const doc=await PDFDocument.create(); doc.setTitle('Liquidity State — وين تحط الستوب؟ (Volume Profile)'); doc.setAuthor('Liquidity State');
for(const fp of files){const png=await doc.embedPng(fs.readFileSync(fp));const p=doc.addPage([1080,1350]);p.drawImage(png,{x:0,y:0,width:1080,height:1350});}
fs.writeFileSync('dist/stop-vp-carousel.pdf',await doc.save());
console.log('DONE 6 pages + PDF');
