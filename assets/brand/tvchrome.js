/* ==========================================================================
   Liquidity State — platform chrome for the chart engine
   Price axis, time axis, grid, the live price tag, and the bar countdown.

   These are the parts of a trading screen nobody notices until they are
   missing. A chart with no axes and no clock does not read as a chart, it
   reads as an illustration of one — and the whole point of CHART-PROTOCOL.md
   §8 is that the teaching chart should be indistinguishable from the platform
   the viewer actually trades on.

   It is a LOOK, not a badge: no platform logo is drawn, nothing here claims
   the chart is a recording of one, and the palette is Liquidity State's own.

   Two things it deliberately does NOT do:

     · It does not rescale. The price/pixel ratio is fixed at construction, and
       the chart follows price by sliding its window (markup.js `follow`).
       A true rescale mid-reel either distorts every drawing on the page or
       forces a full re-layout, and both are worse than a window that lags a
       new extreme by half a second.

     · It does not read the clock. Every label comes from the bar's own `t`,
       so a frame captured at any wall time renders identically — which is the
       only way a deterministic seek(t) can survive frame capture.

   Usage:
     const tv = LSChrome(chart, { minutes: 5, decimals: 1, tick: 0.1 });
     chart.seek(t)          // tv patches seek, so the chrome updates with it
   ========================================================================== */

