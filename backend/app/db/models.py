from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Enum, Text, Table, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum
from typing import List, Optional

from .session import Base

# Association tables
user_roles = Table(
    'user_roles',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('role_id', Integer, ForeignKey('roles.id'))
)

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(200), nullable=False)
    full_name = Column(String(100), nullable=True)
    phone_number = Column(String(20), nullable=True)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    roles = relationship("Role", secondary=user_roles, back_populates="users")
    transactions = relationship("Transaction", back_populates="user")
    microloans = relationship("MicroLoan", back_populates="user")
    donations = relationship("Donation", back_populates="donor")
    notifications = relationship(
        "Notification", 
        back_populates="user",
        cascade="all, delete-orphan"
    )
    notification_preferences = relationship(
        "UserNotificationPreference", 
        back_populates="user",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self):
        return f"<User {self.username}>"

class Role(Base):
    __tablename__ = "roles"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, index=True, nullable=False)
    description = Column(String(200), nullable=True)
    
    # Relationships
    users = relationship("User", secondary=user_roles, back_populates="roles")
    
    def __repr__(self):
        return f"<Role {self.name}>"

class TransactionType(str, enum.Enum):
    INCOME = "income"
    EXPENSE = "expense"
    SAVINGS = "savings"
    LOAN = "loan"
    DONATION = "donation"

class TransactionCategory(str, enum.Enum):
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

class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    amount = Column(Float, nullable=False)
    transaction_type = Column(Enum(TransactionType), nullable=False)
    category = Column(Enum(TransactionCategory), nullable=False)
    description = Column(String(200), nullable=True)
    date = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="transactions")
    
    def __repr__(self):
        return f"<Transaction {self.id}: {self.amount} {self.transaction_type}>"

class LoanStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    DISBURSED = "disbursed"
    REPAID = "repaid"
    DEFAULTED = "defaulted"

class MicroLoan(Base):
    __tablename__ = "microloans"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    amount = Column(Float, nullable=False)
    purpose = Column(String(200), nullable=False)
    status = Column(Enum(LoanStatus), default=LoanStatus.PENDING)
    interest_rate = Column(Float, default=0.1)  # 10% interest rate
    term_months = Column(Integer, default=12)  # 12 months term
    disbursement_date = Column(DateTime(timezone=True), nullable=True)
    due_date = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="microloans")
    repayments = relationship("LoanRepayment", back_populates="loan")
    
    def __repr__(self):
        return f"<MicroLoan {self.id}: {self.amount} ({self.status})>"

class LoanRepayment(Base):
    __tablename__ = "loan_repayments"
    
    id = Column(Integer, primary_key=True, index=True)
    loan_id = Column(Integer, ForeignKey("microloans.id"), nullable=False)
    amount = Column(Float, nullable=False)
    payment_date = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(String(20), default="pending")  # pending, completed, failed
    transaction_id = Column(Integer, ForeignKey("transactions.id"), nullable=True)
    
    # Relationships
    loan = relationship("MicroLoan", back_populates="repayments")
    
    def __repr__(self):
        return f"<LoanRepayment {self.id}: {self.amount} for Loan {self.loan_id}>"

class CrowdFundingCampaign(Base):
    __tablename__ = "crowdfunding_campaigns"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    target_amount = Column(Float, nullable=False)
    amount_raised = Column(Float, default=0.0)
    start_date = Column(DateTime(timezone=True), server_default=func.now())
    end_date = Column(DateTime(timezone=True), nullable=False)
    status = Column(String(20), default="active")  # active, completed, cancelled
    image_url = Column(String(500), nullable=True)
    location = Column(JSON, nullable=True)  # {lat: x, lng: y, address: ""}
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    donations = relationship("Donation", back_populates="campaign")
    
    def __repr__(self):
        return f"<CrowdFundingCampaign {self.id}: {self.title}>"

class Donation(Base):
    __tablename__ = "donations"
    
    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("crowdfunding_campaigns.id"), nullable=False)
    donor_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Can be anonymous
    amount = Column(Float, nullable=False)
    message = Column(Text, nullable=True)
    is_anonymous = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    campaign = relationship("CrowdFundingCampaign", back_populates="donations")
    donor = relationship("User", back_populates="donations")
    
    def __repr__(self):
        return f"<Donation {self.id}: {self.amount} to Campaign {self.campaign_id}>"

class PovertyArea(Base):
    __tablename__ = "poverty_areas"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    location = Column(JSON, nullable=False)  # {lat: x, lng: y, address: ""}
    poverty_rate = Column(Float)  # Percentage of population below poverty line
    population = Column(Integer, nullable=True)
    needs = Column(JSON, nullable=True)  # List of needs ["education", "healthcare", "food"]
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<PovertyArea {self.id}: {self.name} ({self.poverty_rate}%)>"

class NotificationType(str, enum.Enum):
    NEW_CAMPAIGN = "new_campaign"
    NEW_DONATION = "new_donation"
    NEW_LOAN = "new_loan"
    LOAN_REPAID = "loan_repaid"
    LOAN_DEFAULTED = "loan_defaulted"

class Notification(Base):
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    notification_type = Column(Enum(NotificationType), nullable=False)
    message = Column(String(200), nullable=False)
    read = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="notifications")
    
    def __repr__(self):
        return f"<Notification {self.id}: {self.message}>"

class UserNotificationPreference(Base):
    __tablename__ = "user_notification_preferences"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    notification_type = Column(Enum(NotificationType), nullable=False)
    enabled = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="notification_preferences")
    
    def __repr__(self):
        return f"<UserNotificationPreference {self.id}: {self.notification_type} for User {self.user_id}>"
