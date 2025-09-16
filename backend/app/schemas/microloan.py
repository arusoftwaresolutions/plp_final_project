from pydantic import BaseModel, Field, validator
from datetime import datetime, date
from typing import Optional, List, Literal
from enum import Enum

class LoanStatus(str, Enum):
    """
    Loan status enumeration.
    """
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    DISBURSED = "disbursed"
    REPAID = "repaid"
    DEFAULTED = "defaulted"

class MicroLoanBase(BaseModel):
    """
    Base microloan schema.
    """
    amount: float = Field(..., gt=0, description="Loan amount (must be greater than 0)")
    purpose: str = Field(..., max_length=200, description="Purpose of the loan")
    term_months: int = Field(12, ge=1, le=60, description="Loan term in months (1-60)")

class MicroLoanCreate(MicroLoanBase):
    """
    Schema for creating a new microloan application.
    """
    pass

class MicroLoanApprove(BaseModel):
    """
    Schema for approving a microloan.
    """
    interest_rate: float = Field(..., gt=0, le=50, description="Annual interest rate (0-50%)")
    term_months: int = Field(12, ge=1, le=60, description="Loan term in months (1-60)")
    disbursement_date: date = Field(..., description="Date when the loan will be disbursed")
    
    @validator('disbursement_date')
    def validate_disbursement_date(cls, v):
        if v < date.today():
            raise ValueError('Disbursement date cannot be in the past')
        return v

class MicroLoanReject(BaseModel):
    """
    Schema for rejecting a microloan application.
    """
    rejection_reason: str = Field(..., max_length=500, description="Reason for rejection")

class MicroLoanUpdate(BaseModel):
    """
    Schema for updating a microloan.
    """
    status: Optional[LoanStatus] = None
    amount: Optional[float] = Field(None, gt=0, description="Loan amount (must be greater than 0)")
    purpose: Optional[str] = Field(None, max_length=200, description="Purpose of the loan")
    term_months: Optional[int] = Field(None, ge=1, le=60, description="Loan term in months (1-60)")
    interest_rate: Optional[float] = Field(None, gt=0, le=50, description="Annual interest rate (0-50%)")
    disbursement_date: Optional[date] = None
    due_date: Optional[date] = None

class MicroLoanInDBBase(MicroLoanBase):
    """
    Base schema for microloan stored in DB.
    """
    id: int
    user_id: int
    status: LoanStatus = LoanStatus.PENDING
    interest_rate: Optional[float] = None
    disbursement_date: Optional[date] = None
    due_date: Optional[date] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True

class MicroLoanResponse(MicroLoanInDBBase):
    """
    Microloan response schema.
    """
    monthly_payment: Optional[float] = None
    total_interest: Optional[float] = None
    total_payment: Optional[float] = None
    amount_paid: float = 0.0
    amount_due: Optional[float] = None
    days_remaining: Optional[int] = None
    is_overdue: bool = False

class LoanRepaymentBase(BaseModel):
    """
    Base loan repayment schema.
    """
    amount: float = Field(..., gt=0, description="Repayment amount (must be greater than 0)")

class LoanRepaymentCreate(LoanRepaymentBase):
    """
    Schema for creating a new loan repayment.
    """
    pass

class LoanRepaymentInDBBase(LoanRepaymentBase):
    """
    Base schema for loan repayment stored in DB.
    """
    id: int
    loan_id: int
    payment_date: datetime
    status: str = "pending"
    transaction_id: Optional[int] = None
    
    class Config:
        orm_mode = True

class LoanRepaymentResponse(LoanRepaymentInDBBase):
    """
    Loan repayment response schema.
    """
    pass

class LoanSummary(BaseModel):
    """
    Loan summary schema.
    """
    total_loans: int = 0
    total_approved: float = 0.0
    total_disbursed: float = 0.0
    total_repaid: float = 0.0
    total_outstanding: float = 0.0
    total_interest_earned: float = 0.0
    default_rate: float = 0.0

class LoanRepaymentSchedule(BaseModel):
    """
    Loan repayment schedule schema.
    """
    payment_number: int
    due_date: date
    principal: float
    interest: float
    total_payment: float
    remaining_balance: float
    status: str = "pending"
    
    class Config:
        orm_mode = True
