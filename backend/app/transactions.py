"""
Transaction management API endpoints
"""

from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from pydantic import BaseModel

from app.database import Transaction, get_db
from app.auth import get_current_user

router = APIRouter()

class TransactionCreate(BaseModel):
    amount: float
    description: str
    category: str
    type: str  # income or expense

class TransactionResponse(BaseModel):
    id: int
    amount: float
    description: str
    category: str
    type: str
    date: datetime

    class Config:
        from_attributes = True

@router.get("/", response_model=List[TransactionResponse])
async def get_transactions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = 50
):
    """Get user's transaction history"""

    transactions = db.query(Transaction).filter(
        Transaction.user_id == current_user.id
    ).order_by(desc(Transaction.date)).limit(limit).all()

    return transactions

@router.post("/", response_model=TransactionResponse)
async def create_transaction(
    transaction_data: TransactionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new transaction"""

    # Validate transaction type
    if transaction_data.type not in ['income', 'expense']:
        raise HTTPException(status_code=400, detail="Type must be 'income' or 'expense'")

    # Validate amount
    if transaction_data.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")

    # Create transaction
    new_transaction = Transaction(
        user_id=current_user.id,
        amount=transaction_data.amount if transaction_data.type == 'income' else -transaction_data.amount,
        description=transaction_data.description,
        category=transaction_data.category,
        type=transaction_data.type
    )

    db.add(new_transaction)
    db.commit()
    db.refresh(new_transaction)

    return new_transaction

@router.get("/categories")
async def get_transaction_categories():
    """Get available transaction categories"""

    return {
        "income": [
            "salary", "freelance", "business", "investment", "gift", "other_income"
        ],
        "expense": [
            "food", "transport", "housing", "utilities", "healthcare",
            "education", "entertainment", "shopping", "savings", "charity", "other"
        ]
    }

@router.get("/summary")
async def get_transaction_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get transaction summary for current month"""

    # Current month filter
    start_of_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    transactions = db.query(Transaction).filter(
        Transaction.user_id == current_user.id,
        Transaction.date >= start_of_month
    ).all()

    # Calculate totals by category
    income_by_category = {}
    expense_by_category = {}
    total_income = 0
    total_expenses = 0

    for transaction in transactions:
        if transaction.type == 'income':
            income_by_category[transaction.category] = income_by_category.get(transaction.category, 0) + transaction.amount
            total_income += transaction.amount
        else:
            expense_by_category[transaction.category] = expense_by_category.get(transaction.category, 0) + abs(transaction.amount)
            total_expenses += abs(transaction.amount)

    return {
        "total_income": total_income,
        "total_expenses": total_expenses,
        "net_balance": total_income - total_expenses,
        "income_by_category": income_by_category,
        "expense_by_category": expense_by_category,
        "transaction_count": len(transactions)
    }

@router.delete("/{transaction_id}")
async def delete_transaction(
    transaction_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a transaction"""

    transaction = db.query(Transaction).filter(
        Transaction.id == transaction_id,
        Transaction.user_id == current_user.id
    ).first()

    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    db.delete(transaction)
    db.commit()

    return {"message": "Transaction deleted successfully"}
