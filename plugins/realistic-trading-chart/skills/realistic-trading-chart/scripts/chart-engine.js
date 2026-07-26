/* realistic-chart-engine — TradingView-style candlestick SVG for brand carousels.
   Generates deterministic realistic OHLC with an engineered structure, then
   renders it with a price grid, right price axis, volume, and clean annotations.
   No external deps. Brand palette baked in but overridable.                    */

'use strict';

function mulberry32(a){return function(){a|=0;a=a+0x6D2B79F5|0;let t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296;};}

const DEFAULTS = {
  width: 1000, height: 620,
  padL: 26, padR: 138, padT: 24, padB: 26,
  volFrac: 0.15,
  bull: '#2ECC9A', bear: '#E15A5A',
  grid: '#22434E', text: '#8BA3AB',
  bg: 'transparent', wickW: 1.6, seed: 7,
  base: 2348.0, n: 64,
  annotate: false,
};

/* Crafted close-path scenario: push up -> rollover -> equal-lows consolidation
   at the pool -> liquidity sweep (long wick below, close back above) -> impulse. */
function buildSeries(o){
  const rnd = mulberry32(o.seed);
  const g = (m,s)=> m + (rnd()*2-1)*s;
  const n = o.n, B = o.base;
  const P = B - 3.6;                                 // pool = equal-lows level
  const SWEEP = 41, EQ = new Set([28,32,36,39,40]);
  const lerp=(a,b,t)=>a+(b-a)*t;

  const cl = new Array(n);
  for(let i=0;i<n;i++){
    let v;
    if(i<=13)      v = lerp(B-1.0, B+4.2, i/13) + g(0,0.5);
    else if(i<=26) v = lerp(B+4.2, P+1.1, (i-13)/13) + g(0,0.45);
    else if(i<=40) v = P + 1.15 + Math.sin((i-27)*0.9)*0.8 + g(0,0.28);
    else if(i===SWEEP) v = P + 0.7;
    else           v = lerp(P+0.9, B+10.5, (i-42)/(n-1-42)) + g(0,0.55);
    cl[i]=v;
  }

  const c=[];
  for(let i=0;i<n;i++){
    const open = i===0 ? B-1.4 : c[i-1].close;
    const close = cl[i];
    let upW = Math.abs(g(0.28,0.22)), dnW = Math.abs(g(0.28,0.22));
    let low  = Math.min(open,close) - dnW;
    let high = Math.max(open,close) + upW;
    if(EQ.has(i)) low = P + g(0.02,0.05);
    if(i===SWEEP){ low = P - 3.15 + g(0,0.2); high = Math.max(open,close)+Math.abs(g(0.25,0.15)); }
    low = Math.min(low, open, close); high = Math.max(high, open, close);
    let vol = 0.5 + Math.abs(close-open)*0.7 + rnd()*0.3;
    if(i>=42 && i<52) vol *= 1.55;
    if(i===SWEEP) vol *= 2.0;
    c.push({open,close,low,high,vol});
  }
  return { candles:c, pool:P, sweepIndex:SWEEP };
}

function niceStep(range, target){
  const raw = range/target;
  const pow = Math.pow(10, Math.floor(Math.log10(raw)));
  const cands = [1,2,2.5,5,10].map(m=>m*pow);
  return cands.find(s=>s>=raw) || cands[cands.length-1];
}

