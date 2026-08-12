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
      subSteps = 12,
      baseVolume = 900,
      keepPath = false             // keep the intrabar path for forming-candle replay
    } = opts;

    const r = rng(seed);
    const out = [];

    /* Regime: a slow three-state chain. Drift is small next to noise — a
       trend you can see bar by bar is not a trend, it is a ramp. */
    const REG = [{ d: 0.16, p: 0.985 }, { d: -0.16, p: 0.985 }, { d: 0, p: 0.972 }];
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
      if (near) pull = Math.sign(near.p - p) * barSig * 0.22;

      const drift = REG[reg].d * vol * 0.35 + pull;

      /* the intrabar path */
      const path = [p];
      let x = p;
      for (let k = 0; k < subSteps; k++) {
        let step = gauss(r) * (barSig / Math.sqrt(subSteps)) + drift / subSteps;
        /* an occasional single-tick spike is what makes a wick a wick */
        if (r() < 0.06) step *= 2.6 + r() * 2.2;
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

  global.LSMarket = {
    rng, gauss, round, toTick, sessionAt, openBoost,
    series, aggregate, footprint, absorption, attachFlow,
    profile, vwap, findSetup, qa, SESSIONS
  };
})(typeof window !== 'undefined' ? window : globalThis);
