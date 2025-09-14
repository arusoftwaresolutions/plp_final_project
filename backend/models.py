from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import enum
import uuid

class UserType(str, enum.Enum):
    FAMILY = "family"
    DONOR = "donor"
    BUSINESS = "business"
    ADMIN = "admin"

class TransactionType(str, enum.Enum):
    INCOME = "income"
    EXPENSE = "expense"

class LoanStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    COMPLETED = "completed"

class CampaignStatus(str, enum.Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    user_type = Column(SQLEnum(UserType), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    family_profile = relationship("FamilyProfile", back_populates="user", uselist=False)
    donor_profile = relationship("DonorProfile", back_populates="user", uselist=False)
    business_profile = relationship("BusinessProfile", back_populates="user", uselist=False)

class FamilyProfile(Base):
    __tablename__ = "family_profiles"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    family_size = Column(Integer, nullable=False)
    monthly_income = Column(Float, nullable=False)
    location = Column(String, nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User", back_populates="family_profile")
    transactions = relationship("Transaction", back_populates="family")
    ai_recommendations = relationship("AIRecommendation", back_populates="family")

class DonorProfile(Base):
    __tablename__ = "donor_profiles"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    total_donated = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User", back_populates="donor_profile")
    donations = relationship("Donation", back_populates="donor")

class BusinessProfile(Base):
    __tablename__ = "business_profiles"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    business_name = Column(String, nullable=False)
    business_type = Column(String, nullable=False)
    annual_revenue = Column(Float, nullable=False)
    location = Column(String, nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User", back_populates="business_profile")
    loan_applications = relationship("LoanApplication", back_populates="business")

class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    family_id = Column(String, ForeignKey("family_profiles.id"), nullable=False)
    amount = Column(Float, nullable=False)
    transaction_type = Column(SQLEnum(TransactionType), nullable=False)
    category = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    date = Column(DateTime(timezone=True), server_default=func.now())
    
    family = relationship("FamilyProfile", back_populates="transactions")

class Campaign(Base):
    __tablename__ = "campaigns"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    target_amount = Column(Float, nullable=False)
    current_amount = Column(Float, default=0.0)
    status = Column(SQLEnum(CampaignStatus), default=CampaignStatus.ACTIVE)
    family_id = Column(String, ForeignKey("family_profiles.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    donations = relationship("Donation", back_populates="campaign")

class Donation(Base):
    __tablename__ = "donations"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    donor_id = Column(String, ForeignKey("donor_profiles.id"), nullable=False)
    campaign_id = Column(String, ForeignKey("campaigns.id"), nullable=False)
    amount = Column(Float, nullable=False)
    is_anonymous = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    donor = relationship("DonorProfile", back_populates="donations")
    campaign = relationship("Campaign", back_populates="donations")

class LoanApplication(Base):
    __tablename__ = "loan_applications"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    business_id = Column(String, ForeignKey("business_profiles.id"), nullable=False)
    amount = Column(Float, nullable=False)
    purpose = Column(Text, nullable=False)
    status = Column(SQLEnum(LoanStatus), default=LoanStatus.PENDING)
    admin_notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    
    business = relationship("BusinessProfile", back_populates="loan_applications")

class AIRecommendation(Base):
    __tablename__ = "ai_recommendations"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    family_id = Column(String, ForeignKey("family_profiles.id"), nullable=False)
    recommendation_type = Column(String, nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    priority = Column(String, nullable=False)  # high, medium, low
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    family = relationship("FamilyProfile", back_populates="ai_recommendations")

class PovertyHotspot(Base):
    __tablename__ = "poverty_hotspots"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    poverty_rate = Column(Float, nullable=False)
    population = Column(Integer, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
