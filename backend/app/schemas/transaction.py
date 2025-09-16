from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional, List, Literal
from enum import Enum

class TransactionType(str, Enum):
    """
    Transaction type enumeration.
    """
    INCOME = "income"
    EXPENSE = "expense"
    SAVINGS = "savings"
    LOAN = "loan"
    DONATION = "donation"

class TransactionCategory(str, Enum):
    """
    Transaction category enumeration.
    """
    # Income categories
    SALARY = "salary"
    BUSINESS = "business"
    INVESTMENT = "investment"
    GIFT = "gift"
    OTHER_INCOME = "other_income"
    
    # Expense categories
    FOOD = "food"
    TRANSPORT = "transport"
    HOUSING = "housing"
    HEALTH = "health"
    EDUCATION = "education"
    ENTERTAINMENT = "entertainment"
    UTILITIES = "utilities"
    OTHER_EXPENSE = "other_expense"
    
    # Savings categories
    EMERGENCY_FUND = "emergency_fund"
    RETIREMENT = "retirement"
    INVESTMENT_SAVINGS = "investment_savings"
    OTHER_SAVINGS = "other_savings"

class TransactionBase(BaseModel):
    """
    Base transaction schema.
    """
    amount: float = Field(..., gt=0, description="Transaction amount (must be greater than 0)")
    transaction_type: TransactionType
    category: TransactionCategory
    description: Optional[str] = Field(None, max_length=200)
    date: datetime = Field(default_factory=datetime.utcnow)

class TransactionCreate(TransactionBase):
    """
    Schema for creating a new transaction.
    """
    pass

class TransactionUpdate(BaseModel):
    """
    Schema for updating a transaction.
    """
    amount: Optional[float] = Field(None, gt=0, description="Transaction amount (must be greater than 0)")
    transaction_type: Optional[TransactionType] = None
    category: Optional[TransactionCategory] = None
    description: Optional[str] = Field(None, max_length=200)
    date: Optional[datetime] = None

class TransactionInDBBase(TransactionBase):
    """
    Base schema for transaction stored in DB.
    """
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True

class TransactionResponse(TransactionInDBBase):
    """
    Transaction response schema.
    """
    pass

class TransactionSummary(BaseModel):
    """
    Transaction summary schema.
    """
    total_income: float = 0.0
    total_expenses: float = 0.0
    total_savings: float = 0.0
    net_balance: float = 0.0
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    transaction_count: int = 0

class TransactionByCategory(BaseModel):
    """
    Transaction summary by category.
    """
    category: str
    transaction_type: TransactionType
    total_amount: float
    count: int
    percentage: float = 0.0

class TransactionFilter(BaseModel):
    """
    Transaction filter schema.
    """
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    transaction_types: Optional[List[TransactionType]] = None
    categories: Optional[List[TransactionCategory]] = None
    min_amount: Optional[float] = None
    max_amount: Optional[float] = None
    
    @validator('end_date', always=True)
    def validate_date_range(cls, v, values):
        if 'start_date' in values and values['start_date'] and v:
            if v < values['start_date']:
                raise ValueError('End date must be after start date')
        return v
    
    @validator('min_amount', 'max_amount')
    def validate_amounts(cls, v, values, **kwargs):
        if v is not None and v < 0:
            raise ValueError('Amount must be positive')
        return v
    
    @validator('min_amount', 'max_amount')
    def validate_amount_range(cls, v, values, **kwargs):
        if 'min_amount' in values and 'max_amount' in values:
            if values['min_amount'] is not None and values['max_amount'] is not None:
                if values['min_amount'] > values['max_amount']:
                    raise ValueError('Minimum amount cannot be greater than maximum amount')
        return v
