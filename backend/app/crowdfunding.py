"""
Crowdfunding API endpoints
"""

from datetime import datetime, timedelta
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from pydantic import BaseModel

from app.database import Campaign, Contribution, get_db
from app.auth import get_current_user

router = APIRouter()

class CampaignCreate(BaseModel):
    title: str
    description: str
    goal_amount: float
    category: str
    end_date: datetime

class CampaignResponse(BaseModel):
    id: int
    title: str
    description: str
    goal_amount: float
    current_amount: float
    category: str
    end_date: datetime
    created_at: datetime
    creator_name: str

    class Config:
        from_attributes = True

class ContributionCreate(BaseModel):
    campaign_id: int
    amount: float
    message: str = None

@router.get("/", response_model=List[CampaignResponse])
async def get_campaigns(db: Session = Depends(get_db)):
    """Get all active campaigns"""

    campaigns = db.query(Campaign).filter(
        Campaign.end_date > datetime.now()
    ).all()

    # Add creator names
    for campaign in campaigns:
        campaign.creator_name = campaign.creator.full_name or campaign.creator.username

    return campaigns

@router.get("/featured")
async def get_featured_campaigns(db: Session = Depends(get_db)):
    """Get featured campaigns (most funded, ending soon)"""

    # Most funded campaigns
    most_funded = db.query(Campaign).filter(
        Campaign.end_date > datetime.now()
    ).order_by(desc(Campaign.current_amount / Campaign.goal_amount)).limit(3).all()

    # Campaigns ending soon
    ending_soon = db.query(Campaign).filter(
        Campaign.end_date > datetime.now(),
        Campaign.end_date <= datetime.now() + timedelta(days=7)
    ).order_by(Campaign.end_date).limit(3).all()

    return {
        "most_funded": most_funded,
        "ending_soon": ending_soon
    }

@router.post("/", response_model=CampaignResponse)
async def create_campaign(
    campaign_data: CampaignCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new crowdfunding campaign"""

    # Validate goal amount
    if campaign_data.goal_amount <= 0:
        raise HTTPException(status_code=400, detail="Goal amount must be positive")

    # Validate end date
    if campaign_data.end_date <= datetime.now():
        raise HTTPException(status_code=400, detail="End date must be in the future")

    # Create campaign
    new_campaign = Campaign(
        creator_id=current_user.id,
        title=campaign_data.title,
        description=campaign_data.description,
        goal_amount=campaign_data.goal_amount,
        current_amount=0.0,
        category=campaign_data.category,
        end_date=campaign_data.end_date
    )

    db.add(new_campaign)
    db.commit()
    db.refresh(new_campaign)

    new_campaign.creator_name = current_user.full_name or current_user.username

    return new_campaign

@router.get("/{campaign_id}")
async def get_campaign(
    campaign_id: int,
    db: Session = Depends(get_db)
):
    """Get campaign details with contributions"""

    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    contributions = db.query(Contribution).filter(
        Contribution.campaign_id == campaign_id
    ).order_by(desc(Contribution.created_at)).all()

    # Calculate progress
    progress = (campaign.current_amount / campaign.goal_amount) * 100 if campaign.goal_amount > 0 else 0

    return {
        "campaign": campaign,
        "contributions": contributions,
        "progress": progress,
        "days_remaining": (campaign.end_date - datetime.now()).days
    }

@router.post("/{campaign_id}/contribute")
async def contribute_to_campaign(
    campaign_id: int,
    contribution_data: ContributionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Contribute to a campaign"""

    # Get campaign
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    # Check if campaign is still active
    if campaign.end_date <= datetime.now():
        raise HTTPException(status_code=400, detail="Campaign has ended")

    # Validate amount
    if contribution_data.amount <= 0:
        raise HTTPException(status_code=400, detail="Contribution amount must be positive")

    # Create contribution
    contribution = Contribution(
        user_id=current_user.id,
        campaign_id=campaign_id,
        amount=contribution_data.amount,
        message=contribution_data.message
    )

    # Update campaign current amount
    campaign.current_amount += contribution_data.amount

    db.add(contribution)
    db.commit()
    db.refresh(campaign)

    return {
        "message": "Contribution successful",
        "campaign": campaign,
        "contribution": contribution
    }

@router.get("/categories")
async def get_campaign_categories():
    """Get available campaign categories"""

    return [
        "education", "healthcare", "housing", "food_security",
        "business_startup", "emergency_relief", "community_development",
        "environmental", "other"
    ]
