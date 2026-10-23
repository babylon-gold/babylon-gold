# Babylon AI Gold Intelligence - Production Quick Start Guide

## 🚀 Your Platform is LIVE!

**Frontend:** https://babylon-gold.vercel.app  
**Backend API:** https://babylon-gold-backend.onrender.com/api/v1  
**Telegram Bot:** @thairaljaabibot

---

## Daily Operations

### Check System Health
```bash
# Backend health check
curl https://babylon-gold-backend.onrender.com/api/v1/health

# Should return:
# {"status":"healthy","backend_version":"0.1.0","data_loaded":true}
```

### Test Analysis Endpoint
```bash
# Get 15-minute analysis
curl "https://babylon-gold-backend.onrender.com/api/v1/analysis?timeframe=15min"

# Get analysis across all timeframes
curl "https://babylon-gold-backend.onrender.com/api/v1/analysis/multi-timeframe"
```

### Monitor Telegram Notifications
```bash
# Check notification status
curl https://babylon-gold-backend.onrender.com/api/v1/notifications/status

# Should show: telegram_enabled: true, telegram_configured: true
```

---

## Available API Endpoints

### Analysis Endpoints
```
GET /api/v1/analysis?timeframe=15min
GET /api/v1/analysis/multi-timeframe
```

Supported timeframes: `5min`, `15min`, `1h`, `4h`

### Notification Endpoints
```
GET /api/v1/notifications/status
POST /api/v1/notifications/test-signal
POST /api/v1/notifications/test-analysis
POST /api/v1/notifications/test-risk
GET /api/v1/notifications/telegram-setup-guide
```

### Health & Status
```
GET /api/v1/health
GET /api/v1/notifications/preferences
```

---

## Deploying Updates

### Step 1: Make Changes Locally
```bash
cd D:\BabylonAI_GoldIntelligence
# Edit files...
```

### Step 2: Commit & Push
```bash
git add .
git commit -m "Your change description"
git push origin main
```

### Step 3: Auto-Deployment
- **Vercel** (Frontend): Automatically redeploys on push to main (~1-2 min)
- **Render** (Backend): Automatically redeploys on push to main (~2-3 min)

### Step 4: Verify Deployment
```bash
# Check backend
curl https://babylon-gold-backend.onrender.com/api/v1/health

# Check frontend
# Visit https://babylon-gold.vercel.app in browser
```

---

## Telegram Notifications

### How It Works
1. Backend analyzes XAU/USD data
2. Generates trading signals
3. Sends notifications to Telegram via @thairaljaabibot
4. You receive alerts in real-time 📲

### Notification Types
- 📈 **Trading Signals**: BUY/SELL alerts with confidence scores
- 📊 **Analysis Updates**: Market analysis summaries
- ⚠️ **Risk Alerts**: Risk management warnings
- 🔧 **System Status**: Platform health updates

### Test Notifications
```bash
# Send test signal notification
curl -X POST https://babylon-gold-backend.onrender.com/api/v1/notifications/test-signal

# Send test analysis notification
curl -X POST https://babylon-gold-backend.onrender.com/api/v1/notifications/test-analysis
```

---

## Monitoring & Troubleshooting

### Check Backend Logs
1. Go to: https://dashboard.render.com
2. Select your babylon-backend service
3. View "Logs" tab for errors

### Check Frontend Deployment
1. Go to: https://vercel.com/dashboard
2. Select babylon-gold project
3. View deployment status & logs

### Common Issues

#### Backend Returns 500 Error
- Check Render logs for specific error
- Verify environment variables (TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID)
- Try restarting service on Render dashboard

#### No Telegram Notifications
- Verify bot token is correct: `TELEGRAM_BOT_TOKEN`
- Verify chat ID is correct: `TELEGRAM_CHAT_ID`
- Try test endpoint: `/api/v1/notifications/test-signal`
- Check if bot needs `/start` command activation

#### Frontend Not Showing Data
- Check browser console (F12) for errors
- Verify `NEXT_PUBLIC_API_URL` is set to backend URL
- Check CORS settings on backend
- Try hard refresh (Ctrl+Shift+R)

---

## Git Workflow

### View Deployment History
```bash
# See all releases
git tag

# See commits since last release
git log v1.0.0..main

# Create new release
git tag -a v1.1.0 -m "Release 1.1.0 - Description"
git push origin v1.1.0
```

### Rollback to Previous Version
```bash
# If needed, create rollback branch
git checkout v1.0.0 -b rollback-v1.0.0
git push origin rollback-v1.0.0

# Then in Vercel/Render, redeploy from that commit
```

---

## Performance Metrics

### Expected Response Times
- Health check: < 50ms
- Analysis endpoint: 100-200ms
- Multi-timeframe: 200-500ms

### Expected Uptime
- Render backend: 99.9% (auto-restart on failure)
- Vercel frontend: 99.99% (global CDN)

---

## Environment Variables Reference

### Frontend (.env.local)
```
NEXT_PUBLIC_API_URL=https://babylon-gold-backend.onrender.com/api/v1
```

### Backend (.env) - CREDENTIALS MUST BE SET
```
TELEGRAM_BOT_TOKEN=<ROTATE_IN_BOTFATHER>
TELEGRAM_CHAT_ID=<YOUR_CHAT_ID>
ADMIN_API_KEY=<GENERATE_SECURE_KEY>
DEBUG=true
DATA_MODE=demo
```

**SECURITY WARNING:** Never commit actual credentials. All token values must be set in Render dashboard, not in code.
See `SECURITY_INCIDENT.md` for credential rotation instructions.

---

## Support Resources

### Documentation
- Frontend: https://babylon-gold.vercel.app
- Backend API: https://babylon-gold-backend.onrender.com/docs (Swagger UI)
- GitHub: https://github.com/babylon-gold/babylon-gold

### Dashboards
- Render: https://dashboard.render.com
- Vercel: https://vercel.com/dashboard
- GitHub: https://github.com/babylon-gold/babylon-gold

### Emergency Contacts
- Developer: Claude (via GitHub Issues)
- Owner: thairaljaabi1980@gmail.com

---

## Next Steps

### Phase 5 Enhancements (Optional)
- [ ] Live XAU/USD data feed
- [ ] User authentication
- [ ] Portfolio tracking
- [ ] Advanced backtesting
- [ ] Mobile app
- [ ] Email notifications
- [ ] Discord integration
- [ ] Admin dashboard

### Maintenance Tasks
- [ ] Monitor error logs weekly
- [ ] Review Telegram notification history
- [ ] Update dependencies monthly
- [ ] Performance monitoring
- [ ] Security updates

---

## Quick Links

| Resource | URL |
|----------|-----|
| Frontend | https://babylon-gold.vercel.app |
| Backend API | https://babylon-gold-backend.onrender.com/api/v1 |
| Telegram Bot | @thairaljaabibot |
| GitHub Repo | https://github.com/babylon-gold/babylon-gold |
| Render Dashboard | https://dashboard.render.com |
| Vercel Dashboard | https://vercel.com/dashboard |

---

## Questions?

For issues, suggestions, or feature requests:
1. Check GitHub Issues: https://github.com/babylon-gold/babylon-gold/issues
2. Create new issue with details
3. Email: thairaljaabi1980@gmail.com

---

**Last Updated:** 2026-10-23  
**Version:** 1.0.0  
**Status:** ✅ PRODUCTION LIVE
