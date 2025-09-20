import asyncio
import logging
import sys
import traceback
from typing import Optional, Dict, Any, List

from fastapi import FastAPI, Request, status, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from urllib.parse import urlparse
from sqlalchemy import select, text, func
from sqlalchemy.exc import SQLAlchemyError, OperationalError

from backend.app.core.config import settings
from backend.app.db.session import AsyncSessionLocal, engine, wait_for_db
from backend.app.db.models import Base

# Import and include API router
from backend.app.api.api_v1.api import api_router
from backend.app.db.session import engine, AsyncSessionLocal, Base
import traceback

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def create_application() -> FastAPI:
    """
    Create and configure the FastAPI application.
    This function is used to ensure proper initialization order.
    """
    app = FastAPI(
        title="Poverty Alleviation Platform API",
        description="API for the Poverty Alleviation Platform",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        debug=settings.DEBUG
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # In production, replace with specific origins
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    return app

# Create the FastAPI application
app = create_application()

# Add request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Request: {request.method} {request.url}")
    logger.debug(f"Headers: {request.headers}")
    
    try:
        body = await request.body()
        if body:
            logger.debug(f"Request body: {body.decode()}")
    except Exception as e:
        logger.warning(f"Could not log request body: {str(e)}")
    
    response = await call_next(request)
    logger.info(f"Response status: {response.status_code}")
    return response

# Add exception handler for unhandled exceptions
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"},
    )

# Add HTTP exception handler
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    logger.warning(f"HTTP Exception: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

# Add validation exception handler
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.warning(f"Validation error: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors()},
    )

async def check_database_setup() -> bool:
    """Check if the database is properly set up and has an admin user."""
    from backend.app.db.models import User
    
    try:
        async with AsyncSessionLocal() as db:
            # Check if users table exists
            await db.execute(text("SELECT 1 FROM users LIMIT 1"))
            
            # Check if admin user exists
            stmt = select(User).where(User.email == settings.FIRST_SUPERUSER_EMAIL)
            result = await db.execute(stmt)
            admin_user = result.scalar_one_or_none()
            
            return {
                "database_initialized": True,
                "admin_user_exists": admin_user is not None,
                "admin_user_active": admin_user.is_active if admin_user else False
            }
    except Exception as e:
        logger.error(f"Database setup check failed: {e}")
        return {
            "database_initialized": False,
            "admin_user_exists": False,
            "admin_user_active": False,
            "error": str(e)
        }

# Health check endpoint
@app.get("/health")
async def health_check() -> Dict[str, Any]:
    """Health check endpoint for monitoring."""
    try:
        # Check database connection
        async with AsyncSessionLocal() as db:
            await db.execute(text("SELECT 1"))
        
        return {
            "status": "healthy",
            "database": "connected"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service unavailable - database connection failed"
        )

# Root endpoint
@app.get("/")
async def root() -> Dict[str, Any]:
    """Root endpoint with API information."""
    # Check database status
    try:
        db_status = await check_database_setup()
        
        return {
            "message": "Welcome to the Poverty Alleviation Platform API",
            "documentation": {
                "swagger": "/docs",
                "redoc": "/redoc"
            },
            "status": "operational",
            "database": {
                "initialized": db_status["database_initialized"],
                "admin_user_exists": db_status["admin_user_exists"],
                "admin_user_active": db_status["admin_user_active"]
            }
        }
    except Exception as e:
        logger.error(f"Root endpoint error: {e}")
        return {
            "message": "Welcome to the Poverty Alleviation Platform API",
            "status": "degraded",
            "environment": settings.ENVIRONMENT,
            "error": "Unable to check database status",
            "documentation": {
                "swagger": "/docs",
                "redoc": "/redoc"
            }
        }

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)

# Safe int parser
def safe_int(val: Optional[str], default: int) -> int:
    if val is None:
        return default
    if isinstance(val, str) and '*****' in val:  # Handle masked values
        print(f"[WARNING] Attempted to convert masked value to int: {val}")
        return default
    try:
        return int(val)
    except (ValueError, TypeError):
        return default


