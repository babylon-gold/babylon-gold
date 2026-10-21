# Quick Start: Deploy Babylon AI to Cloud

Fast-track deployment guide for getting the Babylon AI platform live in minutes.

## 🚀 5-Minute Deployment (Local Testing First)

### Step 1: Test Locally (2 minutes)

```bash
# Clone and prepare
git clone https://github.com/yourname/babylon-gold.git
cd babylon-gold

# Copy environment template
cp .env.example .env

# Start services
docker-compose up --build

# Verify
# Frontend: http://localhost:3000 ✓
# Backend: http://localhost:8000 ✓
```

## 🌐 Deploy Frontend to Vercel (3 minutes)

### Quick Deploy

```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
cd frontend
vercel --prod

# Get your URL (e.g., babylon-gold.vercel.app)
```

## 🔧 Deploy Backend to Railway (3 minutes)

### Quick Deploy

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and setup
railway login
railway init

# Deploy
railway up

# Get your API URL
```

## 🔗 Connect Frontend to Backend

### Update Frontend Environment

In Vercel Dashboard:
1. Settings > Environment Variables
2. Add `NEXT_PUBLIC_API_URL` = `https://your-railway-backend-url/api/v1`
3. Redeploy

## ✅ Verify Production

```bash
# Test frontend
curl https://your-vercel-app.vercel.app

# Test backend
curl https://your-railway-backend.railway.app/health

# Test API connection
curl https://your-railway-backend.railway.app/api/v1/admin/system/health-detailed
```

## 📊 Monitor Production

### Vercel Monitoring
- Dashboard: https://vercel.com/dashboard
- Logs: `vercel logs --follow`
- Metrics: View in dashboard

### Railway Monitoring
- Dashboard: https://railway.app
- Logs: `railway logs -f`
- Metrics: View in service dashboard

---

## 🐛 Troubleshooting Quick Reference

### Frontend Not Loading
```bash
# Check environment
vercel env list

# Redeploy
vercel --prod --force

# Check logs
vercel logs --follow
```

### Backend Health Check Failing
```bash
# Check logs
railway logs -f

# Check environment variables
railway variables list

# Restart service
railway status
```

### API Connection Failing
```bash
# Test API directly
curl https://your-backend-url/health -v

# Check CORS headers
curl -H "Origin: https://your-frontend.vercel.app" \
     https://your-backend-url/api/v1/health -v

# Verify API URL in frontend environment
echo $NEXT_PUBLIC_API_URL
```

---

## 📋 Required Secrets

### Before First Deploy

```env
# Backend Secrets (Railway)
TELEGRAM_BOT_TOKEN=your_token_here
TELEGRAM_CHAT_ID=your_chat_id_here

# Frontend Secrets (Vercel)
NEXT_PUBLIC_API_URL=https://your-backend-url/api/v1

# GitHub Secrets (for CI/CD)
VERCEL_TOKEN=xxx
VERCEL_ORG_ID=xxx
VERCEL_PROJECT_ID=xxx
RAILWAY_TOKEN_PRODUCTION=xxx
```

---

## 🎯 Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| Build fails | `npm run build` locally to debug |
| Frontend can't reach API | Update `NEXT_PUBLIC_API_URL` in Vercel |
| CORS errors | Check backend `ALLOWED_ORIGINS` |
| Telegram not working | Verify `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` |
| Database connection fails | Check `DATABASE_URL` format |
| Timeouts | Increase timeout in backend health check |

---

## 🔐 Security Checklist

Before going live:

- [ ] No secrets in code
- [ ] Environment variables secured
- [ ] SSL/TLS enabled (automatic)
- [ ] CORS properly configured
- [ ] Rate limiting enabled
- [ ] Input validation added
- [ ] Error messages sanitized
- [ ] Logs don't expose secrets

---

## 📈 Performance Optimization

### Frontend (Vercel)
- Automatic code splitting (Next.js)
- Image optimization enabled
- CDN edge caching
- ISR (Incremental Static Regeneration)

### Backend (Railway)
- Uvicorn with multiple workers
- Connection pooling
- Response compression
- Request caching headers

---

## 🔄 CI/CD Automation

Once deployed, automatic deployments trigger on:

```
develop branch → Staging (Railway)
main branch → Production (Vercel + Railway)
```

Monitor at: https://github.com/yourname/babylon-gold/actions

---

## 📞 Support

| Task | Command |
|------|---------|
| View logs | `vercel logs` / `railway logs` |
| Redeploy | `vercel --prod` / `railway up` |
| Check health | `curl https://api.babylongold.com/health` |
| Check status | Dashboard URLs above |

---

## 🎉 Success Indicators

✅ Production is live when:
- Frontend loads without errors
- Dashboard displays data
- Charts render properly
- Signals update in real-time
- Notifications working (if configured)
- Admin panel accessible
- API responses < 500ms

---

**Estimated Total Time**: 10-15 minutes
**Estimated Cost**: $0-10/month (free tiers available)

Ready to deploy? Let's go! 🚀
