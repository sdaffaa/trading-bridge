import fs from 'fs';
const b64=p=>fs.readFileSync(p).toString('base64');
const faces=[['Plex',400,'fonts/IBMPlexSansArabic-Regular.ttf'],['Plex',500,'fonts/IBMPlexSansArabic-Medium.ttf'],
 ['Plex',600,'fonts/IBMPlexSansArabic-SemiBold.ttf'],['Plex',700,'fonts/IBMPlexSansArabic-Bold.ttf']];
let fontcss=faces.map(([f,w,p])=>`@font-face{font-family:'${f}';font-weight:${w};font-display:block;src:url(data:font/ttf;base64,${b64(p)}) format('truetype')}`).join('\n');
const scene=fs.readFileSync('scene.js','utf8');

const css=`
*{margin:0;padding:0;box-sizing:border-box}
html,body{width:1080px;height:1920px;overflow:hidden;background:#04121c}
#stage{position:relative;width:1080px;height:1920px;font-family:'Plex',sans-serif}
.layer{position:absolute;inset:0}
.hook{display:flex;align-items:center;justify-content:center}
.hookart{position:absolute;top:120px;left:0;width:1080px;display:flex;justify-content:center}
.logo{position:absolute;top:250px;left:0;width:1080px;display:flex;flex-direction:column;align-items:center;gap:12px}
.logo .gem{width:66px;height:66px}
.logo .wm{font-weight:700;font-size:30px;letter-spacing:6px;color:#12333f}
.card{position:absolute;left:64px;top:600px;width:952px;height:980px;background:linear-gradient(180deg,#0E1E24,#12262E);
  border-radius:30px;padding:34px;overflow:hidden;box-shadow:0 24px 70px #0b263533;border:1px solid #21414c}
.cardhead{display:flex;justify-content:space-between;align-items:center;height:44px;margin-bottom:6px}
.cardhead .chl{color:#9FB4BC;font-size:22px;font-weight:600;direction:rtl}
.cardhead .chr{color:#5E828C;font-size:20px;direction:rtl}
.chart{width:884px;height:912px;position:relative}
.chart svg{position:absolute;top:0;left:0}
.maintext{position:absolute;left:90px;right:90px;text-align:center;direction:rtl;font-weight:700;line-height:1.35;
  text-shadow:0 2px 18px #0003}
.tcard{position:absolute;width:264px;background:#ffffffee;border:2px solid;border-radius:14px;padding:10px 18px;
  direction:rtl;text-align:right;box-shadow:0 10px 30px #0b263522}
.tcard b{display:block;font-size:24px}
.tcard span{font-size:21px;color:#3d5560}
.summary{position:absolute;left:120px;right:120px;top:1040px;display:flex;flex-direction:column;gap:16px;direction:rtl}
.summary .srow{display:flex;align-items:center;gap:16px;background:#ffffffea;border:1px solid #cdd9db;border-radius:16px;
  padding:16px 22px;font-size:38px;font-weight:600;color:#12333f}
.summary .sn{flex:none;width:48px;height:48px;border-radius:12px;background:#12333f;color:#fff;font-weight:700;
  display:flex;align-items:center;justify-content:center;font-size:26px}
.cta{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:22px;
  background:linear-gradient(180deg,#F6F1E9,#EAE0D2);direction:rtl;padding:0 90px}
.cta .ctalogo{width:80px;height:80px;margin-bottom:6px}
.cta .ctamain{font-size:82px;font-weight:700;color:#12333f;text-align:center;line-height:1.3}
.cta .ctamain span{color:#1c8f86}
.cta .ctasub{font-size:44px;font-weight:500;color:#4a616b;text-align:center}
.cta .handle{margin-top:16px;font-size:40px;font-weight:700;color:#1c8f86;direction:ltr}
`;
const html=`<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8"><style>${fontcss}\n${css}</style></head>`+
`<body><div id="stage"></div><script>${scene}</script>`+
`<script>window.__ready=true;window.renderFrame=function(t){document.getElementById('stage').innerHTML=window.buildStage(t);};</script></body></html>`;
fs.writeFileSync('index.html',html);
console.log('index.html',(html.length/1e6).toFixed(2),'MB');