# Database seeding function
async def init_db():
    """Initialize the database with sample data."""
    from datetime import datetime, timedelta
    import json
    from sqlalchemy import select
    from backend.app.db.models import (
        Role, User, Transaction, TransactionType, TransactionCategory,
        MicroLoan, LoanStatus, LoanRepayment, CrowdFundingCampaign,
        Donation, PovertyArea, Notification, NotificationType,
        UserNotificationPreference
    )
    from passlib.context import CryptContext
    from backend.app.core.security import get_password_hash

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    # Check if database is already fully seeded
    async with AsyncSessionLocal() as db:
        # Check if we have all required data
        roles_exist = (await db.execute(select(func.count()).select_from(Role))).scalar() >= 3
        users_exist = (await db.execute(select(func.count()).select_from(User))).scalar() >= 2
        
        if roles_exist and users_exist:
            logger.info("✅ Database already initialized with sample data")
            return
            
        logger.info("🌱 Database not fully initialized, proceeding with seeding...")
            
    try:
        async with AsyncSessionLocal() as db:
            # Create roles if they don't exist
            roles = {
                "admin": await db.execute(select(Role).filter(Role.name == "admin")),
                "user": await db.execute(select(Role).filter(Role.name == "user")),
                "donor": await db.execute(select(Role).filter(Role.name == "donor"))
            }
            
            if not roles["admin"].scalars().first():
                admin_role = Role(name="admin", description="Administrator with full access")
                db.add(admin_role)
                
            if not roles["user"].scalars().first():
                user_role = Role(name="user", description="Regular user")
                db.add(user_role)
                
            if not roles["donor"].scalars().first():
                donor_role = Role(name="donor", description="Donor user")
                db.add(donor_role)
            
            await db.commit()
            
            # Refresh role objects
            admin_role = (await db.execute(select(Role).filter(Role.name == "admin"))).scalars().first()
            user_role = (await db.execute(select(Role).filter(Role.name == "user"))).scalars().first()
            donor_role = (await db.execute(select(Role).filter(Role.name == "donor"))).scalars().first()
            
            logger.info("✅ Verified/Created roles: admin, user, donor")

            # --- USERS ---
            # Create admin user with properly hashed password
            admin_password = settings.FIRST_SUPERUSER_PASSWORD or "admin123"
            admin_user = User(
                username=settings.FIRST_SUPERUSER or "admin",
                email=settings.FIRST_SUPERUSER_EMAIL or "admin@example.com",
                hashed_password=pwd_context.hash(admin_password),
                full_name="Admin User",
                is_verified=True,
                is_active=True,
                roles=[admin_role, user_role, donor_role]
            )
            logger.info(f"Created admin user with email: {admin_user.email}")
            user1 = User(
                username="john_doe",
                email="john@example.com",
                hashed_password=pwd_context.hash("password123"),
                full_name="John Doe",
                is_verified=True,
                is_active=True,
                roles=[user_role]
            )
            user2 = User(
                username="jane_smith",
                email="jane@example.com",
                hashed_password=pwd_context.hash("password123"),
                full_name="Jane Smith",
                is_verified=True,
                is_active=True,
                roles=[user_role, donor_role]
            )
            # No need to create TransactionCategory instances as they are enums
            # The TransactionCategory enum is already defined in models.py
            # We'll use the enum values directly when creating transactions
            pass
            
            # LoanStatus and NotificationType are enums, no need to create them
            # They are already defined in models.py and can be used directly
            
            # NotificationType is an enum, no need to create it
            # It's already defined in models.py and can be used directly
            
            # Save all users
            db.add_all([admin_user, user1, user2])
            await db.commit()
            
            logger.info("✅ Created sample users and configuration data")

            # --- TRANSACTIONS ---
            today = datetime.utcnow()
            transactions = [
                Transaction(
                    user=admin_user,
                    amount=1500.00,
                    transaction_type=TransactionType.INCOME,
                    category=TransactionCategory.SALARY.value,
                    description="Monthly salary",
                    date=today - timedelta(days=5)
                ),
                Transaction(
                    user=user1,
                    amount=1200.00,
                    transaction_type=TransactionType.INCOME,
                    category=TransactionCategory.SALARY.value,
                    description="Monthly salary",
                    date=today - timedelta(days=10)
                ),
                Transaction(
                    user=user1,
                    amount=150.00,
                    transaction_type=TransactionType.EXPENSE,
                    category=TransactionCategory.FOOD.value,
                    description="Weekly groceries",
                    date=today - timedelta(days=2)
                ),
                Transaction(
                    user=user2,
                    amount=200.00,
                    transaction_type=TransactionType.SAVINGS,
                    category=TransactionCategory.EMERGENCY_FUND.value,
                    description="Monthly savings",
                    date=today - timedelta(days=15)
                )
            ]
            db.add_all(transactions)
            await db.commit()

            # --- MICROLOANS ---
            loan1 = MicroLoan(
                user=user1,
                amount=1000.00,
                purpose="Small business expansion",
                status=LoanStatus.APPROVED,
                interest_rate=0.1,
                term_months=12,
                disbursement_date=today - timedelta(days=30),
                due_date=today + timedelta(days=335)
            )
            loan2 = MicroLoan(
                user=user2,
                amount=2000.00,
                purpose="Education fees",
                status=LoanStatus.PENDING,
                interest_rate=0.08,
                term_months=6
            )
            db.add_all([loan1, loan2])
            await db.commit()

            # --- REPAYMENTS ---
            repayment1 = LoanRepayment(
                loan=loan1,
                amount=100.00,
                payment_date=today - timedelta(days=5),
                status="completed"
            )
            db.add(repayment1)
            await db.commit()

            # --- POVERTY AREAS ---
            poverty_area1 = PovertyArea(
                name="Rural Village A",
                description="A small rural village with limited access to resources",
                location=json.dumps({"latitude": 12.3456, "longitude": 98.7654, "address": "Rural Village A, Country"}),
                poverty_rate=45.5,
                population=1200,
                needs=json.dumps(["clean water", "education", "healthcare"])
            )
            poverty_area2 = PovertyArea(
                name="Urban Slum B",
                description="An urban slum with poor living conditions",
                location=json.dumps({"latitude": 23.4567, "longitude": 87.6543, "address": "Urban Slum B, City"}),
                poverty_rate=65.2,
                population=3500,
                needs=json.dumps(["housing", "sanitation", "employment"])
            )
            db.add_all([poverty_area1, poverty_area2])
            await db.commit()

            # --- CAMPAIGNS ---
            campaign1 = CrowdFundingCampaign(
                title="Clean Water for Rural Village",
                description="Help us provide clean drinking water to 100 families",
                target_amount=10000.00,
                amount_raised=3500.00,
                start_date=today - timedelta(days=30),
                end_date=today + timedelta(days=60),
                status="active",
                image_url="https://example.com/water-campaign.jpg",
                location=json.dumps({"latitude": 12.3456, "longitude": 98.7654, "address": "Rural Village A"}),
                created_by=admin_user.id
            )
            campaign2 = CrowdFundingCampaign(
                title="Education for All",
                description="Support education for children in Urban Slum B",
                target_amount=15000.00,
                amount_raised=5200.00,
                start_date=today - timedelta(days=15),
                end_date=today + timedelta(days=45),
                status="active",
                image_url="https://example.com/education-campaign.jpg",
                location=json.dumps({"latitude": 23.4567, "longitude": 87.6543, "address": "Urban Slum B"}),
                created_by=user2.id
            )
            db.add_all([campaign1, campaign2])
            await db.commit()

            # --- DONATIONS ---
            donation1 = Donation(
                campaign=campaign1,
                donor=user2,
                amount=250.00,
                message="Happy to help with this great cause!",
                is_anonymous=False
            )
            donation2 = Donation(
                campaign=campaign2,
                donor=user1,
                amount=150.00,
                message="Keep up the good work!",
                is_anonymous=True
            )
            db.add_all([donation1, donation2])
            await db.commit()

            # --- NOTIFICATIONS ---
            notification1 = Notification(
                user=user1,
                notification_type=NotificationType.NEW_LOAN,
                message="Your loan application has been approved!",
                read=False
            )
            notification2 = Notification(
                user=user2,
                notification_type=NotificationType.NEW_DONATION,
                message="Thank you for your donation!",
                read=False
            )
            db.add_all([notification1, notification2])
            await db.commit()

            print("✅ Sample data created successfully!")

    except Exception as e:
        print(f"[Startup] Error initializing database: {e}")
        traceback.print_exc()


