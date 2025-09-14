from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import User, LoanApplication, Campaign, Donation, FamilyProfile
from schemas import LoanApplicationUpdate, LoanApplication as LoanApplicationSchema
from auth import get_current_user
from typing import List
from datetime import datetime

router = APIRouter()

def verify_admin(current_user: User = Depends(get_current_user)):
    if current_user.user_type != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin users can access this endpoint"
        )
    return current_user

@router.get("/loan-applications", response_model=List[LoanApplicationSchema])
def get_all_loan_applications(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    loans = db.query(LoanApplication).offset(skip).limit(limit).all()
    return loans

@router.get("/loan-applications/{loan_id}", response_model=LoanApplicationSchema)
def get_loan_application(
    loan_id: str,
    current_user: User = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    loan = db.query(LoanApplication).filter(LoanApplication.id == loan_id).first()
    if not loan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Loan application not found"
        )
    return loan

@router.put("/loan-applications/{loan_id}", response_model=LoanApplicationSchema)
def update_loan_application(
    loan_id: str,
    loan_update: LoanApplicationUpdate,
    current_user: User = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    loan = db.query(LoanApplication).filter(LoanApplication.id == loan_id).first()
    if not loan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Loan application not found"
        )
    
    loan.status = loan_update.status
    loan.admin_notes = loan_update.admin_notes
    loan.reviewed_at = datetime.utcnow()
    
    db.commit()
    db.refresh(loan)
    
    return loan

@router.get("/campaigns", response_model=List[dict])
def get_all_campaigns(
    current_user: User = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    campaigns = db.query(Campaign).all()
    result = []
    for campaign in campaigns:
        donations = db.query(Donation).filter(Donation.campaign_id == campaign.id).all()
        result.append({
            "id": campaign.id,
            "title": campaign.title,
            "description": campaign.description,
            "target_amount": campaign.target_amount,
            "current_amount": campaign.current_amount,
            "status": campaign.status,
            "donation_count": len(donations),
            "created_at": campaign.created_at
        })
    return result

@router.get("/families", response_model=List[dict])
def get_all_families(
    current_user: User = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    families = db.query(FamilyProfile).all()
    result = []
    for family in families:
        user = db.query(User).filter(User.id == family.user_id).first()
        result.append({
            "id": family.id,
            "user_id": family.user_id,
            "full_name": user.full_name if user else "Unknown",
            "email": user.email if user else "Unknown",
            "family_size": family.family_size,
            "monthly_income": family.monthly_income,
            "location": family.location,
            "created_at": family.created_at
        })
    return result

@router.get("/stats")
def get_admin_stats(
    current_user: User = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    total_families = db.query(FamilyProfile).count()
    total_campaigns = db.query(Campaign).count()
    total_donations = db.query(Donation).count()
    total_loans = db.query(LoanApplication).count()
    
    pending_loans = db.query(LoanApplication).filter(LoanApplication.status == "pending").count()
    approved_loans = db.query(LoanApplication).filter(LoanApplication.status == "approved").count()
    
    total_donated = db.query(Donation).with_entities(db.func.sum(Donation.amount)).scalar() or 0
    
    return {
        "total_families": total_families,
        "total_campaigns": total_campaigns,
        "total_donations": total_donations,
        "total_loans": total_loans,
        "pending_loans": pending_loans,
        "approved_loans": approved_loans,
        "total_donated": float(total_donated)
    }
