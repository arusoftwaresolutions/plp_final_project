from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

import pandas as pd
import plotly.express as px
import streamlit as st

from utils import (
    API_BASE_URL,
    api_request,
    format_currency,
    format_date,
    get_auth_headers
)

async def fetch_dashboard_data() -> Dict[str, Any]:
    """Fetch dashboard data from the backend with error handling.
    
    Returns:
        Dictionary containing dashboard data or empty dict on error
    """
    # Default empty data structure
    default_data = {
        "metrics": {
            "total_savings": 0,
            "savings_change": 0,
            "monthly_expenses": 0,
            "expense_change": 0,
            "active_loans": 0,
            "new_loans": 0,
            "community_impact": 0,
            "new_impact": 0
        },
        "expense_breakdown": [],
        "recent_transactions": [],
        "savings_goals": [],
        "financial_health": {}
    }
    
    try:
        # Fetch dashboard data with error handling
        data = await api_request("GET", "/dashboard/")
        if not data:
            st.warning("No data returned from the server. Using default values.")
            return default_data
            
        # Ensure all required fields exist in the response
        if not isinstance(data, dict):
            st.error("Invalid data format received from server.")
            return default_data
            
        # Merge with default data to ensure all keys exist
        if "metrics" not in data:
            data["metrics"] = default_data["metrics"]
        else:
            # Ensure all metric fields exist
            for key in default_data["metrics"]:
                if key not in data["metrics"]:
                    data["metrics"][key] = default_data["metrics"][key]
        
        # Ensure other top-level keys exist
        for key in ["expense_breakdown", "recent_transactions", "savings_goals", "financial_health"]:
            if key not in data:
                data[key] = default_data[key]
        
        return data
        
    except Exception as e:
        st.error(f"Failed to load dashboard data: {str(e)}")
        return default_data

