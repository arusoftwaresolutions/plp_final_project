import os
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
import traceback
import socket

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text, select
from sqlalchemy.engine.url import make_url
from dotenv import load_dotenv

# Load environment variables (only in development)
_ENV = os.getenv("ENVIRONMENT", "production").lower()
if _ENV in ("dev", "development", "local"):
    load_dotenv(override=True)

# Import app modules
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

# -------------------- Lifespan for startup --------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("[Startup] Environment variables:", flush=True)
    for key, value in sorted(os.environ.items()):
        if any(k in key.lower() for k in ['db', 'postgres', 'database', 'railway']):
            print(f"  {key}: {value}", flush=True)

    try:
        db_url = settings.DATABASE
        print(f"[Startup] Using database URL: {db_url}", flush=True)
        parsed = make_url(db_url)
        db_host = parsed.host
        db_port = parsed.port or 5432

        # Validate port
        try:
            db_port = int(db_port)
        except (ValueError, TypeError):
            print(f"[Startup] WARNING: Invalid DB port '{parsed.port}', using 5432")
            db_port = 5432

        # Test DNS
        try:
            socket.getaddrinfo(db_host, db_port)
            print(f"[Startup] DNS resolution OK for {db_host}:{db_port}", flush=True)
        except Exception as e:
            print(f"[Startup] WARNING: DNS resolution failed: {e}", flush=True)

        # Test DB connection and create tables
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT version()"))
            print(f"[Startup] Database version: {result.scalar()}", flush=True)
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("[Startup] Database tables ensured.", flush=True)

        # Seed admin and sample data
        async with AsyncSessionLocal() as db:
            # Admin role
            result = await db.execute(select(Role).where(Role.name == "admin"))
            admin_role = result.scalar_one_or_none()
            if not admin_role:
                admin_role = Role(name="admin", description="Administrator")
                db.add(admin_role)
                await db.flush()

            # Admin user
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

            # Assign role
            if not admin_user.roles:
                admin_user.roles = []
            if admin_role not in admin_user.roles:
                admin_user.roles.append(admin_role)
            await db.commit()
            print("[Startup] Admin user & role ensured.", flush=True)

    except Exception as e:
        print(f"[Startup] Initialization error: {e}", flush=True)
        traceback.print_exc()

    yield

# -------------------- App --------------------
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Poverty Alleviation Platform API",
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
    allow_origin_regex=r'https?://(?:[a-z0-9-]+\.)?yourdomain\.com',
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files
if os.path.isdir("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

# -------------------- Health endpoints --------------------
@app.get("/health", include_in_schema=False)
async def health_check():
    response = {"status": "ok"}
    try:
        db_url = settings.DATABASE
        parsed = make_url(db_url)
        host = parsed.host
        port = parsed.port or 5432
        try:
            socket.getaddrinfo(host, int(port))
            dns_ok = True
        except Exception as e:
            dns_ok = False
            response["dns_error"] = str(e)

        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
        response.update({"database": "connected", "db_host": host, "db_port": int(port), "dns_ok": dns_ok})
    except Exception as e:
        response["database"] = f"disconnected: {e}"
    return response

@app.get("/live", include_in_schema=False)
async def liveness_probe():
    return {"status": "alive"}

@app.get("/ready", include_in_schema=False)
async def readiness_probe():
    response = {"status": "ready", "database": "unknown"}
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
            response["database"] = "connected"
    except Exception as e:
        response["database"] = f"disconnected: {e}"
    return response

# -------------------- Include API --------------------
try:
    from app.api.api_v1.api import api_router
    app.include_router(api_router, prefix=settings.API_V1_STR)
except Exception as e:
    print(f"[Startup] Routers not loaded yet: {e}")
    traceback.print_exc()

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

# -------------------- Main --------------------
if __name__ == "__main__":
    import uvicorn
    port_env = os.getenv("PORT")
    try:
        port = int(port_env)
    except (TypeError, ValueError):
        port = 8000
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        reload_dirs=["app"],
        log_level="info"
    )
