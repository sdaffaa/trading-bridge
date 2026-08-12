import fs from 'fs';
const rows = fs.readFileSync('data/gld_daily.csv','utf8').trim().split('\n').slice(1)
  .map(l=>{const[t,o,h,lo,c,v]=l.trim().split(',');return{t,o:+o,h:+h,l:+lo,c:+c,v:+v};})
  .sort((a,b)=>a.t<b.t?-1:1); // chronological
const N=rows.length;
const TICK=0.5;

// ---- 1. OHLC integrity ----
let bad=0;
rows.forEach((r,i)=>{const okH=r.h>=r.o-1e-9&&r.h>=r.c-1e-9&&r.h>=r.l-1e-9;
  const okL=r.l<=r.o+1e-9&&r.l<=r.c+1e-9; if(!(okH&&okL)){bad++;console.log('BAD OHLC',r.t,r);} });
console.log(`OHLC rows: ${N}, invalid: ${bad}  range ${rows[0].t}..${rows[N-1].t}`);

// ---- Volume Profile over a window ----
function vp(a,b){ // rows[a..b] inclusive
  const bins=new Map();
  for(let i=a;i<=b;i++){const r=rows[i];const nb=Math.max(1,Math.round((r.h-r.l)/TICK));
    const per=r.v/nb;
    for(let k=0;k<nb;k++){const p=+( (Math.floor(r.l/TICK)+k)*TICK ).toFixed(2); bins.set(p,(bins.get(p)||0)+per);}
  }
  const arr=[...bins.entries()].map(([p,v])=>({p:+p,v})).sort((x,y)=>x.p-y.p);
  const total=arr.reduce((s,x)=>s+x.v,0);
  let pIdx=0; arr.forEach((x,i)=>{if(x.v>arr[pIdx].v)pIdx=i;});
  const poc=arr[pIdx].p;
  let lo=pIdx,hi=pIdx,cum=arr[pIdx].v;
  while(cum<0.70*total&&(lo>0||hi<arr.length-1)){
    const dn=lo>0?arr[lo-1].v:-1, up=hi<arr.length-1?arr[hi+1].v:-1;
    if(up>=dn){hi++;cum+=arr[hi].v;} else {lo--;cum+=arr[lo].v;}
  }
  return {poc,vah:arr[hi].p,val:arr[lo].p,profile:arr,total};
}

// ---- 2. scan for break-above-VAH → fail → rotate to POC then VAL ----
let best=null;
for(let W of [12,14,16,18,20,22]){
  for(let a=0;a+W+3<N;a++){
    const b=a+W-1; const {poc,vah,val}=vp(a,b);
    const K=Math.min(N-1,b+18);
    // exit: poke above VAH AND close up near/above VAH (a real acceptance attempt)
    let exitI=-1;
    for(let d=b+1;d<=K;d++){ if(rows[d].h>vah*1.001 && rows[d].c>=vah*0.997){exitI=d;break;} }
    if(exitI<0||rows[exitI].h>vah*1.03)continue;
    // fail: a LATER day closes back below VAH (failed acceptance)
    let failI=-1;
    for(let d=exitI+1;d<=Math.min(K,exitI+5);d++){ if(rows[d].c<vah){failI=d;break;} }
    if(failI<0)continue;
    // rotation: reach POC (>= fail day), then VAL on a STRICTLY later day
    let pocI=-1,valI=-1;
    for(let d=failI;d<=Math.min(N-1,failI+14);d++){ if(pocI<0&&rows[d].l<=poc)pocI=d;
      if(pocI>=0&&d>pocI&&rows[d].l<=val){valI=d;break;} }
    if(pocI<0||valI<0||valI<=pocI)continue;
    const exitHigh=Math.max(...rows.slice(exitI,failI+1).map(r=>r.h));
    const pokePct=(exitHigh-vah)/vah;
    const span=valI-exitI;
    if(span<4||span>14)continue;
    const score = Math.abs(span-7) + pokePct*60; // prefer ~7-candle separated rotation, modest poke
    const cand={a,b,W,poc,vah,val,exitI,failI,pocI,valI,exitHigh,pokePct,span,score};
    if(!best||score<best.score)best=cand;
  }
}
if(!best){console.log('NO SCENARIO FOUND');process.exit(1);}
const {a,b,exitI,failI,pocI,valI,poc,vah,val,exitHigh}=best;
console.log('BEST RANGE',rows[a].t,'..',rows[b].t,'W='+best.W);
console.log('VAH',vah,'POC',poc,'VAL',val,'pokePct',(best.pokePct*100).toFixed(2)+'%');
console.log('exit',rows[exitI].t,'high',exitHigh,' fail',rows[failI].t,'close',rows[failI].c);
console.log('POC hit',rows[pocI].t,' VAL hit',rows[valI].t);

// ---- 3. build visible window + scenario.json ----
const pre=0, post=1;
const v0=Math.max(0,a-pre), v1=Math.min(N-1,valI+post);
const vis=rows.slice(v0,v1+1);
const idx=i=>i-v0;
const {profile,poc:P2,vah:H2,val:L2}=vp(a,b); // recompute for output profile
const slMargin=+(exitHigh*0.003).toFixed(2);
const scenario={
  symbol:'GLD (SPDR Gold Shares)', proxy:'مؤشر متداول يتتبّع الذهب', source:'Alpha Vantage',
  tf:'يومي · 1D', volType:'حجم بورصة حقيقي (NYSE Arca)',
  firstDate:vis[0].t, lastDate:vis[vis.length-1].t,
  rangeStartDate:rows[a].t, rangeEndDate:rows[b].t, valueAreaPct:70,
  vah:+vah.toFixed(2), poc:+poc.toFixed(2), val:+val.toFixed(2),
  rangeI0:idx(a), rangeI1:idx(b),
  exitIdx:idx(exitI), exitHigh:+exitHigh.toFixed(2),
  failIdx:idx(failI),
  entryIdx:idx(failI), entryPrice:+rows[failI].c.toFixed(2),
  slPrice:+(exitHigh+slMargin).toFixed(2), slMargin,
  pocTargetIdx:idx(pocI), valTargetIdx:idx(valI),
  candles:vis.map(r=>({t:r.t.slice(5),o:r.o,h:r.h,l:r.l,c:r.c,v:r.v})),
  profile:profile.map(x=>({p:x.p,v:+x.v.toFixed(0)}))
};
fs.writeFileSync('data/scenario.json',JSON.stringify(scenario,null,1));
console.log('\nvisible candles',vis.length,' entry',scenario.entryPrice,' SL',scenario.slPrice,'(margin',slMargin+')');
console.log('scenario.json written');
