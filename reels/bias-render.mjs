import { chromium } from 'playwright-core';
import { pathToFileURL } from 'url';
import path from 'path';
import fs from 'fs';
const CHROME='/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell';
const url=pathToFileURL(path.resolve('bias-reel.html')).href;
const FPS=30;
const outDir='frames_bias';
fs.rmSync(outDir,{recursive:true,force:true}); fs.mkdirSync(outDir,{recursive:true});
const b=await chromium.launch({executablePath:CHROME,args:['--no-sandbox','--force-color-profile=srgb','--hide-scrollbars','--disable-lcd-text']});
const p=await b.newPage({viewport:{width:1080,height:1920},deviceScaleFactor:1});
await p.goto(url,{waitUntil:'networkidle'});
await p.waitForFunction(()=>window.__ready===true,{timeout:20000});
await p.evaluate(()=>document.fonts&&document.fonts.ready);
const TOTAL=await p.evaluate(()=>window.__TOTAL);
const N=Math.round(TOTAL*FPS);
const stage=await p.$('#stage');
console.log('TOTAL',TOTAL,'frames',N);
for(let f=0; f<N; f++){
  const t=f/FPS;
  await p.evaluate(t=>window.__setT(t),t);
  await p.evaluate(()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r))));
  await stage.screenshot({path:`${outDir}/f${String(f).padStart(4,'0')}.png`});
  if(f%60===0) console.log('frame',f,'/',N);
}
console.log('DONE frames');
await b.close();
