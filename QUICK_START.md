# Quick Start - 5 Minutes to Dashboard

**Get Babylon AI Gold Intelligence running in under 5 minutes.**

---

## ⚡ Prerequisites Check (30 seconds)

Open PowerShell and verify you have these installed:

```powershell
py --version          # Python 3.12+
node --version        # Node 24+
npm --version         # npm 11+
```

✅ All showing correct versions? Continue.  
❌ Missing something? See INSTALLATION.md

---

## 🚀 Start Backend (1 minute)

Open **PowerShell** and run:

```powershell
cd D:\BabylonAI_GoldIntelligence
.\run-backend.ps1
```

**Wait for**:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

✅ **Backend is running**

Verify: Open http://localhost:8000/docs in your browser

---

## 🎨 Start Frontend (2 minutes)

Open a **NEW PowerShell window** and run:

```powershell
cd D:\BabylonAI_GoldIntelligence
.\run-frontend.ps1
```

**Wait for**:
```
  ▲ Next.js 
  - Local:        http://localhost:3000
```

✅ **Frontend is running**

---

## 📊 Open Dashboard (30 seconds)

Open your browser to:

### **http://localhost:3000**

You should see:
- ✅ Arabic RTL interface (حزمة بابل)
- ✅ Dark theme with gold accents
- ✅ Warning banner about educational use
- ✅ Timeframe selector buttons
- ✅ "جاري تحميل البيانات..." (Loading...)
- ✅ Analysis results appear in ~5 seconds

---

## 🎯 What You Can Do Now

### Switch Timeframes
Click buttons at top: **5 دقائق | 15 دقيقة | ساعة واحدة | 4 ساعات**

### View Analysis
Each timeframe shows:
- **Current Price** (XAU/USD)
- **Support/Resistance Levels**
- **Technical Indicators** (EMA, RSI, ATR, ADX)
- **Trading Signal** (Buy/Sell with confidence)
- **Risk Assessment** (Position size, account risk)
- **Arabic Summary** (Click to expand)

### Check API Docs
Visit: http://localhost:8000/docs

Test endpoints interactively in Swagger UI

---

## 🛑 Stopping Services

**To stop backend**: Press `Ctrl+C` in backend PowerShell window

**To stop frontend**: Press `Ctrl+C` in frontend PowerShell window

---

## ❓ Something Didn't Work?

### Backend won't start
```powershell
# Check Python version
py --version

# Check port 8000 is available
netstat -ano | findstr :8000
```

### Frontend won't start
```powershell
# Check Node version
node --version

# Check port 3000 is available
netstat -ano | findstr :3000
```

### Dashboard shows loading forever
- ✅ Verify backend is running (check http://localhost:8000/docs)
- ✅ Check browser console (F12 → Console tab) for errors
- ✅ Verify .env.local exists in frontend folder

**For detailed troubleshooting**: See INSTALLATION.md

---

## 📚 Learn More

- **README.md** - Full documentation
- **INSTALLATION.md** - Detailed setup guide
- **VERIFIED_FEATURES.md** - What's implemented
- **API Docs** - http://localhost:8000/docs

---

## ⏱️ Timeline

| Step | Time | Status |
|------|------|--------|
| Prerequisites check | 30s | Quick |
| Backend startup | 1m | Automated |
| Frontend startup | 2m | Automated |
| Dashboard load | 30s | Auto |
| **Total** | **~4 minutes** | ✅ |

---

## 🎓 What This Platform Shows

✅ Technical indicator implementation  
✅ Signal generation algorithms  
✅ Risk management systems  
✅ FastAPI backend design  
✅ Next.js frontend with TypeScript  
✅ Real-time data processing  
✅ Arabic RTL interface  

---

**Next**: Open http://localhost:3000 and explore! 🚀