async def check_database_connection() -> bool:
    """Check if the database is accessible."""
    try:
        async with AsyncSessionLocal() as db:
            await db.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error(f"❌ Database connection error: {e}")
        return False

async def ensure_admin_user() -> bool:
    """
    Initialize the database with sample data.
    """
    from sqlalchemy import select, func
    from sqlalchemy.orm import selectinload
    from backend.app.db.models import User, Role
    from backend.app.core.security import get_password_hash
    
    logger.info("Starting database initialization...")
    
    async with AsyncSessionLocal() as db:
        try:
            # Check if we have the required roles
            required_roles = ["admin", "moderator", "user"]
            roles = {}
            
            # Create roles if they don't exist
            for role_name in required_roles:
                result = await db.execute(
                    select(Role).where(Role.name == role_name)
                )
                role = result.scalars().first()
                
                if not role:
                    description = {
                        "admin": "Administrator with full access",
                        "moderator": "Moderator with limited admin access",
                        "user": "Regular user"
                    }.get(role_name, role_name.capitalize())
                    
                    role = Role(name=role_name, description=description)
                    db.add(role)
                    logger.info(f"Created role: {role_name}")
                
                roles[role_name] = role
            
            await db.commit()
            
            # Check if admin user exists
            admin_email = "admin@example.com"
            result = await db.execute(
                select(User)
                .options(selectinload(User.roles))
                .where(User.email == admin_email)
            )
            admin = result.scalars().first()
            
            if not admin:
                # Create admin user
                admin = User(
                    email=admin_email,
                    username="admin",
                    hashed_password=get_password_hash("admin123"),
                    full_name="Admin User",
                    is_active=True,
                    is_verified=True
                )
                db.add(admin)
                await db.commit()
                await db.refresh(admin)
                logger.info("Created admin user")
            
            # Ensure admin has the admin role
            admin_roles = {role.name for role in admin.roles}
            if "admin" not in admin_roles:
                admin.roles.append(roles["admin"])
                await db.commit()
                logger.info("Assigned admin role to admin user")
            
            # Verify we have at least one admin user
            if not admin.is_active:
                admin.is_active = True
                await db.commit()
                logger.info("Activated admin user")
            
            logger.info("✅ Database initialization completed successfully")
            
        except Exception as e:
            logger.error(f"❌ Database initialization failed: {str(e)}", exc_info=True)
            await db.rollback()
            return False
            
        return True

