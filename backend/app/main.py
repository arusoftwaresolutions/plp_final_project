import os
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
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

# Import local modules
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

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("[Startup] Environment variables:", flush=True)
    for key, value in sorted(os.environ.items()):
        if any(k in key.lower() for k in ['db', 'postgres', 'database', 'railway']):
            print(f"  {key}: {value}", flush=True)

    try:
        db_url = os.environ.get("DATABASE_URL") or settings.DATABASE
        print(f"[Startup] Using DATABASE_URL: {db_url}", flush=True)

        # Test DNS resolution
        parsed = make_url(db_url)
        db_host = parsed.host
        db_port = parsed.port or 5432
        try:
            socket.getaddrinfo(db_host, db_port)
            print(f"[Startup] DNS: {db_host}:{db_port} resolves successfully", flush=True)
        except Exception as dns_e:
            print(f"[Startup] WARNING: DNS resolution failed: {dns_e}", flush=True)

        # Test database connection and create tables
        print("[Startup] Testing database connection...", flush=True)
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT version()"))
            print(f"[Startup] Database version: {result.scalar()}", flush=True)
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("[Startup] Tables created (if not exist)", flush=True)

        # Seed admin user and roles
        async with AsyncSessionLocal() as db:
            # Ensure 'admin' role exists
            result = await db.execute(select(Role).where(Role.name == "admin"))
            admin_role = result.scalar_one_or_none() or Role(name="admin", description="Administrator")
            if not admin_role.id:
                db.add(admin_role)
                await db.flush()

            # Ensure admin user exists
            result = await db.execute(select(User).where(User.email == settings.FIRST_SUPERUSER_EMAIL))
            admin_user = result.scalar_one_or_none()
            if admin_user is None:
                admin_user = User(
                    username=settings.FIRST_SUPERUSER,
                    email=settings.FIRST_SUPERUSER_EMAIL,
                    hashed_password=get_password_hash(settings.FIRST_SUPERUSER_PASSWORD),
                    is_active=True,
                    is_verified=True,
                    roles=[admin_role]
                )
                db.add(admin_user)
            else:
                if admin_role not in (admin_user.roles or []):
                    if not admin_user.roles:
                        admin_user.roles = []
                    admin_user.roles.append(admin_role)

            await db.commit()
            print("[Startup] Admin user and roles ensured", flush=True)

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
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Mount static files if directory exists
if os.path.isdir("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

# Health check
@app.get("/health", include_in_schema=False)
async def health_check():
    response = {"status": "ok"}
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
        response["database"] = "connected"
    except Exception as e:
        response["database"] = f"disconnected: {str(e)}"
    return response

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
