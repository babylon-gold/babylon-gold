# Babylon AI Gold Intelligence - Cloud Deployment Guide

Complete guide for deploying the Babylon AI platform to production cloud environments.

## 📋 Table of Contents

1. [Overview](#overview)
2. [Local Docker Testing](#local-docker-testing)
3. [Frontend Deployment (Vercel)](#frontend-deployment-vercel)
4. [Backend Deployment (Railway)](#backend-deployment-railway)
5. [Alternative: Docker + Kubernetes](#alternative-docker--kubernetes)
6. [Environment Variables](#environment-variables)
7. [Monitoring & Logs](#monitoring--logs)
8. [CI/CD Pipeline](#cicd-pipeline)
9. [Troubleshooting](#troubleshooting)

---

## Overview

The Babylon AI Gold Intelligence platform consists of:

- **Frontend**: Next.js 16 (React 19) - TypeScript
- **Backend**: FastAPI - Python 3.11
- **Data**: OHLC candles, Technical indicators, Trading signals

### Recommended Architecture

```
┌─────────────────────────────────────┐
│          Users (Browser)            │
└────────────────┬────────────────────┘
                 │
         ┌───────▼────────┐
         │  Vercel CDN    │
         │  (Frontend)    │
         └───────┬────────┘
                 │
         ┌───────▼────────┐
         │  Railway       │
         │  (Backend)     │
         └────────────────┘
```

---

## Local Docker Testing

Test the complete stack locally before deploying to cloud.

### Prerequisites

```bash
# Install Docker and Docker Compose
# macOS/Windows: Download Docker Desktop
# Linux: sudo apt-get install docker.io docker-compose
```

### Build and Run

```bash
# Clone repository
git clone https://github.com/yourname/babylon-gold.git
cd babylon-gold

# Create .env file
cp .env.example .env

# Edit .env with your settings
nano .env

# Build and start containers
docker-compose up --build

# Backend will be available at: http://localhost:8000
# Frontend will be available at: http://localhost:3000
```

### Verify Services

```bash
# Check backend health
curl http://localhost:8000/health

# Check frontend
curl http://localhost:3000

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Stop services
docker-compose down
```

---

## Frontend Deployment (Vercel)

Deploy Next.js frontend to Vercel (recommended for Next.js projects).

### Step 1: Prepare Repository

```bash
# Initialize git if not already done
git init
git add .
git commit -m "Initial commit: Babylon AI Gold Intelligence platform"

# Push to GitHub
git remote add origin https://github.com/yourname/babylon-gold.git
git push -u origin main
```

### Step 2: Connect to Vercel

1. Go to [vercel.com](https://vercel.com)
2. Sign in with GitHub account
3. Click "Add New Project"
4. Select your repository
5. Configure project settings:
   - **Framework**: Next.js
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `.next`

### Step 3: Environment Variables

In Vercel dashboard, add environment variables:

```
NEXT_PUBLIC_API_URL=https://api.babylongold.com/api/v1
```

### Step 4: Deploy

```bash
# Deploy directly from CLI
npm install -g vercel
cd frontend
vercel --prod
```

### Verify Deployment

```bash
# Your frontend will be at: https://babylon-gold.vercel.app
# Custom domain: Configure in Vercel dashboard > Settings > Domains
```

---

## Backend Deployment (Railway)

Deploy FastAPI backend to Railway.

### Step 1: Create Railway Account

1. Go to [railway.app](https://railway.app)
2. Sign in with GitHub
3. Click "New Project"
4. Select "Deploy from GitHub repo"

### Step 2: Connect Repository

1. Select your GitHub repository
2. Choose deployment source: `Dockerfile.backend`
3. Configure environment:

```
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
DATABASE_URL=optional_postgres_url
ENVIRONMENT=production
```

### Step 3: Configure Services

- **Port**: 8000
- **Health Check**: `/health`
- **Restart Policy**: Always

### Step 4: Deploy

```bash
# Deploy via Railway CLI
npm install -g @railway/cli
railway link  # Link to your Railway project
railway up    # Deploy
```

### Step 4: Get API URL

```bash
# After deployment, Railway will provide a URL like:
# https://babylon-gold-api-production.railway.app

# Use this in frontend environment variables:
NEXT_PUBLIC_API_URL=https://babylon-gold-api-production.railway.app/api/v1
```

---

## Alternative: Docker + Kubernetes

For advanced users who need more control and scalability.

### Prerequisites

```bash
# Install kubectl
# Install cloud CLI:
# - GCP: gcloud CLI
# - AWS: aws CLI
# - Azure: az CLI
```

### Google Cloud Run (Simple)

```bash
# Build images
docker build -f Dockerfile.backend -t gcr.io/YOUR_PROJECT/babylon-backend .
docker build -f Dockerfile.frontend -t gcr.io/YOUR_PROJECT/babylon-frontend .

# Push to Google Container Registry
docker push gcr.io/YOUR_PROJECT/babylon-backend
docker push gcr.io/YOUR_PROJECT/babylon-frontend

# Deploy backend to Cloud Run
gcloud run deploy babylon-backend \
  --image gcr.io/YOUR_PROJECT/babylon-backend \
  --platform managed \
  --region us-central1 \
  --set-env-vars TELEGRAM_BOT_TOKEN=xxx

# Deploy frontend to Cloud Run
gcloud run deploy babylon-frontend \
  --image gcr.io/YOUR_PROJECT/babylon-frontend \
  --platform managed \
  --region us-central1 \
  --set-env-vars NEXT_PUBLIC_API_URL=https://babylon-backend-url.run.app
```

### AWS ECS + ECR

```bash
# Create ECR repositories
aws ecr create-repository --repository-name babylon-backend
aws ecr create-repository --repository-name babylon-frontend

# Build and push images
docker build -f Dockerfile.backend -t 123456789.dkr.ecr.us-east-1.amazonaws.com/babylon-backend .
docker push 123456789.dkr.ecr.us-east-1.amazonaws.com/babylon-backend

# Deploy via ECS/Fargate (configure in AWS console)
```

---

## Environment Variables

### Backend (.env)

```env
# Telegram Configuration
TELEGRAM_BOT_TOKEN=your_bot_token_from_botfather
TELEGRAM_CHAT_ID=your_chat_id

# Optional Database
DATABASE_URL=postgresql://user:password@host:5432/babylon_gold

# Environment
ENVIRONMENT=production
DEBUG=false

# CORS
ALLOWED_ORIGINS=https://babylon-gold.vercel.app,https://babylongold.com

# API
API_TITLE=Babylon AI Gold Intelligence
API_VERSION=1.0.0
```

### Frontend (.env.local)

```env
NEXT_PUBLIC_API_URL=https://api.babylongold.com/api/v1
NEXT_PUBLIC_APP_NAME=Babylon AI
NEXT_PUBLIC_APP_VERSION=1.0.0
```

---

## Monitoring & Logs

### Vercel Monitoring

```bash
# View logs in Vercel dashboard
# Dashboard > Deployments > Logs
# Real-time logs via CLI:
vercel logs --follow
```

### Railway Monitoring

```bash
# View logs in Railway dashboard
# Project > Services > Logs

# Or via CLI:
railway logs -f

# Monitor metrics:
# Project > Services > Metrics (CPU, Memory, Network)
```

### Application Monitoring

```bash
# Optional: Set up Sentry for error tracking
# Install Sentry SDK in both frontend and backend
# Configure Sentry DSN in environment variables
```

---

## CI/CD Pipeline

The `.github/workflows/ci-cd.yml` file provides automated:

1. **Testing**: Backend (pytest) and Frontend (npm build)
2. **Building**: Docker image builds
3. **Pushing**: Images to container registry
4. **Deploying**: To staging (develop branch) and production (main branch)

### Setup GitHub Secrets

In GitHub repository settings > Secrets and variables > Actions:

```
VERCEL_TOKEN        # Get from Vercel > Settings > Tokens
VERCEL_ORG_ID       # Your Vercel organization ID
VERCEL_PROJECT_ID   # Your Vercel project ID

RAILWAY_TOKEN_STAGING      # Railway staging token
RAILWAY_TOKEN_PRODUCTION   # Railway production token

GITHUB_TOKEN        # Automatically provided
```

### Trigger Deployment

```bash
# Push to develop branch for staging
git push origin develop

# Push to main branch for production
git push origin main

# Monitor CI/CD progress in GitHub > Actions
```

---

## Troubleshooting

### Frontend Issues

```bash
# Build fails
npm run build

# Check environment variables
echo $NEXT_PUBLIC_API_URL

# Clear cache
rm -rf .next
npm run build

# Test locally
npm run dev
```

### Backend Issues

```bash
# Check health endpoint
curl -X GET http://localhost:8000/health

# View detailed logs
docker logs babylon-backend

# Verify environment variables
env | grep TELEGRAM

# Test database connection
python -c "import psycopg2; psycopg2.connect('...')"
```

### Network Issues

```bash
# Check backend is accessible from frontend
curl https://api.babylongold.com/health

# Check CORS headers
curl -H "Origin: https://babylon-gold.vercel.app" \
     -H "Access-Control-Request-Method: GET" \
     -v https://api.babylongold.com/api/v1/dashboard
```

### Docker Issues

```bash
# Rebuild images without cache
docker-compose build --no-cache

# Check image size
docker images | grep babylon

# Prune unused images
docker image prune -a

# Check container resource usage
docker stats
```

---

## Custom Domain Setup

### For Frontend (Vercel)

1. Go to Vercel Dashboard > Settings > Domains
2. Add your domain (e.g., babylon-gold.com)
3. Update DNS records with Vercel's nameservers
4. SSL certificate automatically provisioned

### For Backend (Railway)

1. Railway Dashboard > Services > babylon-backend > Settings
2. Add custom domain
3. Update DNS with CNAME record
4. SSL certificate automatically provisioned

### Example DNS Configuration

```
# For babylon-gold.com (Frontend on Vercel)
babylon-gold.com    A       76.76.19.89  # Vercel IP

# For api.babylon-gold.com (Backend on Railway)
api               CNAME    babylon-backend-prod.railway.app
```

---

## Maintenance & Updates

```bash
# View deployment history
vercel list  # Frontend
railway status  # Backend

# Rollback to previous deployment
vercel rollback  # Frontend

# Update environment variables
# Vercel: Dashboard > Settings > Environment Variables
# Railway: Dashboard > Services > Settings > Variables

# Monitor uptime
# Use services like: UptimeRobot, Pingdom, or cloud provider monitoring
```

---

## Production Checklist

- [ ] Environment variables configured
- [ ] Database backups enabled
- [ ] Monitoring and alerting set up
- [ ] Custom domain configured
- [ ] SSL certificate active
- [ ] CORS properly configured
- [ ] Rate limiting enabled
- [ ] Telegram bot token secured
- [ ] API documentation deployed
- [ ] Health checks passing
- [ ] CI/CD pipeline working
- [ ] Rollback procedure tested

---

## Support

For deployment issues:

1. Check logs in Vercel/Railway dashboard
2. Review error messages in CI/CD pipeline
3. Test locally with `docker-compose up`
4. Verify environment variables
5. Check GitHub Actions workflow status

---

**Last Updated**: 2026-10-21
**Version**: 1.0.0
