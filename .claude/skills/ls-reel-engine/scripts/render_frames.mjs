#!/usr/bin/env node
// Deterministic frame capture: load the reel HTML, call window.renderFrame(t) per frame, screenshot at 1080x1920.
// Usage: node render_frames.mjs --html index.html --out frames --fps 30 --dur 23.5 [--playwright <path>]
import fs from 'fs';
const arg=(k,d)=>{const i=process.argv.indexOf('--'+k);return i>=0?process.argv[i+1]:d;};
const HTML=arg('html','index.html'), OUT=arg('out','frames'), FPS=+arg('fps','30'), DUR=+arg('dur','23.5');
const PW=arg('playwright','/opt/node22/lib/node_modules/playwright/index.mjs');
const {chromium}=await import(PW);
fs.rmSync(OUT,{recursive:true,force:true});fs.mkdirSync(OUT,{recursive:true});
const N=Math.round(FPS*DUR);
const browser=await chromium.launch();
const page=await browser.newPage({viewport:{width:1080,height:1920},deviceScaleFactor:1});
const errs=[];page.on('pageerror',e=>errs.push(String(e)));
await page.setContent(fs.readFileSync(HTML,'utf8'),{waitUntil:'load'});
await page.evaluate(()=>document.fonts.ready);
const t0=Date.now();
for(let f=0;f<N;f++){await page.evaluate(tt=>window.renderFrame(tt),f/FPS);
  await page.screenshot({path:`${OUT}/${String(f).padStart(4,'0')}.png`,clip:{x:0,y:0,width:1080,height:1920}});
  if(f%60===0)console.error(`frame ${f}/${N}`);}
await browser.close();
if(errs.length){console.error('PAGE ERRORS:',errs.slice(0,3));process.exit(1);}
console.error(`rendered ${N} frames in ${((Date.now()-t0)/1000).toFixed(1)}s -> ${OUT}`);
