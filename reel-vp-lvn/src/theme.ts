// Brand + layout + timeline constants (Liquidity State)
export const FPS = 30;
export const DURATION_S = 22.0;
export const W = 1080;
export const H = 1920;

export const COLORS = {
  bgTop: '#0E1E24',
  bgBot: '#12262E',
  surface: '#1B3A45',
  white: '#F2F5F7',
  grey: '#9FB4BC',
  teal: '#2ECC9A',      // bullish / accept
  tealDim: '#1f6b5a',
  red: '#E15A5A',       // bearish / SL
  cyan: '#37D0E0',      // accent / nPOC target (<=10% usage)
  gold: '#D6A94A',      // rare accent
  black: '#0A0C10',
  candleUp: '#26A69A',  // TradingView native
  candleDown: '#EF5350',
};

// Chart pane geometry (inside 9:16 safe zones)
export const CHART = {
  x: 44, y: 315, w: 992, h: 985,   // full pane
  profW: 210,                      // right-side profile width
};
export const PRICE_LO = 3314.5;
export const PRICE_HI = 3357.5;

// Beat timeline (seconds) — the 22s "under-30%" cut
export const BEATS = {
  b1: 0.0, b2: 3.0, b3: 4.6, b4: 5.4, b5: 6.8, b7: 10.0,
  b8: 13.2, b9: 14.8, b10: 18.6, b11: 19.8, end: 22.0,
};

export const s = (sec: number) => Math.round(sec * FPS);
