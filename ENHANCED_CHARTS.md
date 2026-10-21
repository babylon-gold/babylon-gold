# Enhanced Charts System

**Status**: ✅ Complete  
**Access**: `http://localhost:3000/charts`

---

## 🎨 Overview

Enhanced Charts provide **professional-grade technical analysis** with interactive candlestick charts, technical indicator panels, and zoom/pan controls.

### **Features**

✅ **Interactive Candlestick Charts**
- Real candlestick visualization with OHLC data
- EMA overlays (20, 50, 200)
- Support/Resistance levels
- Zoom and pan controls

✅ **Technical Indicator Panels**
- RSI(14) chart with overbought/oversold zones
- ADX(14) chart with trend strength zones
- ATR(14) volatility chart

✅ **Multi-Timeframe Support**
- 5min, 15min, 1h, 4h candles
- Real-time data refresh
- Historical data visualization

✅ **User-Friendly Controls**
- 🔍 Zoom in/out (adjust candle density)
- ◄ ► Pan left/right (navigate history)
- ↺ Reset to default view
- Live price display

---

## 📍 Access

### **URL**
```
http://localhost:3000/charts
```

### **Navigation**
From main dashboard → Click "الرسوم البيانية" (Charts) in navigation bar

---

## 🎯 Components

### **1. EnhancedCandlestickChart.tsx**
Main candlestick chart component with:
- 200 historical candles loaded from API
- EMA lines (20/50/200) overlaid
- Support/Resistance reference lines
- Zoom/Pan controls
- Live tooltip on hover
- Auto-refresh every 60 seconds

**Usage:**
```tsx
<EnhancedCandlestickChart timeframe="15min" />
```

### **2. IndicatorCharts.tsx**
Three indicator sub-panels:

**RSI(14) Chart**
- Shows relative strength index (0-100 scale)
- Overbought zone > 70 (red line)
- Oversold zone < 30 (green line)
- Neutral zone 30-70
- Excellent for divergence trading

