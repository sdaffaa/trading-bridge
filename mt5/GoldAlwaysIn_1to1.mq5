//+------------------------------------------------------------------+
//|                                           GoldAlwaysIn_1to1.mq5  |
//|  XAUUSD always-in-market EA: one position at a time, one SL and  |
//|  one TP, a new position opens as soon as the previous one closes |
//|  (no pause between trades). Default direction = 3-timeframe vote |
//|  (research/families/A_indicators, most stable combo) with        |
//|  SL = 3 x ATR(H1). TP = SL x InpTPRatio (see mt5/README.md).     |
//+------------------------------------------------------------------+
#property copyright "trading-bridge"
#property version   "2.00"

#include <Trade/Trade.mqh>

enum ENUM_DIR_MODE
  {
   DIR_MTF_VOTE  = 3,   // 3-TF majority vote: H4 Stoch(5) K>D, M5 price<HMA(5), M15 MACD(5,35,5) hist falling (default)
   DIR_EMA_CROSS = 0,   // Fast EMA vs Slow EMA on signal TF
   DIR_EMA_LONG  = 1,   // Price vs long EMA (200) on signal TF
   DIR_BOTH      = 2    // Both must agree, else fall back to long EMA
  };

//--- inputs
input group "Strategy"
input ENUM_DIR_MODE   InpDirMode      = DIR_MTF_VOTE; // Direction mode
input ENUM_TIMEFRAMES InpSignalTF     = PERIOD_H1;    // Signal / ATR timeframe
input int             InpFastEMA      = 20;           // Fast EMA
input int             InpSlowEMA      = 50;           // Slow EMA
input int             InpLongEMA      = 200;          // Long EMA
input int             InpATRPeriod    = 14;           // ATR period
input double          InpATRMult      = 3.0;          // SL = ATR(signal TF) x this
input double          InpTPRatio      = 0.6;          // TP = SL x this (1.0 = 1:1; 0.6 -> ~63% win rate in tests)

input group "Risk"
input double          InpRiskPct      = 1.0;          // Risk per trade, % of balance (0 = fixed lot)
input double          InpFixedLot     = 0.01;         // Fixed lot (used when risk = 0)
input double          InpMaxSpreadUSD = 0.60;         // Skip entry if spread (price units) is above this
input double          InpDailyMaxLossPct = 0.0;       // Pause until next day after this daily loss % (0 = off, trades never stop)
input int             InpMaxConsecLoss   = 0;         // Pause until next day after N losses in a row (0 = off)

input group "Execution"
input string          InpSymbol       = "";           // Symbol (empty = chart symbol, e.g. XAUUSD / GOLD)
input ulong           InpMagic        = 20260929;     // Magic number
input int             InpSlippagePts  = 50;           // Max deviation, points
input string          InpComment      = "GoldAlwaysIn";

//--- globals
CTrade   trade;
string   sym;
int      hFast = INVALID_HANDLE, hSlow = INVALID_HANDLE, hLong = INVALID_HANDLE, hATR = INVALID_HANDLE;
datetime pauseUntil = 0;
datetime lastAttempt = 0;
int      dayWins = 0, dayLosses = 0, consecLoss = 0;
datetime statDay = 0;

//+------------------------------------------------------------------+
int OnInit()
  {
   sym = (InpSymbol == "") ? _Symbol : InpSymbol;
   if(!SymbolSelect(sym, true))
     {
      Print("Symbol not available: ", sym);
      return INIT_FAILED;
     }
   hFast = iMA(sym, InpSignalTF, InpFastEMA, 0, MODE_EMA, PRICE_CLOSE);
   hSlow = iMA(sym, InpSignalTF, InpSlowEMA, 0, MODE_EMA, PRICE_CLOSE);
   hLong = iMA(sym, InpSignalTF, InpLongEMA, 0, MODE_EMA, PRICE_CLOSE);
   hATR  = iATR(sym, InpSignalTF, InpATRPeriod);
   if(hFast == INVALID_HANDLE || hSlow == INVALID_HANDLE || hLong == INVALID_HANDLE || hATR == INVALID_HANDLE)
     {
      Print("Indicator handle creation failed: ", GetLastError());
      return INIT_FAILED;
     }
   trade.SetExpertMagicNumber(InpMagic);
   trade.SetDeviationInPoints(InpSlippagePts);
   trade.SetTypeFilling(PickFilling());
   EventSetTimer(1);   // keeps trying to enter even when ticks are sparse
   Print("GoldAlwaysIn started on ", sym, " mode=", EnumToString(InpDirMode), " SL=",
         DoubleToString(InpATRMult, 2), "xATR(", EnumToString(InpSignalTF), ") TP=SLx", DoubleToString(InpTPRatio, 2));
   TryEnter();         // enter immediately on start if flat
   return INIT_SUCCEEDED;
  }

