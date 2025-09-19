from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app import models, schemas
from backend.app.api import deps
from backend.app.db.session import get_db
from backend.app.services import microloan as microloan_service

router = APIRouter()

@router.get("/", response_model=List[schemas.MicroLoanResponse])
async def read_microloans(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve microloans. Admin can see all, users see only their own.
    """
    if deps.is_superuser(current_user):
        microloans = await microloan_service.get_multi(db, skip=skip, limit=limit)
    else:
        microloans = await microloan_service.get_user_microloans(
            db, user_id=current_user.id, skip=skip, limit=limit
        )
    return microloans

@router.post("/apply", response_model=schemas.MicroLoanResponse, status_code=status.HTTP_201_CREATED)
async def apply_for_microloan(
    *,
    db: AsyncSession = Depends(get_db),
    microloan_in: schemas.MicroLoanCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Apply for a new microloan.
    """
    # Check if user has any pending or active loans
    existing_loans = await microloan_service.get_user_active_loans(db, user_id=current_user.id)
    if existing_loans:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You already have an active or pending loan",
        )
    
    # Create new microloan application
    microloan = await microloan_service.create(
        db, obj_in=microloan_in, user_id=current_user.id
    )
    return microloan

@router.get("/{loan_id}", response_model=schemas.MicroLoanResponse)
async def read_microloan(
    loan_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Get microloan by ID.
    """
    microloan = await microloan_service.get(db, id=loan_id)
    if not microloan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Microloan not found",
        )
    
    # Check if the microloan belongs to the current user or if user is admin
    if microloan.user_id != current_user.id and not deps.is_superuser(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    return microloan

@router.put("/{loan_id}/approve", response_model=schemas.MicroLoanResponse)
async def approve_microloan(
    *,
    db: AsyncSession = Depends(get_db),
    loan_id: int,
    approval_data: schemas.MicroLoanApprove,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Approve a microloan application (admin only).
    """
    microloan = await microloan_service.get(db, id=loan_id)
    if not microloan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Microloan not found",
        )
    
    if microloan.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot approve microloan with status: {microloan.status}",
        )
    
    # Update microloan status to approved
    update_data = {
        "status": "approved",
        "approved_by": current_user.id,
        "approved_at": datetime.utcnow(),
        "interest_rate": approval_data.interest_rate,
        "term_months": approval_data.term_months,
    }
    
    microloan = await microloan_service.update(
        db, db_obj=microloan, obj_in=update_data
    )
    
    return microloan

@router.put("/{loan_id}/reject", response_model=schemas.MicroLoanResponse)
async def reject_microloan(
    *,
    db: AsyncSession = Depends(get_db),
    loan_id: int,
    rejection_data: schemas.MicroLoanReject,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Reject a microloan application (admin only).
    """
    microloan = await microloan_service.get(db, id=loan_id)
    if not microloan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Microloan not found",
        )
    
    if microloan.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot reject microloan with status: {microloan.status}",
        )
    
    # Update microloan status to rejected
    update_data = {
        "status": "rejected",
        "rejected_by": current_user.id,
        "rejected_at": datetime.utcnow(),
        "rejection_reason": rejection_data.rejection_reason,
    }
    
    microloan = await microloan_service.update(
        db, db_obj=microloan, obj_in=update_data
    )
    
    return microloan

@router.post("/{loan_id}/repay", response_model=schemas.LoanRepaymentResponse)
async def repay_loan(
    *,
    db: AsyncSession = Depends(get_db),
    loan_id: int,
    repayment_data: schemas.LoanRepaymentCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Make a loan repayment.
    """
    microloan = await microloan_service.get(db, id=loan_id)
    if not microloan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Microloan not found",
        )
    
    # Check if the microloan belongs to the current user
    if microloan.user_id != current_user.id and not deps.is_superuser(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    # Process loan repayment
    repayment = await microloan_service.process_repayment(
        db, 
        loan_id=loan_id, 
        amount=repayment_data.amount,
        user_id=current_user.id
    )
    
    return repayment

@router.get("/{loan_id}/repayments", response_model=List[schemas.LoanRepaymentResponse])
async def get_loan_repayments(
    loan_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Get all repayments for a specific loan.
    """
    microloan = await microloan_service.get(db, id=loan_id)
    if not microloan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Microloan not found",
        )
    
    # Check if the microloan belongs to the current user or if user is admin
    if microloan.user_id != current_user.id and not deps.is_superuser(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    repayments = await microloan_service.get_repayments(db, loan_id=loan_id)
    return repayments
