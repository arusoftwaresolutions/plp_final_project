from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from models import UserType, TransactionType, LoanStatus, CampaignStatus

# User schemas
class UserBase(BaseModel):
    email: str
    full_name: str
    user_type: UserType

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class User(UserBase):
    id: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

# Family schemas
class FamilyProfileBase(BaseModel):
    family_size: int
    monthly_income: float
    location: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class FamilyProfileCreate(FamilyProfileBase):
    pass

class FamilyProfile(FamilyProfileBase):
    id: str
    user_id: str
    created_at: datetime
    
    class Config:
        from_attributes = True

# Transaction schemas
class TransactionBase(BaseModel):
    amount: float
    transaction_type: TransactionType
    category: str
    description: Optional[str] = None

class TransactionCreate(TransactionBase):
    pass

class Transaction(TransactionBase):
    id: str
    family_id: str
    date: datetime
    
    class Config:
        from_attributes = True

# Campaign schemas
class CampaignBase(BaseModel):
    title: str
    description: str
    target_amount: float

class CampaignCreate(CampaignBase):
    pass

class Campaign(CampaignBase):
    id: str
    current_amount: float
    status: CampaignStatus
    family_id: str
    created_at: datetime
    
    class Config:
        from_attributes = True

# Donation schemas
class DonationBase(BaseModel):
    amount: float
    is_anonymous: bool = False

class DonationCreate(DonationBase):
    campaign_id: str

class Donation(DonationBase):
    id: str
    donor_id: str
    campaign_id: str
    created_at: datetime
    
    class Config:
        from_attributes = True

# Business schemas
class BusinessProfileBase(BaseModel):
    business_name: str
    business_type: str
    annual_revenue: float
    location: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class BusinessProfileCreate(BusinessProfileBase):
    pass

class BusinessProfile(BusinessProfileBase):
    id: str
    user_id: str
    created_at: datetime
    
    class Config:
        from_attributes = True

# Loan schemas
class LoanApplicationBase(BaseModel):
    amount: float
    purpose: str

class LoanApplicationCreate(LoanApplicationBase):
    pass

class LoanApplicationUpdate(BaseModel):
    status: LoanStatus
    admin_notes: Optional[str] = None

class LoanApplication(LoanApplicationBase):
    id: str
    business_id: str
    status: LoanStatus
    admin_notes: Optional[str] = None
    created_at: datetime
    reviewed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# AI schemas
class AIRecommendationBase(BaseModel):
    recommendation_type: str
    title: str
    description: str
    priority: str

class AIRecommendation(AIRecommendationBase):
    id: str
    family_id: str
    is_read: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# Geospatial schemas
class PovertyHotspotBase(BaseModel):
    name: str
    latitude: float
    longitude: float
    poverty_rate: float
    population: int
    description: Optional[str] = None

class PovertyHotspot(PovertyHotspotBase):
    id: str
    created_at: datetime
    
    class Config:
        from_attributes = True

# Dashboard schemas
class DashboardStats(BaseModel):
    total_income: float
    total_expenses: float
    net_income: float
    transaction_count: int
    recent_transactions: List[Transaction]
    ai_recommendations: List[AIRecommendation]
