# Babylon AI Gold Intelligence

**Professional XAU/USD Intraday Market Analysis Platform**

A professional-grade, Arabic-first AI-powered analysis platform for XAU/USD (Gold/USD) intraday trading. Provides technical analysis, signal generation, risk management, and market regime detection.

---

## ⚠️ Important Disclaimer

**This is an educational and research platform ONLY.**

- ❌ No live trading execution
- ❌ No broker order placement
- ❌ No real money operations
- ❌ Sample data is synthetic or historical
- ❌ No investment advice or performance claims

This platform is designed for learning technical analysis and understanding market dynamics. Always consult a licensed financial advisor before trading with real money.

---

## 🎯 Features

### Backend (FastAPI)
- ✅ **OHLC Data Management**: Load and manage XAU/USD candles from CSV
- ✅ **Technical Indicators**: EMA (20/50/200), RSI, ATR, ADX
- ✅ **Market Analysis**: Support/Resistance detection, Market regime identification
- ✅ **Signal Engine**: WATCH, CONFIRMED, INVALIDATED, RISK_BLOCK states
- ✅ **Risk Management**: Position sizing, account risk assessment, stop-loss calculations
- ✅ **Backtesting Support**: Historical analysis with no look-ahead bias
- ✅ **Multi-Timeframe**: 5-min, 15-min, 1-hour, 4-hour analysis
- ✅ **REST API**: Full API with OpenAPI/Swagger documentation

### Frontend (Next.js + React)
- ✅ **RTL Arabic Dashboard**: Professional dark theme with Cairo font
- ✅ **Responsive Design**: Mobile, tablet, and desktop support
- ✅ **Interactive Charts**: Candlestick visualization and indicator overlays
- ✅ **Real-time Indicators**: Live technical indicator display
- ✅ **Signal Cards**: Clear signal presentation with confidence levels
- ✅ **Risk Assessment Panel**: Visual risk evaluation
- ✅ **Arabic Analysis**: Detailed analysis summaries in Arabic (no fabricated data)
- ✅ **Timeframe Selector**: Switch between analysis periods

---

## 📋 Requirements

### Prerequisites
- **Windows 10/11** (Project developed for Windows)
- **Python 3.12+** (for backend)
- **Node.js 24+** / **npm 11+** (for frontend)
- **Git 2.5+** (for version control)

### Verified Components
- Python: `3.12.10`
- Node.js: `v26.7.0`
- npm: `11.19.0`
- Git: `2.56.0`

---

## 🚀 Quick Start

### 1. Clone and Setup

```powershell
cd D:\BabylonAI_GoldIntelligence
git init
git add .
git commit -m "Initial commit"
```

### 2. Start Backend

**Option A: Using PowerShell script (Recommended)**
```powershell
.\run-backend.ps1
```

**Option B: Manual start**
```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python main.py
```

Backend runs on: `http://localhost:8000`
API Docs: `http://localhost:8000/docs`

### 3. Start Frontend

**Option A: Using PowerShell script (Recommended)**
```powershell
.\run-frontend.ps1
```

**Option B: Manual start**
```powershell
cd frontend
npm install
npm run dev
```

Frontend runs on: `http://localhost:3000`

---

## 📊 API Endpoints

### Health
- `GET /api/v1/health` - Backend health status

### Data Management
- `GET /api/v1/data/candles/{interval}` - Get OHLC candles (5min, 15min, 1h, 4h)
- `GET /api/v1/data/status` - Data loading status
- `POST /api/v1/data/reload` - Reload data from disk

### Signal Generation
- `GET /api/v1/signals/generate/{interval}` - Generate trading signal
- `GET /api/v1/signals/signal-history/{interval}` - Get recent signals
- `POST /api/v1/signals/assess-risk/{interval}` - Risk assessment for signal

### Market Analysis
- `GET /api/v1/analysis/complete/{interval}` - Complete market analysis
- `GET /api/v1/analysis/multi-timeframe` - Multi-timeframe comparison

**Full API documentation**: http://localhost:8000/docs

---

## 🏗️ Project Structure

