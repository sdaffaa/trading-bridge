/* ==========================================================================
   Liquidity State — Karaoke caption track
   Short caption groups (1–4 words) swapped at speech pace. Measured cadence
   from the reference: median hold 0.60s, range 0.3–1.1s.

   Drive with seek(t) so caption timing and chart timing share one clock.
   Text may contain <em> to mark the one term that carries gold emphasis —
   a number, a level name, the thing the sentence is actually about.
   ========================================================================== */

(function (global) {
  'use strict';

  const HOLD = 0.6;              // default hold when a cue gives no duration

  function LSCaptions({ mount, track = [], hold = HOLD }) {
    const host = typeof mount === 'string' ? document.querySelector(mount) : mount;

    /* Normalise: accept [{t, text}] or ["text", …] (auto-spaced at `hold`) */
    const cues = track.map((c, i) =>
      typeof c === 'string' ? { t: i * hold, text: c } : c
    ).sort((a, b) => a.t - b.t);

    cues.forEach((c, i) => {
      c.end = c.end != null ? c.end
            : (i + 1 < cues.length ? cues[i + 1].t : c.t + hold);
    });

    const node = document.createElement('div');
    node.className = 'ls-reel-caption';
    host.appendChild(node);

    let shown = -1;
    function seek(t) {
      let idx = -1;
      for (let i = 0; i < cues.length; i++) {
        if (t >= cues[i].t && t < cues[i].end) { idx = i; break; }
      }
      if (idx === shown) return api;
      shown = idx;
      node.innerHTML = idx < 0 ? '' : cues[idx].text;
      return api;
    }

    function duration() { return cues.length ? cues[cues.length - 1].end : 0; }

    const api = { node, seek, duration, get cues() { return cues; } };
    return api;
  }

  /* Build a track from plain lines at a fixed pace, with optional per-line
     duration: "text" or ["text", seconds]. Returns [{t, text, end}]. */
  LSCaptions.pace = function (lines, { start = 0, hold = HOLD } = {}) {
    let t = start;
    return lines.map(l => {
      const [text, d] = Array.isArray(l) ? l : [l, hold];
      const cue = { t, text, end: t + d };
      t += d;
      return cue;
    });
  };

  LSCaptions.HOLD = HOLD;
  global.LSCaptions = LSCaptions;
})(window);
