#!/usr/bin/env node
// Universal Chart Realism — QA engine (§10 of the master prompt).
// Computes every required diagnostic and applies the critical export gates.
// Usage: node chart_qa.mjs --scenario data/scenario.json [--mode Real|Reconstructed|Simulated] [--json qa.json]
// Real/Reconstructed data is NEVER failed for being outside a diagnostic range (the prompt forbids
// bending real data); ranges are advisory there and enforced only for Simulated.
import fs from 'fs';
const arg=(k,d)=>{const i=process.argv.indexOf('--'+k);return i>=0?process.argv[i+1]:d;};
const S=JSON.parse(fs.readFileSync(arg('scenario','data/scenario.json'),'utf8'));
const MODE=arg('mode','Reconstructed');
const C=S.candles;
const n=C.length, sim=MODE==='Simulated';
const r2=x=>Math.round(x*100)/100, pct=x=>Math.round(x*1000)/10;
const med=a=>{const s=[...a].sort((x,y)=>x-y);return s.length%2?s[(s.length-1)/2]:(s[s.length/2-1]+s[s.length/2])/2;};
const mean=a=>a.reduce((s,x)=>s+x,0)/a.length;

// ---------- basics ----------
const body=C.map(c=>Math.abs(c.c-c.o)), range=C.map(c=>c.h-c.l);
const br=C.map((c,i)=>range[i]>0?body[i]/range[i]:0);
let ohlcBad=0; C.forEach(c=>{if(!(c.h>=c.o-1e-9&&c.h>=c.c-1e-9&&c.h>=c.l-1e-9&&c.l<=c.o+1e-9&&c.l<=c.c+1e-9))ohlcBad++;});

// ---------- morphology vs rolling median range ----------
const roll=[]; for(let i=0;i<n;i++){const w=range.slice(Math.max(0,i-9),i+1);roll.push(med(w)||1);}
const rel=range.map((x,i)=>x/roll[i]);
const morph={contraction:0,normal:0,displacement:0,outlier:0};
rel.forEach(x=>{ if(x>2.8)morph.outlier++; else if(x>=1.5)morph.displacement++; else if(x>=0.65)morph.normal++; else morph.contraction++;});

// ---------- ER / overlap / pause / pullback ----------
const ER=(a,b)=>{const net=Math.abs(C[b].c-C[a].o);const sum=body.slice(a,b+1).reduce((s,x)=>s+x,0);return sum>0?net/sum:0;};
const erAll=r2(ER(0,n-1));
const W=5, wins=[]; for(let i=0;i+W<=n;i++)wins.push(ER(i,i+W-1));
const pauseRate=wins.filter(x=>x<0.35).length/wins.length;
// longest run of windows with ER>0.85 (proxy for "ER without pause")
let hotRun=0,cur=0; wins.forEach(x=>{if(x>0.85){cur++;hotRun=Math.max(hotRun,cur);}else cur=0;});
const overlaps=[]; for(let i=1;i<n;i++){const lo=Math.max(C[i].l,C[i-1].l),hi=Math.min(C[i].h,C[i-1].h);
  const inter=Math.max(0,hi-lo), small=Math.min(range[i],range[i-1])||1; overlaps.push(inter/small);}
const overlapAvg=r2(mean(overlaps));
// pullback depth: largest counter-move vs net move
const netUp=C[n-1].c>=C[0].o; let peak=C[0].c, maxDD=0;
C.forEach(c=>{ if(netUp){peak=Math.max(peak,c.h);maxDD=Math.max(maxDD,peak-c.l);} else {peak=Math.min(peak,c.l);maxDD=Math.max(maxDD,c.h-peak);} });
const netMove=Math.abs(C[n-1].c-C[0].o)||1;
const pullbackDepth=r2(maxDD/netMove);

// ---------- reversal / doji / inside / outside / streak ----------
const dir=C.map(c=>c.c>c.o?1:(c.c<c.o?-1:0));
const wave=netUp?1:-1;
const isDoji=C.map((c,i)=>range[i]>0&&body[i]/range[i]<0.1);
const reversal=C.filter((c,i)=>!isDoji[i]&&dir[i]===-wave).length;
let inside=0,outside=0;
for(let i=1;i<n;i++){ if(C[i].h<=C[i-1].h&&C[i].l>=C[i-1].l)inside++; if(C[i].h>C[i-1].h&&C[i].l<C[i-1].l)outside++; }
let streak=1,best=1; for(let i=1;i<n;i++){ if(dir[i]!==0&&dir[i]===dir[i-1]){streak++;best=Math.max(best,streak);}else streak=1; }

