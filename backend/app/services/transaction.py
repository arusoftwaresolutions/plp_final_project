from datetime import datetime, date
from typing import List, Optional, Union, Tuple, Dict, Any
from decimal import Decimal
from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Transaction, User, TransactionCategory, TransactionType
from app.schemas.transaction import (
    TransactionCreate, 
    TransactionUpdate, 
    TransactionSummary,
    TransactionFilter,
    TransactionCategoryCreate,
    TransactionCategoryUpdate
)
from app.services.base import CRUDBase
from app.core.exceptions import (
    InsufficientFundsError,
    TransactionError
)

class CRUDTransaction(CRUDBase[Transaction, TransactionCreate, TransactionUpdate]):
    """
    Transaction CRUD operations.
    """
    
    async def get_user_transactions(
        self, 
        db: AsyncSession, 
        user_id: int,
        skip: int = 0, 
        limit: int = 100,
        filters: Optional[TransactionFilter] = None
    ) -> Tuple[List[Transaction], int]:
        """
        Get transactions for a specific user with optional filtering and pagination.
        
        Args:
            db: Database session
            user_id: ID of the user
            skip: Number of records to skip
            limit: Maximum number of records to return
            filters: Optional filters to apply
            
        Returns:
            Tuple containing list of transactions and total count
        """
        # Start building the query
        query = select(Transaction).filter(Transaction.user_id == user_id)
        
        # Apply filters if provided
        if filters:
            if filters.type:
                query = query.filter(Transaction.type == filters.type)
                
            if filters.category_id:
                query = query.filter(Transaction.category_id == filters.category_id)
                
            if filters.min_amount is not None:
                query = query.filter(Transaction.amount >= filters.min_amount)
                
            if filters.max_amount is not None:
                query = query.filter(Transaction.amount <= filters.max_amount)
                
            if filters.start_date:
                query = query.filter(Transaction.transaction_date >= filters.start_date)
                
            if filters.end_date:
                # Include transactions on the end date
                end_date = datetime.combine(filters.end_date, datetime.max.time())
                query = query.filter(Transaction.transaction_date <= end_date)
                
            if filters.description:
                query = query.filter(
                    Transaction.description.ilike(f"%{filters.description}%")
                )
        
        # Get total count for pagination
        count_query = select(func.count()).select_from(query.subquery())
        total = (await db.execute(count_query)).scalar()
        
        # Apply ordering and pagination
        query = query.order_by(Transaction.transaction_date.desc())
        query = query.offset(skip).limit(limit)
        
        # Execute the query
        result = await db.execute(query)
        transactions = result.scalars().all()
        
        return transactions, total
    
    async def get_summary(
        self, 
        db: AsyncSession, 
        user_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> TransactionSummary:
        """
        Get a summary of transactions for a user.
        
        Args:
            db: Database session
            user_id: ID of the user
            start_date: Optional start date for filtering
            end_date: Optional end date for filtering
            
        Returns:
            TransactionSummary: Summary of transactions
        """
        # Start building the query
        query = select(
            Transaction.type,
            func.sum(Transaction.amount).label("total_amount"),
            func.count().label("count"),
            Transaction.currency
        ).filter(Transaction.user_id == user_id)
        
        # Apply date filters if provided
        if start_date:
            query = query.filter(Transaction.transaction_date >= start_date)
            
        if end_date:
            end_date = datetime.combine(end_date, datetime.max.time())
            query = query.filter(Transaction.transaction_date <= end_date)
        
        # Group by transaction type and currency
        query = query.group_by(Transaction.type, Transaction.currency)
        
        # Execute the query
        result = await db.execute(query)
        rows = result.all()
        
        # Initialize summary
        summary = TransactionSummary(
            total_income=Decimal('0.00'),
            total_expenses=Decimal('0.00'),
            net_balance=Decimal('0.00'),
            transaction_count=0,
            by_category={},
            by_currency={}
        )
        
        # Process the results
        for row in rows:
            trans_type, amount, count, currency = row
            amount = Decimal(str(amount))  # Convert to Decimal for precision
            
            # Update totals by type
            if trans_type == TransactionType.INCOME:
                summary.total_income += amount
            elif trans_type == TransactionType.EXPENSE:
                summary.total_expenses += amount
            
            # Update currency summary
            if currency not in summary.by_currency:
                summary.by_currency[currency] = {
                    'income': Decimal('0.00'),
                    'expenses': Decimal('0.00'),
                    'net': Decimal('0.00')
                }
            
            if trans_type == TransactionType.INCOME:
                summary.by_currency[currency]['income'] += amount
                summary.by_currency[currency]['net'] += amount
            else:
                summary.by_currency[currency]['expenses'] += amount
                summary.by_currency[currency]['net'] -= amount
            
            summary.transaction_count += count
        
        # Calculate net balance
        summary.net_balance = summary.total_income - summary.total_expenses
        
        # Get category breakdown
        category_query = select(
            TransactionCategory.name,
            Transaction.type,
            func.sum(Transaction.amount).label("total_amount"),
            func.count().label("count")
        ).join(
            Transaction.category
        ).filter(
            Transaction.user_id == user_id
        )
        
        # Apply date filters to category query
        if start_date:
            category_query = category_query.filter(Transaction.transaction_date >= start_date)
            
        if end_date:
            end_date = datetime.combine(end_date, datetime.max.time())
            category_query = category_query.filter(Transaction.transaction_date <= end_date)
        
        category_query = category_query.group_by(TransactionCategory.name, Transaction.type)
        
        # Execute category query
        category_result = await db.execute(category_query)
        
        # Process category results
        for name, trans_type, amount, count in category_result.all():
            amount = Decimal(str(amount))
            
            if name not in summary.by_category:
                summary.by_category[name] = {
                    'income': Decimal('0.00'),
                    'expenses': Decimal('0.00'),
                    'net': Decimal('0.00'),
                    'count': 0
                }
            
            if trans_type == TransactionType.INCOME:
                summary.by_category[name]['income'] += amount
                summary.by_category[name]['net'] += amount
            else:
                summary.by_category[name]['expenses'] += amount
                summary.by_category[name]['net'] -= amount
            
            summary.by_category[name]['count'] += count
        
        return summary
    
    async def create(
        self, 
        db: AsyncSession, 
        *, 
        obj_in: TransactionCreate,
        user_id: int
    ) -> Transaction:
        """
        Create a new transaction for a user.
        """
        # Check if category exists
        category = await db.get(TransactionCategory, obj_in.category_id)
        if not category:
            raise TransactionError("Category not found")
        
        # Create the transaction
        db_obj = Transaction(
            **obj_in.dict(exclude={"id"}),
            user_id=user_id
        )
        
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        
        # Update user balance if needed
        if category.affects_balance:
            user = await db.get(User, user_id)
            if not user:
                raise TransactionError("User not found")
                
            if db_obj.type == TransactionType.INCOME:
                user.balance += db_obj.amount
            else:
                if user.balance < db_obj.amount and not user.allow_negative_balance:
                    await db.rollback()
                    raise InsufficientFundsError("Insufficient funds")
                user.balance -= db_obj.amount
            
            await db.commit()
        
        return db_obj
    
    async def update(
        self, 
        db: AsyncSession, 
        *, 
        db_obj: Transaction, 
        obj_in: Union[TransactionUpdate, Dict[str, Any]]
    ) -> Transaction:
        """
        Update a transaction.
        """
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        
        # Store old values for balance adjustment
        old_amount = db_obj.amount
        old_type = db_obj.type
        old_category_id = db_obj.category_id
        
        # Get the old category
        old_category = await db.get(TransactionCategory, old_category_id)
        
        # Update the transaction
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        
        db.add(db_obj)
        
        # If amount, type, or category changed and affects balance, update user balance
        if any(field in update_data for field in ["amount", "type", "category_id"]):
            user = await db.get(User, db_obj.user_id)
            if not user:
                await db.rollback()
                raise TransactionError("User not found")
            
            # Get the new category
            new_category = await db.get(TransactionCategory, db_obj.category_id)
            if not new_category:
                await db.rollback()
                raise TransactionError("Category not found")
            
            # If old category affected balance, reverse its effect
            if old_category and old_category.affects_balance:
                if old_type == TransactionType.INCOME:
                    user.balance -= old_amount
                else:
                    user.balance += old_amount
            
            # If new category affects balance, apply its effect
            if new_category.affects_balance:
                if db_obj.type == TransactionType.INCOME:
                    user.balance += db_obj.amount
                else:
                    if user.balance < db_obj.amount and not user.allow_negative_balance:
                        await db.rollback()
                        raise InsufficientFundsError("Insufficient funds")
                    user.balance -= db_obj.amount
        
        await db.commit()
        await db.refresh(db_obj)
        
        return db_obj
    
    async def delete(self, db: AsyncSession, *, id: int, user_id: int) -> Transaction:
        """
        Delete a transaction and adjust user balance if needed.
        """
        # Get the transaction with the category loaded
        result = await db.execute(
            select(Transaction).options(selectinload(Transaction.category))
            .filter(and_(Transaction.id == id, Transaction.user_id == user_id))
        )
        db_obj = result.scalars().first()
        
        if not db_obj:
            raise TransactionError("Transaction not found")
        
        # If category affects balance, adjust user balance
        if db_obj.category.affects_balance:
            user = await db.get(User, user_id)
            if not user:
                raise TransactionError("User not found")
                
            if db_obj.type == TransactionType.INCOME:
                if user.balance < db_obj.amount and not user.allow_negative_balance:
                    raise InsufficientFundsError("Cannot delete transaction: insufficient funds")
                user.balance -= db_obj.amount
            else:
                user.balance += db_obj.amount
            
            await db.commit()
        
        # Now delete the transaction
        await db.delete(db_obj)
        await db.commit()
        
        return db_obj

class CRUDTransactionCategory(CRUDBase[TransactionCategory, TransactionCategoryCreate, TransactionCategoryUpdate]):
    """
    Transaction Category CRUD operations.
    """
    
    async def get_user_categories(
        self, 
        db: AsyncSession, 
        user_id: int,
        type: Optional[TransactionType] = None,
        include_system: bool = False
    ) -> List[TransactionCategory]:
        """
        Get transaction categories for a user.
        
        Args:
            db: Database session
            user_id: ID of the user
            type: Optional transaction type to filter by
            include_system: Whether to include system categories
            
        Returns:
            List of transaction categories
        """
        query = select(TransactionCategory).filter(
            or_(
                TransactionCategory.user_id == user_id,
                TransactionCategory.is_system == True
            )
        )
        
        if type:
            query = query.filter(TransactionCategory.type == type)
            
        if not include_system:
            query = query.filter(TransactionCategory.is_system == False)
        
        result = await db.execute(query)
        return result.scalars().all()
    
    async def get_default_categories(
        self, 
        db: AsyncSession
    ) -> List[TransactionCategory]:
        """
        Get default system categories.
        """
        result = await db.execute(
            select(TransactionCategory)
            .filter(TransactionCategory.is_system == True)
        )
        return result.scalars().all()
    
    async def create_default_categories(
        self, 
        db: AsyncSession,
        user_id: int
    ) -> None:
        """
        Create default categories for a user.
        """
        default_categories = [
            # Income categories
            {"name": "Salary", "type": TransactionType.INCOME, "is_system": False, "icon": "💼"},
            {"name": "Freelance", "type": TransactionType.INCOME, "is_system": False, "icon": "💻"},
            {"name": "Investments", "type": TransactionType.INCOME, "is_system": False, "icon": "📈"},
            {"name": "Gift", "type": TransactionType.INCOME, "is_system": False, "icon": "🎁"},
            {"name": "Other Income", "type": TransactionType.INCOME, "is_system": True, "icon": "💰"},
            
            # Expense categories
            {"name": "Housing", "type": TransactionType.EXPENSE, "is_system": False, "icon": "🏠"},
            {"name": "Food", "type": TransactionType.EXPENSE, "is_system": False, "icon": "🍔"},
            {"name": "Transportation", "type": TransactionType.EXPENSE, "is_system": False, "icon": "🚗"},
            {"name": "Utilities", "type": TransactionType.EXPENSE, "is_system": False, "icon": "💡"},
            {"name": "Healthcare", "type": TransactionType.EXPENSE, "is_system": False, "icon": "🏥"},
            {"name": "Entertainment", "type": TransactionType.EXPENSE, "is_system": False, "icon": "🎬"},
            {"name": "Education", "type": TransactionType.EXPENSE, "is_system": False, "icon": "📚"},
            {"name": "Shopping", "type": TransactionType.EXPENSE, "is_system": False, "icon": "🛍️"},
            {"name": "Other Expense", "type": TransactionType.EXPENSE, "is_system": True, "icon": "💸"},
        ]
        
        for category_data in default_categories:
            category = TransactionCategory(
                **category_data,
                user_id=user_id if not category_data["is_system"] else None,
                affects_balance=True
            )
            db.add(category)
        
        await db.commit()

# Create instances of the services
transaction = CRUDTransaction(Transaction)
transaction_category = CRUDTransactionCategory(TransactionCategory)
