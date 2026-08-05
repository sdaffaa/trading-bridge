const fs=require('fs'),path=require('path');const {chromium}=require('playwright');
const OUT=path.join(__dirname,'..','out');
(async()=>{
  const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium-1194/chrome-linux/chrome'});
  const p=await b.newPage({viewport:{width:1560,height:1180}});
  for(const id of fs.readdirSync(OUT).filter(f=>fs.statSync(path.join(OUT,f)).isDirectory())){
    const files=fs.readdirSync(path.join(OUT,id)).filter(f=>f.endsWith('.png')).sort();
    const imgs=files.map(f=>{
      const d=fs.readFileSync(path.join(OUT,id,f)).toString('base64');
      return `<figure><img src="data:image/png;base64,${d}"><figcaption>${f}</figcaption></figure>`;
    }).join('');
    await p.setContent(`<style>body{margin:0;background:#5a5a5a;font-family:monospace;display:flex;flex-wrap:wrap;gap:10px;padding:12px}
      figure{margin:0}img{width:360px;display:block;border:1px solid #222}
      figcaption{color:#fff;font-size:13px;padding:3px}</style>${imgs}`);
    await p.waitForTimeout(200);
    await p.screenshot({path:path.join(OUT,`QA-${id}.png`),fullPage:true});
    console.log('QA sheet:',id);
  }
  await b.close();
})();
