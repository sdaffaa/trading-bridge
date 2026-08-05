// Brand-styled SVG chart builders for light carousel slides.
// One shared renderer -> every chart is real geometry, consistently styled.

const WBASE = 820, HBASE = 620;
const C = {
  bull: '#159C74', bear: '#D0504F', ink: '#0E1E24',
  grid: 'rgba(14,30,36,0.075)', teal: '#1E9E78', cyan: '#17808F',
  gold: '#B8862B', muted: '#5C7078', profile: '#9FB4BC', profileHot: '#159C74',
};

const esc = (s) => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;');

// ---- candle sets (hand-authored to be truthful to each concept) ----
function balanceSet() {
  // Mean-reverting auction around 40.8 -> genuine balance (fat middle, thin edges)
  const out = [];
  const center = 40.8;
  const seq = [1.5,-.8,1.2,-1.7,.6,1.4,-1.1,.5,-1.6,1.1,-.7,1.8,-1.2,.9,-.5,1.3,-1.7,.7,1.1,-.9,.6,-1.4,1.2,-.7];
  let p = 41.4;
  for (const d of seq) {
    const pull = (center - p) * 0.20;          // gentle mean reversion -> balance with real extremes
    const o = p, c = p + pull + d;
    out.push([o, Math.max(o, c) + .38, Math.min(o, c) - .38, c]);
    p = c;
  }
  return out;
}

