# Aggregate SQLAlchemy models so `from backend.app import models` exposes ORM classes

# Export the core models defined in backend/app/db/models.py
from backend.app.db.models import (
    Base,
    User,
    Role,
    Transaction,
    TransactionType,
    TransactionCategory,
    MicroLoan,
    LoanRepayment,
    CrowdFundingCampaign,
    Donation,
    PovertyArea,
)

# Export notification-related models defined in this package
from backend.app.models.notification import (
    Notification,
    NotificationType,
    UserNotificationPreference,
)

__all__ = [name for name in globals().keys() if not name.startswith("_")]
