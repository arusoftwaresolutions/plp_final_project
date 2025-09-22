"""
Dashboard API endpoints
"""

from datetime import datetime, timedelta
from typing import List, Dict
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from app.database import User, Transaction, Campaign, LoanApplication, get_db
from app.auth import get_current_user
from app.ai_module import financial_ai

router = APIRouter()

@router.get("/")
async def get_dashboard_data(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get dashboard overview data"""

    # Get current month's transactions
    start_of_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    end_of_month = (start_of_month + timedelta(days=32)).replace(day=1) - timedelta(seconds=1)

    transactions = db.query(Transaction).filter(
        Transaction.user_id == current_user.id,
        Transaction.date >= start_of_month
    ).all()

    # Calculate financial metrics
    total_income = sum(t.amount for t in transactions if t.type == 'income')
    total_expenses = sum(abs(t.amount) for t in transactions if t.type == 'expense')
    balance = total_income - total_expenses

    # Get recent transactions
    recent_transactions = db.query(Transaction).filter(
        Transaction.user_id == current_user.id
    ).order_by(desc(Transaction.date)).limit(10).all()

    # Get user's campaigns
    user_campaigns = db.query(Campaign).filter(
        Campaign.creator_id == current_user.id
    ).all()

    # Get loan applications
    loan_applications = db.query(LoanApplication).filter(
        LoanApplication.user_id == current_user.id
    ).all()

    # AI analysis
    ai_insights = financial_ai.analyze_spending_patterns(
        [t.__dict__ for t in transactions],
        current_user.monthly_income
    )

    return {
        "balance": balance,
        "monthly_income": total_income,
        "monthly_expenses": total_expenses,
        "savings": current_user.monthly_income - total_expenses if current_user.monthly_income > 0 else 0,
        "recent_transactions": recent_transactions,
        "user_campaigns": user_campaigns,
        "loan_applications": loan_applications,
        "ai_recommendations": ai_insights.get("recommendations", []),
        "spending_analysis": {
            "total_expenses": ai_insights.get("total_expenses", 0),
            "category_breakdown": ai_insights.get("category_breakdown", {}),
            "spending_ratio": ai_insights.get("spending_ratio", 0)
        }
    }

@router.get("/charts")
async def get_dashboard_charts(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get data for dashboard charts"""

    # Last 6 months data
    chart_data = []
    current_date = datetime.now()

    for i in range(5, -1, -1):
        month_start = (current_date.replace(day=1) - timedelta(days=i * 30)).replace(day=1)
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(seconds=1)

        transactions = db.query(Transaction).filter(
            Transaction.user_id == current_user.id,
            Transaction.date >= month_start,
            Transaction.date <= month_end
        ).all()

        income = sum(t.amount for t in transactions if t.type == 'income')
        expenses = sum(abs(t.amount) for t in transactions if t.type == 'expense')

        chart_data.append({
            "month": month_start.strftime("%B %Y"),
            "income": income,
            "expenses": expenses,
            "balance": income - expenses
        })

    return chart_data

@router.get("/goals")
async def get_financial_goals(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get user's financial goals and progress"""

    # Calculate current savings
    transactions = db.query(Transaction).filter(
        Transaction.user_id == current_user.id,
        Transaction.category == 'savings'
    ).all()

    total_savings = sum(abs(t.amount) for t in transactions if t.type == 'income')

    # Define sample goals (in real app, these would be stored in DB)
    goals = [
        {
            "id": 1,
            "title": "Emergency Fund",
            "target_amount": current_user.monthly_income * 6,  # 6 months of income
            "current_amount": total_savings,
            "target_date": datetime.now() + timedelta(days=365),
            "category": "emergency"
        },
        {
            "id": 2,
            "title": "Monthly Savings Goal",
            "target_amount": current_user.monthly_income * 0.2,  # 20% of income
            "current_amount": total_savings,
            "target_date": datetime.now() + timedelta(days=30),
            "category": "monthly"
        }
    ]

    return goals

@router.get("/community-impact")
async def get_community_impact(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get community impact metrics"""

    # Total contributions made by user
    total_contributions = db.query(func.sum(Transaction.amount)).filter(
        Transaction.user_id == current_user.id,
        Transaction.type == 'expense',
        Transaction.category == 'charity'
    ).scalar() or 0

    # Campaigns created by user
    campaigns_count = db.query(Campaign).filter(
        Campaign.creator_id == current_user.id
    ).count()

    # Loans received
    loans_received = db.query(LoanApplication).filter(
        LoanApplication.user_id == current_user.id,
        LoanApplication.status == 'approved'
    ).count()

    return {
        "total_contributions": total_contributions,
        "campaigns_created": campaigns_count,
        "loans_received": loans_received,
        "impact_score": min(100, (total_contributions / 100) + (campaigns_count * 10) + (loans_received * 5))
    }
