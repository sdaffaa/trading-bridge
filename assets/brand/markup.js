/* ==========================================================================
   Liquidity State — Chart Markup Engine
   Adopted markup method: inline-labelled level lines, outlined zones (OB),
   swing-labelled structure zigzag, fib scale, trendline, projection path.
   Renders SVG; all colors come from brand.css custom properties.

   Coordinates are expressed as (candle index, price) — never pixels — so
   markup stays locked to the data when the canvas or range changes.

   Motion: pass `anim: {}` to build a draw-on timeline at the measured
   reference cadence (see MARKUP.md §Rhythm), then drive it with seek(t).
   ========================================================================== */

(function (global) {
  'use strict';

  const NS = 'http://www.w3.org/2000/svg';
  const el = (n, a = {}) => {
    const e = document.createElementNS(NS, n);
    for (const k in a) e.setAttribute(k, a[k]);
    return e;
  };

  /* Reference cadence, measured from the source recording (seconds).
     Stroke length per element type; everything else is spacing. */
  const CADENCE = {
    start:      0.6,   // first stroke begins
    rest:       0.9,   // silence between one stroke ending and the next starting
    labelLag:   0.7,   // label fades in this long after its stroke lands
    labelDur:   0.4,   // label fade duration
    dur: {
      level:      0.5,
      trend:      0.6,
      zone:       1.0,
      structure:  2.2, // the full traverse — deliberately the longest stroke
      projection: 0.9,
      fib:        0.8,
      swing:      0.3,
      invalid:    0.35,
      vp:         1.2,   // the profile wipes open across its range
    }
  };

  const easeOut = p => 1 - Math.pow(1 - p, 3);
  const clamp01 = v => v < 0 ? 0 : v > 1 ? 1 : v;

  /* ========================================================================
     Drawing rules — the same two rules the chart-drawing-accuracy skill
     enforces, applied here so markup terminates correctly as it is drawn
     instead of being corrected afterwards.

     A drawing starts on the candle that created it and ends on the candle
     that broke it. Nothing counts as a break until price has departed the
     drawing at least once: a level is born touching price, so the bar right
     after it is still on it — that is not a break, that is price not having
     left yet.

     Kept behaviourally identical to scripts/verify_drawing.py in the skill;
     `npm test`-style parity is checked by tools/check-rules-parity.js.
     ======================================================================== */

  function firstDeparture(candles, start, touching) {
    for (let j = start + 1; j < candles.length; j++) {
      if (!touching(candles[j])) return j;
    }
    return null;                     // price never leaves → the anchor is wrong
  }

  function levelTouch(price, side, tol) {
    return side === 'above'
      ? c => c.h >= price - tol
      : c => c.l <= price + tol;
  }

  function zoneOverlap(top, bottom, tol) {
    return c => c.h >= bottom - tol && c.l <= top + tol;
  }

  /* Returns {brk, dep} — the breaking bar and the bar price first left on. */
  function levelBreak(candles, price, start, mode, side, tol) {
    if (side === 'auto') side = price >= candles[start].c ? 'above' : 'below';
    const touching = levelTouch(price, side, tol);
    const dep = firstDeparture(candles, start, touching);
    if (dep === null) return { brk: null, dep: null };
    for (let j = dep + 1; j < candles.length; j++) {
      const c = candles[j];
      const hit = mode === 'close'
        ? (side === 'above' ? c.c > price + tol : c.c < price - tol)
        : touching(c);
      if (hit) return { brk: j, dep };
    }
    return { brk: null, dep };
  }

  function zoneBreakBar(candles, top, bottom, start, mode, tol) {
    const overlaps = zoneOverlap(top, bottom, tol);
    const dep = firstDeparture(candles, start, overlaps);
    if (dep === null) return { brk: null, dep: null };
    for (let j = dep + 1; j < candles.length; j++) {
      const c = candles[j];
      const hit = mode === 'fill' ? (c.l <= bottom + tol && c.h >= top - tol)
                : mode === 'close' ? (c.c >= bottom - tol && c.c <= top + tol)
                : overlaps(c);
      if (hit) return { brk: j, dep };
    }
    return { brk: null, dep };
  }

  const levelHolds = (price, tol) => c => c.l - tol <= price && price <= c.h + tol;

  function LSChart(opts) {
    const {
      mount,
      width = 936,
      height = 620,
      candles = [],
      padding = { top: 28, right: 150, bottom: 40, left: 20 },
      priceRange = null,
      candleWidth = null,
      barsRight = 6,           // empty bars kept at the right for projections
      anim = null,             // pass {} for defaults, or override any CADENCE key
      autoTerminate = false,   // end levels/zones at the candle that broke them
      tolerance = 0
    } = opts;

    /* Drawings that were asked to run to the edge but shouldn't have, and
       anchors that don't hold up. Read chart.violations after layout(). */
    const violations = [];

    /* Resolve a drawing's right edge.
         to: <number>  use it verbatim
         to: 'auto'    always terminate at the break
         to: 'edge'    always run to the right edge
         to omitted    terminate at the break when autoTerminate is on
       Returns null for "run to the edge". */
    function resolveEnd(to, compute) {
      if (typeof to === 'number') return to;
      if (to === 'edge') return null;
      if (to === 'auto' || (to == null && autoTerminate)) {
        const r = compute();
        return r === null ? null : r;
      }
      return null;
    }

    const A = anim ? Object.assign({}, CADENCE, anim, {
      dur: Object.assign({}, CADENCE.dur, anim.dur)
    }) : null;

    const host = typeof mount === 'string' ? document.querySelector(mount) : mount;
    const svg = el('svg', {
      viewBox: `0 0 ${width} ${height}`,
      width: '100%', class: 'ls-chart'
    });
    host.appendChild(svg);
    const defs = el('defs'); svg.appendChild(defs);

    // layers, painted back to front
    const gGrid    = el('g', { class: 'ls-layer-grid' });
    const gZone    = el('g', { class: 'ls-layer-zone' });
    const gCandle  = el('g', { class: 'ls-layer-candle' });
    const gStruct  = el('g', { class: 'ls-layer-struct' });
    const gLabel   = el('g', { class: 'ls-layer-label' });
    [gGrid, gZone, gCandle, gStruct, gLabel].forEach(g => svg.appendChild(g));

    // ---- scales -----------------------------------------------------------
    let lo, hi;
    if (priceRange) { [lo, hi] = priceRange; }
    else {
      lo = Math.min(...candles.map(c => c.l));
      hi = Math.max(...candles.map(c => c.h));
      const pad = (hi - lo) * 0.08;
      lo -= pad; hi += pad;
    }
    const plotL = padding.left, plotR = width - padding.right;
    const plotT = padding.top,  plotB = height - padding.bottom;
    const n = candles.length + barsRight;
    const step = (plotR - plotL) / n;
    const cw = candleWidth || Math.max(3, step * 0.58);

    const X = i => plotL + step * (i + 0.5);
    const Y = p => plotB - ((p - lo) / (hi - lo)) * (plotB - plotT);

    const jobs = [];        // deferred text measurement, run in layout()
    const track = [];       // animation entries
    let cursor = A ? A.start : 0;
    let uid = 0;

    /* Register an animation entry and advance the timeline cursor.
       kind: 'stroke' (dash reveal) | 'fade' | 'wipe' (clip-rect grow) */
    function cue(nodes, kind, t0, dur, extra) {
      if (!A) return;
      track.push(Object.assign({ nodes: [].concat(nodes), kind, t0, dur }, extra || {}));
    }
    function schedule(type, at, dur) {
      if (!A) return { t0: 0, dur: 0 };      // static chart — nothing to sequence
      const d = dur != null ? dur : A.dur[type];
      const t0 = at != null ? at : cursor;
      if (at == null) cursor = t0 + d + A.rest;
      return { t0, dur: d };
    }
    function cueLabel(node, strokeEnd) {
      if (!A) return;
      cue(node, 'fade', strokeEnd + A.labelLag, A.labelDur);
    }

    // ---- candles ----------------------------------------------------------
    function drawCandles() {
      candles.forEach((c, i) => {
        const up = c.c >= c.o;
        const g = el('g', { class: up ? 'ls-candle-up' : 'ls-candle-down' });
        g.appendChild(el('line', {
          x1: X(i), x2: X(i), y1: Y(c.h), y2: Y(c.l), 'stroke-width': 1.6
        }));
        const yo = Y(c.o), yc = Y(c.c);
        g.appendChild(el('rect', {
          x: X(i) - cw / 2, y: Math.min(yo, yc),
          width: cw, height: Math.max(1.5, Math.abs(yc - yo))
        }));
        gCandle.appendChild(g);
      });
      return api;
    }

    // ---- 1. level line with inline centred label --------------------------
    // The line breaks around the text — the signature of this markup method.
    function level({ price, label, from = 0, to, tone = 'primary',
                     dashed = false, at, dur, mode = 'touch', side = 'auto',
                     tol = tolerance }) {
      const end = resolveEnd(to, () => {
        if (!candles[from]) return null;
        if (!levelHolds(price, tol)(candles[from])) {
          violations.push({ id: label || `level@${price}`, kind: 'level', status: 'anchor',
            message: `bar ${from} never reaches ${price} — the line starts from a candle ` +
                     `that did not make that level` });
        }
        const { brk, dep } = levelBreak(candles, price, from, mode, side, tol);
        if (dep === null) {
          violations.push({ id: label || `level@${price}`, kind: 'level', status: 'invalid',
            message: `price never leaves ${price} after bar ${from}` });
          return null;
        }
        return brk;                       // null → never broken, run to the edge
      });

      const y = Y(price);
      const x1 = X(from) - step / 2;
      const x2 = end === null ? plotR : X(end) + step / 2;
      const cls = `ls-mk-line ls-mk-${tone}` + (dashed ? ' ls-mk-dashed' : '');

      const lineA = el('line', { class: cls, x1, y1: y, x2, y2: y });
      const lineB = el('line', { class: cls, x1, y1: y, x2, y2: y });
      gStruct.appendChild(lineA); gStruct.appendChild(lineB);
      if (!label) lineB.remove();

      const s = schedule('level', at, dur);
      cue(label ? [lineA, lineB] : [lineA], 'stroke', s.t0, s.dur);

      if (label) {
        const t = el('text', {
          class: `ls-mk-label ls-mk-${tone}-t`, x: (x1 + x2) / 2, y,
          'text-anchor': 'middle', 'dominant-baseline': 'central'
        });
        t.textContent = label;
        gLabel.appendChild(t);
        cueLabel(t, s.t0 + s.dur);

        jobs.push(() => {                     // split the line around the text
          const w = t.getComputedTextLength() / 2 + 10;
          const mid = (x1 + x2) / 2;
          lineA.setAttribute('x2', mid - w);
          lineB.setAttribute('x1', mid + w);
        });
      }
      return api;
    }

    // ---- 2. zone / order block -------------------------------------------
    function zone({ from, to, top, bottom, label, tone = 'primary',
                    align = 'center', at, dur, mode = 'touch', tol = tolerance }) {
      const end = resolveEnd(to, () => {
        if (!candles[from]) return null;
        if (!zoneOverlap(top, bottom, tol)(candles[from])) {
          violations.push({ id: label || 'zone', kind: 'zone', status: 'anchor',
            message: `bar ${from} never trades in ${bottom}–${top} — the box is anchored ` +
                     `to a candle that did not create it` });
        }
        const { brk, dep } = zoneBreakBar(candles, top, bottom, from, mode, tol);
        if (dep === null) {
          violations.push({ id: label || 'zone', kind: 'zone', status: 'invalid',
            message: `price never leaves the zone after bar ${from}` });
          return null;
        }
        return brk;
      });

      const x1 = X(from) - step / 2;
      const x2 = end === null ? plotR : X(end) + step / 2;
      const yT = Y(top), yB = Y(bottom);
      const w = x2 - x1, h = Math.max(2, yB - yT);

      const rect = el('rect', {
        class: `ls-mk-zone ls-mk-zone-${tone}`, x: x1, y: yT, width: w, height: h
      });
      gZone.appendChild(rect);

      const s = schedule('zone', at, dur);
      if (A) {                                 // wipe the zone open left → right
        const id = `lsclip${++uid}`;
        const cp = el('clipPath', { id });
        const cr = el('rect', { x: x1, y: yT - 2, width: 0, height: h + 4 });
        cp.appendChild(cr); defs.appendChild(cp);
        rect.setAttribute('clip-path', `url(#${id})`);
        cue(rect, 'wipe', s.t0, s.dur, { clip: cr, full: w });
      }

      if (label) {
        const anchor = align === 'right' ? 'end' : align === 'left' ? 'start' : 'middle';
        const lx = align === 'right' ? x2 - 14 : align === 'left' ? x1 + 14 : (x1 + x2) / 2;
        const t = el('text', {
          class: `ls-mk-label ls-mk-${tone}-t`, x: lx, y: (yT + yB) / 2,
          'text-anchor': anchor, 'dominant-baseline': 'central'
        });
        t.textContent = label;
        gLabel.appendChild(t);
        cueLabel(t, s.t0 + s.dur);
      }
      return api;
    }

    // ---- 3. structure zigzag ---------------------------------------------
    function structure(points, { tone = 'accent', projection = false, at, dur } = {}) {
      const d = points.map((p, k) => `${k ? 'L' : 'M'}${X(p.i)},${Y(p.price)}`).join(' ');
      const path = el('path', {
        class: `ls-mk-zigzag ls-mk-${tone}` + (projection ? ' ls-mk-dashed' : ''),
        d, fill: 'none'
      });
      gStruct.appendChild(path);
      const s = schedule(projection ? 'projection' : 'structure', at, dur);
      cue(path, 'stroke', s.t0, s.dur);
      return api;
    }

    // ---- 4. swing point: hollow marker + (n) label ------------------------
    function swing({ i, price, label, place = 'below', marker = true, at, dur }) {
      const x = X(i), y = Y(price);
      const s = schedule('swing', at, dur);
      const parts = [];
      if (marker) {
        const c = el('circle', { class: 'ls-mk-marker', cx: x, cy: y, r: 5.5 });
        gStruct.appendChild(c); parts.push(c);
      }
      if (label) {
        const t = el('text', {
          class: 'ls-mk-swing', x, y: place === 'below' ? y + 24 : y - 17,
          'text-anchor': 'middle'
        });
        t.textContent = label;
        gLabel.appendChild(t); parts.push(t);
      }
      cue(parts, 'fade', s.t0, s.dur);
      return api;
    }

    // ---- 5. fib scale -----------------------------------------------------
    function fib({ i, priceFrom, priceTo, levels = [0, 0.5, 0.618, 1],
                   width: fw = 90, at, dur }) {
      const x = X(i);
      const parts = [];
      const rail = el('line', {
        class: 'ls-mk-line ls-mk-accent ls-mk-dashed',
        x1: x, x2: x, y1: Y(priceFrom), y2: Y(priceTo)
      });
      gStruct.appendChild(rail);
      const s = schedule('fib', at, dur);
      cue(rail, 'stroke', s.t0, s.dur);

      levels.forEach(lv => {
        const y = Y(priceFrom + (priceTo - priceFrom) * lv);
        const tick = el('line', {
          class: 'ls-mk-line ls-mk-muted', x1: x, x2: x + fw, y1: y, y2: y
        });
        gStruct.appendChild(tick);
        const t = el('text', {
          class: 'ls-mk-fib', x: x - 8, y, 'text-anchor': 'end',
          'dominant-baseline': 'central'
        });
        t.textContent = String(lv);
        gLabel.appendChild(t);
        parts.push(tick, t);
      });
      cue(parts, 'fade', s.t0 + s.dur * 0.5, A ? A.labelDur : 0);
      return api;
    }

    // ---- 6. trendline with rotated inline label ---------------------------
    function trend({ i1, p1, i2, p2, label, extend = true, tone = 'primary', at, dur }) {
      let x1 = X(i1), y1 = Y(p1), x2 = X(i2), y2 = Y(p2);
      if (extend) {                            // project to the right edge
        const m = (y2 - y1) / (x2 - x1);
        y2 = y1 + m * (plotR - x1); x2 = plotR;
      }
      const line = el('line', { class: `ls-mk-line ls-mk-${tone}`, x1, y1, x2, y2 });
      gStruct.appendChild(line);
      const s = schedule('trend', at, dur);
      cue(line, 'stroke', s.t0, s.dur);

      if (label) {
        const fx = 0.84, mx = x1 + (x2 - x1) * fx, my = y1 + (y2 - y1) * fx;
        const ang = Math.atan2(y2 - y1, x2 - x1) * 180 / Math.PI;
        const t = el('text', {
          class: `ls-mk-label ls-mk-${tone}-t`, x: mx, y: my, dy: -9,
          'text-anchor': 'middle', transform: `rotate(${ang} ${mx} ${my})`
        });
        t.textContent = label;
        gLabel.appendChild(t);
        cueLabel(t, s.t0 + s.dur);
      }
      return api;
    }

    // ---- 7. invalidation cross -------------------------------------------
    function invalid({ i, price, size = 11, at, dur }) {
      const x = X(i), y = Y(price);
      const g = el('g', { class: 'ls-mk-invalid' });
      g.appendChild(el('line', { x1: x - size, y1: y - size, x2: x + size, y2: y + size }));
      g.appendChild(el('line', { x1: x + size, y1: y - size, x2: x - size, y2: y + size }));
      gLabel.appendChild(g);
      const s = schedule('invalid', at, dur);
      cue(g, 'fade', s.t0, s.dur);
      return api;
    }

    // ---- 8. fixed-range volume profile ------------------------------------
    /* Histogram of traded activity across the leg, drawn inside the range and
       anchored to its left edge. Volume is approximated from the candles in
       range when the caller has no per-bin data. Returns the POC price. */
    function volumeProfile({ from, to, bins = 26, widthPct = 0.32,
                             valueArea = 0.68, volumes = null, box = true, at, dur }) {
      const x1 = X(from) - step / 2, x2 = X(to) + step / 2;
      const seg = candles.slice(from, to + 1);
      const pHi = Math.max(...seg.map(c => c.h)), pLo = Math.min(...seg.map(c => c.l));
      const bh = (pHi - pLo) / bins;

      let vol = volumes;
      if (!vol) {                              // time-at-price approximation
        vol = new Array(bins).fill(0);
        seg.forEach(c => {
          const a = Math.max(0, Math.floor((Math.min(c.l, c.o, c.c) - pLo) / bh));
          const b = Math.min(bins - 1, Math.floor((Math.max(c.h, c.o, c.c) - pLo) / bh));
          const body = Math.abs(c.c - c.o) + bh;
          for (let k = a; k <= b; k++) vol[k] += body;
        });
      }
      const vMax = Math.max(...vol);
      const pocIdx = vol.indexOf(vMax);
      const pocPrice = pLo + (pocIdx + 0.5) * bh;

      // value area: grow outward from the POC until the share is covered
      const total = vol.reduce((a, b) => a + b, 0);
      let acc = vol[pocIdx], loI = pocIdx, hiI = pocIdx;
      while (acc < total * valueArea && (loI > 0 || hiI < bins - 1)) {
        const dn = loI > 0 ? vol[loI - 1] : -1;
        const up = hiI < bins - 1 ? vol[hiI + 1] : -1;
        if (up >= dn) acc += vol[++hiI]; else acc += vol[--loI];
      }

      const g = el('g', { class: 'ls-mk-vp' });
      const maxW = (x2 - x1) * widthPct;
      vol.forEach((v, k) => {
        const y = Y(pLo + (k + 1) * bh);
        g.appendChild(el('rect', {
          class: 'ls-mk-vp-bar' + (k >= loI && k <= hiI ? ' ls-mk-vp-va' : ''),
          x: x1, y, width: Math.max(1, (v / vMax) * maxW),
          height: Math.max(1, Y(pLo) - Y(pLo + bh) - 1)
        }));
      });
      gZone.appendChild(g);

      if (box) gZone.appendChild(el('rect', {
        class: 'ls-mk-vp-box', x: x1, y: Y(pHi), width: x2 - x1, height: Y(pLo) - Y(pHi)
      }));

      const s = schedule('vp', at, dur);
      if (A) {
        const id = `lsclip${++uid}`;
        const cp = el('clipPath', { id });
        const cr = el('rect', { x: x1 - 2, y: Y(pHi) - 2, width: 0, height: Y(pLo) - Y(pHi) + 4 });
        cp.appendChild(cr); defs.appendChild(cp);
        g.setAttribute('clip-path', `url(#${id})`);
        cue(g, 'wipe', s.t0, s.dur, { clip: cr, full: x2 - x1 });
      }
      api.pocPrice = pocPrice;
      return api;
    }

    // ---- 9. point of control ---------------------------------------------
    function poc({ price, from, label = 'POC', at, dur }) {
      const y = Y(price), x1 = X(from) - step / 2;
      const line = el('line', { class: 'ls-mk-poc', x1, y1: y, x2: plotR, y2: y });
      gStruct.appendChild(line);
      const s = schedule('level', at, dur);
      cue(line, 'stroke', s.t0, s.dur);
      if (label) {                            // label rides the right end of the rail
        const t = el('text', {
          class: 'ls-mk-poc-t', x: plotR - 10, y, dy: -12, 'text-anchor': 'end'
        });
        t.textContent = label;
        gLabel.appendChild(t);
        cueLabel(t, s.t0 + s.dur);
      }
      return api;
    }

    // ---- 10. position tool (entry / stop / target) ------------------------
    function position({ from, to = null, entry, stop, target, at, dur }) {
      const x1 = X(from) - step / 2;
      const x2 = to === null ? plotR : X(to) + step / 2;
      const w = x2 - x1;
      const yE = Y(entry), yS = Y(stop), yT = Y(target);

      const gt = el('rect', { class: 'ls-mk-pos-target', x: x1, y: Math.min(yE, yT),
                              width: w, height: Math.abs(yE - yT) });
      const gs = el('rect', { class: 'ls-mk-pos-stop', x: x1, y: Math.min(yE, yS),
                              width: w, height: Math.abs(yE - yS) });
      const ln = el('line', { class: 'ls-mk-pos-entry', x1, y1: yE, x2, y2: yE });
      gZone.appendChild(gt); gZone.appendChild(gs); gStruct.appendChild(ln);

      const s = schedule('zone', at, dur);
      if (A) {
        const id = `lsclip${++uid}`;
        const cp = el('clipPath', { id });
        const cr = el('rect', { x: x1, y: Math.min(yT, yS) - 2, width: 0,
                                height: Math.abs(yT - yS) + 4 });
        cp.appendChild(cr); defs.appendChild(cp);
        [gt, gs, ln].forEach(nd => nd.setAttribute('clip-path', `url(#${id})`));
        cue([gt], 'wipe', s.t0, s.dur, { clip: cr, full: w });
      }
      return api;
    }

    // ---- gridlines --------------------------------------------------------
    function grid(count = 4) {
      for (let k = 1; k < count; k++) {
        const y = plotT + ((plotB - plotT) / count) * k;
        gGrid.appendChild(el('line', { class: 'ls-grid', x1: plotL, x2: plotR, y1: y, y2: y }));
      }
      return api;
    }

    // ---- layout + motion --------------------------------------------------
    /* Must run after the SVG is in the document: measures every label, cuts the
       gap in its line, then captures stroke lengths for the draw-on reveal. */
    function layout() {
      jobs.forEach(f => f()); jobs.length = 0;
      if (!A) return api;
      track.forEach(e => {
        if (e.kind !== 'stroke') return;
        e.len = e.nodes.map(nd => {
          const L = nd.getTotalLength ? nd.getTotalLength() : 0;
          return L || 1;
        });
      });
      seek(0);
      return api;
    }

    function duration() {
      return track.reduce((m, e) => Math.max(m, e.t0 + e.dur), 0);
    }

    /* Deterministic: the visual state at time t. Drives both live playback
       and frame-accurate capture. */
    function seek(t) {
      track.forEach(e => {
        const p = easeOut(clamp01(e.dur > 0 ? (t - e.t0) / e.dur : (t >= e.t0 ? 1 : 0)));
        if (e.kind === 'stroke') {
          e.nodes.forEach((nd, k) => {
            const L = (e.len && e.len[k]) || 1;
            nd.style.strokeDasharray = L;
            nd.style.strokeDashoffset = L * (1 - p);
          });
        } else if (e.kind === 'wipe') {
          e.clip.setAttribute('width', e.full * p);
        } else {
          e.nodes.forEach(nd => { nd.style.opacity = p; });
        }
      });
      return api;
    }

    function play(onDone) {
      const total = duration(), t0 = performance.now();
      (function frame(now) {
        const t = (now - t0) / 1000;
        seek(t);
        if (t < total) requestAnimationFrame(frame);
        else if (onDone) onDone();
      })(t0);
      return api;
    }

    const api = {
      svg, X, Y, drawCandles, grid, level, zone, structure,
      swing, fib, trend, invalid, volumeProfile, poc, position,
      layout, seek, play, duration,
      get violations() { return violations; },
      get timeline() { return track; }
    };
    return api;
  }

  /* Standalone audit — same rules, no drawing. Mirrors verify_drawing.py so a
     chart can be checked before it is built, or in a test. */
  LSChart.audit = function (candles, drawings) {
    const last = candles.length - 1;
    return drawings.map(d => {
      const id = d.id || d.kind || 'drawing';
      const start = d.from == null ? 0 : d.from;
      const end = d.to == null ? null : d.to;
      const mode = d.mode || 'touch';
      const tol = d.tolerance || 0;
      const F = (status, message, should_end_at = null) =>
        ({ id, kind: d.kind, status, message, should_end_at });

      if (!Number.isInteger(start) || start < 0 || start > last)
        return F('invalid', `origin bar ${start} is outside the series (0..${last})`);
      if (end !== null && end < start)
        return F('invalid', `ends at bar ${end}, before it starts at ${start}`);

      if (d.kind === 'projection')
        return end !== null && end <= last
          ? F('too_short', `a projection should extend past the last bar (${last})`)
          : F('ok', 'projection extends beyond the last bar, as intended');

      if (d.kind === 'target') {
        let hit = null;
        for (let j = start; j <= last; j++)
          if (levelHolds(d.price, tol)(candles[j])) { hit = j; break; }
        return hit === null
          ? F('ok', `untapped target at ${d.price}; price never gets there`)
          : F('too_long', `declared a target, but price reaches ${d.price} at bar ${hit}`, hit);
      }

      let brk, dep;
      if (d.kind === 'zone') {
        if (d.top <= d.bottom) return F('invalid', `top must be above bottom`);
        if (!zoneOverlap(d.top, d.bottom, tol)(candles[start]))
          return F('anchor', `bar ${start} never trades in ${d.bottom}–${d.top}`);
        ({ brk, dep } = zoneBreakBar(candles, d.top, d.bottom, start, mode, tol));
        if (dep === null) return F('invalid', `price never leaves the zone after bar ${start}`);
      } else {
        if (!levelHolds(d.price, tol)(candles[start]))
          return F('anchor', `bar ${start} never reaches ${d.price}`);
        ({ brk, dep } = levelBreak(candles, d.price, start, mode, d.side || 'auto', tol));
        if (dep === null) return F('invalid', `price never leaves ${d.price} after bar ${start}`);
        if (brk === null) {
          let seen = false;
          for (let j = start; j <= last; j++)
            if (levelHolds(d.price, tol)(candles[j])) { seen = true; break; }
          if (!seen) return F('floating', `price never returns to ${d.price} after bar ${start}`);
        }
      }

      if (brk === null)
        return (end === null || end === last)
          ? F('ok', 'never broken; runs to the last bar')
          : F('too_short', `never broken, so it should run to bar ${last}, not ${end}`, last);
      if (end === null) return F('too_long', `runs to the right edge but bar ${brk} breaks it`, brk);
      if (end > brk)    return F('too_long', `ends at bar ${end} but bar ${brk} already broke it`, brk);
      if (end < brk)    return F('too_short', `ends at bar ${end} but survives until bar ${brk}`, brk);
      return F('ok', `ends exactly at the breaking bar ${brk}`);
    });
  };

  LSChart.CADENCE = CADENCE;
  global.LSChart = LSChart;
})(window);
