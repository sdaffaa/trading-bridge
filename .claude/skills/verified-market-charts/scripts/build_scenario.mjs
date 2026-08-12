#!/usr/bin/env node
// Verified Volume-Profile scenario builder for Liquidity State charts.
// Reads a real OHLCV CSV, verifies integrity, builds a Fixed-Range Volume Profile,
// and finds a mathematically-valid "break above VAH -> failed acceptance -> rotate to POC then VAL".
// Usage:
//   node build_scenario.mjs --csv data/gld_daily.csv --out data/scenario.json \
//     --tick 0.5 --va 0.70 --symbol "GLD (SPDR Gold Shares)" --source "Alpha Vantage" \
//     --tf "يومي · 1D" --voltype "حجم بورصة حقيقي (NYSE Arca)"
// CSV header must be: timestamp,open,high,low,close,volume  (any date order; sorted ascending internally)
import fs from 'fs';
const arg=(k,d)=>{const i=process.argv.indexOf('--'+k);return i>=0?process.argv[i+1]:d;};
const CSV=arg('csv'), OUT=arg('out','scenario.json'), TICK=+arg('tick','0.5'), VA=+arg('va','0.70');
const PRE=+arg('pre','0'), POST=+arg('post','1');
const META={symbol:arg('symbol','—'),source:arg('source','—'),tf:arg('tf','—'),volType:arg('voltype','—')};
if(!CSV){console.error('need --csv');process.exit(1);}

const rows=fs.readFileSync(CSV,'utf8').trim().split('\n').slice(1)
  .map(l=>{const[t,o,h,lo,c,v]=l.trim().split(',');return{t,o:+o,h:+h,l:+lo,c:+c,v:+v};})
  .sort((a,b)=>a.t<b.t?-1:1);
const N=rows.length;

// 1) OHLC integrity
let bad=0;
rows.forEach(r=>{const okH=r.h>=r.o-1e-9&&r.h>=r.c-1e-9&&r.h>=r.l-1e-9, okL=r.l<=r.o+1e-9&&r.l<=r.c+1e-9;
  if(!(okH&&okL)){bad++;console.error('BAD OHLC',r.t);}});
if(bad){console.error(`ABORT: ${bad} invalid OHLC rows`);process.exit(2);}

// Volume Profile over rows[a..b] (volume spread uniformly across each bar's H-L range)
function vp(a,b){
  const bins=new Map();
  for(let i=a;i<=b;i++){const r=rows[i], nb=Math.max(1,Math.round((r.h-r.l)/TICK)), per=r.v/nb;
    for(let k=0;k<nb;k++){const p=+((Math.floor(r.l/TICK)+k)*TICK).toFixed(2);bins.set(p,(bins.get(p)||0)+per);}}
  const arr=[...bins.entries()].map(([p,v])=>({p:+p,v})).sort((x,y)=>x.p-y.p);
  const total=arr.reduce((s,x)=>s+x.v,0);
  let pi=0;arr.forEach((x,i)=>{if(x.v>arr[pi].v)pi=i;});
  let lo=pi,hi=pi,cum=arr[pi].v;
  while(cum<VA*total&&(lo>0||hi<arr.length-1)){
    const dn=lo>0?arr[lo-1].v:-1, up=hi<arr.length-1?arr[hi+1].v:-1;
    if(up>=dn){hi++;cum+=arr[hi].v;}else{lo--;cum+=arr[lo].v;}}
  return {poc:arr[pi].p,vah:arr[hi].p,val:arr[lo].p,profile:arr};
}

// 2) scan for break-above-VAH -> fail (later close back inside) -> rotate to POC then VAL (distinct days)
let best=null;
for(const W of [12,14,16,18,20,22]) for(let a=0;a+W+3<N;a++){
  const b=a+W-1, {poc,vah,val}=vp(a,b), K=Math.min(N-1,b+18);
  let exitI=-1; for(let d=b+1;d<=K;d++) if(rows[d].h>vah*1.001&&rows[d].c>=vah*0.997){exitI=d;break;}
  if(exitI<0||rows[exitI].h>vah*1.03)continue;
  let failI=-1; for(let d=exitI+1;d<=Math.min(K,exitI+5);d++) if(rows[d].c<vah){failI=d;break;}
  if(failI<0)continue;
  let pocI=-1,valI=-1;
  for(let d=failI;d<=Math.min(N-1,failI+14);d++){ if(pocI<0&&rows[d].l<=poc)pocI=d; if(pocI>=0&&d>pocI&&rows[d].l<=val){valI=d;break;} }
  if(pocI<0||valI<0||valI<=pocI)continue;
  const exitHigh=Math.max(...rows.slice(exitI,failI+1).map(r=>r.h)), poke=(exitHigh-vah)/vah, span=valI-exitI;
  if(span<4||span>14)continue;
  const score=Math.abs(span-7)+poke*60, cand={a,b,poc,vah,val,exitI,failI,pocI,valI,exitHigh,score};
  if(!best||score<best.score)best=cand;
}
if(!best){console.error('NO SCENARIO FOUND — try a different data window');process.exit(3);}

const {a,b,exitI,failI,pocI,valI,poc,vah,val,exitHigh}=best;
const v0=Math.max(0,a-PRE), v1=Math.min(N-1,valI+POST), vis=rows.slice(v0,v1+1), idx=i=>i-v0;
const {profile}=vp(a,b), slMargin=+(exitHigh*0.003).toFixed(2);
const scenario={
  ...META, firstDate:vis[0].t, lastDate:vis[vis.length-1].t,
  rangeStartDate:rows[a].t, rangeEndDate:rows[b].t, valueAreaPct:Math.round(VA*100),
  vah:+vah.toFixed(2), poc:+poc.toFixed(2), val:+val.toFixed(2),
  rangeI0:idx(a), rangeI1:idx(b), exitIdx:idx(exitI), exitHigh:+exitHigh.toFixed(2),
  failIdx:idx(failI), entryIdx:idx(failI), entryPrice:+rows[failI].c.toFixed(2),
  slPrice:+(exitHigh+slMargin).toFixed(2), slMargin,
  pocTargetIdx:idx(pocI), valTargetIdx:idx(valI),
  candles:vis.map(r=>({t:r.t.slice(5),o:r.o,h:r.h,l:r.l,c:r.c,v:r.v})),
  profile:profile.map(x=>({p:x.p,v:+x.v.toFixed(0)}))
};
fs.writeFileSync(OUT,JSON.stringify(scenario,null,1));
console.error(`OK ${N} rows verified · Range ${rows[a].t}..${rows[b].t} · VAH ${vah} POC ${poc} VAL ${val}`);
console.error(`exit ${rows[exitI].t} ${exitHigh} · fail ${rows[failI].t} ${rows[failI].c} · POC ${rows[pocI].t} · VAL ${rows[valI].t}`);
console.error(`entry ${scenario.entryPrice} SL ${scenario.slPrice} · wrote ${OUT} (${vis.length} candles)`);
