import fs from 'fs';
import { chromium } from '/opt/node22/lib/node_modules/playwright/index.mjs';

const FPS=30, DUR=23.5, N=Math.round(FPS*DUR);
fs.rmSync('frames',{recursive:true,force:true}); fs.mkdirSync('frames');
const html=fs.readFileSync('index.html','utf8');
const browser=await chromium.launch();
const page=await browser.newPage({viewport:{width:1080,height:1920},deviceScaleFactor:1});
await page.setContent(html,{waitUntil:'load'});
await page.evaluate(()=>document.fonts.ready);
const t0=Date.now();
for(let f=0;f<N;f++){
  const t=f/FPS;
  await page.evaluate(tt=>window.renderFrame(tt),t);
  await page.screenshot({path:`frames/${String(f).padStart(4,'0')}.png`,clip:{x:0,y:0,width:1080,height:1920}});
  if(f%60===0)process.stdout.write(`frame ${f}/${N}\n`);
}
await browser.close();
console.log('rendered',N,'frames in',((Date.now()-t0)/1000).toFixed(1),'s');
