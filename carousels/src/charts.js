// Liquidity State — SVG chart engine. All charts are educational illustrations.
const P = {
  BULL:'#20939E', BEAR:'#0B2635', RED:'#DF7573', GREEN:'#5FA05E',
  TEAL:'#257A93', MUTED:'#6A7B84', GRID:'#DCE6E8', AXIS:'#A7B9BF',
  HEAD:'#0B2635', ZONEB:'#20939E', LABELBG:'#0B2635'
};
const esc = s => String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
const f = n => Math.round(n*100)/100;
const cw = t => [...String(t)].reduce((a,ch)=>a+(/[A-Za-z0-9%+\-−]/.test(ch)?11:15),0)+24; // chip width estimate
// rounded label chip with RTL-safe, centered text (handles mixed Arabic+Latin)
const chip = (x,y,w,text,bg,fg='#fff',h=28)=>
  `<rect x="${f(x)}" y="${f(y)}" rx="6" width="${f(w)}" height="${h}" fill="${bg}"/>`+
  `<text x="${f(x+w/2)}" y="${f(y+h/2+6.5)}" font-size="18" font-weight="700" fill="${fg}" text-anchor="middle" font-family="Tajawal,InterLS,sans-serif" direction="rtl" unicode-bidi="plaintext">${esc(text)}</text>`;

function scaleY(min,max,padTop,plotH){
  return p => padTop + (max-p)/(max-min)*plotH;
}

