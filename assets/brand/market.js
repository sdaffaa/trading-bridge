/* ==========================================================================
   Liquidity State — Market simulation, order flow, and the QA gate
   Companion to markup.js (what price DID) and footprint.js (how flow is DRAWN).
   This module is what produces the numbers those two render.

   It exists because of one rule in CHART-PROTOCOL.md §7:

       THE MARKET IS GENERATED FIRST AND THE LESSON IS FOUND INSIDE IT.

   The tempting way to build a teaching chart is to decide the outcome and
   then write candles that arrive at it. That chart is always subtly wrong:
   the sweep is too clean, every false break reverses, the retest never fails,
   and the delta always agrees with the candle. A viewer who trades cannot say
   why it looks fake, only that it does.

   So: `series()` runs a market forward with no idea what the reel is about —
   regimes, volatility clustering, session activity, liquidity magnets that
   sometimes reject and sometimes go through. Then `findSetup()` SEARCHES that
   series for a place where the pattern's conditions happen to occur in the
   right chronological order. If it isn't there, the seed is discarded and
   another market is run. Nothing is ever written backwards from the answer.

   Everything downstream is derived, never decorated:
     footprint()  bid/ask per level; total is the bar's volume, delta is the
                  difference, bar POC is the level that actually traded most
     profile()    built from those same volumes; POC/VAH/VAL fall where the
                  volume puts them
     vwap()       Σ(typical × volume) / Σ(volume)
     qa()         re-derives all of it independently and reports mismatches

   Volume here is simulated. It is labelled as such on every page that uses it
   (CHART-PROTOCOL.md §1) and is never presented as exchange tape.
   ========================================================================== */