// ---------- anti-pattern: motif / similarity / lag ----------
const motifs={}; for(let i=0;i+3<=n;i++){const k=dir.slice(i,i+3).map(d=>d>0?'U':d<0?'D':'N').join('');motifs[k]=(motifs[k]||0)+1;}
const motifTotal=Object.values(motifs).reduce((s,x)=>s+x,0);
const topMotif=Object.entries(motifs).sort((a,b)=>b[1]-a[1])[0]||['-',0];
const motifShare=topMotif[1]/motifTotal;
let motifRepeat=1,mrBest=1; for(let i=1;i+3<=n;i++){const a=dir.slice(i-1,i+2).join(),b=dir.slice(i,i+3).join();
  if(a===b){motifRepeat++;mrBest=Math.max(mrBest,motifRepeat);}else motifRepeat=1;}
const simPairs=(arr)=>{let c=0,t=0;for(let i=1;i<arr.length;i++){t++;const a=arr[i],b=arr[i-1],m=Math.max(Math.abs(a),Math.abs(b))||1;
  if(Math.abs(a-b)/m<0.15)c++;} return c/t;};
const bodySim=simPairs(body), rangeSim=simPairs(range);
const shapeSim=(()=>{let c=0,t=0;for(let i=1;i<n;i++){t++;
  const f=k=>[body[k]/(range[k]||1),(C[k].h-Math.max(C[k].o,C[k].c))/(range[k]||1),(Math.min(C[k].o,C[k].c)-C[k].l)/(range[k]||1)];
  const a=f(i),b=f(i-1); if(a.every((v,j)=>Math.abs(v-b[j])<0.15))c++;} return c/t;})();
const corr=(a,b)=>{const ma=mean(a),mb=mean(b);const num=a.reduce((s,x,i)=>s+(x-ma)*(b[i]-mb),0);
  const da=Math.sqrt(a.reduce((s,x)=>s+(x-ma)**2,0)),db=Math.sqrt(b.reduce((s,x)=>s+(x-mb)**2,0));return da&&db?num/(da*db):0;};
const lagDir=L=>{let m=0,t=0;for(let i=L;i<n;i++){if(dir[i]===0||dir[i-L]===0)continue;t++;if(dir[i]===dir[i-L])m++;}return t?m/t:0;};
const lagBody=L=>r2(Math.abs(corr(body.slice(L),body.slice(0,n-L))));

// ---------- trade logic ----------
const trade={};
if(S.entryIdx!=null&&S.slPrice!=null){
  const risk=Math.abs(S.entryPrice-S.slPrice);
  trade.risk=r2(risk);
  trade.R_to_POC=risk?r2(Math.abs(S.poc-S.entryPrice)/risk):null;
  trade.R_to_VAL=risk?r2(Math.abs(S.val-S.entryPrice)/risk):null;
  trade.chronological = S.exitIdx<=S.failIdx && S.failIdx<=S.entryIdx && S.entryIdx<=S.pocTargetIdx && S.pocTargetIdx<S.valTargetIdx;
  trade.slAboveExitHigh = S.slPrice>S.exitHigh;
  trade.noFutureLeak = trade.chronological;
}

// ---------- gates ----------
const gates=[];
const G=(name,ok,sev,note)=>gates.push({name,ok,sev,note});
G('OHLC صالح لكل شمعة', ohlcBad===0, 'حرج', `${ohlcBad} صف غير صالح`);
G('الترتيب الزمني للنموذج (لا Future Leak)', trade.chronological!==false, 'حرج', 'exit ≤ fail ≤ entry ≤ POC < VAL');
G('مصدر البيانات مُعلن', !!(S.source&&S.symbol&&S.tf), 'حرج', `${S.symbol||'?'} · ${S.source||'?'} · ${S.tf||'?'}`);
G('عدد الشموع ضمن نطاق الكاروسيل 28–48', n>=28&&n<=48, 'مرتفع', `${n} شمعة`);
G('لا Motif ثلاثي متكرر أكثر من مرتين', mrBest<=2, sim?'مرتفع':'تشخيصي', `أطول تكرار ${mrBest}`);
G('Motif Share ≤ 50%', motifShare<=0.5, sim?'مرتفع':'تشخيصي', `${pct(motifShare)}%`);
G('ER > 0.85 لا يستمر بلا Pause', hotRun<=8, sim?'مرتفع':'تشخيصي', `أطول سلسلة ${hotRun} نافذة`);
G('Lag3 Direction Match 35–60%', lagDir(3)>=0.35&&lagDir(3)<=0.60, 'تشخيصي', `${pct(lagDir(3))}%`);
G('Lag3 Body Corr < 0.40', lagBody(3)<0.40, sim?'مرتفع':'تشخيصي', `${lagBody(3)}`);
G('أطول سلسلة لون واحد ≤ 6', best<=6, sim?'مرتفع':'تشخيصي', `${best}`);
G('متوسط Body/Range 38–58%', mean(br)>=0.38&&mean(br)<=0.58, 'تشخيصي', `${pct(mean(br))}%`);
if(trade.slAboveExitHigh!==undefined) G('الستوب فوق قمة الخروج', trade.slAboveExitHigh, 'حرج', `${S.slPrice} > ${S.exitHigh}`);

