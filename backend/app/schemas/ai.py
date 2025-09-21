from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class BudgetCategory(BaseModel):
    """Represents a budget category with spending recommendations."""
    category: str = Field(..., description="Name of the budget category")
    current_amount: float = Field(..., description="Current spending in this category")
    suggested_max: float = Field(..., description="Suggested maximum spending")
    recommendation: str = Field(..., description="Personalized recommendation")
    description: str = Field(..., description="Description of the category")


class BudgetRecommendation(BaseModel):
    """Budget recommendation for a user."""
    user_id: int = Field(..., description="ID of the user")
    time_period: str = Field("monthly", description="Time period for the budget")
    total_income: float = Field(..., description="User's total income")
    current_monthly_spending: float = Field(..., description="Current monthly spending")
    categories: List[BudgetCategory] = Field(..., description="Budget categories")
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    is_default: bool = Field(False, description="Whether this is a default recommendation")


class CampaignRecommendation(BaseModel):
    """Campaign recommendation for a user."""
    campaign_id: int = Field(..., description="ID of the recommended campaign")
    title: str = Field(..., description="Campaign title")
    description: str = Field(..., description="Campaign description")
    current_amount: float = Field(..., description="Amount raised so far")
    target_amount: float = Field(..., description="Funding goal")
    end_date: datetime = Field(..., description="Campaign end date")
    category: str = Field(..., description="Campaign category")
    match_score: float = Field(..., description="How well this matches user interests (0-1)")
    reason: str = Field(..., description="Why this campaign was recommended")


class LoanEligibility(BaseModel):
    """Loan eligibility information for a user."""
    is_eligible: bool = Field(..., description="Whether the user is eligible")
    reason: str = Field(..., description="Reason for eligibility decision")
    max_eligible_amount: float = Field(..., description="Maximum eligible loan amount")
    recommended_amount: float = Field(..., description="Recommended loan amount")
    interest_rate: float = Field(..., description="Annual interest rate (APR)")
    monthly_payment: float = Field(..., description="Estimated monthly payment")


class PovertyInsight(BaseModel):
    """Insights about poverty in a specific area."""
    area_id: int = Field(..., description="ID of the area")
    area_name: str = Field(..., description="Name of the area")
    poverty_rate: float = Field(..., description="Poverty rate in percentage")
    average_income: float = Field(..., description="Average household income")
    population: int = Field(..., description="Total population")
    insights: List[str] = Field(..., description="List of insights about the area")
    generated_at: datetime = Field(default_factory=datetime.utcnow)


class UserFinancialProfile(BaseModel):
    """Financial profile of a user."""
    user_id: int = Field(..., description="ID of the user")
    total_income: float = Field(0.0, description="Total monthly income")
    total_expenses: float = Field(0.0, description="Total monthly expenses")
    total_debt: float = Field(0.0, description="Total outstanding debt")
    credit_score: int = Field(300, description="Credit score (300-850)")
    active_loans: int = Field(0, description="Number of active loans")


# Response schemas for API endpoints
class AIRecommendationsResponse(BaseModel):
    """Response schema for AI recommendations."""
    budget_recommendations: List[BudgetCategory] = Field(..., description="Budget recommendations")
    campaign_recommendations: List[CampaignRecommendation] = Field(..., description="Campaign recommendations")
    loan_eligibility: LoanEligibility = Field(..., description="Loan eligibility information")
    poverty_insights: List[PovertyInsight] = Field(..., description="Poverty insights")
    generated_at: datetime = Field(..., description="When recommendations were generated")
    user_id: int = Field(..., description="ID of the user")
    note: Optional[str] = Field(None, description="Additional notes")


class SpendingAnalysisRequest(BaseModel):
    """Request schema for spending analysis."""
    start_date: Optional[datetime] = Field(None, description="Start date for analysis")
    end_date: Optional[datetime] = Field(None, description="End date for analysis")
    categories: Optional[List[str]] = Field(None, description="Categories to analyze")


class SpendingAnalysisResponse(BaseModel):
    """Response schema for spending analysis."""
    user_id: int = Field(..., description="ID of the user")
    analysis_period: Dict[str, datetime] = Field(..., description="Analysis period")
    total_spending: float = Field(..., description="Total spending in period")
    category_breakdown: Dict[str, float] = Field(..., description="Spending by category")
    trends: List[str] = Field(..., description="Spending trends and insights")
    recommendations: List[str] = Field(..., description="Personalized recommendations")
    generated_at: datetime = Field(default_factory=datetime.utcnow)


class FinancialHealthScore(BaseModel):
    """Financial health score schema."""
    user_id: int = Field(..., description="ID of the user")
    overall_score: int = Field(..., description="Overall financial health score (0-100)")
    score_breakdown: Dict[str, int] = Field(..., description="Breakdown of scores by category")
    risk_level: str = Field(..., description="Risk level (Low/Medium/High)")
    recommendations: List[str] = Field(..., description="Recommendations to improve financial health")
    generated_at: datetime = Field(default_factory=datetime.utcnow)
