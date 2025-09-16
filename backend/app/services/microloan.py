from datetime import datetime, date, timedelta
from decimal import Decimal
from typing import List, Optional, Tuple, Dict, Any
from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import MicroLoan, LoanRepayment, User, Transaction
from app.schemas.microloan import (
    MicroLoanCreate, MicroLoanUpdate, MicroLoanApprove, MicroLoanReject,
    LoanRepaymentCreate, LoanSummary, LoanRepaymentSchedule
)
from app.services.base import CRUDBase
from app.core.exceptions import LoanError, InsufficientFundsError

class CRUDMicroLoan(CRUDBase[MicroLoan, MicroLoanCreate, MicroLoanUpdate]):
    """MicroLoan CRUD operations."""
    
    async def get_user_loans(
        self, db: AsyncSession, user_id: int, status: Optional[str] = None,
        skip: int = 0, limit: int = 100
    ) -> Tuple[List[MicroLoan], int]:
        """Get loans for a user with optional status filtering."""
        query = select(MicroLoan).filter(MicroLoan.user_id == user_id)
        if status:
            query = query.filter(MicroLoan.status == status)
        
        count = (await db.execute(select(func.count()).select_from(query.subquery()))).scalar()
        result = await db.execute(query.order_by(MicroLoan.created_at.desc()).offset(skip).limit(limit))
        return result.scalars().all(), count

    async def create_loan_application(
        self, db: AsyncSession, obj_in: MicroLoanCreate, user_id: int
    ) -> MicroLoan:
        """Create a new loan application."""
        existing_loans = await self.get_user_loans(db, user_id, status__in=["pending", "approved", "disbursed"])
        if existing_loans[1] > 0:
            raise LoanError("You already have an active or pending loan")
        
        db_obj = MicroLoan(
            **obj_in.dict(),
            user_id=user_id,
            status="pending",
            application_date=datetime.utcnow()
        )
        
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def approve_loan(
        self, db: AsyncSession, loan_id: int, approver_id: int, obj_in: MicroLoanApprove
    ) -> MicroLoan:
        """Approve a loan application."""
        loan = await self.get(db, id=loan_id)
        if not loan:
            raise LoanError("Loan not found")
        if loan.status != "pending":
            raise LoanError(f"Cannot approve a loan with status: {loan.status}")
        
        due_date = obj_in.disbursement_date + timedelta(days=obj_in.term_months * 30)
        loan.status = "approved"
        loan.approved_by = approver_id
        loan.approval_date = datetime.utcnow()
        loan.interest_rate = obj_in.interest_rate
        loan.term_months = obj_in.term_months
        loan.disbursement_date = obj_in.disbursement_date
        loan.due_date = due_date
        
        await db.commit()
        await db.refresh(loan)
        return loan

    async def create_repayment(
        self, db: AsyncSession, loan_id: int, user_id: int, obj_in: LoanRepaymentCreate
    ) -> LoanRepayment:
        """Create a loan repayment."""
        loan = await self.get(db, id=loan_id)
        if not loan or loan.user_id != user_id:
            raise LoanError("Loan not found")
        
        repayment = LoanRepayment(
            loan_id=loan_id,
            amount=obj_in.amount,
            payment_date=datetime.utcnow(),
            status="completed"
        )
        
        db.add(repayment)
        await db.commit()
        await db.refresh(repayment)
        return repayment

    async def get_loan_summary(self, db: AsyncSession, user_id: Optional[int] = None) -> LoanSummary:
        """Get loan summary statistics."""
        query = select(
            func.count(MicroLoan.id).label("total_loans"),
            func.sum(MicroLoan.amount).label("total_approved"),
            func.sum(
                case(
                    [(MicroLoan.status.in_(["disbursed", "repaid"]), MicroLoan.amount)],
                    else_=0
                )
            ).label("total_disbursed"),
            func.sum(
                case(
                    [(MicroLoan.status == "repaid", MicroLoan.amount)],
                    else_=0
                )
            ).label("total_repaid")
        )
        
        if user_id:
            query = query.filter(MicroLoan.user_id == user_id)
        
        result = await db.execute(query)
        row = result.first()
        
        return LoanSummary(
            total_loans=row.total_loans or 0,
            total_approved=Decimal(str(row.total_approved or 0)),
            total_disbursed=Decimal(str(row.total_disbursed or 0)),
            total_repaid=Decimal(str(row.total_repaid or 0)),
            total_outstanding=Decimal(str((row.total_disbursed or 0) - (row.total_repaid or 0)))
        )

# Create an instance of the service
microloan = CRUDMicroLoan(MicroLoan)
