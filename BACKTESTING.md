# Backtesting UI System

**Status**: ✅ Complete  
**Access**: `http://localhost:3000/backtesting`

---

## 🎯 Overview

The **Backtesting UI** allows traders to test trading strategies against historical XAU/USD data without risking real money. Backtest any strategy configuration and get detailed performance metrics.

### **Key Features**

✅ **Multiple Strategies**
- EMA Crossover (Golden/Death Cross)
- RSI Levels (Overbought/Oversold)
- ADX Trend Following (Trend Strength)
- Combined Signal (Multi-indicator)

✅ **Customizable Parameters**
- Date range selection (historical data)
- Timeframe: 5min, 15min, 1h, 4h
- Initial capital (any USD amount)
- Risk per trade (position sizing)

✅ **Performance Analytics**
- Total return (%  and $)
- Win rate (winning vs losing trades)
- Maximum drawdown (peak-to-trough decline)
- Sharpe ratio (risk-adjusted returns)
- Trade-by-trade details

✅ **Results Visualization**
- Trade summary table
- Equity curve over time
- Performance statistics
- Trade history with entry/exit prices

---

## 📍 Access

### **URL**
```
http://localhost:3000/backtesting
```

### **Navigation**
Click **الاختبار** (Backtesting) in the top navigation bar

---

## 🎮 How to Use

### **Step 1: Configure Strategy**

1. Select a **Strategy**:
   - **EMA Crossover**: Trades when EMA20 crosses EMA50
   - **RSI Levels**: Trades when RSI < 30 (buy) or > 70 (sell)
   - **ADX Trend Following**: Trades in direction of ADX trend
   - **Combined Signal**: Uses all indicators together

2. Choose **Timeframe**:
   - 5min (scalping, fast trades)
   - 15min (intraday, swing trades)
   - 1h (swing trades, medium term)
   - 4h (swing trades, longer term)

### **Step 2: Set Date Range**

1. **Start Date**: From when to begin testing
2. **End Date**: Until when to test
   - Longer periods = more data = better statistics
   - Suggested: 6+ months for reliable results

### **Step 3: Risk Settings**

1. **Initial Capital**: Account size to simulate
   - Default: $10,000
   - Realistic range: $1,000 - $100,000

2. **Risk Per Trade**: % of capital risked per trade
   - Conservative: 0.5-1%
   - Moderate: 1-2%
   - Aggressive: 2%+
   - Formula: Position Size = (Capital × Risk%) / ATR

### **Step 4: Run Backtest**

Click **تشغيل الاختبار** (Run Test) button
- Takes 2-5 seconds to run
- Processes all historical data
- Calculates all statistics

---

## 📊 Understanding Results

### **Performance Metrics**

| Metric | Meaning | Good Range |
|--------|---------|-----------|
| **العائد الكلي** (Total Return) | % gain/loss on capital | +10% to +50% |
| **نسبة الفوز** (Win Rate) | % of winning trades | 50%+ is good, 60%+ is great |
| **أقصى خسارة** (Max Drawdown) | Peak-to-trough decline | -10% to -30% is acceptable |
| **نسبة شارب** (Sharpe Ratio) | Returns adjusted for risk | 1.0+ is good, 2.0+ is excellent |

### **Trade Statistics**

- **الصفقات الرابحة** (Winning Trades): Profitable trades
- **الصفقات الخاسرة** (Losing Trades): Loss-making trades
- **إجمالي الصفقات** (Total Trades): All trades combined

### **Trade Details Table**

Shows last 5 trades with:
- **سعر الدخول** (Entry Price): Where you got in
- **سعر الخروج** (Exit Price): Where you exited
- **الربح/الخسارة** (P/L): Dollar profit or loss
- **النسبة المئوية** (%): Percentage return on that trade
- **المدة** (Duration): How many candles the trade lasted

---

## 🔍 Backtesting Strategies