@app.on_event("startup")
async def on_startup():
    """Initialize application services on startup."""
    logger.info("🚀 Starting application...")
    
    # Log database URL (with redacted password)
    db_url = settings.DATABASE
    parsed = urlparse(db_url)
    if parsed.password:
        redacted_netloc = f"{parsed.username}:*****@{parsed.hostname}"
        if parsed.port:
            redacted_netloc += f":{parsed.port}"
        logger.info(f"🔍 Connecting to database: {parsed.scheme}://{redacted_netloc}{parsed.path}")
    else:
        logger.info(f"🔍 Connecting to database: {db_url}")
    
    # Wait for database to be ready
    logger.info("🔍 Checking database connection...")
    if not await wait_for_db(db_url):
        logger.error("❌ Failed to connect to database. Please check your database settings.")
        return
    
    try:
        # Create database tables
        logger.info("🔄 Creating database tables...")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        # Initialize database with seed data
        logger.info("🌱 Seeding database...")
        try:
            await init_db()
            logger.info("✅ Database seeding completed successfully")
        except Exception as seed_error:
            logger.error(f"⚠️ Error during database seeding: {seed_error}")
            logger.error(traceback.format_exc())
        
        # Ensure admin user exists
        try:
            await ensure_admin_user()
            logger.info("✅ Admin user check completed")
        except Exception as admin_error:
            logger.error(f"⚠️ Error ensuring admin user: {admin_error}")
            logger.error(traceback.format_exc())
        
        logger.info("✅ Database initialization complete")
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize database: {e}")
        logger.error(traceback.format_exc())
        raise


# Run locally
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)