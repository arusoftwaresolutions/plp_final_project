"""
Main application module for the Poverty Alleviation Platform.
This module contains the FastAPI application and database initialization code.
"""
import os
import sys
from pathlib import Path
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from typing import Optional
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import select
import traceback
from dotenv import load_dotenv

# Add the project root to the Python path
sys.path.append(str(Path(__file__).parent.parent.parent))

# Load environment variables in development
_ENV = os.getenv("ENVIRONMENT", "production").lower()
if _ENV in ("dev", "development", "local"):
    load_dotenv(override=True)

# Local imports
from backend.app.core.config import settings
from backend.app.db.session import engine, Base, AsyncSessionLocal
from backend.app.core.security import get_password_hash
from backend.app.api.api_v1.api import api_router

# Import models to register them with SQLAlchemy
from backend.app.db.models import *  # noqa

# Safe int parser to handle masked values and other edge cases
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

async def init_db():
    """Initialize the database with sample data."""
    try:
        async with AsyncSessionLocal() as db:
            # Check if we already have data
            result = await db.execute(select(Role).limit(1))
            if result.scalars().first() is not None:
                return  # Database already initialized

            # Create roles
            admin_role = Role(name="admin", description="Administrator with full access")
            user_role = Role(name="user", description="Regular user")
            donor_role = Role(name="donor", description="Donor user")
            
            db.add_all([admin_role, user_role, donor_role])
            await db.flush()

            # Create admin user
            admin_user = User(
                username=settings.FIRST_SUPERUSER,
                email=settings.FIRST_SUPERUSER_EMAIL,
                hashed_password=get_password_hash(settings.FIRST_SUPERUSER_PASSWORD),
                is_active=True,
                is_verified=True,
                roles=[admin_role]
            )
            db.add(admin_user)
            await db.flush()
            
            # Create sample users
            sample_users = [
                {"username": "john", "email": "john@example.com", "roles": [user_role]},
                {"username": "sara", "email": "sara@example.com", "roles": [user_role]},
                {"username": "dana", "email": "dana@example.com", "roles": [donor_role]},
                {"username": "peter", "email": "peter@example.com", "roles": [donor_role]},
            ]
            
            created_users = {}
            default_pwd = "SamplePass123!"
            
            for user_data in sample_users:
                user = User(
                    username=user_data["username"],
                    email=user_data["email"],
                    hashed_password=get_password_hash(default_pwd),
                    is_active=True,
                    is_verified=True,
                    roles=user_data["roles"]
                )
                db.add(user)
                created_users[user_data["username"]] = user
            
            await db.flush()
            
            # Create sample campaign if none exists
            result = await db.execute(select(CrowdFundingCampaign).limit(1))
            if not result.scalars().first():
                campaign = CrowdFundingCampaign(
                    title="Clean Water for Village X",
                    description="Help us provide clean water to Village X by building a new well.",
                    target_amount=10000.0,
                    amount_raised=0.0,
                    end_date=datetime.utcnow() + timedelta(days=30),
                    status="active",
                    location={"lat": 9.03, "lng": 38.74, "address": "Village X"},
                    created_by=created_users["john"].id
                )
                db.add(campaign)
                await db.flush()
                
                # Add sample donations
                donations = [
                    {"donor": "dana", "amount": 250.0, "message": "Happy to help!"},
                    {"donor": "peter", "amount": 500.0, "message": "Great cause!"}
                ]
                
                for donation_data in donations:
                    donor = created_users[donation_data["donor"]]
                    donation = Donation(
                        campaign_id=campaign.id,
                        donor_id=donor.id,
                        amount=donation_data["amount"],
                        message=donation_data["message"],
                        is_anonymous=False
                    )
                    db.add(donation)
                    campaign.amount_raised += donation.amount
            
            await db.commit()
            print("[Startup] Database initialized with sample data")
            
    except Exception as e:
        await db.rollback()
        print(f"[Startup] Error initializing database: {e}")
        traceback.print_exc()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle application startup and shutdown events."""
    # Create database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Initialize database with sample data
    await init_db()
    
    yield
    
    # Clean up resources on shutdown
    await engine.dispose()

# Create the FastAPI application with lifespan management
app = FastAPI(
    title="Poverty Alleviation Platform API",
    description="API for the Poverty Alleviation Platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)

# Health check endpoint
@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT
    }

# Root endpoint
@app.get("/", tags=["root"])
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Welcome to the Poverty Alleviation Platform API",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT,
        "docs": "/docs",
        "redoc": "/redoc"
    }

# Exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )

# This allows running with `python -m backend.app.main` for local development
if __name__ == "__main__":
    import uvicorn
    
    # Get the port from environment variable with fallback
    port = int(os.getenv("PORT", 8000))
    
    uvicorn.run(
        "backend.app.main:app",
        host="0.0.0.0",
        port=port,
        reload=settings.ENVIRONMENT != "production"
    )
