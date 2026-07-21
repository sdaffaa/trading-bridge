export const FPS = 30;
export const TEAL = '#4fd0e0';
export const RED = '#ff5b6a';
export const GREEN = '#39d98a';
export const TRANS = 8;

export const SCENES = {
  black: 36,       // ~1.2s
  chartLow: 110,   // to ~4s
  footprint: 320,  // 4-15s
  explosion: 140,  // 15-20s
  cta: 174,        // 20-25s
};
export const totalStopFrames =
  Object.values(SCENES).reduce((a, b) => a + b, 0) - TRANS * (Object.keys(SCENES).length - 1);

// candle path: downtrend -> sweep low -> explosive rally
export const CLOSES = [
  2358, 2356, 2352, 2354, 2349, 2346, 2348, 2343, 2340, 2342,
  2338, 2336, 2334, /* sweep idx 12 */ 2339, 2345, 2352, 2360, 2366, 2372, 2378, 2384,
];
export const SWEEP_IDX = 12;
export const STOP_PRICE = 2332.6;

// footprint ladder rows (price high->low). b=buy(bid) s=sell(ask)
export const FOOT = [
  {p: 2341, b: 34, s: 41},
  {p: 2340, b: 41, s: 78},
  {p: 2339, b: 48, s: 156},
  {p: 2338, b: 55, s: 284},
  {p: 2337, b: 66, s: 421},
  {p: 2336, b: 78, s: 552},
  {p: 2335, b: 96, s: 631},
  {p: 2334, b: 168, s: 604},
];
export const SWEEP_ROWS = [4, 5, 6, 7]; // stop/absorption zone (0-indexed)