void OnDeinit(const int reason)
  {
   EventKillTimer();
   IndicatorRelease(hFast); IndicatorRelease(hSlow);
   IndicatorRelease(hLong); IndicatorRelease(hATR);
   Comment("");
  }

void OnTick()  { TryEnter(); }
void OnTimer() { TryEnter(); }

//--- re-enter the moment our position is closed by SL or TP
void OnTradeTransaction(const MqlTradeTransaction &trans,
                        const MqlTradeRequest &request,
                        const MqlTradeResult &result)
  {
   if(trans.type != TRADE_TRANSACTION_DEAL_ADD) return;
   if(!HistoryDealSelect(trans.deal)) return;
   if(HistoryDealGetInteger(trans.deal, DEAL_MAGIC) != (long)InpMagic) return;
   if(HistoryDealGetString(trans.deal, DEAL_SYMBOL) != sym) return;
   long entry = HistoryDealGetInteger(trans.deal, DEAL_ENTRY);
   if(entry != DEAL_ENTRY_OUT && entry != DEAL_ENTRY_OUT_BY) return;

   double pnl = HistoryDealGetDouble(trans.deal, DEAL_PROFIT)
              + HistoryDealGetDouble(trans.deal, DEAL_SWAP)
              + HistoryDealGetDouble(trans.deal, DEAL_COMMISSION);
   RollDay();
   if(pnl >= 0) { dayWins++; consecLoss = 0; }
   else         { dayLosses++; consecLoss++; }
   lastAttempt = 0;
   TryEnter();
  }

//+------------------------------------------------------------------+
void TryEnter()
  {
   RollDay();
   ShowStatus();
   if(HasOpenPosition()) return;
   if(TimeCurrent() < pauseUntil) return;
   if(TimeCurrent() == lastAttempt) return;   // at most one attempt per second
   lastAttempt = TimeCurrent();

   if(!TerminalInfoInteger(TERMINAL_TRADE_ALLOWED) || !MQLInfoInteger(MQL_TRADE_ALLOWED)) return;
   if(SymbolInfoInteger(sym, SYMBOL_TRADE_MODE) != SYMBOL_TRADE_MODE_FULL) return;
   if(RiskGuardHit()) return;

   MqlTick tk;
   if(!SymbolInfoTick(sym, tk) || tk.bid <= 0 || tk.ask <= 0) return;
   if(tk.ask - tk.bid > InpMaxSpreadUSD) return;

   int dir = Direction();
   if(dir == 0) return;

   double atr[1];
   if(CopyBuffer(hATR, 0, 1, 1, atr) != 1 || atr[0] <= 0) return;

   double point  = SymbolInfoDouble(sym, SYMBOL_POINT);
   int    digits = (int)SymbolInfoInteger(sym, SYMBOL_DIGITS);
   double minDist = (SymbolInfoInteger(sym, SYMBOL_TRADE_STOPS_LEVEL) + 5) * point;
   double dist = MathMax(InpATRMult * atr[0], minDist);

   double price = (dir > 0) ? tk.ask : tk.bid;
   double sl = NormalizeDouble(price - dir * dist, digits);
   double tpDist = MathMax(dist * InpTPRatio, minDist);
   double tp = NormalizeDouble(price + dir * tpDist, digits);
   double lots = LotSize(dist);
   if(lots <= 0) return;

   bool ok = (dir > 0) ? trade.Buy(lots, sym, price, sl, tp, InpComment)
                       : trade.Sell(lots, sym, price, sl, tp, InpComment);
   if(!ok || (trade.ResultRetcode() != TRADE_RETCODE_DONE && trade.ResultRetcode() != TRADE_RETCODE_PLACED))
      PrintFormat("Entry failed: retcode=%u %s", trade.ResultRetcode(), trade.ResultRetcodeDescription());
   else
      PrintFormat("%s %.2f %s @%.2f SL=%.2f TP=%.2f (sl dist=%.2f)",
                  dir > 0 ? "BUY" : "SELL", lots, sym, price, sl, tp, dist);
  }

