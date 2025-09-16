from pydantic import BaseModel, Field, HttpUrl, validator
from datetime import datetime, date
from typing import Optional, List, Dict, Any
from enum import Enum

class CampaignStatus(str, Enum):
    """
    Campaign status enumeration.
    """
    DRAFT = "draft"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class CampaignBase(BaseModel):
    """
    Base crowdfunding campaign schema.
    """
    title: str = Field(..., max_length=200, description="Campaign title")
    description: str = Field(..., description="Detailed description of the campaign")
    target_amount: float = Field(..., gt=0, description="Funding target amount")
    start_date: datetime = Field(default_factory=datetime.utcnow)
    end_date: datetime = Field(..., description="Campaign end date and time")
    image_url: Optional[HttpUrl] = Field(None, description="URL of the campaign image")
    location: Optional[Dict[str, Any]] = Field(None, description="Geolocation data for the campaign")

class CampaignCreate(CampaignBase):
    """
    Schema for creating a new crowdfunding campaign.
    """
    @validator('end_date')
    def validate_end_date(cls, v, values):
        if 'start_date' in values and v <= values['start_date']:
            raise ValueError('End date must be after start date')
        if v.date() < date.today():
            raise ValueError('End date cannot be in the past')
        return v

class CampaignUpdate(BaseModel):
    """
    Schema for updating a crowdfunding campaign.
    """
    title: Optional[str] = Field(None, max_length=200, description="Campaign title")
    description: Optional[str] = Field(None, description="Detailed description of the campaign")
    target_amount: Optional[float] = Field(None, gt=0, description="Funding target amount")
    end_date: Optional[datetime] = Field(None, description="Campaign end date and time")
    image_url: Optional[HttpUrl] = Field(None, description="URL of the campaign image")
    location: Optional[Dict[str, Any]] = Field(None, description="Geolocation data for the campaign")
    status: Optional[CampaignStatus] = None

class CampaignInDBBase(CampaignBase):
    """
    Base schema for campaign stored in DB.
    """
    id: int
    created_by: int
    amount_raised: float = 0.0
    status: CampaignStatus = CampaignStatus.DRAFT
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True

class CampaignResponse(CampaignInDBBase):
    """
    Campaign response schema.
    """
    progress_percentage: float = 0.0
    days_remaining: Optional[int] = None
    donor_count: int = 0
    is_owner: bool = False

class DonationBase(BaseModel):
    """
    Base donation schema.
    """
    amount: float = Field(..., gt=0, description="Donation amount (must be greater than 0)")
    message: Optional[str] = Field(None, max_length=500, description="Optional message from donor")
    is_anonymous: bool = Field(False, description="Whether the donation is anonymous")

class DonationCreate(DonationBase):
    """
    Schema for creating a new donation.
    """
    campaign_id: int = Field(..., description="ID of the campaign to donate to")

class DonationInDBBase(DonationBase):
    """
    Base schema for donation stored in DB.
    """
    id: int
    campaign_id: int
    donor_id: Optional[int] = None
    created_at: datetime
    
    class Config:
        orm_mode = True

class DonationResponse(DonationInDBBase):
    """
    Donation response schema.
    """
    donor_name: Optional[str] = None
    campaign_title: Optional[str] = None

class DonationWithCampaignResponse(DonationInDBBase):
    """
    Donation response with campaign details.
    """
    campaign: Optional[CampaignResponse] = None
    donor_name: Optional[str] = None

class CampaignWithDonationsResponse(CampaignResponse):
    """
    Campaign response with donations.
    """
    donations: List[DonationResponse] = []

class CampaignStats(BaseModel):
    """
    Campaign statistics schema.
    """
    total_campaigns: int = 0
    active_campaigns: int = 0
    completed_campaigns: int = 0
    total_raised: float = 0.0
    total_donors: int = 0
    avg_donation: float = 0.0

class DonorLeaderboard(BaseModel):
    """
    Donor leaderboard entry schema.
    """
    donor_id: int
    donor_name: str
    total_donated: float
    donation_count: int
    last_donation: datetime
    
    class Config:
        orm_mode = True

class CampaignSearchFilter(BaseModel):
    """
    Campaign search filter schema.
    """
    status: Optional[CampaignStatus] = None
    min_amount: Optional[float] = None
    max_amount: Optional[float] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    location: Optional[Dict[str, Any]] = None
    search_query: Optional[str] = None
    
    @validator('max_amount')
    def validate_amounts(cls, v, values):
        if 'min_amount' in values and values['min_amount'] is not None and v is not None:
            if values['min_amount'] > v:
                raise ValueError('Minimum amount cannot be greater than maximum amount')
        return v
    
    @validator('end_date')
    def validate_dates(cls, v, values):
        if 'start_date' in values and values['start_date'] is not None and v is not None:
            if values['start_date'] > v:
                raise ValueError('Start date cannot be after end date')
        return v
