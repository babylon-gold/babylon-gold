# Health Check & Monitoring Setup

Guide for setting up health checks and monitoring for the Babylon AI platform.

## 📊 Health Check Endpoints

### Backend Health Endpoint

The backend provides a health check endpoint:

```
GET /health
```

**Response (200 OK)**:
```json
{
  "status": "healthy",
  "timestamp": "2026-10-21T14:30:00Z",
  "service": "Babylon AI Backend",
  "version": "1.0.0"
}
```

### Detailed Health Endpoint

```
GET /api/v1/admin/system/health-detailed
```

**Response**:
```json
{
  "status": "healthy",
  "data": {
    "is_loaded": true,
    "data_type": "historical",
    "data_age_hours": 1.8,
    "candle_counts": {
      "5min": 25920,
      "15min": 33867,
      "1h": 20826,
      "4h": 8545
    }
  },
  "refresh": {
    "status": "completed_successfully",
    "last_refresh": "2026-10-21T02:00:00Z",
    "duration_seconds": 45.3,
    "error_count": 0
  },
  "scheduler": {
    "running": true,
    "jobs": [
      {
        "id": "daily_refresh",
        "name": "Daily Data Refresh",
        "next_run_time": "2026-10-22T02:00:00Z"
      }
    ]
  }
}
```

---

## 🔍 Monitoring Setup

### 1. Vercel (Frontend Monitoring)

#### Built-in Monitoring
- **Analytics**: View in Vercel Dashboard > Analytics
- **Logs**: `vercel logs --follow`
- **Performance**: Automatic lighthouse audits
- **Deployment Status**: Automatic deployment tracking

#### Configure Alerts
```bash
# Vercel CLI - Setup project alerts
vercel env add VERCEL_ANALYTICS_ID your_key
```

### 2. Railway (Backend Monitoring)

#### Built-in Monitoring
- **Metrics**: CPU, Memory, Network in dashboard
- **Logs**: Automatic log aggregation
- **Health Checks**: Automatic every 30 seconds
- **Metrics Logs**: View in service > Metrics

#### Configure Health Check in Railway
```yaml
# railway.json
{
  "services": {
    "backend": {
      "healthCheck": {
        "path": "/health",
        "interval": 30,
        "timeout": 10,
        "successThreshold": 1,
        "failureThreshold": 3
      }
    }
  }
}
```

### 3. Uptime Monitoring (UptimeRobot)

#### Setup Monitoring

