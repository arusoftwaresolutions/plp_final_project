import calendar
from datetime import datetime, timedelta

import pandas as pd
import plotly.express as px
import streamlit as st

from utils import get_auth_headers, format_currency, format_date, API_BASE_URL

def get_transactions():
    """Fetch transactions from the backend."""
    # In a real app, this would call your backend API
    # For now, we'll use mock data
    transactions = [
        {"id": 1, "date": "2023-06-15", "description": "Grocery Store", "amount": -85.50, "category": "Food"},
        {"id": 2, "date": "2023-06-14", "description": "Freelance Work", "amount": 350.00, "category": "Income"},
        {"id": 3, "date": "2023-06-10", "description": "Electric Bill", "amount": -65.75, "category": "Utilities"},
        {"id": 4, "date": "2023-06-08", "description": "Coffee Shop", "amount": -4.50, "category": "Food"},
        {"id": 5, "date": "2023-06-05", "description": "Part-time Job", "amount": 200.00, "category": "Income"},
        {"id": 6, "date": "2023-06-01", "description": "Rent", "amount": -400.00, "category": "Housing"},
        {"id": 7, "date": "2023-05-28", "description": "Supermarket", "amount": -120.30, "category": "Food"},
        {"id": 8, "date": "2023-05-25", "description": "Freelance Project", "amount": 500.00, "category": "Income"},
    ]
    return pd.DataFrame(transactions)

def show():
    """Show the transactions page."""
    st.title("Transactions")
    
    # Add tabs for different views
    tab1, tab2 = st.tabs(["All Transactions", "Add Transaction"])
    
    with tab1:
        # Date range filter
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start Date", value=datetime.now() - timedelta(days=30))
        with col2:
            end_date = st.date_input("End Date", value=datetime.now())
        
        # Category filter
        all_categories = ["All"] + ["Food", "Income", "Utilities", "Housing", "Transportation", "Healthcare", "Entertainment"]
        selected_category = st.selectbox("Category", all_categories)
        
        # Get and filter transactions
        transactions_df = get_transactions()
        transactions_df['date'] = pd.to_datetime(transactions_df['date'])
        
        # Apply filters
        mask = (transactions_df['date'].dt.date >= start_date) & \
               (transactions_df['date'].dt.date <= end_date)
        
        if selected_category != "All":
            mask = mask & (transactions_df['category'] == selected_category)
        
        filtered_df = transactions_df[mask].sort_values('date', ascending=False)
        
        # Display summary metrics
        total_income = filtered_df[filtered_df['amount'] > 0]['amount'].sum()
        total_expenses = abs(filtered_df[filtered_df['amount'] < 0]['amount'].sum())
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Income", f"${total_income:,.2f}")
        with col2:
            st.metric("Total Expenses", f"${total_expenses:,.2f}")
        
        # Display transactions in a table
        st.subheader("Transaction History")
        
        # Format the table with custom styling
        def format_amount(amount):
            color = "green" if amount > 0 else "red"
            return f'<span style="color: {color}">{amount:+,.2f}</span>'
        
        # Display styled DataFrame
        st.markdown(
            filtered_df.style.format({
                'amount': format_amount,
                'date': lambda x: x.strftime('%b %d, %Y')
            }).hide(axis="index").to_html(), 
            unsafe_allow_html=True
        )
        
        # Add some space
        st.write("")
        
        # Monthly trends chart
        st.subheader("Monthly Trends")
        
        # Prepare data for the chart
        monthly_data = transactions_df.copy()
        monthly_data['month'] = monthly_data['date'].dt.to_period('M')
        monthly_data['month'] = monthly_data['month'].dt.strftime('%b %Y')
        monthly_data['is_income'] = monthly_data['amount'] > 0
        
        # Pivot for stacked bar chart
        pivot_data = monthly_data.pivot_table(
            index='month',
            columns='is_income',
            values='amount',
            aggfunc='sum',
            fill_value=0
        ).reset_index()
        
        # Rename columns for clarity
        pivot_data.columns = ['Month', 'Expenses', 'Income']
        pivot_data['Expenses'] = abs(pivot_data['Expenses'])
        
        # Create stacked bar chart
        fig = px.bar(
            pivot_data.melt(id_vars='Month', var_name='Type', value_name='Amount'),
            x='Month',
            y='Amount',
            color='Type',
            title='Income vs Expenses by Month',
            color_discrete_map={
                'Income': '#10B981',
                'Expenses': '#EF4444'
            }
        )
        
        fig.update_layout(
            barmode='group',
            xaxis_title='',
            yaxis_title='Amount ($)',
            legend_title='',
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        # Add transaction form
        with st.form("add_transaction"):
            st.subheader("Add New Transaction")
            
            col1, col2 = st.columns(2)
            
            with col1:
                transaction_type = st.radio(
                    "Transaction Type",
                    ["Expense", "Income"],
                    horizontal=True
                )
                
                amount = st.number_input(
                    "Amount",
                    min_value=0.01,
                    step=0.01,
                    format="%.2f"
                )
                
                if transaction_type == "Expense":
                    amount = -amount
                
                date = st.date_input("Date", value=datetime.now())
            
            with col2:
                category = st.selectbox(
                    "Category",
                    ["Food", "Housing", "Transportation", "Utilities", 
                     "Healthcare", "Education", "Entertainment", "Other"]
                )
                
                description = st.text_input("Description")
                
                # Add some space
                st.write("")
                st.write("")
                
                submit_button = st.form_submit_button("Add Transaction")
            
            if submit_button:
                # In a real app, this would save to your backend
                st.success("✅ Transaction added successfully!")
                
                # Show a preview
                st.subheader("Preview")
                
                preview_df = pd.DataFrame([{
                    "Date": date.strftime('%b %d, %Y'),
                    "Description": description,
                    "Category": category,
                    "Amount": f"{'+' if amount > 0 else ''}{amount:.2f}"
                }])
                
                st.dataframe(
                    preview_df.style.highlight_between(
                        subset=['Amount'],
                        left=0.01,  # Any positive number
                        right=None,  # No upper bound
                        props='color:green;',
                        axis=None
                    ).highlight_between(
                        subset=['Amount'],
                        left=None,  # No lower bound
                        right=0,    # Any negative number
                        props='color:red;',
                        axis=None
                    ),
                    hide_index=True
                )
                
                # Reset form
                st.experimental_rerun()
    
    # Add custom styles
    st.markdown("""
        <style>
            /* Style the table */
            table {
                width: 100%;
                border-collapse: collapse;
                margin: 1rem 0;
                font-size: 0.9em;
            }
            
            th {
                background-color: #f8fafc;
                text-align: left;
                padding: 0.75rem;
                border-bottom: 2px solid #e2e8f0;
                font-weight: 600;
                color: #475569;
            }
            
            td {
                padding: 0.75rem;
                border-bottom: 1px solid #e2e8f0;
            }
            
            tr:hover {
                background-color: #f8fafc;
            }
            
            /* Style form elements */
            .stRadio > div {
                display: flex;
                gap: 1rem;
            }
            
            .stRadio > div > label {
                margin: 0;
                flex: 1;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 0.5rem;
                border-radius: 0.5rem;
                background: #f1f5f9;
                transition: all 0.2s;
            }
            
            .stRadio > div > label:hover {
                background: #e2e8f0;
            }
            
            .stRadio > div > div[data-baseweb="radio"] {
                margin-right: 0.5rem;
            }
            
            .stButton > button {
                width: 100%;
                margin-top: 1.5rem;
            }
        </style>
    """, unsafe_allow_html=True)