function mkChart({candles, levels = [], zones = [], marks = [], profile = false,
                  profileHot = null, pad = 1.6, labels = [], vlines = [], w, h}) {
  const W = w || WBASE, H = h || HBASE;
  const lo = Math.min(...candles.map(c => c[2]), ...levels.map(l => l.p).filter(Number.isFinite), ...zones.flatMap(z => [z.lo, z.hi]).filter(Number.isFinite)) - pad;
  const hi = Math.max(...candles.map(c => c[1]), ...levels.map(l => l.p).filter(Number.isFinite), ...zones.flatMap(z => [z.lo, z.hi]).filter(Number.isFinite)) + pad;
  const narrow = W < 600;
  const padL = 18, padR = profile ? (narrow ? 120 : 190) : (narrow ? 26 : 96), padT = 22, padB = 26;
  const plotW = W - padL - padR, plotH = H - padT - padB;
  const y = (p) => padT + (hi - p) / (hi - lo) * plotH;
  const n = candles.length;
  const slot = plotW / n;
  const bw = Math.max(6, slot * 0.6);
  const x = (i) => padL + i * slot + slot / 2;

  // ---- profile bins computed up-front so POC/VA are DERIVED, never hardcoded ----
  let bins = null, pocP = null, vahP = null, valP = null;
  if (profile) {
    const NB = 26, step = (hi - lo) / NB, vol = new Array(NB).fill(0);
    for (const [o, h, l, c] of candles) {
      const a = Math.max(0, Math.floor((l - lo) / step));
      const b = Math.min(NB - 1, Math.floor((h - lo) / step));
      const span = Math.max(1, b - a + 1);
      for (let i = a; i <= b; i++) vol[i] += 1 / span;
    }
    const price = (i) => lo + (i + .5) * step;
    let pi = 0; vol.forEach((v, i) => { if (v > vol[pi]) pi = i; });
    pocP = price(pi);
    const total = vol.reduce((a, b) => a + b, 0);
    let loI = pi, hiI = pi, acc = vol[pi];
    while (acc < total * 0.7 && (loI > 0 || hiI < NB - 1)) {
      const L = loI > 0 ? vol[loI - 1] : -1, R = hiI < NB - 1 ? vol[hiI + 1] : -1;
      if (R >= L) { hiI++; acc += vol[hiI]; } else { loI--; acc += vol[loI]; }
    }
    valP = price(loI); vahP = price(hiI);
    bins = {NB, step, vol, price, mx: Math.max(...vol)};
  }
  const resolve = (o) => o.auto === 'poc' ? pocP : o.auto === 'vah' ? vahP : o.auto === 'val' ? valP : o.p;

  let s = '', zoneLabels = '';
  // grid
  for (let k = 0; k <= 4; k++) {
    const yy = padT + (k / 4) * plotH;
    s += `<line x1="${padL}" x2="${W - padR + (profile ? (narrow ? 112 : 178) : (narrow ? 18 : 84))}" y1="${yy}" y2="${yy}" stroke="${C.grid}" stroke-width="1"/>`;
  }
  // zones
  for (const z0 of zones) {
    const z = z0.auto === 'va' ? {...z0, lo: valP, hi: vahP} : z0;
    s += `<rect x="${padL}" y="${y(z.hi)}" width="${plotW + (profile ? (narrow ? 112 : 178) : (narrow ? 18 : 84))}" height="${Math.max(2, y(z.lo) - y(z.hi))}" fill="${z.color || C.teal}" opacity="${z.op ?? 0.11}"${z.dash ? ` stroke="${z.color || C.teal}" stroke-opacity="0.5" stroke-dasharray="6 5"` : ''}/>`;
    if (z.label) {
      const ly = (y(z.hi) + y(z.lo)) / 2, lw = z.label.length * 10 + 24;
      zoneLabels += `<rect x="${padL + 6}" y="${ly - 17}" width="${lw}" height="30" rx="8" fill="#FBFCFC" opacity=".92"/>`
        + `<text x="${padL + 6 + lw / 2}" y="${ly + 5}" text-anchor="middle" font-family="Tajawal" font-weight="700" font-size="19" fill="${z.color || C.teal}">${esc(z.label)}</text>`;
    }
  }
  // vertical guides
  for (const v of vlines) {
    s += `<line x1="${x(v.i)}" x2="${x(v.i)}" y1="${padT}" y2="${padT + plotH}" stroke="${v.color || C.muted}" stroke-opacity="0.35" stroke-width="1.5" stroke-dasharray="5 5"/>`;
  }
  // profile histogram (uses the bins computed above)
  if (profile) {
    const px0 = W - padR + 16, pw = narrow ? 96 : 152;
    for (let i = 0; i < bins.NB; i++) {
      const p = bins.price(i);
      const w = (bins.vol[i] / bins.mx) * pw;
      const hot = profileHot && p >= profileHot.lo && p <= profileHot.hi;
      const cold = profileHot && profileHot.coldLo != null && p >= profileHot.coldLo && p <= profileHot.coldHi;
      const fill = hot ? C.profileHot : cold ? '#C6D2D6' : C.profile;
      s += `<rect x="${px0}" y="${y(p) - (plotH / bins.NB) / 2}" width="${Math.max(1.5, w)}" height="${Math.max(2, plotH / bins.NB - 2)}" rx="2" fill="${fill}" opacity="${hot ? .95 : cold ? .9 : .55}"/>`;
    }
  }
  // candles
  candles.forEach((cd, i) => {
    const [o, h, l, c] = cd;
    const up = c >= o, col = up ? C.bull : C.bear;
    const top = Math.min(y(o), y(c)), hgt = Math.max(2, Math.abs(y(c) - y(o)));
    s += `<line x1="${x(i)}" x2="${x(i)}" y1="${y(h)}" y2="${y(l)}" stroke="${col}" stroke-width="1.7"/>`;
    s += `<rect x="${x(i) - bw / 2}" y="${top}" width="${bw}" height="${hgt}" rx="1.5" fill="${col}"/>`;
  });
  // levels
  for (const L0 of levels) {
    const L = {...L0, p: resolve(L0)};
    s += `<line x1="${padL}" x2="${W - padR + (profile ? (narrow ? 112 : 178) : (narrow ? 18 : 84))}" y1="${y(L.p)}" y2="${y(L.p)}" stroke="${L.color || C.ink}" stroke-width="${L.w || 1.8}" ${L.dash ? `stroke-dasharray="${L.dash}"` : ''} opacity="${L.op ?? 0.9}"/>`;
    if (L.tag) {
      const tw = L.tag.length * 10.5 + 20;
      const tx = L.side === 'left' ? padL + 6 : W - padR + (profile ? (narrow ? 112 : 178) : (narrow ? 18 : 84)) - tw;
      const ty = y(L.p) + (L.dy || 0);
      s += `<rect x="${tx}" y="${ty - 15}" width="${tw}" height="27" rx="6" fill="${L.color || C.ink}"/>`;
      s += `<text x="${tx + tw / 2}" y="${ty + 4}" text-anchor="middle" font-family="Tajawal" font-weight="700" font-size="17" fill="#fff">${esc(L.tag)}</text>`;
    }
  }
  // marks (arrows / dots / text)
  for (const m of marks) {
    if (m.kind === 'arrow') {
      const x1 = x(m.i), y1 = y(m.from), y2 = y(m.to);
      s += `<line x1="${x1}" x2="${x1}" y1="${y1}" y2="${y2}" stroke="${m.color || C.cyan}" stroke-width="3" marker-end="url(#ah)"/>`;
    } else if (m.kind === 'dot') {
      s += `<circle cx="${x(m.i)}" cy="${y(m.p)}" r="${m.r || 7}" fill="none" stroke="${m.color || C.cyan}" stroke-width="3"/>`;
    } else if (m.kind === 'text') {
      s += `<text x="${m.x != null ? m.x : x(m.i)}" y="${m.y != null ? m.y : y(m.p)}" text-anchor="${m.anchor || 'middle'}" font-family="Tajawal" font-weight="700" font-size="${m.size || 19}" fill="${m.color || C.ink}">${esc(m.t)}</text>`;
    } else if (m.kind === 'brace') {
      const xx = x(m.i);
      s += `<line x1="${xx}" x2="${xx}" y1="${y(m.hi)}" y2="${y(m.lo)}" stroke="${m.color || C.gold}" stroke-width="2.5"/>`;
      s += `<line x1="${xx - 8}" x2="${xx + 8}" y1="${y(m.hi)}" y2="${y(m.hi)}" stroke="${m.color || C.gold}" stroke-width="2.5"/>`;
      s += `<line x1="${xx - 8}" x2="${xx + 8}" y1="${y(m.lo)}" y2="${y(m.lo)}" stroke="${m.color || C.gold}" stroke-width="2.5"/>`;
      s += `<text x="${xx + 14}" y="${(y(m.hi) + y(m.lo)) / 2 + 6}" font-family="Tajawal" font-weight="700" font-size="19" fill="${m.color || C.gold}">${esc(m.t)}</text>`;
    }
  }
  for (const L of labels) {
    s += `<text x="${L.x}" y="${L.y}" text-anchor="${L.anchor || 'start'}" font-family="Tajawal" font-weight="${L.weight || 700}" font-size="${L.size || 19}" fill="${L.color || C.muted}">${esc(L.t)}</text>`;
  }

  s += zoneLabels;
  return `<svg viewBox="0 0 ${W} ${H}" width="100%" direction="ltr" xmlns="http://www.w3.org/2000/svg">
    <defs><marker id="ah" markerWidth="9" markerHeight="9" refX="4.5" refY="4.5" orient="auto">
      <path d="M0,0 L9,4.5 L0,9 z" fill="${C.cyan}"/></marker></defs>${s}</svg>`;
}

