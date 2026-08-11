/* ==========================================================================
   Liquidity State — Footprint / order-flow renderer
   Companion to markup.js. Where markup.js draws what price DID, this draws
   what happened INSIDE the candle: how much traded on the bid and on the ask
   at each price.

   One rule governs the whole module, and it is a market convention rather
   than a typographic one:

       THE LADDER IS ALWAYS LTR — BID LEFT, ASK RIGHT.

   The page around it is RTL Arabic; the ladder is not. Every trading platform
   in the world prints bid×ask left-to-right, and a reader who mirrors it once
   will misread every footprint they ever see afterwards. Arabic labels sit
   outside the ladder and stay RTL; the numbers inside it never move.

   Four variants, each matching one page of the reference carousel:

     ladder  the hero panel — BID | ASK columns, a heat bar behind the bid,
             one row lit up. Used on the cover to pose the question.
     heat    definition figure — bid cells | candle | ask cells, with the
             volume painted into the candle body as bands.
     inside  the anatomy table — a bid/ask grid laid over the candle body,
             a brace naming the body, an imbalance row called out in red.
     bars    the evidence — Bid | Price | Ask with proportional bars, buy
             green on the ask, sell red on the bid.

   Rows are always given high price first, so index 0 is the top of the
   ladder, the same way you read it on a chart.

   Usage:
     const fp = LSFootprint({ mount: '#fp', variant: 'ladder', width: 420,
                              height: 620, rows: [...] });
     fp.at(6, 'ask')   -> {x, y} of that cell, for hanging your own callouts
   ========================================================================== */