```
D:\BabylonAI_GoldIntelligence\
│
├── backend/                          # FastAPI backend
│   ├── main.py                      # Application entry point
│   ├── requirements.txt              # Python dependencies
│   ├── .venv/                       # Virtual environment (created on first run)
│   │
│   ├── core/                        # Core business logic
│   │   ├── config.py                # Configuration and settings
│   │   ├── models.py                # Data models (Pydantic)
│   │   ├── data_service.py          # OHLC data management
│   │   ├── indicators.py            # Technical indicator calculations
│   │   ├── signal_engine.py         # Trading signal generation
│   │   └── risk_management.py       # Risk assessment
│   │
│   ├── api/                         # API layer
│   │   └── routes/
│   │       ├── health.py            # Health check endpoint
│   │       ├── data.py              # Data endpoints
│   │       ├── signals.py           # Signal endpoints
│   │       └── analysis.py          # Analysis endpoints
│   │
│   └── tests/                       # Unit and integration tests
│       └── test_api.py              # API tests
│
├── frontend/                         # Next.js frontend
│   ├── package.json                 # NPM dependencies
│   ├── next.config.js               # Next.js configuration
│   ├── tsconfig.json                # TypeScript configuration
│   ├── tailwind.config.ts           # Tailwind CSS configuration
│   │
│   ├── app/                         # Next.js app directory
│   │   ├── layout.tsx               # Root layout (Arabic RTL)
│   │   ├── page.tsx                 # Dashboard main page
│   │   └── globals.css              # Global styles
│   │
│   ├── components/                  # React components
│   │   ├── Dashboard.tsx            # Main dashboard layout
│   │   ├── CandlestickChart.tsx    # Price chart visualization
│   │   ├── IndicatorPanel.tsx       # Technical indicators display
│   │   ├── SignalCard.tsx           # Trading signal card
│   │   ├── AnalysisPanel.tsx        # Arabic analysis summary
│   │   ├── TimeframeSelector.tsx    # Timeframe switcher
│   │   └── LoadingSpinner.tsx       # Loading indicator
│   │
│   └── lib/                         # Utilities
│       └── api.ts                   # API client and TypeScript types
│
├── BabylonAI_Gold_Data_Starter/     # Data package (starter included)
│   ├── data/
│   │   ├── demo/                   # Synthetic demo data
│   │   │   ├── XAUUSD_5min_SYNTHETIC.csv
│   │   │   ├── XAUUSD_15min_SYNTHETIC.csv
│   │   │   ├── XAUUSD_1h_SYNTHETIC.csv
│   │   │   └── XAUUSD_4h_SYNTHETIC.csv
│   │   └── live/                   # Live quote and real data
│   │
│   ├── scripts/                    # Data utilities
│   │   ├── fetch_live_goldapi.py   # Fetch live gold prices
│   │   ├── fetch_history_twelvedata.py  # Fetch historical candles
│   │   ├── make_demo.py            # Generate demo data
│   │   └── validate_csv.py         # Validate CSV files
│   │
│   └── tests/                      # Data package tests
│
├── run-backend.ps1                 # Backend startup script
├── run-frontend.ps1                # Frontend startup script
├── README.md                        # This file
└── .git/                           # Git repository

```

---

## 🔧 Configuration

### Backend Configuration (`backend/core/config.py`)

Key settings:

```python
# CORS origins (frontend URLs)
CORS_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

# Indicator periods
EMA_SHORT = 20          # EMA 20
EMA_MEDIUM = 50         # EMA 50
EMA_LONG = 200          # EMA 200
RSI_PERIOD = 14         # RSI period
ATR_PERIOD = 14         # ATR period
ADX_PERIOD = 14         # ADX period

# Signal thresholds
WATCH_THRESHOLD = 0.5              # WATCH signal confidence
CONFIRMED_THRESHOLD = 0.7          # CONFIRMED signal confidence

# Risk management
MAX_POSITION_SIZE = 10.0           # Max position size (%)
MAX_LOSS_PER_TRADE = 2.0           # Max loss per trade (%)
```

### Frontend Configuration

