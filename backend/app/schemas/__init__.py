# Aggregate exports so `from app import schemas` exposes expected symbols like `schemas.UserResponse`.

# User schemas
from .user import (
    UserBase,
    UserCreate,
    UserUpdate,
    UserInDBBase,
    UserResponse,
    UserInDB,
    UserWithRoles,
    UserRegister,
)

# Token schemas
from .token import Token, TokenPayload

# Transaction schemas
from .transaction import (
    TransactionBase,
    TransactionCreate,
    TransactionUpdate,
    TransactionResponse,
    TransactionSummary,
    TransactionByCategory,
)

# Microloan schemas
from .microloan import (
    MicroLoanBase,
    MicroLoanCreate,
    MicroLoanUpdate,
    MicroLoanResponse,
    MicroLoanApprove,
    MicroLoanReject,
    LoanRepaymentCreate,
    LoanRepaymentResponse,
)

# Crowdfunding schemas (alias to match expected names in endpoints)
from .crowdfunding import (
    CampaignBase as CrowdFundingCampaignBase,
    CampaignCreate as CrowdFundingCampaignCreate,
    CampaignUpdate as CrowdFundingCampaignUpdate,
    CampaignResponse as CrowdFundingCampaignResponse,
    DonationCreate,
    DonationResponse,
    DonationWithCampaignResponse,
)

# Poverty area schemas
from .poverty_area import (
    PovertyAreaBase,
    PovertyAreaCreate,
    PovertyAreaUpdate,
    PovertyAreaResponse,
    PovertyAreaMapResponse,
    PovertyStatsSummary,
    PovertyNeedsAnalysis,
)

# Notification schemas
from .notification import (
    Notification,
    NotificationCreate,
    NotificationPreference,
    NotificationPreferenceUpdate,
    NotificationType,
)

__all__ = [name for name in globals().keys() if not name.startswith("_")]
