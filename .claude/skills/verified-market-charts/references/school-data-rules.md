# Per-school data rules (what each tool may and may not claim)

## SMC / ICT
- Markup must match the candles: no BOS without a close beyond the level; no CHoCH from a single reversal candle;
  Order Block on the last opposite candle before a confirmed impulse; Equal Highs/Lows need a logical tolerance
  within Tick Size (not pixel-identical).
- ICT: FVG = 3 valid candles (gap between candle-1 high and candle-3 low, or inverse). Displacement must show in
  the candle's range+close, not just a label. OTE only after correct swing high/low; show the real fib levels used.

## Volume Profile
- Real profile needs Volume-at-Price or tick/trade data. With OHLCV only, the distribution is **تقديري** — say so.
- Define the exact Fixed-Range / Session start & end. POC = highest-volume level; VAH/VAL from the stated value-
  area % (e.g. 70%). Don't place HVN/LVN cosmetically. Profile total must equal the data's total volume.

## VWAP
- State the type (Session vs Anchored) and the reset/anchor point. Compute from real price×volume. If bar-based,
  say so. Never nudge the VWAP line by hand to touch an entry.

## Volume
- Exchange volume for centralized markets; Tick Volume only where that's all there is (name the provider). Each
  volume bar aligns to its candle's time. Don't invent Volume Climax / Dry-up without supporting data.

## Footprint / Order Flow
- Requires tick/trade data + Bid/Ask (or a documented aggressor-side method) + Tick Size + session/timezone.
  Delta = Ask − Bid. Never infer Bid×Ask/Delta/Absorption from OHLC or candle shape alone.
- If no order-flow data: build an **internally consistent teaching example** (Ask−Bid=Delta; Bar POC = max-volume
  level within the bar; Delta sign need not match candle color — e.g. down candle with positive delta for trapped
  buyers/absorption; Imbalance only at the configured ratio, e.g. 300% diagonal). Label `Footprint تعليمي — بيانات محاكاة`;
  never attach a real contract/exchange.

## Simulation (Mode C) candle integrity
Every candle: High ≥ O,C,L and Low ≤ O,C; body between O and C; wicks reach H/L; even spacing; respect Tick Size /
decimals; no unexplained intrabar gaps. Build the scenario forward in time (context → level → approach → sweep/test
→ evidence → confirmation → entry → stop → target); never draw the outcome first then back-fill candles, and never
use future candles to justify an earlier decision.
