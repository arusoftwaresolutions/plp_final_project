# 🚀 Railway Deployment Guide

## Quick Deploy Steps:

### 1. Push to GitHub
```bash
git init
git add .
git commit -m "Financial Platform - Railway Ready"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/financial-platform.git
git push -u origin main
```

### 2. Deploy Backend
1. Go to [railway.app](https://railway.app)
2. Click "New Project" → "Deploy from GitHub repo"
3. Select your repository
4. **IMPORTANT**: Leave **Root Directory** empty (it will use the root Dockerfile)
5. Click "Deploy Now"

### 3. Add PostgreSQL Database
1. In your project, click "New" → "Database" → "PostgreSQL"
2. Wait for database to be created
3. Copy the **DATABASE_URL** from the "Connect" tab

### 4. Configure Backend Environment Variables
In your backend service, go to "Variables" tab and add:
```
DATABASE_URL=postgresql://postgres:password@host:port/railway
SECRET_KEY=your-super-secret-key-here-change-this
STRIPE_PUBLIC_KEY=pk_test_your_stripe_public_key
STRIPE_SECRET_KEY=sk_test_your_stripe_secret_key
```

### 5. Deploy Frontend
1. Click "New" → "GitHub Repo"
2. Select same repository
3. Set **Root Directory** to `frontend`
4. Add environment variable:
```
BACKEND_URL=https://your-backend-url.railway.app
```

### 6. Initialize Database
1. Go to backend service → "Deployments" → "View Logs"
2. Run these commands:
```bash
alembic upgrade head
python seed_data.py
```

## ✅ Your Financial Platform is Live!

- **Frontend**: https://your-frontend-url.railway.app
- **Backend API**: https://your-backend-url.railway.app
- **API Docs**: https://your-backend-url.railway.app/docs

## 🔧 Management
- **View Logs**: Click on service → "Deployments" → "View Logs"
- **Redeploy**: Click "Redeploy" button
- **Environment Variables**: Service → "Variables" tab