(function (global) {
  'use strict';

  /* ---- deterministic randomness ------------------------------------------
     Seeded and reproducible: a chart that cannot be regenerated cannot be
     checked, and the QA gate has to be able to re-run the same market. */
  function rng(seed) {
    let s = seed >>> 0 || 1;
    return function () {
      s = (s * 1664525 + 1013904223) >>> 0;
      return s / 4294967296;
    };
  }
  const gauss = r => {                     // Box–Muller, one draw
    const u = Math.max(1e-12, r()), v = r();
    return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v);
  };
  const round = (v, d) => {
    const f = Math.pow(10, d);
    return Math.round(v * f) / f;
  };
  const toTick = (v, tick) => Math.round(v / tick) * tick;

  /* ---- session activity ---------------------------------------------------
     Volume and range are not flat across the day. Two humps — London and New
     York — over a thin overnight, and the overlap is the busiest hour of the
     session. Times are UTC minutes from midnight. */
  const SESSIONS = [
    { name: 'asia',   from:  0 * 60, to:  7 * 60, act: 0.55 },
    { name: 'london', from:  7 * 60, to: 13 * 60, act: 1.15 },
    { name: 'overlap',from: 13 * 60, to: 16 * 60, act: 1.55 },
    { name: 'ny',     from: 16 * 60, to: 21 * 60, act: 1.00 },
    { name: 'late',   from: 21 * 60, to: 24 * 60, act: 0.50 }
  ];
  function sessionAt(minuteOfDay) {
    const m = ((minuteOfDay % 1440) + 1440) % 1440;
    return SESSIONS.find(s => m >= s.from && m < s.to) || SESSIONS[0];
  }
  /* A soft bump at each open: the first bars of London and New York carry the
     day's cleanest expansion, and a chart without it looks like a random
     walk with a clock drawn on it. */
  function openBoost(minuteOfDay) {
    const m = ((minuteOfDay % 1440) + 1440) % 1440;
    let b = 1;
    [[7 * 60, 0.85], [13 * 60 + 30, 1.05]].forEach(([o, amp]) => {
      const d = Math.abs(m - o);
      if (d < 75) b += amp * Math.exp(-(d * d) / (2 * 32 * 32));
    });
    return b;
  }

  /* ======================================================================
     series() — run a market forward
     ====================================================================== */
  /* The price path inside a bar is simulated at sub-step resolution and the
     bar is READ OFF it: open is the first sub-step, close the last, high and
     low the extremes. Composing o/h/l/c independently is where fake candles
     come from — it is also how you end up with a low above an open. Read off
     a path, OHLC integrity is not enforced, it is structural. */
  function series(opts) {
    const {
      bars = 480,
      start = 2000,
      tick = 0.1,
      decimals = 2,
      minutes = 5,                 // bar length
      startMinute = 6 * 60,        // UTC minute of the first bar
      vol = 0.9,                   // base per-bar sigma, in price units
      seed = 1,
      /* 24, not 12. Body/Range is not a free parameter: it falls out of how
         many times price changes its mind inside the bar. At 12 sub-steps the
         net move is a large share of the path's own extremes and the mean
         lands near 0.60 — bodies with almost no wick, which is the single most
         obvious tell of a generated chart. At 24 it lands inside the 0.38–0.58
         band CHART-REALISM.md §6 asks for, and the wicks arrive with it. 30 puts
         the mean near the middle of the band instead of its top edge. */
      subSteps = 30,
      baseVolume = 900,
      /* Shape knobs. Defaults are the ones measured against CHART-REALISM.md
         §6–§7; a page that needs an older market pins them explicitly rather
         than inheriting whatever the module currently prefers. */
      spikeP = 0.03, spikeBase = 2.4, spikeVar = 1.6,
      wickP = 0.22,                // chance of a push-and-return inside the bar
      regimeDrift = 0.10,          // how hard a regime leans, in units of vol
      regimeHold = 0.982,          // per-bar chance a regime persists
      magnetPull = 0.08,           // how hard an untaken swing attracts price
      keepPath = false             // keep the intrabar path for forming-candle replay
    } = opts;

    const r = rng(seed);
    const out = [];

    /* Regime: a slow three-state chain. Drift is small next to noise — a
       trend you can see bar by bar is not a trend, it is a ramp. */
    /* Measured against a driftless walk over 44-bar windows: at d = 0.16 the
       regime showed up in the BODY SIGNS — same-colour runs over six in 23% of
       windows against the coin's 13%, and lag-3 direction match tripping the
       cyclicity check four times as often. A trend a viewer can read off the
       colours bar by bar is not a trend, it is a ramp; the regime belongs in
       where price ends up, not in the sign of every candle. */
    const REG = [{ d: regimeDrift, p: regimeHold }, { d: -regimeDrift, p: regimeHold },
                 { d: 0, p: regimeHold - 0.010 }];
    let reg = 2;

    /* Volatility clustering, GARCH(1,1)-shaped: today's shock feeds tomorrow's
       sigma, so quiet stretches persist and so do violent ones. This is what
       produces the coil-then-expand the protocol asks for, without anyone
       scripting a coil. */
    const OMEGA = 0.14, ALPHA = 0.20, BETA = 0.74;
    let sig = vol, lastShock = vol;

    /* Liquidity magnets: recent swing extremes attract price, and when it gets
       there it EITHER rejects or goes through. Which one is a coin weighted by
       the regime — that is the whole reason some sweeps reverse and some do
       not, and why a chart built this way has both. */
    const swings = { hi: [], lo: [] };
    let p = start;

    for (let i = 0; i < bars; i++) {
      const minute = startMinute + i * minutes;
      const ses = sessionAt(minute);
      const act = ses.act * openBoost(minute);

      if (r() > REG[reg].p) reg = Math.floor(r() * 3);
      sig = Math.sqrt(OMEGA * vol * vol + ALPHA * lastShock * lastShock + BETA * sig * sig);
      const barSig = Math.min(sig, vol * 3.2) * act;

      /* pull toward the nearest untouched extreme within reach */
      let pull = 0;
      const near = [...swings.hi, ...swings.lo]
        .filter(s => !s.taken && Math.abs(s.p - p) < barSig * 9)
        .sort((a, b) => Math.abs(a.p - p) - Math.abs(b.p - p))[0];
      if (near) pull = Math.sign(near.p - p) * barSig * magnetPull;

      const drift = REG[reg].d * vol * 0.35 + pull;

      /* the intrabar path */
      const path = [p];
      let x = p;
      /* A wick is a push that came BACK. Without one, every extension of the
         range also moves the close, so the body keeps pace with the range and
         Body/Range sits near 0.60 — bodies with almost nothing on either end,
         which is the most obvious tell of a generated chart. This is an
         excursion that returns: it raises the range and leaves the close near
         where it was, and it lands on one side only, which is where the
         asymmetry §6 asks for comes from. */
      let wickAt = -1, wickDir = 0, wickLen = 0;
      /* `wickP > 0` first, and that ordering is load-bearing: `r() < 0` is
         false either way, but the draw still happens and every later number in
         the stream shifts. A page that pins wickP: 0 to reproduce an older
         market would get a different market — a seed that is not a seed. */
      if (wickP > 0 && r() < wickP) {
        wickLen = 2 + Math.floor(r() * 3);
        /* The return has to FIT. Truncated by the end of the bar it stops
           being an excursion and becomes a push — it moves the close, which
           adds directional persistence and lengthens same-colour runs. That
           showed up immediately as twenty run violations where there had been
           twelve, from a change that was supposed to touch only the wicks. */
        const room = Math.max(1, subSteps - 2 * wickLen - 1);
        wickAt = 1 + Math.floor(r() * room);
        wickDir = r() < 0.5 ? 1 : -1;
      }
      for (let k = 0; k < subSteps; k++) {
        let step = gauss(r) * (barSig / Math.sqrt(subSteps)) + drift / subSteps;
        /* an occasional single-tick spike is what makes a wick a wick */
        /* Rarer and smaller than it was: at 6% and up to 4.8x this printed a
           candle above 2.80x the rolling median roughly once every twenty
           bars, and a chart where every twentieth candle is an outlier has no
           outliers — it has a texture. */
        if (r() < spikeP) step *= spikeBase + r() * spikeVar;
        if (wickAt >= 0) {
          const d = k - wickAt;
          if (d >= 0 && d < wickLen) step += wickDir * (barSig / Math.sqrt(subSteps)) * 1.6;
          else if (d >= wickLen && d < 2 * wickLen) step -= wickDir * (barSig / Math.sqrt(subSteps)) * 1.6;
        }
        x += step;
        path.push(x);
      }
      const o = path[0], c = path[path.length - 1];
      let h = Math.max(...path), l = Math.min(...path);

      /* Sweep behaviour at a magnet: overshoot the level, then either give it
         back inside the same bar (a rejection) or close beyond it (a real
         break). Not scripted per event — rolled per touch. */
      if (near && h >= near.p && near.p >= o && !near.taken) {
        near.taken = true;
        if (r() < 0.58) { h = Math.max(h, near.p + barSig * (0.10 + r() * 0.28)); }
      }
      if (near && l <= near.p && near.p <= o && !near.taken) {
        near.taken = true;
        if (r() < 0.58) { l = Math.min(l, near.p - barSig * (0.10 + r() * 0.28)); }
      }

      const bar = {
        t: minute,
        o: toTick(o, tick), c: toTick(c, tick),
        h: toTick(h, tick), l: toTick(l, tick),
        session: ses.name
      };
      /* the path is the truth, but rounding to the tick can put a rounded body
         a tick outside a rounded wick — so the wick is widened, never the body
         moved. A body is a decision; a wick is an extreme. */
      bar.h = Math.max(bar.h, bar.o, bar.c);
      bar.l = Math.min(bar.l, bar.o, bar.c);
      bar.o = round(bar.o, decimals); bar.c = round(bar.c, decimals);
      bar.h = round(bar.h, decimals); bar.l = round(bar.l, decimals);

      /* Volume tracks range and session, with its own noise — the correlation
         is real but it is not an identity, and drawing it as one is a tell. */
      const rng01 = Math.max(tick, bar.h - bar.l);
      /* Volume follows the session and the bar's range, but only follows them:
         range already carries the session, so coupling to both at full weight
         squares the effect and prints an overlap bar twenty times an Asian
         one. Damped so the busiest hour runs roughly 3–4× the quietest, which
         is what the tape actually does. */
      bar.v = Math.max(40, Math.round(
        baseVolume * Math.pow(act, 0.72) * (0.62 + 0.42 * rng01 / (vol * 2))
        * (0.74 + r() * 0.58)));

      /* The path the bar was read off. Kept only on request, because it is
         twelve numbers per bar and only the replay needs them — but it is the
         only honest source for a forming candle: interpolating open→close
         invents an intrabar route the bar never took. */
      if (keepPath) {
        bar.path = path.map(v => round(toTick(v, tick), decimals));
        bar.path[0] = bar.o;
        bar.path[bar.path.length - 1] = bar.c;
      }

      out.push(bar);
      lastShock = Math.abs(c - o) + 1e-9;
      p = c;

      /* register swing extremes once they are confirmed by two bars either
         side — a pivot you can see before it is confirmed is future data */
      const j = out.length - 3;
      if (j >= 1) {
        const a = out[j - 1], b = out[j], d = out[j + 1];
        if (b.h > a.h && b.h > d.h) swings.hi.push({ i: j, p: b.h, taken: false });
        if (b.l < a.l && b.l < d.l) swings.lo.push({ i: j, p: b.l, taken: false });
      }
    }
    return out;
  }

  /* ======================================================================
     aggregate — same contract as timeframe.js, kept here for volume
     ====================================================================== */
  /* LSTF.aggregate does not carry volume or timestamps; a higher frame built
     from flow data has to sum the volume, not drop it. */
  function aggregate(ltf, n) {
    const out = [];
    for (let i = 0; i + n <= ltf.length; i += n) {
      const g = ltf.slice(i, i + n);
      out.push({
        t: g[0].t, session: g[0].session,
        o: g[0].o, c: g[n - 1].c,
        h: Math.max(...g.map(x => x.h)), l: Math.min(...g.map(x => x.l)),
        v: g.reduce((s, x) => s + (x.v || 0), 0)
      });
    }
    return out;
  }

  /* ======================================================================
     footprint() — what happened inside one candle
     ====================================================================== */
  /* Every number here is generated once and then read back: the totals are
     not asserted, they are what the levels add up to. The one thing that is
     deliberately loose is the SIGN of delta — a down candle with positive
     delta is not an error, it is trapped buyers, and a generator that never
     produces one cannot teach absorption. */
  function footprint(bar, opts = {}) {
    const {
      tick = 0.1,
      rows: wantRows = 9,
      seed = 1,
      imbalanceRatio = 3.0,       // 300% diagonal, declared on screen
      imbalanceMin = 40           // below this the ratio is noise, not flow
    } = opts;

    const r = rng(seed);
    const span = Math.max(tick, bar.h - bar.l);
    const rowStep = Math.max(tick, toTick(span / wantRows, tick));
    const prices = [];
    for (let p = bar.l; p <= bar.h + 1e-9; p += rowStep) prices.push(round(p, 4));
    if (prices[prices.length - 1] < bar.h - 1e-9) prices.push(round(bar.h, 4));

    /* Time at price: a bar spends most of its life inside its body and least
       at the tip of its wicks. Weight the rows that way, then let noise move
       the peak off centre so the bar POC is not always the midpoint. */
    const bodyLo = Math.min(bar.o, bar.c), bodyHi = Math.max(bar.o, bar.c);
    const skew = 0.5 + (r() - 0.5) * 0.7;
    const w = prices.map(p => {
      const inBody = p >= bodyLo - 1e-9 && p <= bodyHi + 1e-9;
      const dEdge = Math.min(Math.abs(p - bar.h), Math.abs(p - bar.l)) / span;
      let x = (inBody ? 1.9 : 0.7) + 1.5 * dEdge;
      /* The skew is positioned against the bar's RANGE, not its body. Against
         the body it divides by a number that goes to zero on exactly the bars
         this matters for — a long wick has a small body — so the extreme rows
         get pinned to the floor, and that quietly makes absorption impossible
         to generate at the only place it ever actually happens. */
      const rel = (p - bar.l) / span;
      x *= 0.55 + skew * (1 - Math.abs(rel - skew));
      return Math.max(0.05, x * (0.7 + r() * 0.7));
    });
    /* Absorption is not a label applied afterwards — it is a thing that has to
       happen inside the bar for the label to be true. A bar with a long wick
       sometimes carries a block of size parked at the tip of it: that is a
       passive order eating the aggression, and it is why price got there and
       came straight back. Rolled by the bar's own shape and seed, never by
       what the reel wants to say. */
    const upWick = (bar.h - bodyHi) / span, dnWick = (bodyLo - bar.l) / span;
    let block = null;
    if (upWick > 0.36 && r() < 0.34) block = { end: 'hi', size: 1.7 + r() * 2.1 };
    else if (dnWick > 0.36 && r() < 0.34) block = { end: 'lo', size: 1.7 + r() * 2.1 };
    if (block) {
      const k = block.end === 'hi' ? prices.length - 1 : 0;
      const k2 = block.end === 'hi' ? prices.length - 2 : 1;
      w[k] *= block.size * 2.4;
      if (prices.length > 2) w[k2] *= block.size * 1.3;
    }

    const wSum = w.reduce((a, b) => a + b, 0);

    /* Split each row into bid and ask. Direction tilts the split, but only
       tilts it — and the tilt is per row, so the ladder has both sides
       everywhere the way a real one does. */
    const up = bar.c >= bar.o;
    const tilt = (up ? 0.54 : 0.46) + (r() - 0.5) * 0.10;
    const rows = prices.map((p, k) => {
      const share = w[k] / wSum;
      const total = Math.max(2, Math.round(bar.v * share));
      const near = 1 - Math.abs(p - bar.c) / span;          // flow leans to the close
      const a = Math.min(0.88, Math.max(0.12, tilt + (near - 0.5) * 0.30 + (r() - 0.5) * 0.22));
      const ask = Math.round(total * a);
      return { price: round(p, 4), ask, bid: total - ask };
    }).reverse();                          // index 0 is the top of the ladder

    /* Make the rows add up to the bar exactly. The residue lands on the
       heaviest row, which is where a rounding error is invisible and where it
       cannot change which row is the POC. */
    let sum = rows.reduce((s, x) => s + x.bid + x.ask, 0);
    const heavy = rows.reduce((m, x, k) => (x.bid + x.ask) > (rows[m].bid + rows[m].ask) ? k : m, 0);
    const fix = bar.v - sum;
    if (fix > 0) rows[heavy].ask += fix;
    else {
      let owe = -fix;
      for (let k = 0; k < rows.length && owe > 0; k++) {
        const kk = (heavy + k) % rows.length;
        const take = Math.min(owe, rows[kk].bid);
        rows[kk].bid -= take; owe -= take;
      }
    }
    sum = rows.reduce((s, x) => s + x.bid + x.ask, 0);

    const totalVol = sum;
    const delta = rows.reduce((s, x) => s + x.ask - x.bid, 0);
    const pocRow = rows.reduce((m, x, k) => (x.bid + x.ask) > (rows[m].bid + rows[m].ask) ? k : m, 0);

    /* Diagonal imbalance: ask at a price against bid one price BELOW it, the
       way every footprint platform computes it. Reported only where the ratio
       is actually met and both sides carry real size — an imbalance drawn on
       12 against 3 is decoration. */
    const imbalances = [];
    for (let k = 0; k < rows.length - 1; k++) {
      const a = rows[k].ask, b = rows[k + 1].bid;
      if (a >= imbalanceMin && b > 0 && a / b >= imbalanceRatio)
        imbalances.push({ row: k, side: 'buy', ratio: +(a / b).toFixed(2) });
      if (b >= imbalanceMin && a > 0 && b / a >= imbalanceRatio)
        imbalances.push({ row: k + 1, side: 'sell', ratio: +(b / a).toFixed(2) });
    }

    return {
      rows, total: totalVol, delta,
      poc: rows[pocRow].price, pocRow,
      imbalances,
      imbalanceRatio, imbalanceMin
    };
  }

  /* Absorption is a claim about a level, not about a bar, so it is tested
     against the bar's own outcome: heavy trade at an extreme that price then
     failed to leave in that direction. If the bar closed away from it, the
     size was absorbed; if it closed through it, nothing was. */
  function absorption(bar, fp, opts = {}) {
    const { heavy = 1.9, failFrac = 0.55 } = opts;
    const span = Math.max(1e-9, bar.h - bar.l);
    const avg = fp.total / fp.rows.length;
    const top = fp.rows[0], bot = fp.rows[fp.rows.length - 1];
    const topVol = top.bid + top.ask, botVol = bot.bid + bot.ask;
    if (topVol > avg * heavy && (bar.h - bar.c) / span > failFrac)
      return { at: top.price, side: 'sell', vol: topVol, note: 'حجم عند القمة والسعر ما قدر يثبت' };
    if (botVol > avg * heavy && (bar.c - bar.l) / span > failFrac)
      return { at: bot.price, side: 'buy', vol: botVol, note: 'حجم عند القاع والسعر ما قدر يكسر' };
    return null;
  }

  function attachFlow(candles, opts = {}) {
    const seed0 = opts.seed || 7;
    return candles.map((c, i) => {
      const fp = footprint(c, Object.assign({}, opts, { seed: seed0 + i * 2654435761 % 2147483647 }));
      fp.absorption = absorption(c, fp, opts);
      return fp;
    });
  }

  /* ======================================================================
     profile() — built from the SAME volumes, never re-invented
     ====================================================================== */
  /* The flow argument is what makes this honest: with it, each row of the
     profile is the sum of real per-price trade from the footprints, and the
     profile's grand total equals the sum of the bars' volume by construction.
     Without it the module falls back to time-at-price, and says so. */
  function profile({ candles, from = 0, to = null, bins = 24, valueArea = 0.70,
                     flow = null, tick = 0.1 }) {
    const b = to == null ? candles.length - 1 : to;
    const seg = candles.slice(from, b + 1);
    const hi = Math.max(...seg.map(c => c.h)), lo = Math.min(...seg.map(c => c.l));
    const bh = (hi - lo) / bins;
    const vol = new Array(bins).fill(0);

    if (flow) {
      for (let i = from; i <= b; i++) {
        flow[i].rows.forEach(rw => {
          let k = Math.floor((rw.price - lo) / bh);
          k = Math.max(0, Math.min(bins - 1, k));
          vol[k] += rw.bid + rw.ask;
        });
      }
    } else {
      seg.forEach(c => {
        const a = Math.max(0, Math.floor((c.l - lo) / bh));
        const z = Math.min(bins - 1, Math.floor((c.h - lo) / bh));
        const per = (c.v || 1) / (z - a + 1);
        for (let k = a; k <= z; k++) vol[k] += per;
      });
    }

    const total = vol.reduce((a, c) => a + c, 0);
    const pocIdx = vol.indexOf(Math.max(...vol));
    let acc = vol[pocIdx], loI = pocIdx, hiI = pocIdx;
    while (acc < total * valueArea && (loI > 0 || hiI < bins - 1)) {
      const dn = loI > 0 ? vol[loI - 1] : -1;
      const up = hiI < bins - 1 ? vol[hiI + 1] : -1;
      if (up >= dn) acc += vol[++hiI]; else acc += vol[--loI];
    }
    const rowP = k => lo + (k + 0.5) * bh;
    return {
      lo, hi, bins, bh, vol, total, valueArea,
      poc: toTick(rowP(pocIdx), tick),
      vah: toTick(rowP(hiI) + bh / 2, tick),
      val: toTick(rowP(loI) - bh / 2, tick),
      source: flow ? 'footprint' : 'time-at-price',
      from, to: b
    };
  }

  /* ======================================================================
     vwap() — arithmetic, not an indicator preset
     ====================================================================== */
  function vwap(candles, anchor = 0) {
    const out = new Array(candles.length).fill(null);
    let pv = 0, v = 0;
    for (let i = anchor; i < candles.length; i++) {
      const c = candles[i];
      const typical = (c.h + c.l + c.c) / 3;
      pv += typical * (c.v || 0); v += (c.v || 0);
      out[i] = v ? pv / v : typical;
    }
    return out;
  }

  /* ======================================================================
     findSetup() — the lesson is FOUND, not written
     ====================================================================== */
  /* Give it the conditions in the order they must occur; it walks the series
     forward and returns the first place all of them hold, or null. Each test
     may only look at bars up to its own index — the walk enforces it by
     handing every test a slice that ends where it is standing, so a condition
     physically cannot read a bar that has not printed. */
  function findSetup(candles, { steps, maxGap = 8, from = 20, to = null }) {
    const last = (to == null ? candles.length - 1 : to);
    for (let s = from; s <= last; s++) {
      const hit = [];
      let i = s, ok = true;
      for (const step of steps) {
        let found = -1;
        /* `same: true` is for evidence that belongs to the bar the previous
           step matched — the delta and the ladder of the sweep bar itself.
           It is still not future information: a bar's flow is only complete
           once it closes, which is why it is tested one step later in time
           even though it is read off the same bar. */
        const j0 = step.same && hit.length ? hit[hit.length - 1].bar : i;
        for (let j = j0; j <= Math.min(last, j0 + maxGap); j++) {
          const past = candles.slice(0, j + 1);       // nothing after j exists
          if (step.test(past, j, hit)) { found = j; break; }
        }
        if (found < 0) { ok = false; break; }
        hit.push({ name: step.name, bar: found });
        i = found + 1;
      }
      if (ok) return hit;
    }
    return null;
  }

  /* ======================================================================
     qa() — the mandatory gate, re-derived independently
     ====================================================================== */
  /* Nothing here trusts the generator. Every figure is recomputed from the
     candles and compared; a disagreement is a blocking problem, not a note. */
  function qa({ candles, flow = null, prof = null, vw = null,
                tick = 0.1, decimals = 2, minutes = 5, markup = [], replayRate = null }) {
    const p = [];
    const F = (kind, message) => p.push({ kind, message });
    const eps = tick / 2 + 1e-9;

    candles.forEach((c, i) => {
      if (!(c.h >= c.o - eps && c.h >= c.c - eps && c.h >= c.l - eps))
        F('ohlc', `bar ${i}: high ${c.h} is not the highest of ${c.o}/${c.c}/${c.l}`);
      if (!(c.l <= c.o + eps && c.l <= c.c + eps))
        F('ohlc', `bar ${i}: low ${c.l} is not the lowest of ${c.o}/${c.c}`);
      const rt = v => Math.abs(v / tick - Math.round(v / tick)) < 1e-6;
      if (![c.o, c.h, c.l, c.c].every(rt))
        F('tick', `bar ${i}: ${c.o}/${c.h}/${c.l}/${c.c} is not on the ${tick} tick`);
      const dp = v => (String(v).split('.')[1] || '').length <= decimals;
      if (![c.o, c.h, c.l, c.c].every(dp))
        F('decimals', `bar ${i}: more than ${decimals} decimals`);
      if (i > 0) {
        const d = c.t - candles[i - 1].t;
        if (d !== minutes) F('time', `bar ${i}: spacing is ${d}m, not ${minutes}m`);
      }
      if (c.v != null && !(c.v > 0)) F('volume', `bar ${i}: volume ${c.v}`);
    });

    if (flow) {
      flow.forEach((f, i) => {
        const c = candles[i];
        const sum = f.rows.reduce((s, x) => s + x.bid + x.ask, 0);
        if (sum !== c.v) F('flow', `bar ${i}: ladder sums to ${sum}, bar volume is ${c.v}`);
        if (sum !== f.total) F('flow', `bar ${i}: reported total ${f.total} ≠ ladder ${sum}`);
        const d = f.rows.reduce((s, x) => s + x.ask - x.bid, 0);
        if (d !== f.delta) F('flow', `bar ${i}: reported delta ${f.delta} ≠ ask−bid ${d}`);
        const mx = Math.max(...f.rows.map(x => x.bid + x.ask));
        const pocOk = f.rows.some(x => (x.bid + x.ask) === mx && x.price === f.poc);
        if (!pocOk) F('flow', `bar ${i}: bar POC ${f.poc} is not the heaviest level`);
        f.rows.forEach(rw => {
          if (rw.price < c.l - eps || rw.price > c.h + eps)
            F('flow', `bar ${i}: ladder price ${rw.price} outside ${c.l}–${c.h}`);
          if (rw.bid < 0 || rw.ask < 0) F('flow', `bar ${i}: negative side volume`);
        });
        f.imbalances.forEach(im => {
          const k = im.row;
          const a = im.side === 'buy' ? f.rows[k].ask : f.rows[k].bid;
          const b = im.side === 'buy' ? f.rows[k + 1].bid : f.rows[k - 1].ask;
          if (!(a / b >= f.imbalanceRatio - 1e-9 && a >= f.imbalanceMin))
            F('flow', `bar ${i}: imbalance reported below the declared ${f.imbalanceRatio}× / ${f.imbalanceMin}`);
        });
      });
    }

    if (prof) {
      const re = profile({ candles, from: prof.from, to: prof.to, bins: prof.bins,
                           valueArea: prof.valueArea, flow, tick });
      ['poc', 'vah', 'val'].forEach(k => {
        if (Math.abs(re[k] - prof[k]) > eps)
          F('profile', `${k.toUpperCase()} recomputes to ${re[k]}, page shows ${prof[k]}`);
      });
      const barSum = candles.slice(prof.from, prof.to + 1).reduce((s, c) => s + (c.v || 0), 0);
      if (flow && Math.abs(prof.total - barSum) > 0.5)
        F('profile', `profile total ${prof.total} ≠ the ${barSum} traded over its range`);
      if (!(prof.val < prof.poc + eps && prof.poc < prof.vah + eps))
        F('profile', `VAL ${prof.val} / POC ${prof.poc} / VAH ${prof.vah} are out of order`);
    }

    if (vw) {
      const re = vwap(candles, vw.anchor || 0);
      const i = vw.at != null ? vw.at : candles.length - 1;
      if (Math.abs(re[i] - vw.value) > tick)
        F('vwap', `VWAP at bar ${i} recomputes to ${re[i].toFixed(4)}, page shows ${vw.value}`);
    }

    /* No future information. A drawing may not appear before the replay has
       printed the bar that justifies it. */
    if (replayRate && markup.length) {
      markup.forEach(m => {
        if (m.bar == null || m.at == null) return;
        const earliest = replayRate.timeOfBar(m.bar);
        if (m.at < earliest - 1e-6)
          F('future', `"${m.id}" draws at ${m.at}s but its bar ${m.bar} prints at ${earliest.toFixed(2)}s`);
      });
    }

    return p;
  }

  /* ======================================================================
     realism() — the style yardstick from CHART-REALISM.md
     ======================================================================
     Everything above answers "is this internally consistent?". This answers a
     different question: "does it MOVE like a market?". A series can have
     perfect OHLC integrity, a ladder that sums exactly, and still read as
     generated — because every third candle is red, or one three-candle motif
     covers half the chart, or the bodies at lag 3 correlate at 0.7.

     These are diagnostic ranges for a simulation, not laws the market obeys
     (CHART-REALISM.md §15). They are never applied to real data. */

  const body = c => c.c - c.o;
  const span = c => Math.max(1e-12, c.h - c.l);       // `rng` is the seeded RNG
  const mean = a => a.length ? a.reduce((x, y) => x + y, 0) / a.length : 0;
  const median = a => {
    if (!a.length) return 0;
    const s = [...a].sort((x, y) => x - y), m = s.length >> 1;
    return s.length % 2 ? s[m] : (s[m - 1] + s[m]) / 2;
  };
  function corr(a, b) {
    const n = Math.min(a.length, b.length);
    if (n < 3) return 0;
    const ma = mean(a.slice(0, n)), mb = mean(b.slice(0, n));
    let num = 0, da = 0, db = 0;
    for (let i = 0; i < n; i++) {
      const x = a[i] - ma, y = b[i] - mb;
      num += x * y; da += x * x; db += y * y;
    }
    return da && db ? num / Math.sqrt(da * db) : 0;
  }

  /* Efficiency ratio: net move over the sum of the effort spent making it. */
  function er(candles, from = 0, to = candles.length - 1) {
    const seg = candles.slice(from, to + 1);
    if (seg.length < 2) return 0;
    const net = Math.abs(seg[seg.length - 1].c - seg[0].o);
    const eff = seg.reduce((s, c) => s + Math.abs(body(c)), 0);
    return eff ? net / eff : 0;
  }

  function realism(candles, opts = {}) {
    const { medianWin = 20, motifN = 3, pauseWin = 5 } = opts;
    const n = candles.length;
    const bodies = candles.map(body);
    const ranges = candles.map(span);
    const absB = bodies.map(Math.abs);

    /* --- movement ------------------------------------------------------- */
    const erAll = er(candles);
    const erWin = [];
    for (let i = 0; i + pauseWin <= n; i++) erWin.push(er(candles, i, i + pauseWin - 1));
    const pauseRate = erWin.filter(v => v < 0.35).length / Math.max(1, erWin.length);

    let ov = [];
    for (let i = 1; i < n; i++) {
      const a = candles[i - 1], b = candles[i];
      const lo = Math.max(a.l, b.l), hi = Math.min(a.h, b.h);
      ov.push(Math.max(0, hi - lo) / Math.min(span(a), span(b)));
    }
    const overlap = mean(ov);

    /* Pullback depth needs legs, and a leg needs confirmed pivots — so the
       pivots are the same two-bar-either-side ones the setup search uses. */
    const piv = [];
    for (let i = 2; i < n - 2; i++) {
      const c = candles[i];
      if (c.h > candles[i-1].h && c.h > candles[i-2].h && c.h > candles[i+1].h && c.h > candles[i+2].h)
        piv.push({ i, p: c.h, k: 'h' });
      else if (c.l < candles[i-1].l && c.l < candles[i-2].l && c.l < candles[i+1].l && c.l < candles[i+2].l)
        piv.push({ i, p: c.l, k: 'l' });
    }
    const depths = [];
    for (let k = 2; k < piv.length; k++) {
      if (piv[k - 2].k === piv[k].k) continue;              // not a leg + counter
      const leg = Math.abs(piv[k - 1].p - piv[k - 2].p);
      const back = Math.abs(piv[k].p - piv[k - 1].p);
      if (leg > 0) depths.push(back / leg);
    }
    const pullbackDepth = mean(depths.filter(d => d > 0 && d < 3));

    /* --- morphology ----------------------------------------------------- */
    const bodyRange = mean(candles.map(c => Math.abs(body(c)) / span(c)));
    const buckets = { contraction: 0, normal: 0, displacement: 0, outlier: 0, other: 0 };
    const rel = [];
    /* Outliers are counted, and so are the number of separate EVENTS they form.
       Six candles above 2.80× the rolling median is either a chart with a
       violent expansion in it — a coil, a sweep, a displacement, all touching —
       or a chart with a spiky texture, and the raw count cannot tell those
       apart. The count of contiguous runs can. */
    let outRun = false, outlierRuns = 0;
    for (let i = medianWin; i < n; i++) {
      const med = median(ranges.slice(i - medianWin, i));
      const r = med ? ranges[i] / med : 1;
      rel.push(r);
      if (r > 2.80) { if (!outRun) { outlierRuns++; outRun = true; } } else outRun = false;
      if (r > 2.80) buckets.outlier++;
      else if (r >= 1.50) buckets.displacement++;
      else if (r >= 0.65 && r <= 1.35) buckets.normal++;
      else if (r >= 0.35 && r < 0.80) buckets.contraction++;
      else buckets.other++;
    }
    const relTot = Math.max(1, rel.length);

    /* --- reversal and shape counts -------------------------------------- */
    const dojiCut = 0.12;
    const doji = candles.filter(c => Math.abs(body(c)) / span(c) < dojiCut).length;
    let inside = 0, outside = 0;
    for (let i = 1; i < n; i++) {
      if (candles[i].h <= candles[i-1].h && candles[i].l >= candles[i-1].l) inside++;
      if (candles[i].h >= candles[i-1].h && candles[i].l <= candles[i-1].l) outside++;
    }
    /* Reversal share is defined PER WAVE (CHART-REALISM.md §7), and that is not
       a detail. Over a long sideways series the "net direction" is noise, so
       roughly half the bodies oppose it by construction and the number lands
       near 50% no matter what the market did — a reading that says nothing and
       fails the band every time. So it is measured leg by leg, between the
       confirmed pivots, and each leg is judged against the band for the kind
       of move it actually is. */
    const legs = [];
    for (let k = 1; k < piv.length; k++) {
      const a = piv[k - 1].i, b = piv[k].i;
      if (b - a < 5) continue;
      const seg = candles.slice(a, b + 1);
      const dir = Math.sign(seg[seg.length - 1].c - seg[0].o) || 1;
      const nd = seg.filter(c => Math.abs(body(c)) / span(c) >= dojiCut);
      const rv = nd.length ? nd.filter(c => Math.sign(body(c)) === -dir).length / nd.length : 0;
      const e = er(seg);
      const kind = e >= 0.60 ? 'trend' : e < 0.35 ? 'range' : 'mixed';
      const band = kind === 'trend' ? [0.12, 0.30] : kind === 'range' ? [0.20, 0.45] : [0.12, 0.45];
      legs.push({ from: a, to: b, bars: b - a + 1, er: +e.toFixed(3), kind,
                  reversal: +rv.toFixed(3), ok: rv >= band[0] && rv <= band[1] });
    }
    const legsOk = legs.length ? legs.filter(l => l.ok).length / legs.length : 1;
    const netDir = Math.sign(candles[n-1].c - candles[0].o) || 1;
    const nonDoji = candles.filter(c => Math.abs(body(c)) / span(c) >= dojiCut);
    const reversal = nonDoji.length
      ? nonDoji.filter(c => Math.sign(body(c)) === -netDir).length / nonDoji.length : 0;
    /* The longest same-colour run, and whether it was a displacement. §7 caps
       runs at six "إلا في إزاحة قصيرة مبررة" — so the run is measured with the
       thing that justifies it, rather than the exception being left to
       judgement afterwards: a run whose candles are large against the local
       median and which travelled efficiently IS the displacement the rule
       exempts. */
    const medAll = median(ranges);
    let run = 1, runStart = 0, longestRun = 1, longestAt = 0;
    for (let i = 1; i < n; i++) {
      if (Math.sign(bodies[i]) === Math.sign(bodies[i-1]) && bodies[i] !== 0) {
        run++;
        if (run > longestRun) { longestRun = run; longestAt = runStart; }
      } else { run = 1; runStart = i; }
    }
    const runSeg = candles.slice(longestAt, longestAt + longestRun);
    const runIsDisplacement = longestRun <= 8 &&
      er(runSeg) >= 0.75 &&
      mean(runSeg.map(span)) >= medAll * 1.15;

    /* --- similarity and cyclicity --------------------------------------- */
    const near = (a, b) => Math.abs(a - b) / Math.max(1e-12, Math.max(Math.abs(a), Math.abs(b))) <= 0.15;
    let bodySim = 0, rangeSim = 0, shapeSim = 0;
    for (let i = 1; i < n; i++) {
      if (near(absB[i], absB[i-1])) bodySim++;
      if (near(ranges[i], ranges[i-1])) rangeSim++;
      const f = c => [Math.abs(body(c)) / span(c),
                      (c.h - Math.max(c.o, c.c)) / span(c),
                      (Math.min(c.o, c.c) - c.l) / span(c)];
      const a = f(candles[i-1]), b = f(candles[i]);
      const d = Math.sqrt(a.reduce((s, v, k) => s + (v - b[k]) * (v - b[k]), 0));
      if (d <= 0.15) shapeSim++;
    }
    const denom = Math.max(1, n - 1);

    /* Groups of three, NOT a sliding window (CHART-REALISM.md §8 says
       "مجموعات 3"). Slid, the metric measures something else entirely: the only
       3-gram that can repeat back to back is a constant one, so a run of ten
       green candles reports as "UUD repeats 8×" — a motif that never repeated
       and a count that came from a different motif. Tiled, "one motif covers
       more than half the groups" is the statement it was meant to be. */
    const sym = c => Math.abs(body(c)) / span(c) < dojiCut ? 'N' : (body(c) > 0 ? 'U' : 'D');
    const motifs = {};
    const seq = [];
    for (let i = 0; i + motifN <= n; i += motifN) {
      const m = candles.slice(i, i + motifN).map(sym).join('');
      motifs[m] = (motifs[m] || 0) + 1;
      seq.push(m);
    }
    const motifTot = Math.max(1, seq.length);
    const topMotif = Object.entries(motifs).sort((a, b) => b[1] - a[1])[0] || ['', 0];
    /* The longest consecutive repeat, and WHICH motif achieved it — reporting
       the most frequent motif's name next to another motif's run is how a
       metric lies while every number in it is correct. */
    let rep = 1, maxRep = 1, maxRepOf = seq[0] || '';
    for (let i = 1; i < seq.length; i++) {
      if (seq[i] === seq[i - 1]) {
        rep++;
        if (rep > maxRep) { maxRep = rep; maxRepOf = seq[i]; }
      } else rep = 1;
    }

    const lag = k => ({
      body: corr(bodies.slice(k), bodies.slice(0, n - k)),
      range: corr(ranges.slice(k), ranges.slice(0, n - k)),
      dir: bodies.slice(k).filter((v, i) => Math.sign(v) === Math.sign(bodies[i]) && v !== 0).length /
           Math.max(1, n - k)
    });

    return {
      bars: n,
      er: +erAll.toFixed(3), pauseRate: +pauseRate.toFixed(3),
      overlap: +overlap.toFixed(3), pullbackDepth: +pullbackDepth.toFixed(3),
      bodyRange: +bodyRange.toFixed(3),
      size: { contraction: +(buckets.contraction / relTot).toFixed(3),
              normal: +(buckets.normal / relTot).toFixed(3),
              displacement: +(buckets.displacement / relTot).toFixed(3),
              outlier: buckets.outlier, outlierRuns },
      reversal: +reversal.toFixed(3),          // whole-series, reported not gated
      legs, legsOk: +legsOk.toFixed(3),
      doji: +(doji / n).toFixed(3),
      inside: +(inside / denom).toFixed(3), outside: +(outside / denom).toFixed(3),
      longestRun, longestRunAt: longestAt, runIsDisplacement,
      bodySim: +(bodySim / denom).toFixed(3),
      rangeSim: +(rangeSim / denom).toFixed(3),
      shapeSim: +(shapeSim / denom).toFixed(3),
      motif: { top: topMotif[0], share: +(topMotif[1] / motifTot).toFixed(3),
               groups: motifTot, maxRepeat: maxRep, maxRepeatOf: maxRepOf },
      lag1: lag(1), lag3: lag(3)
    };
  }

  /* The gate. Ranges are CHART-REALISM.md §4–§8; the wave type is read off the
     series' own ER rather than asserted, because the reversal band depends on
     which kind of move this actually is. */
  function realismGate(st, opts = {}) {
    const p = [];
    const F = (kind, message) => p.push({ kind, message });

    if (st.bodyRange < 0.38 || st.bodyRange > 0.58)
      F('bodyRange', `mean Body/Range is ${st.bodyRange}, outside 0.38–0.58`);
    if (st.longestRun > 6 && !st.runIsDisplacement)
      F('run', `${st.longestRun} same-colour bodies in a row at bar ${st.longestRunAt} ` +
               `(limit 6, and this run is not a displacement)`);
    if (st.motif.maxRepeat > 2)
      F('motif', `motif "${st.motif.maxRepeatOf}" repeats ${st.motif.maxRepeat}× consecutively (limit 2)`);
    /* Same sample problem as the lag tests: a 20-candle context card tiles into
       six groups, and one motif landing in four of them is 67% by luck alone.
       Below the floor the share is reported and not judged. */
    const MOTIF_MIN = opts.minMotifGroups == null ? 12 : opts.minMotifGroups;
    if (st.motif.groups >= MOTIF_MIN && st.motif.share > 0.50)
      F('motif', `one motif covers ${(st.motif.share * 100).toFixed(0)}% of ` +
                 `${st.motif.groups} groups (limit 50%)`);
    /* The lag tests need a sample. On a 20-candle H4 card, Direction Match at
       lag 3 has seventeen observations and a standard error near 0.12 — 0.65
       is inside noise, and failing a chart for it is the gate inventing a
       finding. Below the floor the numbers are still reported, just not judged. */
    const LAG_MIN = opts.lagMinBars == null ? 40 : opts.lagMinBars;
    if (st.bars >= LAG_MIN) {
      if (st.lag3.dir >= 0.60)
        F('cyclic', `Direction Match at lag 3 is ${st.lag3.dir.toFixed(2)} — 0.60+ reads as cyclic`);
      if (Math.abs(st.lag3.body) >= 0.40)
        F('cyclic', `|body correlation| at lag 3 is ${Math.abs(st.lag3.body).toFixed(2)} (limit 0.40)`);
    }
    if (st.bodySim === 0 && st.rangeSim === 0)
      F('similarity', 'zero similarity everywhere — as artificial as too much of it');
    const minLegs = opts.minLegsOk == null ? 0.65 : opts.minLegsOk;
    if (st.legs.length >= 3 && st.legsOk < minLegs) {
      const bad = st.legs.filter(l => !l.ok)
        .map(l => `${l.from}–${l.to} ${l.kind} ${(l.reversal * 100).toFixed(0)}%`).slice(0, 4);
      F('reversal', `only ${(st.legsOk * 100).toFixed(0)}% of legs sit inside their reversal band ` +
                    `(need ${(minLegs * 100).toFixed(0)}%): ${bad.join(' · ')}`);
    }
    if (st.bars >= 8 && st.pauseRate === 0)
      F('pause', 'no measurable Pause anywhere — a move longer than 8 bars must contain one');
    /* CHART-REALISM.md §6 says an outlier means "check for news or an error",
       not "forbidden" — so the count is reported and the SHAPE is judged. */
    const maxRuns = opts.maxOutlierRuns == null ? 2 : opts.maxOutlierRuns;
    if (st.size.outlierRuns > maxRuns)
      F('size', `${st.size.outlier} candles above 2.80× the rolling median in ` +
                `${st.size.outlierRuns} separate bursts (limit ${maxRuns}) — spiky texture, not one expansion`);
    if (opts.maxOutliers != null && st.size.outlier > opts.maxOutliers)
      F('size', `${st.size.outlier} candles above 2.80× the rolling median`);
    return p;
  }

  global.LSMarket = {
    rng, gauss, round, toTick, sessionAt, openBoost,
    series, aggregate, footprint, absorption, attachFlow,
    profile, vwap, findSetup, qa, er, realism, realismGate, SESSIONS
  };
})(typeof window !== 'undefined' ? window : globalThis);
