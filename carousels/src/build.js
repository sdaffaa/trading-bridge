import fs from 'fs';
import path from 'path';
import { chromium } from '/opt/node22/lib/node_modules/playwright/index.mjs';
import { PDFDocument } from 'pdf-lib';
import sharp from 'sharp';
import { carousels, HANDLE } from './content.js';
import { renderChart, gemSVG } from './charts.js';

const ROOT = path.resolve('.');
const FONTS = fs.readFileSync('src/fonts.css','utf8');
const THEME = fs.readFileSync('src/theme.css','utf8');
const PNG = 'out/png', PDF = 'dist';
fs.mkdirSync(PNG,{recursive:true}); fs.mkdirSync(PDF,{recursive:true});

const esc = s => String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
const hook = s => esc(s).replace(/\n/g,'<br>').replace(/\(\((.+?)\)\)/g,'<span class="hl">$1</span>');
const hl = s => esc(s).replace(/\(\((.+?)\)\)/g,'<span class="hl">$1</span>');

function dots(n,total=6){let s='<div class="dots">';for(let i=1;i<=total;i++)s+=`<i class="${i===n?'on':''}"></i>`;return s+'</div>';}

function coverDecor(){
  // faint rising candle silhouette + grid
  let s=`<svg viewBox="0 0 1080 1350" xmlns="http://www.w3.org/2000/svg">`;
  for(let g=0;g<14;g++)s+=`<line x1="0" y1="${g*100}" x2="1080" y2="${g*100}" stroke="#20939E" stroke-width="1" opacity="0.25"/>`;
  const base=1050; let x=90;
  const seq=[[40,120],[60,150],[30,90],[70,180],[50,140],[80,210],[45,120],[65,170],[35,100],[75,200],[55,150],[85,220]];
  seq.forEach((c,i)=>{const h=c[1],top=base-(i*46)-c[0]; s+=`<line x1="${x+22}" y1="${top-30}" x2="${x+22}" y2="${top+h+30}" stroke="#20939E" stroke-width="2"/>`+
    `<rect x="${x}" y="${top}" width="44" height="${h}" fill="none" stroke="#20939E" stroke-width="2"/>`;x+=80;});
  return s+`</svg>`;
}

function frameHead(c,pageNum){
  return `<div class="topbar"><div class="brand"><div class="gemwrap" style="width:44px;height:44px">${gemSVG('#F7FAFB','#20939E')}</div>`+
    `<span class="wm">Liquidity State</span></div>`+
    `<span class="counter num">0${pageNum} / 06</span></div>`;
}
function frameHeadDark(c,pageNum){
  return `<div class="topbar"><div class="brand"><div style="width:44px;height:44px">${gemSVG('#F7FAFB','#20939E')}</div>`+
    `<span class="wm">Liquidity State</span></div>`+
    `<span class="counter num">0${pageNum} / 06</span></div>`;
}
function footer(c,pageNum,dark=false){
  const left = dark?`<span class="num">${HANDLE}</span>`:`<span>محتوى تعليمي · ليس توصية</span>`;
  return `<div class="footer">${left}${dots(pageNum)}<span class="num">${HANDLE}</span></div>`;
}

function chartCard(chart,slide){
  const cap = slide.illusNum?'أرقام تعليمية — ليست بيانات حقيقية':(slide.illus?'رسم توضيحي — ليس شارتًا حقيقيًا':'');
  return `<div class="visual"><div class="chartcard"><div dir="ltr">${renderChart(chart)}</div>`+
    (cap?`<div class="cap"><span class="illus">${cap}</span><span class="num">Liquidity State</span></div>`:'')+`</div></div>`;
}
function rowsBlock(rows){
  return `<div class="rows">`+rows.map(r=>{
    const cls = r.i==='⚠'?'warn':(r.i==='✓'?'ok':'');
    return `<div class="row ${cls}"><div class="idx num">${esc(r.i)}</div><div class="rtx"><b>${esc(r.b)}</b><span>${esc(r.s)}</span></div></div>`;
  }).join('')+`</div>`;
}
function checkBlock(items){
  return `<div class="checklist">`+items.map(it=>{
    const bad=it.bad; return `<div class="check ${bad?'bad':''}"><span class="bx">${bad?'✕':'✓'}</span><span>${esc(it.t)}</span></div>`;
  }).join('')+`</div>`;
}

