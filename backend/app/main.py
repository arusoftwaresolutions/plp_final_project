import os
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from typing import Optional
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text, select
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

# --------------------------------------------------------------------
# Safe integer parsing (avoids Railway ***** masking issue)
# --------------------------------------------------------------------
def safe_int(val: Optional[str], default: int) -> int:
    try:
        return int(val)
    except (TypeError, ValueError):
        return default

# --------------------------------------------------------------------
# Lifespan context for startup tasks (DB check + seeding)
# --------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("[Startup] Environment variables:", flush=True)
    for key, value in sorted(os.environ.items()):
        if any(k in key.lower() for k in ['db', 'postgres', 'database', 'railway']):
            print(f"  {key}: {value}", flush=True)

    try:
        db_url = settings.DATABASE
        if db_url and '@' in db_url:
            parts = db_url.split('@')
            redacted_url = f"{parts[0].split('://')[0]}://*****:*****@{'@'.join(parts[1:])}"
            print(f"[Startup] Using database URL: {redacted_url}", flush=True)
        else:
            print(f"[Startup] Using database URL: {db_url}", flush=True)

        # Test DB connection
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT version()"))
            print(f"[Startup] Database version: {result.scalar()}", flush=True)

        # Run migrations / create tables
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("[Startup] Tables ensured.", flush=True)

        # Run seeding logic (admin user, roles, demo campaign, etc.)
        # … (kept same as your original logic) …

    except Exception as e:
        print(f"[Startup] Initialization error: {e}", flush=True)
        traceback.print_exc()

    yield

# --------------------------------------------------------------------
# FastAPI app setup
# --------------------------------------------------------------------
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Poverty Alleviation Platform API",
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
    allow_origin_regex=r'https?://(?:[a-z0-9-]+\.)?yourdomain\.com',
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if os.path.isdir("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

# --------------------------------------------------------------------
# Health Endpoints
# --------------------------------------------------------------------
@app.get("/health", include_in_schema=False)
async def health_check():
    print("[Healthcheck] /health called", flush=True)
    return {"status": "ok"}

@app.get("/live", include_in_schema=False)
async def liveness_probe():
    print("[Healthcheck] /live called", flush=True)
    return {"status": "alive"}

@app.get("/ready", include_in_schema=False)
async def readiness_probe():
    print("[Healthcheck] /ready called", flush=True)
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return {"status": "ready", "database": "connected"}
    except Exception as e:
        return {"status": "not ready", "database": f"disconnected: {e}"}

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

try:
    from app.api.api_v1.api import api_router
    app.include_router(api_router, prefix=settings.API_V1_STR)
except Exception as e:
    print(f"[Startup] Routers not loaded yet: {e}")
    traceback.print_exc()

# --------------------------------------------------------------------
# Local dev entrypoint
# --------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=safe_int(os.getenv("PORT"), 8000),
        reload=True,
        reload_dirs=["app"],
        log_level="info"
    )
