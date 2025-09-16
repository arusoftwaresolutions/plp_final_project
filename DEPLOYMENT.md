# Deployment Guide: Poverty Alleviation Platform

This guide provides step-by-step instructions for deploying the Poverty Alleviation Platform to Railway.

## Prerequisites

1. A Railway account (https://railway.app/)
2. GitHub account (for repository connection)
3. Docker installed locally (for testing)
4. Railway CLI (optional, for advanced deployment)

## Deployment Steps

### 1. Prepare Your Repository

1. Ensure all your code is committed and pushed to your GitHub repository
2. Update the `.env.production` file with your production environment variables
3. Update the `API_BASE_URL` in the frontend to point to your production backend

### 2. Deploy to Railway

#### Option A: Using Railway Dashboard (Recommended)

1. Go to [Railway Dashboard](https://railway.app/dashboard)
2. Click "New Project" and select "Deploy from GitHub repo"
3. Connect your GitHub account and select your repository
4. Configure the following settings:
   - **Build Command:** `pip install -r backend/requirements.txt && cd frontend && npm install && npm run build`
   - **Start Command:** `uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT`
   - **Environment Variables:** Import from `.env.production` or set them manually in the Railway dashboard
5. Click "Deploy"

#### Option B: Using Railway CLI

1. Install Railway CLI:
   ```bash
   npm i -g @railway/cli
   ```

2. Login to Railway:
   ```bash
   railway login
   ```

3. Link your project:
   ```bash
   railway init
   ```

4. Set environment variables:
   ```bash
   railway env push .env.production
   ```

5. Deploy your application:
   ```bash
   railway up
   ```

### 3. Configure Database

1. In the Railway dashboard, go to your project
2. Click "New" and select "Database"
3. Choose PostgreSQL and create the database
4. Update your `DATABASE_URL` environment variable with the new database connection string
5. Run database migrations:
   ```bash
   # Connect to your Railway environment
   railway run -- python -m alembic upgrade head
   ```

### 4. Configure Custom Domain (Optional)

1. In the Railway dashboard, go to your project
2. Click on the "Settings" tab
3. Under "Domains", click "Generate Domain"
4. To use a custom domain:
   - Click "Add Custom Domain"
   - Follow the instructions to update your DNS settings

### 5. Set Up SSL (Automatic with Railway)

Railway automatically provisions SSL certificates for your domains through Let's Encrypt. No additional configuration is needed.

### 6. Verify Deployment

1. Once deployed, visit your application URL
2. Test all major functionality:
   - User registration and login
   - Dashboard loading
   - Form submissions
   - API endpoints
3. Check logs in the Railway dashboard for any errors

## Environment Variables

Make sure to set the following required environment variables in your Railway dashboard:

```
# Application
DEBUG=False
ENVIRONMENT=production

# Database
DATABASE_URL=postgresql://user:password@host:port/dbname

# Authentication
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Frontend
FRONTEND_URL=https://your-frontend-url.com

# CORS
CORS_ORIGINS=https://your-frontend-url.com
```

## Scaling

Railway automatically scales your application based on traffic. You can manually adjust resources in the Railway dashboard under the "Resources" tab.

## Monitoring

Railway provides built-in monitoring:
- View logs in real-time
- Monitor resource usage
- Set up alerts for errors or high resource usage

## Backups

For the database:
1. Go to your database in Railway
2. Click on the "Backups" tab
3. Configure automatic backups
4. Set up a retention policy

## Troubleshooting

### Common Issues

1. **Application Not Starting**
   - Check logs in Railway dashboard
   - Verify all environment variables are set
   - Ensure the build process completes successfully

2. **Database Connection Issues**
   - Verify `DATABASE_URL` is correct
   - Check if the database is running and accessible
   - Ensure migrations have been applied

3. **CORS Errors**
   - Verify `CORS_ORIGINS` includes your frontend URL
   - Check if the backend is properly configured to handle CORS

### Accessing Logs

1. In Railway dashboard, go to your project
2. Click on the "Logs" tab
3. View real-time logs and filter by service

## Maintenance

### Updating the Application

1. Push changes to your repository
2. Railway will automatically detect changes and redeploy
3. Monitor the deployment in the Railway dashboard

### Database Migrations

To run migrations:

```bash
railway run -- python -m alembic upgrade head
```

## Support

For additional help:
- Check the [Railway Documentation](https://docs.railway.app/)
- Join the [Railway Discord](https://discord.gg/railway)
- Contact Railway support through the dashboard
