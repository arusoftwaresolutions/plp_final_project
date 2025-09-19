from datetime import datetime
from decimal import Decimal
from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.app.models import PovertyArea, User, Transaction, TransactionType
from backend.app.schemas.poverty_area import (
    PovertyAreaCreate,
    PovertyAreaUpdate,
    PovertyStatsSummary,
    PovertyNeedsAnalysis,
    PovertyAreaFilter
)
from backend.app.services.base import CRUDBase
from backend.app.core.exceptions import ValidationError

class CRUDPovertyArea(CRUDBase[PovertyArea, PovertyAreaCreate, PovertyAreaUpdate]):
    """Poverty Area CRUD operations."""
    
    async def get_with_stats(
        self, 
        db: AsyncSession, 
        area_id: int,
        include_related: bool = True
    ) -> Optional[PovertyArea]:
        """Get a poverty area with statistics."""
        query = select(PovertyArea).filter(PovertyArea.id == area_id)
        
        if include_related:
            query = query.options(
                selectinload(PovertyArea.related_campaigns),
                selectinload(PovertyArea.related_loans)
            )
        
        result = await db.execute(query)
        return result.scalars().first()
    
    async def search_areas(
        self,
        db: AsyncSession,
        filters: Optional[PovertyAreaFilter] = None,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[PovertyArea], int]:
        """Search poverty areas with filtering and pagination."""
        query = select(PovertyArea)
        
        if filters:
            if filters.min_poverty_rate is not None:
                query = query.filter(PovertyArea.poverty_rate >= filters.min_poverty_rate)
            if filters.max_poverty_rate is not None:
                query = query.filter(PovertyArea.poverty_rate <= filters.max_poverty_rate)
            if filters.min_population is not None:
                query = query.filter(PovertyArea.population >= filters.min_population)
            if filters.max_population is not None:
                query = query.filter(PovertyArea.population <= filters.max_population)
            if filters.needs:
                # Find areas that have any of the specified needs
                conditions = []
                for need in filters.needs:
                    conditions.append(PovertyArea.needs.contains([need]))
                query = query.filter(or_(*conditions))
            if filters.bbox:
                # Spatial filtering using bounding box [min_lng, min_lat, max_lng, max_lat]
                min_lng, min_lat, max_lng, max_lat = filters.bbox
                query = query.filter(
                    and_(
                        PovertyArea.location['coordinates'][0] >= min_lng,
                        PovertyArea.location['coordinates'][1] >= min_lat,
                        PovertyArea.location['coordinates'][0] <= max_lng,
                        PovertyArea.location['coordinates'][1] <= max_lat
                    )
                )
        
        # Get total count for pagination
        count = (await db.execute(select(func.count()).select_from(query.subquery()))).scalar()
        
        # Apply ordering and pagination
        result = await db.execute(
            query.order_by(PovertyArea.poverty_rate.desc())
            .offset(skip)
            .limit(limit)
        )
        
        return result.scalars().all(), count
    
    async def get_stats_summary(self, db: AsyncSession) -> PovertyStatsSummary:
        """Get summary statistics for poverty areas."""
        # Get basic stats
        result = await db.execute(
            select(
                func.count(PovertyArea.id).label("total_areas"),
                func.avg(PovertyArea.poverty_rate).label("avg_poverty_rate"),
                func.sum(PovertyArea.population).label("total_population")
            )
        )
        
        stats = result.first()
        
        # Get most common needs
        needs_result = await db.execute(
            select(
                func.unnest(PovertyArea.needs).label("need"),
                func.count().label("count")
            )
            .group_by("need")
            .order_by(func.count().desc())
            .limit(10)
        )
        
        most_common_needs = [
            {"need": row.need, "count": row.count}
            for row in needs_result.all()
        ]
        
        # Get poverty distribution by range
        distribution = await self._get_poverty_distribution(db)
        
        return PovertyStatsSummary(
            total_areas=stats.total_areas or 0,
            avg_poverty_rate=float(stats.avg_poverty_rate or 0),
            total_population=stats.total_population or 0,
            most_common_needs=most_common_needs,
            poverty_distribution=distribution
        )
    
    async def analyze_needs(
        self,
        db: AsyncSession,
        need: Optional[str] = None
    ) -> List[PovertyNeedsAnalysis]:
        """Analyze poverty needs across areas."""
        if need:
            # Get analysis for a specific need
            query = """
            SELECT 
                unnest(needs) as need,
                COUNT(*) as area_count,
                AVG(poverty_rate) as avg_poverty_rate,
                SUM(population) as total_population
            FROM poverty_areas
            WHERE :need = ANY(needs)
            GROUP BY need
            """
            result = await db.execute(query, {"need": need})
            rows = result.all()
        else:
            # Get analysis for all needs
            query = """
            WITH needs_unnested AS (
                SELECT id, unnest(needs) as need, poverty_rate, population
                FROM poverty_areas
            )
            SELECT 
                need,
                COUNT(*) as area_count,
                AVG(poverty_rate) as avg_poverty_rate,
                SUM(population) as total_population
            FROM needs_unnested
            GROUP BY need
            ORDER BY area_count DESC
            """
            result = await db.execute(query)
            rows = result.all()
        
        # Calculate total areas for percentage calculation
        total_areas = await db.scalar(select(func.count(PovertyArea.id)))
        
        # Format the results
        analyses = []
        for row in rows:
            percentage = (row.area_count / total_areas) * 100 if total_areas else 0
            
            # Get sample areas with this need
            sample_areas = await db.execute(
                select(PovertyArea)
                .filter(PovertyArea.needs.contains([row.need]))
                .limit(5)
            )
            
            analyses.append(
                PovertyNeedsAnalysis(
                    need=row.need,
                    count=row.area_count,
                    percentage=percentage,
                    avg_poverty_rate=float(row.avg_poverty_rate or 0),
                    total_population=row.total_population or 0,
                    areas=[
                        {
                            "id": area.id,
                            "name": area.name,
                            "poverty_rate": area.poverty_rate,
                            "population": area.population
                        }
                        for area in sample_areas.scalars().all()
                    ]
                )
            )
        
        return analyses
    
    async def _get_poverty_distribution(
        self,
        db: AsyncSession
    ) -> List[Dict[str, Any]]:
        """Get distribution of poverty rates across ranges."""
        ranges = [
            (0, 10, "0-10%"),
            (10, 20, "10-20%"),
            (20, 30, "20-30%"),
            (30, 40, "30-40%"),
            (40, 101, "40%+")
        ]
        
        distribution = []
        
        for min_rate, max_rate, label in ranges:
            query = """
            SELECT 
                COUNT(*) as area_count,
                COALESCE(SUM(population), 0) as total_population
            FROM poverty_areas
            WHERE poverty_rate >= :min_rate AND poverty_rate < :max_rate
            """
            
            result = await db.execute(
                query,
                {"min_rate": min_rate, "max_rate": max_rate}
            )
            
            row = result.first()
            distribution.append({
                "range": label,
                "area_count": row.area_count or 0,
                "population": row.total_population or 0
            })
        
        return distribution

# Create an instance of the service
poverty_area = CRUDPovertyArea(PovertyArea)
