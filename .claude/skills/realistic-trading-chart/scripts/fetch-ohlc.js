'use strict';
/* fetch-ohlc.js — pull REAL candlestick OHLC from free, key-less public sources.
 *
 *   const { fetchOHLC } = require('./fetch-ohlc');
 *   const candles = await fetchOHLC({ symbol: 'XAUUSD', interval: '15m', limit: 120 });
 *   // -> [{ time, open, high, low, close, volume }, ...] oldest → newest
 *
 * Providers tried in order (first success wins); none needs an API key:
 *   1. Yahoo Finance   (gold spot/futures, forex, indices, stocks, crypto)
 *   2. Binance         (crypto; PAXGUSDT ≈ gold spot as a fallback proxy)
 *   3. Stooq           (daily CSV; interval falls back to 1d)
 *
 * Requires outbound network access to those hosts. In a locked/egress-filtered
 * sandbox every host may return 403 — run this where the network is open
 * (local Claude Code, CI with internet, your machine).
 */

const YF_INTERVAL = { '1m':'1m','5m':'5m','15m':'15m','30m':'30m','1h':'60m','4h':'60m','1d':'1d' };
const YF_RANGE    = { '1m':'1d','5m':'5d','15m':'1mo','30m':'1mo','1h':'3mo','4h':'6mo','1d':'1y' };
// map a trading symbol to candidate Yahoo tickers (first that returns data wins)
const YF_SYMBOLS = {
  XAUUSD: ['GC=F','XAUUSD=X'], GOLD: ['GC=F'], XAGUSD: ['SI=F','XAGUSD=X'],
  EURUSD: ['EURUSD=X'], GBPUSD: ['GBPUSD=X'], USDJPY: ['USDJPY=X'],
  BTCUSD: ['BTC-USD'], ETHUSD: ['ETH-USD'], US100: ['^NDX'], US500: ['^GSPC'],
};

async function getJSON(url){
  const r = await fetch(url, { headers: { 'User-Agent': 'Mozilla/5.0', 'Accept':'application/json,text/plain,*/*' } });
  if(!r.ok) throw new Error(`HTTP ${r.status} ${url.split('?')[0]}`);
  return r.json();
}
async function getText(url){
  const r = await fetch(url, { headers: { 'User-Agent': 'Mozilla/5.0' } });
  if(!r.ok) throw new Error(`HTTP ${r.status} ${url.split('?')[0]}`);
  return r.text();
}

async function fromYahoo(symbol, interval, limit){
  const tickers = YF_SYMBOLS[symbol.toUpperCase()] || [symbol];
  const iv = YF_INTERVAL[interval] || '15m', rg = YF_RANGE[interval] || '1mo';
  let lastErr;
  for(const t of tickers){
    try{
      const url = `https://query1.finance.yahoo.com/v8/finance/chart/${encodeURIComponent(t)}?interval=${iv}&range=${rg}`;
      const j = await getJSON(url);
      const res = j?.chart?.result?.[0];
      const ts = res?.timestamp, q = res?.indicators?.quote?.[0];
      if(!ts || !q) throw new Error('no data');
      const out=[];
      for(let i=0;i<ts.length;i++){
        if(q.open[i]==null||q.close[i]==null||q.high[i]==null||q.low[i]==null) continue;
        out.push({ time: ts[i]*1000, open:q.open[i], high:q.high[i], low:q.low[i], close:q.close[i], volume:q.volume?.[i] ?? 0 });
      }
      if(out.length) return { source:`yahoo:${t}`, candles: out.slice(-limit) };
    }catch(e){ lastErr=e; }
  }
  throw lastErr || new Error('yahoo: no ticker matched');
}

async function fromBinance(symbol, interval, limit){
  // only sensible for crypto / gold-proxy; map XAUUSD/GOLD -> PAXGUSDT
  const map = { XAUUSD:'PAXGUSDT', GOLD:'PAXGUSDT', BTCUSD:'BTCUSDT', ETHUSD:'ETHUSDT' };
  const s = map[symbol.toUpperCase()] || (symbol.toUpperCase().endsWith('USDT')?symbol.toUpperCase():null);
  if(!s) throw new Error('binance: unsupported symbol');
  const iv = ({'1m':'1m','5m':'5m','15m':'15m','30m':'30m','1h':'1h','4h':'4h','1d':'1d'})[interval] || '15m';
  const url = `https://api.binance.com/api/v3/klines?symbol=${s}&interval=${iv}&limit=${Math.min(limit,1000)}`;
  const j = await getJSON(url);
  const out = j.map(k=>({ time:k[0], open:+k[1], high:+k[2], low:+k[3], close:+k[4], volume:+k[5] }));
  if(!out.length) throw new Error('binance: empty');
  return { source:`binance:${s}`, candles: out.slice(-limit) };
}

async function fromStooq(symbol, _interval, limit){
  const s = symbol.toLowerCase();
  const txt = await getText(`https://stooq.com/q/d/l/?s=${encodeURIComponent(s)}&i=d`);
  const rows = txt.trim().split('\n').slice(1);
  const out=[];
  for(const r of rows){
    const [d,o,h,l,c,v] = r.split(',');
    if(!c || isNaN(+c)) continue;
    out.push({ time:Date.parse(d), open:+o, high:+h, low:+l, close:+c, volume:+(v||0) });
  }
  if(!out.length) throw new Error('stooq: empty');
  return { source:`stooq:${s} (daily)`, candles: out.slice(-limit) };
}

async function fetchOHLC({ symbol='XAUUSD', interval='15m', limit=120, providers } = {}){
  const chain = providers || [fromYahoo, fromBinance, fromStooq];
  const errs=[];
  for(const p of chain){
    try{ const r = await p(symbol, interval, limit); r.symbol=symbol; r.interval=interval; return r; }
    catch(e){ errs.push(`${p.name}: ${e.message}`); }
  }
  throw new Error(`all providers failed for ${symbol} ${interval}\n  - ${errs.join('\n  - ')}`);
}

module.exports = { fetchOHLC, fromYahoo, fromBinance, fromStooq };

if(require.main===module){
  const arg=(n,d)=>{const i=process.argv.indexOf('--'+n);return i<0?d:process.argv[i+1];};
  fetchOHLC({ symbol:arg('symbol','XAUUSD'), interval:arg('interval','15m'), limit:+arg('limit',120) })
    .then(r=>{ console.error(`source=${r.source} candles=${r.candles.length}`); process.stdout.write(JSON.stringify(r.candles)); })
    .catch(e=>{ console.error('FETCH FAILED:', e.message); process.exit(1); });
}
