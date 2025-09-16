from datetime import datetime, timedelta
from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app import models, schemas
from app.api import deps
from app.db.session import get_db
from app.services import crowdfunding as crowdfunding_service

router = APIRouter()

@router.get("/campaigns/", response_model=List[schemas.CrowdFundingCampaignResponse])
async def list_campaigns(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    List all crowdfunding campaigns with optional filtering by status.
    """
    campaigns = await crowdfunding_service.get_campaigns(
        db, skip=skip, limit=limit, status=status
    )
    return campaigns

@router.post("/campaigns/", response_model=schemas.CrowdFundingCampaignResponse, status_code=status.HTTP_201_CREATED)
async def create_campaign(
    *,
    db: AsyncSession = Depends(get_db),
    campaign_in: schemas.CrowdFundingCampaignCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create a new crowdfunding campaign.
    """
    # Verify end date is in the future
    if campaign_in.end_date <= datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="End date must be in the future",
        )
    
    # Create new campaign
    campaign = await crowdfunding_service.create_campaign(
        db, obj_in=campaign_in, created_by=current_user.id
    )
    return campaign

@router.get("/campaigns/{campaign_id}", response_model=schemas.CrowdFundingCampaignResponse)
async def get_campaign(
    campaign_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Get a specific crowdfunding campaign by ID.
    """
    campaign = await crowdfunding_service.get_campaign(db, campaign_id=campaign_id)
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found",
        )
    return campaign

@router.put("/campaigns/{campaign_id}", response_model=schemas.CrowdFundingCampaignResponse)
async def update_campaign(
    *,
    db: AsyncSession = Depends(get_db),
    campaign_id: int,
    campaign_in: schemas.CrowdFundingCampaignUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update a crowdfunding campaign.
    """
    campaign = await crowdfunding_service.get_campaign(db, campaign_id=campaign_id)
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found",
        )
    
    # Only campaign creator or admin can update
    if campaign.created_by != current_user.id and not deps.is_superuser(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to update this campaign",
        )
    
    # Prevent updating if campaign is already completed or cancelled
    if campaign.status in ["completed", "cancelled"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot update a {campaign.status} campaign",
        )
    
    # Update campaign
    campaign = await crowdfunding_service.update_campaign(
        db, db_obj=campaign, obj_in=campaign_in
    )
    return campaign

@router.post("/campaigns/{campaign_id}/donate", response_model=schemas.DonationResponse, status_code=status.HTTP_201_CREATED)
async def donate_to_campaign(
    *,
    db: AsyncSession = Depends(get_db),
    campaign_id: int,
    donation_in: schemas.DonationCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Donate to a crowdfunding campaign.
    """
    # Get campaign
    campaign = await crowdfunding_service.get_campaign(db, campaign_id=campaign_id)
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found",
        )
    
    # Check if campaign is active
    if campaign.status != "active":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot donate to a {campaign.status} campaign",
        )
    
    # Check if campaign has ended
    if campaign.end_date < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This campaign has already ended",
        )
    
    # Process donation
    donation = await crowdfunding_service.process_donation(
        db,
        campaign_id=campaign_id,
        donor_id=current_user.id,
        amount=donation_in.amount,
        message=donation_in.message,
        is_anonymous=donation_in.is_anonymous,
    )
    
    return donation

@router.get("/campaigns/{campaign_id}/donations", response_model=List[schemas.DonationResponse])
async def get_campaign_donations(
    campaign_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Get all donations for a specific campaign.
    """
    # Check if campaign exists
    campaign = await crowdfunding_service.get_campaign(db, campaign_id=campaign_id)
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found",
        )
    
    # Get donations
    donations = await crowdfunding_service.get_campaign_donations(
        db, campaign_id=campaign_id
    )
    
    # Filter out anonymous donations if user is not admin or campaign creator
    if not deps.is_superuser(current_user) and campaign.created_by != current_user.id:
        donations = [d for d in donations if not d.is_anonymous]
    
    return donations

@router.get("/my-donations", response_model=List[schemas.DonationWithCampaignResponse])
async def get_my_donations(
    current_user: models.User = Depends(deps.get_current_active_user),
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Get all donations made by the current user.
    """
    donations = await crowdfunding_service.get_user_donations(
        db, user_id=current_user.id, skip=skip, limit=limit
    )
    return donations

@router.get("/my-campaigns", response_model=List[schemas.CrowdFundingCampaignResponse])
async def get_my_campaigns(
    current_user: models.User = Depends(deps.get_current_active_user),
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Get all campaigns created by the current user.
    """
    campaigns = await crowdfunding_service.get_user_campaigns(
        db, user_id=current_user.id, skip=skip, limit=limit
    )
    return campaigns

@router.post("/campaigns/{campaign_id}/complete", response_model=schemas.CrowdFundingCampaignResponse)
async def complete_campaign(
    *,
    db: AsyncSession = Depends(get_db),
    campaign_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Mark a campaign as completed (campaign creator or admin only).
    """
    campaign = await crowdfunding_service.get_campaign(db, campaign_id=campaign_id)
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found",
        )
    
    # Only campaign creator or admin can complete
    if campaign.created_by != current_user.id and not deps.is_superuser(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to complete this campaign",
        )
    
    # Update campaign status to completed
    campaign = await crowdfunding_service.update_campaign_status(
        db, campaign_id=campaign_id, status="completed"
    )
    
    return campaign