// ---------- named charts ----------
const CH = {};

CH.split = () => {
  const cs = balanceSet();
  const left = mkChart({candles: cs, w: 430, h: 620,
    labels: [{t: 'الجارت لحاله', x: 16, y: 18, color: C.muted, size: 20}]});
  const right = mkChart({candles: cs, profile: true, w: 430, h: 620,
    labels: [{t: '+ البروفايل الحجمي', x: 16, y: 18, color: C.teal, size: 20}]});
  return `<div class="dual">${left}${right}</div>`;
};

CH.poc = () => mkChart({
  candles: balanceSet(), profile: true, profileHot: {lo: 40.2, hi: 41.4},
  levels: [{auto: 'poc', color: C.teal, dash: '9 6', tag: 'POC', w: 2.2}],
  labels: [{t: 'أكبر حجم تداول', x: 18, y: 16, color: C.muted, size: 18}],
});

CH.va = () => mkChart({
  candles: balanceSet(), profile: true, profileHot: {lo: 39.3, hi: 42.3},
  zones: [{auto: 'va', color: C.teal, op: 0.10}],
  levels: [
    {auto: 'vah', color: C.cyan, dash: '6 5', tag: 'VAH', w: 1.8, dy: -19},
    {auto: 'poc', color: C.teal, dash: '9 6', tag: 'POC', w: 2},
    {auto: 'val', color: C.cyan, dash: '6 5', tag: 'VAL', w: 1.8, dy: 19},
  ],
  labels: [{t: '70% من الحجم', x: 18, y: 16, color: C.teal, size: 18}],
});

