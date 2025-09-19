from typing import Optional
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.core.config import settings

# Import and include API router
from backend.app.api.api_v1.api import api_router
from backend.app.db.session import engine, AsyncSessionLocal, Base
import traceback

# Create app only ONCE
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
    allow_origins=["*"],  # Allow all origins for now
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

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT
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

    try:
        async with AsyncSessionLocal() as db:
            # Check if already seeded
            result = await db.execute(select(Role).limit(1))
            if result.scalars().first() is not None:
                print("[Startup] Database already initialized, skipping seeding")
                return

            print("[Startup] Creating sample data...")

            # --- ROLES ---
            admin_role = Role(name="admin", description="Administrator with full access")
            user_role = Role(name="user", description="Regular user")
            donor_role = Role(name="donor", description="Donor user")
            db.add_all([admin_role, user_role, donor_role])
            await db.commit()

            # --- USERS ---
            admin_user = User(
                username=settings.FIRST_SUPERUSER,
                email=settings.FIRST_SUPERUSER_EMAIL,
                hashed_password=get_password_hash(settings.FIRST_SUPERUSER_PASSWORD),
                full_name="Admin User",
                is_verified=True,
                is_active=True,
                roles=[admin_role, user_role, donor_role]
            )
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
            db.add_all([admin_user, user1, user2])
            await db.commit()

            # --- TRANSACTIONS ---
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


# Startup event (only one place now)
@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await init_db()
    print("✅ Database ready")


# Run locally
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)
