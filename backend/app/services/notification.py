from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Notification, User, UserNotificationPreference
from app.schemas.notification import (
    NotificationCreate,
    NotificationUpdate,
    NotificationPreferenceUpdate,
    NotificationType
)

class NotificationService:
    """Service for handling user notifications and preferences."""
    
    async def create_notification(
        self,
        db: AsyncSession,
        notification_in: NotificationCreate,
        user_id: int
    ) -> Notification:
        """Create a new notification for a user."""
        db_notification = Notification(
            user_id=user_id,
            title=notification_in.title,
            message=notification_in.message,
            notification_type=notification_in.notification_type,
            data=notification_in.data or {},
            is_read=False
        )
        
        db.add(db_notification)
        await db.commit()
        await db.refresh(db_notification)
        return db_notification
    
    async def get_user_notifications(
        self,
        db: AsyncSession,
        user_id: int,
        read: Optional[bool] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Notification]:
        """Get notifications for a user with optional filters."""
        query = select(Notification).filter(Notification.user_id == user_id)
        
        if read is not None:
            query = query.filter(Notification.is_read == read)
            
        result = await db.execute(
            query.order_by(Notification.created_at.desc())
            .offset(offset).limit(limit)
        )
        return result.scalars().all()
    
    async def mark_as_read(
        self,
        db: AsyncSession,
        notification_id: int,
        user_id: int
    ) -> bool:
        """Mark a notification as read."""
        result = await db.execute(
            select(Notification)
            .filter(
                Notification.id == notification_id,
                Notification.user_id == user_id
            )
        )
        notification = result.scalars().first()
        
        if notification:
            notification.is_read = True
            notification.read_at = datetime.utcnow()
            await db.commit()
            return True
        return False
    
    async def mark_all_as_read(
        self,
        db: AsyncSession,
        user_id: int
    ) -> int:
        """Mark all user's notifications as read."""
        result = await db.execute(
            select(Notification)
            .filter(
                Notification.user_id == user_id,
                Notification.is_read == False
            )
        )
        
        count = 0
        for notification in result.scalars().all():
            notification.is_read = True
            notification.read_at = datetime.utcnow()
            count += 1
        
        if count > 0:
            await db.commit()
        
        return count
    
    async def get_unread_count(
        self,
        db: AsyncSession,
        user_id: int
    ) -> int:
        """Get count of unread notifications."""
        result = await db.execute(
            select(func.count(Notification.id))
            .filter(
                Notification.user_id == user_id,
                Notification.is_read == False
            )
        )
        return result.scalar() or 0
    
    async def get_user_preferences(
        self,
        db: AsyncSession,
        user_id: int
    ) -> List[UserNotificationPreference]:
        """Get notification preferences for a user."""
        result = await db.execute(
            select(UserNotificationPreference)
            .filter(UserNotificationPreference.user_id == user_id)
        )
        return result.scalars().all()
    
    async def update_preferences(
        self,
        db: AsyncSession,
        user_id: int,
        preferences: List[NotificationPreferenceUpdate]
    ) -> List[UserNotificationPreference]:
        """Update notification preferences for a user."""
        updated = []
        
        for pref_in in preferences:
            # Try to find existing preference
            result = await db.execute(
                select(UserNotificationPreference)
                .filter(
                    UserNotificationPreference.user_id == user_id,
                    UserNotificationPreference.notification_type == pref_in.notification_type
                )
            )
            
            pref = result.scalars().first()
            
            if pref:
                # Update existing preference
                pref.enabled = pref_in.enabled
                pref.email_enabled = pref_in.email_enabled
                pref.push_enabled = pref_in.push_enabled
            else:
                # Create new preference
                pref = UserNotificationPreference(
                    user_id=user_id,
                    notification_type=pref_in.notification_type,
                    enabled=pref_in.enabled,
                    email_enabled=pref_in.email_enabled,
                    push_enabled=pref_in.push_enabled
                )
                db.add(pref)
            
            updated.append(pref)
        
        await db.commit()
        return updated

# Create a singleton instance of the service
notification_service = NotificationService()
