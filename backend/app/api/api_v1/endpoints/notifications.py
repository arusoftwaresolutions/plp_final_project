from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud, models, schemas
from app.api import deps
from app.services import notification as notification_service

router = APIRouter()

@router.get("/", response_model=List[schemas.Notification])
async def get_notifications(
    db: AsyncSession = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    read: Optional[bool] = None,
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """
    Retrieve notifications for the current user.
    """
    notifications = await notification_service.get_user_notifications(
        db=db,
        user_id=current_user.id,
        read=read,
        skip=skip,
        limit=limit
    )
    return notifications

@router.get("/unread-count", response_model=int)
async def get_unread_count(
    db: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """
    Get count of unread notifications for the current user.
    """
    return await notification_service.get_unread_count(db, user_id=current_user.id)

@router.post("/mark-as-read/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
async def mark_notification_as_read(
    notification_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """
    Mark a notification as read.
    """
    success = await notification_service.mark_as_read(
        db=db,
        notification_id=notification_id,
        user_id=current_user.id
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found or not owned by user"
        )
    return None

@router.post("/mark-all-read", response_model=int)
async def mark_all_notifications_as_read(
    db: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """
    Mark all notifications as read for the current user.
    Returns the number of notifications marked as read.
    """
    return await notification_service.mark_all_as_read(db, user_id=current_user.id)

@router.get("/preferences", response_model=List[schemas.NotificationPreference])
async def get_notification_preferences(
    db: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """
    Get notification preferences for the current user.
    """
    return await notification_service.get_user_preferences(db, user_id=current_user.id)

@router.put("/preferences", response_model=List[schemas.NotificationPreference])
async def update_notification_preferences(
    preferences: List[schemas.NotificationPreferenceUpdate],
    db: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """
    Update notification preferences for the current user.
    """
    return await notification_service.update_preferences(
        db=db,
        user_id=current_user.id,
        preferences=preferences
    )

@router.post("/test", status_code=status.HTTP_201_CREATED)
async def send_test_notification(
    notification_in: schemas.NotificationCreate,
    db: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_superuser),
):
    """
    Send a test notification (admin only).
    """
    notification = await notification_service.create_notification(
        db=db,
        notification_in=notification_in,
        user_id=current_user.id
    )
    return notification

@router.get("/types", response_model=List[str])
async def get_notification_types():
    """
    Get all available notification types.
    """
    return [t.value for t in schemas.NotificationType]