const critFail=gates.filter(g=>g.sev==='حرج'&&!g.ok);
const highFail=gates.filter(g=>g.sev==='مرتفع'&&!g.ok);

const report={
  mode:MODE, symbol:S.symbol, source:S.source, tf:S.tf, volType:S.volType,
  window:`${S.firstDate} → ${S.lastDate}`, fixedRange:`${S.rangeStartDate} → ${S.rangeEndDate}`,
  candles:n,
  body:{mean:r2(mean(body)),median:r2(med(body)),max:r2(Math.max(...body))},
  range:{mean:r2(mean(range)),median:r2(med(range)),max:r2(Math.max(...range))},
  bodyRangePct:pct(mean(br)),
  morphology:morph,
  motion:{ER:erAll, overlapAvg, pullbackDepth, pauseRate:pct(pauseRate), hotWindowRun:hotRun},
  candlestats:{reversalPct:pct(reversal/n), dojiPct:pct(isDoji.filter(Boolean).length/n),
    insidePct:pct(inside/(n-1)), outsidePct:pct(outside/(n-1)), longestSameColor:best},
  antiPattern:{bodySimilarity:pct(bodySim), rangeSimilarity:pct(rangeSim), shapeSimilarity:pct(shapeSim),
    topMotif:topMotif[0], motifSharePct:pct(motifShare), motifMaxRepeat:mrBest,
    lag1Dir:pct(lagDir(1)), lag3Dir:pct(lagDir(3)), lag1BodyCorr:lagBody(1), lag3BodyCorr:lagBody(3)},
  trade, gates,
  verdict: critFail.length? 'REJECT (فشل حرج)' : (sim&&highFail.length? 'REGENERATE (فشل مرتفع)' : 'PASS')
};
if(arg('json')) fs.writeFileSync(arg('json'),JSON.stringify(report,null,1));

const L=[];
L.push(`— QA تقرير واقعية الجارت — الوضع: ${MODE} —`);
L.push(`${report.symbol} · ${report.tf} · ${report.source} · ${report.volType||''}`);
L.push(`النافذة ${report.window} | Fixed Range ${report.fixedRange} | شموع: ${n}`);
L.push(`Body متوسط/وسيط/أقصى: ${report.body.mean}/${report.body.median}/${report.body.max} · Range: ${report.range.mean}/${report.range.median}/${report.range.max} · Body/Range ${report.bodyRangePct}%`);
L.push(`مورفولوجيا: انكماش ${morph.contraction} · عادية ${morph.normal} · إزاحة ${morph.displacement} · شاذة ${morph.outlier}`);
L.push(`حركة: ER ${erAll} · Overlap ${overlapAvg} · PullbackDepth ${pullbackDepth} · PauseRate ${report.motion.pauseRate}%`);
L.push(`شموع: عكسية ${report.candlestats.reversalPct}% · Doji ${report.candlestats.dojiPct}% · Inside ${report.candlestats.insidePct}% · Outside ${report.candlestats.outsidePct}% · أطول لون ${best}`);
L.push(`نمطية: BodySim ${report.antiPattern.bodySimilarity}% · RangeSim ${report.antiPattern.rangeSimilarity}% · ShapeSim ${report.antiPattern.shapeSimilarity}% · Motif ${topMotif[0]} ${report.antiPattern.motifSharePct}% (تكرار ${mrBest}) · Lag3 ${report.antiPattern.lag3Dir}% / corr ${report.antiPattern.lag3BodyCorr}`);
if(trade.risk) L.push(`صفقة: Risk ${trade.risk} · R→POC ${trade.R_to_POC} · R→VAL ${trade.R_to_VAL} · ترتيب زمني ${trade.chronological?'سليم':'خطأ'}`);
L.push('— البوابات —');
gates.forEach(g=>L.push(`${g.ok?'✅':(g.sev==='تشخيصي'?'ℹ️':'❌')} [${g.sev}] ${g.name} — ${g.note}`));
L.push(`النتيجة: ${report.verdict}`);
console.log(L.join('\n'));
process.exit(critFail.length?2:0);
