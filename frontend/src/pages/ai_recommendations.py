import random
import time

import streamlit as st

from utils import get_auth_headers, format_currency, format_date

def get_ai_recommendations():
    """Fetch AI-generated financial recommendations."""
    # In a real app, this would call your backend AI service
    # For now, we'll use mock data
    
    # Simulate API call delay
    time.sleep(1)
    
    # Mock recommendations
    recommendations = [
        {
            "title": "Reduce Food Expenses",
            "description": "You're spending 35% of your income on food. Consider meal planning to reduce costs.",
            "impact": "Potential savings: $120/month",
            "difficulty": "Easy",
            "category": "Expense Reduction",
            "icon": "🍽️"
        },
        {
            "title": "Start an Emergency Fund",
            "description": "You don't have an emergency fund. Aim to save 3-6 months of living expenses.",
            "impact": "Financial security during emergencies",
            "difficulty": "Medium",
            "category": "Savings",
            "icon": "💰"
        },
        {
            "title": "Pay Off High-Interest Debt",
            "description": "Focus on paying off your credit card balance to reduce interest payments.",
            "impact": "Save $45/month in interest",
            "difficulty": "High",
            "category": "Debt Management",
            "icon": "💳"
        },
        {
            "title": "Explore Microloans",
            "description": "Consider applying for a microloan to grow your small business.",
            "impact": "Potential income increase",
            "difficulty": "Medium",
            "category": "Income Generation",
            "icon": "📈"
        },
        {
            "title": "Track Daily Expenses",
            "description": "Start tracking every expense to better understand your spending habits.",
            "impact": "Better financial awareness",
            "difficulty": "Easy",
            "category": "Financial Literacy",
            "icon": "📊"
        },
        {
            "title": "Join Community Savings Group",
            "description": "Participate in a local savings group to build discipline and community support.",
            "impact": "Collective savings and support",
            "difficulty": "Easy",
            "category": "Community",
            "icon": "👥"
        }
    ]
    
    # Randomly select 3-5 recommendations
    return random.sample(recommendations, k=random.randint(3, 5))

def show():
    """Show the AI recommendations page."""
    st.title("AI-Powered Recommendations")
    st.markdown("Personalized financial advice to help you achieve your goals.")
    
    # Add a refresh button
    if st.button("🔄 Get New Recommendations"):
        st.experimental_rerun()
    
    # Display loading state
    with st.spinner("Analyzing your financial data..."):
        recommendations = get_ai_recommendations()
    
    # Display recommendations in cards
    for i, rec in enumerate(recommendations, 1):
        with st.container():
            st.markdown(f"""
                <div style="
                    background: white;
                    border-radius: 10px;
                    padding: 1.5rem;
                    margin: 1rem 0;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                ">
                    <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                        <div style="
                            font-size: 2rem;
                            margin-right: 1rem;
                            background: #f0f9ff;
                            width: 3rem;
                            height: 3rem;
                            border-radius: 50%;
                            display: flex;
                            align-items: center;
                            justify-content: center;
                        ">
                            {rec['icon']}
                        </div>
                        <div>
                            <h3 style="margin: 0;">{rec['title']}</h3>
                            <div style="
                                display: inline-block;
                                background: #e0f2fe;
                                color: #0369a1;
                                padding: 0.25rem 0.5rem;
                                border-radius: 1rem;
                                font-size: 0.8rem;
                                margin-top: 0.25rem;
                            ">
                                {rec['category']} • {rec['difficulty']}
                            </div>
                        </div>
                    </div>
                    <p style="color: #4b5563; margin: 0.75rem 0 1rem 0;">
                        {rec['description']}
                    </p>
                    <div style="
                        display: flex;
                        justify-content: space-between;
                        align-items: center;
                        color: #10b981;
                        font-weight: 500;
                        font-size: 0.9rem;
                    ">
                        <span>✨ {rec['impact']}</span>
                        <button style="
                            background: #3b82f6;
                            color: white;
                            border: none;
                            padding: 0.5rem 1rem;
                            border-radius: 0.5rem;
                            cursor: pointer;
                            font-weight: 500;
                        ">
                            Learn More
                        </button>
                    </div>
                </div>
            """, unsafe_allow_html=True)
    
    # Add some space at the bottom
    st.write("")
    st.write("")
    
    # Disclaimer
    st.info("""
        ℹ️ These recommendations are generated by AI based on your financial data. 
        They are for informational purposes only and should not be considered as financial advice.
    """)
    
    # Add custom styles
    st.markdown("""
        <style>
            .stButton>button {
                border-radius: 20px;
                padding: 0.5rem 1.5rem;
                font-weight: 500;
            }
            .stButton>button:hover {
                background-color: #1d4ed8;
                border-color: #1d4ed8;
            }
        </style>
    """, unsafe_allow_html=True)
