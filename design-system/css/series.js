/* ============================================================================
   Liquidity State — Series chart engine (series.js)
   Extends the strict chart rules with the annotation vocabulary used in the
   "أخطاء المتداولين" carousel: dashed connectors, marker glyphs (ring / X /
   check), retest boxes, and FRAMELESS haloed labels (main + sub line).

   Every price/level/box/marker is anchored to a real OHLC value — never a
   raw pixel. Labels carry NO frame (brand rule): text sits on a cream halo
   via paint-order:stroke.

   Usage:
     const c = new SeriesChart(svg, ohlc, { width, height, padL, padR, padT, padB });
     c.render();
     c.level(100, { label: "مستوى رئيسي", side: "start" });
     c.box(21, 23, 66, 62, { tone: "turq", opacity: 0.16 });
     c.annot({ at:{i:10, price:100}, labelXY:{x:470,y:120},
               text:"لمس المستوى", tone:"neutral", marker:"ring", dash:false });
   ========================================================================= */

const NS = "http://www.w3.org/2000/svg";
const C = {
  ink: "#0F2E3C", text2: "#5C6C73", axis: "#93A2A8",
  turq: "#2E7D96", turqDark: "#1E627A", up: "#2E8CA6", down: "#122F3E",
  red: "#D24B4B", cream: "#F2EEE7", grey: "#7F929B",
};
const tone = (t) => ({ neutral: C.ink, turq: C.turqDark, bull: C.turqDark, bear: C.red, red: C.red, grey: C.grey }[t] || C.ink);

function el(n, a, parent) {
  const e = document.createElementNS(NS, n);
  for (const k in a) e.setAttribute(k, a[k]);
  if (parent) parent.appendChild(e);
  return e;
}

export class SeriesChart {
  constructor(svg, ohlc, o = {}) {
    if (!Array.isArray(ohlc) || ohlc.length < 20 || ohlc.length > 40) {
      throw new Error(`SeriesChart: 20–40 candles required (got ${ohlc && ohlc.length}); 6–10 forbidden.`);
    }
    this.svg = svg;
    this.data = ohlc;
    this.W = o.width || 1000;
    this.H = o.height || 620;
    this.padL = o.padL ?? 40;
    this.padR = o.padR ?? 40;
    this.padT = o.padT ?? 40;
    this.padB = o.padB ?? 40;
    this.gap = o.gap ?? 0.32;
    const hi = Math.max(...ohlc.map((d) => d.h));
    const lo = Math.min(...ohlc.map((d) => d.l));
    const r = hi - lo || 1;
    this.hi = hi + r * (o.headroom ?? 0.08);
    this.lo = lo - r * (o.floor ?? 0.08);
    this.svg.setAttribute("viewBox", `0 0 ${this.W} ${this.H}`);
    this.plotW = this.W - this.padL - this.padR;
    this.plotH = this.H - this.padT - this.padB;
    this.slot = this.plotW / ohlc.length;
    this.bodyW = this.slot * (1 - this.gap);
    this.g = {};
  }
  y(p) { return this.padT + ((this.hi - p) / (this.hi - this.lo)) * this.plotH; }
  x(i) { return this.padL + this.slot * (i + 0.5); }
  layer(n) { return (this.g[n] ||= el("g", { "data-l": n }, this.svg)); }

  render() {
    const g = this.layer("candles");
    this.data.forEach((d, i) => {
      const up = d.c >= d.o;
      const col = up ? C.up : C.down;
      const cx = this.x(i);
      el("line", { x1: cx, x2: cx, y1: this.y(d.h), y2: this.y(d.l), stroke: col, "stroke-width": 1.8 }, g);
      const yo = this.y(d.o), yc = this.y(d.c);
      el("rect", {
        x: cx - this.bodyW / 2, y: Math.min(yo, yc), width: this.bodyW,
        height: Math.max(2, Math.abs(yc - yo)), rx: 0, fill: col,
      }, g);
    });
    return this;
  }

  /** dashed horizontal key level + frameless haloed label at one end */
  level(price, o = {}) {
    const g = this.layer("levels");
    const y = this.y(price);
    const x1 = o.x1 ?? this.padL, x2 = o.x2 ?? this.W - this.padR;
    el("line", { x1, y1: y, x2, y2: y, stroke: tone(o.tone || "neutral"),
      "stroke-width": 1.7, "stroke-dasharray": o.solid ? "0" : "8 8", "stroke-linecap": "round" }, g);
    if (o.label) {
      // anchor "middle" avoids RTL start/end ambiguity; caller gives a safe x
      const side = o.side || "start";
      const half = (o.labelWidth ?? 200) / 2;
      const lx = o.labelX ?? (side === "start" ? x1 + half + 8 : x2 - half - 8);
      this._text(g, lx, y - 14, o.label, {
        tone: o.tone || "neutral", weight: 700, size: o.size || 26, anchor: "middle",
      });
    }
    return this;
  }

