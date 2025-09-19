from typing import Optional
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.core.config import settings

# Import and include API router after app creation to avoid circular imports
from backend.app.api.api_v1.api import api_router

# Create app first
app = FastAPI(title="Poverty Alleviation Platform API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Welcome to the Poverty Alleviation Platform API",
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc"
        },
        "status": "operational",
        "version": "1.0.0"
    }

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)

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
    from datetime import datetime, timedelta
    import json
    from sqlalchemy import select
    from sqlalchemy.orm import joinedload
    from backend.app.db.models import (
        Role, User, Transaction, TransactionType, TransactionCategory,
        MicroLoan, LoanStatus, LoanRepayment, CrowdFundingCampaign,
        Donation, PovertyArea, Notification, NotificationType,
        UserNotificationPreference
    )
    from passlib.context import CryptContext
    
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    try:
        async with AsyncSessionLocal() as db:
            # Check if we already have data
            result = await db.execute(select(Role).limit(1))
            if result.scalars().first() is not None:
                print("Database already initialized, skipping sample data creation")
                return

            print("Creating sample data...")
            
            # Create roles
            admin_role = Role(name="admin", description="Administrator with full access")
            user_role = Role(name="user", description="Regular user")
            donor_role = Role(name="donor", description="Donor user")
            
            db.add_all([admin_role, user_role, donor_role])
            await db.commit()
            await db.refresh(admin_role)
            await db.refresh(user_role)
            await db.refresh(donor_role)
            
            # Create admin user
            admin_user = User(
                username="admin",
                email="admin@example.com",
                hashed_password=pwd_context.hash("admin123"),
                full_name="Admin User",
                is_verified=True,
                is_active=True
            )
            admin_user.roles = [admin_role, user_role, donor_role]
            
            # Create regular users
            user1 = User(
                username="john_doe",
                email="john@example.com",
                hashed_password=pwd_context.hash("password123"),
                full_name="John Doe",
                is_verified=True,
                is_active=True
            )
            user1.roles = [user_role]
            
            user2 = User(
                username="jane_smith",
                email="jane@example.com",
                hashed_password=pwd_context.hash("password123"),
                full_name="Jane Smith",
                is_verified=True,
                is_active=True
            )
            user2.roles = [user_role, donor_role]
            
            db.add_all([admin_user, user1, user2])
            await db.commit()
            
            # Create transactions
            today = datetime.utcnow()
            transactions = [
                Transaction(
                    user=admin_user,
                    amount=1500.00,
                    transaction_type=TransactionType.INCOME,
                    category=TransactionCategory.SALARY,
                    description="Monthly salary",
                    date=today - timedelta(days=5)
                ),
                Transaction(
                    user=user1,
                    amount=1200.00,
                    transaction_type=TransactionType.INCOME,
                    category=TransactionCategory.SALARY,
                    description="Monthly salary",
                    date=today - timedelta(days=10)
                ),
                Transaction(
                    user=user1,
                    amount=150.00,
                    transaction_type=TransactionType.EXPENSE,
                    category=TransactionCategory.FOOD,
                    description="Weekly groceries",
                    date=today - timedelta(days=2)
                ),
                Transaction(
                    user=user2,
                    amount=200.00,
                    transaction_type=TransactionType.SAVINGS,
                    category=TransactionCategory.EMERGENCY_FUND,
                    description="Monthly savings",
                    date=today - timedelta(days=15)
                )
            ]
            
            db.add_all(transactions)
            await db.commit()
            
            # Create microloans
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
            
            # Create loan repayments
            repayment1 = LoanRepayment(
                loan=loan1,
                amount=100.00,
                payment_date=today - timedelta(days=5),
                status="completed"
            )
            
            db.add(repayment1)
            await db.commit()
            
            # Create poverty areas
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
            
            # Create crowdfunding campaigns
            campaign1 = CrowdFundingCampaign(
                title="Clean Water for Rural Village",
                description="Help us provide clean drinking water to 100 families in Rural Village A",
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
            
            # Create donations
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
            
            # Create notifications
            notification1 = Notification(
                user=user1,
                notification_type=NotificationType.NEW_LOAN,
                message="Your loan application has been approved!",
                read=False
            )
            
            notification2 = Notification(
                user=user2,
                notification_type=NotificationType.NEW_DONATION,
                message="Thank you for your donation to Education for All!",
                read=False
            )
            
            db.add_all([notification1, notification2])
            await db.commit()
            
            # Update campaign amounts raised
            campaign1.amount_raised = 3500.00
            campaign2.amount_raised = 5200.00
            await db.commit()
            
            print("✅ Sample data created successfully!")
            
            
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
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for now, can be restricted later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/health")
async def health_check():
    from backend.app.core.config import settings
    return {
        "status": "ok",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT
    }

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    from backend.app.db.session import engine, Base
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Database initialized")

# This allows running with `python -m backend.app.main` for local development
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)