Create `frontend/.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

---

## 📈 Technical Indicators

### Implemented Indicators

| Indicator | Period | Purpose | Signal |
|-----------|--------|---------|--------|
| EMA 20 | 20 | Short-term trend | Price above/below = trend direction |
| EMA 50 | 50 | Medium-term trend | EMA ordering = trend strength |
| EMA 200 | 200 | Long-term trend | Major support/resistance |
| RSI | 14 | Momentum | >70 = overbought, <30 = oversold |
| ATR | 14 | Volatility | Stop-loss sizing, position sizing |
| ADX | 14 | Trend strength | >25 = strong trend, <20 = weak trend |
| Support/Resistance | 20-bar | Key levels | Reversal zones |
| Market Regime | Dynamic | Market type | Uptrend, Downtrend, Ranging |

### Signal States

| State | Confidence | Meaning | Action |
|-------|-----------|---------|--------|
| **CONFIRMED** | ≥ 70% | Strong signal with alignment | Consider trade |
| **WATCH** | 50-70% | Emerging signal | Monitor closely |
| **INVALIDATED** | < 50% | Weak/conflicting signals | Wait for clarity |
| **RISK_BLOCK** | Any | Risk limits exceeded | Do not trade |

---

## 🧪 Testing

### Backend API Tests

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
pytest tests/test_api.py -v
```

### Available Tests

- `test_root()` - Root endpoint
- `test_health_check()` - Health status
- `test_data_status()` - Data loading
- `test_get_candles_*()` - Candle retrieval
- `test_generate_signal_*()` - Signal generation
- `test_complete_analysis_*()` - Complete analysis

### Data Validation

```powershell
cd BabylonAI_Gold_Data_Starter
py -3 scripts\validate_csv.py data\demo\XAUUSD_15min_SYNTHETIC.csv
```

---

## 📊 Data Sources

### Demo/Synthetic Data (Included)
- **Source**: Generated algorithmically
- **Note**: Clearly labeled as `SYNTHETIC_DEMO_NOT_REAL`
- **Use**: Testing, UI development, learning
- **NOT for**: Performance claims, trading

### Live Data (Optional)
- **Provider**: Gold API (goldapi.com) - No API key required
- **Script**: `BabylonAI_Gold_Data_Starter/scripts/fetch_live_goldapi.py`
- **Command**: `py -3 scripts\fetch_live_goldapi.py`

### Historical Data (Optional)
- **Provider**: Twelve Data (twelvedata.com)
- **Requires**: API key (free plan available)
- **Command**: `$env:TWELVEDATA_API_KEY = 'your_key'; py -3 scripts\fetch_history_twelvedata.py --interval 15min --count 1000`

---

## 🚨 Important Limitations

### Data Limitations
- Demo data is synthetic and does not reflect real market conditions
- Historical data depends on external provider availability and API keys
- No tick-level data; only candlestick data
- No volume data from most providers

### Feature Limitations
- No live broker integration
- No order execution
- No real-time streaming (30-second refresh)
- No look-ahead bias protection for backtests (in progress)
- No advanced risk metrics (Sharpe ratio, max drawdown, etc.) yet
- No webhook/Telegram integration (structure ready, not enabled)

### Accuracy Notes
- Support/Resistance detected from recent highs/lows, not advanced methods
- Market regime is simplified (no Fibonacci, advanced pattern recognition)
- Risk calculations assume fixed position sizing
- Backtesting not fully implemented (analysis endpoints only)

---

## 🔐 Security

### What This Platform Does NOT Do
- ❌ Store passwords or credentials
- ❌ Access real brokerage accounts
- ❌ Execute any trades
- ❌ Store personal financial data
- ❌ Transmit data to external services (except configured data providers)

### Running Locally
- All data stays on your machine
- Backend runs on `localhost:8000` (local only by default)
- No cloud services required
- Modify `CORS_ORIGINS` in config to restrict access

---

## 📝 Verified Working Features

### ✅ Backend
- [x] Candle loading from CSV files
- [x] EMA, RSI, ATR, ADX calculations
- [x] Signal generation with confidence scoring
- [x] Risk assessment and position sizing
- [x] Multi-timeframe analysis
- [x] REST API with CORS
- [x] API documentation (Swagger/OpenAPI)
- [x] Data status endpoint
- [x] Health checks

