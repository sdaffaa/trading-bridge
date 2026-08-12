/* =============================================================================
   timeframe.js — one market, two frames

   Every trade on this account is read on M15 and entered on M5, and the only
   honest way to show two frames is to have ONE series underneath them. The M5
   candles are the market; the M15 candles are DERIVED from them, three to one.

   Drawing two independently-generated charts and captioning them "M15" and
   "M5" is the timeframe version of inventing a price: the M5 wick that takes
   the entry would not exist inside the M15 candle it is drawn under, and
   anyone who checks would find the two charts describe different markets.

     const M5  = build(...);                    // the market
     const M15 = LSTF.aggregate(M5, 3);         // the higher frame, derived
     LSTF.verify(M5, M15, 3);                   // [] or a list of mismatches

   Indexing runs both ways, because a reel constantly needs "which M5 bars are
   inside this M15 bar" and "which M15 bar am I standing in":

     LSTF.span(7, 3)      → { from: 21, to: 23 }
     LSTF.parent(22, 3)   → 7
   ========================================================================== */
(function (root) {
  'use strict';

  /* n LTF candles → 1 HTF candle. A partial tail group is dropped rather than
     emitted half-formed: an unclosed higher-frame candle is not a candle, and
     drawing it invites levels anchored to a high that has not printed yet. */
  function aggregate(candles, n) {
    if (!Array.isArray(candles)) throw new TypeError('aggregate: candles must be an array');
    if (!(n >= 2)) throw new RangeError('aggregate: n must be 2 or more');
    const out = [];
    for (let i = 0; i + n <= candles.length; i += n) {
      let h = -Infinity, l = Infinity;
      for (let k = i; k < i + n; k++) {
        if (candles[k].h > h) h = candles[k].h;
        if (candles[k].l < l) l = candles[k].l;
      }
      out.push({ o: candles[i].o, c: candles[i + n - 1].c, h, l });
    }
    return out;
  }

  /* Proves the pair rather than trusting it. Returns [] when every higher-frame
     candle is exactly the group beneath it — open of the first, close of the
     last, the extremes of all n. Used as a delivery gate, not a debug aid. */
  function verify(ltf, htf, n, tol) {
    const t = tol == null ? 1e-9 : tol;
    const errs = [];
    /* A leftover tail is silent otherwise: aggregate() drops it, so both sides
       agree while the last bars sit on the lower chart with no higher-frame
       candle above them. On a two-frame page that is exactly the mismatch this
       function exists to catch. */
    if (ltf.length % n !== 0) {
      errs.push({ i: null, field: 'tail',
                  message: `${ltf.length} ltf bars is not a multiple of ${n}; ` +
                           `the last ${ltf.length % n} have no htf candle above them` });
    }
    const expect = aggregate(ltf, n);
    if (htf.length !== expect.length) {
      errs.push({ i: null, field: 'length',
                  message: `htf has ${htf.length} candles, ${ltf.length} ltf ÷ ${n} gives ${expect.length}` });
    }
    const m = Math.min(htf.length, expect.length);
    for (let i = 0; i < m; i++) {
      ['o', 'h', 'l', 'c'].forEach(f => {
        if (Math.abs(htf[i][f] - expect[i][f]) > t) {
          errs.push({ i, field: f, htf: htf[i][f], ltf: expect[i][f],
                      message: `htf bar ${i} ${f} = ${htf[i][f]}, its ${n} ltf bars give ${expect[i][f]}` });
        }
      });
    }
    return errs;
  }

  /* The LTF bars inside one HTF bar, and the HTF bar one LTF bar sits in. */
  function span(iHtf, n)  { return { from: iHtf * n, to: iHtf * n + n - 1 }; }
  function parent(iLtf, n) { return Math.floor(iLtf / n); }

  /* Replay progress in one frame, expressed in the other. A reel that expands
     an M15 candle into its three M5 candles needs the two charts to be at the
     same instant, not at the same bar number. */
  function toLtf(iHtf, n) { return iHtf * n; }
  function toHtf(iLtf, n) { return Math.floor(iLtf / n); }

  root.LSTF = { aggregate, verify, span, parent, toLtf, toHtf };
})(typeof window !== 'undefined' ? window : globalThis);
