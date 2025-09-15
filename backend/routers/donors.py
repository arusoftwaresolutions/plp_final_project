from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import User, DonorProfile, Campaign, Donation
from schemas import (
    DonationCreate, Donation as DonationSchema,
    Campaign as CampaignSchema
)
from auth import get_current_user
from typing import List

router = APIRouter()

@router.get("/campaigns", response_model=List[CampaignSchema])
def get_all_campaigns(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    campaigns = db.query(Campaign).filter(Campaign.status == "active").offset(skip).limit(limit).all()
    return campaigns

@router.get("/campaigns/{campaign_id}", response_model=CampaignSchema)
def get_campaign(
    campaign_id: str,
    db: Session = Depends(get_db)
):
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    return campaign

@router.post("/donate", response_model=DonationSchema)
def make_donation(
    donation: DonationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.user_type != "donor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only donor users can make donations"
        )
    
    # Get donor profile
    donor_profile = db.query(DonorProfile).filter(DonorProfile.user_id == current_user.id).first()
    if not donor_profile:
        # Create donor profile if it doesn't exist
        donor_profile = DonorProfile(user_id=current_user.id)
        db.add(donor_profile)
        db.commit()
        db.refresh(donor_profile)
    
    # Verify campaign exists
    campaign = db.query(Campaign).filter(Campaign.id == donation.campaign_id).first()
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    
    # Create donation
    db_donation = Donation(
        donor_id=donor_profile.id,
        campaign_id=donation.campaign_id,
        amount=donation.amount,
        is_anonymous=donation.is_anonymous
    )
    db.add(db_donation)
    
    # Update campaign current amount
    campaign.current_amount += donation.amount
    
    # Update donor total donated
    donor_profile.total_donated += donation.amount
    
    db.commit()
    db.refresh(db_donation)
    
    return db_donation

@router.get("/my-donations", response_model=List[DonationSchema])
def get_my_donations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.user_type != "donor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only donor users can access donations"
        )
    
    donor_profile = db.query(DonorProfile).filter(DonorProfile.user_id == current_user.id).first()
    if not donor_profile:
        return []
    
    donations = db.query(Donation).filter(Donation.donor_id == donor_profile.id).all()
    return donations

@router.get("/stats")
def get_donor_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.user_type != "donor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only donor users can access stats"
        )
    
    donor_profile = db.query(DonorProfile).filter(DonorProfile.user_id == current_user.id).first()
    if not donor_profile:
        return {
            "total_donated": 0.0,
            "donation_count": 0,
            "campaigns_supported": 0
        }
    
    donations = db.query(Donation).filter(Donation.donor_id == donor_profile.id).all()
    campaigns_supported = len(set(d.campaign_id for d in donations))
    
    return {
        "total_donated": donor_profile.total_donated,
        "donation_count": len(donations),
        "campaigns_supported": campaigns_supported
    }

