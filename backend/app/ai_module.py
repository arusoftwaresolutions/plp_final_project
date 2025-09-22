"""
AI module for financial analysis and recommendations
"""

import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from typing import List, Dict, Tuple
import random

class FinancialAI:
    """AI module for analyzing spending patterns and providing recommendations"""

    def __init__(self):
        """Initialize AI models"""
        self.spending_model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.budget_model = LinearRegression()
        self.scaler = StandardScaler()
        self.is_trained = False

    def train_models(self, historical_data: List[Dict]):
        """Train AI models on historical financial data"""
        if not historical_data:
            return

        # Prepare data for training
        X = []
        y_spending = []
        y_budget = []

        for record in historical_data:
            features = [
                record.get('income', 0),
                record.get('age', 30),
                record.get('family_size', 1),
                record.get('location_risk', 0.5),
                len(record.get('transactions', []))
            ]
            X.append(features)

            # Target variables
            spending_ratio = record.get('spending_ratio', 0.7)
            recommended_budget = record.get('recommended_budget', 0.6)

            y_spending.append(spending_ratio)
            y_budget.append(recommended_budget)

        X = np.array(X)
        y_spending = np.array(y_spending)
        y_budget = np.array(y_budget)

        # Scale features
        X_scaled = self.scaler.fit_transform(X)

        # Train models
        self.spending_model.fit(X_scaled, y_spending)
        self.budget_model.fit(X_scaled, y_budget)

        self.is_trained = True

    def analyze_spending_patterns(self, transactions: List[Dict], monthly_income: float) -> Dict:
        """Analyze user spending patterns and provide insights"""

        if not transactions:
            return {
                "total_expenses": 0,
                "category_breakdown": {},
                "spending_ratio": 0,
                "recommendations": ["Start tracking your expenses to get personalized recommendations."]
            }

        # Calculate totals by category
        category_totals = {}
        total_expenses = 0

        for transaction in transactions:
            category = transaction.get('category', 'other')
            amount = abs(transaction.get('amount', 0))

            if transaction.get('type') == 'expense':
                category_totals[category] = category_totals.get(category, 0) + amount
                total_expenses += amount

        # Calculate spending ratio
        spending_ratio = total_expenses / monthly_income if monthly_income > 0 else 0

        # Generate AI recommendations based on spending patterns
        recommendations = self._generate_recommendations(category_totals, spending_ratio, monthly_income)

        return {
            "total_expenses": total_expenses,
            "category_breakdown": category_totals,
            "spending_ratio": spending_ratio,
            "recommendations": recommendations
        }

    def _generate_recommendations(self, categories: Dict, spending_ratio: float, monthly_income: float) -> List[str]:
        """Generate personalized financial recommendations"""

        recommendations = []

        # Analyze spending ratios by category
        food_spending = categories.get('food', 0)
        transport_spending = categories.get('transport', 0)
        housing_spending = categories.get('housing', 0)
        entertainment_spending = categories.get('entertainment', 0)

        total_expenses = sum(categories.values())

        # Food spending analysis
        if food_spending > 0:
            food_ratio = food_spending / total_expenses
            if food_ratio > 0.3:  # More than 30% on food
                recommendations.append(f"You spent {food_ratio:.1%} of your expenses on food. Consider meal planning to reduce this by 10-15% and save ${(food_spending * 0.15):.2f} monthly.")

        # Transport spending analysis
        if transport_spending > 0:
            transport_ratio = transport_spending / total_expenses
            if transport_ratio > 0.15:  # More than 15% on transport
                recommendations.append(f"Your transportation costs are {transport_ratio:.1%} of total expenses. Consider carpooling or public transport to reduce costs by 20-30%.")

        # Housing analysis
        if housing_spending > 0 and monthly_income > 0:
            housing_ratio = housing_spending / monthly_income
            if housing_ratio > 0.4:  # More than 40% on housing
                recommendations.append(f"Housing costs represent {housing_ratio:.1%} of your income, which is above the recommended 30%. Consider more affordable housing options.")

        # Entertainment analysis
        if entertainment_spending > 0:
            entertainment_ratio = entertainment_spending / total_expenses
            if entertainment_ratio > 0.1:  # More than 10% on entertainment
                recommendations.append(f"Entertainment spending is {entertainment_ratio:.1%} of your budget. Reducing this by 20% could save ${(entertainment_spending * 0.2):.2f} monthly.")

        # Overall spending ratio analysis
        if spending_ratio > 0.8:  # More than 80% spending ratio
            recommendations.append("Your spending ratio is very high. Consider creating a stricter budget and tracking all expenses carefully.")
            recommendations.append("Building an emergency fund should be a priority. Aim to save 10-20% of your income monthly.")
        elif spending_ratio > 0.6:  # More than 60% spending ratio
            recommendations.append(f"Your current spending ratio is {spending_ratio:.1%}. Try to reduce it to 50-60% to improve financial stability.")
        else:
            recommendations.append("Your spending ratio is healthy. Continue monitoring and consider increasing savings.")

        # Savings recommendations
        if monthly_income > 0:
            recommended_savings = monthly_income * 0.2  # 20% savings rate
            current_savings = monthly_income - total_expenses
            if current_savings < recommended_savings:
                shortfall = recommended_savings - current_savings
                recommendations.append(f"Consider saving ${(shortfall):.2f} more monthly to reach the recommended 20% savings rate.")

        # Debt/loan recommendations
        if total_expenses > monthly_income * 0.9:
            recommendations.append("Your expenses are very close to your income. Consider debt consolidation or additional income sources.")

        return recommendations[:5]  # Limit to 5 recommendations

    def predict_optimal_budget(self, user_profile: Dict) -> Dict:
        """Predict optimal budget allocation for a user"""

        if not self.is_trained:
            # Return default budget allocation
            return {
                "housing": 0.3,
                "food": 0.2,
                "transport": 0.1,
                "utilities": 0.1,
                "healthcare": 0.05,
                "savings": 0.2,
                "entertainment": 0.05
            }

        # Prepare features for prediction
        features = np.array([[
            user_profile.get('monthly_income', 1000),
            user_profile.get('age', 30),
            user_profile.get('family_size', 1),
            user_profile.get('location_risk', 0.5),
            user_profile.get('transaction_count', 10)
        ]])

        features_scaled = self.scaler.transform(features)

        # Predict optimal ratios
        spending_ratio = max(0.3, min(0.8, self.spending_model.predict(features_scaled)[0]))
        budget_ratio = max(0.4, min(0.7, self.budget_model.predict(features_scaled)[0]))

        return {
            "spending_ratio": spending_ratio,
            "budget_ratio": budget_ratio,
            "recommended_monthly_budget": user_profile.get('monthly_income', 1000) * budget_ratio
        }

    def generate_loan_recommendations(self, user_profile: Dict, loan_offers: List[Dict]) -> List[Dict]:
        """Generate personalized loan recommendations"""

        recommendations = []

        for offer in loan_offers:
            score = self._calculate_loan_fit_score(user_profile, offer)

            recommendation = {
                "loan_id": offer.get('id'),
                "title": offer.get('title'),
                "fit_score": score,
                "reasoning": self._generate_loan_reasoning(user_profile, offer, score),
                "max_amount": offer.get('max_amount'),
                "interest_rate": offer.get('interest_rate'),
                "term_months": offer.get('max_term_months')
            }

            recommendations.append(recommendation)

        # Sort by fit score (highest first)
        recommendations.sort(key=lambda x: x['fit_score'], reverse=True)

        return recommendations

    def _calculate_loan_fit_score(self, user_profile: Dict, loan_offer: Dict) -> float:
        """Calculate how well a loan fits the user's profile"""

        score = 0.5  # Base score

        # Income vs loan amount
        monthly_income = user_profile.get('monthly_income', 0)
        max_loan_amount = loan_offer.get('max_amount', 0)

        if monthly_income > 0:
            loan_to_income_ratio = max_loan_amount / (monthly_income * 12)
            if loan_to_income_ratio < 2:
                score += 0.2
            elif loan_to_income_ratio < 3:
                score += 0.1

        # Credit score consideration
        user_credit_score = user_profile.get('credit_score', 500)
        min_credit_score = loan_offer.get('min_credit_score', 0)

        if user_credit_score >= min_credit_score:
            score += 0.2

        # Interest rate consideration
        interest_rate = loan_offer.get('interest_rate', 0)
        if interest_rate < 10:
            score += 0.1

        return min(1.0, score)

    def _generate_loan_reasoning(self, user_profile: Dict, loan_offer: Dict, score: float) -> str:
        """Generate reasoning for loan recommendation"""

        monthly_income = user_profile.get('monthly_income', 0)
        max_amount = loan_offer.get('max_amount', 0)

        if score > 0.8:
            return f"Excellent fit! This ${max_amount:.2f} loan matches your ${monthly_income:.2f} monthly income well."
        elif score > 0.6:
            return f"Good match. Consider this loan option for your financial needs."
        elif score > 0.4:
            return f"Moderate fit. Review the terms carefully before applying."
        else:
            return f"May not be the best fit for your current financial situation."

# Global AI instance
financial_ai = FinancialAI()