// ---- candlestick chart with overlays ----
function candles(spec){
  const W = spec.w||920, H = spec.h||470;
  const padL = spec.padL??18, padR = spec.padR??84, padT = 20;
  const hasVol = !!spec.volume;
  const volH = hasVol ? 78 : 0;
  const plotH = H - padT - 34 - volH;
  const cs = spec.candles;
  let lo = Math.min(...cs.map(c=>c.l)), hi = Math.max(...cs.map(c=>c.h));
  (spec.levels||[]).forEach(l=>{lo=Math.min(lo,l.p);hi=Math.max(hi,l.p);});
  (spec.zones||[]).forEach(z=>{lo=Math.min(lo,z.p1,z.p2);hi=Math.max(hi,z.p1,z.p2);});
  (spec.vwap||[]).forEach(v=>{lo=Math.min(lo,v.p);hi=Math.max(hi,v.p);});
  const pad=(hi-lo)*0.10; lo-=pad; hi+=pad;
  const plotW = W - padL - padR;
  const n = cs.length, slot = plotW/n;
  const bw = Math.min(slot*0.56, 34);
  const y = scaleY(lo,hi,padT,plotH);
  const cx = i => padL + slot*(i+0.5);
  let s = `<svg viewBox="0 0 ${W} ${H}" width="100%" xmlns="http://www.w3.org/2000/svg" font-family="InterLS,Tajawal,sans-serif">`;
  // grid
  for(let g=0; g<=4; g++){ const yy=padT+plotH*g/4; s+=`<line x1="${padL}" y1="${f(yy)}" x2="${padL+plotW}" y2="${f(yy)}" stroke="${P.GRID}" stroke-width="1"/>`; }

  // zones (price bands across width)
  (spec.zones||[]).forEach(z=>{
    const y1=y(Math.max(z.p1,z.p2)), y2=y(Math.min(z.p1,z.p2));
    const col=z.color||P.ZONEB;
    s+=`<rect x="${padL}" y="${f(y1)}" width="${plotW}" height="${f(y2-y1)}" fill="${col}" fill-opacity="${z.fill??0.14}"/>`;
    if(z.label){ s+=chip(padL+6, f(y1)+6, cw(z.label), z.label, col); }
  });
  // boxes anchored to candle indices (FVG / OB precise)
  (spec.boxes||[]).forEach(b=>{
    const x1=padL+slot*b.i1, x2=padL+slot*(b.i2+1);
    const y1=y(Math.max(b.p1,b.p2)), y2=y(Math.min(b.p1,b.p2));
    const col=b.color||P.TEAL;
    s+=`<rect x="${f(x1)}" y="${f(y1)}" width="${f(x2-x1)}" height="${f(y2-y1)}" fill="${col}" fill-opacity="${b.fill??0.18}" stroke="${col}" stroke-width="1.5" stroke-dasharray="${b.dash||'0'}"/>`;
    if(b.label){ s+=`<text x="${f(x1)+8}" y="${f(y1)-8}" font-size="19" font-weight="700" fill="${col}" font-family="Tajawal,InterLS,sans-serif" direction="rtl" unicode-bidi="plaintext">${esc(b.label)}</text>`; }
  });
  // vwap / lines poly
  if(spec.vwap){ const pts=spec.vwap.map(v=>`${f(cx(v.i))},${f(y(v.p))}`).join(' ');
    s+=`<polyline points="${pts}" fill="none" stroke="${P.TEAL}" stroke-width="3" stroke-dasharray="2 0"/>`;
    const last=spec.vwap[spec.vwap.length-1];
    s+=chip(cx(last.i)+6, y(last.p)-15, 76, 'VWAP', P.TEAL,'#fff',30);
  }
  // horizontal levels — anchored to the candles that establish/consume them (never edge-to-edge).
  // Chips are queued and drawn AFTER the candles so markup never gets painted over (and never hides price).
  const chips=[];
  (spec.levels||[]).forEach(l=>{
    const yy=y(l.p), col=l.color||P.HEAD, dash=l.style==='solid'?'0':'7 6';
    const x1 = l.i1!=null ? padL+slot*l.i1 : padL;
    const x2 = l.i2!=null ? padL+slot*(l.i2+1) : padL+plotW;
    s+=`<line x1="${f(x1)}" y1="${f(yy)}" x2="${f(x2)}" y2="${f(yy)}" stroke="${col}" stroke-width="2" stroke-dasharray="${dash}"/>`;
    if(l.label){ const w=cw(l.label); const lx = l.side==='left'? Math.max(padL,x1) : Math.min(padL+plotW-w, x2-w);
      chips.push({x:lx,y:f(yy)-30,w,text:l.label,col}); }
  });

  // candles: wick then body
  cs.forEach((c,i)=>{
    const bull=c.c>=c.o, col=bull?P.BULL:P.BEAR, x=cx(i);
    s+=`<line x1="${f(x)}" y1="${f(y(c.h))}" x2="${f(x)}" y2="${f(y(c.l))}" stroke="${col}" stroke-width="2.4"/>`;
    const yo=y(c.o), yc=y(c.c); let top=Math.min(yo,yc), h=Math.abs(yc-yo); if(h<3)h=3;
    s+=`<rect x="${f(x-bw/2)}" y="${f(top)}" width="${f(bw)}" height="${f(h)}" fill="${col}" rx="2"/>`;
  });

  // markers: entry / sl / target
  (spec.markers||[]).forEach(m=>{
    const x=cx(m.i), yy=y(m.p);
    const map={entry:[P.TEAL,'دخول'],sl:[P.RED,'إبطال'],target:[P.GREEN,'هدف'],sweep:[P.RED,'سحب']};
    const [col,def]=map[m.type]||[P.HEAD,''];
    const lab=m.label??def;
    const mx1 = m.i1!=null ? padL+slot*m.i1 : padL;
    const mx2 = m.i2!=null ? padL+slot*(m.i2+1) : padL+plotW;
    s+=`<line x1="${f(mx1)}" y1="${f(yy)}" x2="${f(mx2)}" y2="${f(yy)}" stroke="${col}" stroke-width="1.6" stroke-dasharray="2 5" opacity="0.85"/>`;
    s+=`<circle cx="${f(x)}" cy="${f(yy)}" r="6.5" fill="${col}"/>`;
    const lx = m.side==='right'? Math.min(padL+plotW-cw(lab), mx2-cw(lab)) : Math.max(padL+2, mx1);
    chips.push({x:lx,y:f(yy)-30,w:cw(lab),text:lab,col});
  });
  // annotations (callout arrow)
  (spec.notes||[]).forEach(a=>{
    const x=cx(a.i), yy=y(a.p);
    const tx = a.tx ?? (x> W/2 ? x-8 : x+8);
    const ty = a.ty ?? (yy-46);
    const anchor = a.tx!=null ? (a.anchor||'end') : (x>W/2?'end':'start');
    s+=`<line x1="${f(x)}" y1="${f(yy)}" x2="${f(tx)}" y2="${f(ty)}" stroke="${P.MUTED}" stroke-width="1.6"/>`;
    s+=`<circle cx="${f(x)}" cy="${f(yy)}" r="4.5" fill="${P.MUTED}"/>`;
    s+=`<text x="${f(tx)}" y="${f(ty)-6}" font-size="20" font-weight="700" fill="${P.HEAD}" text-anchor="${anchor}" font-family="Tajawal,sans-serif" direction="rtl">${esc(a.text)}</text>`;
  });

  // markup chips last: resolve overlaps so no label covers another or the price action
  if(chips.length){
    chips.sort((a,b)=>a.y-b.y);
    for(let i=1;i<chips.length;i++){
      for(let j=0;j<i;j++){
        const a=chips[j],b=chips[i];
        const overlapX = b.x < a.x+a.w+8 && a.x < b.x+b.w+8;
        if(overlapX && Math.abs(b.y-a.y) < 32) b.y = a.y + 34;
      }
    }
    chips.forEach(c=>{ s+=chip(c.x, Math.max(2,Math.min(c.y, padT+plotH-30)), c.w, c.text, c.col); });
  }
  // volume sub-panel
  if(hasVol){
    const vy0 = padT+plotH+34, vmax=Math.max(...spec.volume.map(v=>v.v));
    s+=`<line x1="${padL}" y1="${f(vy0+volH)}" x2="${padL+plotW}" y2="${f(vy0+volH)}" stroke="${P.AXIS}" stroke-width="1"/>`;
    spec.volume.forEach((v,i)=>{
      const h=(v.v/vmax)*(volH-6), x=cx(i);
      const col=v.c!=null?(v.c?P.BULL:P.BEAR):(cs[i].c>=cs[i].o?P.BULL:P.BEAR);
      s+=`<rect x="${f(x-bw/2)}" y="${f(vy0+volH-h)}" width="${f(bw)}" height="${f(h)}" fill="${col}" fill-opacity="${v.hl?0.95:0.5}" rx="1.5"/>`;
    });
    s+=`<text x="${padL}" y="${f(vy0)+2}" font-size="17" fill="${P.MUTED}" font-family="Tajawal">Volume</text>`;
  }
  s+=`</svg>`; return s;
}