async def show():
    """Show the dashboard page with financial overview and metrics."""
    st.title("Dashboard")
    
    # Check if user is authenticated
    if not st.session_state.get("authenticated", False):
        st.warning("Please log in to view the dashboard.")
        st.session_state.current_page = "Login"
        st.experimental_rerun()
        return
    
    # Show loading state
    with st.spinner("Loading your financial dashboard..."):
        dashboard_data = await fetch_dashboard_data()
    
    # Extract metrics with safe defaults
    metrics = dashboard_data.get("metrics", {})
    
    # Create columns for metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_savings = float(metrics.get("total_savings", 0))
        savings_change = float(metrics.get("savings_change", 0))
        st.metric(
            "Total Savings", 
            format_currency(total_savings),
            delta=f"{'+' if savings_change >= 0 else ''}{savings_change:.1f}%" if savings_change != 0 else None,
            help="Your total savings across all accounts"
        )
    
    with col2:
        monthly_expenses = float(metrics.get("monthly_expenses", 0))
        expense_change = float(metrics.get("expense_change", 0))
        st.metric(
            "Monthly Expenses", 
            format_currency(monthly_expenses),
            delta=(
                f"{'+' if expense_change > 0 else ''}{format_currency(expense_change)} "
                f"({abs(expense_change):.1f}%)"
            ) if expense_change != 0 else None,
            help="Your total expenses this month"
        )
    
    with col3:
        active_loans = int(metrics.get("active_loans", 0))
        new_loans = int(metrics.get("new_loans", 0))
        st.metric(
            "Active Loans", 
            str(active_loans),
            delta=f"{new_links} New" if new_loans > 0 else None,
            help="Number of active loans in your account"
        )
    
    with col4:
        community_impact = int(metrics.get("community_impact", 0))
        new_impact = int(metrics.get("new_impact", 0))
        st.metric(
            "Community Impact", 
            f"{community_impact} Families",
            delta=f"+{new_impact} this month" if new_impact > 0 else None,
            help="Number of families impacted through your activities"
        )
    
    # Main content
    st.markdown("---")
    row1 = st.columns([2, 1])
    
    # Expense breakdown chart
    with row1[0]:
        st.subheader("Expense Breakdown")
        expense_data = dashboard_data.get("expense_breakdown", [])
        if expense_data and len(expense_data) > 0:
            try:
                df = pd.DataFrame(expense_data)
                # Ensure required columns exist
                if 'amount' not in df.columns or 'category' not in df.columns:
                    st.warning("Invalid expense data format.")
                else:
                    # Convert amount to float and handle any non-numeric values
                    df['amount'] = pd.to_numeric(df['amount'], errors='coerce').fillna(0)
                    
                    # Group small categories into 'Other'
                    threshold = df['amount'].sum() * 0.05  # 5% threshold
                    small_categories = df[df['amount'] < threshold]
                    if not small_categories.empty:
                        other_row = pd.DataFrame({
                            'category': ['Other'],
                            'amount': [small_categories['amount'].sum()]
                        })
                        df = pd.concat([df[df['amount'] >= threshold], other_row])
                    
                    # Create the pie chart
                    fig = px.pie(
                        df, 
                        values='amount', 
                        names='category',
                        hole=0.4,
                        color_discrete_sequence=px.colors.qualitative.Pastel,
                        title="Monthly Expenses by Category"
                    )
                    fig.update_traces(
                        textposition='inside',
                        textinfo='percent+label',
                        hovertemplate='<b>%{label}</b><br>' +
                                    'Amount: %{value:$,.2f}<br>' +
                                    'Percentage: %{percent:.1%}<extra></extra>',
                        textfont_size=12
                    )
                    fig.update_layout(
                        margin=dict(t=40, b=10, l=10, r=10),
                        showlegend=False,
                        hoverlabel=dict(
                            bgcolor="white",
                            font_size=14,
                            font_family="Arial"
                        )
                    )
                    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
                    
            except Exception as e:
                st.error(f"Error displaying expense breakdown: {str(e)}")
        else:
            st.info("No expense data available for the current period.")
            
    # Financial health summary
    with row1[1]:
        st.subheader("Financial Health")
        financial_health = dashboard_data.get("financial_health", {})
        
        # Calculate health score (0-100)
        health_score = int(financial_health.get("score", 0) * 100)
        
        # Determine health status and color
        if health_score >= 75:
            status = "Excellent"
            color = "#10B981"  # Green
        elif health_score >= 50:
            status = "Good"
            color = "#3B82F6"  # Blue
        elif health_score >= 25:
            status = "Fair"
            color = "#F59E0B"  # Yellow
        else:
            status = "Needs Attention"
            color = "#EF4444"  # Red
        
        # Display health score with a gauge chart
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=health_score,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Financial Health Score"},
            gauge={
                'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "darkgray"},
                'bar': {'color': color},
                'steps': [
                    {'range': [0, 25], 'color': "#FEE2E2"},  # Light red
                    {'range': [25, 50], 'color': "#FEF3C7"},  # Light yellow
                    {'range': [50, 75], 'color': "#DBEAFE"},  # Light blue
                    {'range': [75, 100], 'color': "#D1FAE5"}  # Light green
                ],
                'threshold': {
                    'line': {'color': color, 'width': 4},
                    'thickness': 0.75,
                    'value': health_score
                }
            }
        ))
        
        fig.update_layout(
            height=250,
            margin=dict(t=40, b=10, l=10, r=10)
        )
        
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        
        # Display status and recommendations
        st.markdown(f"**Status:** <span style='color:{color}'>{status}</span>", unsafe_allow_html=True)
        
        # Show key metrics
        st.markdown("### Key Metrics")
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Savings Rate", 
                     f"{financial_health.get('savings_rate', 0):.1f}%",
                     help="Percentage of income saved")
            
        with col2:
            st.metric("Debt-to-Income", 
                     f"{financial_health.get('debt_to_income', 0):.1f}%",
                     help="Lower is better")
        
        # Show recommendations if available
        recommendations = financial_health.get("recommendations", [])
        if recommendations:
            st.markdown("### Recommendations")
            for rec in recommendations[:3]:  # Show top 3 recommendations
                st.markdown(f"- {rec}")
        else:
            st.info("No expense data available")
    
    # Income vs Expenses
    with row1[1]:
        st.subheader("Income vs Expenses")
        income_expense_data = dashboard_data.get("income_vs_expenses", {})
        if income_expense_data:
            months = income_expense_data.get("months", [])
            income = income_expense_data.get("income", [])
            expenses = income_expense_data.get("expenses", [])
        
            df = pd.DataFrame({
                'Month': months,
                'Amount': income + expenses,
                'Type': ['Income'] * len(months) + ['Expenses'] * len(months)
            })
            
            fig = px.bar(
                df, 
                x='Month', 
                y='Amount', 
                color='Type',
                barmode='group',
                color_discrete_map={
                    'Income': '#2ecc71', 
                    'Expenses': '#e74c3c'
                }
            )
            
            fig.update_layout(
                showlegend=True,
                xaxis_title="",
                yaxis_title="Amount ($)",
                legend_title=""
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No income/expense data available")
    
    # Second row of charts
    row2 = st.columns(2)
    
    # Recent Transactions
    with row2[0]:
        st.subheader("Recent Transactions")
        transactions = dashboard_data.get("recent_transactions", [])
        
        if transactions:
            df = pd.DataFrame(transactions)
            
            # Format date and amount
            df['date'] = pd.to_datetime(df['date']).dt.strftime('%b %d')
            
            # Style the DataFrame
            def color_negative_red(val):
                color = 'red' if val < 0 else 'green'
                return f'color: {color}'
            
            st.dataframe(
                df.style.applymap(color_negative_red, subset=['amount']).format({
                    'amount': '${:,.2f}'.format
                }),
                hide_index=True,
                use_container_width=True,
                column_order=['date', 'description', 'amount', 'category'],
                column_config={
                    'date': 'Date',
                    'description': 'Description',
                    'amount': 'Amount',
                    'category': 'Category'
                }
            )
            
            if st.button("View All Transactions", use_container_width=True):
                st.session_state.current_page = "Transactions"
                st.experimental_rerun()
        else:
            st.info("No recent transactions")
    
    # Financial Goals
    with row2[1]:
        st.subheader("Financial Goals")
        goals = dashboard_data.get("financial_goals", [])
        
        if goals:
            for goal in goals:
                progress = (goal.get('current', 0) / goal.get('target', 1)) * 100
                st.write(f"**{goal.get('name', 'Goal')}**")
                st.progress(min(progress / 100, 1.0))
                st.caption(
                    f"{format_currency(goal.get('current', 0))} of "
                    f"{format_currency(goal.get('target', 0))} ({progress:.1f}%)"
                )
                st.write("---")
            
            if st.button("Manage Goals", use_container_width=True):
                st.session_state.current_page = "Profile"
                st.experimental_rerun()
        else:
            st.info("No financial goals set")
            if st.button("Create a Goal", use_container_width=True):
                st.session_state.current_page = "Profile"
                st.experimental_rerun()
    
    # Add some spacing at the bottom
    st.write("")
    st.write("")
    
    # Add custom CSS for the dashboard
    st.markdown("""
        <style>
            .stProgress > div > div > div {
                background-color: #3B82F6;
            }
            .stProgress > div > div {
                background-color: #E5E7EB;
            }
        </style>
    """, unsafe_allow_html=True)
