from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import random

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from streamlit_extras.metric_cards import style_metric_cards

from utils import (
    API_BASE_URL,
    api_request,
    format_currency,
    format_date,
    get_auth_headers
)

# Set page config - must be the first Streamlit command
st.set_page_config(
    page_title="Dashboard - SDG Finance",
    page_icon="📊",
    layout="wide"
)

# Custom CSS for dashboard
def load_css():
    """Load custom CSS styles for the dashboard."""
    st.markdown("""
    <style>
        /* Custom scrollbar */
        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }
        
        ::-webkit-scrollbar-track {
            background: #f1f1f1;
            border-radius: 10px;
        }
        
        ::-webkit-scrollbar-thumb {
            background: #888;
            border-radius: 10px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: #555;
        }
        
        /* Card hover effects */
        .card {
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            border: none !important;
            border-radius: 12px !important;
            overflow: hidden;
        }
        
        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 20px rgba(0,0,0,0.1) !important;
        }
        
        /* Custom metric cards */
        .stMetric {
            border-left: 4px solid #4b6cb7;
            padding-left: 1rem;
            border-radius: 4px;
        }
        
        /* Section headers */
        .section-header {
            border-bottom: 2px solid #e0e0e0;
            padding-bottom: 0.5rem;
            margin-bottom: 1.5rem;
            color: #2c3e50;
        }
        
        /* Input fields */
        .stTextInput>div>div>input,
        .stTextArea>div>div>textarea,
        .stSelectbox>div>div>div,
        .stNumberInput>div>div>input,
        .stDateInput>div>div>input {
            border-radius: 0.375rem !important;
            border: 1px solid #d1d5db !important;
            padding: 0.5rem 0.75rem !important;
        }
        
    </style>
    """, unsafe_allow_html=True)

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
    """Show the dashboard page with financial overview and metrics.
    
    This is the main async function that renders the dashboard.
    """
    # Load custom CSS
    load_css()
    
    # Page header
    st.markdown("<h1 class='section-header'>📊 Financial Dashboard</h1>", unsafe_allow_html=True)
    
    # Check if user is authenticated
    if not st.session_state.get("authenticated", False):
        st.warning("🔒 Please log in to view the dashboard.")
        st.session_state.current_page = "Login"
        st.rerun()
        return
    
    # Show loading state and fetch data
    with st.spinner("Loading your financial dashboard..."):
        try:
            # Load dashboard data
            dashboard_data = await fetch_dashboard_data()
            
            # Check if we got valid data
            if not dashboard_data or not isinstance(dashboard_data, dict):
                st.error("Failed to load dashboard data: Invalid data format")
                return
                
            # Extract metrics with safe defaults
            metrics = dashboard_data.get("metrics", {})
        except Exception as e:
            st.error(f"Failed to load dashboard data: {str(e)}")
            return
    
    # Create columns for metrics
    st.markdown("### Key Metrics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="💰 Total Savings",
            value=format_currency(metrics.get('total_savings', 0)),
            delta=f"{metrics.get('savings_change', 0)}% from last month",
            delta_color="normal"
        )
    
    with col2:
        st.metric(
            label="💸 Monthly Expenses",
            value=format_currency(metrics.get('monthly_expenses', 0)),
            delta=f"{metrics.get('expense_change', 0)}% from last month",
            delta_color="inverse"
        )
    
    with col3:
        st.metric(
            label="🏦 Active Loans",
            value=metrics.get('active_loans', 0),
            delta=f"{metrics.get('new_loans', 0)} new this month",
            delta_color="normal"
        )
    
    with col4:
        st.metric(
            label="🌍 Community Impact",
            value=f"${metrics.get('community_impact', 0):,}",
            delta=f"{metrics.get('new_impact', 0)}% this month",
            delta_color="normal"
        )
    
    # Style the metric cards
    style_metric_cards(
        background_color="rgba(255, 255, 255, 0.8)",
        border_left_color="#4b6cb7",
        border_radius_px=10,
        box_shadow=True
    )
    
    # Main content area
    st.markdown("<div class='card' style='padding: 1.5rem; margin: 1rem 0;'>", unsafe_allow_html=True)
    
    # Create tabs for different sections
    tab1, tab2, tab3 = st.tabs(["📈 Overview", "💳 Transactions", "📊 Analytics"])
    
    with tab1:
        st.markdown("### Financial Overview")
        
        # Create two columns for charts
        col1, col2 = st.columns(2)
        
        with col1:
            # Expense breakdown chart
            st.markdown("#### 💰 Expense Breakdown")
            if 'expense_breakdown' in dashboard_data and dashboard_data['expense_breakdown']:
                df_expenses = pd.DataFrame(dashboard_data['expense_breakdown'])
                
                # Create a donut chart with custom colors
                fig = go.Figure(data=[
                    go.Pie(
                        labels=df_expenses['category'],
                        values=df_expenses['amount'],
                        hole=0.5,
                        marker_colors=px.colors.qualitative.Pastel,
                        textinfo='label+percent',
                        textposition='inside',
                        hoverinfo='label+value+percent',
                        sort=False
                    )
                ])
                
                fig.update_layout(
                    margin=dict(t=0, b=0, l=0, r=0),
                    showlegend=False,
                    height=300
                )
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No expense data available")
            
            # Financial health summary
            with col2:
                st.markdown("#### 🏆 Financial Health")
                financial_health = dashboard_data.get("financial_health", {})
                
                # Calculate health score (0-100)
                health_score = int(financial_health.get("score", 0) * 100)
                
                # Determine health status and color
                if health_score >= 75:
                    status = "Excellent"
                    color = "#27ae60"
                elif health_score >= 50:
                    status = "Good"
                    color = "#2ecc71"
                elif health_score >= 25:
                    status = "Fair"
                    color = "#f39c12"
                else:
                    status = "Needs Attention"
                    color = "#e74c3c"
                
                # Create gauge chart
                fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=health_score,
                    domain={'x': [0, 1], 'y': [0, 1]},
                    title={'text': f"Health Score: {status}", 'font': {'size': 16}},
                    gauge={
                        'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "darkgray"},
                        'bar': {'color': color},
                        'steps': [
                            {'range': [0, 25], 'color': '#e74c3c'},
                            {'range': [25, 50], 'color': '#f39c12'},
                            {'range': [50, 75], 'color': '#2ecc71'},
                            {'range': [75, 100], 'color': '#27ae60'}
                        ],
                        'threshold': {
                            'line': {'color': "black", 'width': 4},
                            'thickness': 0.75,
                            'value': health_score
                        }
                    }
                ))
                
                fig.update_layout(
                    margin=dict(t=50, b=10, l=10, r=10),
                    height=300
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Add health tips
                if health_score < 50:
                    st.warning("💡 Tips to improve your financial health:")
                    st.markdown("""
                    - Build an emergency fund (3-6 months of expenses)
                    - Pay down high-interest debt
                    - Review and reduce unnecessary expenses
                    - Consider increasing your savings rate
                    """)
        
        # Add some spacing
        st.markdown("---")
        
        # Recent transactions
        st.markdown("### Recent Activity")
        if 'recent_transactions' in dashboard_data and dashboard_data['recent_transactions']:
            df_transactions = pd.DataFrame(dashboard_data['recent_transactions'])
            
            # Ensure required columns exist
            required_columns = ['date', 'description', 'amount', 'category']
            for col in required_columns:
                if col not in df_transactions.columns:
                    df_transactions[col] = ""
            
            # Format the date column if it exists
            if 'date' in df_transactions.columns:
                df_transactions['date'] = pd.to_datetime(df_transactions['date']).dt.strftime('%Y-%m-%d')
            
            # Display the transactions in a nice table
            st.dataframe(
                df_transactions[['date', 'description', 'category', 'amount']],
                column_config={
                    "date": "Date",
                    "description": "Description",
                    "category": "Category",
                    "amount": st.column_config.NumberColumn(
                        "Amount",
                        format="$%.2f",
                    )
                },
                hide_index=True,
                use_container_width=True,
                height=300
            )
        else:
            st.info("No recent transactions found")
        
        # Add a section for upcoming bills
        st.markdown("### Upcoming Bills")
        
        if 'upcoming_bills' in dashboard_data and dashboard_data['upcoming_bills']:
            df_bills = pd.DataFrame(dashboard_data['upcoming_bills'])
            
            # Ensure required columns exist
            required_columns = ['due_date', 'description', 'amount', 'status']
            for col in required_columns:
                if col not in df_bills.columns:
                    df_bills[col] = ""
            
            # Format the date column if it exists
            if 'due_date' in df_bills.columns:
                df_bills['due_date'] = pd.to_datetime(df_bills['due_date']).dt.strftime('%Y-%m-%d')
            
            # Display the bills in a nice table with status indicators
            st.dataframe(
                df_bills[['due_date', 'description', 'amount', 'status']],
                column_config={
                    "due_date": "Due Date",
                    "description": "Description",
                    "amount": st.column_config.NumberColumn(
                        "Amount",
                        format="$%.2f",
                    ),
                    "status": "Status"
                },
                hide_index=True,
                use_container_width=True,
                height=200
            )
        else:
            st.info("No upcoming bills found")
        
        # Add a section for quick actions
        st.markdown("### Quick Actions")
        
        # Create columns for action buttons
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("💸 Add Expense", use_container_width=True):
                st.session_state.show_expense_form = True
            
        with col2:
            if st.button("💳 Add Income", use_container_width=True):
                st.session_state.show_income_form = True
                
        with col3:
            if st.button("📊 View Reports", use_container_width=True):
                st.session_state.page = "reports"
        
        # Add a refresh button at the bottom
        if st.button("🔄 Refresh Dashboard", type="primary", use_container_width=True):
            st.rerun()
        
        # Add a small footer
        st.markdown("---")
        st.caption("Last updated: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        
        # Add smooth scrolling and auto-refresh
        try:
            st.components.v1.html("""
            <script>
                // Auto-refresh the page every 5 minutes
                setTimeout(function(){
                    window.location.reload();
                }, 300000);
                
                // Add smooth scrolling for better navigation
                document.querySelectorAll('a[href^="#"]').forEach(anchor => {
                    anchor.addEventListener('click', function (e) {
                        e.preventDefault();
                        const target = document.querySelector(this.getAttribute('href'));
                        if (target) {
                            target.scrollIntoView({
                                behavior: 'smooth'
                            });
                        }
                    });
                });
            </script>
            """, height=0)
                
        except Exception as e:
            # Handle any errors that might occur during rendering
            st.error(f"An error occurred while loading the dashboard: {str(e)}")
            st.error("Please try refreshing the page or contact support if the issue persists.")
            logger.error(f"Dashboard error: {str(e)}", exc_info=True)
    
    # Add a button to reset the dashboard
    if st.button("🔄 Reset Dashboard", type="secondary"):
        st.session_state.clear()
        st.rerun()

    # Close the main content area div
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Add a small delay to ensure all components are rendered
    st.empty()
    
    # Add a custom success message if this is the first load
    if 'first_load' not in st.session_state:
        st.session_state.first_load = False
        st.toast("🎉 Dashboard loaded successfully!", icon="✅")
    
    # Add a small delay to ensure all components are rendered
    st.empty()
    
    # Add a custom CSS to improve the overall look and feel
    st.markdown("""
    <style>
        /* Improve the look of the main content area */
        .main .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        
        /* Style the section headers */
        h3 {
            color: #2c3e50;
            border-bottom: 2px solid #f0f2f6;
            padding-bottom: 0.5rem;
            margin-top: 1.5rem;
        }
        
        /* Style the cards */
        .card {
            background: white;
            border-radius: 10px;
            padding: 1.5rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
            margin-bottom: 1.5rem;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        
        .card:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 12px rgba(0, 0, 0, 0.1);
        }
        
        /* Style the status indicators */
        .status-excellent { color: #10B981; }
        .status-good { color: #3B82F6; }
        .status-fair { color: #F59E0B; }
        .status-poor { color: #EF4444; }
        
        /* Style the footer */
        .footer {
            margin-top: 2rem;
            padding: 1rem 0;
            text-align: center;
            color: #6c757d;
            font-size: 0.9rem;
            border-top: 1px solid #e9ecef;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Add a footer with version and copyright information
    st.markdown("""
    <div class="footer">
        <p>SDG Finance Platform v1.0.0 | © 2025 All Rights Reserved</p>
        <p>For support, please contact: support@arusoftware.solutions</p>
    </div>
    """, unsafe_allow_html=True)

    # Financial Health Section
    with st.container():
        st.subheader("Financial Health")
        col1, col2 = st.columns(2)
        
        with col1:
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
                st.info("No financial recommendations available")
        
        # Income vs Expenses
        with col2:
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

def main():
    """Main entry point for the dashboard."""
    import asyncio
    
    # Check if we're running in a Streamlit context
    try:
        import streamlit as st
        if not hasattr(st, '_is_running_with_streamlit'):
            raise ImportError("Not running with Streamlit")
        
        # If we're in Streamlit, run the async function
        if 'dashboard_initialized' not in st.session_state:
            st.session_state.dashboard_initialized = True
            asyncio.run(show())
    except:
        # If not in Streamlit, just run the async function directly
        asyncio.run(show())

# This allows the dashboard to be imported and used as a module
def run():
    """Run the dashboard."""
    import asyncio
    asyncio.run(show())

# This is the main entry point when running the script directly
if __name__ == "__main__":
    # Check if we're running in Streamlit
    try:
        import streamlit as st
        if hasattr(st, '_is_running_with_streamlit'):
            # If yes, just run the main function
            main()
        else:
            # If not, print instructions
            print("This is a Streamlit component and should be run as part of the main application.")
            print("Please run the main application using:")
            print("\n    streamlit run app.py\n")
    except ImportError:
        # If streamlit is not available, just run the main function
        main()