function slideBody(c,s,pageNum){
  if(s.kind==='cover'){
    return `<div class="slide cover"><div class="cov-chart">${coverDecor()}</div><div class="frame">`+
      frameHeadDark(c,pageNum)+
      `<div class="kicker en">${esc(s.kicker)}</div>`+
      `<div class="hook">${hook(s.hook)}</div>`+
      `<div class="subq">${esc(s.subq)}</div>`+
      `<div class="swipe">اسحب <span class="num">←</span></div>`+
      `<div class="tag">${esc(s.tag)}</div>`+
      `<div class="footer"><span class="num">${HANDLE}</span>${dots(pageNum)}<span></span></div>`+
      `</div></div>`;
  }
  if(s.kind==='cta'){
    const inner = `<div class="eyebrow">${esc(s.eyebrow)}</div>`+
      `<div class="h1">${hl(s.h1)}</div>`+
      `<div class="ctabox"><div class="kw">اكتب «<span class="word">${esc(s.keyword)}</span>» بالتعليقات، وأرسل لك الملخص.</div>`+
      `<div class="sub">تعليقك يفتح لك ملخص الكاروسيل مباشرة في الخاص.</div></div>`+
      `<div class="reasons">`+s.reasons.map(r=>`<div class="reason"><span class="ic">${r.ic}</span><span>${esc(r.t)}</span></div>`).join('')+`</div>`+
      `<div class="handle"><div style="width:34px;height:34px">${gemSVG('#0B2635','#257A93')}</div><span class="en">${HANDLE}</span></div>`;
    return `<div class="slide cta"><div class="frame">`+frameHead(c,pageNum)+`<div class="stage">${inner}</div>`+footer(c,pageNum)+`</div></div>`;
  }
  // content
  let inner = `<div class="eyebrow">${esc(s.eyebrow)}${s.chip?`<span class="chip en">${esc(s.chip)}</span>`:''}</div>`+
    `<div class="h1">${hl(s.h1)}</div>`;
  if(s.lead && !s.chart) inner += `<div class="lead">${esc(s.lead)}</div>`;
  if(s.chart){ inner += chartCard(s.chart,s); if(s.lead) inner += `<div class="lead" style="margin-top:20px">${esc(s.lead)}</div>`; }
  if(s.rows) inner += rowsBlock(s.rows);
  if(s.checklist) inner += checkBlock(s.checklist);
  if(s.note) inner += `<div class="small" style="margin-top:22px">${esc(s.note)}</div>`;
  return `<div class="slide content"><div class="frame">`+frameHead(c,pageNum)+`<div class="stage">${inner}</div>`+footer(c,pageNum)+`</div></div>`;
}

function pageHTML(bodyHTML){
  return `<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8">`+
    `<style>${FONTS}\n${THEME}</style></head><body>${bodyHTML}</body></html>`;
}

const slug = (c,p)=>`${c.idx}_${String(p).padStart(2,'0')}_${c.slug}`;

async function main(){
  const browser = await chromium.launch();
  const page = await browser.newPage({viewport:{width:1080,height:1350},deviceScaleFactor:2});
  const manifest=[];
  for(const c of carousels){
    for(let i=0;i<c.slides.length;i++){
      const pn=i+1, s=c.slides[i];
      const html = pageHTML(slideBody(c,s,pn));
      await page.setContent(html,{waitUntil:'networkidle'});
      await page.evaluate(()=>document.fonts.ready);
      const file = path.join(PNG, slug(c,pn)+'.png');
      const buf = await page.screenshot({clip:{x:0,y:0,width:1080,height:1350}});
      await sharp(buf).resize(1080,1350,{kernel:'lanczos3'}).png({compressionLevel:9}).toFile(file);
      manifest.push({carousel:c.idx, page:pn, file, kind:s.kind});
      process.stdout.write(`✓ ${slug(c,pn)}.png\n`);
    }
  }
  await browser.close();

  // ---- PDFs ----
  async function pngToPdf(files, outPath, meta){
    const doc = await PDFDocument.create();
    doc.setTitle(meta.title); doc.setAuthor('Liquidity State');
    doc.setSubject(meta.subject||'Educational trading carousel'); doc.setCreator('Liquidity State');
    for(const fpath of files){
      const png = await doc.embedPng(fs.readFileSync(fpath));
      const pg = doc.addPage([1080,1350]);
      pg.drawImage(png,{x:0,y:0,width:1080,height:1350});
    }
    fs.writeFileSync(outPath, await doc.save());
  }
  const allFiles=[];
  for(const c of carousels){
    const files = c.slides.map((_,i)=>path.join(PNG,slug(c,i+1)+'.png'));
    allFiles.push(...files);
    const out = path.join(PDF, `${c.idx}_${c.slug}.pdf`);
    await pngToPdf(files,out,{title:`${c.title} — Liquidity State`, subject:`${c.type} · ${c.domains}`});
    process.stdout.write(`✓ PDF ${path.basename(out)}\n`);
  }
  await pngToPdf(allFiles, path.join(PDF,'liquidity-state-batch_30pages.pdf'),
    {title:'Liquidity State — دفعة 5 كاروسيلات (30 صفحة)', subject:'ICT · SMC · Footprint · Volume Profile · VWAP · Volume · Psychology'});
  process.stdout.write(`✓ PDF combined 30 pages\n`);

  fs.writeFileSync('out/manifest.json', JSON.stringify(manifest,null,2));
  console.log('DONE', manifest.length, 'pages');
}
main().catch(e=>{console.error(e);process.exit(1);});
