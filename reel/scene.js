/* Liquidity State — VP stop-placement reel (Mode B: rebuilt from verified historical market data).
   Source: GLD (SPDR Gold Shares) daily, Alpha Vantage. Volume Profile = تقديري (built from real daily volume). */
(function(){
const D=window.__DATA;
const W=1080,H=1920;
const clamp=(v,a,b)=>Math.max(a,Math.min(b,v));
const lerp=(a,b,x)=>a+(b-a)*x;
const smooth=x=>{x=clamp(x,0,1);return x*x*(3-2*x);};
const seg=(t,a,b)=>smooth((t-a)/(b-a));
const fade=(t,a,d=0.2)=>clamp((t-a)/d,0,1);
const esc=s=>String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
const fmtP=p=>{const r=Math.round(p*10)/10;return (r%1?r.toFixed(1):r.toFixed(0));};

const C=D.candles, N=C.length;
const VAH=D.vah, POC=D.poc, VAL=D.val;
const EXIT=D.exitIdx, FAIL=D.failIdx, POCI=D.pocTargetIdx, VALI=D.valTargetIdx;
const EXITHI=D.exitHigh, ENTRY=D.entryPrice, SL=D.slPrice, R1=D.rangeI0, R2=D.rangeI1;

// ---- reveal schedule from real indices ----
const revealAt=[];
for(let i=0;i<N;i++){
  if(i<=R2) revealAt[i]=3.4 + (R2?i/R2:0)*1.1;
  else if(i<=EXIT) revealAt[i]=6.4 + (i-R2)*0.28;
  else if(i===FAIL) revealAt[i]=8.6;
  else revealAt[i]=15.8 + (i-(FAIL+1))*(2.1/Math.max(1,N-1-(FAIL+1)));
}

// ---- geometry ----
const INW=884, INH=912, HEADER=96, PX0=76, PY0=HEADER+8, PLOTH=INH-PY0-18;
let lo=Math.min(...C.map(c=>c.l)), hi=Math.max(...C.map(c=>c.h), SL);
const pad=(hi-lo)*0.06; lo-=pad; hi+=pad;
const AXW=48, PROFW=118, GAP=12, CAX1=INW-AXW-PROFW-GAP-8, CAW=CAX1-PX0;
const yP=p=>PY0+(hi-p)/(hi-lo)*PLOTH;
const slot=CAW/N, BW=Math.min(slot*0.58,22);
const xi=i=>PX0+(i+0.5)*slot;
// "nice" round price ticks for a TradingView-style axis
function niceStep(raw){const p=Math.pow(10,Math.floor(Math.log10(raw)));const n=raw/p;return (n<1.5?1:n<3?2:n<7?5:10)*p;}
const TICKS=(()=>{const step=niceStep((hi-lo)/6);const out=[];for(let v=Math.ceil(lo/step)*step; v<=hi; v+=step)out.push(+v.toFixed(2));return out;})();
const lastRevealed=t=>{let k=0;for(let i=0;i<N;i++)if(t>=revealAt[i])k=i;return k;};

// ---- camera ----
const CEN={full:[INW/2,PY0+PLOTH/2,1], exit:[xi(EXIT),yP(EXITHI-1),1.15],
  ret:[xi(EXIT)+(FAIL-EXIT)*slot/2, yP((EXITHI+ENTRY)/2), 1.12]};
function cam(t){let a,b,x=0;
  if(t<6.5)a=b=CEN.full;
  else if(t<7.3){a=CEN.full;b=CEN.exit;x=seg(t,6.5,7.3);}
  else if(t<8.3)a=b=CEN.exit;
  else if(t<9.1){a=CEN.exit;b=CEN.ret;x=seg(t,8.3,9.1);}
  else if(t<15.7)a=b=CEN.ret;
  else if(t<18.2){a=CEN.ret;b=CEN.full;x=seg(t,15.7,18.2);}
  else a=b=CEN.full;
  const cx=lerp(a[0],b[0],x),cy=lerp(a[1],b[1],x),s=lerp(a[2],b[2],x);
  return {tx:INW/2-s*cx, ty:(PY0+PLOTH/2)-s*cy, s};
}

const CY='#2FC6C6',STEEL='#90A7AF',AMBER='#E0A458',RED='#DF7573',TGT='#57C7A6',WHITE='#EAF2F3',MUT='#7E97A0';
function line(p,col,on){ if(on<=0)return '';const y=yP(p);
  return `<line x1="${PX0}" y1="${y.toFixed(1)}" x2="${INW-AXW}" y2="${y.toFixed(1)}" stroke="${col}" stroke-width="4.5" opacity="${on}"/>`; }
// price-axis chip pinned to the screen (survives camera zoom/pan) — Latin, no RTL
function pchip(scrY,lab,price,col,on){ if(on<=0||scrY<PY0-18||scrY>INH-4)return '';
  return `<rect x="4" y="${(scrY-15).toFixed(1)}" rx="6" width="132" height="30" fill="${col}" opacity="${on}"/>`+
    `<text x="13" y="${(scrY+6).toFixed(1)}" font-size="19" font-weight="700" fill="#08222b" font-family="Plex" direction="ltr" text-anchor="start">${lab}</text>`+
    `<text x="130" y="${(scrY+6).toFixed(1)}" font-size="18" font-weight="700" fill="#08222b" font-family="Plex" direction="ltr" text-anchor="end">${fmtP(price)}</text>`; }
function chartSVG(t){
  const cm=cam(t), reveal=i=>fade(t,revealAt[i],0.22);
  const scrY=p=>cm.ty+cm.s*yP(p);
  const dim=seg(t,10.2,10.6)*(1-seg(t,15.5,15.9));
  let g='';
  TICKS.forEach(p=>{const y=yP(p);g+=`<line x1="${PX0}" y1="${y.toFixed(1)}" x2="${INW-AXW}" y2="${y.toFixed(1)}" stroke="#173039" stroke-width="1"/>`;});
  // fixed-range bracket
  const frOn=fade(t,3.5,0.4);
  if(frOn>0){const x1=xi(R1)-slot*0.4,x2=xi(R2)+slot*0.4,yb=PY0-2;
    g+=`<line x1="${x1}" y1="${yb}" x2="${x2}" y2="${yb}" stroke="${MUT}" stroke-width="3" opacity="${frOn}"/>`+
       `<line x1="${x1}" y1="${yb}" x2="${x1}" y2="${yb+12}" stroke="${MUT}" stroke-width="3" opacity="${frOn}"/>`+
       `<line x1="${x2}" y1="${yb}" x2="${x2}" y2="${yb+12}" stroke="${MUT}" stroke-width="3" opacity="${frOn}"/>`+
       `<text x="${((x1+x2)/2).toFixed(0)}" y="${yb-8}" font-size="19" fill="${MUT}" text-anchor="middle" font-family="Plex" direction="rtl" opacity="${frOn}">Fixed Range · نطاق الاحتساب</text>`;}
  // value-area shade
  const vaOn=fade(t,4.9,0.4);
  if(vaOn>0)g+=`<rect x="${PX0}" y="${yP(VAH).toFixed(1)}" width="${CAW}" height="${(yP(VAL)-yP(VAH)).toFixed(1)}" fill="${CY}" opacity="${0.05*vaOn}"/>`;
  // profile histogram (real volume, تقديري distribution)
  const pOn=fade(t,4.0,0.5), pr=D.profile.filter(x=>x.p>=lo&&x.p<=hi), pmax=Math.max(...pr.map(x=>x.v)), pxr=INW-AXW-6, bh=Math.max(4,PLOTH/((hi-lo)/0.5)-1);
  pr.forEach(x=>{const w=(x.v/pmax)*(PROFW-8);const inVA=x.p<=VAH&&x.p>=VAL;const col=Math.abs(x.p-POC)<0.26?AMBER:(inVA?CY:STEEL);
    g+=`<rect x="${(pxr-w).toFixed(1)}" y="${(yP(x.p)-bh/2).toFixed(1)}" width="${w.toFixed(1)}" height="${bh.toFixed(1)}" fill="${col}" opacity="${(col===AMBER?0.9:0.5)*pOn}" rx="2"/>`;});
  // level LINES (chips are drawn screen-pinned below)
  g+=line(VAH,CY,fade(t,4.9))+line(POC,AMBER,fade(t,5.4))+line(VAL,CY,fade(t,5.9));
  // SL band+line (above exit high)
  const slOn=fade(t,13.8,0.35);
  if(slOn>0){g+=`<rect x="${PX0}" y="${yP(SL).toFixed(1)}" width="${INW-AXW-PX0}" height="${(yP(EXITHI)-yP(SL)).toFixed(1)}" fill="${RED}" opacity="${0.20*slOn}"/>`+
    `<line x1="${PX0}" y1="${yP(SL).toFixed(1)}" x2="${INW-AXW}" y2="${yP(SL).toFixed(1)}" stroke="${RED}" stroke-width="2.5" opacity="${slOn}"/>`;}
  // candles
  for(let i=0;i<N;i++){const op=reveal(i); if(op<=0)continue;
    const c=C[i], bull=c.c>=c.o, col=bull?CY:STEEL, x=xi(i);
    const d=(i===EXIT||i===FAIL)?1:(1-0.55*dim), oo=op*d;
    g+=`<line x1="${x.toFixed(1)}" y1="${yP(c.h).toFixed(1)}" x2="${x.toFixed(1)}" y2="${yP(c.l).toFixed(1)}" stroke="${col}" stroke-width="2.4" opacity="${oo}"/>`;
    let yt=Math.min(yP(c.o),yP(c.c)),hh=Math.abs(yP(c.c)-yP(c.o)); if(hh<3)hh=3;
    g+=`<rect x="${(x-BW/2).toFixed(1)}" y="${yt.toFixed(1)}" width="${BW.toFixed(1)}" height="${hh.toFixed(1)}" fill="${col}" rx="2" opacity="${oo}"/>`;}
  // exit-high marker
  const exOn=fade(t,7.2,0.3);
  if(exOn>0){const x=xi(EXIT),y=yP(EXITHI),ly=yP(SL)-14;
    g+=`<line x1="${x.toFixed(1)}" y1="${y.toFixed(1)}" x2="${x.toFixed(1)}" y2="${(ly+6).toFixed(1)}" stroke="${WHITE}" stroke-width="1.4" opacity="${0.7*exOn}"/>`+
       `<circle cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" r="7" fill="${WHITE}" opacity="${exOn}"/>`+
       `<text x="${x.toFixed(1)}" y="${ly.toFixed(1)}" font-size="19" fill="${WHITE}" text-anchor="middle" font-family="Plex" direction="rtl" opacity="${exOn}">قمة الخروج · ${fmtP(EXITHI)}</text>`;}
  // fail frame
  const cbOn=fade(t,8.6,0.3)*(1-seg(t,17.8,18.2));
  if(cbOn>0){const x=xi(FAIL),c=C[FAIL];g+=`<rect x="${(x-BW/2-7).toFixed(1)}" y="${(yP(c.h)-6).toFixed(1)}" width="${BW+14}" height="${(yP(c.l)-yP(c.h)+12).toFixed(1)}" fill="none" stroke="${WHITE}" stroke-width="2.2" rx="6" opacity="${cbOn}"/>`;}
  // entry
  const enOn=fade(t,11.9,0.3);
  if(enOn>0){const x=xi(FAIL),y=yP(ENTRY),cw2=200,cxr=x-14;
    g+=`<line x1="${PX0}" y1="${y.toFixed(1)}" x2="${CAX1}" y2="${y.toFixed(1)}" stroke="${WHITE}" stroke-width="1.6" stroke-dasharray="2 6" opacity="${0.8*enOn}"/>`+
       `<circle cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" r="6" fill="${WHITE}" opacity="${enOn}"/>`+
       `<rect x="${(cxr-cw2).toFixed(1)}" y="${(y+8).toFixed(1)}" rx="7" width="${cw2}" height="32" fill="#0c2731" stroke="${WHITE}" stroke-width="1" opacity="${enOn}"/>`+
       `<text x="${(cxr-cw2/2).toFixed(0)}" y="${(y+30).toFixed(1)}" font-size="18" fill="${WHITE}" text-anchor="middle" font-family="Plex" direction="rtl" opacity="${enOn}">دخول تعليمي · ${fmtP(ENTRY)}</text>`;}
  // target dots
  const pocOn=fade(t,16.2,0.3),valOn=fade(t,17.5,0.3);
  if(pocOn>0)g+=`<circle cx="${xi(POCI).toFixed(1)}" cy="${yP(POC).toFixed(1)}" r="6" fill="${AMBER}" opacity="${pocOn}"/>`;
  if(valOn>0)g+=`<circle cx="${xi(VALI).toFixed(1)}" cy="${yP(VAL).toFixed(1)}" r="6" fill="${TGT}" opacity="${valOn}"/>`;
  // static layer (outside camera): header + screen-pinned price chips
  const hOn=fade(t,2.0,0.4);
  let hd=`<text x="${INW/2}" y="30" font-size="23" font-weight="700" fill="#CFE0E4" text-anchor="middle" font-family="Plex" direction="rtl" unicode-bidi="plaintext" opacity="${hOn}">الذهب (GLD) · إطار يومي — إعادة رسم من بيانات سوق تاريخية</text>`+
    `<text x="${INW/2}" y="60" font-size="17" fill="#728b95" text-anchor="middle" font-family="Plex" direction="rtl" unicode-bidi="plaintext" opacity="${hOn}">المصدر: Alpha Vantage · Volume Profile تقديري · حجم يومي حقيقي · VA 70% · ${D.firstDate}→${D.lastDate}</text>`;
  // right price axis (TradingView-style): vertical rule + round-number ticks (screen-pinned)
  const axOn=fade(t,3.2,0.5), axX=INW-AXW;
  hd+=`<line x1="${axX}" y1="${PY0-4}" x2="${axX}" y2="${INH-8}" stroke="#20404a" stroke-width="1.5" opacity="${axOn}"/>`;
  TICKS.forEach(p=>{const y=cm.ty+cm.s*yP(p); if(y<PY0-2||y>INH-6)return;
    hd+=`<line x1="${axX}" y1="${y.toFixed(1)}" x2="${axX+5}" y2="${y.toFixed(1)}" stroke="#3a5a64" stroke-width="1.5" opacity="${axOn}"/>`+
      `<text x="${INW-4}" y="${(y+5).toFixed(1)}" font-size="17" fill="#8fa8b0" text-anchor="end" font-family="Plex" direction="ltr" opacity="${axOn}">${fmtP(p)}</text>`;});
  // live last-price tag on the axis (moves as candles reveal)
  const li=lastRevealed(t), lc=C[li], lpY=cm.ty+cm.s*yP(lc.c), up=lc.c>=lc.o, lpc=up?CY:STEEL;
  if(li>=0&&lpY>PY0-2&&lpY<INH-6&&fade(t,revealAt[0]||0,0.2)>0){
    hd+=`<line x1="${PX0}" y1="${lpY.toFixed(1)}" x2="${axX}" y2="${lpY.toFixed(1)}" stroke="${lpc}" stroke-width="1" stroke-dasharray="3 4" opacity="0.55"/>`+
      `<rect x="${axX+2}" y="${(lpY-13).toFixed(1)}" width="${AXW-4}" height="26" rx="4" fill="${lpc}"/>`+
      `<text x="${INW-4}" y="${(lpY+5).toFixed(1)}" font-size="16" font-weight="700" fill="#06222b" text-anchor="end" font-family="Plex" direction="ltr">${fmtP(lc.c)}</text>`;}
  hd+=pchip(scrY(VAH),'VAH',VAH,CY,fade(t,4.9))+pchip(scrY(POC),'POC',POC,AMBER,fade(t,5.4))+pchip(scrY(VAL),'VAL',VAL,CY,fade(t,5.9))+pchip(scrY(SL),'SL',SL,RED,fade(t,13.8,0.35));
  return `<svg viewBox="0 0 ${INW} ${INH}" width="${INW}" height="${INH}">`+
    `<g transform="translate(${cm.tx.toFixed(2)},${cm.ty.toFixed(2)}) scale(${cm.s.toFixed(4)})">${g}</g>${hd}</svg>`;
}

const T=[
 [0.00,0.70,'أقرب ظل يضرب ستوبك.',1],
 [0.70,1.80,'وين مكانه المنطقي؟',1],
 [1.80,3.30,'فوق بطلان الفكرة… مو فوق أي ظل.',0],
 [3.30,4.70,'المثال داخل رينج واضح.',0],
 [4.70,6.40,'VAH فوق · POC وسط · VAL تحت',0],
 [6.40,8.20,'السعر خرج فوق VAH',0],
 [8.20,10.20,'ثم رجع داخل منطقة القيمة',0],
 [10.20,11.70,'هذا فشل قبول… مو اختراق.',0],
 [11.70,13.60,'الدخول بعد تأكيد الرجوع',0],
 [13.60,15.70,'الستوب فوق قمة الخروج',0],
 [15.70,18.20,'الهدف الأول POC… ثم VAL',0],
 [18.20,20.00,'السياق يحدد الستوب، مو أقرب ظل.',0]
];
const curText=t=>{for(const s of T)if(t>=s[0]&&t<s[1])return s;return null;};
const gem=st=>`<svg viewBox="0 0 100 100" width="100%" height="100%"><g fill="none" stroke="${st}" stroke-width="4" stroke-linejoin="round"><path d="M50 6 L88 28 L88 72 L50 94 L12 72 L12 28 Z"/><path d="M50 6 L50 40 M12 28 L50 40 L88 28 M12 72 L50 40 L88 72 M50 40 L50 94"/><path d="M50 6 L30 22 L12 28 M50 6 L70 22 L88 28"/></g></svg>`;

window.buildStage=function(t){
  const lightA=seg(t,1.8,2.2);
  let html='';
  html+=`<div class="layer" style="background:radial-gradient(120% 80% at 50% 30%,#0a2230,#04121c 70%);opacity:${1-lightA}"></div>`;
  html+=`<div class="layer" style="background:linear-gradient(180deg,#F6F1E9,#EFE7DA);opacity:${lightA}"></div>`;
  if(lightA<1){
    const push=1+0.10*smooth(clamp((t-0.70)/1.0,0,1)), swept=fade(t,0.05,0.15);
    const hk=`<svg viewBox="0 0 1080 1200" width="1080" height="1200"><g transform="translate(540,640) scale(${push.toFixed(3)}) translate(-540,-640)">
      <line x1="540" y1="300" x2="540" y2="760" stroke="#2FC6C6" stroke-width="10"/>
      <rect x="486" y="560" width="108" height="200" rx="8" fill="#2FC6C6"/>
      <line x1="300" y1="330" x2="820" y2="330" stroke="#DF7573" stroke-width="6" stroke-dasharray="14 10" opacity="${swept}"/>
      <circle cx="540" cy="300" r="12" fill="#EAF2F3" opacity="${swept}"/>
      <text x="812" y="316" font-size="34" fill="#DF7573" text-anchor="end" font-family="Plex" direction="rtl" opacity="${swept}">ستوب</text></g></svg>`;
    html+=`<div class="layer hook" style="opacity:${1-lightA}"><div class="hookart">${hk}</div></div>`;
  }
  html+=`<div class="logo" style="opacity:${lightA}"><div class="gem">${gem('#12333f')}</div><div class="wm">LIQUIDITY STATE</div></div>`;
  const cardDim=(1-0.62*seg(t,18.3,18.7))*(1-0.5*seg(t,20.0,20.4));
  html+=`<div class="card" style="opacity:${(lightA*cardDim).toFixed(3)}">`+
    `<div class="chart">${lightA>0.02?chartSVG(t):''}</div></div>`;
  const s1=curText(t);
  if(s1){const isHook=s1[3]===1, col=lightA<0.5?'#EAF2F3':'#12333f';
    const op=isHook?1:fade(t,s1[0],0.18), size=isHook?96:64, yPos=lightA<0.5?980:372;
    html+=`<div class="maintext" style="top:${yPos}px;color:${col};opacity:${op};font-size:${size}px">${esc(s1[2])}</div>`;}
  const tOut=1-seg(t,17.9,18.2);
  const pocCard=fade(t,16.3,0.3)*tOut, valCard=fade(t,17.6,0.3)*tOut;
  if(lightA>0.5){
    if(pocCard>0)html+=`<div class="tcard" style="left:104px;top:1416px;opacity:${pocCard};border-color:#E0A458"><b style="color:#b57518">الهدف ١ · POC ${fmtP(POC)}</b><span>عودة إلى نقطة التحكم</span></div>`;
    if(valCard>0)html+=`<div class="tcard" style="left:104px;top:1498px;opacity:${valCard};border-color:#57C7A6"><b style="color:#2c8f77">الهدف ٢ · VAL ${fmtP(VAL)}</b><span>حد القيمة الأدنى</span></div>`;
  }
  const sumOn=fade(t,18.6,0.3)*(1-seg(t,19.8,20.1));
  if(sumOn>0){const items=['رينج واضح · قيمة 70%','فشل قبول فوق VAH','ستوب فوق قمة الخروج + هامش'];
    html+=`<div class="summary" style="opacity:${sumOn}">`+items.map((x,i)=>`<div class="srow"><span class="sn">${i+1}</span><span>${esc(x)}</span></div>`).join('')+`</div>`;}
  const ctaOn=fade(t,20.1,0.35);
  if(ctaOn>0){html+=`<div class="cta" style="opacity:${ctaOn}">`+
    `<div class="ctalogo"><div class="gem">${gem('#12333f')}</div></div>`+
    `<div class="ctamain">اكتب «<span>ستوب</span>» وخذ قائمة الفحص</div>`+
    `<div class="ctasub">احفظها قبل صفقتك الجاية</div>`+
    `<div class="ctasub">وأرسلها لمتداول يحطّ الستوب عشوائي</div>`+
    `<div class="handle">@liquidity.state</div></div>`;}
  return html;
};
window.__DUR=23.5;
})();
