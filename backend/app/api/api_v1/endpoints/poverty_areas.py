from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app import models, schemas
from app.api import deps
from app.db.session import get_db
from app.services import poverty_area as poverty_area_service

router = APIRouter()

@router.get("/", response_model=List[schemas.PovertyAreaResponse])
async def list_poverty_areas(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    min_poverty_rate: Optional[float] = None,
    max_poverty_rate: Optional[float] = None,
    needs: Optional[str] = None,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    List poverty areas with optional filtering.
    """
    # Parse needs string into a list if provided
    needs_list = needs.split(",") if needs else None
    
    areas = await poverty_area_service.get_areas(
        db,
        skip=skip,
        limit=limit,
        min_poverty_rate=min_poverty_rate,
        max_poverty_rate=max_poverty_rate,
        needs=needs_list,
    )
    return areas

@router.post("/", response_model=schemas.PovertyAreaResponse, status_code=status.HTTP_201_CREATED)
async def create_poverty_area(
    *,
    db: AsyncSession = Depends(get_db),
    area_in: schemas.PovertyAreaCreate,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Create a new poverty area (admin only).
    """
    area = await poverty_area_service.create(db, obj_in=area_in)
    return area

@router.get("/{area_id}", response_model=schemas.PovertyAreaResponse)
async def get_poverty_area(
    area_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Get a specific poverty area by ID.
    """
    area = await poverty_area_service.get(db, id=area_id)
    if not area:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Poverty area not found",
        )
    return area

@router.put("/{area_id}", response_model=schemas.PovertyAreaResponse)
async def update_poverty_area(
    *,
    db: AsyncSession = Depends(get_db),
    area_id: int,
    area_in: schemas.PovertyAreaUpdate,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Update a poverty area (admin only).
    """
    area = await poverty_area_service.get(db, id=area_id)
    if not area:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Poverty area not found",
        )
    
    area = await poverty_area_service.update(
        db, db_obj=area, obj_in=area_in
    )
    return area

@router.delete("/{area_id}", response_model=schemas.PovertyAreaResponse)
async def delete_poverty_area(
    *,
    db: AsyncSession = Depends(get_db),
    area_id: int,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Delete a poverty area (admin only).
    """
    area = await poverty_area_service.get(db, id=area_id)
    if not area:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Poverty area not found",
        )
    
    area = await poverty_area_service.remove(db, id=area_id)
    return area

@router.get("/map/data", response_model=List[schemas.PovertyAreaMapResponse])
async def get_poverty_areas_for_map(
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get poverty areas data formatted for map visualization.
    """
    areas = await poverty_area_service.get_areas_for_map(db)
    return areas

@router.get("/stats/summary", response_model=schemas.PovertyStatsSummary)
async def get_poverty_stats_summary(
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get summary statistics about poverty areas.
    """
    stats = await poverty_area_service.get_stats_summary(db)
    return stats

@router.get("/needs/analysis", response_model=List[schemas.PovertyNeedsAnalysis])
async def analyze_poverty_needs(
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Analyze and categorize poverty needs across areas.
    """
    analysis = await poverty_area_service.analyze_needs(db)
    return analysis
