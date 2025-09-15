from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import User, BusinessProfile, LoanApplication
from schemas import (
    BusinessProfileCreate, BusinessProfile as BusinessProfileSchema,
    LoanApplicationCreate, LoanApplication as LoanApplicationSchema
)
from auth import get_current_user
from typing import List

router = APIRouter()

@router.post("/profile", response_model=BusinessProfileSchema)
def create_business_profile(
    profile: BusinessProfileCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.user_type != "business":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only business users can create business profiles"
        )
    
    # Check if profile already exists
    existing_profile = db.query(BusinessProfile).filter(BusinessProfile.user_id == current_user.id).first()
    if existing_profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Business profile already exists"
        )
    
    db_profile = BusinessProfile(
        user_id=current_user.id,
        **profile.dict()
    )
    db.add(db_profile)
    db.commit()
    db.refresh(db_profile)
    
    return db_profile

@router.get("/profile", response_model=BusinessProfileSchema)
def get_business_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.user_type != "business":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only business users can access business profiles"
        )
    
    profile = db.query(BusinessProfile).filter(BusinessProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business profile not found"
        )
    
    return profile

@router.post("/loan-applications", response_model=LoanApplicationSchema)
def create_loan_application(
    loan: LoanApplicationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.user_type != "business":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only business users can create loan applications"
        )
    
    profile = db.query(BusinessProfile).filter(BusinessProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business profile not found"
        )
    
    db_loan = LoanApplication(
        business_id=profile.id,
        **loan.dict()
    )
    db.add(db_loan)
    db.commit()
    db.refresh(db_loan)
    
    return db_loan

@router.get("/loan-applications", response_model=List[LoanApplicationSchema])
def get_loan_applications(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.user_type != "business":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only business users can access loan applications"
        )
    
    profile = db.query(BusinessProfile).filter(BusinessProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business profile not found"
        )
    
    loans = db.query(LoanApplication).filter(LoanApplication.business_id == profile.id).all()
    return loans

@router.get("/loan-applications/{loan_id}", response_model=LoanApplicationSchema)
def get_loan_application(
    loan_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.user_type != "business":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only business users can access loan applications"
        )
    
    profile = db.query(BusinessProfile).filter(BusinessProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business profile not found"
        )
    
    loan = db.query(LoanApplication).filter(
        LoanApplication.id == loan_id,
        LoanApplication.business_id == profile.id
    ).first()
    
    if not loan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Loan application not found"
        )
    
    return loan