CH.hvnlvn = () => {
  const cs = balanceSet();
  let p = cs[cs.length - 1][3];
  // fast leg down: traverses the thin area in few, large bars
  for (const d of [-1.4, -1.7, -1.5, -1.2]) { const o = p, c = p + d; cs.push([o, o + .2, c - .3, c]); p = c; }
  // short base at the destination (kept brief so the traversal band stays genuinely thin)
  for (const d of [.3, -.2, .3]) { const o = p, c = p + d; cs.push([o, Math.max(o, c) + .3, Math.min(o, c) - .3, c]); p = c; }
  return mkChart({
    candles: cs, profile: true,
    profileHot: {lo: 39.2, hi: 42.6, coldLo: 36.3, coldHi: 38.8},
    zones: [
      {lo: 39.2, hi: 42.6, color: C.teal, op: 0.12, label: 'HVN — ثقيل'},
      {lo: 36.3, hi: 38.8, color: C.cyan, op: 0.10, label: 'LVN — خفيف', dash: true},
    ],
  });
};

CH.stopfail = () => {
  const cs = [];
  let p = 38.0;
  for (const d of [.5, .4, .6, .3, .7, .5, .6, .4, .8, .5]) { const o = p, c = p + d; cs.push([o, Math.max(o, c) + .3, Math.min(o, c) - .3, c]); p = c; }
  cs.push([p, 44.6, p - .4, p - 1.2]); p -= 1.2;              // sweep wick above stop then reject
  for (const d of [-1.1, -1.5, -1.3, -1.0, -.8, -.6]) { const o = p, c = p + d; cs.push([o, o + .25, c - .3, c]); p = c; }
  return mkChart({
    candles: cs,
    levels: [
      {p: 44.2, color: C.bear, tag: 'ستوبك', w: 2},
      {p: 34.0, color: C.bull, dash: '7 5', tag: 'هدفك', w: 2},
    ],
    marks: [
      {kind: 'dot', i: 10, p: 44.4, color: C.bear, r: 12},
      {kind: 'text', i: 10, p: 46.2, t: 'يطق هني', color: C.bear, size: 20},
    ],
  });
};

CH.tight = () => {
  const cs = balanceSet().slice(0, 18);
  return mkChart({
    candles: cs, pad: 2.2,
    zones: [{lo: 39.2, hi: 42.4, color: C.muted, op: 0.10, label: 'نطاق الحركة العادي'}],
    levels: [
      {p: 41.9, color: C.bear, dash: '6 4', tag: 'ستوب ضيّق ✕', w: 2},
      {p: 43.4, color: C.bull, dash: '6 4', tag: 'برّا النطاق ✓', w: 2},
    ],
  });
};

CH.order = () => {
  const cs = balanceSet().slice(0, 20);
  return mkChart({
    candles: cs, pad: 2.4,
    levels: [
      {p: 43.6, color: C.ink, dash: '7 5', tag: 'هني فكرتي تفشل', w: 2},
      {p: 41.2, color: C.teal, dash: '5 5', tag: 'الدخول', w: 1.8},
    ],
    marks: [
      {kind: 'brace', i: 21, lo: 41.2, hi: 43.6, t: 'المسافة', color: C.gold},
      {kind: 'text', x: 18, y: 18, t: '١) المكان أولاً   ٢) بعدين الحجم', color: C.muted, size: 18, anchor: 'start'},
    ],
  });
};

CH.highs = () => {
  // two genuine swing highs: strong (higher) then weak (lower high) — $5 apart
  const cs = [];
  const push = (o, c, wu = .25, wd = .25) => cs.push([o, Math.max(o, c) + wu, Math.min(o, c) - wd, c]);
  let p = 39.0;
  for (const d of [.5, .6, .5, .7]) { push(p, p + d); p += d; }
  push(p, 42.35, .25, .2); p = 42.35;          // strong high = 42.6 with wick
  for (const d of [-.6, -.8, -.5, -.4]) { push(p, p + d); p += d; }
  for (const d of [.5, .6, .5]) { push(p, p + d); p += d; }
  push(p, 41.85, .25, .2); p = 41.85;          // weak (lower) high = 42.1
  for (const d of [-.5, -.7, -.6, -.4, -.3]) { push(p, p + d); p += d; }
  return mkChart({
    candles: cs, pad: .9,
    levels: [
      {p: 42.6, color: C.bull, dash: '7 5', tag: 'هاي قوي', w: 1.9, side: 'left', dy: -20},
      {p: 42.1, color: C.bear, dash: '7 5', tag: 'هاي ضعيف', w: 1.9, side: 'left', dy: 20},
    ],
    marks: [
      {kind: 'brace', i: cs.length - 0.25, lo: 42.1, hi: 42.6, t: '$5', color: C.gold},
    ],
  });
};

