# Babylon AI Gold Intelligence - Installation Guide

Complete setup instructions for running the platform locally on Windows 10/11.

---

## ✅ Prerequisites Check

Verify your system has the required software installed:

### 1. Python 3.12+

```powershell
py --version
```

Expected output: `Python 3.12.x` or higher

If not installed: Download from https://www.python.org/downloads/

### 2. Node.js 24+ and npm 11+

```powershell
node --version
npm --version
```

Expected output: 
- `v24.x.x` or higher for Node
- `11.x.x` or higher for npm

If not installed: Download from https://nodejs.org/

### 3. Git 2.5+

```powershell
git --version
```

Expected output: `git version 2.5.x` or higher

If not installed: Download from https://git-scm.com/

### 4. Space on Disk

- Minimum: 500 MB
- Recommended: 1 GB

---

## 🚀 Step-by-Step Installation

### Step 1: Navigate to Project Directory

```powershell
cd D:\BabylonAI_GoldIntelligence
```

### Step 2: Backend Setup

#### Option A: Using the Startup Script (Recommended)

```powershell
.\run-backend.ps1
```

The script will:
- Create a Python virtual environment if needed
- Install all required packages
- Start the FastAPI backend on port 8000

#### Option B: Manual Setup

```powershell
# Navigate to backend folder
cd backend

# Create virtual environment
python -m venv .venv

# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Start the server
python main.py
```

**Success indicator**: You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Verify** the backend is running:
- Open browser: http://localhost:8000/docs
- You should see the API documentation (Swagger UI)

### Step 3: Frontend Setup (New Terminal/PowerShell Window)

#### Option A: Using the Startup Script (Recommended)

```powershell
# In a NEW terminal window
cd D:\BabylonAI_GoldIntelligence
.\run-frontend.ps1
```

The script will:
- Install npm dependencies (if needed)
- Create `.env.local` configuration
- Start the Next.js development server on port 3000

#### Option B: Manual Setup

```powershell
# In a NEW terminal window
cd D:\BabylonAI_GoldIntelligence\frontend

# Install dependencies
npm install --legacy-peer-deps

# Create environment file
$content = 'NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1'
Set-Content -Path .env.local -Value $content -Encoding utf8

# Start the development server
npm run dev
```

**Success indicator**: You should see:
```
  ▲ Next.js 16.x.x
  - Local:        http://localhost:3000
```

---

## 🌐 Accessing the Application

Once both backend and frontend are running:

### Frontend Dashboard
- **URL**: http://localhost:3000
- **Language**: Arabic (RTL)
- **Theme**: Dark mode
- **Features**: Live analysis, signal generation, risk assessment

### Backend API Documentation
- **URL**: http://localhost:8000/docs
- **Format**: Swagger/OpenAPI
- **Endpoints**: All available with interactive testing

### API Base URL
- **Development**: http://localhost:8000/api/v1
- **Used by**: Frontend for all data requests

---

## ⚙️ Configuration

### Backend Configuration

Edit `backend/core/config.py` to customize:

```python
# Database path
DATA_DIR = "../BabylonAI_Gold_Data_Starter/data"

# Indicator settings
EMA_SHORT = 20      # Can change to any period
RSI_PERIOD = 14     # Adjust for sensitivity

# Signal thresholds
CONFIRMED_THRESHOLD = 0.7      # Increase for stricter signals
WATCH_THRESHOLD = 0.5          # Lower = more alerts

# Risk management
MAX_POSITION_SIZE = 10.0       # Maximum position size (%)
MAX_LOSS_PER_TRADE = 2.0       # Maximum loss per trade (%)
```

### Frontend Configuration

Edit `frontend/.env.local`:

```env
# Backend API address
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1

# Can point to remote backend if desired
# NEXT_PUBLIC_API_URL=http://your-server:8000/api/v1
```

---

## 🧪 Testing the Installation

### 1. Health Check

```powershell
# Test backend health
curl http://localhost:8000/api/v1/health

# Expected response:
# {
#   "status": "healthy" or "degraded",
#   "backend_version": "0.1.0",
#   "data_loaded": true
# }
```

### 2. Run API Tests

```powershell
cd D:\BabylonAI_GoldIntelligence\backend
.\.venv\Scripts\Activate.ps1
python -m pytest tests/test_api.py -v
```

Expected output: `9 passed` (all tests should pass)

### 3. Load Dashboard

Open http://localhost:3000 in your browser and verify:
- [ ] Page loads with Arabic header
- [ ] Timeframe buttons visible
- [ ] Dark theme applied
- [ ] "جاري تحميل البيانات..." (Loading...) message appears
- [ ] Analysis results appear within 10 seconds

---

## 🔄 Data Loading

### Using Demo Data (Included)

