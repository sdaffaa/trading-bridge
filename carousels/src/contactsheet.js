import fs from 'fs';
import path from 'path';
import { chromium } from '/opt/node22/lib/node_modules/playwright/index.mjs';
import { carousels } from './content.js';

const PNG='out/png';
const b64=p=>'data:image/png;base64,'+fs.readFileSync(p).toString('base64');
const slug=(c,p)=>`${c.idx}_${String(p).padStart(2,'0')}_${c.slug}`;

let rows='';
for(const c of carousels){
  let cells='';
  for(let i=1;i<=6;i++){cells+=`<div class="cell"><img src="${b64(path.join(PNG,slug(c,i)+'.png'))}"><span>${c.idx}·${i}</span></div>`;}
  rows+=`<div class="rowlabel">${c.idx} — ${c.title} <em>(${c.type} · ${c.domains}) · كلمة: ${c.kw}</em></div><div class="row">${cells}</div>`;
}
const html=`<!doctype html><html dir="rtl"><head><meta charset="utf-8"><style>
body{background:#20303a;margin:0;padding:34px;font-family:sans-serif}
.rowlabel{color:#cfe0e4;font-size:20px;font-weight:700;margin:22px 6px 10px;direction:rtl}
.rowlabel em{color:#8fb0b8;font-weight:400;font-size:16px}
.row{display:grid;grid-template-columns:repeat(6,1fr);gap:12px}
.cell{position:relative;background:#000;border-radius:6px;overflow:hidden}
.cell img{width:100%;display:block}
.cell span{position:absolute;top:6px;left:6px;background:#000a;color:#fff;font-size:14px;padding:2px 8px;border-radius:4px;direction:ltr}
</style></head><body>${rows}</body></html>`;

const browser=await chromium.launch();
const page=await browser.newPage({viewport:{width:1600,height:2400},deviceScaleFactor:1});
await page.setContent(html,{waitUntil:'networkidle'});
await page.evaluate(()=>document.fonts.ready);
const h=await page.evaluate(()=>document.body.scrollHeight);
await page.setViewportSize({width:1600,height:h});
await page.screenshot({path:'out/contact-sheet.png',fullPage:true});
await browser.close();
console.log('contact sheet done, height',h);
