export const FPS = 30;
export const TEAL = '#4fd0e0';
export const RED = '#ff5b6a';
export const GREEN = '#39d98a';

// scene durations (frames). TransitionSeries overlap = TRANS.
export const TRANS = 15;
export const SCENES = {
  hook: 150,        // 5s
  analogy: 570,     // 19s
  conditions: 480,  // 16s
  execution: 390,   // 13s
  closing: 270,     // 9s (net 60s total)
};
export const totalTradeFrames =
  Object.values(SCENES).reduce((a, b) => a + b, 0) - TRANS * (Object.keys(SCENES).length - 1);

// Documented-trade numbers — derived from the chart's visible levels (XAUUSD).
// Replace with the real values before posting.
export const TRADE = {
  symbol: 'XAUUSD',
  entry: 2346.0,
  stop: 2338.0,
  target: 2378.0,
  resultPips: 320,
  rr: '1 : 4',
};
