/* Liquidity State — VP stop-placement reel. Deterministic scene: buildStage(t) → HTML for #stage.
   Educational schematic (رسم توضيحي): no real XAUUSD prices, no R values. */
(function(){
const W=1080,H=1920;
// ---------- helpers ----------
const clamp=(v,a,b)=>Math.max(a,Math.min(b,v));
const lerp=(a,b,x)=>a+(b-a)*x;
const smooth=x=>{x=clamp(x,0,1);return x*x*(3-2*x);};
const seg=(t,a,b)=>smooth((t-a)/(b-a));        // 0..1 ramp between a and b
const fade=(t,a,d=0.2)=>clamp((t-a)/d,0,1);    // fade-in after a over d
const esc=s=>String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');

// ---------- data (schematic) ----------
const C=[ // o,h,l,c
 [102,103,101,102],[102,105,101,104],[104,106,103,105],[105,107,104,106],[106,108,105,107],
 [107,108,105,106],[106,107,104,105],[105,106,103,104],[104,106,103,105],[105,108,104,107],
 [107,109,106,108],  // 10 tests VAH
 [108,112,108,111],  // 11 EXIT above VAH (high=112 exit-high)
 [111,111,105,106],  // 12 fails, closes back inside value
 [106,107,104,105],  // 13 return confirmation (below VAH)
 [105,105,103,104],  // 14 to POC
 [104,104,101,102],  // 15 toward VAL
 [102,102,100,100]   // 16 at VAL
];
const N=C.length;
const VAH=108,POC=104,VAL=100,EXITHI=112,ENTRY=105,SLTOP=113.0,SLBOT=112.0;
const revealAt=[]; for(let i=0;i<=10;i++)revealAt[i]=3.4+i*(1.2/10);
revealAt[11]=6.7; revealAt[12]=8.5; revealAt[13]=11.9; revealAt[14]=16.1; revealAt[15]=16.8; revealAt[16]=17.5;

// ---------- chart geometry (card-inner coords) ----------
const INW=884, INH=912;
const HEADER=64, PX0=74, PY0=HEADER+8, PLOTH=INH-PY0-18;
const PROFW=168, GAP=16, CAX1=INW-PROFW-GAP-8, CAW=CAX1-PX0;
const lo=98.5, hi=113.5;
const yP=p=>PY0+(hi-p)/(hi-lo)*PLOTH;
const slot=CAW/N, BW=20;
const xi=i=>PX0+(i+0.5)*slot;

// ---------- camera ----------
const CEN={full:[INW/2,PY0+PLOTH/2,1], exit:[xi(11),yP(110.5),1.16], ret:[xi(12)+slot/2,yP(108.7),1.12]};
function cam(t){
  let a=CEN.full,b=CEN.full,x=0;
  if(t<6.5){a=b=CEN.full;}
  else if(t<7.3){a=CEN.full;b=CEN.exit;x=seg(t,6.5,7.3);}
  else if(t<8.3){a=b=CEN.exit;}
  else if(t<9.1){a=CEN.exit;b=CEN.ret;x=seg(t,8.3,9.1);}
  else if(t<15.7){a=b=CEN.ret;}
  else if(t<18.2){a=CEN.ret;b=CEN.full;x=seg(t,15.7,18.2);}
  else {a=b=CEN.full;}
  const cx=lerp(a[0],b[0],x),cy=lerp(a[1],b[1],x),s=lerp(a[2],b[2],x);
  return {tx:INW/2 - s*cx, ty:(PY0+PLOTH/2) - s*cy, s};
}

// ---------- chart svg ----------
const CY='#2FC6C6', STEEL='#90A7AF', AMBER='#E0A458', RED='#DF7573', TGT='#57C7A6', WHITE='#EAF2F3', MUT='#7E97A0';
function levelLine(p,label,ar,col,on){
  if(on<=0)return '';
  const y=yP(p);
  let s=`<line x1="${PX0}" y1="${y.toFixed(1)}" x2="${CAX1}" y2="${y.toFixed(1)}" stroke="${col}" stroke-width="5" stroke-dasharray="${label==='POC'?'0':'2 0'}" opacity="${on}"/>`;
  s+=`<rect x="6" y="${(y-16).toFixed(1)}" rx="6" width="60" height="32" fill="${col}" opacity="${on}"/>`;
  s+=`<text x="36" y="${(y+7).toFixed(1)}" font-size="21" font-weight="700" fill="#08222b" text-anchor="middle" font-family="Plex" opacity="${on}">${label}</text>`;
  s+=`<text x="${CAX1-6}" y="${(y-11).toFixed(1)}" font-size="19" fill="${col}" text-anchor="end" font-family="Plex" direction="rtl" opacity="${on}">${ar}</text>`;
  return s;
}
function chartSVG(t){
  const cm=cam(t);
  const reveal=(i)=>fade(t,revealAt[i],0.22);
  const dim=seg(t,10.2,10.6)*(1-seg(t,15.5,15.9)); // dim others 10.2..15.7
  let g='';
  // grid
  for(let k=0;k<=4;k++){const y=PY0+PLOTH*k/4;g+=`<line x1="${PX0}" y1="${y}" x2="${CAX1}" y2="${y}" stroke="#1d3a44" stroke-width="1"/>`;}
  // fixed-range bracket (c0..c10)
  const frOn=fade(t,3.5,0.4);
  if(frOn>0){const x1=xi(0)-slot*0.4,x2=xi(10)+slot*0.4,yb=PY0-2;
    g+=`<line x1="${x1}" y1="${yb}" x2="${x2}" y2="${yb}" stroke="${MUT}" stroke-width="3" opacity="${frOn}"/>`+
       `<line x1="${x1}" y1="${yb}" x2="${x1}" y2="${yb+12}" stroke="${MUT}" stroke-width="3" opacity="${frOn}"/>`+
       `<line x1="${x2}" y1="${yb}" x2="${x2}" y2="${yb+12}" stroke="${MUT}" stroke-width="3" opacity="${frOn}"/>`+
       `<text x="${((x1+x2)/2).toFixed(0)}" y="${yb-8}" font-size="20" fill="${MUT}" text-anchor="middle" font-family="Plex" direction="rtl" opacity="${frOn}">Fixed Range · نطاق الاحتساب</text>`;}
  // value-area shade
  const vaOn=fade(t,4.9,0.4);
  if(vaOn>0)g+=`<rect x="${PX0}" y="${yP(VAH).toFixed(1)}" width="${CAW}" height="${(yP(VAL)-yP(VAH)).toFixed(1)}" fill="${CY}" opacity="${0.05*vaOn}"/>`;
  // profile histogram (illustrative), computed over range c0..c10
  const prof=[[100,10],[101,16],[102,26],[103,40],[104,58],[105,44],[106,34],[107,40],[108,30],[109,16],[110,9],[111,7],[112,6]];
  const pOn=fade(t,4.0,0.5), pmax=58, pxr=INW-6;
  prof.forEach(([p,v])=>{const w=(v/pmax)*(PROFW-10);const col=p===POC?AMBER:(p<=VAH&&p>=VAL?CY:STEEL);
    g+=`<rect x="${(pxr-w).toFixed(1)}" y="${(yP(p)-10).toFixed(1)}" width="${w.toFixed(1)}" height="18" fill="${col}" opacity="${(p===POC?0.85:0.5)*pOn}" rx="3"/>`;});
  // levels sequential
  g+=levelLine(VAH,'VAH','قمة القيمة',CY,fade(t,4.9));
  g+=levelLine(POC,'POC','نقطة التحكم',AMBER,fade(t,5.4));
  g+=levelLine(VAL,'VAL','قاع القيمة',CY,fade(t,5.9));
  // SL band
  const slOn=fade(t,13.8,0.35);
  if(slOn>0){g+=`<rect x="${PX0}" y="${yP(SLTOP).toFixed(1)}" width="${CAW}" height="${(yP(SLBOT)-yP(SLTOP)).toFixed(1)}" fill="${RED}" opacity="${0.22*slOn}"/>`+
    `<line x1="${PX0}" y1="${yP(SLBOT).toFixed(1)}" x2="${CAX1}" y2="${yP(SLBOT).toFixed(1)}" stroke="${RED}" stroke-width="3" opacity="${slOn}"/>`;}
  // candles
  for(let i=0;i<N;i++){const op=reveal(i); if(op<=0)continue;
    const [o,h,l,c]=C[i], bull=c>=o, col=bull?CY:STEEL, x=xi(i);
    let d=(i===11||i===12)?1:(1-0.55*dim); const oo=op*d;
    g+=`<line x1="${x.toFixed(1)}" y1="${yP(h).toFixed(1)}" x2="${x.toFixed(1)}" y2="${yP(l).toFixed(1)}" stroke="${col}" stroke-width="2.6" opacity="${oo}"/>`;
    let yt=Math.min(yP(o),yP(c)),hh=Math.abs(yP(c)-yP(o)); if(hh<3)hh=3;
    g+=`<rect x="${(x-BW/2).toFixed(1)}" y="${yt.toFixed(1)}" width="${BW}" height="${hh.toFixed(1)}" fill="${col}" rx="2" opacity="${oo}"/>`;}
  // exit-high marker (label raised above SL band)
  const exOn=fade(t,7.2,0.3);
  if(exOn>0){const x=xi(11),y=yP(EXITHI),ly=yP(SLTOP)-14;
    g+=`<line x1="${x.toFixed(1)}" y1="${y.toFixed(1)}" x2="${x.toFixed(1)}" y2="${(ly+6).toFixed(1)}" stroke="${WHITE}" stroke-width="1.4" opacity="${0.7*exOn}"/>`+
       `<circle cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" r="7" fill="${WHITE}" opacity="${exOn}"/>`+
       `<text x="${x.toFixed(1)}" y="${ly.toFixed(1)}" font-size="20" fill="${WHITE}" text-anchor="middle" font-family="Plex" direction="rtl" opacity="${exOn}">قمة الخروج</text>`;}
  // close-back frame (c12)
  const cbOn=fade(t,8.6,0.3)*(1-seg(t,17.8,18.2));
  if(cbOn>0){const x=xi(12);g+=`<rect x="${(x-BW/2-7).toFixed(1)}" y="${(yP(111)-6).toFixed(1)}" width="${BW+14}" height="${(yP(105)-yP(111)+12).toFixed(1)}" fill="none" stroke="${WHITE}" stroke-width="2.4" rx="6" opacity="${cbOn}"/>`;}
  // entry
  const enOn=fade(t,11.9,0.3);
  if(enOn>0){const x=xi(13),y=yP(ENTRY),cw2=176,cxr=x-14;
    g+=`<line x1="${PX0}" y1="${y.toFixed(1)}" x2="${CAX1}" y2="${y.toFixed(1)}" stroke="${WHITE}" stroke-width="1.6" stroke-dasharray="2 6" opacity="${0.8*enOn}"/>`+
       `<circle cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" r="6" fill="${WHITE}" opacity="${enOn}"/>`+
       `<rect x="${(cxr-cw2).toFixed(1)}" y="${(y+8).toFixed(1)}" rx="7" width="${cw2}" height="32" fill="#0c2731" stroke="${WHITE}" stroke-width="1" opacity="${enOn}"/>`+
       `<text x="${(cxr-cw2/2).toFixed(0)}" y="${(y+30).toFixed(1)}" font-size="19" fill="${WHITE}" text-anchor="middle" font-family="Plex" direction="rtl" opacity="${enOn}">دخول بعد الرجوع</text>`;}
  // target markers
  const pocOn=fade(t,16.3,0.3), valOn=fade(t,17.6,0.3);
  if(pocOn>0){const x=xi(14);g+=`<circle cx="${x.toFixed(1)}" cy="${yP(POC).toFixed(1)}" r="6" fill="${AMBER}" opacity="${pocOn}"/>`;}
  if(valOn>0){const x=xi(16);g+=`<circle cx="${x.toFixed(1)}" cy="${yP(VAL).toFixed(1)}" r="6" fill="${TGT}" opacity="${valOn}"/>`;}
  return `<svg viewBox="0 0 ${INW} ${INH}" width="${INW}" height="${INH}"><defs></defs>`+
         `<g transform="translate(${cm.tx.toFixed(2)},${cm.ty.toFixed(2)}) scale(${cm.s.toFixed(4)})">${g}</g></svg>`;
}

// ---------- text timeline ----------
const T=[
 [0.00,0.70,'أقرب ظل يضرب ستوبك.','',1],
 [0.70,1.80,'وين مكانه المنطقي؟','',1],
 [1.80,3.30,'فوق بطلان الفكرة… مو فوق أي ظل.','',0],
 [3.30,4.70,'وهذا المثال داخل رينج واضح.','',0],
 [4.70,6.40,'VAH فوق · POC وسط · VAL تحت','',0],
 [6.40,8.20,'السعر خرج فوق VAH','',0],
 [8.20,10.20,'ثم أغلق داخل منطقة القيمة','',0],
 [10.20,11.70,'هذا فشل قبول… مو اختراق.','',0],
 [11.70,13.60,'الدخول بعد تأكيد الرجوع','',0],
 [13.60,15.70,'الستوب فوق قمة الخروج','',0],
 [15.70,18.20,'الهدف الأول POC… ثم VAL','',0],
 [18.20,20.00,'السياق يحدد الستوب، مو أقرب ظل.','',0]
];
function curText(t){for(const s of T)if(t>=s[0]&&t<s[1])return s;return null;}

// ---------- gem logo ----------
const gem=(stroke)=>`<svg viewBox="0 0 100 100" width="100%" height="100%"><g fill="none" stroke="${stroke}" stroke-width="4" stroke-linejoin="round"><path d="M50 6 L88 28 L88 72 L50 94 L12 72 L12 28 Z"/><path d="M50 6 L50 40 M12 28 L50 40 L88 28 M12 72 L50 40 L88 72 M50 40 L50 94"/><path d="M50 6 L30 22 L12 28 M50 6 L70 22 L88 28"/></g></svg>`;

// ---------- stage builder ----------
window.buildStage=function(t){
  const lightA = seg(t,1.8,2.2);            // 0 navy → 1 light
  let html='';
  // backgrounds
  html+=`<div class="layer" style="background:radial-gradient(120% 80% at 50% 30%,#0a2230,#04121c 70%);opacity:${1-lightA}"></div>`;
  html+=`<div class="layer" style="background:linear-gradient(180deg,#F6F1E9,#EFE7DA);opacity:${lightA}"></div>`;

  // ===== HOOK phase (navy) =====
  if(lightA<1){
    const push=1+0.10*smooth(clamp((t-0.70)/1.0,0,1)); // push-in during 0.7..1.7
    const swept=fade(t,0.05,0.15);
    // close-up: one candle with long upper wick + stop line getting swept
    const hk=`<svg viewBox="0 0 1080 1200" width="1080" height="1200">
      <g transform="translate(540,640) scale(${push.toFixed(3)}) translate(-540,-640)">
      <line x1="540" y1="300" x2="540" y2="760" stroke="#2FC6C6" stroke-width="10"/>
      <rect x="486" y="560" width="108" height="200" rx="8" fill="#2FC6C6"/>
      <line x1="300" y1="330" x2="820" y2="330" stroke="#DF7573" stroke-width="6" stroke-dasharray="14 10" opacity="${swept}"/>
      <circle cx="540" cy="300" r="12" fill="#EAF2F3" opacity="${swept}"/>
      <text x="812" y="316" font-size="34" fill="#DF7573" text-anchor="end" font-family="Plex" direction="rtl" opacity="${swept}">ستوب</text>
      </g></svg>`;
    html+=`<div class="layer hook" style="opacity:${1-lightA}"><div class="hookart">${hk}</div></div>`;
  }

  // ===== LIGHT phase: logo + card =====
  // logo (fixed, top-center)
  html+=`<div class="logo" style="opacity:${lightA}"><div class="gem">${gem('#12333f')}</div><div class="wm">LIQUIDITY STATE</div></div>`;
  // card
  const cardOp=lightA;
  const cardDim=(1-0.62*seg(t,18.3,18.7))*(1-0.5*seg(t,20.0,20.4)); // dim under summary, then CTA
  html+=`<div class="card" style="opacity:${(cardOp*cardDim).toFixed(3)}">`+
        `<div class="cardhead"><span class="chl">Volume Profile — رسم توضيحي</span><span class="chr">مثال تعليمي · ليس توصية</span></div>`+
        `<div class="chart">${lightA>0.02?chartSVG(t):''}</div></div>`;

  // ===== main text (above card) =====
  const seg1=curText(t);
  if(seg1){
    const isHook = seg1[4]===1;
    const col = lightA<0.5 ? '#EAF2F3' : '#12333f';
    const op = (isHook?1:fade(t,seg1[0],0.18)) * (isHook? (1-0*lightA):1);
    const size = isHook?96:66;
    const yPos = lightA<0.5 ? 980 : 372;   // hook centered lower; teaching above card
    html+=`<div class="maintext" style="top:${yPos}px;color:${col};opacity:${op};font-size:${size}px">${esc(seg1[2])}</div>`;
  }

  // ===== target chips (activate individually, lower-left, gone before summary) =====
  const tOut=1-seg(t,17.9,18.2);
  const pocCard=fade(t,16.4,0.3)*tOut, valCard=fade(t,17.7,0.3)*tOut;
  if(lightA>0.5){
    if(pocCard>0)html+=`<div class="tcard" style="left:104px;top:1420px;opacity:${pocCard};border-color:#E0A458"><b style="color:#b57518">الهدف ١</b><span>POC · نقطة التحكم</span></div>`;
    if(valCard>0)html+=`<div class="tcard" style="left:104px;top:1502px;opacity:${valCard};border-color:#57C7A6"><b style="color:#2c8f77">الهدف ٢</b><span>VAL · قاع القيمة</span></div>`;
  }

  // ===== summary 3 points (18.4–20.0) — over dimmed chart =====
  const sumOn=fade(t,18.6,0.3)*(1-seg(t,19.8,20.1));
  if(sumOn>0){
    const items=['رينج واضح','فشل قبول خارج VAH','ستوب فوق قمة الخروج'];
    html+=`<div class="summary" style="opacity:${sumOn}">`+items.map((x,i)=>`<div class="srow"><span class="sn">${i+1}</span><span>${esc(x)}</span></div>`).join('')+`</div>`;
  }

  // ===== CTA (20.0–23.5) =====
  const ctaOn=fade(t,20.1,0.35);
  if(ctaOn>0){
    html+=`<div class="cta" style="opacity:${ctaOn}">`+
      `<div class="ctalogo"><div class="gem">${gem('#12333f')}</div></div>`+
      `<div class="ctamain">اكتب «<span>ستوب</span>» وخذ قائمة الفحص</div>`+
      `<div class="ctasub">احفظها قبل صفقتك الجاية</div>`+
      `<div class="ctasub">وأرسلها لمتداول يحطّ الستوب عشوائي</div>`+
      `<div class="handle">@liquidity.state</div>`+
      `</div>`;
  }
  return html;
};
window.__DUR=23.5;
})();
