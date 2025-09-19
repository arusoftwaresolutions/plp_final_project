from datetime import datetime
from enum import Enum as PyEnum
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship

from backend.app.db.base_class import Base

class NotificationType(str, PyEnum):
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

class Notification(Base):
    """Model for storing user notifications."""
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    notification_type = Column(String(50), nullable=False)
    data = Column(JSON, nullable=False, default=dict)
    is_read = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    read_at = Column(DateTime, nullable=True)
    
    # Relationship
    user = relationship("User", back_populates="notifications")
    
    def __repr__(self):
        return f"<Notification {self.id} - {self.title}>"

class UserNotificationPreference(Base):
    """Model for storing user notification preferences."""
    __tablename__ = "user_notification_preferences"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    notification_type = Column(String(50), nullable=False)
    enabled = Column(Boolean, default=True, nullable=False)
    email_enabled = Column(Boolean, default=False, nullable=False)
    push_enabled = Column(Boolean, default=True, nullable=False)
    sms_enabled = Column(Boolean, default=False, nullable=False)
    
    # Relationship
    user = relationship("User", back_populates="notification_preferences")
    
    __table_args__ = (
        # Ensure one preference per user per notification type
        {'sqlite_autoincrement': True},
    )
    
    def __repr__(self):
        return f"<UserNotificationPreference {self.user_id} - {self.notification_type}>"

# Import User model from db.models to avoid circular imports
from backend.app.db.models import User

# Add relationships to User model if not already present
if not hasattr(User, 'notifications'):
    User.notifications = relationship(
        "Notification", 
        back_populates="user",
        cascade="all, delete-orphan"
    )

if not hasattr(User, 'notification_preferences'):
    User.notification_preferences = relationship(
        "UserNotificationPreference", 
        back_populates="user",
        cascade="all, delete-orphan"
    )
