import os
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import traceback
from sqlalchemy import text, select
from sqlalchemy.engine.url import make_url
import socket

# Load environment variables first (only in development)
_ENV = os.getenv("ENVIRONMENT", "production").lower()
if _ENV in ("dev", "development", "local"):
    load_dotenv(override=True)

# Then import local modules
try:
    from app.core.config import settings
    from app.db.session import engine, Base, AsyncSessionLocal
    from app.core.security import get_current_user, get_password_hash
    from app.db.models import (
        User,
        Role,
        Transaction,
        TransactionType,
        TransactionCategory,
        MicroLoan,
        LoanRepayment,
        CrowdFundingCampaign,
        Donation,
        PovertyArea,
        Notification,
        NotificationType,
    )
except ImportError as e:
    import sys
    print(f"Import error: {e}")
    print(f"Python path: {sys.path}")
    raise

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Print all environment variables for debugging
    print("[Startup] Environment variables:", flush=True)
    for key, value in sorted(os.environ.items()):
        if any(k in key.lower() for k in ['db', 'postgres', 'database', 'railway']):
            print(f"  {key}: {value}", flush=True)
    
    # Always ensure tables exist and seed an admin user on startup
    try:
        # Print DATABASE diagnostics
        try:
            db_url = settings.DATABASE
            print(f"[Startup] Using database URL: {db_url}", flush=True)
            
            parsed = make_url(db_url)
            db_host = parsed.host
            db_port = parsed.port or 5432
            
            print(f"[Startup] Database configuration:", flush=True)
            print(f"  Driver: {parsed.drivername}", flush=True)
            print(f"  Host: {db_host}", flush=True)
            print(f"  Port: {db_port}", flush=True)
            print(f"  Database: {parsed.database}", flush=True)
            print(f"  Username: {parsed.username}", flush=True)
            
            # Test DNS resolution
            try:
                socket.getaddrinfo(db_host, db_port)
                print("[Startup] DNS: Host resolves successfully", flush=True)
            except Exception as dns_e:
                print(f"[Startup] WARNING: DNS resolution failed for host '{db_host}': {dns_e}", flush=True)

            # Test database connection
            print("[Startup] Testing database connection...", flush=True)
            try:
                async with engine.connect() as conn:
                    result = await conn.execute(text("SELECT version()"))
                    version = result.scalar()
                    print(f"[Startup] Database version: {version}", flush=True)
                
                print("[Startup] Creating database tables (if not exist)...", flush=True)
                async with engine.begin() as conn:
                    await conn.run_sync(Base.metadata.create_all)
                print("[Startup] Tables are ready.", flush=True)
                
            except Exception as db_error:
                print(f"[Startup] ERROR: Database connection failed: {db_error}", flush=True)
                print("[Startup] This is likely due to incorrect database configuration.", flush=True)
                print("[Startup] Please check your DATABASE_URL or individual database environment variables.", flush=True)
                raise
        except Exception as e:
            print(f"[Startup] Error during database initialization: {e}", flush=True)
            raise

        # Seed admin role and user
        async with AsyncSessionLocal() as db:
            # Ensure 'admin' role exists
            result = await db.execute(select(Role).where(Role.name == "admin"))
            admin_role = result.scalar_one_or_none()
            if admin_role is None:
                admin_role = Role(name="admin", description="Administrator")
                db.add(admin_role)
                await db.flush()

            # Ensure initial admin user exists
            result = await db.execute(select(User).where(User.email == settings.FIRST_SUPERUSER_EMAIL))
            admin_user = result.scalar_one_or_none()
            if admin_user is None:
                admin_user = User(
                    username=settings.FIRST_SUPERUSER,
                    email=settings.FIRST_SUPERUSER_EMAIL,
                    hashed_password=get_password_hash(settings.FIRST_SUPERUSER_PASSWORD),
                    is_active=True,
                    is_verified=True,
                )
                db.add(admin_user)
                await db.flush()

            # Ensure admin user has admin role
            if admin_role not in (admin_user.roles or []):
                # Initialize roles list if None
                if not admin_user.roles:
                    admin_user.roles = []
                admin_user.roles.append(admin_role)

            await db.commit()
            print("[Startup] Admin user and role are ensured.", flush=True)

            # Seed core roles
            print("[Startup] Ensuring core roles and sample data...", flush=True)
            sample_roles = [
                ("user", "Standard user"),
                ("donor", "Donor user"),
            ]
            existing_roles = {r.name for r in (await db.execute(select(Role))).scalars().all()}
            for name, desc in sample_roles:
                if name not in existing_roles:
                    db.add(Role(name=name, description=desc))
            await db.flush()

            roles_map = {r.name: r for r in (await db.execute(select(Role))).scalars().all()}

            # Seed sample users if they don't exist
            default_pwd = "SamplePass123!"
            sample_users = [
                {"username": "john", "email": "john@example.com", "roles": ["user"]},
                {"username": "sara", "email": "sara@example.com", "roles": ["user"]},
                {"username": "dana", "email": "dana.donor@example.com", "roles": ["donor"]},
                {"username": "peter",  "email": "peter.donor@example.com",  "roles": ["donor"]},
            ]

            created_users = {}
            for u in sample_users:
                result = await db.execute(select(User).where(User.email == u["email"]))
                user_obj = result.scalar_one_or_none()
                if user_obj is None:
                    user_obj = User(
                        username=u["username"],
                        email=u["email"],
                        hashed_password=get_password_hash(default_pwd),
                        is_active=True,
                        is_verified=True,
                    )
                    db.add(user_obj)
                    await db.flush()
                # attach roles
                if not user_obj.roles:
                    user_obj.roles = []
                for rn in u["roles"]:
                    role_obj = roles_map.get(rn)
                    if role_obj and role_obj not in user_obj.roles:
                        user_obj.roles.append(role_obj)
                created_users[u["username"]] = user_obj

            await db.flush()

            # Seed a demo crowdfunding campaign if none exists
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
                    created_by=created_users.get("john", admin_user).id if 'admin_user' in locals() else created_users.get("john").id,
                )
                db.add(demo_campaign)
                await db.flush()

                # Donations from donors
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

            # Seed a poverty area if none exists
            result = await db.execute(select(PovertyArea))
            if result.scalars().first() is None:
                db.add(PovertyArea(
                    name="Kora Community",
                    description="Community with limited access to basic services.",
                    location={"lat": 8.98, "lng": 38.79, "address": "Kora"},
                    poverty_rate=42.5,
                    population=12000,
                    needs=["clean_water", "education", "healthcare"],
                ))
                await db.flush()

            # Seed transactions for john and sara if none exist
            result = await db.execute(select(Transaction))
            if result.scalars().first() is None:
                for username in ["john", "sara"]:
                    user = created_users.get(username)
                    if user:
                        db.add_all([
                            Transaction(
                                user_id=user.id,
                                amount=1500.0,
                                transaction_type=TransactionType.INCOME,
                                category=TransactionCategory.SALARY,
                                description="Monthly salary",
                            ),
                            Transaction(
                                user_id=user.id,
                                amount=-200.0,
                                transaction_type=TransactionType.EXPENSE,
                                category=TransactionCategory.FOOD,
                                description="Groceries",
                            ),
                        ])
                await db.flush()

            # Seed a microloan for john if none exists
            result = await db.execute(select(MicroLoan))
            if result.scalars().first() is None and created_users.get("john"):
                db.add(MicroLoan(
                    user_id=created_users["john"].id,
                    amount=1000.0,
                    purpose="Start small poultry business",
                ))
                await db.flush()

            # Seed basic notifications if none exist
            result = await db.execute(select(Notification))
            if result.scalars().first() is None:
                # Notify donors about the campaign
                for uname in ("dana", "peter"):
                    u = created_users.get(uname)
                    if u:
                        db.add(Notification(
                            user_id=u.id,
                            notification_type=NotificationType.NEW_CAMPAIGN,
                            message="A new campaign 'Clean Water for Village X' has launched!",
                        ))
                # Notify john about loan status (demo message)
                if created_users.get("john"):
                    db.add(Notification(
                        user_id=created_users["john"].id,
                        notification_type=NotificationType.NEW_LOAN,
                        message="Your microloan application has been received.",
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
print(f"[Startup] Configuring CORS with origins: {settings.BACKEND_CORS_ORIGINS}", flush=True)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
    allow_origin_regex=r'https?://(?:[a-z0-9-]+\.)?yourdomain\.com',  # Add your domain pattern here
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files only if directory exists to avoid startup crash
if os.path.isdir("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

# Health check endpoints (must be defined before CORS middleware)
@app.get("/health", include_in_schema=False)
async def health_check():
    """Simple health check endpoint that always returns 200 when the app is running."""
    response = {"status": "ok"}
    # Check database connection
    try:
        db_url = settings.DATABASE
        parsed = make_url(db_url)
        host = parsed.host
        port = parsed.port or 5432
        dns_ok = True
        dns_error = None
        try:
            socket.getaddrinfo(host, port)
        except Exception as e:
            dns_ok = False
            dns_error = str(e)

        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
        response["database"] = "connected"
        response["db_host"] = host
        response["db_port"] = port
        response["dns_ok"] = dns_ok
        if not dns_ok:
            response["dns_error"] = dns_error
    except Exception as e:
        try:
            db_url = settings.DATABASE
            parsed = make_url(db_url)
            host = parsed.host
            port = parsed.port or 5432
            response["db_host"] = host
            response["db_port"] = port
            try:
                socket.getaddrinfo(host, port)
                response["dns_ok"] = True
            except Exception as de:
                response["dns_ok"] = False
                response["dns_error"] = str(de)
        except Exception:
            pass
        response["database"] = f"disconnected: {str(e)}"
    
    return response

# Liveness probe endpoint
@app.get("/live", include_in_schema=False)
async def liveness_probe():
    """Liveness probe for Kubernetes/container orchestration."""
    return {"status": "alive"}

# Readiness probe endpoint with optional database check
@app.get("/ready", include_in_schema=False)
async def readiness_probe():
    """Readiness probe that checks if the application is ready to receive traffic."""
    response = {
        "status": "ready",
        "database": "unknown"
    }
    
    # Optional: Check database connection
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
            response["database"] = "connected"
    except Exception as e:
        response["database"] = f"disconnected: {str(e)}"
    
    return response

# Include API router after health checks, but do not fail startup if routers have issues
try:
    from app.api.api_v1.api import api_router  # defer import to avoid slowing initial import
    app.include_router(api_router, prefix=settings.API_V1_STR)
except Exception as e:
    print(f"[Startup] Routers not loaded yet: {e}")
    traceback.print_exc()

# Root endpoint with API information
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