(function (global) {
  'use strict';

  const NS = 'http://www.w3.org/2000/svg';
  const el = (n, a = {}) => {
    const e = document.createElementNS(NS, n);
    for (const k in a) e.setAttribute(k, a[k]);
    return e;
  };
  const hhmm = m => {
    const x = ((m % 1440) + 1440) % 1440;
    return String(Math.floor(x / 60)).padStart(2, '0') + ':' + String(x % 60).padStart(2, '0');
  };
  const mmss = s => {
    const x = Math.max(0, Math.round(s));
    return String(Math.floor(x / 60)).padStart(2, '0') + ':' + String(x % 60).padStart(2, '0');
  };

  function LSChrome(chart, opts = {}) {
    const {
      candles,
      minutes = 5,
      decimals = 1,
      priceStep = null,           // axis step; auto if omitted
      timeEvery = 12,             // a time label every N bars
      gutter = 8,                 // gap between the plot and the axis
      countdown = true,
      lastTag = true
    } = opts;

    const P = chart.plot;
    const g = el('g', { class: 'ls-tv' });
    chart.gAxis.appendChild(g);

    /* ---- the two rules that keep the axis honest ------------------------
       Grid lines and price labels are generated ONCE across a range wider
       than the plot, then moved as a block by the current vertical pan. They
       are never regenerated per frame: regenerating them makes the label set
       flicker as the window slides, and a flickering axis is the single most
       obvious sign of a chart that is being drawn rather than run. */
    const span = chart.priceHi - chart.priceLo;
    let stepP = priceStep;
    if (!stepP) {
      const raw = span / 6;
      const mag = Math.pow(10, Math.floor(Math.log10(raw)));
      stepP = [1, 2, 2.5, 5, 10].map(m => m * mag).find(v => v >= raw) || mag * 10;
    }
    const gGridRow = el('g', { class: 'ls-tv-grid' });
    const gPriceRow = el('g', { class: 'ls-tv-prices' });
    g.appendChild(gGridRow); g.appendChild(gPriceRow);

    const rows = [];
    const over = span * 1.2;                       // enough to cover any slide
    for (let p = Math.ceil((chart.priceLo - over) / stepP) * stepP;
         p <= chart.priceHi + over; p += stepP) {
      const y = chart.Y(p);
      const ln = el('line', { class: 'ls-tv-h', x1: P.L, x2: P.R, y1: y, y2: y });
      const tx = el('text', {
        class: 'ls-tv-price', x: P.R + gutter, y,
        'text-anchor': 'start', 'dominant-baseline': 'central'
      });
      tx.textContent = p.toFixed(decimals);
      gGridRow.appendChild(ln); gPriceRow.appendChild(tx);
      rows.push({ p, y, ln, tx });
    }

    /* vertical separators every `timeEvery` bars, and the time strip */
    const gTime = el('g', { class: 'ls-tv-time' });
    g.appendChild(gTime);
    const ticks = [];
    for (let i = 0; i < candles.length; i += timeEvery) {
      const x = chart.X(i);
      const ln = el('line', { class: 'ls-tv-v', x1: x, x2: x, y1: P.T, y2: P.B });
      const tx = el('text', {
        class: 'ls-tv-t', x, y: P.B + 26, 'text-anchor': 'middle'
      });
      tx.textContent = hhmm(candles[i].t);
      gTime.appendChild(ln); gTime.appendChild(tx);
      ticks.push({ i, x, ln, tx });
    }

    const axisLine = el('line', { class: 'ls-tv-axis', x1: P.L, x2: P.R, y1: P.B, y2: P.B });
    g.appendChild(axisLine);

    /* ---- the live price tag + countdown --------------------------------- */
    const gTag = el('g', { class: 'ls-tv-tag' });
    const tagBox = el('rect', { class: 'ls-tv-tag-box', x: P.R + 2, y: 0, width: 92, height: 34, rx: 5 });
    const tagTxt = el('text', {
      class: 'ls-tv-tag-t', x: P.R + gutter, y: 0,
      'text-anchor': 'start', 'dominant-baseline': 'central'
    });
    const tagLine = el('line', { class: 'ls-tv-tag-l', x1: P.L, x2: P.R, y1: 0, y2: 0 });
    const cdBox = el('rect', { class: 'ls-tv-cd-box', x: P.R + 2, y: 0, width: 92, height: 28, rx: 5 });
    const cdTxt = el('text', {
      class: 'ls-tv-cd-t', x: P.R + gutter, y: 0,
      'text-anchor': 'start', 'dominant-baseline': 'central'
    });
    if (lastTag) { g.appendChild(tagLine); gTag.appendChild(tagBox); gTag.appendChild(tagTxt); }
    if (countdown) { gTag.appendChild(cdBox); gTag.appendChild(cdTxt); }
    g.appendChild(gTag);
    gTag.style.opacity = 0; tagLine.style.opacity = 0;

    /* ---- update ---------------------------------------------------------- */
    /* The bar the replay is currently printing and how far into it we are.
       Derived from the same timeline the candles are, so the tag can never
       disagree with the chart it sits on. */
    function liveBar() {
      const e = chart.timeline.find(x => x.kind === 'replay');
      if (!e) return { i: candles.length - 1, frac: 1 };
      const t = chart._t == null ? 0 : chart._t;
      const seg = e.segs.find(s => t < s.t1) || e.segs[e.segs.length - 1];
      /* During a hold the replay is frozen with b0 as the bar that has just
         OPENED, so the last completed close is b0-1. Reading b0 would put the
         close of an unfinished bar on the axis — the price tag announcing
         where the candle will end. That is future information, and it is the
         easiest one in the whole page to ship by accident. */
      if (!seg.run) return { i: Math.max(0, Math.min(seg.b0 - 1, candles.length - 1)), frac: 1 };
      const raw = seg.b0 + Math.max(0, t - seg.t0) * e.rate;
      const i = Math.min(candles.length - 1, Math.floor(raw));
      return { i, frac: raw - Math.floor(raw) };
    }

    function update() {
      const dy = chart.panY, dx = chart.panX;
      gGridRow.setAttribute('transform', `translate(0,${dy})`);
      gPriceRow.setAttribute('transform', `translate(0,${dy})`);
      gTime.setAttribute('transform', `translate(${dx},0)`);

      /* A price label that has slid out of the plot is not clipped, it is
         removed: half a number hanging off the top of a chart is a bug the
         eye finds instantly. */
      /* Computed before the rows are drawn so the axis label sitting under the
         live tag can be dropped: two numbers stacked on top of each other in
         the same 30px is the one place this chrome ever looks broken. */
      const lb = liveBar();
      const lc = candles[lb.i];
      const lpath = lc && lc.path && lc.path.length > 1 ? lc.path : (lc ? [lc.o, lc.c] : null);
      const lk = lpath ? Math.max(0, Math.min(lpath.length - 1,
                          Math.round(lb.frac * (lpath.length - 1)))) : 0;
      const tagY = lpath ? chart.Y(lpath[lk]) + dy : -1e9;

      rows.forEach(r => {
        const y = r.y + dy;
        const on = y > P.T + 6 && y < P.B - 6 && Math.abs(y - tagY) > 26;
        r.ln.style.display = y > P.T + 6 && y < P.B - 6 ? '' : 'none';
        r.tx.style.display = on ? '' : 'none';
      });
      ticks.forEach(k => {
        const x = k.x + dx;
        const on = x > P.L + 10 && x < P.R - 10;
        k.ln.style.display = on ? '' : 'none';
        k.tx.style.display = on ? '' : 'none';
      });

      const { i, frac } = lb;
      const c = candles[i];
      if (!c) return;
      /* The tag follows the FORMING close, not the finished one — otherwise it
         announces where the bar will end before it ends, which is exactly the
         future information the QA gate exists to catch. */
      const path = lpath;
      const k = lk;
      const px = path[k];
      const y = tagY;
      const up = px >= c.o;

      tagLine.setAttribute('y1', y); tagLine.setAttribute('y2', y);
      tagBox.setAttribute('y', y - 17);
      tagTxt.setAttribute('y', y);
      tagTxt.textContent = px.toFixed(decimals);
      cdBox.setAttribute('y', y + 20);
      cdTxt.setAttribute('y', y + 34);
      cdTxt.textContent = mmss(minutes * 60 * (1 - frac));
      gTag.setAttribute('class', 'ls-tv-tag ' + (up ? 'up' : 'dn'));
      tagLine.setAttribute('class', 'ls-tv-tag-l ' + (up ? 'up' : 'dn'));

      const vis = y > P.T + 4 && y < P.B - 4;
      gTag.style.opacity = vis ? 1 : 0;
      tagLine.style.opacity = vis ? 1 : 0;
    }

    /* Patch seek so a page can never forget to refresh the chrome — and record
       the time, because the tag needs to know where the replay is. */
    const seek0 = chart.seek;
    chart.seek = function (t) { chart._t = t; seek0(t); update(); return chart; };

    return { update, rows, ticks, stepP };
  }

  global.LSChrome = LSChrome;
})(typeof window !== 'undefined' ? window : globalThis);
