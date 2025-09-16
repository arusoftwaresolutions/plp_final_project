from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app import models, schemas
from app.api import deps
from app.db.session import get_db
from app.services import transaction as transaction_service

router = APIRouter()

@router.get("/", response_model=List[schemas.TransactionResponse])
async def read_transactions(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve transactions for the current user.
    """
    transactions = await transaction_service.get_user_transactions(
        db, user_id=current_user.id, skip=skip, limit=limit
    )
    return transactions

@router.post("/", response_model=schemas.TransactionResponse, status_code=status.HTTP_201_CREATED)
async def create_transaction(
    *,
    db: AsyncSession = Depends(get_db),
    transaction_in: schemas.TransactionCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new transaction for the current user.
    """
    transaction = await transaction_service.create(
        db, obj_in=transaction_in, user_id=current_user.id
    )
    return transaction

@router.get("/{transaction_id}", response_model=schemas.TransactionResponse)
async def read_transaction(
    transaction_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Get transaction by ID.
    """
    transaction = await transaction_service.get(db, id=transaction_id)
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found",
        )
    
    # Check if the transaction belongs to the current user
    if transaction.user_id != current_user.id and not deps.is_superuser(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    return transaction

@router.put("/{transaction_id}", response_model=schemas.TransactionResponse)
async def update_transaction(
    *,
    db: AsyncSession = Depends(get_db),
    transaction_id: int,
    transaction_in: schemas.TransactionUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update a transaction.
    """
    transaction = await transaction_service.get(db, id=transaction_id)
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found",
        )
    
    # Check if the transaction belongs to the current user
    if transaction.user_id != current_user.id and not deps.is_superuser(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    transaction = await transaction_service.update(
        db, db_obj=transaction, obj_in=transaction_in
    )
    return transaction

@router.delete("/{transaction_id}", response_model=schemas.TransactionResponse)
async def delete_transaction(
    *,
    db: AsyncSession = Depends(get_db),
    transaction_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete a transaction.
    """
    transaction = await transaction_service.get(db, id=transaction_id)
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found",
        )
    
    # Check if the transaction belongs to the current user
    if transaction.user_id != current_user.id and not deps.is_superuser(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    transaction = await transaction_service.remove(db, id=transaction_id)
    return transaction

@router.get("/summary/", response_model=schemas.TransactionSummary)
async def get_transaction_summary(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> Any:
    """
    Get transaction summary for the current user.
    """
    summary = await transaction_service.get_summary(
        db, user_id=current_user.id, start_date=start_date, end_date=end_date
    )
    return summary

@router.get("/categories/", response_model=List[schemas.TransactionByCategory])
async def get_transactions_by_category(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> Any:
    """
    Get transactions grouped by category for the current user.
    """
    transactions = await transaction_service.get_by_category(
        db, user_id=current_user.id, start_date=start_date, end_date=end_date
    )
    return transactions