CH.breakfail = () => {
  const cs = [];
  let p = 38.6;
  for (const d of [.4, .5, .3, .6, .4, .5]) { const o = p, c = p + d; cs.push([o, Math.max(o, c) + .3, Math.min(o, c) - .3, c]); p = c; }
  cs.push([p, 43.2, p - .2, 42.9]); p = 42.9;                  // break above
  cs.push([p, 43.4, 41.2, 41.4]); p = 41.4;                    // reject
  for (const d of [-.9, -1.1, -.8, -.7]) { const o = p, c = p + d; cs.push([o, o + .25, c - .3, c]); p = c; }
  return mkChart({
    candles: cs,
    levels: [{p: 42.7, color: C.ink, dash: '6 4', tag: 'الهاي', w: 1.9}],
    marks: [
      {kind: 'dot', i: 6, p: 43.0, color: C.bear, r: 11},
      {kind: 'text', i: 6, p: 44.6, t: 'دخلت مع الكسر', color: C.bear, size: 19},
      {kind: 'arrow', i: 10, from: 41.0, to: 38.4, color: C.bear},
    ],
  });
};

CH.pools = () => {
  const cs = balanceSet().slice(0, 20);
  const hi = Math.max(...cs.map(c => c[1])), lo = Math.min(...cs.map(c => c[2]));
  return mkChart({
    candles: cs, pad: 1.4,
    zones: [
      {lo: hi + .06, hi: hi + 1.0, color: C.bear, op: 0.14, label: 'سيولة فوق الهاي'},
      {lo: lo - 1.0, hi: lo - .06, color: C.bull, op: 0.14, label: 'سيولة تحت اللو'},
    ],
    levels: [
      {p: hi, color: C.ink, dash: '5 5', w: 1.5, op: .45},
      {p: lo, color: C.ink, dash: '5 5', w: 1.5, op: .45},
    ],
  });
};

CH.why = () => {
  const cs = balanceSet().slice(0, 16);
  const hi = Math.max(...cs.map(c => c[1]));
  const mid = cs[cs.length - 1][3];
  return mkChart({
    candles: cs, pad: 1.4,
    zones: [{lo: hi + .06, hi: hi + 1.0, color: C.bear, op: 0.15, label: 'أوامر جاهزة'}],
    levels: [{p: hi, color: C.ink, dash: '5 5', w: 1.5, op: .45}],
    marks: [
      {kind: 'arrow', i: cs.length + .6, from: mid, to: hi + .5, color: C.cyan},
      {kind: 'text', i: cs.length - 4.5, p: mid - 1.15, t: 'السوق يروح لها', color: C.cyan, size: 20},
    ],
  });
};

CH.sweep = () => {
  // range -> sweep above the pool -> displacement back inside -> entry after the sweep
  const cs = [];
  const push = (o, c, wu = .3, wd = .3) => cs.push([o, Math.max(o, c) + wu, Math.min(o, c) - wd, c]);
  let p = 40.2;
  for (const d of [.35, -.3, .4, -.35, .3, .25]) { push(p, p + d); p += d; }
  const rangeHi = Math.max(...cs.map(c => c[1]));
  const poolLo = rangeHi + .05, poolHi = rangeHi + .95;
  cs.push([p, poolHi - .15, p - .3, rangeHi - .55]);           // the sweep: wick into the pool, close back inside
  p = rangeHi - .55;
  for (const d of [-.85, -1.15, -.95, -.6, -.5]) { push(p, p + d, .2, .3); p += d; }
  return mkChart({
    candles: cs, pad: 1.0,
    zones: [{lo: poolLo, hi: poolHi, color: C.bear, op: 0.14, label: 'السيولة'}],
    levels: [{p: rangeHi, color: C.ink, dash: '5 5', w: 1.6, op: .5}],
    marks: [
      {kind: 'dot', i: 6, p: poolHi - .2, color: C.gold, r: 11},
      {kind: 'text', i: 5.2, p: poolHi + .55, t: '١) السحب', color: C.gold, size: 20},
      {kind: 'dot', i: 7, p: cs[7][3], color: C.teal, r: 11},
      {kind: 'text', i: 9.6, p: cs[7][3] + .75, t: '٢) الدخول بعد السحب', color: C.teal, size: 20},
    ],
  });
};

module.exports = {CH, C};