// ---- volume profile beside candles ----
function volProfile(spec){
  const W=920,H=470,padT=20,padR=250,padL=18; const plotH=H-padT-34;
  const cs=spec.candles; let lo=Math.min(...cs.map(c=>c.l)),hi=Math.max(...cs.map(c=>c.h));
  const pad=(hi-lo)*0.10; lo-=pad;hi+=pad;
  const plotW=W-padL-padR, n=cs.length, slot=plotW/n, bw=Math.min(slot*0.56,30);
  const y=scaleY(lo,hi,padT,plotH), cx=i=>padL+slot*(i+0.5);
  let s=`<svg viewBox="0 0 ${W} ${H}" width="100%" xmlns="http://www.w3.org/2000/svg" font-family="InterLS,Tajawal,sans-serif">`;
  for(let g=0;g<=4;g++){const yy=padT+plotH*g/4;s+=`<line x1="${padL}" y1="${f(yy)}" x2="${padL+plotW}" y2="${f(yy)}" stroke="${P.GRID}"/>`;}
  // value area shading
  if(spec.va){ const y1=y(spec.va.vah),y2=y(spec.va.val);
    s+=`<rect x="${padL}" y="${f(y1)}" width="${W-padL-8}" height="${f(y2-y1)}" fill="${P.TEAL}" fill-opacity="0.07"/>`;}
  // profile bars (right)
  const px0=W-padR+16, pmax=Math.max(...spec.profile.map(r=>r.v)), pw=padR-40;
  spec.profile.forEach(r=>{
    const yy=y(r.p), bh=Math.max(6,(hi-lo)/spec.profile.length/(hi-lo)*plotH-3);
    const w=(r.v/pmax)*pw, col=r.poc?P.RED:(r.hvn?P.TEAL:'#9DC0C7');
    s+=`<rect x="${f(px0)}" y="${f(yy-bh/2)}" width="${f(w)}" height="${f(bh)}" fill="${col}" fill-opacity="${r.poc?0.95:0.6}" rx="2"/>`;
  });
  // POC/VAH/VAL lines
  const marks=[]; if(spec.va){marks.push(['VAH',spec.va.vah,P.TEAL]);marks.push(['VAL',spec.va.val,P.TEAL]);}
  const poc=spec.profile.find(r=>r.poc); if(poc)marks.push(['POC',poc.p,P.RED]);
  const vchips=[];
  marks.forEach(([lab,p,col])=>{const yy=y(p);
    s+=`<line x1="${padL}" y1="${f(yy)}" x2="${W-8}" y2="${f(yy)}" stroke="${col}" stroke-width="2" stroke-dasharray="${lab==='POC'?'0':'7 6'}"/>`;
    vchips.push({y:f(yy)-28,lab,col});});
  cs.forEach((c,i)=>{const bull=c.c>=c.o,col=bull?P.BULL:P.BEAR,x=cx(i);
    s+=`<line x1="${f(x)}" y1="${f(y(c.h))}" x2="${f(x)}" y2="${f(y(c.l))}" stroke="${col}" stroke-width="2.2"/>`;
    const yo=y(c.o),yc=y(c.c);let top=Math.min(yo,yc),h=Math.abs(yc-yo);if(h<3)h=3;
    s+=`<rect x="${f(x-bw/2)}" y="${f(top)}" width="${f(bw)}" height="${f(h)}" fill="${col}" rx="2"/>`;});
  // level chips on top of the candles so markup stays readable (and never hidden by price)
  vchips.sort((a,b)=>a.y-b.y);
  for(let i=1;i<vchips.length;i++) if(vchips[i].y-vchips[i-1].y<30) vchips[i].y=vchips[i-1].y+30;
  vchips.forEach(c=>{s+=chip(padL+2,c.y,62,c.lab,c.col,'#fff',26);});
  (spec.notes||[]).forEach(a=>{const x=cx(a.i),yy=y(a.p);const tx=a.tx??x-8,ty=a.ty??yy-46;
    s+=`<line x1="${f(x)}" y1="${f(yy)}" x2="${f(tx)}" y2="${f(ty)}" stroke="${P.MUTED}" stroke-width="1.6"/><circle cx="${f(x)}" cy="${f(yy)}" r="4.5" fill="${P.MUTED}"/>`+
      `<text x="${f(tx)}" y="${f(ty)-6}" font-size="20" font-weight="700" fill="${P.HEAD}" text-anchor="${a.anchor||'end'}" font-family="Tajawal" direction="rtl">${esc(a.text)}</text>`;});
  s+=`</svg>`;return s;
}