(function (global) {
  'use strict';

  const NS = 'http://www.w3.org/2000/svg';
  const el = (n, a = {}) => {
    const e = document.createElementNS(NS, n);
    for (const k in a) e.setAttribute(k, a[k]);
    return e;
  };

  /* Compact is how a live ladder prints — 1.6K, not 1,600 — and it is what
     the cover uses. The anatomy table has room for the real number. */
  const fmt = (v, compact) => {
    if (v == null) return '';
    if (!compact) return v.toLocaleString('en-US');
    return v >= 1000 ? (v / 1000).toFixed(1) + 'K' : String(v);
  };

  const maxOf = (rows, key) =>
    Math.max(1, ...rows.map(r => r[key] || 0));

  function LSFootprint(opts) {
    const {
      mount,
      variant = 'ladder',
      width = 420,
      height = 620,
      rows = [],
      compact = variant === 'ladder',
      labels = {},
      candle = null,          // {o,h,l,c} for 'heat' — drawn beside the ladder
      panel = variant === 'ladder',
      /* Which side the depth bar measures. 'total' is right whenever the
         question is "where did the most trade", which is what makes one row
         the row; 'bid'/'ask' when one side is the story. */
      heatKey = 'bid',
      callouts = [],          // [{row, col, side, text, len, tone}]
      box = null,             // {from, to, col, tone} outline over a row range
      brace = null,           // {from, to, text} for 'inside'
      anim = null             // {} to build on camera; see seek() below
    } = opts;

    const L = Object.assign({ bid: 'BID', ask: 'ASK', price: 'Price' }, labels);

    const host = typeof mount === 'string' ? document.querySelector(mount) : mount;
    const svg = el('svg', {
      class: `ls-fp ls-fp-${variant}`, width, height,
      viewBox: `0 0 ${width} ${height}`, xmlns: NS
    });

    const gBack  = el('g', { class: 'ls-fp-back'  });   // panel, cells, tracks
    const gBar   = el('g', { class: 'ls-fp-bars'  });   // heat + volume bars
    const gMark  = el('g', { class: 'ls-fp-mark'  });   // highlights, boxes, braces
    const gText  = el('g', { class: 'ls-fp-text'  });   // every number and label
    [gBack, gBar, gMark, gText].forEach(g => svg.appendChild(g));
    if (host) host.appendChild(svg);

    /* ---- vertical rhythm ------------------------------------------------
       The header is part of the ladder, not a caption above it, so it gets a
       row of its own and everything below divides what is left. */
    const hasHeader = variant !== 'inside';
    const padY   = variant === 'ladder' ? 18 : 6;
    const hdrH   = hasHeader ? 40 : 0;
    const topY   = padY + hdrH;
    const bodyH  = height - topY - padY;
    const rowH   = rows.length ? bodyH / rows.length : bodyH;
    const rowY   = i => topY + rowH * i;
    const rowMid = i => rowY(i) + rowH / 2;

    /* Column geometry per variant, as fractions of the width. Keeping these
       in one table is what lets a slide re-size a footprint without any of
       the internals shifting out of alignment. */
    const GEO = {
      ladder: { bidNum: 0.28, barX: 0.30, barW: 0.32, askNum: 0.90,
                hdrBid: 0.27, hdrAsk: 0.775, div: 0.53, edge: 0.045 },
      heat:   { bidX: 0.02, cellW: 0.255, candX: 0.355, candW: 0.29, askX: 0.725 },
      inside: { tableX: 0.33, tableW: 0.34 },
      bars:   { bidX: 0.06, colW: 0.235, priceX: 0.33, priceW: 0.19,
                askX: 0.55, gap: 4 }
    }[variant];
    const F = f => width * f;

    /* ---- timeline --------------------------------------------------------
       A ladder that appears whole is a graphic. A ladder that builds price by
       price is the point being made — the viewer watches volume accumulate at
       one level. So every node can carry a cue, and seek(t) drives them all
       off the same clock the chart and captions use.

       Bars grow from the edge they are anchored to rather than fading, because
       a bar's length is its meaning: fading one in states the answer, growing
       it shows the answer arriving. */
    const A = anim && Object.assign(
      { at: 0, panel: 0.35, rowStagger: 0.055, rowDur: 0.30 }, anim);
    const cues = [];
    let tMax = A ? A.at : 0;

    function cue(node, kind, t0, dur, origin) {
      if (!A) return node;
      if (origin) {
        node.style.transformBox = 'fill-box';
        node.style.transformOrigin = origin;
      }
      cues.push({ node, kind, t0, dur });
      tMax = Math.max(tMax, t0 + dur);
      return node;
    }
    /* When row i reveals. Rows run top to bottom, the direction a ladder is
       read, so the stagger is the reading order and not an effect. */
    const rowT = i => A.at + A.panel + i * A.rowStagger;

    /* R = something belonging to row i. P = the furniture around the rows,
       which is all there before the first price prints. */
    const R = (node, i, origin) =>
      A ? cue(node, origin ? 'growX' : 'fade', rowT(i), A.rowDur, origin) : node;
    const P = node => A ? cue(node, 'fade', A.at, A.panel) : node;

    const text = (s, x, y, cls, anchor = 'middle') => {
      const t = el('text', {
        class: cls, x, y, 'text-anchor': anchor, 'dominant-baseline': 'central'
      });
      t.textContent = s;
      gText.appendChild(t);
      return t;
    };

    /* Where a cell sits, so a caller can hang a leader off it without
       re-deriving this geometry by hand. */
    function at(i, col) {
      const y = rowMid(i);
      if (variant === 'ladder')
        return { x: col === 'ask' ? F(GEO.askNum) : F(GEO.bidNum), y };
      if (variant === 'heat')
        return { x: col === 'ask' ? F(GEO.askX + GEO.cellW / 2)
                                  : F(GEO.bidX + GEO.cellW / 2), y };
      if (variant === 'inside')
        return { x: col === 'ask' ? F(GEO.tableX + GEO.tableW * 0.75)
                                  : F(GEO.tableX + GEO.tableW * 0.25), y };
      return { x: col === 'ask' ? F(GEO.askX + GEO.colW / 2)
             : col === 'price' ? F(GEO.priceX + GEO.priceW / 2)
                               : F(GEO.bidX + GEO.colW / 2), y };
    }

    // ---- variant 1: the hero ladder --------------------------------------
    function drawLadder() {
      if (panel) {
        gBack.appendChild(P(el('rect', {
          class: 'ls-fp-panel', x: 1, y: 1, rx: 16, ry: 16,
          width: width - 2, height: height - 2
        })));
      }
      P(text(L.bid, F(GEO.hdrBid), padY + hdrH / 2, 'ls-fp-hdr'));
      P(text(L.ask, F(GEO.hdrAsk), padY + hdrH / 2, 'ls-fp-hdr'));
      gBack.appendChild(P(el('line', {
        class: 'ls-fp-div', x1: F(GEO.div), x2: F(GEO.div),
        y1: padY + 10, y2: padY + hdrH - 10
      })));

      const vol = r => heatKey === 'total' ? (r.bid || 0) + (r.ask || 0) : (r[heatKey] || 0);
      const mx = Math.max(1, ...rows.map(vol));
      rows.forEach((r, i) => {
        if (r.hi) {                       // the row the whole page is about
          const h = el('rect', {
            class: 'ls-fp-hi', x: F(GEO.edge), y: rowY(i) + 2, rx: 7, ry: 7,
            width: width - F(GEO.edge) * 2, height: rowH - 4
          });
          gMark.appendChild(h);
          /* The lit row lands after the ladder finishes, not with its own
             row: it is the conclusion, and a conclusion that arrives during
             the evidence is not one. */
          if (A) cue(h, 'fade', rowT(rows.length) + 0.15, 0.4);
        }
        /* The bar reads as depth behind the number, so it is drawn at an
           opacity that scales with volume rather than in a second colour —
           one hue, one meaning. */
        const w = F(GEO.barW) * (vol(r) / mx);
        gBar.appendChild(R(el('rect', {
          class: 'ls-fp-heat', x: F(GEO.barX), y: rowY(i) + rowH * 0.22,
          width: Math.max(2, w), height: rowH * 0.56, rx: 2,
          opacity: (0.25 + 0.6 * (vol(r) / mx)).toFixed(3)
        }), i, 'left center'));
        const cls = 'ls-fp-num' + (r.hi ? ' ls-fp-num-hi' : '');
        R(text(fmt(r.bid, compact), F(GEO.bidNum), rowMid(i), cls, 'end'), i);
        R(text(fmt(r.ask, compact), F(GEO.askNum), rowMid(i), cls, 'end'), i);
      });
    }

    // ---- variant 2: cells either side of a heated candle ------------------
    function drawHeat() {
      P(text(L.bid, F(GEO.bidX + GEO.cellW / 2), padY + hdrH / 2, 'ls-fp-hdr'));
      P(text(L.ask, F(GEO.askX + GEO.cellW / 2), padY + hdrH / 2, 'ls-fp-hdr'));

      const mx = Math.max(maxOf(rows, 'bid'), maxOf(rows, 'ask'));

      /* The candle is the point of the figure: the cells to either side are
         the same volume, only unpacked. So the body spans exactly the rows,
         and the wick runs past them on both ends. */
      const bx = F(GEO.candX), bw = F(GEO.candW), cx = bx + bw / 2;
      gBack.appendChild(P(el('line', {
        class: 'ls-fp-wick', x1: cx, x2: cx,
        y1: topY - (candle && candle.wickUp || 46),
        y2: rowY(rows.length) + (candle && candle.wickDn || 46)
      })));
      gBack.appendChild(P(el('rect', {
        class: 'ls-fp-body', x: bx, y: topY, width: bw, height: rowH * rows.length
      })));

      rows.forEach((r, i) => {
        const v = ((r.bid || 0) + (r.ask || 0)) / 2 / mx;
        gBar.appendChild(R(el('rect', {
          class: 'ls-fp-band', x: bx + 1, y: rowY(i),
          width: bw - 2, height: rowH, opacity: (0.07 + 0.40 * v).toFixed(3)
        }), i));
        [['bid', GEO.bidX], ['ask', GEO.askX]].forEach(([k, gx]) => {
          gBack.appendChild(R(el('rect', {
            class: 'ls-fp-cell' + (r.hi ? ' ls-fp-cell-hi' : ''),
            x: F(gx), y: rowY(i) + 2, rx: 3, ry: 3,
            width: F(GEO.cellW), height: rowH - 4
          }), i));
          R(text(fmt(r[k], compact), F(gx + GEO.cellW / 2), rowMid(i), 'ls-fp-num'), i);
        });
      });
    }

    // ---- variant 3: the grid laid over the candle body --------------------
    function drawInside() {
      const tx = F(GEO.tableX), tw = F(GEO.tableW), cx = tx + tw / 2;
      const y0 = topY, y1 = rowY(rows.length);

      gBack.appendChild(P(el('line', {
        class: 'ls-fp-wick', x1: cx, x2: cx, y1: y0 - 62, y2: y1 + 62
      })));

      rows.forEach((r, i) => {
        const imb = !!r.imb;
        /* Bid tinted, ask neutral — the two sides must be told apart at a
           glance, before any number is read. An imbalance row overrides
           both, because it is the only thing on the page that matters. */
        gBack.appendChild(R(el('rect', {
          class: imb ? 'ls-fp-imb' : 'ls-fp-bid',
          x: tx, y: rowY(i), width: tw / 2, height: rowH
        }), i));
        gBack.appendChild(R(el('rect', {
          class: imb ? 'ls-fp-imb' : 'ls-fp-ask',
          x: cx, y: rowY(i), width: tw / 2, height: rowH
        }), i));
        R(text(fmt(r.bid, compact), tx + tw * 0.25, rowMid(i), 'ls-fp-num-lg'), i);
        R(text(fmt(r.ask, compact), tx + tw * 0.75, rowMid(i), 'ls-fp-num-lg'), i);
      });

      gMark.appendChild(P(el('rect', {
        class: 'ls-fp-frame', x: tx, y: y0, width: tw, height: y1 - y0
      })));

      if (brace) {
        const by0 = rowY(brace.from), by1 = rowY(brace.to + 1);
        const bx = tx - 16, k = 12;
        gMark.appendChild(el('path', {
          class: 'ls-fp-brace', fill: 'none',
          d: `M${bx},${by0} q${-k},0 ${-k},${k} L${bx - k},${(by0 + by1) / 2 - k}` +
             ` q0,${k} ${-k * 0.5},${k} q${k * 0.5},0 ${k * 0.5},${k}` +
             ` L${bx - k},${by1 - k} q0,${k} ${k},${k}`
        }));
        text(brace.text, bx - k * 2 - 14, (by0 + by1) / 2, 'ls-fp-brace-t', 'end');
      }
    }

    // ---- variant 4: proportional bid / price / ask bars -------------------
    function drawBars() {
      const cw = F(GEO.colW), pw = F(GEO.priceW);
      const bidL = F(GEO.bidX), priceL = F(GEO.priceX), askL = F(GEO.askX);
      P(text(L.bid,   bidL + cw / 2,   padY + hdrH / 2, 'ls-fp-hdr-sm'));
      P(text(L.price, priceL + pw / 2, padY + hdrH / 2, 'ls-fp-hdr-sm'));
      P(text(L.ask,   askL + cw / 2,   padY + hdrH / 2, 'ls-fp-hdr-sm'));

      const mx = Math.max(maxOf(rows, 'bid'), maxOf(rows, 'ask'));
      rows.forEach((r, i) => {
        const y = rowY(i) + GEO.gap / 2, h = rowH - GEO.gap;

        // empty tracks, so a row with no trade still reads as a row
        gBack.appendChild(R(el('rect', { class: 'ls-fp-track', x: bidL, y, width: cw, height: h }), i));
        gBack.appendChild(R(el('rect', { class: 'ls-fp-track', x: askL, y, width: cw, height: h }), i));
        gBack.appendChild(R(el('rect', { class: 'ls-fp-price', x: priceL, y, width: pw, height: h }), i));
        R(text(String(r.price), priceL + pw / 2, rowMid(i), 'ls-fp-num'), i);

        /* Bid grows leftward, ask grows rightward — away from price, the
           direction each side is actually pushing. */
        if (r.bid) {
          const w = cw * (r.bid / mx);
          gBar.appendChild(R(el('rect',
            { class: 'ls-fp-sell', x: bidL + cw - w, y, width: w, height: h }),
            i, 'right center'));
        }
        if (r.ask) {
          const w = cw * (r.ask / mx);
          gBar.appendChild(R(el('rect', { class: 'ls-fp-buy', x: askL, y, width: w, height: h }),
            i, 'left center'));
        }
      });

      if (box) {
        const bx = box.col === 'bid' ? bidL : askL;
        const bn = el('rect', {
          class: 'ls-fp-box', x: bx - 5, y: rowY(box.from) - 2, rx: 6, ry: 6,
          width: cw + 10, height: rowY(box.to + 1) - rowY(box.from) + 4
        });
        gMark.appendChild(bn);
        if (A) cue(bn, 'fade', rowT(rows.length) + 0.15, 0.4);
      }
    }

    ({ ladder: drawLadder, heat: drawHeat, inside: drawInside, bars: drawBars }[variant])();

    /* ---- callouts --------------------------------------------------------
       A dashed leader out to an Arabic label. The leader stops short of the
       cell — same rule the chart markup follows: point at the thing, do not
       touch it. */
    callouts.forEach(co => {
      const g = el('g');                    // one cue for the whole callout
      gMark.appendChild(g);
      if (A) cue(g, 'fade', co.at != null ? co.at : rowT(rows.length) + 0.5, 0.45);
      const p = at(co.row, co.col || 'ask');
      const side = co.side || 'right';
      const len = co.len || 90;
      const dir = side === 'right' ? 1 : -1;
      const x0 = side === 'right' ? Math.max(p.x, F(0.9)) : Math.min(p.x, F(0.1));
      const x1 = x0 + dir * len;
      const tone = co.tone ? ` ls-fp-${co.tone}-t` : '';
      if (co.dot) {
        g.appendChild(el('circle', {
          class: 'ls-fp-dot', cx: x0, cy: p.y, r: 5
        }));
      }
      g.appendChild(el('line', {
        class: 'ls-fp-leader' + tone, x1: x0 + dir * 10, x2: x1, y1: p.y, y2: p.y
      }));
      const t = el('text', {
        class: 'ls-fp-callout' + tone, x: x1 + dir * 12, y: p.y,
        'text-anchor': side === 'right' ? 'start' : 'end',
        'dominant-baseline': 'central'
      });
      /* Two lines when the label is long — one leader, two rows of text. */
      String(co.text).split('\n').forEach((line, k, all) => {
        const ts = el('tspan', {
          x: x1 + dir * 12,
          dy: k === 0 ? -(all.length - 1) * 15 : 30
        });
        ts.textContent = line;
        t.appendChild(ts);
      });
      g.appendChild(t);
    });

    /* One clock, shared with LSChart and LSCaptions — the caller drives all
       three from the same t so nothing can drift apart across a render. */
    function seek(t) {
      cues.forEach(c => {
        const p = c.dur <= 0 ? (t >= c.t0 ? 1 : 0)
                             : Math.max(0, Math.min(1, (t - c.t0) / c.dur));
        const e = p * p * (3 - 2 * p);              // smoothstep, no overshoot
        if (c.kind === 'growX') {
          c.node.style.transform = `scaleX(${e})`;
          c.node.style.opacity = p > 0 ? 1 : 0;
        } else {
          c.node.style.opacity = e;
        }
      });
      return fp;
    }

    const fp = { svg, at, rowH, rowY, rowMid, seek,
                 duration: () => tMax, get animated() { return !!A; } };
    if (A) seek(A.at - 1);                          // start hidden
    return fp;
  }

  LSFootprint.fmt = fmt;
  global.LSFootprint = LSFootprint;
})(window);
