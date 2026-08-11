/* ==========================================================================
   Liquidity State — Chart Markup Engine
   Adopted markup method: inline-labelled level lines, outlined zones (OB),
   swing-labelled structure zigzag, fib scale, trendline, projection path.
   Renders SVG; all colors come from brand.css custom properties.

   Coordinates are expressed as (candle index, price) — never pixels — so
   markup stays locked to the data when the canvas or range changes.
   ========================================================================== */

(function (global) {
  'use strict';

  const NS = 'http://www.w3.org/2000/svg';
  const el = (n, a = {}) => {
    const e = document.createElementNS(NS, n);
    for (const k in a) e.setAttribute(k, a[k]);
    return e;
  };

  function LSChart(opts) {
    const {
      mount,
      width = 936,
      height = 620,
      candles = [],
      padding = { top: 28, right: 150, bottom: 40, left: 20 },
      priceRange = null,
      candleWidth = null,
      barsRight = 6            // empty bars kept at the right for projections
    } = opts;

    const host = typeof mount === 'string' ? document.querySelector(mount) : mount;
    const svg = el('svg', {
      viewBox: `0 0 ${width} ${height}`,
      width: '100%', class: 'ls-chart'
    });
    host.appendChild(svg);

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

    // deferred text-measurement jobs (run in layout())
    const jobs = [];

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
    function level({ price, label, from = 0, to = null, tone = 'primary', dashed = false }) {
      const y = Y(price);
      const x1 = X(from) - step / 2;
      const x2 = to === null ? plotR : X(to) + step / 2;
      const cls = `ls-mk-line ls-mk-${tone}` + (dashed ? ' ls-mk-dashed' : '');

      const lineA = el('line', { class: cls, x1, y1: y, x2, y2: y });
      const lineB = el('line', { class: cls, x1, y1: y, x2, y2: y });
      gStruct.appendChild(lineA); gStruct.appendChild(lineB);

      if (!label) { lineB.remove(); return api; }

      const t = el('text', {
        class: `ls-mk-label ls-mk-${tone}-t`, x: (x1 + x2) / 2, y,
        'text-anchor': 'middle', 'dominant-baseline': 'central'
      });
      t.textContent = label;
      gLabel.appendChild(t);

      jobs.push(() => {                       // split the line around the text
        const w = t.getComputedTextLength() / 2 + 10;
        const mid = (x1 + x2) / 2;
        lineA.setAttribute('x2', mid - w);
        lineB.setAttribute('x1', mid + w);
      });
      return api;
    }

    // ---- 2. zone / order block -------------------------------------------
    function zone({ from, to = null, top, bottom, label, tone = 'primary', align = 'center' }) {
      const x1 = X(from) - step / 2;
      const x2 = to === null ? plotR : X(to) + step / 2;
      const yT = Y(top), yB = Y(bottom);
      gZone.appendChild(el('rect', {
        class: `ls-mk-zone ls-mk-zone-${tone}`,
        x: x1, y: yT, width: x2 - x1, height: Math.max(2, yB - yT)
      }));
      if (label) {
        const anchor = align === 'right' ? 'end' : align === 'left' ? 'start' : 'middle';
        const lx = align === 'right' ? x2 - 14 : align === 'left' ? x1 + 14 : (x1 + x2) / 2;
        const t = el('text', {
          class: `ls-mk-label ls-mk-${tone}-t`, x: lx, y: (yT + yB) / 2,
          'text-anchor': anchor, 'dominant-baseline': 'central'
        });
        t.textContent = label;
        gLabel.appendChild(t);
      }
      return api;
    }

    // ---- 3. structure zigzag ---------------------------------------------
    function structure(points, { tone = 'accent', projection = false } = {}) {
      const d = points.map((p, k) => `${k ? 'L' : 'M'}${X(p.i)},${Y(p.price)}`).join(' ');
      gStruct.appendChild(el('path', {
        class: `ls-mk-zigzag ls-mk-${tone}` + (projection ? ' ls-mk-dashed' : ''),
        d, fill: 'none'
      }));
      return api;
    }

    // ---- 4. swing point: hollow marker + (n) label ------------------------
    function swing({ i, price, label, place = 'below', marker = true }) {
      const x = X(i), y = Y(price);
      if (marker) gStruct.appendChild(el('circle', { class: 'ls-mk-marker', cx: x, cy: y, r: 5.5 }));
      if (label) {
        const t = el('text', {
          class: 'ls-mk-swing', x, y: place === 'below' ? y + 24 : y - 17,
          'text-anchor': 'middle'
        });
        t.textContent = label;
        gLabel.appendChild(t);
      }
      return api;
    }

    // ---- 5. fib scale -----------------------------------------------------
    function fib({ i, priceFrom, priceTo, levels = [0, 0.5, 0.618, 1], width: fw = 90 }) {
      const x = X(i);
      gStruct.appendChild(el('line', {
        class: 'ls-mk-line ls-mk-accent ls-mk-dashed',
        x1: x, x2: x, y1: Y(priceFrom), y2: Y(priceTo)
      }));
      levels.forEach(lv => {
        const p = priceFrom + (priceTo - priceFrom) * lv;
        const y = Y(p);
        gStruct.appendChild(el('line', {
          class: 'ls-mk-line ls-mk-muted', x1: x, x2: x + fw, y1: y, y2: y
        }));
        const t = el('text', {
          class: 'ls-mk-fib', x: x - 8, y, 'text-anchor': 'end', 'dominant-baseline': 'central'
        });
        t.textContent = String(lv);
        gLabel.appendChild(t);
      });
      return api;
    }

    // ---- 6. trendline with rotated inline label ---------------------------
    function trend({ i1, p1, i2, p2, label, extend = true, tone = 'primary' }) {
      let x1 = X(i1), y1 = Y(p1), x2 = X(i2), y2 = Y(p2);
      if (extend) {                            // project to the right edge
        const m = (y2 - y1) / (x2 - x1);
        y2 = y1 + m * (plotR - x1); x2 = plotR;
      }
      gStruct.appendChild(el('line', { class: `ls-mk-line ls-mk-${tone}`, x1, y1, x2, y2 }));
      if (label) {
        const fx = 0.84, mx = x1 + (x2 - x1) * fx, my = y1 + (y2 - y1) * fx;
        const ang = Math.atan2(y2 - y1, x2 - x1) * 180 / Math.PI;
        const t = el('text', {
          class: `ls-mk-label ls-mk-${tone}-t`, x: mx, y: my, dy: -9,
          'text-anchor': 'middle', transform: `rotate(${ang} ${mx} ${my})`
        });
        t.textContent = label;
        gLabel.appendChild(t);
      }
      return api;
    }

    // ---- 7. invalidation cross -------------------------------------------
    function invalid({ i, price, size = 11 }) {
      const x = X(i), y = Y(price);
      const g = el('g', { class: 'ls-mk-invalid' });
      g.appendChild(el('line', { x1: x - size, y1: y - size, x2: x + size, y2: y + size }));
      g.appendChild(el('line', { x1: x + size, y1: y - size, x2: x - size, y2: y + size }));
      gLabel.appendChild(g);
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

    // run deferred text measurements — call after the SVG is in the document
    function layout() { jobs.forEach(f => f()); jobs.length = 0; return api; }

    const api = {
      svg, X, Y, drawCandles, grid, level, zone, structure,
      swing, fib, trend, invalid, layout
    };
    return api;
  }

  global.LSChart = LSChart;
})(window);
