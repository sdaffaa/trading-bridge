/* ============================================================================
   Liquidity State — Chart engine (chart.js)
   Renders brand-styled candlestick SVG from REAL OHLC data and provides
   annotation primitives that snap to exact wick/close prices.

   Design rules enforced here:
     - price->y mapping is deterministic (no randomness).
     - hline(), box(), breakArrow(), tag() take PRICES, never pixels, so every
       object lands exactly on a real level (BOS on wick high, SSL on wick low,
       box edges on actual swing prices, arrow head touching the line).
     - labels are frameless with a cream halo (via .ls-tag / paint-order).

   Usage:
     const c = new LSChart(svgEl, ohlc, {padTop, padBottom});
     c.render();
     c.hline(price, {tone:'bull', label:'BOS', from:'left'});
     c.box(x1Index, x2Index, priceHigh, priceLow, {label:'OB'});
     c.breakArrow(atIndex, price, {tone:'bull'});
     c.tag(atIndex, price, 'CHoCH', {tone:'bear', dy:-18});

   Never fabricate candles for the "real market" scene — pass verified OHLC.
   ========================================================================= */

const SVGNS = "http://www.w3.org/2000/svg";

function el(name, attrs) {
  const n = document.createElementNS(SVGNS, name);
  for (const k in attrs) n.setAttribute(k, attrs[k]);
  return n;
}

export class LSChart {
  /**
   * @param {SVGSVGElement} svg  target svg element (width/height set via viewBox)
   * @param {Array<{o:number,h:number,l:number,c:number}>} ohlc  real candles (20–40)
   * @param {object} opts
   */
  constructor(svg, ohlc, opts = {}) {
    if (!Array.isArray(ohlc) || ohlc.length < 20 || ohlc.length > 40) {
      throw new Error(
        `LSChart: educational charts require 20–40 candles (got ${ohlc && ohlc.length}). ` +
          `6–10 candles are forbidden by brand spec.`
      );
    }
    this.svg = svg;
    this.data = ohlc;
    this.W = opts.width || 1000;
    this.H = opts.height || 720;
    this.padL = opts.padLeft ?? 24;
    this.padR = opts.padRight ?? 96; // room for price scale on the right
    this.padT = opts.padTop ?? 60;
    this.padB = opts.padBottom ?? 48;
    this.gap = opts.gap ?? 0.28; // fraction of slot used as spacing

    const highs = ohlc.map((d) => d.h);
    const lows = ohlc.map((d) => d.l);
    this.hi = Math.max(...highs);
    this.lo = Math.min(...lows);
    const range = this.hi - this.lo || 1;
    this.hi += range * 0.06; // headroom so wicks/labels breathe
    this.lo -= range * 0.06;

    this.svg.setAttribute("viewBox", `0 0 ${this.W} ${this.H}`);
    this.plotW = this.W - this.padL - this.padR;
    this.plotH = this.H - this.padT - this.padB;
    this.slot = this.plotW / ohlc.length;
    this.bodyW = this.slot * (1 - this.gap);

    this.layers = {};
  }

  /** map a real price to a pixel y (deterministic). */
  y(price) {
    return this.padT + ((this.hi - price) / (this.hi - this.lo)) * this.plotH;
  }
  /** center x of candle at index i. */
  x(i) {
    return this.padL + this.slot * (i + 0.5);
  }

  _layer(name) {
    if (!this.layers[name]) {
      const g = el("g", { "data-layer": name });
      this.svg.appendChild(g);
      this.layers[name] = g;
    }
    return this.layers[name];
  }

  render() {
    const g = this._layer("candles");
    this.data.forEach((d, i) => {
      const up = d.c >= d.o;
      const cls = up ? "up" : "down";
      const cx = this.x(i);
      // wick
      g.appendChild(
        el("line", {
          x1: cx, x2: cx, y1: this.y(d.h), y2: this.y(d.l),
          class: `ls-wick-${cls}`,
        })
      );
      // body (min 2px so dojis stay visible)
      const yo = this.y(d.o), yc = this.y(d.c);
      const top = Math.min(yo, yc);
      const h = Math.max(2, Math.abs(yc - yo));
      g.appendChild(
        el("rect", {
          x: cx - this.bodyW / 2, y: top, width: this.bodyW, height: h,
          rx: 0, class: `ls-candle-${cls}`,
        })
      );
    });
    this._priceScale();
    return this;
  }

