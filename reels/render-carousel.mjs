import { chromium } from 'playwright-core';
import { pathToFileURL } from 'url';
import path from 'path';
import fs from 'fs';
const CHROME='/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell';
const url=pathToFileURL(path.resolve('carousel-slides.html')).href;
fs.mkdirSync('out/carousel',{recursive:true});
const b=await chromium.launch({executablePath:CHROME,args:['--no-sandbox','--force-color-profile=srgb','--hide-scrollbars']});
const p=await b.newPage({viewport:{width:1080,height:1350},deviceScaleFactor:2});
await p.goto(url,{waitUntil:'networkidle'}); await p.evaluate(()=>document.fonts.ready); await p.waitForTimeout(400);
const names=['01-cover','02-discipline','03-risk','04-consistency','05-patience','06-mindset'];
for(let i=0;i<names.length;i++){const el=await p.$('#s'+(i+1));
  await el.screenshot({path:`out/carousel/${names[i]}.png`});}
console.log('ok'); await b.close();
