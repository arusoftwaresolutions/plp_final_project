# 🚀 Deployment Guide - Financial Platform

## Option 1: Railway (Recommended - Easiest)

### Step 1: Prepare Your Repository
1. Push your code to GitHub:
```bash
git init
git add .
git commit -m "Initial commit - Financial Platform"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/financial-platform.git
git push -u origin main
```

### Step 2: Deploy Backend to Railway
1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your repository
5. Choose "Deploy Now"

### Step 3: Add PostgreSQL Database
1. In your Railway project, click "New" → "Database" → "PostgreSQL"
2. Wait for database to be created
3. Copy the database URL from the "Connect" tab

### Step 4: Configure Environment Variables
In your Railway backend service, go to "Variables" tab and add:
```
DATABASE_URL=postgresql://postgres:password@host:port/railway
SECRET_KEY=your-super-secret-key-here
STRIPE_PUBLIC_KEY=your-stripe-public-key
STRIPE_SECRET_KEY=your-stripe-secret-key
```

### Step 5: Deploy Frontend to Railway
1. Create a new service in Railway
2. Connect to the same GitHub repo
3. Set the root directory to `frontend`
4. Add environment variable:
```
BACKEND_URL=https://your-backend-url.railway.app
```

### Step 6: Run Database Migrations
1. Go to your backend service in Railway
2. Click "Deployments" → "View Logs"
3. In the terminal, run:
```bash
alembic upgrade head
python seed_data.py
```

---

## Option 2: Render (Free Tier)

### Step 1: Prepare for Render
Create these files in your project root:

**render.yaml**:
```yaml
services:
  - type: web
    name: financial-platform-backend
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: DATABASE_URL
        fromDatabase:
          name: financial-platform-db
          property: connectionString
      - key: SECRET_KEY
        generateValue: true
      - key: STRIPE_PUBLIC_KEY
        sync: false
      - key: STRIPE_SECRET_KEY
        sync: false

  - type: web
    name: financial-platform-frontend
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: streamlit run app.py --server.port $PORT --server.address 0.0.0.0
    envVars:
      - key: BACKEND_URL
        fromService:
          type: web
          name: financial-platform-backend
          property: host

databases:
  - name: financial-platform-db
    databaseName: financial_platform
    user: financial_platform_user
```

### Step 2: Deploy to Render
1. Go to [render.com](https://render.com)
2. Sign up with GitHub
3. Click "New" → "Blueprint"
4. Connect your GitHub repository
5. Select the `render.yaml` file
6. Click "Apply"

---

## Option 3: DigitalOcean App Platform

### Step 1: Create App Spec
Create `.do/app.yaml`:
```yaml
name: financial-platform
services:
- name: backend
  source_dir: backend
  github:
    repo: YOUR_USERNAME/financial-platform
    branch: main
  run_command: uvicorn main:app --host 0.0.0.0 --port $PORT
  environment_slug: python
  instance_count: 1
  instance_size_slug: basic-xxs
  envs:
  - key: DATABASE_URL
    scope: RUN_TIME
    type: SECRET
  - key: SECRET_KEY
    scope: RUN_TIME
    type: SECRET
  - key: STRIPE_PUBLIC_KEY
    scope: RUN_TIME
    type: SECRET
  - key: STRIPE_SECRET_KEY
    scope: RUN_TIME
    type: SECRET

- name: frontend
  source_dir: frontend
  github:
    repo: YOUR_USERNAME/financial-platform
    branch: main
  run_command: streamlit run app.py --server.port $PORT --server.address 0.0.0.0
  environment_slug: python
  instance_count: 1
  instance_size_slug: basic-xxs
  envs:
  - key: BACKEND_URL
    scope: RUN_TIME
    value: ${backend.PUBLIC_URL}

databases:
- name: financial-platform-db
  engine: PG
  version: "13"
  size: db-s-dev-database
```

### Step 2: Deploy
1. Go to [DigitalOcean App Platform](https://cloud.digitalocean.com/apps)
2. Click "Create App"
3. Connect GitHub repository
4. Select "App Spec" and choose your `.do/app.yaml`
5. Deploy

---

## Option 4: Vercel + Supabase (Serverless)

### Step 1: Deploy Backend to Vercel
1. Install Vercel CLI: `npm i -g vercel`
2. In your project root: `vercel`
3. Follow the prompts

### Step 2: Set up Supabase Database
1. Go to [supabase.com](https://supabase.com)
2. Create new project
3. Get database URL from Settings → Database
4. Add to Vercel environment variables

### Step 3: Deploy Frontend to Vercel
1. Create `vercel.json`:
```json
{
  "builds": [
    {
      "src": "frontend/app.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "frontend/app.py"
    }
  ]
}
```

---

## 🔧 Post-Deployment Steps

### 1. Database Setup
After deployment, run these commands in your backend service:
```bash
# Run migrations
alembic upgrade head

# Seed demo data
python seed_data.py
```

### 2. Test Your Deployment
1. Visit your frontend URL
2. Register a new account
3. Test the features:
   - Family dashboard
   - Add transactions
   - View AI recommendations
   - Browse campaigns (as donor)
   - Apply for loans (as business)

### 3. Configure Custom Domain (Optional)
1. In your platform's dashboard, add a custom domain
2. Update DNS records as instructed
3. Enable SSL certificate

---

## 🆓 Free Tier Limits

### Railway
- $5 credit monthly
- 500 hours of usage
- 1GB RAM, 1 vCPU

### Render
- 750 hours/month
- Sleeps after 15min inactivity
- 512MB RAM

### DigitalOcean
- $100 credit for new users
- Basic tier: $5/month after credit

### Vercel + Supabase
- Vercel: 100GB bandwidth/month
- Supabase: 500MB database, 2GB bandwidth

---

## 🎯 Recommended Deployment Strategy

**For Demo/Portfolio**: Use **Render** (completely free, easy setup)
**For Production**: Use **Railway** (reliable, good performance)
**For Learning**: Use **DigitalOcean** (professional features, $100 credit)

---

## 🚨 Important Notes

1. **Environment Variables**: Always set `SECRET_KEY` to a secure random string
2. **Database**: Use the provided database URL from your platform
3. **CORS**: The backend is configured to allow all origins (change for production)
4. **SSL**: Most platforms provide SSL automatically
5. **Monitoring**: Check logs regularly for any issues

---

## 🔍 Troubleshooting

### Common Issues:
1. **Database Connection**: Check `DATABASE_URL` format
2. **CORS Errors**: Verify `BACKEND_URL` in frontend
3. **Port Issues**: Use `$PORT` environment variable
4. **Build Failures**: Check Python version compatibility

### Getting Help:
- Check platform-specific documentation
- Review application logs
- Test locally first with `docker-compose up`

---

**🎉 Your Financial Platform is now live and ready to help families, donors, and businesses!**
