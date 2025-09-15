from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import User, FamilyProfile, Transaction, AIRecommendation
from schemas import AIRecommendation as AIRecommendationSchema
from auth import get_current_user
from typing import List
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import joblib
import os
from datetime import datetime, timedelta

router = APIRouter()

def generate_ai_recommendations(family_id: str, db: Session):
    """Generate AI-powered budgeting recommendations for a family"""
    # Get family profile
    family = db.query(FamilyProfile).filter(FamilyProfile.id == family_id).first()
    if not family:
        return []
    
    # Get recent transactions (last 3 months)
    three_months_ago = datetime.utcnow() - timedelta(days=90)
    transactions = db.query(Transaction).filter(
        Transaction.family_id == family_id,
        Transaction.date >= three_months_ago
    ).all()
    
    recommendations = []
    
    if not transactions:
        # No transaction data - provide general recommendations
        recommendations.append({
            "recommendation_type": "budgeting",
            "title": "Start Tracking Your Expenses",
            "description": "Begin by tracking all your income and expenses to understand your spending patterns.",
            "priority": "high"
        })
        return recommendations
    
    # Calculate spending patterns
    income_transactions = [t for t in transactions if t.transaction_type == "income"]
    expense_transactions = [t for t in transactions if t.transaction_type == "expense"]
    
    total_income = sum(t.amount for t in income_transactions)
    total_expenses = sum(t.amount for t in expense_transactions)
    
    # Calculate spending by category
    category_spending = {}
    for t in expense_transactions:
        category_spending[t.category] = category_spending.get(t.category, 0) + t.amount
    
    # Generate recommendations based on spending patterns
    if total_expenses > total_income * 0.8:
        recommendations.append({
            "recommendation_type": "budgeting",
            "title": "High Spending Alert",
            "description": f"Your expenses (${total_expenses:.2f}) are {((total_expenses/total_income)*100):.1f}% of your income. Consider reducing discretionary spending.",
            "priority": "high"
        })
    
    # Find highest spending category
    if category_spending:
        highest_category = max(category_spending, key=category_spending.get)
        highest_amount = category_spending[highest_category]
        
        if highest_amount > total_income * 0.3:
            recommendations.append({
                "recommendation_type": "category_optimization",
                "title": f"Optimize {highest_category.title()} Spending",
                "description": f"You're spending ${highest_amount:.2f} on {highest_category}, which is {((highest_amount/total_income)*100):.1f}% of your income. Look for ways to reduce this expense.",
                "priority": "medium"
            })
    
    # Emergency fund recommendation
    if total_income > 0:
        monthly_income = total_income / 3  # Approximate monthly income
        emergency_fund_target = monthly_income * 3  # 3 months of expenses
        
        recommendations.append({
            "recommendation_type": "savings",
            "title": "Build Emergency Fund",
            "description": f"Consider building an emergency fund of ${emergency_fund_target:.2f} (3 months of income) for financial security.",
            "priority": "medium"
        })
    
    # Save recommendations to database
    for rec in recommendations:
        db_recommendation = AIRecommendation(
            family_id=family_id,
            recommendation_type=rec["recommendation_type"],
            title=rec["title"],
            description=rec["description"],
            priority=rec["priority"]
        )
        db.add(db_recommendation)
    
    db.commit()
    return recommendations

@router.post("/generate-recommendations")
def generate_recommendations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.user_type != "family":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only family users can generate AI recommendations"
        )
    
    family_profile = db.query(FamilyProfile).filter(FamilyProfile.user_id == current_user.id).first()
    if not family_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Family profile not found"
        )
    
    recommendations = generate_ai_recommendations(family_profile.id, db)
    
    return {"message": f"Generated {len(recommendations)} recommendations", "recommendations": recommendations}

@router.get("/recommendations", response_model=List[AIRecommendationSchema])
def get_recommendations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.user_type != "family":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only family users can access AI recommendations"
        )
    
    family_profile = db.query(FamilyProfile).filter(FamilyProfile.user_id == current_user.id).first()
    if not family_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Family profile not found"
        )
    
    recommendations = db.query(AIRecommendation).filter(
        AIRecommendation.family_id == family_profile.id
    ).order_by(AIRecommendation.created_at.desc()).all()
    
    return recommendations

@router.put("/recommendations/{recommendation_id}/read")
def mark_recommendation_read(
    recommendation_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.user_type != "family":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only family users can mark recommendations as read"
        )
    
    family_profile = db.query(FamilyProfile).filter(FamilyProfile.user_id == current_user.id).first()
    if not family_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Family profile not found"
        )
    
    recommendation = db.query(AIRecommendation).filter(
        AIRecommendation.id == recommendation_id,
        AIRecommendation.family_id == family_profile.id
    ).first()
    
    if not recommendation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recommendation not found"
        )
    
    recommendation.is_read = True
    db.commit()
    
    return {"message": "Recommendation marked as read"}

@router.get("/budget-forecast")
def get_budget_forecast(
    months: int = 6,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.user_type != "family":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only family users can access budget forecasts"
        )
    
    family_profile = db.query(FamilyProfile).filter(FamilyProfile.user_id == current_user.id).first()
    if not family_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Family profile not found"
        )
    
    # Get recent transactions for forecasting
    six_months_ago = datetime.utcnow() - timedelta(days=180)
    transactions = db.query(Transaction).filter(
        Transaction.family_id == family_profile.id,
        Transaction.date >= six_months_ago
    ).all()
    
    if not transactions:
        return {"message": "Insufficient data for forecasting"}
    
    # Simple forecasting based on historical averages
    monthly_income = sum(t.amount for t in transactions if t.transaction_type == "income") / 6
    monthly_expenses = sum(t.amount for t in transactions if t.transaction_type == "expense") / 6
    
    forecast = []
    for i in range(months):
        month = datetime.utcnow() + timedelta(days=30*i)
        forecast.append({
            "month": month.strftime("%Y-%m"),
            "projected_income": monthly_income,
            "projected_expenses": monthly_expenses,
            "projected_savings": monthly_income - monthly_expenses
        })
    
    return {
        "forecast": forecast,
        "average_monthly_income": monthly_income,
        "average_monthly_expenses": monthly_expenses,
        "average_monthly_savings": monthly_income - monthly_expenses
    }

