# Services package - Import all services for easy access from other modules

# AI Service
try:
    from .ai_service import ai_service
except ImportError:
    ai_service = None

# Authentication Service
try:
    from .auth import auth
except ImportError:
    auth = None

# User Service
try:
    from .user import user
except ImportError:
    user = None

# Transaction Services
try:
    from .transaction import transaction, transaction_category
except ImportError:
    transaction = None
    transaction_category = None

# Crowdfunding Service
try:
    from .crowdfunding import crowdfunding
except ImportError:
    crowdfunding = None

# Microloan Service
try:
    from .microloan import microloan
except ImportError:
    microloan = None

# Notification Service
try:
    from .notification import notification
except ImportError:
    notification = None

# Poverty Area Service
try:
    from .poverty_area import poverty_area
except ImportError:
    poverty_area = None

# Base Service (if needed)
try:
    from .base import CRUDBase
except ImportError:
    CRUDBase = None
