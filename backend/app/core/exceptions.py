"""
Custom exception classes used across the backend services layer.
These provide semantic error categories that route handlers can map to HTTP errors.
"""

class AppError(Exception):
    """Base class for application-specific errors."""
    pass

class ValidationError(AppError):
    """Raised when input validation fails at the service layer."""
    pass

class TransactionError(AppError):
    """Raised for generic transaction-related failures."""
    pass

class InsufficientFundsError(TransactionError):
    """Raised when a user does not have enough balance for an operation."""
    pass

class CampaignError(AppError):
    """Raised for crowdfunding campaign domain errors."""
    pass

class LoanError(AppError):
    """Raised for microloan domain errors."""
    pass
