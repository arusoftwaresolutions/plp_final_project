from fastapi import APIRouter

from .endpoints import (
    auth,
    users,
    transactions,
    microloans,
    crowdfunding,
    poverty_areas,
    notifications,
    ai  # Add AI endpoints
)

api_router = APIRouter()

# Include all API endpoints
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(transactions.router, prefix="/transactions", tags=["Transactions"])
api_router.include_router(microloans.router, prefix="/microloans", tags=["Microloans"])
api_router.include_router(crowdfunding.router, prefix="/crowdfunding", tags=["Crowdfunding"])
api_router.include_router(poverty_areas.router, prefix="/poverty-areas", tags=["Poverty Areas"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["Notifications"])
api_router.include_router(ai.router, prefix="/ai", tags=["AI"])  # Add AI router