  /** semi-transparent turquoise box anchored to indices + swing prices */
  box(i1, i2, pHigh, pLow, o = {}) {
    const g = this.layer("boxes");
    const xA = this.x(i1) - this.bodyW / 2, xB = this.x(i2) + this.bodyW / 2;
    const yT = this.y(pHigh), yB = this.y(pLow);
    el("rect", {
      x: xA, y: yT, width: xB - xA, height: yB - yT,
      fill: `rgba(46,125,150,${o.opacity ?? 0.16})`,
      stroke: C.turqDark, "stroke-width": 1, rx: 0,
    }, g);
    return this;
  }

  /** annotation: dashed connector + marker glyph on the chart + haloed label */
  annot(o) {
    const g = this.layer("annot");
    const px = o.at.x ?? this.x(o.at.i);
    const py = o.at.y ?? this.y(o.at.price);
    const lx = o.labelXY.x, ly = o.labelXY.y;
    const t = o.tone || "neutral";
    // connector from label toward marker (leaves a small gap at the marker)
    if (o.connector !== false) {
      const dx = px - lx, dy = py - ly;
      const len = Math.hypot(dx, dy) || 1;
      const gap = (o.markerR || 13) + 4;
      const ex = px - (dx / len) * gap, ey = py - (dy / len) * gap;
      el("line", {
        x1: lx, y1: ly, x2: ex, y2: ey,
        stroke: tone(t), "stroke-width": 1.5,
        "stroke-dasharray": o.dash === false ? "0" : "6 6", "stroke-linecap": "round",
      }, g);
    }
    this._marker(g, px, py, o.marker || "dot", t, o.markerR || 13);
    this._text(g, lx, ly, o.text, { tone: t, weight: 800, size: o.size || 27, anchor: o.anchor || "middle" });
    if (o.sub) this._text(g, lx, ly + (o.subDy || 30), o.sub, { tone: "sub", weight: 500, size: o.subSize || 21, anchor: o.anchor || "middle" });
    return this;
  }

  _marker(g, x, y, type, t, r) {
    if (type === "ring") {
      el("circle", { cx: x, cy: y, r, fill: "#FFFFFF", stroke: tone(t), "stroke-width": 2.6 }, g);
      el("circle", { cx: x, cy: y, r: 3.4, fill: tone(t) }, g);
    } else if (type === "xred") {
      const s = r * 0.72;
      // cream halo underlay so the X lifts off candles (frameless)
      for (const [c, w] of [[C.cream, 8], [C.red, 3.4]]) {
        el("line", { x1: x - s, y1: y - s, x2: x + s, y2: y + s, stroke: c, "stroke-width": w, "stroke-linecap": "round" }, g);
        el("line", { x1: x - s, y1: y + s, x2: x + s, y2: y - s, stroke: c, "stroke-width": w, "stroke-linecap": "round" }, g);
      }
    } else if (type === "xcircle") {
      el("circle", { cx: x, cy: y, r, fill: C.grey }, g);
      const s = r * 0.44;
      el("path", { d: `M${x - s} ${y - s} L${x + s} ${y + s} M${x - s} ${y + s} L${x + s} ${y - s}`, stroke: "#FFF", "stroke-width": 2.6, "stroke-linecap": "round" }, g);
    } else if (type === "check") {
      el("circle", { cx: x, cy: y, r, fill: C.turq }, g);
      const s = r * 0.5;
      el("path", { d: `M${x - s} ${y} L${x - s * 0.2} ${y + s * 0.8} L${x + s} ${y - s * 0.7}`, fill: "none", stroke: "#FFF", "stroke-width": 2.8, "stroke-linecap": "round", "stroke-linejoin": "round" }, g);
    } else {
      el("circle", { cx: x, cy: y, r: 5, fill: tone(t) }, g);
    }
  }

  _text(g, x, y, str, o) {
    const fill = o.tone === "sub" ? C.text2 : tone(o.tone);
    const t = el("text", {
      x, y, "text-anchor": o.anchor || "middle",
      "font-family": "Tajawal, sans-serif", "font-weight": o.weight || 700,
      "font-size": o.size || 26, fill,
      "paint-order": "stroke", stroke: C.cream, "stroke-width": 6, "stroke-linejoin": "round",
    }, g);
    t.textContent = str;
    return t;
  }
}
