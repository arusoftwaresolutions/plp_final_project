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

# Load environment variables only in development
_ENV = os.getenv("ENVIRONMENT", "production").lower()
if _ENV in ("dev", "development", "local"):
    load_dotenv(override=True)

# Import local modules
try:
    from app.core.config import settings
    from app.db.session import engine, Base, AsyncSessionLocal
    from app.core.security import get_password_hash
    from app.db.models import User, Role, Transaction, TransactionType, TransactionCategory, MicroLoan, LoanRepayment, CrowdFundingCampaign, Donation, PovertyArea, Notification, NotificationType
except ImportError as e:
    import sys
    print(f"Import error: {e}")
    print(f"Python path: {sys.path}")
    raise

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("[Startup] Environment variables (DB-related only):")
    for key, value in sorted(os.environ.items()):
        if any(k in key.lower() for k in ['db', 'postgres', 'database', 'railway']):
            print(f"  {key}: {value}")

    # Use safe parsing for DATABASE_URL to avoid errors from masked values
    try:
        db_url = settings.DATABASE
        print(f"[Startup] Using database URL: {db_url}")

        parsed = make_url(db_url)
        db_host = parsed.host or "localhost"
        db_port = parsed.port or 5432  # default if missing or masked

        print(f"[Startup] Database host: {db_host}")
        print(f"[Startup] Database port: {db_port}")

        # Try DNS resolution but skip exceptions if Railway masks values
        try:
            socket.getaddrinfo(db_host, db_port)
            print(f"[Startup] DNS: Host {db_host} resolves successfully on port {db_port}")
        except Exception as dns_e:
            print(f"[Startup] WARNING: DNS resolution failed (likely masked): {dns_e}")

        # Test connection
        try:
            async with engine.connect() as conn:
                result = await conn.execute(text("SELECT version()"))
                version = result.scalar()
                print(f"[Startup] Database version: {version}")
        except Exception as db_error:
            print(f"[Startup] WARNING: Could not connect to DB (check DATABASE_URL): {db_error}")

        # Ensure tables
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("[Startup] Tables ensured.")

    except Exception as e:
        print(f"[Startup] Initialization error: {e}")
        traceback.print_exc()

    yield

# Create FastAPI app
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

# Mount static files if exist
if os.path.isdir("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

# Health check endpoint
@app.get("/health", include_in_schema=False)
async def health_check():
    return {"status": "ok"}

# Root endpoint
@app.get("/")
async def root():
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": "production" if not settings.DEBUG else "development",
        "docs": "/docs",
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