//--- +1 buy, -1 sell, 0 unknown (uses only the last COMPLETED bar)
int Direction()
  {
   if(InpDirMode == DIR_MTF_VOTE) return MtfVote();
   double f[1], s[1], l[1], c[];
   if(CopyBuffer(hFast, 0, 1, 1, f) != 1) return 0;
   if(CopyBuffer(hSlow, 0, 1, 1, s) != 1) return 0;
   if(CopyBuffer(hLong, 0, 1, 1, l) != 1) return 0;
   if(CopyClose(sym, InpSignalTF, 1, 1, c) != 1) return 0;

   int cross = (f[0] > s[0]) ? 1 : -1;
   int lng   = (c[0] > l[0]) ? 1 : -1;
   switch(InpDirMode)
     {
      case DIR_EMA_CROSS: return cross;
      case DIR_EMA_LONG:  return lng;
      default:            return (cross == lng) ? cross : lng;
     }
  }

//--- 3-timeframe majority vote, every input from the last COMPLETED bar of its TF.
//    Mirrors research/families/A_indicators/signals.py (stoch5_KD, px_vs_HMA5 inverted,
//    MACD5_35_hslope inverted) combined with MAJ[] as in validate.py.
int MtfVote()
  {
   int a = StochKD(PERIOD_H4, 5, 3);
   int b = -PriceVsHMA(PERIOD_M5, 5);
   int c = -MacdHistSlope(PERIOD_M15, 5, 35, 5);
   if(a == 0 || b == 0 || c == 0) return 0;
   int s = a + b + c;
   return (s > 0) ? 1 : -1;
  }

int Sgn(double x) { return (x > 0) ? 1 : ((x < 0) ? -1 : 0); }

//--- sign(%K - %D); %K raw (no slowing), %D = SMA(dPer) of %K
int StochKD(ENUM_TIMEFRAMES tf, int kPer, int dPer)
  {
   MqlRates r[];
   ArraySetAsSeries(r, true);
   int need = kPer + dPer;
   if(CopyRates(sym, tf, 1, need, r) != need) return 0;   // r[0] = last completed bar
   double k[];
   ArrayResize(k, dPer);
   for(int j = 0; j < dPer; j++)
     {
      double hh = r[j].high, ll = r[j].low;
      for(int q = j; q < j + kPer; q++) { hh = MathMax(hh, r[q].high); ll = MathMin(ll, r[q].low); }
      if(hh - ll <= 0) return 0;
      k[j] = 100.0 * (r[j].close - ll) / (hh - ll);
     }
   double d = 0;
   for(int j = 0; j < dPer; j++) d += k[j];
   d /= dPer;
   return Sgn(k[0] - d);
  }

//--- linear-weighted MA of x[end-n+1 .. end] (oldest-first array, newest weight = n)
double Wma(const double &x[], int end, int n)
  {
   double num = 0, den = 0;
   for(int w = 1; w <= n; w++) { num += w * x[end - n + w]; den += w; }
   return num / den;
  }

//--- sign(close - HMA(n)) on the last completed bar; HMA = WMA_sqrt(n)(2*WMA_n/2 - WMA_n)
int PriceVsHMA(ENUM_TIMEFRAMES tf, int n)
  {
   int h = MathMax(n / 2, 1), sq = MathMax((int)MathSqrt(n), 1);
   int cnt = n + sq + 2;
   double c[];
   ArraySetAsSeries(c, false);
   if(CopyClose(sym, tf, 1, cnt, c) != cnt) return 0;    // oldest first, c[cnt-1] = last completed
   double raw[];
   ArrayResize(raw, cnt);
   for(int i = n - 1; i < cnt; i++) raw[i] = 2.0 * Wma(c, i, h) - Wma(c, i, n);
   double hma = Wma(raw, cnt - 1, sq);
   return Sgn(c[cnt - 1] - hma);
  }

//--- sign(hist[t] - hist[t-1]), MACD = EMA(f) - EMA(s), signal = EMA(g) of MACD, hist = MACD - signal
int MacdHistSlope(ENUM_TIMEFRAMES tf, int f, int slw, int g)
  {
   int cnt = 600;   // long warm-up so the recursive EMAs converge
   double c[];
   ArraySetAsSeries(c, false);
   int got = CopyClose(sym, tf, 1, cnt, c);
   if(got < slw * 4) return 0;
   double af = 2.0 / (f + 1), aS = 2.0 / (slw + 1), ag = 2.0 / (g + 1);
   double ef = c[0], es = c[0], sig = 0, histPrev = 0, hist = 0;
   for(int i = 0; i < got; i++)
     {
      ef = af * c[i] + (1 - af) * ef;
      es = aS * c[i] + (1 - aS) * es;
      double m = ef - es;
      sig = (i == 0) ? m : ag * m + (1 - ag) * sig;
      histPrev = hist;
      hist = m - sig;
     }
   return Sgn(hist - histPrev);
  }

