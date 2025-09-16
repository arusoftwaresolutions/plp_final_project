from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple, Union
from decimal import Decimal
import numpy as np
import pandas as pd
import logging
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
from sqlalchemy import select, func, and_, or_, case
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload

from app.models import (
    User, Transaction, TransactionCategory, MicroLoan,
    CrowdFundingCampaign, PovertyArea, Notification
)
from app.schemas.ai import (
    BudgetRecommendation, BudgetCategory, CampaignRecommendation,
    LoanEligibility, PovertyInsight, UserFinancialProfile
)
from app.core.config import settings

logger = logging.getLogger(__name__)

class AIService:
    """AI Service for generating recommendations and insights."""
    
    def __init__(self):
        self.budget_model = None
        self.campaign_model = None
        self.loan_model = None
        self.poverty_model = None
        self.vectorizer = TfidfVectorizer(stop_words='english')
        self._models_trained = False
        self.scaler = StandardScaler()
        self.label_encoders = {}
    
    async def _get_user_financial_profile(self, db: AsyncSession, user_id: int) -> UserFinancialProfile:
        """Get comprehensive financial profile for a user."""
        try:
            # Get user data with related transactions and loans
            result = await db.execute(
                select(User)
                .options(
                    selectinload(User.transactions),
                    selectinload(User.loans)
                )
                .where(User.id == user_id)
            )
            user = result.scalars().first()
            
            if not user:
                raise ValueError(f"User with ID {user_id} not found")
            
            # Calculate financial metrics
            total_income = sum(
                t.amount for t in user.transactions 
                if t.transaction_type == 'INCOME' and t.status == 'COMPLETED'
            )
            
            total_expenses = sum(
                abs(t.amount) for t in user.transactions 
                if t.transaction_type == 'EXPENSE' and t.status == 'COMPLETED'
            )
            
            # Get active loans
            active_loans = [
                loan for loan in user.loans 
                if loan.status in ['ACTIVE', 'APPROVED']
            ]
            
            total_debt = sum(loan.remaining_amount for loan in active_loans)
            
            # Calculate credit score (simplified)
            credit_score = max(300, min(850, 700 - (len(active_loans) * 20) + (total_income // 1000)))
            
            return UserFinancialProfile(
                user_id=user_id,
                total_income=float(total_income),
                total_expenses=float(total_expenses),
                total_debt=float(total_debt),
                credit_score=credit_score,
                active_loans=len(active_loans)
            )
            
        except Exception as e:
            logger.error(f"Error getting financial profile for user {user_id}: {str(e)}")
            raise
    
    async def train_models(self, db: AsyncSession) -> None:
        """Train machine learning models with the latest data."""
        # This would be called periodically (e.g., daily) to retrain models
        await self._train_budget_model(db)
        await self._train_campaign_model(db)
        await self._train_loan_model(db)
        self._models_trained = True
    
    def _get_default_budget_recommendation(self, profile: UserFinancialProfile, time_period: str) -> BudgetRecommendation:
        """Generate default budget recommendations based on financial best practices."""
        total_income = profile.total_income or 1  # Avoid division by zero
        
        # Default budget categories with recommended percentages
        budget_categories = [
            ('HOUSING', 0.25, 'Housing costs should not exceed 25% of income'),
            ('FOOD', 0.15, 'Groceries and dining out'),
            ('TRANSPORTATION', 0.10, 'Commuting and vehicle expenses'),
            ('UTILITIES', 0.10, 'Electricity, water, internet, etc.'),
            ('HEALTHCARE', 0.05, 'Medical expenses and insurance'),
            ('SAVINGS', 0.20, 'Emergency fund and investments'),
            ('DEBT', 0.15, 'Credit cards and loan payments'),
            ('ENTERTAINMENT', 0.05, 'Leisure activities'),
            ('OTHER', 0.05, 'Miscellaneous expenses')
        ]
        
        categories = []
        for category, pct, description in budget_categories:
            categories.append(BudgetCategory(
                category=category,
                current_amount=0.0,
                suggested_max=float(total_income * pct),
                recommendation=f"Recommended {pct*100}% of income for {category.lower()}",
                description=description
            ))
        
        return BudgetRecommendation(
            user_id=profile.user_id,
            time_period=time_period,
            total_income=float(total_income),
            current_monthly_spending=0.0,
            categories=categories,
            generated_at=datetime.utcnow(),
            is_default=True
        )
    
    async def check_loan_eligibility(
        self,
        db: AsyncSession,
        user_id: int,
        loan_amount: float,
        loan_duration_months: int
    ) -> LoanEligibility:
        """Check if a user is eligible for a loan and provide terms."""
        try:
            # Get user's financial profile
            profile = await self._get_user_financial_profile(db, user_id)
            
            # Basic eligibility criteria
            if profile.credit_score < 600:
                return LoanEligibility(
                    is_eligible=False,
                    reason="Credit score is too low (minimum 600 required)",
                    max_eligible_amount=0.0,
                    recommended_amount=0.0,
                    interest_rate=0.0,
                    monthly_payment=0.0
                )
            
            # Calculate debt-to-income ratio
            monthly_income = profile.total_income / 12 if profile.total_income > 0 else 0
            monthly_debt_payments = sum(
                loan.monthly_payment for loan in profile.active_loans
            )
            
            # Calculate new loan's monthly payment (estimate)
            interest_rate = self._calculate_interest_rate(profile.credit_score)
            monthly_interest_rate = interest_rate / 12 / 100
            new_loan_payment = (loan_amount * monthly_interest_rate * 
                              (1 + monthly_interest_rate) ** loan_duration_months) / \
                             ((1 + monthly_interest_rate) ** loan_duration_months - 1)
            
            # Calculate new DTI
            total_monthly_debt = monthly_debt_payments + new_loan_payment
            dti = (total_monthly_debt / monthly_income) if monthly_income > 0 else float('inf')
            
            # Check DTI threshold (typically should be < 43%)
            if dti > 0.43:
                # Calculate maximum affordable payment
                max_affordable_payment = (monthly_income * 0.43) - monthly_debt_payments
                if max_affordable_payment <= 0:
                    return LoanEligibility(
                        is_eligible=False,
                        reason="Debt-to-income ratio too high with existing loans",
                        max_eligible_amount=0.0,
                        recommended_amount=0.0,
                        interest_rate=0.0,
                        monthly_payment=0.0
                    )
                
                # Calculate maximum loan amount
                max_loan_amount = (max_affordable_payment * 
                                 ((1 + monthly_interest_rate) ** loan_duration_months - 1)) / \
                                (monthly_interest_rate * (1 + monthly_interest_rate) ** loan_duration_months)
                
                return LoanEligibility(
                    is_eligible=False,
                    reason=f"Loan amount too high. Maximum recommended: ${max_loan_amount:,.2f}",
                    max_eligible_amount=float(max_loan_amount),
                    recommended_amount=float(max_loan_amount * 0.8),  # 80% of max as recommendation
                    interest_rate=float(interest_rate),
                    monthly_payment=float(max_loan_amount * monthly_interest_rate * 
                                       (1 + monthly_interest_rate) ** loan_duration_months / 
                                       ((1 + monthly_interest_rate) ** loan_duration_months - 1))
                )
            
            # If we get here, the loan is approved
            return LoanEligibility(
                is_eligible=True,
                reason="Loan approved based on credit score and DTI ratio",
                max_eligible_amount=float(loan_amount * 1.5),  # Can potentially get more
                recommended_amount=float(loan_amount),
                interest_rate=float(interest_rate),
                monthly_payment=float(new_loan_payment)
            )
            
        except Exception as e:
            logger.error(f"Error checking loan eligibility for user {user_id}: {str(e)}")
            raise
    
    def _calculate_interest_rate(self, credit_score: int) -> float:
        """Calculate interest rate based on credit score."""
        if credit_score >= 800:
            return 8.0  # Prime rate
        elif 740 <= credit_score < 800:
            return 10.0
        elif 670 <= credit_score < 740:
            return 12.0
        elif 600 <= credit_score < 670:
            return 15.0
        else:
            return 20.0  # Subprime
            
    async def get_campaign_recommendations(
        self,
        db: AsyncSession,
        user_id: int,
        limit: int = 5
    ) -> List[CampaignRecommendation]:
        """Get personalized campaign recommendations for a user."""
        try:
            # Get user's interests and past donations
            result = await db.execute(
                select(User)
                .options(
                    selectinload(User.donations)
                    .selectinload(Donation.campaign)
                )
                .where(User.id == user_id)
            )
            user = result.scalars().first()
            
            if not user:
                raise ValueError(f"User with ID {user_id} not found")
            
            # Get active campaigns
            result = await db.execute(
                select(CrowdFundingCampaign)
                .where(
                    and_(
                        CrowdFundingCampaign.status == 'ACTIVE',
                        CrowdFundingCampaign.end_date > datetime.utcnow()
                    )
                )
                .options(selectinload(CrowdFundingCampaign.category))
                .order_by(CrowdFundingCampaign.created_at.desc())
                .limit(100)  # Get recent campaigns to choose from
            )
            campaigns = result.scalars().all()
            
            if not campaigns:
                return []
            
            # Simple recommendation: prioritize campaigns similar to past donations
            user_categories = {}
            for donation in user.donations:
                if donation.campaign and donation.campaign.category:
                    cat = donation.campaign.category.name
                    user_categories[cat] = user_categories.get(cat, 0) + 1
            
            # Score campaigns based on user's interests
            scored_campaigns = []
            for campaign in campaigns:
                score = 0
                
                # Boost score if category matches user's interests
                if campaign.category and campaign.category.name in user_categories:
                    score += user_categories[campaign.category.name] * 10
                
                # Boost new campaigns
                if (datetime.utcnow() - campaign.created_at).days < 7:
                    score += 5
                
                # Boost campaigns close to their funding goal
                if campaign.current_amount > 0:
                    progress = campaign.current_amount / campaign.target_amount
                    if 0.7 <= progress < 1.0:  # Almost funded
                        score += 8
                    elif 0.5 <= progress < 0.7:  # Halfway there
                        score += 5
                
                scored_campaigns.append((campaign, score))
            
            # Sort by score and take top recommendations
            scored_campaigns.sort(key=lambda x: x[1], reverse=True)
            
            recommendations = []
            for campaign, score in scored_campaigns[:limit]:
                recommendations.append(CampaignRecommendation(
                    campaign_id=campaign.id,
                    title=campaign.title,
                    description=campaign.description,
                    current_amount=float(campaign.current_amount),
                    target_amount=float(campaign.target_amount),
                    end_date=campaign.end_date,
                    category=campaign.category.name if campaign.category else "General",
                    match_score=float(score / 100),  # Normalize to 0-1
                    reason="Matches your interests" if score > 0 else "Popular in your area"
                ))
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating campaign recommendations: {str(e)}")
            return []
    
    async def get_poverty_insights(
        self,
        db: AsyncSession,
        area_id: Optional[int] = None
    ) -> List[PovertyInsight]:
        """Get insights about poverty in specific areas or globally."""
        try:
            insights = []
            
            # Get poverty statistics
            query = select(PovertyArea)
            if area_id:
                query = query.where(PovertyArea.id == area_id)
            
            result = await db.execute(query)
            areas = result.scalars().all()
            
            for area in areas:
                # Calculate basic statistics
                total_population = area.population
                poverty_rate = area.poverty_rate
                avg_income = area.average_income
                
                # Generate insights
                insight_texts = []
                
                if poverty_rate > 30:
                    insight_texts.append(
                        f"High poverty rate of {poverty_rate}% indicates significant "
                        f"economic challenges in this area."
                    )
                
                if avg_income < 20000:
                    insight_texts.append(
                        f"Low average income (${avg_income:,.0f}) suggests limited "
                        f"economic opportunities for residents."
                    )
                
                # Add employment insights if data available
                if hasattr(area, 'unemployment_rate') and area.unemployment_rate > 10:
                    insight_texts.append(
                        f"High unemployment rate ({area.unemployment_rate}%) is contributing "
                        f"to economic hardship in the area."
                    )
                
                # Add education insights if data available
                if hasattr(area, 'education_level') and area.education_level < 50:
                    insight_texts.append(
                        "Low education levels may be limiting economic mobility "
                        "for residents in this area."
                    )
                
                # If no specific insights, add a general one
                if not insight_texts:
                    insight_texts.append(
                        "This area shows moderate economic indicators. "
                        "Targeted interventions could help improve conditions."
                    )
                
                insights.append(PovertyInsight(
                    area_id=area.id,
                    area_name=area.name,
                    poverty_rate=float(poverty_rate),
                    average_income=float(avg_income),
                    population=int(total_population),
                    insights=insight_texts,
                    generated_at=datetime.utcnow()
                ))
            
            return insights
            
        except Exception as e:
            logger.error(f"Error generating poverty insights: {str(e)}")
            return []
    
    async def get_budget_recommendation(
        self,
        db: AsyncSession,
        user_id: int,
        time_period: str = "monthly"
    ) -> BudgetRecommendation:
        """
        Generate personalized budget recommendations based on user's spending patterns.
        
        Args:
            db: Database session
            user_id: ID of the user
            time_period: Time period for the budget ('weekly', 'monthly', 'yearly')
            
        Returns:
            BudgetRecommendation object with personalized budget suggestions
        """
        try:
            # Get user's financial profile
            profile = await self._get_user_financial_profile(db, user_id)
            
            # Get user's transaction history
            result = await db.execute(
                select(Transaction)
                .where(
                    and_(
                        Transaction.user_id == user_id,
                        Transaction.status == 'COMPLETED',
                        Transaction.transaction_date >= datetime.utcnow() - timedelta(days=90)
                    )
                )
                .options(selectinload(Transaction.category))
            )
            transactions = result.scalars().all()
            
            # If no transactions, return default recommendations
            if not transactions:
                return self._get_default_budget_recommendation(profile, time_period)
                
            # Categorize transactions
            categories = {}
            for t in transactions:
                category_name = t.category.name if t.category else 'OTHER'
                if category_name not in categories:
                    categories[category_name] = {
                        'amount': 0,
                        'count': 0,
                        'transactions': []
                    }
                categories[category_name]['amount'] += abs(t.amount)
                categories[category_name]['count'] += 1
                categories[category_name]['transactions'].append(t)
            
            # Calculate average spending by category
            avg_monthly_spending = {}
            for category, data in categories.items():
                # Average over 3 months
                avg_monthly_spending[category] = data['amount'] / 3
            
            # Generate recommendations
            recommendations = []
            total_income = profile.total_income or 1  # Avoid division by zero
            
            # Common budget categories with recommended percentages
            budget_categories = [
                ('HOUSING', 0.25, 'Housing costs should not exceed 25% of income'),
                ('FOOD', 0.15, 'Groceries and dining out'),
                ('TRANSPORTATION', 0.10, 'Commuting and vehicle expenses'),
                ('UTILITIES', 0.10, 'Electricity, water, internet, etc.'),
                ('HEALTHCARE', 0.05, 'Medical expenses and insurance'),
                ('SAVINGS', 0.20, 'Emergency fund and investments'),
                ('DEBT', 0.15, 'Credit cards and loan payments'),
                ('ENTERTAINMENT', 0.05, 'Leisure activities'),
                ('OTHER', 0.05, 'Miscellaneous expenses')
            ]
            
            # Adjust based on user's actual spending
            for category, default_pct, description in budget_categories:
                current_pct = (avg_monthly_spending.get(category, 0) / total_income) if total_income > 0 else 0
                
                # If user is spending significantly more than recommended
                if current_pct > default_pct * 1.5:
                    recommendation = f"Consider reducing {category.lower()} expenses. " \
                                   f"You're spending {current_pct*100:.1f}% of your income " \
                                   f"(recommended: {default_pct*100}%)."
                    suggested_max = total_income * default_pct
                else:
                    recommendation = f"Your {category.lower()} spending is within recommended limits."
                    suggested_max = total_income * default_pct
                
                recommendations.append(BudgetCategory(
                    category=category,
                    current_amount=float(avg_monthly_spending.get(category, 0)),
                    suggested_max=float(suggested_max),
                    recommendation=recommendation,
                    description=description
                ))
            
            # Calculate total suggested budget
            total_suggested = sum(c.suggested_max for c in recommendations)
            
            # Adjust if total exceeds 100%
            if total_suggested > total_income * 0.95:  # Allow 5% buffer
                adjustment_factor = (total_income * 0.95) / total_suggested
                for cat in recommendations:
                    cat.suggested_max *= adjustment_factor
            
            return BudgetRecommendation(
                user_id=user_id,
                time_period=time_period,
                total_income=float(total_income),
                current_monthly_spending=float(sum(avg_monthly_spending.values())),
                categories=recommendations,
                generated_at=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"Error generating budget recommendation for user {user_id}: {str(e)}")
            raise
        """Generate personalized budget recommendations for a user."""
        if not self._models_trained:
            await self.train_models(db)
        
        # Get user's recent transactions
        end_date = datetime.utcnow()
        if time_period == "weekly":
            start_date = end_date - timedelta(days=7)
        elif time_period == "monthly":
            start_date = end_date - timedelta(days=30)
        else:  # yearly
            start_date = end_date - timedelta(days=365)
        
        # Get transactions for the period
        result = await db.execute(
            select(
                TransactionCategory.name,
                TransactionCategory.type,
                func.sum(Transaction.amount).label("total_amount")
            )
            .join(Transaction.category)
            .filter(
                Transaction.user_id == user_id,
                Transaction.transaction_date >= start_date,
                Transaction.transaction_date <= end_date
            )
            .group_by(TransactionCategory.name, TransactionCategory.type)
        )
        
        categories = []
        total_income = Decimal('0')
        total_expenses = Decimal('0')
        
        for name, trans_type, amount in result.all():
            amount = Decimal(str(amount or '0'))
            if trans_type == "income":
                total_income += amount
            else:
                total_expenses += amount
            
            categories.append(BudgetCategory(
                name=name,
                type=trans_type,
                amount=amount,
                percentage=(
                    (amount / total_income * 100) if trans_type == "expense" and total_income > 0 else 0
                )
            ))
        
        # Generate recommendations (simplified example)
        savings_rate = ((total_income - total_expenses) / total_income * 100) if total_income > 0 else 0
        
        recommendations = []
        if savings_rate < 10:
            recommendations.append("Consider increasing your savings rate to at least 10% of your income.")
        
        # Find largest expense categories
        expense_categories = [c for c in categories if c.type == "expense"]
        if expense_categories:
            largest_expense = max(expense_categories, key=lambda x: x.amount)
            if largest_expense.amount / total_income > 0.3:  # If largest expense is >30% of income
                recommendations.append(
                    f"Your {largest_expense.name} expenses are quite high. "
                    f"Consider ways to reduce this category."
                )
        
        return BudgetRecommendation(
            categories=categories,
            total_income=total_income,
            total_expenses=total_expenses,
            savings_rate=float(savings_rate),
            recommendations=recommendations,
            time_period=time_period,
            generated_at=datetime.utcnow()
        )
    
    async def get_campaign_recommendations(
        self,
        db: AsyncSession,
        user_id: int,
        limit: int = 5
    ) -> List[CampaignRecommendation]:
        """Get personalized campaign recommendations for a user."""
        if not self._models_trained:
            await self.train_models(db)
        
        # Get user's past donations and interests (simplified example)
        result = await db.execute(
            select(CrowdFundingCampaign)
            .filter(CrowdFundingCampaign.status == "active")
            .order_by(func.random())  # In a real app, this would use ML ranking
            .limit(limit)
        )
        
        campaigns = result.scalars().all()
        
        return [
            CampaignRecommendation(
                campaign_id=campaign.id,
                title=campaign.title,
                description=campaign.description[:200] + "..." if campaign.description else "",
                image_url=campaign.image_url,
                amount_raised=campaign.amount_raised,
                target_amount=campaign.target_amount,
                progress=(campaign.amount_raised / campaign.target_amount * 100) if campaign.target_amount > 0 else 0,
                days_left=(campaign.end_date - datetime.utcnow()).days
            )
            for campaign in campaigns
        ]
    
    async def check_loan_eligibility(
        self,
        db: AsyncSession,
        user_id: int,
        loan_amount: Decimal,
        loan_term: int
    ) -> LoanEligibility:
        """Check if a user is eligible for a loan and provide terms."""
        if not self._models_trained:
            await self.train_models(db)
        
        # Get user's financial data
        user = await db.get(User, user_id)
        if not user:
            raise ValueError("User not found")
        
        # Get user's income (simplified: sum of income transactions from last 3 months)
        income_result = await db.execute(
            select(func.sum(Transaction.amount))
            .join(TransactionCategory)
            .filter(
                Transaction.user_id == user_id,
                TransactionCategory.type == "income",
                Transaction.transaction_date >= datetime.utcnow() - timedelta(days=90)
            )
        )
        
        monthly_income = (income_result.scalar() or 0) / 3  # Average monthly income
        
        # Get user's expenses (simplified: average from last 3 months)
        expense_result = await db.execute(
            select(func.sum(Transaction.amount))
            .join(TransactionCategory)
            .filter(
                Transaction.user_id == user_id,
                TransactionCategory.type == "expense",
                Transaction.transaction_date >= datetime.utcnow() - timedelta(days=90)
            )
        )
        
        monthly_expenses = (expense_result.scalar() or 0) / 3  # Average monthly expenses
        
        # Simple eligibility check (in a real app, this would use a trained model)
        disposable_income = monthly_income - monthly_expenses
        max_affordable_payment = disposable_income * Decimal('0.4')  # Max 40% of disposable income
        
        # Calculate monthly payment (simple interest for example)
        annual_interest_rate = Decimal('0.12')  # 12% annual interest
        monthly_rate = annual_interest_rate / 12
        monthly_payment = (
            loan_amount * 
            (monthly_rate * (1 + monthly_rate) ** loan_term) / 
            ((1 + monthly_rate) ** loan_term - 1)
        )
        
        is_eligible = monthly_payment <= max_affordable_payment
        
        # Generate explanation
        explanation = []
        if is_eligible:
            explanation.append("Your income and expenses suggest you can afford this loan.")
        else:
            explanation.append(
                "Based on your current income and expenses, this loan payment would be "
                f"{monthly_payment:.2f}, which exceeds the recommended maximum of "
                f"{max_affordable_payment:.2f} (40% of your disposable income)."
            )
        
        return LoanEligibility(
            is_eligible=is_eligible,
            recommended_amount=float(loan_amount) if is_eligible else float(max_affordable_payment * loan_term * Decimal('0.8')),  # 80% of max
            interest_rate=float(annual_interest_rate * 100),  # As percentage
            monthly_payment=float(monthly_payment),
            loan_term=loan_term,
            explanation=explanation,
            generated_at=datetime.utcnow()
        )
    
    async def get_poverty_insights(
        self,
        db: AsyncSession,
        area_id: Optional[int] = None,
        region: Optional[str] = None
    ) -> List[PovertyInsight]:
        """Generate insights about poverty in a specific area or region."""
        query = select(PovertyArea)
        
        if area_id:
            query = query.filter(PovertyArea.id == area_id)
        elif region:
            query = query.filter(PovertyArea.region == region)
        else:
            # Default to global insights if no filter
            pass
        
        result = await db.execute(query)
        areas = result.scalars().all()
        
        if not areas:
            return []
        
        # Calculate basic statistics
        total_population = sum(area.population or 0 for area in areas)
        avg_poverty_rate = np.mean([area.poverty_rate or 0 for area in areas])
        
        # Count needs (flatten all needs lists and count occurrences)
        needs_count = {}
        for area in areas:
            for need in area.needs or []:
                needs_count[need] = needs_count.get(need, 0) + 1
        
        # Generate insights
        insights = []
        
        # Insight 1: Overall poverty rate
        insights.append(PovertyInsight(
            title=f"Poverty Rate in {areas[0].name if area_id else region or 'Selected Areas'}",
            description=f"The average poverty rate is {avg_poverty_rate:.1f}%" + 
                       (f" in {areas[0].name}" if area_id else ""),
            metric=float(avg_poverty_rate),
            metric_unit="%",
            trend="stable",  # In a real app, this would compare with historical data
            related_data={
                "total_areas": len(areas),
                "total_population": total_population,
                "poverty_population": int(total_population * (avg_poverty_rate / 100))
            }
        ))
        
        # Insight 2: Most common needs
        if needs_count:
            most_common_need, need_count = max(needs_count.items(), key=lambda x: x[1])
            percentage = (need_count / len(areas)) * 100
            
            insights.append(PovertyInsight(
                title="Most Pressing Need",
                description=f"{most_common_need} is the most common need, "
                          f"affecting {percentage:.1f}% of areas",
                metric=float(percentage),
                metric_unit="% of areas",
                trend="increasing" if percentage > 50 else "stable",
                related_data={
                    "need": most_common_need,
                    "areas_affected": need_count,
                    "total_areas": len(areas)
                }
            ))
        
        # Insight 3: Population density vs poverty (example)
        if len(areas) > 1:  # Only if we have multiple areas
            pop_density_poverty = [
                ((area.population or 0) / (area.area_km2 or 1), area.poverty_rate or 0)
                for area in areas if area.area_km2 and area.population
            ]
            
            if pop_density_poverty:
                densities, poverty_rates = zip(*pop_density_poverty)
                correlation = np.corrcoef(densities, poverty_rates)[0, 1]
                
                if abs(correlation) > 0.3:  # Moderate correlation
                    trend = "increasing" if correlation > 0 else "decreasing"
                    insights.append(PovertyInsight(
                        title="Population Density and Poverty",
                        description=(
                            f"There is a {trend} relationship between population density and poverty rates "
                            f"(correlation: {correlation:.2f})."
                        ),
                        metric=float(correlation),
                        metric_unit="correlation",
                        trend=trend,
                        related_data={
                            "correlation_strength": "moderate" if 0.3 <= abs(correlation) < 0.7 else "strong",
                            "relationship": "positive" if correlation > 0 else "negative"
                        }
                    ))
        
        return insights
    
    async def _train_budget_model(self, db: AsyncSession) -> None:
        """Train the budget recommendation model."""
        # In a real implementation, this would train an ML model on historical data
        # This is a placeholder that would be replaced with actual model training code
        pass
    
    async def _train_campaign_model(self, db: AsyncSession) -> None:
        """Train the campaign recommendation model."""
        # In a real implementation, this would train an ML model on user behavior
        # This is a placeholder that would be replaced with actual model training code
        pass
    
    async def _train_loan_model(self, db: AsyncSession) -> None:
        """Train the loan eligibility model."""
        # In a real implementation, this would train an ML model on loan repayment history
        # This is a placeholder that would be replaced with actual model training code
        pass

# Create a singleton instance of the AI service
ai_service = AIService()
