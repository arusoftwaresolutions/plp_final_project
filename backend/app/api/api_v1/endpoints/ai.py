from typing import Any, List, Optional
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app import models, schemas
from backend.app.api import deps
from backend.app.db.session import get_db
from backend.app.services import ai as ai_service

router = APIRouter()

@router.get("/recommendations", response_model=schemas.AIRecommendationsResponse)
async def get_ai_recommendations(
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get AI-powered financial recommendations for the current user.
    """
    try:
        # Get user financial data
        user_financial_profile = await ai_service.get_user_financial_profile(
            db, user_id=current_user.id
        )

        # Generate budget recommendations
        budget_recommendations = await ai_service.generate_budget_recommendations(
            db, user_id=current_user.id
        )

        # Generate campaign recommendations
        campaign_recommendations = await ai_service.generate_campaign_recommendations(
            db, user_id=current_user.id
        )

        # Generate loan eligibility assessment
        loan_eligibility = await ai_service.assess_loan_eligibility(
            db, user_id=current_user.id
        )

        # Generate poverty insights
        poverty_insights = await ai_service.generate_poverty_insights(
            db, user_id=current_user.id
        )

        # Combine all recommendations
        recommendations = {
            "budget_recommendations": budget_recommendations,
            "campaign_recommendations": campaign_recommendations,
            "loan_eligibility": loan_eligibility,
            "poverty_insights": poverty_insights,
            "generated_at": datetime.utcnow(),
            "user_id": current_user.id
        }

        return recommendations

    except Exception as e:
        # Return fallback recommendations if AI service fails
        return {
            "budget_recommendations": [
                {
                    "category": "Food",
                    "current_amount": 0,
                    "suggested_max": 300,
                    "recommendation": "Consider meal planning to reduce food expenses",
                    "description": "Basic food and groceries"
                },
                {
                    "category": "Transport",
                    "current_amount": 0,
                    "suggested_max": 150,
                    "recommendation": "Use public transport when possible",
                    "description": "Transportation costs"
                }
            ],
            "campaign_recommendations": [],
            "loan_eligibility": {
                "is_eligible": False,
                "reason": "No financial history available",
                "max_eligible_amount": 0,
                "recommended_amount": 0,
                "interest_rate": 0,
                "monthly_payment": 0
            },
            "poverty_insights": [],
            "generated_at": datetime.utcnow(),
            "user_id": current_user.id,
            "note": "AI service temporarily unavailable - showing default recommendations"
        }

@router.post("/analyze-spending", response_model=schemas.SpendingAnalysisResponse)
async def analyze_user_spending(
    analysis_request: schemas.SpendingAnalysisRequest,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Analyze user spending patterns and provide insights.
    """
    try:
        analysis = await ai_service.analyze_spending_patterns(
            db, user_id=current_user.id, request=analysis_request
        )
        return analysis
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to analyze spending patterns"
        )

@router.get("/financial-health", response_model=schemas.FinancialHealthScore)
async def get_financial_health_score(
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get user's financial health score and recommendations.
    """
    try:
        health_score = await ai_service.calculate_financial_health_score(
            db, user_id=current_user.id
        )
        return health_score
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to calculate financial health score"
        )
