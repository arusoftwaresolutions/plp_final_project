"""
Profile management API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database import User, get_db
from app.auth import get_current_user

router = APIRouter()

class ProfileUpdate(BaseModel):
    full_name: str = None
    monthly_income: float = None

@router.get("/")
async def get_profile(current_user: User = Depends(get_current_user)):
    """Get user profile"""

    return {
        "id": current_user.id,
        "email": current_user.email,
        "username": current_user.username,
        "full_name": current_user.full_name,
        "monthly_income": current_user.monthly_income,
        "created_at": current_user.created_at,
        "is_admin": current_user.is_admin
    }

@router.put("/")
async def update_profile(
    profile_data: ProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user profile"""

    # Update fields if provided
    if profile_data.full_name is not None:
        current_user.full_name = profile_data.full_name

    if profile_data.monthly_income is not None:
        if profile_data.monthly_income < 0:
            raise HTTPException(status_code=400, detail="Monthly income cannot be negative")
        current_user.monthly_income = profile_data.monthly_income

    db.commit()
    db.refresh(current_user)

    return {"message": "Profile updated successfully", "user": current_user}

@router.get("/stats")
async def get_profile_stats(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get user profile statistics"""

    from app.database import Transaction, Campaign, Contribution, LoanApplication

    # Transaction stats
    total_transactions = db.query(Transaction).filter(
        Transaction.user_id == current_user.id
    ).count()

    total_income = db.query(func.sum(Transaction.amount)).filter(
        Transaction.user_id == current_user.id,
        Transaction.type == 'income'
    ).scalar() or 0

    total_expenses = db.query(func.sum(func.abs(Transaction.amount))).filter(
        Transaction.user_id == current_user.id,
        Transaction.type == 'expense'
    ).scalar() or 0

    # Campaign stats
    campaigns_created = db.query(Campaign).filter(
        Campaign.creator_id == current_user.id
    ).count()

    total_raised = db.query(func.sum(Campaign.current_amount)).filter(
        Campaign.creator_id == current_user.id
    ).scalar() or 0

    # Contribution stats
    contributions_made = db.query(Contribution).filter(
        Contribution.user_id == current_user.id
    ).count()

    total_contributed = db.query(func.sum(Contribution.amount)).filter(
        Contribution.user_id == current_user.id
    ).scalar() or 0

    # Loan stats
    loans_applied = db.query(LoanApplication).filter(
        LoanApplication.user_id == current_user.id
    ).count()

    loans_approved = db.query(LoanApplication).filter(
        LoanApplication.user_id == current_user.id,
        LoanApplication.status == 'approved'
    ).count()

    return {
        "transaction_stats": {
            "total_transactions": total_transactions,
            "total_income": total_income,
            "total_expenses": total_expenses,
            "net_worth": total_income - total_expenses
        },
        "campaign_stats": {
            "campaigns_created": campaigns_created,
            "total_raised": total_raised
        },
        "contribution_stats": {
            "contributions_made": contributions_made,
            "total_contributed": total_contributed
        },
        "loan_stats": {
            "loans_applied": loans_applied,
            "loans_approved": loans_approved
        }
    }
