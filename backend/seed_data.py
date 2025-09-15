"""
Seed script to populate the database with demo data
"""
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import Base, User, FamilyProfile, DonorProfile, BusinessProfile, Transaction, Campaign, Donation, LoanApplication, PovertyHotspot, AIRecommendation
from auth import get_password_hash
from datetime import datetime, timedelta
import random

def create_demo_data():
    """Create demo data for testing"""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    try:
        # Create demo users
        users_data = [
            {
                "email": "family1@example.com",
                "full_name": "John Smith",
                "user_type": "family",
                "password": "password123"
            },
            {
                "email": "family2@example.com", 
                "full_name": "Maria Garcia",
                "user_type": "family",
                "password": "password123"
            },
            {
                "email": "donor1@example.com",
                "full_name": "Alice Johnson",
                "user_type": "donor",
                "password": "password123"
            },
            {
                "email": "donor2@example.com",
                "full_name": "Bob Wilson",
                "user_type": "donor", 
                "password": "password123"
            },
            {
                "email": "business1@example.com",
                "full_name": "Tech Startup LLC",
                "user_type": "business",
                "password": "password123"
            },
            {
                "email": "admin@example.com",
                "full_name": "Admin User",
                "user_type": "admin",
                "password": "password123"
            }
        ]
        
        users = []
        for user_data in users_data:
            user = User(
                email=user_data["email"],
                hashed_password=get_password_hash(user_data["password"]),
                full_name=user_data["full_name"],
                user_type=user_data["user_type"]
            )
            db.add(user)
            db.flush()  # Get the ID
            users.append(user)
        
        db.commit()
        
        # Create family profiles
        family_profiles = [
            {
                "user_id": users[0].id,
                "family_size": 4,
                "monthly_income": 4500.0,
                "location": "New York, NY",
                "latitude": 40.7128,
                "longitude": -74.0060
            },
            {
                "user_id": users[1].id,
                "family_size": 3,
                "monthly_income": 3200.0,
                "location": "Los Angeles, CA",
                "latitude": 34.0522,
                "longitude": -118.2437
            }
        ]
        
        families = []
        for profile_data in family_profiles:
            family = FamilyProfile(**profile_data)
            db.add(family)
            db.flush()
            families.append(family)
        
        # Create donor profiles
        donor_profiles = []
        for i in range(2):
            donor = DonorProfile(user_id=users[i+2].id)
            db.add(donor)
            db.flush()
            donor_profiles.append(donor)
        
        # Create business profile
        business = BusinessProfile(
            user_id=users[4].id,
            business_name="Tech Startup LLC",
            business_type="Technology",
            annual_revenue=150000.0,
            location="San Francisco, CA",
            latitude=37.7749,
            longitude=-122.4194
        )
        db.add(business)
        db.flush()
        
        # Create transactions for families
        transaction_categories = ["Food", "Housing", "Transportation", "Healthcare", "Entertainment", "Education", "Utilities"]
        
        for family in families:
            # Create income transactions
            for i in range(6):  # 6 months of data
                income_date = datetime.utcnow() - timedelta(days=30*i)
                income = Transaction(
                    family_id=family.id,
                    amount=family.monthly_income + random.uniform(-200, 200),
                    transaction_type="income",
                    category="Salary",
                    description="Monthly salary",
                    date=income_date
                )
                db.add(income)
            
            # Create expense transactions
            for i in range(30):  # 30 random expenses
                expense_date = datetime.utcnow() - timedelta(days=random.randint(1, 180))
                category = random.choice(transaction_categories)
                amount = random.uniform(20, 500)
                
                expense = Transaction(
                    family_id=family.id,
                    amount=amount,
                    transaction_type="expense",
                    category=category,
                    description=f"Expense for {category.lower()}",
                    date=expense_date
                )
                db.add(expense)
        
        # Create campaigns
        campaigns = [
            {
                "title": "Emergency Medical Fund",
                "description": "Help cover unexpected medical expenses for our family",
                "target_amount": 5000.0,
                "family_id": families[0].id
            },
            {
                "title": "Education Fund",
                "description": "Support our children's education and school supplies",
                "target_amount": 3000.0,
                "family_id": families[1].id
            }
        ]
        
        campaign_objects = []
        for campaign_data in campaigns:
            campaign = Campaign(**campaign_data)
            db.add(campaign)
            db.flush()
            campaign_objects.append(campaign)
        
        # Create donations
        for i, campaign in enumerate(campaign_objects):
            for j in range(random.randint(3, 8)):
                donation = Donation(
                    donor_id=donor_profiles[j % len(donor_profiles)].id,
                    campaign_id=campaign.id,
                    amount=random.uniform(25, 500),
                    is_anonymous=random.choice([True, False])
                )
                db.add(donation)
                campaign.current_amount += donation.amount
        
        # Create loan applications
        loan_applications = [
            {
                "business_id": business.id,
                "amount": 25000.0,
                "purpose": "Equipment purchase for expansion",
                "status": "pending"
            },
            {
                "business_id": business.id,
                "amount": 15000.0,
                "purpose": "Working capital",
                "status": "approved"
            }
        ]
        
        for loan_data in loan_applications:
            loan = LoanApplication(**loan_data)
            db.add(loan)
        
        # Create poverty hotspots
        poverty_hotspots = [
            {
                "name": "Downtown Poverty Zone",
                "latitude": 40.7589,
                "longitude": -73.9851,
                "poverty_rate": 25.5,
                "population": 15000,
                "description": "High poverty area in downtown Manhattan"
            },
            {
                "name": "South Side Community",
                "latitude": 40.6782,
                "longitude": -73.9442,
                "poverty_rate": 18.2,
                "population": 22000,
                "description": "Community with elevated poverty rates"
            },
            {
                "name": "East Village Area",
                "latitude": 40.7282,
                "longitude": -73.9918,
                "poverty_rate": 22.1,
                "population": 18000,
                "description": "Mixed-income neighborhood with poverty pockets"
            }
        ]
        
        for hotspot_data in poverty_hotspots:
            hotspot = PovertyHotspot(**hotspot_data)
            db.add(hotspot)
        
        # Create AI recommendations
        for family in families:
            recommendations = [
                {
                    "family_id": family.id,
                    "recommendation_type": "budgeting",
                    "title": "Track Your Spending",
                    "description": "Consider using a budgeting app to track your daily expenses and identify areas for savings.",
                    "priority": "high"
                },
                {
                    "family_id": family.id,
                    "recommendation_type": "savings",
                    "title": "Build Emergency Fund",
                    "description": "Aim to save 3-6 months of expenses in an emergency fund for financial security.",
                    "priority": "medium"
                }
            ]
            
            for rec_data in recommendations:
                recommendation = AIRecommendation(**rec_data)
                db.add(recommendation)
        
        db.commit()
        print("Demo data created successfully!")
        
    except Exception as e:
        print(f"Error creating demo data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_demo_data()

