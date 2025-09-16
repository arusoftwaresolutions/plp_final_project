import streamlit as st
import plotly.express as px
import pandas as pd
import requests
from datetime import datetime, timedelta
from ..services import api

def show():
    """Display the main dashboard with key metrics and visualizations."""
    st.title("Dashboard")
    
    try:
        # Fetch user data
        user_data = api.get_user_profile()
        transactions = api.get_recent_transactions()
        loan_status = api.get_loan_status()
        
        # Display key metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Balance", f"${user_data.get('balance', 0):,.2f}")
        with col2:
            st.metric("Monthly Income", f"${user_data.get('monthly_income', 0):,.2f}")
        with col3:
            st.metric("Active Loans", user_data.get('active_loans', 0))
        
        # Recent transactions
        st.subheader("Recent Transactions")
        if transactions:
            df = pd.DataFrame(transactions)
            df['date'] = pd.to_datetime(df['date'])
            st.dataframe(
                df[['date', 'description', 'amount', 'category']],
                column_config={
                    'date': 'Date',
                    'description': 'Description',
                    'amount': st.column_config.NumberColumn('Amount', format='$%.2f'),
                    'category': 'Category'
                },
                hide_index=True,
                use_container_width=True
            )
        else:
            st.info("No recent transactions found.")
        
        # Spending by category
        st.subheader("Spending by Category")
        if transactions:
            category_data = df[df['amount'] < 0].groupby('category')['amount'].sum().abs().reset_index()
            if not category_data.empty:
                fig = px.pie(
                    category_data,
                    values='amount',
                    names='category',
                    title='Spending Distribution',
                    hole=0.4
                )
                st.plotly_chart(fig, use_container_width=True)
        
        # Loan status
        if loan_status and 'active_loans' in loan_status and loan_status['active_loans'] > 0:
            st.subheader("Loan Status")
            loan_col1, loan_col2 = st.columns(2)
            with loan_col1:
                st.metric("Total Owed", f"${loan_status.get('total_owed', 0):,.2f}")
            with loan_col2:
                st.metric("Next Payment Due", 
                         loan_status.get('next_payment_date', 'N/A'),
                         f"${loan_status.get('next_payment_amount', 0):,.2f}")
            
            # Loan progress
            if 'loan_id' in loan_status:
                st.progress(loan_status.get('repayment_progress', 0) / 100)
                st.caption(f"Repayment Progress: {loan_status.get('repayment_progress', 0)}%")
        
        # Budget recommendations
        st.subheader("Budget Recommendations")
        recommendations = api.get_budget_recommendations()
        if recommendations:
            for category in recommendations.get('categories', [])[:3]:  # Show top 3
                with st.expander(f"{category['name']} - ${category['spent']} of ${category['budget']}"):
                    st.progress(min(category['spent'] / category['budget'], 1.0))
                    st.caption(category['recommendation'])
        
    except Exception as e:
        st.error(f"Error loading dashboard data: {str(e)}")

def get_ai_insights():
    """Get AI-powered financial insights."""
    try:
        insights = api.get_ai_insights()
        if insights:
            st.subheader("AI Financial Insights")
            for insight in insights.get('insights', [])[:3]:  # Show top 3 insights
                with st.container():
                    st.markdown(f"**{insight['title']}**")
                    st.markdown(insight['description'])
                    if 'action_items' in insight:
                        st.markdown("**Action Items:**")
                        for item in insight['action_items']:
                            st.markdown(f"- {item}")
    except Exception as e:
        st.error(f"Error loading AI insights: {str(e)}")

if __name__ == "__main__":
    show()