Demo synthetic data is automatically loaded on startup:

```powershell
# Backend automatically loads:
# - BabylonAI_Gold_Data_Starter/data/demo/XAUUSD_5min_SYNTHETIC.csv
# - BabylonAI_Gold_Data_Starter/data/demo/XAUUSD_15min_SYNTHETIC.csv
# - BabylonAI_Gold_Data_Starter/data/demo/XAUUSD_1h_SYNTHETIC.csv
# - BabylonAI_Gold_Data_Starter/data/demo/XAUUSD_4h_SYNTHETIC.csv
```

### Using Live Data (Optional)

Fetch current gold prices:

```powershell
cd BabylonAI_Gold_Data_Starter
py -3 scripts\fetch_live_goldapi.py
```

### Using Historical Data (Optional)

Requires a Twelve Data API key:

```powershell
cd BabylonAI_Gold_Data_Starter
$env:TWELVEDATA_API_KEY = 'YOUR_API_KEY_HERE'
py -3 scripts\fetch_history_twelvedata.py --interval 15min --count 1000
```

---

## 🐛 Troubleshooting

### Backend Won't Start

**Problem**: "python: command not found" or similar

```powershell
# Solution: Use py instead
py main.py

# Or check Python installation
py --version
```

**Problem**: "Port 8000 already in use"

```powershell
# Check what's using the port
netstat -ano | findstr :8000

# Kill the process (get PID from above)
taskkill /PID <PID> /F

# Or use a different port by editing main.py:
# uvicorn.run(..., port=8001)
```

**Problem**: "ModuleNotFoundError: No module named 'fastapi'"

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Frontend Won't Start

**Problem**: "npm: command not found"

```powershell
# Solution: Install Node.js from https://nodejs.org/
# Then restart PowerShell and try again
```

**Problem**: "Port 3000 already in use"

```powershell
# Check what's using the port
netstat -ano | findstr :3000

# Kill the process
taskkill /PID <PID> /F
```

**Problem**: "Cannot GET /..."

```powershell
# The frontend is running but not serving the page
# Ensure backend is running on port 8000
# Check .env.local has correct API_URL
```

### Data Not Loading

**Problem**: "No data found" or empty dashboard

```powershell
# Check demo data exists
cd BabylonAI_Gold_Data_Starter
dir data\demo\

# Verify file names exactly match:
# - XAUUSD_5min_SYNTHETIC.csv
# - XAUUSD_15min_SYNTHETIC.csv
# - XAUUSD_1h_SYNTHETIC.csv
# - XAUUSD_4h_SYNTHETIC.csv

# Check backend loaded data
curl http://localhost:8000/api/v1/data/status
```

**Problem**: "CSV validation error"

```powershell
# Validate CSV files
cd BabylonAI_Gold_Data_Starter
py -3 scripts\validate_csv.py data\demo\XAUUSD_15min_SYNTHETIC.csv
```

### API Connection Errors

**Problem**: "Failed to fetch" in dashboard

1. Verify backend is running:
   ```powershell
   curl http://localhost:8000/api/v1/health
   ```

2. Check .env.local:
   ```powershell
   cat frontend\.env.local
   # Should show: NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
   ```

3. Check CORS in backend config:
   ```powershell
   # Should include localhost:3000
   # backend/core/config.py line ~18
   ```

---

## 📋 Startup Checklist

- [ ] Python 3.12+ installed
- [ ] Node.js 24+ installed
- [ ] npm 11+ installed
- [ ] Project directory accessible
- [ ] Backend virtual environment created
- [ ] Backend dependencies installed
- [ ] Backend running on port 8000
- [ ] Frontend dependencies installed
- [ ] Frontend running on port 3000
- [ ] Dashboard accessible at http://localhost:3000
- [ ] API docs accessible at http://localhost:8000/docs
- [ ] Demo data loaded successfully
- [ ] All tests passing

---

## 🎯 Next Steps

After successful installation:

1. **Explore the Dashboard**
   - Switch between timeframes
   - Review technical indicators
   - Check signal states and confidence levels

2. **Review the Code**
   - Backend logic: `backend/core/`
   - Frontend components: `frontend/components/`
   - API endpoints: `backend/api/routes/`

3. **Customize Settings**
   - Adjust indicator periods
   - Change signal thresholds
   - Modify risk parameters

4. **Test with Real Data** (Optional)
   - Set up API keys (Twelve Data, Gold API)
   - Load historical data
   - Analyze real market conditions

---

## 📞 Getting Help

If you encounter issues:

1. Check this troubleshooting section
2. Review the main README.md
3. Check backend logs for errors
4. Verify all prerequisites are met
5. Try restarting both services

---

**Installation Date**: October 20, 2026
**Status**: Ready for Development