**ADX(14) Chart**
- Shows trend strength (0-50 scale)
- Weak trend < 25 (green zone)
- Strong trend > 40 (orange zone)
- Use to filter trades (don't trade against strong trends)

**ATR(14) Chart**
- Bar chart showing volatility
- Rising ATR = more volatile (expect bigger moves)
- Falling ATR = consolidation (expect smaller moves)
- Use to set proper stop loss distances

**Usage:**
```tsx
<IndicatorCharts timeframe="15min" />
```

---

## 🎮 Controls Guide

### **Zoom Controls**
- **Zoom In (🔍+)**: Decrease visible candles (show more detail)
- **Zoom Out (🔍-)**: Increase visible candles (show broader view)
- **Pan Left (→)**: Move forward in time (newer data)
- **Pan Right (←)**: Move backward in time (older data)
- **Reset (↺)**: Return to default 50-candle view

### **Interaction**
- **Hover over chart**: See detailed price data in tooltip
- **Click timeframe**: Switch between 5min, 15min, 1h, 4h
- **Auto-refresh**: Data updates every 60 seconds

---

## 📊 Technical Analysis Guide

### **EMA Strategies**

**Golden Cross** (BUY Signal)
```
EMA 20 crosses ABOVE EMA 50
↓
Look for confluence with RSI < 70
↓
Strong uptrend confirmation
```

**Death Cross** (SELL Signal)
```
EMA 20 crosses BELOW EMA 50
↓
Look for confluence with RSI > 30
↓
Strong downtrend confirmation
```

**EMA Alignment**
```
Price > EMA20 > EMA50 > EMA200 = Strong Uptrend ✅
Price < EMA20 < EMA50 < EMA200 = Strong Downtrend ❌
Mixed = No Clear Trend (WAIT) ⏸
```

### **RSI Trading**

| RSI Level | Signal | Action |
|-----------|--------|--------|
| > 70 | Overbought | Sell / Take Profits |
| 50-70 | Bullish | Strong Uptrend |
| 30-50 | Neutral | Consolidation |
| < 30 | Oversold | Buy / Add Positions |

**RSI Divergence** (Powerful!)
- Price makes new high but RSI doesn't → Bullish exhaustion (reverse coming)
- Price makes new low but RSI doesn't → Bearish exhaustion (reverse coming)

### **ADX Trend Filter**

Only trade in direction of ADX trend:
- **ADX < 25**: Low trend strength (avoid breakouts)
- **ADX 25-40**: Moderate trend (good for swing trades)
- **ADX > 40**: Strong trend (best for day trading)

**Rule**: Don't short when ADX > 40 and price trending up!

### **ATR Stop Loss**

Professional SL/TP placement using ATR:

```
Entry Price: 4120.50
1-ATR = 1 × 15.23 = 15.23
2-ATR = 2 × 15.23 = 30.46

Conservative Stop Loss: Entry - 1.5-ATR = 4105.27
Aggressive Stop Loss: Entry - 1.0-ATR = 4105.27

Take Profit: Entry + 2.0-ATR = 4151.23 (Risk/Reward = 1:2)
```

---

## 🔄 Data Refresh

### **Automatic Updates**
- Charts refresh every **60 seconds**
- Loads latest 100-200 candles from API
- New signals from signal engine included

### **Manual Refresh**
- Change timeframe = instant refresh
- Reset button = clears zoom/pan state

### **API Endpoint**
```
GET /api/v1/historical/candles-with-indicators/{interval}
?limit=200
```

Response includes:
```json
{
  "candles": [
    {
      "timestamp_utc": "2026-10-21T12:30:00Z",
      "open": 4120.50,
      "high": 4125.00,
      "low": 4118.50,
      "close": 4123.00,
      "volume": 1500,
      "bar_complete": true
    }
  ],
  "indicators": [
    {
      "ema_20": 4121.85,
      "ema_50": 4118.50,
      "ema_200": 4100.25,
      "rsi": 65.5,
      "adx": 35.2,
      "atr": 15.23,
      "support_level": 4110.00,
      "resistance_level": 4130.00
    }
  ]
}
```

---

## 🎯 Trading Scenarios

### **Scenario 1: Breakout Trade**
```
✓ Price breaks above resistance (red line)
✓ EMA 20 > EMA 50 (momentum)
✓ RSI 50-70 (entering overbought)
✓ ADX > 25 (trend is forming)
✓ ATR rising (volatility expanding)
→ BUY SIGNAL: Good risk/reward setup
```

### **Scenario 2: Reversal from Support**
```
✓ Price touches support (green line)
✓ RSI < 30 (oversold condition)
✓ ADX < 25 (low trend → reversal likely)
✓ ATR dropping (quiet before the move)
→ BUY SIGNAL: High probability reversal
```

### **Scenario 3: Trend Continuation**
```
✓ Price above all 3 EMAs
✓ EMA 20 > EMA 50 > EMA 200
✓ RSI 50-70 (not overextended)
✓ ADX > 40 (strong trend)
→ HOLD/ADD: Ride the trend
```

### **Scenario 4: No Trade (WAIT)**
```
✗ Price oscillating between EMAs
✗ RSI stuck at 50
✗ ADX < 20 (no trend)
✗ No clear S/R confluence
→ WAIT: For better setup
```

---

## 📈 Best Practices

### **Chart Viewing**
1. Start with **1h timeframe** for general trend
2. Zoom to **15min** for entry confirmation
3. Check **5min** for exact entry point
4. Always use **4h** to confirm overall market bias

### **Indicator Confirmation**
- Use **RSI + ADX** together (RSI shows momentum, ADX shows trend)
- **EMA crossover** is primary signal
- **Support/Resistance** confirms entry zones
- **ATR** determines proper position sizing

### **Risk Management**
- Set stop loss at support/resistance + 0.5-ATR (safety margin)
- Set take profit at 1.5-2.0x risk distance
- Never risk more than 1-2% per trade
- Use ATR to size position accordingly

---

## 🔧 Technical Details

### **Technologies**
- **Recharts**: Candlestick & indicator visualization
- **Chart.js**: Alternative charting (legacy support)
- **React Hooks**: State management for zoom/pan
- **TailwindCSS**: Styling

### **Performance**
- Loads 200 candles max (balance between detail & speed)
- Charts render at 60fps
- Zoom/pan is GPU-accelerated
- Auto-cleanup on component unmount

### **Data Sources**
- Historical OHLC data: `/api/v1/data/candles/{interval}`
- Indicator values: `/api/v1/historical/candles-with-indicators/{interval}`
- Both endpoints use **real CSV data** from gold market

---

## 📚 Files

```
frontend/
├── components/
│   ├── EnhancedCandlestickChart.tsx (150 lines)
│   ├── IndicatorCharts.tsx (200 lines)
│   └── Navigation.tsx (updated with /charts link)
├── app/
│   └── charts/
│       └── page.tsx (full page component)
└── package.json (added recharts)
```

---

## 🚀 Next Steps

### **Optional Enhancements**
- [ ] Add volume profile
- [ ] Add Bollinger Bands
- [ ] Add MACD indicator
- [ ] Add Fibonacci retracement levels
- [ ] Export chart as PNG
- [ ] Save custom chart layouts
- [ ] Add alert when price touches S/R

### **Integration Points**
- Charts auto-load from `/signals` endpoint (signal history)
- Charts display current signal state on candlestick
- Clicking on candlestick shows signal details

---

## ❓ FAQ

**Q: Why is the chart showing old data?**  
A: Charts load 200 candles by default. Use pan right to see older data. Data refreshes every 60 seconds.

**Q: Can I see real-time updates?**  
A: Yes! Charts auto-refresh every 60 seconds with latest candles. Change timeframe to trigger immediate refresh.

**Q: Why are some candles missing?**  
A: Markets close/reopen. API returns only complete bars. Use zoom out to see more candles.

**Q: How do I interpret support/resistance lines?**  
A: Green = buy zone (bounce from here), Red = sell zone (resistance here). These are calculated from EMA200 ± volatility.

**Q: What's the best timeframe for analysis?**  
A: Use multiple timeframes! 1h for trend, 15min for entry, 5min for timing. Always trade direction of higher timeframe.

---

## 📞 Support

For issues:
1. Check browser console (F12) for errors
2. Verify backend is running (`http://localhost:8000/docs`)
3. Check data status: `/api/v1/data/status`
4. Restart frontend: kill node, npm run dev

---

## 🎉 You're All Set!

Your platform now has **professional technical analysis charts** ready for serious trading analysis! 📈

Navigate to `/charts` and start analyzing! 🚀