double LotSize(double dist)
  {
   double vmin = SymbolInfoDouble(sym, SYMBOL_VOLUME_MIN);
   double vmax = SymbolInfoDouble(sym, SYMBOL_VOLUME_MAX);
   double step = SymbolInfoDouble(sym, SYMBOL_VOLUME_STEP);
   double lots = InpFixedLot;
   if(InpRiskPct > 0)
     {
      double tickVal  = SymbolInfoDouble(sym, SYMBOL_TRADE_TICK_VALUE_LOSS);
      if(tickVal <= 0) tickVal = SymbolInfoDouble(sym, SYMBOL_TRADE_TICK_VALUE);
      double tickSize = SymbolInfoDouble(sym, SYMBOL_TRADE_TICK_SIZE);
      if(tickVal <= 0 || tickSize <= 0) return 0;
      double riskMoney = AccountInfoDouble(ACCOUNT_BALANCE) * InpRiskPct / 100.0;
      double lossPerLot = dist / tickSize * tickVal;
      lots = riskMoney / lossPerLot;
     }
   lots = MathFloor(lots / step) * step;
   if(lots < vmin)
     {
      PrintFormat("Lot %.4f below broker minimum %.2f - raise balance/risk or lower ATR mult", lots, vmin);
      return 0;
     }
   return MathMin(lots, vmax);
  }

bool HasOpenPosition()
  {
   for(int i = PositionsTotal() - 1; i >= 0; i--)
     {
      ulong t = PositionGetTicket(i);
      if(t == 0) continue;
      if(PositionGetString(POSITION_SYMBOL) == sym && PositionGetInteger(POSITION_MAGIC) == (long)InpMagic)
         return true;
     }
   return false;
  }

//--- daily loss / losing-streak guard; pauses until the next server day
bool RiskGuardHit()
  {
   bool hit = false;
   if(InpMaxConsecLoss > 0 && consecLoss >= InpMaxConsecLoss) hit = true;
   if(InpDailyMaxLossPct > 0)
     {
      double pnl = TodayPnL();
      double bal = AccountInfoDouble(ACCOUNT_BALANCE);
      if(pnl < 0 && -pnl >= (bal - pnl) * InpDailyMaxLossPct / 100.0) hit = true;
     }
   if(hit)
     {
      pauseUntil = DayStart(TimeCurrent()) + 86400;
      Print("Risk guard hit - paused until ", TimeToString(pauseUntil));
     }
   return hit;
  }

double TodayPnL()
  {
   double pnl = 0;
   if(!HistorySelect(DayStart(TimeCurrent()), TimeCurrent() + 60)) return 0;
   for(int i = HistoryDealsTotal() - 1; i >= 0; i--)
     {
      ulong d = HistoryDealGetTicket(i);
      if(HistoryDealGetInteger(d, DEAL_MAGIC) != (long)InpMagic) continue;
      if(HistoryDealGetString(d, DEAL_SYMBOL) != sym) continue;
      pnl += HistoryDealGetDouble(d, DEAL_PROFIT) + HistoryDealGetDouble(d, DEAL_SWAP)
           + HistoryDealGetDouble(d, DEAL_COMMISSION);
     }
   return pnl;
  }

datetime DayStart(datetime t) { return t - (t % 86400); }

void RollDay()
  {
   datetime d = DayStart(TimeCurrent());
   if(d != statDay) { statDay = d; dayWins = 0; dayLosses = 0; consecLoss = 0; }
  }

ENUM_ORDER_TYPE_FILLING PickFilling()
  {
   long modes = SymbolInfoInteger(sym, SYMBOL_FILLING_MODE);
   if((modes & SYMBOL_FILLING_FOK) == SYMBOL_FILLING_FOK) return ORDER_FILLING_FOK;
   if((modes & SYMBOL_FILLING_IOC) == SYMBOL_FILLING_IOC) return ORDER_FILLING_IOC;
   return ORDER_FILLING_RETURN;
  }

void ShowStatus()
  {
   int n = dayWins + dayLosses;
   Comment(StringFormat("GoldAlwaysIn | %s\nToday: %d trades, %d W / %d L (%.0f%%)\n%s",
           sym, n, dayWins, dayLosses, n > 0 ? 100.0 * dayWins / n : 0.0,
           TimeCurrent() < pauseUntil ? "PAUSED by risk guard" : "Running"));
  }
//+------------------------------------------------------------------+