1. Go to [uptimerobot.com](https://uptimerobot.com)
2. Sign up (free tier available)
3. Add monitors:

**Frontend Monitor**
- Type: HTTPS
- URL: `https://babylon-gold.vercel.app`
- Check interval: Every 5 minutes
- Alert: On down > 1 minute

**Backend Monitor**
- Type: HTTPS
- URL: `https://api.babylongold.com/health`
- Check interval: Every 5 minutes
- Alert: On down > 1 minute

#### Webhook Alerts (Optional)
```bash
# Configure webhook for Slack notifications
POST https://hooks.slack.com/services/YOUR/WEBHOOK/URL
{
  "text": "Babylon AI Backend is DOWN",
  "channel": "#alerts"
}
```

### 4. Error Tracking (Sentry)

#### Setup Sentry

1. Go to [sentry.io](https://sentry.io)
2. Sign up and create project
3. Create separate projects for frontend and backend

#### Backend Configuration

```python
# backend/main.py
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn="https://xxxxx@xxxxx.ingest.sentry.io/xxxxx",
    integrations=[FastApiIntegration()],
    traces_sample_rate=0.1,
    environment="production"
)
```

#### Frontend Configuration

```typescript
// frontend/next.config.js
module.exports = {
  experimental: {
    instrumentationHook: true,
  },
  ...
}

// frontend/instrumentation.ts
import * as Sentry from "@sentry/nextjs";

export function register() {
  if (process.env.NEXT_RUNTIME === "nodejs") {
    Sentry.init({
      dsn: process.env.SENTRY_DSN,
      environment: process.env.ENVIRONMENT,
    });
  }
}
```

---

## 📈 Monitoring Dashboard

### Key Metrics to Track

1. **Availability**
   - Uptime percentage (target: 99.9%)
   - Error rate < 0.1%
   - Health check status

2. **Performance**
   - API response time (target: < 200ms)
   - Frontend load time (target: < 2s)
   - Database query time (target: < 100ms)

3. **Business**
   - Daily active users
   - Signals generated
   - API request volume
   - Notification sent count

4. **Infrastructure**
   - CPU usage (target: < 70%)
   - Memory usage (target: < 80%)
   - Disk usage (target: < 80%)
   - Network bandwidth

### Example Dashboard Queries

**Vercel Analytics**
```
Dashboard > Analytics > Web Vitals
- First Contentful Paint (FCP)
- Largest Contentful Paint (LCP)
- Cumulative Layout Shift (CLS)
```

**Railway Metrics**
```
Service > Metrics
- CPU Usage %
- Memory Usage %
- Network I/O
- Request Duration
```

---

## 🚨 Alert Configuration

### Recommended Alerts

| Condition | Threshold | Action |
|-----------|-----------|--------|
| Frontend down | 1 min | Slack notification + SMS |
| Backend down | 1 min | Slack notification + SMS + Page |
| API latency high | > 500ms | Slack notification |
| Error rate high | > 1% | Slack notification |
| CPU high | > 80% | Slack notification |
| Memory high | > 85% | Slack notification |
| Disk full | > 90% | Slack notification + Email |

### Slack Integration

**Vercel**
1. Go to Vercel Dashboard > Settings > Integrations
2. Add Slack
3. Configure channels for alerts

**Railway**
1. Go to Railway Dashboard > Team Settings > Integrations
2. Add Slack webhook
3. Configure notifications

**UptimeRobot**
1. Create alert contact (Slack)
2. Assign to monitors
3. Configure notification rules

---

## 🔧 Manual Health Checks

### Quick Health Check Script

```bash
#!/bin/bash
# health_check.sh

echo "🏥 Babylon AI Health Check"
echo "=========================="

# Frontend
echo "📱 Frontend: $(curl -s -o /dev/null -w "%{http_code}" https://babylon-gold.vercel.app)"

# Backend
BACKEND_STATUS=$(curl -s https://api.babylongold.com/health | jq '.status')
echo "🔧 Backend: $BACKEND_STATUS"

# Detailed Health
echo "📊 Detailed Health:"
curl -s https://api.babylongold.com/api/v1/admin/system/health-detailed | jq '.'
```

### Run Periodic Checks

```bash
# Run health check every hour
0 * * * * /path/to/health_check.sh >> /var/log/babylon_health.log
```

---

## 📋 Monitoring Checklist

- [ ] Vercel monitoring enabled
- [ ] Railway monitoring active
- [ ] UptimeRobot monitors created
- [ ] Sentry integration complete
- [ ] Slack webhooks configured
- [ ] SMS alerts configured
- [ ] Email alerts configured
- [ ] Dashboard created
- [ ] Custom alerts configured
- [ ] On-call schedule established
- [ ] Escalation contacts documented
- [ ] Health check tests passing

---

## 🎯 Success Criteria

✅ Monitoring is working when:

1. **Availability**
   - Frontend responds < 2s
   - Backend responds < 200ms
   - Health check succeeds consistently

2. **Alerts**
   - Slack notifications working
   - SMS alerts triggered on outage
   - Email summaries sent daily

3. **Data**
   - Metrics visible in dashboards
   - Error tracking capturing issues
   - Performance data logged

4. **Response**
   - Team notified of issues
   - On-call responds quickly
   - Escalation procedures working

---

## 📞 Monitoring Support

| Issue | Resource |
|-------|----------|
| Vercel logs | `vercel logs` or Dashboard |
| Railway logs | `railway logs` or Dashboard |
| UptimeRobot | uptime.com dashboard |
| Sentry errors | sentry.io dashboard |
| Slack alerts | #alerts channel |

---

**Last Updated**: 2026-10-21
**Monitoring Status**: ✅ Active
