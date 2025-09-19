from typing import Optional
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.core.config import settings

# Import and include API router after app creation to avoid circular imports
from backend.app.api.api_v1.api import api_router
from backend.app.db.session import engine, Base, AsyncSessionLocal

import traceback

# ======================
# Safe int parser
# ======================
def safe_int(val: Optional[str], default: int) -> int:
    """Safely convert a string to an integer, handling various edge cases."""
    if val is None:
        return default
    if isinstance(val, str) and '*****' in val:  # Handle masked values
        print(f"[WARNING] Attempted to convert masked value to int: {val}")
        return default
    try:
        return int(val)
    except (ValueError, TypeError):
        return default


# ======================
# Database seeding
# ======================
async def init_db():
    """Initialize the database with sample data."""
    from datetime import datetime, timedelta
    import json
    from sqlalchemy import select
    from backend.app.db.models import (
        Role, User, Transaction, TransactionType, TransactionCategory,
        MicroLoan, LoanStatus, LoanRepayment, CrowdFundingCampaign,
        Donation, PovertyArea, Notification, NotificationType,
    )
    from passlib.context import CryptContext

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    try:
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(Role).limit(1))
            if result.scalars().first() is not None:
                print("ℹ️ Database already initialized, skipping seeding")
                return

            print("🚀 Creating sample data...")

            # Roles
            admin_role = Role(name="admin", description="Administrator with full access")
            user_role = Role(name="user", description="Regular user")
            donor_role = Role(name="donor", description="Donor user")
            db.add_all([admin_role, user_role, donor_role])
            await db.commit()

            # Users
            admin_user = User(
                username="admin",
                email="admin@example.com",
                hashed_password=pwd_context.hash("admin123"),
                full_name="Admin User",
                is_verified=True,
                is_active=True,
            )
            admin_user.roles = [admin_role, user_role, donor_role]

            db.add(admin_user)
            await db.commit()

            print("✅ Sample data created successfully!")

    except Exception as e:
        print(f"[Startup] Error initializing database: {e}")
        traceback.print_exc()


# ======================
# Lifespan
# ======================
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Seed DB
    await init_db()

    yield

    await engine.dispose()


# ======================
# FastAPI Application (SINGLE definition with lifespan)
# ======================
app = FastAPI(
    title="Poverty Alleviation Platform API",
    description="API for the Poverty Alleviation Platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,  # ✅ ensures seeding runs
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for now, can be restricted later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Welcome to the Poverty Alleviation Platform API",
        "documentation": {"swagger": "/docs", "redoc": "/redoc"},
        "status": "operational",
        "version": "1.0.0",
    }


# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "ok", "version": "1.0.0", "environment": settings.ENVIRONMENT}


# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)


# Local run
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)
