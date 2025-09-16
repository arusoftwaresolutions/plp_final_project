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
