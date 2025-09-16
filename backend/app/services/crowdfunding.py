from datetime import datetime, date
from decimal import Decimal
from typing import List, Optional, Tuple, Dict, Any
from sqlalchemy import select, func, and_, or_, case
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import (
    CrowdFundingCampaign, 
    Donation, 
    User,
    Transaction,
    TransactionType
)
from app.schemas.crowdfunding import (
    CampaignCreate,
    CampaignUpdate,
    CampaignStatus,
    DonationCreate,
    CampaignStats,
    DonorLeaderboard,
    CampaignSearchFilter
)
from app.services.base import CRUDBase
from app.core.exceptions import CampaignError, ValidationError

class CRUDCampaign(CRUDBase[CrowdFundingCampaign, CampaignCreate, CampaignUpdate]):
    """Crowdfunding Campaign CRUD operations."""
    
    async def get_active_campaigns(
        self, db: AsyncSession, skip: int = 0, limit: int = 100,
        filters: Optional[CampaignSearchFilter] = None
    ) -> Tuple[List[CrowdFundingCampaign], int]:
        """Get active campaigns with optional filtering."""
        query = select(CrowdFundingCampaign).filter(
            CrowdFundingCampaign.status == CampaignStatus.ACTIVE,
            CrowdFundingCampaign.end_date > datetime.utcnow()
        )
        
        if filters:
            if filters.min_amount is not None:
                query = query.filter(CrowdFundingCampaign.target_amount >= filters.min_amount)
            if filters.max_amount is not None:
                query = query.filter(CrowdFundingCampaign.target_amount <= filters.max_amount)
            if filters.search_query:
                query = query.filter(
                    or_(
                        CrowdFundingCampaign.title.ilike(f"%{filters.search_query}%"),
                        CrowdFundingCampaign.description.ilike(f"%{filters.search_query}%")
                    )
                )
        
        count = (await db.execute(select(func.count()).select_from(query.subquery()))).scalar()
        result = await db.execute(
            query.options(selectinload(CrowdFundingCampaign.creator))
            .order_by(CrowdFundingCampaign.created_at.desc())
            .offset(skip).limit(limit)
        )
        return result.scalars().all(), count
    
    async def create_campaign(
        self, db: AsyncSession, obj_in: CampaignCreate, creator_id: int
    ) -> CrowdFundingCampaign:
        """Create a new crowdfunding campaign."""
        if obj_in.end_date <= datetime.utcnow():
            raise ValidationError("End date must be in the future")
        
        db_obj = CrowdFundingCampaign(
            **obj_in.dict(exclude={"id"}),
            created_by=creator_id,
            status=CampaignStatus.ACTIVE,
            amount_raised=Decimal('0.00'),
            created_at=datetime.utcnow()
        )
        
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def update_campaign(
        self, db: AsyncSession, db_obj: CrowdFundingCampaign, obj_in: CampaignUpdate
    ) -> CrowdFundingCampaign:
        """Update a campaign."""
        update_data = obj_in.dict(exclude_unset=True)
        
        # Prevent updating certain fields if campaign is completed or cancelled
        if db_obj.status in [CampaignStatus.COMPLETED, CampaignStatus.CANCELLED]:
            for field in ["status", "target_amount", "end_date"]:
                if field in update_data:
                    raise CampaignError(f"Cannot update {field} for a {db_obj.status} campaign")
        
        # Update the campaign
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def add_donation(
        self, db: AsyncSession, campaign_id: int, donor_id: int, obj_in: DonationCreate
    ) -> Donation:
        """Add a donation to a campaign."""
        # Get the campaign with a row-level lock to prevent race conditions
        result = await db.execute(
            select(CrowdFundingCampaign)
            .filter(CrowdFundingCampaign.id == campaign_id)
            .with_for_update()
        )
        campaign = result.scalars().first()
        
        if not campaign:
            raise CampaignError("Campaign not found")
        
        if campaign.status != CampaignStatus.ACTIVE:
            raise CampaignError(f"Cannot donate to a {campaign.status} campaign")
        
        if campaign.end_date < datetime.utcnow():
            campaign.status = CampaignStatus.COMPLETED
            db.add(campaign)
            await db.commit()
            raise CampaignError("This campaign has already ended")
        
        # Create the donation
        donation = Donation(
            campaign_id=campaign_id,
            donor_id=donor_id,
            amount=obj_in.amount,
            message=obj_in.message,
            is_anonymous=obj_in.is_anonymous,
            created_at=datetime.utcnow()
        )
        
        # Update campaign amount raised
        campaign.amount_raised += obj_in.amount
        
        # Create a transaction record
        transaction = Transaction(
            user_id=donor_id,
            amount=obj_in.amount,
            type="expense",
            description=f"Donation to campaign: {campaign.title}",
            reference=f"DONATION-{campaign_id}",
            status="completed"
        )
        
        db.add_all([donation, campaign, transaction])
        await db.commit()
        await db.refresh(donation)
        
        # Check if campaign target is reached
        if campaign.amount_raised >= campaign.target_amount:
            campaign.status = CampaignStatus.COMPLETED
            campaign.completed_at = datetime.utcnow()
            db.add(campaign)
            await db.commit()
        
        return donation
    
    async def get_campaign_stats(self, db: AsyncSession) -> CampaignStats:
        """Get crowdfunding statistics."""
        result = await db.execute(
            select(
                func.count(CrowdFundingCampaign.id).label("total_campaigns"),
                func.sum(case(
                    (CrowdFundingCampaign.status == CampaignStatus.ACTIVE, 1),
                    else_=0
                )).label("active_campaigns"),
                func.sum(case(
                    (CrowdFundingCampaign.status == CampaignStatus.COMPLETED, 1),
                    else_=0
                )).label("completed_campaigns"),
                func.sum(CrowdFundingCampaign.amount_raised).label("total_raised"),
                func.count(Donation.id.distinct()).label("total_donors")
            ).select_from(CrowdFundingCampaign)
            .outerjoin(Donation)
        )
        
        row = result.first()
        
        return CampaignStats(
            total_campaigns=row.total_campaigns or 0,
            active_campaigns=row.active_campaigns or 0,
            completed_campaigns=row.completed_campaigns or 0,
            total_raised=Decimal(str(row.total_raised or '0.00')),
            total_donors=row.total_donors or 0,
            avg_donation=(
                Decimal(str(row.total_raised or '0.00')) / row.total_donors
                if row.total_donors and row.total_raised
                else Decimal('0.00')
            )
        )
    
    async def get_donor_leaderboard(
        self, db: AsyncSession, limit: int = 10
    ) -> List[DonorLeaderboard]:
        """Get top donors by total amount donated."""
        result = await db.execute(
            select(
                User.id.label("donor_id"),
                User.full_name.label("donor_name"),
                func.sum(Donation.amount).label("total_donated"),
                func.count(Donation.id).label("donation_count"),
                func.max(Donation.created_at).label("last_donation")
            )
            .select_from(Donation)
            .join(User, Donation.donor_id == User.id)
            .group_by(User.id, User.full_name)
            .order_by(func.sum(Donation.amount).desc())
            .limit(limit)
        )
        
        return [
            DonorLeaderboard(
                donor_id=row.donor_id,
                donor_name=row.donor_name,
                total_donated=Decimal(str(row.total_donated or '0.00')),
                donation_count=row.donation_count or 0,
                last_donation=row.last_donation or datetime.utcnow()
            )
            for row in result.all()
        ]

# Create an instance of the service
campaign = CRUDCampaign(CrowdFundingCampaign)
