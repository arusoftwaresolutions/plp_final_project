from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import User, FamilyProfile, Transaction, Campaign, AIRecommendation
from schemas import (
    FamilyProfileCreate, FamilyProfile as FamilyProfileSchema,
    TransactionCreate, Transaction as TransactionSchema,
    CampaignCreate, Campaign as CampaignSchema,
    DashboardStats
)
from auth import get_current_user
from typing import List
from datetime import datetime, timedelta

router = APIRouter()

@router.post("/profile", response_model=FamilyProfileSchema)
def create_family_profile(
    profile: FamilyProfileCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.user_type != "family":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only family users can create family profiles"
        )
    
    # Check if profile already exists
    existing_profile = db.query(FamilyProfile).filter(FamilyProfile.user_id == current_user.id).first()
    if existing_profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Family profile already exists"
        )
    
    db_profile = FamilyProfile(
        user_id=current_user.id,
        **profile.dict()
    )
    db.add(db_profile)
    db.commit()
    db.refresh(db_profile)
    
    return db_profile

@router.get("/profile", response_model=FamilyProfileSchema)
def get_family_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.user_type != "family":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only family users can access family profiles"
        )
    
    profile = db.query(FamilyProfile).filter(FamilyProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Family profile not found"
        )
    
    return profile

@router.post("/transactions", response_model=TransactionSchema)
def create_transaction(
    transaction: TransactionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.user_type != "family":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only family users can create transactions"
        )
    
    profile = db.query(FamilyProfile).filter(FamilyProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Family profile not found"
        )
    
    db_transaction = Transaction(
        family_id=profile.id,
        **transaction.dict()
    )
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    
    return db_transaction

@router.get("/transactions", response_model=List[TransactionSchema])
def get_transactions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.user_type != "family":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only family users can access transactions"
        )
    
    profile = db.query(FamilyProfile).filter(FamilyProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Family profile not found"
        )
    
    transactions = db.query(Transaction).filter(Transaction.family_id == profile.id).all()
    return transactions

@router.post("/campaigns", response_model=CampaignSchema)
def create_campaign(
    campaign: CampaignCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.user_type != "family":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only family users can create campaigns"
        )
    
    profile = db.query(FamilyProfile).filter(FamilyProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Family profile not found"
        )
    
    db_campaign = Campaign(
        family_id=profile.id,
        **campaign.dict()
    )
    db.add(db_campaign)
    db.commit()
    db.refresh(db_campaign)
    
    return db_campaign

@router.get("/campaigns", response_model=List[CampaignSchema])
def get_campaigns(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.user_type != "family":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only family users can access campaigns"
        )
    
    profile = db.query(FamilyProfile).filter(FamilyProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Family profile not found"
        )
    
    campaigns = db.query(Campaign).filter(Campaign.family_id == profile.id).all()
    return campaigns

@router.get("/dashboard", response_model=DashboardStats)
def get_dashboard_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.user_type != "family":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only family users can access dashboard"
        )
    
    profile = db.query(FamilyProfile).filter(FamilyProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Family profile not found"
        )
    
    # Get transactions
    transactions = db.query(Transaction).filter(Transaction.family_id == profile.id).all()
    
    # Calculate stats
    total_income = sum(t.amount for t in transactions if t.transaction_type == "income")
    total_expenses = sum(t.amount for t in transactions if t.transaction_type == "expense")
    net_income = total_income - total_expenses
    
    # Get recent transactions (last 10)
    recent_transactions = sorted(transactions, key=lambda x: x.date, reverse=True)[:10]
    
    # Get AI recommendations
    ai_recommendations = db.query(AIRecommendation).filter(
        AIRecommendation.family_id == profile.id
    ).order_by(AIRecommendation.created_at.desc()).limit(5).all()
    
    return DashboardStats(
        total_income=total_income,
        total_expenses=total_expenses,
        net_income=net_income,
        transaction_count=len(transactions),
        recent_transactions=recent_transactions,
        ai_recommendations=ai_recommendations
    )
