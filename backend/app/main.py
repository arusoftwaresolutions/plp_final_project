import os
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from typing import Optional
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text, select
from sqlalchemy.engine.url import make_url
import socket
import traceback
from dotenv import load_dotenv

# Load environment variables in development
_ENV = os.getenv("ENVIRONMENT", "production").lower()
if _ENV in ("dev", "development", "local"):
    load_dotenv(override=True)

# Local imports
try:
    from app.core.config import settings
    from app.db.session import engine, Base, AsyncSessionLocal
    from app.core.security import get_password_hash
    from app.db.models import (
        User, Role, Transaction, TransactionType, TransactionCategory,
        MicroLoan, CrowdFundingCampaign, Donation, PovertyArea,
        Notification, NotificationType
    )
except ImportError as e:
    import sys
    print(f"Import error: {e}")
    print(f"Python path: {sys.path}")
    raise

# Safe int parser to avoid Railway ***** issues
def safe_int(val: Optional[str], default: int) -> int:
    try:
        return int(val)
    except (TypeError, ValueError):
        return default

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("[Startup] Environment variables:", flush=True)
    for key, value in sorted(os.environ.items()):
        if any(k in key.lower() for k in ['db', 'postgres', 'database', 'railway']):
            print(f"  {key}: {value}", flush=True)

    try:
        # Get the database URL from settings (already handles Railway's environment variables)
        db_url = settings.DATABASE
        
        # Print a redacted version of the URL for security
        if db_url and '@' in db_url:
            # Redact password in logs
            parts = db_url.split('@')
            redacted_url = f"{parts[0].split('://')[0]}://*****:*****@{'@'.join(parts[1:])}"
            print(f"[Startup] Using database URL: {redacted_url}", flush=True)
        else:
            print(f"[Startup] Using database URL: {db_url}", flush=True)

        # Skip DNS resolution and direct connection test since the engine will handle this
        print("[Startup] Database configuration loaded successfully", flush=True)

        # Test database connection with retry logic
        max_retries = 3
        retry_delay = 2  # seconds
        
        for attempt in range(max_retries):
            try:
                print(f"[Startup] Testing database connection (attempt {attempt + 1}/{max_retries})...", flush=True)
                async with engine.connect() as conn:
                    result = await conn.execute(text("SELECT version()"))
                    version = result.scalar()
                    print(f"[Startup] Successfully connected to database. Version: {version}", flush=True)
                    break  # Connection successful, exit retry loop
            except Exception as db_error:
                if attempt == max_retries - 1:  # Last attempt
                    print(f"[Startup] ERROR: Failed to connect to database after {max_retries} attempts", flush=True)
                    print(f"[Startup] Connection error: {str(db_error)}", flush=True)
                    print("[Startup] Please check your database configuration and ensure the database is accessible", flush=True)
                    raise
                print(f"[Startup] WARNING: Database connection attempt {attempt + 1} failed: {db_error}", flush=True)
                import time
                time.sleep(retry_delay)
        
        # Create tables
        try:
            print("[Startup] Creating database tables if not exist...", flush=True)
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            print("[Startup] Tables are ready.", flush=True)
        except Exception as e:
            print(f"[Startup] WARNING: Error creating tables: {e}", flush=True)
            print("[Startup] Continuing startup...", flush=True)

        # Seed admin role and user
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(Role).where(Role.name == "admin"))
            admin_role = result.scalar_one_or_none()
            if not admin_role:
                admin_role = Role(name="admin", description="Administrator")
                db.add(admin_role)
                await db.flush()

            result = await db.execute(select(User).where(User.email == settings.FIRST_SUPERUSER_EMAIL))
            admin_user = result.scalar_one_or_none()
            if not admin_user:
                admin_user = User(
                    username=settings.FIRST_SUPERUSER,
                    email=settings.FIRST_SUPERUSER_EMAIL,
                    hashed_password=get_password_hash(settings.FIRST_SUPERUSER_PASSWORD),
                    is_active=True,
                    is_verified=True,
                )
                db.add(admin_user)
                await db.flush()

            if admin_role not in (admin_user.roles or []):
                if not admin_user.roles:
                    admin_user.roles = []
                admin_user.roles.append(admin_role)

            await db.commit()
            print("[Startup] Admin user and role are ensured.", flush=True)

            # Seed core roles and sample data
            print("[Startup] Ensuring core roles and sample data...", flush=True)
            sample_roles = [("user", "Standard user"), ("donor", "Donor user")]
            existing_roles = {r.name for r in (await db.execute(select(Role))).scalars().all()}
            for name, desc in sample_roles:
                if name not in existing_roles:
                    db.add(Role(name=name, description=desc))
            await db.flush()

            roles_map = {r.name: r for r in (await db.execute(select(Role))).scalars().all()}

            # Sample users
            default_pwd = "SamplePass123!"
            sample_users = [
                {"username": "john", "email": "john@example.com", "roles": ["user"]},
                {"username": "sara", "email": "sara@example.com", "roles": ["user"]},
                {"username": "dana", "email": "dana.donor@example.com", "roles": ["donor"]},
                {"username": "peter", "email": "peter.donor@example.com", "roles": ["donor"]},
            ]

            created_users = {}
            for u in sample_users:
                result = await db.execute(select(User).where(User.email == u["email"]))
                user_obj = result.scalar_one_or_none()
                if not user_obj:
                    user_obj = User(
                        username=u["username"],
                        email=u["email"],
                        hashed_password=get_password_hash(default_pwd),
                        is_active=True,
                        is_verified=True,
                    )
                    db.add(user_obj)
                    await db.flush()
                if not user_obj.roles:
                    user_obj.roles = []
                for rn in u["roles"]:
                    role_obj = roles_map.get(rn)
                    if role_obj and role_obj not in user_obj.roles:
                        user_obj.roles.append(role_obj)
                created_users[u["username"]] = user_obj
            await db.flush()

            # Demo crowdfunding campaign
            result = await db.execute(select(CrowdFundingCampaign))
            if result.scalars().first() is None:
                demo_campaign = CrowdFundingCampaign(
                    title="Clean Water for Village X",
                    description="Provide clean water access by building a well and filtration system.",
                    target_amount=5000.0,
                    amount_raised=0.0,
                    end_date=datetime.utcnow() + timedelta(days=30),
                    status="active",
                    location={"lat": 9.03, "lng": 38.74, "address": "Village X"},
                    created_by=created_users.get("john").id
                )
                db.add(demo_campaign)
                await db.flush()
                for donor_username, amount in [("dana", 100.0), ("peter", 250.0)]:
                    donor_user = created_users.get(donor_username)
                    if donor_user:
                        db.add(Donation(
                            campaign_id=demo_campaign.id,
                            donor_id=donor_user.id,
                            amount=amount,
                            message=f"Support from {donor_username}",
                            is_anonymous=False,
                        ))
                await db.flush()

            await db.commit()
            print("[Startup] Sample data ensured.", flush=True)

    except Exception as e:
        print(f"[Startup] Initialization error: {e}", flush=True)
        traceback.print_exc()

    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Poverty Alleviation Platform API",
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
    allow_origin_regex=r'https?://(?:[a-z0-9-]+\.)?yourdomain\.com',
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
if os.path.isdir("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

# Health, liveness, readiness endpoints
@app.get("/health", include_in_schema=False)
async def health_check():
    return {"status": "ok"}

@app.get("/live", include_in_schema=False)
async def liveness_probe():
    return {"status": "alive"}

@app.get("/ready", include_in_schema=False)
async def readiness_probe():
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return {"status": "ready", "database": "connected"}
    except Exception as e:
        return {"status": "ready", "database": f"disconnected: {e}"}

# Root endpoint
@app.get("/")
async def root():
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": "production" if not settings.DEBUG else "development",
        "docs": "/docs",
        "redoc": "/redoc",
        "api_v1": "/api/v1"
    }

# Include API router
try:
    from app.api.api_v1.api import api_router
    app.include_router(api_router, prefix=settings.API_V1_STR)
except Exception as e:
    print(f"[Startup] Routers not loaded yet: {e}")
    traceback.print_exc()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8000")),
        reload=True,
        reload_dirs=["app"],
        log_level="info"
    )