// ---- footprint (numbers bars) ----
function footprint(spec){
  const cols=spec.cols; const W=920,H=486,padT=62,padL=26,deltaH=34,gap=10;
  const cw=(W-padL*2)/cols.length; const rows=cols[0].cells.length;
  const gridH=H-padT-deltaH-gap; const rh=gridH/rows;
  let s=`<svg viewBox="0 0 ${W} ${H}" width="100%" xmlns="http://www.w3.org/2000/svg" font-family="InterLS,sans-serif">`;
  s+=`<text x="${padL}" y="26" font-size="18" fill="${P.MUTED}" font-family="InterLS">Bid × Ask</text>`;
  cols.forEach((col,ci)=>{
    const x0=padL+ci*cw;
    // column label ABOVE grid
    s+=`<text x="${f(x0+cw/2)}" y="46" font-size="20" font-weight="700" fill="${P.HEAD}" text-anchor="middle" font-family="Tajawal" direction="rtl">${esc(col.label||'')}</text>`;
    col.cells.forEach((cell,ri)=>{
      const y0=padT+ri*rh;
      let bg='#F4F8F9', bcol=P.GRID;
      if(cell.imb==='ask'){bg='#DCEFE9';bcol=P.BULL;}
      if(cell.imb==='bid'){bg='#F8DEDD';bcol=P.RED;}
      if(cell.absorb){bg='#0B2635';bcol='#20939E';}
      s+=`<rect x="${f(x0+4)}" y="${f(y0+3)}" width="${f(cw-8)}" height="${f(rh-6)}" fill="${bg}" stroke="${bcol}" stroke-width="1.4" rx="7"/>`;
      const tc=cell.absorb?'#fff':P.HEAD;
      s+=`<text x="${f(x0+cw*0.30)}" y="${f(y0+rh/2+7)}" font-size="21" font-weight="700" fill="${cell.imb==='bid'?(cell.absorb?'#F19a99':P.RED):tc}" text-anchor="middle">${cell.bid}</text>`;
      s+=`<text x="${f(x0+cw*0.51)}" y="${f(y0+rh/2+6)}" font-size="16" fill="${cell.absorb?'#6f8a94':P.AXIS}" text-anchor="middle">×</text>`;
      s+=`<text x="${f(x0+cw*0.72)}" y="${f(y0+rh/2+7)}" font-size="21" font-weight="700" fill="${cell.imb==='ask'?P.BULL:tc}" text-anchor="middle">${cell.ask}</text>`;
    });
    // delta footer (below grid)
    if(col.delta!=null){const dc=col.delta>=0?P.BULL:P.RED; const dy=padT+gridH+gap;
      s+=`<rect x="${f(x0+4)}" y="${f(dy)}" width="${f(cw-8)}" height="${deltaH-4}" fill="${dc}" fill-opacity="0.14" stroke="${dc}" stroke-opacity="0.4" rx="7"/>`+
      `<text x="${f(x0+cw/2)}" y="${f(dy+21)}" font-size="18" font-weight="700" fill="${dc}" text-anchor="middle">Δ ${col.delta>0?'+':''}${col.delta}</text>`;}
  });
  s+=`</svg>`;return s;
}

export function renderChart(spec){
  if(!spec) return '';
  if(spec.type==='volprofile') return volProfile(spec);
  if(spec.type==='footprint') return footprint(spec);
  return candles(spec);
}
export const gemSVG = (fill='#F7FAFB',stroke='#20939E')=>`<svg viewBox="0 0 100 100" width="100%" height="100%" xmlns="http://www.w3.org/2000/svg"><g fill="none" stroke="${stroke}" stroke-width="3" stroke-linejoin="round"><path d="M50 6 L88 28 L88 72 L50 94 L12 72 L12 28 Z" fill="${fill}" fill-opacity="0.14"/><path d="M50 6 L50 40 M12 28 L50 40 L88 28 M12 72 L50 40 L88 72 M50 40 L50 94"/><path d="M50 6 L30 22 L12 28 M50 6 L70 22 L88 28"/></g></svg>`;
