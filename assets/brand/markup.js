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

  /* A level is a wick tip, not a price somewhere inside the candle: drawn
     mid-candle it marks a price the candle merely passed through, which is
     every price in its range. Returns the tip it should sit on. */
  const nearestTip = (c, price) =>
    Math.abs(c.h - price) <= Math.abs(c.l - price) ? c.h : c.l;
  const onTip = (c, price, tol) =>
    Math.min(Math.abs(price - c.h), Math.abs(price - c.l)) <= tol;

  /* A box wraps its candles whole — cropped to the body it hides the wick,
     which is the part that did the sweeping. */
  function zoneExtent(candles, start, span) {
    let hi = -Infinity, lo = Infinity;
    for (let k = start; k < start + Math.max(1, span || 1) && k < candles.length; k++) {
      hi = Math.max(hi, candles[k].h); lo = Math.min(lo, candles[k].l);
    }
    return { hi, lo };
  }

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
      barsVisible = null,      /* how many bars fill the plot. Set this for replay:
                                  otherwise pitch is derived from the whole series,
                                  so a long series draws hair-thin candles and the
                                  replay reads as half speed even at the right rate —
                                  perceived speed is pitch x rate, not rate alone. */
      anim = null,             // pass {} for defaults, or override any CADENCE key
      autoTerminate = false,   // end levels/zones at the candle that broke them
      snapToCandle = false,    // pull levels onto wick tips, expand boxes to full candles
      tolerance = 0
    } = opts;

    /* Drawings that don't hold up. Read chart.violations after layout(). */
    const violations = [];
    /* Everything snapToCandle silently changed. Snapping edits your numbers,
       so it reports what it did — a correction you can't see is a correction
       you can't check. */
    const corrections = [];

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
    /* Everything anchored to a bar index lives inside gPan so replay can jump
       the viewport by whole candle pitches. Grid and price scale stay outside:
       they are horizontal and must not travel with the bars. */
    const gPan = el('g', { class: 'ls-layer-pan' });
    svg.appendChild(gGrid);
    [gZone, gCandle, gStruct, gLabel].forEach(g => gPan.appendChild(g));
    svg.appendChild(gPan);

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
    const n = barsVisible ? barsVisible : candles.length + barsRight;
    const step = (plotR - plotL) / n;
    const cw = candleWidth || Math.max(3, step * 0.58);

    const X = i => plotL + step * (i + 0.5);
    const Y = p => plotB - ((p - lo) / (hi - lo)) * (plotB - plotT);

    const candleNodes = [];  // one per bar, for replay reveal
    let panX = 0;            // current viewport offset, set by the replay handler
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
        candleNodes.push(g);
      });
      return api;
    }

    // ---- 1. level line with inline centred label --------------------------
    // The line breaks around the text — the signature of this markup method.
    function level({ price, label, from = 0, to, tone = 'primary',
                     dashed = false, at, dur, mode = 'touch', side = 'auto',
                     tol = tolerance, edge = true, target = false }) {
      /* A target marks price that hasn't happened yet — untapped liquidity, a
         take-profit. It has no anchor candle, cannot be broken, and must never
         be snapped onto one. It only has to stay untouched. */
      if (target) { edge = false; to = 'edge'; }

      const c0 = candles[from];
      if (c0 && edge && !onTip(c0, price, tol)) {
        const tip = nearestTip(c0, price);
        if (snapToCandle) {
          corrections.push({ id: label || 'level', kind: 'level', field: 'price',
            from: price, to: tip, why: 'pulled onto the wick tip of bar ' + from });
          price = tip;
        }
        else violations.push({ id: label || `level@${price}`, kind: 'level', status: 'edge',
          message: `sits mid-candle at ${price}; bar ${from} runs ${c0.l}–${c0.h}, ` +
                   `so the level is ${tip}` });
      }
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
                    align = 'center', at, dur, mode = 'touch', tol = tolerance,
                    whole = true, spanBars = 1 }) {
      if (candles[from] && whole) {
        const { hi, lo } = zoneExtent(candles, from, spanBars);
        if (Math.abs(top - hi) > tol || Math.abs(bottom - lo) > tol) {
          if (snapToCandle) {
            corrections.push({ id: label || 'zone', kind: 'zone', field: 'extent',
              from: [bottom, top], to: [lo, hi],
              why: 'expanded to wrap bar ' + from + ' wick to wick' });
            top = hi; bottom = lo;
          }
          else violations.push({ id: label || 'zone', kind: 'zone', status: 'partial',
            message: `is ${bottom}–${top} but the candle(s) it wraps run ${lo}–${hi}; ` +
                     `the box must cover them wick to wick` });
        }
      }
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
                             valueArea = 0.70, volumes = null, box = true,
                             showVA = false, nodes = false, developing = false,
                             at, dur }) {
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
      const rowPrice = k => pLo + (k + 0.5) * bh;

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

      /* Everything the profile draws besides the histogram — the range box, the
         value-area shading, its edges and their labels — is scheduled with the
         histogram. Left uncued it would sit on the chart from frame zero and
         announce the value area before the profile that measured it exists. */
      const chrome = [];

      if (box) {
        const r = el('rect', {
          class: 'ls-mk-vp-box', x: x1, y: Y(pHi), width: x2 - x1, height: Y(pLo) - Y(pHi)
        });
        gZone.appendChild(r); chrome.push(r);
      }

      const s = schedule('vp', at, dur);
      if (A) {
        const id = `lsclip${++uid}`;
        const cp = el('clipPath', { id });
        const cr = el('rect', { x: x1 - 2, y: Y(pHi) - 2, width: 0, height: Y(pLo) - Y(pHi) + 4 });
        cp.appendChild(cr); defs.appendChild(cp);
        g.setAttribute('clip-path', `url(#${id})`);
        cue(g, 'wipe', s.t0, s.dur, { clip: cr, full: x2 - x1 });
      }
      /* Value area edges. The spec wants the percentage the indicator is
         actually set to — 70% is only the usual default, not a law. */
      const VAH = rowPrice(hiI) + bh / 2, VAL = rowPrice(loI) - bh / 2;

      if (showVA) {
        // insertBefore(g): the profile's own bars have to stay readable, so the
        // shading goes underneath them rather than on top
        const band = el('rect', {
          class: 'ls-mk-va-band', x: x1, y: Y(VAH),
          width: plotR - x1, height: Math.max(2, Y(VAL) - Y(VAH))
        });
        gZone.insertBefore(band, g); chrome.push(band);
        [['VAH', VAH], ['VAL', VAL]].forEach(([nm, pv]) => {
          const ln = el('line', {
            class: 'ls-mk-va-edge', x1, x2: plotR, y1: Y(pv), y2: Y(pv)
          });
          gStruct.appendChild(ln); chrome.push(ln);
          const t = el('text', {
            class: 'ls-mk-va-t', x: plotR - 8, y: Y(pv), dy: nm === 'VAH' ? -8 : 16,
            'text-anchor': 'end'
          });
          t.textContent = nm;
          gLabel.appendChild(t); chrome.push(t);
        });
      }

      if (A && chrome.length) cue(chrome, 'fade', s.t0 + s.dur * 0.45, s.dur * 0.55);

      /* HVN / LVN are drawn as BANDS the thickness of the rows that form them.
         Drawn as a line they claim a precision the profile does not have — a
         node is a region of acceptance, not a price. */
      const hvn = [], lvn = [];
      if (nodes) {
        const mean = total / bins;
        for (let k = 1; k < bins - 1; k++) {
          const isPeak = vol[k] >= vol[k-1] && vol[k] >= vol[k+1] && vol[k] > mean * 1.25;
          const isVoid = vol[k] <= vol[k-1] && vol[k] <= vol[k+1] && vol[k] < mean * 0.55;
          if (!isPeak && !isVoid) continue;
          let a = k, b = k;                         // grow to the rows forming it
          while (a > 0      && (isPeak ? vol[a-1] > mean : vol[a-1] < mean)) a--;
          while (b < bins-1 && (isPeak ? vol[b+1] > mean : vol[b+1] < mean)) b++;
          const top = rowPrice(b) + bh / 2, bottom = rowPrice(a) - bh / 2;
          (isPeak ? hvn : lvn).push({ top, bottom });
          gZone.insertBefore(el('rect', {
            class: isPeak ? 'ls-mk-hvn' : 'ls-mk-lvn',
            x: x1, y: Y(top), width: plotR - x1, height: Math.max(2, Y(bottom) - Y(top))
          }), g);
          k = b;                                    // don't re-emit the same node
        }
      }

      /* Results live on api.profile, not loose on api: a flat `api.poc` would
         collide with the poc() method and silently hand you a function where
         you expected a price. */
      api.profile = { poc: pocPrice, vah: VAH, val: VAL, hvn, lvn, developing,
                      hi: pHi, lo: pLo };
      api.pocPrice = pocPrice;              // kept: already in use
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
      /* "to the right edge" means the edge of the SERIES, not of the plot.
         On a replayed chart the bars run past plotR and travel into view on
         gPan, so anchoring to plotR puts x2 left of x1 and the boxes come out
         with a negative width — which renders as nothing at all. */
      const x2 = to === null ? Math.max(plotR, X(candles.length - 1) + step / 2)
                             : X(to) + step / 2;
      const w = Math.max(0, x2 - x1);
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

    // ---- 11. numbered anchor ---------------------------------------------
    /* A hollow ring on the exact pixel the element is anchored to, carrying the
       step number. The ring is what proves the line starts on the wick tip
       rather than near it. */
    function anchor({ i, price, n, at, dur, r = 13 }) {
      const x = X(i), y = Y(price);
      const g = el('g', { class: 'ls-mk-anchor' });
      g.appendChild(el('circle', { class: 'ls-mk-anchor-ring', cx: x, cy: y, r }));
      const t = el('text', {
        class: 'ls-mk-anchor-n', x, y, 'text-anchor': 'middle',
        'dominant-baseline': 'central'
      });
      t.textContent = String(n);
      g.appendChild(t);
      gLabel.appendChild(g);
      const s = schedule('swing', at, dur);
      cue(g, 'fade', s.t0, s.dur);
      return api;
    }

    // ---- 12. sticker + leader --------------------------------------------
    /* The label never sits on a candle. It floats in empty space and reaches
       the price with one calm curve that stops short of the target, so the
       candle it is talking about stays fully readable. */
    function sticker({ i, price, text, n, dx = 0, dy = -90, gap = 16,
                       side = 'auto', at, dur }) {
      const tx = X(i), ty = Y(price);
      const cx = tx + dx, cy = ty + dy;

      const g = el('g', { class: 'ls-mk-sticker' });
      const box = el('rect', { class: 'ls-mk-sticker-box', rx: 10, ry: 10 });
      const label = el('text', {
        class: 'ls-mk-sticker-t', x: cx, y: cy,
        'text-anchor': 'middle', 'dominant-baseline': 'central'
      });
      label.textContent = (n != null ? `${n} · ` : '') + text;
      const leader = el('path', { class: 'ls-mk-leader', fill: 'none' });
      gLabel.appendChild(leader); gLabel.appendChild(g);
      g.appendChild(box); g.appendChild(label);

      jobs.push(() => {
        const w = label.getComputedTextLength() + 34, h = 42;
        /* Keep the box inside the plot. A sticker that runs off the edge loses
           the end of its own label, and the offset that was fine on one bar is
           wrong once the viewport pans. */
        let bx = cx - w / 2;
        bx = Math.max(plotL + 4, Math.min(bx, plotR - w - 4));
        const cxc = bx + w / 2;
        label.setAttribute('x', cxc);
        box.setAttribute('x', bx);         box.setAttribute('y', cy - h / 2);
        box.setAttribute('width', w);      box.setAttribute('height', h);

        // Leave from the box edge facing the target, arrive just short of it.
        const from = side === 'auto' ? (Math.abs(dy) > Math.abs(dx)
          ? { x: cxc, y: cy + Math.sign(dy || 1) * -h / 2 }
          : { x: cxc + Math.sign(dx || 1) * -w / 2, y: cy }) : { x: cxc, y: cy };
        const len = Math.hypot(tx - from.x, ty - from.y) || 1;
        const end = { x: tx - (tx - from.x) / len * gap,
                      y: ty - (ty - from.y) / len * gap };
        const mx = (from.x + end.x) / 2 + (end.y - from.y) * 0.16;
        const my = (from.y + end.y) / 2 - (end.x - from.x) * 0.16;
        leader.setAttribute('d', `M${from.x},${from.y} Q${mx},${my} ${end.x},${end.y}`);
      });

      const s = schedule('level', at, dur);
      cue([g, leader], 'fade', s.t0, s.dur, { anchorX: tx });
      const cueEntry = track.length ? track[track.length - 1] : null;
      if (cueEntry) jobs.push(() => {
        // recorded for the visibility test in seek(); the box, not the anchor,
        // is what actually gets cut by the plot edge
        cueEntry.boxX = +box.getAttribute('x');
        cueEntry.boxW = +box.getAttribute('width');
      });
      return api;
    }

    // ---- 13. price scale --------------------------------------------------
    /* Round prices down the right edge. Reading a level off the chart is only
       possible when the scale is actually on it. */
    function priceScale({ step, decimals = 1, at, dur } = {}) {
      const span = hi - lo;
      if (!step) {                                   // pick a round-ish step
        const raw = span / 5;
        const mag = Math.pow(10, Math.floor(Math.log10(raw)));
        step = [1, 2, 2.5, 5, 10].map(m => m * mag)
                 .find(v => v >= raw) || mag * 10;
      }
      const parts = [];
      for (let p = Math.ceil(lo / step) * step; p <= hi; p += step) {
        const y = Y(p);
        const t = el('text', {
          class: 'ls-mk-price', x: plotR + 14, y,
          'text-anchor': 'start', 'dominant-baseline': 'central'
        });
        t.textContent = p.toFixed(decimals);
        gLabel.appendChild(t);
        gGrid.appendChild(el('line', { class: 'ls-grid', x1: plotL, x2: plotR, y1: y, y2: y }));
        parts.push(t);
      }
      const s = schedule('level', at, dur);
      cue(parts, 'fade', s.t0, s.dur);
      return api;
    }

    // ---- 14. bar replay ---------------------------------------------------
    /* Print the candles forward the way TradingView's bar replay does.

       Measured from the reference recording: 4.71 candles/sec (one bar every
       ~212ms), which matches the 5x setting shown in its toolbar. The viewport
       does NOT scroll smoothly — when a bar prints, the chart jumps by exactly
       one candle pitch. That discreteness is the whole feel of it; interpolating
       the pan turns a replay into a camera move and reads as a different thing.

       `window` is how many bars stay on screen before the jumping starts. */
    function replay({ rate = 4.71, window: win = 40, at = 0, start = 1,
                      holds = [] } = {}) {
      if (!A) return api;

      /* Holds are the pauses where the story gets told: the replay freezes on
         the bar that just printed while that step's markup draws, then runs on.
         Without them every event flashes past in 212ms and the markup lands on
         a chart that has already moved somewhere else.

         Build the piecewise timeline once so n(t) stays a lookup, and so each
         step can ask when its own hold begins. */
      const segs = [];
      let tAcc = at, prevBar = start;
      [...holds].sort((a, b) => a.atBar - b.atBar).forEach(h => {
        const tStart = tAcc + (h.atBar - prevBar) / rate;
        segs.push({ run: true, b0: prevBar, t0: tAcc, t1: tStart });
        segs.push({ run: false, b0: h.atBar, t0: tStart, t1: tStart + h.seconds });
        h.t = tStart;                       // when this step's markup should start
        tAcc = tStart + h.seconds; prevBar = h.atBar;
      });
      const tEnd = tAcc + (candles.length - prevBar) / rate;
      segs.push({ run: true, b0: prevBar, t0: tAcc, t1: tEnd });

      track.push({ kind: 'replay', t0: at, dur: tEnd - at,
                   rate, win, start, segs, nodes: candleNodes, pan: gPan });
      api.holds = holds;
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
      /* Text is measured here, so it must be measured against the real font.
         Tajawal arrives via @font-face; measuring before it loads sizes every
         sticker to fallback metrics and clips the Arabic inside it. The jobs
         are idempotent, so re-run them once the font is actually ready. */
      jobs.forEach(f => f());
      if (typeof document !== 'undefined' && document.fonts &&
          document.fonts.status !== 'loaded') {
        document.fonts.ready.then(() => { jobs.forEach(f => f()); });
      }
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
        if (e.kind === 'replay') {
          // integer bar count → the pan lands on whole pitches by construction
          let n;
          const seg = e.segs.find(g => t < g.t1) || e.segs[e.segs.length - 1];
          if (!seg.run) n = seg.b0;                       // frozen on this bar
          else n = seg.b0 + Math.floor(Math.max(0, t - seg.t0) * e.rate);
          n = Math.max(0, Math.min(candles.length, n));
          e.nodes.forEach((nd, i) => { nd.style.display = i < n ? '' : 'none'; });
          panX = -Math.max(0, n - e.win) * step;
          e.pan.setAttribute('transform', `translate(${panX},0)`);
          return;
        }
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
          /* A label is hidden the moment the pan would clip it. Testing the
             anchor is not enough — the box is much wider than the point it
             hangs from, so it gets cut long before its bar leaves the plot,
             and a half-rendered word reads as a rendering bug. */
          const off = e.boxX != null &&
                      (e.boxX + panX < plotL - 2 ||
                       e.boxX + panX + e.boxW > plotR + 2);
          e.nodes.forEach(nd => {
            nd.style.opacity = p;
            nd.style.display = off ? 'none' : '';
          });
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
      anchor, sticker, priceScale, replay,
      layout, seek, play, duration,
      get violations() { return violations; },
      get corrections() { return corrections; },
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
        if (d.whole !== false) {
          const { hi, lo } = zoneExtent(candles, start, d.spanBars || 1);
          if (Math.abs(d.top - hi) > tol || Math.abs(d.bottom - lo) > tol)
            return F('partial', `is ${d.bottom}–${d.top} but the candle(s) run ${lo}–${hi}`);
        }
        ({ brk, dep } = zoneBreakBar(candles, d.top, d.bottom, start, mode, tol));
        if (dep === null) return F('invalid', `price never leaves the zone after bar ${start}`);
      } else {
        if (!levelHolds(d.price, tol)(candles[start]))
          return F('anchor', `bar ${start} never reaches ${d.price}`);
        if (d.edge !== false && !onTip(candles[start], d.price, tol))
          return F('edge', `sits mid-candle at ${d.price}; bar ${start} runs ` +
                           `${candles[start].l}–${candles[start].h}`);
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
