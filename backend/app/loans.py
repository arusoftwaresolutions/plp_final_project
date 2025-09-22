"""
Microloan API endpoints
"""

from datetime import datetime, timedelta
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel

from app.database import LoanOffer, LoanApplication, LoanRepayment, get_db
from app.auth import get_current_user
from app.ai_module import financial_ai

router = APIRouter()

class LoanApplicationCreate(BaseModel):
    loan_offer_id: int
    amount: float
    term_months: int

class LoanApplicationResponse(BaseModel):
    id: int
    amount: float
    term_months: int
    status: str
    monthly_payment: float
    total_amount: float
    remaining_balance: float
    created_at: datetime
    loan_title: str

    class Config:
        from_attributes = True

@router.get("/offers")
async def get_loan_offers(db: Session = Depends(get_db)):
    """Get available loan offers"""

    offers = db.query(LoanOffer).filter(LoanOffer.is_active == True).all()

    return offers

@router.get("/offers/recommendations")
async def get_personalized_loan_recommendations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get AI-powered personalized loan recommendations"""

    offers = db.query(LoanOffer).filter(LoanOffer.is_active == True).all()

    user_profile = {
        "monthly_income": current_user.monthly_income,
        "credit_score": 650,  # This would come from external credit check
        "existing_loans": db.query(LoanApplication).filter(
            LoanApplication.user_id == current_user.id,
            LoanApplication.status.in_(['approved', 'pending'])
        ).count()
    }

    recommendations = financial_ai.generate_loan_recommendations(user_profile, [o.__dict__ for o in offers])

    return recommendations

@router.post("/apply")
async def apply_for_loan(
    application_data: LoanApplicationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Apply for a loan"""

    # Get loan offer
    offer = db.query(LoanOffer).filter(LoanOffer.id == application_data.loan_offer_id).first()
    if not offer:
        raise HTTPException(status_code=404, detail="Loan offer not found")

    # Validate amount
    if application_data.amount <= 0 or application_data.amount > offer.max_amount:
        raise HTTPException(status_code=400, detail=f"Amount must be between 0 and {offer.max_amount}")

    # Validate term
    if application_data.term_months <= 0 or application_data.term_months > offer.max_term_months:
        raise HTTPException(status_code=400, detail=f"Term must be between 1 and {offer.max_term_months} months")

    # Calculate loan details
    monthly_rate = offer.interest_rate / 100 / 12
    monthly_payment = application_data.amount * (monthly_rate * (1 + monthly_rate) ** application_data.term_months) / ((1 + monthly_rate) ** application_data.term_months - 1)
    total_amount = monthly_payment * application_data.term_months

    # Create loan application
    application = LoanApplication(
        user_id=current_user.id,
        loan_offer_id=offer.id,
        amount=application_data.amount,
        term_months=application_data.term_months,
        status="pending",
        monthly_payment=round(monthly_payment, 2),
        total_amount=round(total_amount, 2),
        remaining_balance=round(total_amount, 2)
    )

    db.add(application)
    db.commit()
    db.refresh(application)

    # Add creator name to response
    application.loan_title = offer.title

    return application

@router.get("/applications")
async def get_loan_applications(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's loan applications"""

    applications = db.query(LoanApplication).filter(
        LoanApplication.user_id == current_user.id
    ).all()

    # Add loan titles
    for app in applications:
        app.loan_title = app.loan_offer.title

    return applications

@router.get("/applications/{application_id}")
async def get_loan_application(
    application_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get loan application details with repayment schedule"""

    application = db.query(LoanApplication).filter(
        LoanApplication.id == application_id,
        LoanApplication.user_id == current_user.id
    ).first()

    if not application:
        raise HTTPException(status_code=404, detail="Loan application not found")

    # Get repayment schedule
    repayments = db.query(LoanRepayment).filter(
        LoanRepayment.loan_application_id == application_id
    ).order_by(LoanRepayment.due_date).all()

    return {
        "application": application,
        "repayments": repayments,
        "next_payment": next((r for r in repayments if not r.is_paid), None)
    }

@router.post("/applications/{application_id}/repay")
async def make_loan_repayment(
    application_id: int,
    amount: float,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Make a loan repayment"""

    application = db.query(LoanApplication).filter(
        LoanApplication.id == application_id,
        LoanApplication.user_id == current_user.id
    ).first()

    if not application:
        raise HTTPException(status_code=404, detail="Loan application not found")

    if application.status != 'approved':
        raise HTTPException(status_code=400, detail="Loan not approved yet")

    if amount <= 0:
        raise HTTPException(status_code=400, detail="Repayment amount must be positive")

    # Get next unpaid repayment
    next_repayment = db.query(LoanRepayment).filter(
        LoanRepayment.loan_application_id == application_id,
        LoanRepayment.is_paid == False
    ).order_by(LoanRepayment.due_date).first()

    if not next_repayment:
        raise HTTPException(status_code=400, detail="No pending repayments")

    # Process payment
    next_repayment.is_paid = True
    next_repayment.paid_date = datetime.now()
    application.remaining_balance -= amount

    # Check if loan is fully paid
    if application.remaining_balance <= 0:
        application.status = 'completed'
        application.completed_at = datetime.now()

    db.commit()

    return {
        "message": "Payment processed successfully",
        "application": application,
        "repayment": next_repayment
    }

# Admin endpoints for loan management
@router.put("/applications/{application_id}/approve")
async def approve_loan_application(
    application_id: int,
    current_user: User = Depends(get_current_user),  # This should be admin only
    db: Session = Depends(get_db)
):
    """Approve a loan application (admin only)"""

    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")

    application = db.query(LoanApplication).filter(
        LoanApplication.id == application_id
    ).first()

    if not application:
        raise HTTPException(status_code=404, detail="Loan application not found")

    if application.status != 'pending':
        raise HTTPException(status_code=400, detail="Application already processed")

    # Approve application
    application.status = 'approved'
    application.approved_at = datetime.now()

    # Create repayment schedule
    repayment_amount = application.monthly_payment
    due_date = datetime.now() + timedelta(days=30)  # First payment in 30 days

    for i in range(application.term_months):
        repayment = LoanRepayment(
            user_id=application.user_id,
            loan_application_id=application.id,
            amount=repayment_amount,
            due_date=due_date + timedelta(days=i * 30)
        )
        db.add(repayment)

    db.commit()

    return {"message": "Loan approved successfully", "application": application}
