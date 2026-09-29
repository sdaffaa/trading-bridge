//+------------------------------------------------------------------+
//|                                           GoldAlwaysIn_1to1.mq5  |
//|  XAUUSD always-in-market EA: one position at a time, one SL and  |
//|  one TP at 1:1, a new position opens as soon as the previous one |
//|  closes. Direction = trend filter (best robust result in the     |
//|  research/ backtests: ~56% win rate at 1:1 with 2 x ATR).        |
//+------------------------------------------------------------------+
#property copyright "trading-bridge"
#property version   "1.00"

#include <Trade/Trade.mqh>

enum ENUM_DIR_MODE
  {
   DIR_EMA_CROSS = 0,   // Fast EMA vs Slow EMA (default)
   DIR_EMA_LONG  = 1,   // Price vs long EMA (200)
   DIR_BOTH      = 2    // Both must agree, else fall back to long EMA
  };

//--- inputs
input group "Strategy"
input ENUM_TIMEFRAMES InpSignalTF     = PERIOD_H1;    // Signal timeframe
input ENUM_DIR_MODE   InpDirMode      = DIR_EMA_CROSS;// Direction mode
input int             InpFastEMA      = 20;           // Fast EMA
input int             InpSlowEMA      = 50;           // Slow EMA
input int             InpLongEMA      = 200;          // Long EMA
input int             InpATRPeriod    = 14;           // ATR period
input double          InpATRMult      = 2.0;          // SL = TP = ATR x this (1:1)

input group "Risk"
input double          InpRiskPct      = 1.0;          // Risk per trade, % of balance (0 = fixed lot)
input double          InpFixedLot     = 0.01;         // Fixed lot (used when risk = 0)
input double          InpMaxSpreadUSD = 0.60;         // Skip entry if spread (price units) is above this
input double          InpDailyMaxLossPct = 6.0;       // Pause until next day after this daily loss % (0 = off)
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
   Print("GoldAlwaysIn started on ", sym, " TF=", EnumToString(InpSignalTF),
         " SL=TP=", DoubleToString(InpATRMult, 2), "xATR");
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
   double tp = NormalizeDouble(price + dir * dist, digits);
   double lots = LotSize(dist);
   if(lots <= 0) return;

   bool ok = (dir > 0) ? trade.Buy(lots, sym, price, sl, tp, InpComment)
                       : trade.Sell(lots, sym, price, sl, tp, InpComment);
   if(!ok || (trade.ResultRetcode() != TRADE_RETCODE_DONE && trade.ResultRetcode() != TRADE_RETCODE_PLACED))
      PrintFormat("Entry failed: retcode=%u %s", trade.ResultRetcode(), trade.ResultRetcodeDescription());
   else
      PrintFormat("%s %.2f %s @%.2f SL=%.2f TP=%.2f (dist=%.2f)",
                  dir > 0 ? "BUY" : "SELL", lots, sym, price, sl, tp, dist);
  }

//--- +1 buy, -1 sell, 0 unknown (uses only the last COMPLETED bar)
int Direction()
  {
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
   Comment(StringFormat("GoldAlwaysIn 1:1 | %s\nToday: %d trades, %d W / %d L (%.0f%%)\n%s",
           sym, n, dayWins, dayLosses, n > 0 ? 100.0 * dayWins / n : 0.0,
           TimeCurrent() < pauseUntil ? "PAUSED by risk guard" : "Running"));
  }
//+------------------------------------------------------------------+