### ✅ Frontend
- [x] Arabic RTL layout
- [x] Dark theme interface
- [x] Timeframe selection (5min, 15min, 1h, 4h)
- [x] Signal display with icons
- [x] Indicator values display
- [x] Risk assessment panel
- [x] Arabic analysis summary (expandable)
- [x] Loading states
- [x] Error handling
- [x] 30-second auto-refresh
- [x] Responsive design

### ✅ Integration
- [x] Frontend ↔ Backend communication
- [x] Real-time signal generation
- [x] Data API endpoints
- [x] Error handling and fallbacks

---

## 🚧 Not Yet Implemented

- [ ] Complete backtesting engine (framework ready)
- [ ] Database persistence (currently RAM-based)
- [ ] User authentication
- [ ] Portfolio tracking
- [ ] Trade history logging
- [ ] TradingView webhooks (structure ready, disabled)
- [ ] Telegram notifications (structure ready, disabled)
- [ ] Advanced charting (Plotly/TradingView integration)
- [ ] ML-based signal enhancement
- [ ] Drag-and-drop strategy builder

---

## 🛠️ Troubleshooting

### Backend won't start

```powershell
# Check Python version
py --version          # Should be 3.10+

# Verify dependencies
cd backend
.\.venv\Scripts\Activate.ps1
pip list | Select-String "fastapi|uvicorn"

# Check port availability
netstat -ano | findstr :8000
```

### Frontend won't start

```powershell
# Check Node version
node --version        # Should be 14+
npm --version         # Should be 6+

# Clear cache and reinstall
cd frontend
rm -r node_modules
npm cache clean --force
npm install
```

### API connection errors

```
Error: "Could not connect to backend"
```

- ✅ Check backend is running: `http://localhost:8000/docs`
- ✅ Check API URL in `frontend/.env.local`
- ✅ Check CORS settings in `backend/core/config.py`
- ✅ Check firewall isn't blocking port 8000/3000

### No data loaded

- ✅ Check demo data exists: `BabylonAI_Gold_Data_Starter/data/demo/`
- ✅ Verify file names: `XAUUSD_5min_SYNTHETIC.csv` (exact case)
- ✅ Check file format: Must be valid CSV with headers

---

## 📚 Documentation

### Key Files
- [Backend Configuration](backend/core/config.py)
- [Data Models](backend/core/models.py)
- [Signal Engine](backend/core/signal_engine.py)
- [Frontend API Client](frontend/lib/api.ts)
- [Data Package README](BabylonAI_Gold_Data_Starter/README_AR.md)

### External References
- [Gold API Docs](https://gold-api.com/docs)
- [Twelve Data API](https://twelvedata.com/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Next.js Guide](https://nextjs.org/docs)

---

## 📞 Support

### Reporting Issues

Include when reporting issues:
1. Python/Node version: `py --version`, `node --version`
2. Error message (full stack trace)
3. Steps to reproduce
4. Which component: Backend/Frontend/Data

### Common Questions

**Q: Can I use real money with this?**
A: No. This is educational only. Never trade with real money using this platform.

**Q: Where do I get historical data?**
A: Use scripts in `BabylonAI_Gold_Data_Starter/scripts/` with your own API keys.

**Q: How do I deploy to production?**
A: Not recommended. This is a development tool. If needed, add authentication, rate limiting, and security hardening first.

---

## 📄 License

This project is provided for educational and research purposes.

---

## 🎓 Learning Path

1. **Start**: Run the demo with synthetic data
2. **Learn**: Study the signal engine logic in `backend/core/signal_engine.py`
3. **Experiment**: Modify indicator thresholds and test results
4. **Extend**: Add new indicators or analysis methods
5. **Share**: Document your findings and improvements

---

## ✨ Built With

- **Backend**: FastAPI, Pydantic, Python 3.12
- **Frontend**: Next.js 16, React 19, Tailwind CSS, TypeScript
- **Charts**: Chart.js, react-chartjs-2
- **Icons**: Lucide React
- **Data**: CSV, External APIs (optional)

---

## 🙏 Acknowledgments

- Data starter package and structure
- Cairo font for Arabic typography
- Open-source technical analysis libraries

---

**Last Updated**: October 20, 2026

**Status**: Functional MVP - Educational Use Only

---

**Remember**: Past performance ≠ future results. Always use proper risk management and never trade with money you can't afford to lose.