  _priceScale() {
    const g = this._layer("axis");
    const ticks = 5;
    for (let t = 0; t <= ticks; t++) {
      const p = this.lo + ((this.hi - this.lo) * t) / ticks;
      const yy = this.y(p);
      g.appendChild(
        el("text", {
          x: this.W - this.padR + 12, y: yy + 6,
          class: "ls-axis-text",
        })
      ).textContent = p.toFixed(this._decimals());
    }
  }
  _decimals() {
    const r = this.hi - this.lo;
    if (r > 100) return 1;
    if (r > 1) return 2;
    return r > 0.1 ? 3 : 5;
  }

  /** Horizontal level snapped to an exact price, round-handle ends. */
  hline(price, o = {}) {
    const tone = o.tone || "neutral"; // neutral | bull | bear
    const g = this._layer("levels");
    const y = this.y(price);
    const x1 = o.x1 ?? this.padL;
    const x2 = o.x2 ?? this.W - this.padR;
    g.appendChild(el("line", { x1, y1: y, x2, y2: y, class: `ls-hline ls-hline--${tone}` }));
    g.appendChild(el("circle", { cx: x1, cy: y, class: `ls-handle ls-handle--${tone}` }));
    g.appendChild(el("circle", { cx: x2, cy: y, class: `ls-handle ls-handle--${tone}` }));
    if (o.label) this.tag(o.labelAt ?? 0, price, o.label, { tone, dy: o.dy ?? -14, anchor: "start" });
    return this;
  }

  /** Range / order-block box anchored to swing prices and candle indices. */
  box(i1, i2, priceHigh, priceLow, o = {}) {
    const g = this._layer("boxes");
    const xA = this.x(i1) - this.bodyW / 2;
    const xB = this.x(i2) + this.bodyW / 2;
    const yT = this.y(priceHigh);
    const yB = this.y(priceLow);
    g.appendChild(
      el("rect", { x: xA, y: yT, width: xB - xA, height: yB - yT, class: "ls-box" })
    );
    if (o.label) this.tag(i2, priceHigh, o.label, { tone: o.tone || "bull", dy: -14, anchor: "end" });
    return this;
  }

  /** Break arrow whose head touches `price` exactly at candle `i`. */
  breakArrow(i, price, o = {}) {
    const tone = o.tone || "bull";
    const g = this._layer("breaks");
    const cx = this.x(i);
    const yHead = this.y(price);
    const dir = o.dir || (tone === "bear" ? 1 : -1); // -1 head points up
    const len = o.len ?? 70;
    const yTail = yHead - dir * len * -1; // tail away from head
    const tailY = yHead + dir * len; // tail below (bull) / above (bear)
    g.appendChild(
      el("line", { x1: cx, y1: tailY, x2: cx, y2: yHead, class: `ls-break-${tone}` })
    );
    // arrow head — apex exactly on yHead
    const s = 9;
    const pts =
      dir < 0
        ? `${cx},${yHead} ${cx - s},${yHead + s * 1.4} ${cx + s},${yHead + s * 1.4}`
        : `${cx},${yHead} ${cx - s},${yHead - s * 1.4} ${cx + s},${yHead - s * 1.4}`;
    g.appendChild(el("polygon", { points: pts, class: `ls-break-${tone}` }));
    return this;
  }

  /** Frameless haloed label at exact (index, price). */
  tag(i, price, text, o = {}) {
    const g = this._layer("tags");
    const tone = o.tone || "neutral";
    const anchor = o.anchor || "middle";
    const x = this.x(i) + (o.dx || 0);
    const y = this.y(price) + (o.dy ?? -14);
    const t = el("text", { x, y, "text-anchor": anchor, class: `ls-tag ls-tag--${tone}` });
    t.textContent = text;
    g.appendChild(t);
    return this;
  }
}