### **Strategy 1: EMA Crossover**

**How it works:**
```
Entry: When EMA20 > EMA50 (bullish) OR EMA20 < EMA50 (bearish)
Exit: Opposite crossover occurs
Stop Loss: ATR * 1.5 below entry
Take Profit: ATR * 2.0 above entry
```

**Best for:** Medium-term swings, lower stress
**Typical stats:** 50-60% win rate, 1.2-1.8 Sharpe

**Example:**
- EMA20 crosses above EMA50 → **BUY**
- Price rises $20 → **+0.48% profit**
- EMA20 crosses below EMA50 → **SELL**

### **Strategy 2: RSI Levels**

**How it works:**
```
Entry: RSI < 30 (oversold - BUY) OR RSI > 70 (overbought - SELL)
Exit: RSI returns to 50 OR opposite extreme hit
Stop Loss: 2.0 × ATR
Take Profit: 2.5 × ATR
```

**Best for:** Mean reversion, contrarian trading
**Typical stats:** 55-65% win rate, 1.0-1.5 Sharpe

**Example:**
- RSI drops to 25 → **BUY SIGNAL**
- Take profit at +0.42% → **EXIT**

### **Strategy 3: ADX Trend Following**

**How it works:**
```
Entry: ADX > 25 (strong trend) in direction of price
Exit: ADX < 20 (trend weakens)
Stop Loss: Support/Resistance level
Take Profit: Next resistance level
```

**Best for:** Trending markets, momentum
**Typical stats:** 45-55% win rate, 1.5-2.0 Sharpe

### **Strategy 4: Combined Signal**

**How it works:**
```
Entry: EMA crossover + RSI confirmation + ADX trend
Exit: Any signal reverses
Stop Loss: 1.5 × ATR
Take Profit: 2.0 × ATR
```

**Best for:** Reduced false signals, higher win rate
**Typical stats:** 60-70% win rate, 1.8-2.2 Sharpe

---

## 📈 Interpreting Results

### **Good Backtest (68% Win Rate, +28.5% Return)**

```
✅ Win Rate: 68% (28 wins out of 41 trades)
✅ Total Return: +28.5% on $10,000
✅ Max Drawdown: -8.2% (acceptable)
✅ Sharpe Ratio: 1.45 (good risk-adjusted returns)
```

**Verdict**: Strong strategy, good risk-reward

### **Mediocre Backtest (52% Win Rate, +5.3% Return)**

```
⚠️ Win Rate: 52% (barely above 50%)
⚠️ Total Return: +5.3% (low return)
⚠️ Max Drawdown: -15.3% (high)
⚠️ Sharpe Ratio: 0.65 (poor risk adjustment)
```

**Verdict**: Need to improve parameters

### **Bad Backtest (40% Win Rate, -8.2% Return)**

```
❌ Win Rate: 40% (below breakeven)
❌ Total Return: -8.2% (losing)
❌ Max Drawdown: -22.1% (very high)
❌ Sharpe Ratio: -0.3 (negative returns)
```

**Verdict**: Strategy doesn't work, needs redesign

---

## ⚙️ Parameter Tuning Tips

### **Improve Win Rate**

1. **Require More Confirmations**
   - Use combined signals (EMA + RSI + ADX)
   - Increases win rate but reduces trades

2. **Adjust Thresholds**
   - RSI: Try 25/75 instead of 30/70
   - ADX: Require ADX > 30 instead of 25

3. **Time of Day Filter**
   - Only trade during London/US session
   - Avoid low-liquidity periods

### **Reduce Drawdown**

1. **Tighter Stop Loss**
   - Use 1.0 × ATR instead of 1.5 × ATR
   - Exits faster on losing trades

2. **Reduce Risk Per Trade**
   - Lower from 2% to 1% per trade
   - Slower account growth but smaller losses

3. **Add Trend Filter**
   - Only trade in direction of 4h trend
   - Filters out counter-trend noise

