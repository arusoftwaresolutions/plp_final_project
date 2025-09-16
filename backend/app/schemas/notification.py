from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, validator

class NotificationType(str, Enum):
    """Types of notifications in the system."""
    TRANSACTION = "transaction"
    LOAN_APPROVAL = "loan_approval"
    LOAN_REPAYMENT = "loan_repayment"
    CAMPAIGN_UPDATE = "campaign_update"
    DONATION_RECEIVED = "donation_received"
    SYSTEM_ALERT = "system_alert"
    ACCOUNT_UPDATE = "account_update"
    POVERTY_ALERT = "poverty_alert"
    BUDGET_ALERT = "budget_alert"
    RECOMMENDATION = "recommendation"

class NotificationBase(BaseModel):
    """Base schema for notifications."""
    title: str = Field(..., max_length=200)
    message: str = Field(..., max_length=1000)
    notification_type: NotificationType
    data: Dict[str, Any] = {}

class NotificationCreate(NotificationBase):
    """Schema for creating a new notification."""
    pass

class NotificationUpdate(BaseModel):
    """Schema for updating a notification."""
    is_read: Optional[bool] = None

class NotificationInDBBase(NotificationBase):
    """Base schema for notification in database."""
    id: int
    user_id: int
    is_read: bool = False
    created_at: datetime
    read_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True

class Notification(NotificationInDBBase):
    """Schema for notification response."""
    pass

class NotificationPreferenceBase(BaseModel):
    """Base schema for notification preferences."""
    notification_type: NotificationType
    enabled: bool = True
    email_enabled: bool = False
    push_enabled: bool = True

class NotificationPreferenceCreate(NotificationPreferenceBase):
    """Schema for creating notification preferences."""
    pass

class NotificationPreferenceUpdate(NotificationPreferenceBase):
    """Schema for updating notification preferences."""
    pass

class NotificationPreference(NotificationPreferenceBase):
    """Schema for notification preference response."""
    user_id: int
    
    class Config:
        orm_mode = True

class NotificationChannel(str, Enum):
    """Available notification channels."""
    EMAIL = "email"
    PUSH = "push"
    SMS = "sms"
    IN_APP = "in_app"

class NotificationBulkCreate(BaseModel):
    """Schema for creating multiple notifications at once."""
    user_ids: List[int]
    notification: NotificationCreate

class NotificationStats(BaseModel):
    """Schema for notification statistics."""
    total: int = 0
    unread: int = 0
    by_type: Dict[NotificationType, int] = {}
    
    @validator('by_type', pre=True)
    def set_default_by_type(cls, v):
        return v or {}

class NotificationFilter(BaseModel):
    """Schema for filtering notifications."""
    is_read: Optional[bool] = None
    notification_type: Optional[NotificationType] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class NotificationPreferencesUpdate(BaseModel):
    """Schema for updating multiple notification preferences."""
    preferences: List[NotificationPreferenceUpdate]