function chartSVG(opts={}){
  const o = {...DEFAULTS, ...opts};
  const {candles, pool, sweepIndex} = buildSeries(o);
  const n = candles.length;

  const plotT=o.padT, plotB=o.height-o.padB, plotH=plotB-plotT;
  const priceH=plotH*(1-o.volFrac);
  const volTop=plotT+priceH+12, volH=plotH*o.volFrac-12;
  const plotL=o.padL, plotR=o.width-o.padR, plotW=plotR-plotL;

  let lo=Infinity, hi=-Infinity, vmax=0;
  for(const k of candles){ lo=Math.min(lo,k.low); hi=Math.max(hi,k.high); vmax=Math.max(vmax,k.vol);}
  const pd=(hi-lo)*0.07; lo-=pd; hi+=pd;
  const Y=p=>plotT+(hi-p)/(hi-lo)*priceH;
  const slot=plotW/n, bw=slot*0.62, X=i=>plotL+slot*(i+0.5);

  const P=[];
  // grid + right price axis
  const step=niceStep(hi-lo,6); let g0=Math.ceil(lo/step)*step;
  for(let p=g0;p<hi;p+=step){ const y=Y(p);
    P.push(`<line x1="${plotL}" y1="${y.toFixed(1)}" x2="${plotR}" y2="${y.toFixed(1)}" stroke="${o.grid}" stroke-width="1" opacity="0.5"/>`);
    P.push(`<text x="${plotR+12}" y="${(y+6).toFixed(1)}" fill="${o.text}" font-size="18" font-family="Tajawal,sans-serif" font-weight="500">${p.toFixed(2)}</text>`);
  }
  for(let i=8;i<n;i+=12){ const x=X(i);
    P.push(`<line x1="${x.toFixed(1)}" y1="${plotT}" x2="${x.toFixed(1)}" y2="${plotB}" stroke="${o.grid}" stroke-width="1" opacity="0.3"/>`);
  }
  // volume
  for(let i=0;i<n;i++){ const k=candles[i], up=k.close>=k.open, h=(k.vol/vmax)*volH, x=X(i)-bw/2;
    P.push(`<rect x="${x.toFixed(1)}" y="${(volTop+volH-h).toFixed(1)}" width="${bw.toFixed(1)}" height="${Math.max(h,1).toFixed(1)}" fill="${up?o.bull:o.bear}" opacity="0.2"/>`);
  }
  // liquidity line at the pool (equal lows)
  const yPool=Y(pool);
  P.push(`<line x1="${plotL}" y1="${yPool.toFixed(1)}" x2="${plotR}" y2="${yPool.toFixed(1)}" stroke="#CBD7DB" stroke-width="1.5" stroke-dasharray="7 6" opacity="0.85"/>`);
  P.push(`<rect x="${plotR}" y="${(yPool-15).toFixed(1)}" width="126" height="30" rx="5" fill="#3A2A2C"/>`);
  P.push(`<text x="${(plotR+63).toFixed(1)}" y="${(yPool+6).toFixed(1)}" fill="#F2C6C6" font-size="18" font-family="Tajawal,sans-serif" font-weight="700" text-anchor="middle">${pool.toFixed(2)}</text>`);
  // candles
  for(let i=0;i<n;i++){ const k=candles[i], up=k.close>=k.open, col=up?o.bull:o.bear, x=X(i);
    const yO=Y(k.open), yC=Y(k.close), yH=Y(k.high), yL=Y(k.low), top=Math.min(yO,yC), h=Math.max(Math.abs(yC-yO),1.4);
    P.push(`<line x1="${x.toFixed(1)}" y1="${yH.toFixed(1)}" x2="${x.toFixed(1)}" y2="${yL.toFixed(1)}" stroke="${col}" stroke-width="${o.wickW}"/>`);
    P.push(`<rect x="${(x-bw/2).toFixed(1)}" y="${top.toFixed(1)}" width="${bw.toFixed(1)}" height="${h.toFixed(1)}" fill="${col}" rx="1"/>`);
  }
  // last price tag
  const last=candles[n-1], yl=Y(last.close);
  P.push(`<line x1="${plotL}" y1="${yl.toFixed(1)}" x2="${plotR}" y2="${yl.toFixed(1)}" stroke="${o.bull}" stroke-width="1" stroke-dasharray="3 4" opacity="0.7"/>`);
  P.push(`<rect x="${plotR}" y="${(yl-16).toFixed(1)}" width="126" height="32" rx="5" fill="${o.bull}"/>`);
  P.push(`<text x="${(plotR+63).toFixed(1)}" y="${(yl+6).toFixed(1)}" fill="#06231B" font-size="19" font-family="Tajawal,sans-serif" font-weight="800" text-anchor="middle">${last.close.toFixed(2)}</text>`);

  // clean annotations (TradingView-style), optional
  if(o.annotate){
    const sx=X(sweepIndex), sy=Y(candles[sweepIndex].low);
    // marker at sweep low
    P.push(`<circle cx="${sx.toFixed(1)}" cy="${sy.toFixed(1)}" r="7" fill="none" stroke="${o.bear}" stroke-width="2.5"/>`);
    // "Sweep" pill to the LEFT of the low (clear space below the line), with connector
    const pillW=150, pxR=sx-26, pxL=pxR-pillW, pcy=sy;
    P.push(`<line x1="${(sx-8).toFixed(1)}" y1="${sy.toFixed(1)}" x2="${(pxR).toFixed(1)}" y2="${pcy.toFixed(1)}" stroke="${o.bear}" stroke-width="1.4" opacity="0.7"/>`);
    P.push(`<rect x="${pxL.toFixed(1)}" y="${(pcy-18).toFixed(1)}" width="${pillW}" height="36" rx="9" fill="#2A1315" stroke="${o.bear}" stroke-width="1.4"/>`);
    P.push(`<text x="${(pxL+pillW/2).toFixed(1)}" y="${(pcy+6).toFixed(1)}" fill="#F2C6C6" font-size="19" font-family="Tajawal,sans-serif" font-weight="700" text-anchor="middle">سحب السيولة ↓</text>`);
    // "liquidity" tag on the dashed line (left side, above line)
    P.push(`<rect x="${(plotL+8).toFixed(1)}" y="${(yPool-40).toFixed(1)}" width="150" height="32" rx="8" fill="#14303A" stroke="#2E4A54" stroke-width="1.2"/>`);
    P.push(`<text x="${(plotL+83).toFixed(1)}" y="${(yPool-18).toFixed(1)}" fill="#B9CBD1" font-size="18" font-family="Tajawal,sans-serif" font-weight="700" text-anchor="middle">سيولة (استوبات)</text>`);
  }

  const svg=`<svg viewBox="0 0 ${o.width} ${o.height}" width="100%" height="100%" preserveAspectRatio="xMidYMid meet" xmlns="http://www.w3.org/2000/svg">${o.bg!=='transparent'?`<rect width="${o.width}" height="${o.height}" fill="${o.bg}"/>`:''}${P.join('')}</svg>`;
  return { svg, meta:{ pool, last:last.close, sweepIndex } };
}

module.exports = { chartSVG, buildSeries };

if(require.main===module){
  const fs=require('fs');
  const { svg } = chartSVG({ width:1000, height:620, bg:'#12262E', annotate:true, seed:Number(process.argv[2]||7) });
  fs.writeFileSync('chart-test.html', `<!doctype html><meta charset=utf8><body style="margin:0;background:#12262E">${svg}</body>`);
  console.log('wrote chart-test.html');
}