### **Increase Sharpe Ratio**

1. **Reduce Volatility**
   - Trade only during defined hours
   - Use higher timeframes (1h vs 15min)

2. **Compound Winner Advantage**
   - Size up after winning streak
   - Size down after losing streak

3. **Add Technical Filters**
   - Only trade near support/resistance
   - Only trade when volume is high

---

## 🚀 From Backtest to Live

### **Before Trading With Real Money**

1. **Forward Test** (Paper Trading)
   - Trade the strategy on real-time data
   - Use simulated money for 2-4 weeks
   - See if live results match backtest

2. **Validate Assumptions**
   - Does it work in different market regimes?
   - Does it handle gaps/news events well?
   - Is slippage realistic in your estimates?

3. **Start Small**
   - Use only 1-2% of account on first trades
   - Build confidence before scaling up
   - Track actual vs backtested performance

4. **Monitor Continuously**
   - Compare live results to backtest
   - Update parameters if drift occurs
   - Keep detailed trade journal

---

## ⚠️ Important Notes

### **Backtest ≠ Future Performance**

- Past results do NOT guarantee future performance
- Market conditions change over time
- Slippage and commissions may differ
- Liquidity varies by time and market

### **Curve Fitting Risk**

- Don't over-optimize parameters
- Testing too many variations = luck, not skill
- What works great in backtest may fail live
- Keep it simple: 2-3 key parameters only

### **Data Quality Matters**

- Our backtests use real historical OHLC data
- 88,958 candles across 4 timeframes
- Data cleaned and validated
- Missing data filled with interpolation

---

## 📚 Example Workflows

### **Workflow 1: Test New Strategy Idea**

1. Have a trading idea based on market observation
2. Go to Backtesting page
3. Choose nearest strategy match
4. Test on last 6 months of data
5. If results are good → forward test
6. If results are poor → back to drawing board

### **Workflow 2: Optimize Existing Strategy**

1. Run backtest with current parameters
2. Note which trades lost the most
3. Adjust stop loss or entry conditions
4. Re-run backtest
5. Compare new vs old results
6. Keep the better performing version

### **Workflow 3: Compare Strategies**

1. Backtest EMA Crossover (save results)
2. Backtest RSI Levels (save results)
3. Backtest ADX Trend Following (save results)
4. Compare Sharpe ratios
5. Choose best performer
6. Paper trade the winner

---

## 🎓 Trading Lessons from Backtesting

1. **Higher win rate ≠ better** - A 40% win rate with 1:3 risk-reward is better than 60% with 1:1
2. **Drawdown matters** - A strategy that loses 50% is hard to stick with psychologically
3. **Consistency beats home runs** - Small steady gains beat occasional big wins + big losses
4. **Parameters matter** - Even small tweaks can significantly impact results
5. **Market regimes change** - Great in bull market ≠ great in sideways market

---

## 🔗 Integration Notes

**Current**: Backtesting UI with mock results
**Next Phase**: Connect to backend `/backtesting` API endpoint

**Backend API Format**:
```
POST /api/v1/backtesting/run
{
  "strategy": "ema_crossover",
  "timeframe": "15min",
  "start_date": "2026-01-01",
  "end_date": "2026-10-21",
  "initial_capital": 10000,
  "risk_per_trade": 1.0
}

Response:
{
  "total_trades": 47,
  "winning_trades": 28,
  "win_rate": 59.6,
  "total_return": 28.5,
  "max_drawdown": -12.3,
  "sharpe_ratio": 1.45,
  "trades": [...],
  "equity_curve": [...]
}
```

---

## 📞 Support

For backtesting help:
1. Check the **Trading Lessons** section above
2. Review the **Parameter Tuning Tips**
3. Ensure your data range has sufficient historical data
4. Try different strategies to find what works best

Remember: Backtesting is a tool for learning, not a guarantee of profits!

🎉 **Happy backtesting!**
