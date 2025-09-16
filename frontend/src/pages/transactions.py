import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from ..services import api

def show():
    """Display the transactions page."""
    st.title("Transactions")
    
    # Tabs for different views
    tab1, tab2 = st.tabs(["Transaction History", "Spending Analysis"])
    
    with tab1:
        show_transaction_history()
    
    with tab2:
        show_spending_analysis()

def show_transaction_history():
    """Display transaction history with filtering options."""
    try:
        # Date range filter
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start Date", datetime.now() - timedelta(days=30))
        with col2:
            end_date = st.date_input("End Date", datetime.now())
        
        # Category filter
        categories = ["All", "Food", "Transportation", "Housing", "Entertainment", "Utilities", "Other"]
        selected_category = st.selectbox("Category", categories)
        
        # Search box
        search_query = st.text_input("Search transactions")
        
        # In a real app, this would fetch from the API with filters
        # transactions = api.get_transactions(
        #     start_date=start_date,
        #     end_date=end_date,
        #     category=selected_category if selected_category != "All" else None,
        #     search=search_query if search_query else None
        # )
        
        # Mock data for demonstration
        transactions = [
            {
                'id': 1,
                'date': '2023-10-15',
                'description': 'Grocery Store',
                'amount': -125.50,
                'category': 'Food',
                'type': 'expense'
            },
            {
                'id': 2,
                'date': '2023-10-14',
                'description': 'Salary Deposit',
                'amount': 2500.00,
                'category': 'Income',
                'type': 'income'
            },
            {
                'id': 3,
                'date': '2023-10-12',
                'description': 'Electric Bill',
                'amount': -85.75,
                'category': 'Utilities',
                'type': 'expense'
            },
            {
                'id': 4,
                'date': '2023-10-10',
                'description': 'Gas Station',
                'amount': -45.30,
                'category': 'Transportation',
                'type': 'expense'
            },
            {
                'id': 5,
                'date': '2023-10-05',
                'description': 'Freelance Work',
                'amount': 500.00,
                'category': 'Income',
                'type': 'income'
            }
        ]
        
        if not transactions:
            st.info("No transactions found for the selected filters.")
            return
        
        # Convert to DataFrame for display
        df = pd.DataFrame(transactions)
        
        # Apply filters to mock data
        if selected_category != "All":
            df = df[df['category'] == selected_category]
        
        if search_query:
            mask = df['description'].str.contains(search_query, case=False, na=False)
            df = df[mask]
        
        # Display transactions in a data table
        st.subheader("Transaction History")
        
        # Summary cards
        total_income = df[df['type'] == 'income']['amount'].sum()
        total_expenses = abs(df[df['type'] == 'expense']['amount'].sum())
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Income", f"${total_income:,.2f}")
        with col2:
            st.metric("Total Expenses", f"${total_expenses:,.2f}")
        
        # Transactions table
        st.dataframe(
            df[['date', 'description', 'amount', 'category']],
            column_config={
                'date': 'Date',
                'description': 'Description',
                'amount': st.column_config.NumberColumn(
                    'Amount',
                    format='$%.2f',
                    help="Negative amounts are expenses, positive are income"
                ),
                'category': 'Category'
            },
            hide_index=True,
            use_container_width=True
        )
        
        # Export button
        if st.button("Export to CSV"):
            csv = df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"transactions_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
    
    except Exception as e:
        st.error(f"Error loading transactions: {str(e)}")

def show_spending_analysis():
    """Display spending analysis with charts."""
    try:
        # Date range filter
        st.subheader("Spending Analysis")
        
        # Time period selection
        time_period = st.selectbox(
            "Time Period",
            ["Last 7 Days", "Last 30 Days", "Last 3 Months", "Last 6 Months", "This Year"],
            index=1
        )
        
        # In a real app, this would fetch from the API
        # transactions = api.get_transactions(time_period=time_period)
        
        # Mock data for demonstration
        transactions = [
            {'date': '2023-10-15', 'amount': -125.50, 'category': 'Food'},
            {'date': '2023-10-14', 'amount': 2500.00, 'category': 'Income'},
            {'date': '2023-10-12', 'amount': -85.75, 'category': 'Utilities'},
            {'date': '2023-10-10', 'amount': -45.30, 'category': 'Transportation'},
            {'date': '2023-10-10', 'amount': -75.20, 'category': 'Food'},
            {'date': '2023-10-08', 'amount': -120.00, 'category': 'Entertainment'},
            {'date': '2023-10-05', 'amount': 500.00, 'category': 'Income'},
            {'date': '2023-10-03', 'amount': -200.00, 'category': 'Housing'},
            {'date': '2023-10-01', 'amount': -35.50, 'category': 'Transportation'},
            {'date': '2023-09-28', 'amount': -60.00, 'category': 'Food'},
            {'date': '2023-09-25', 'amount': -150.00, 'category': 'Shopping'},
            {'date': '2023-09-20', 'amount': -80.00, 'category': 'Utilities'},
            {'date': '2023-09-15', 'amount': 2500.00, 'category': 'Income'},
        ]
        
        if not transactions:
            st.info("No transaction data available for analysis.")
            return
        
        # Convert to DataFrame
        df = pd.DataFrame(transactions)
        df['date'] = pd.to_datetime(df['date'])
        
        # Filter expenses only for analysis
        expenses = df[df['amount'] < 0].copy()
        expenses['amount'] = expenses['amount'].abs()
        
        if expenses.empty:
            st.info("No expense data available for analysis.")
            return
        
        # Spending by category
        st.subheader("Spending by Category")
        
        category_totals = expenses.groupby('category')['amount'].sum().reset_index()
        
        # Create a pie chart
        fig1 = px.pie(
            category_totals,
            values='amount',
            names='category',
            title='Spending Distribution by Category',
            hole=0.4
        )
        st.plotly_chart(fig1, use_container_width=True)
        
        # Time-based spending
        st.subheader("Spending Over Time")
        
        # Group by date and calculate daily totals
        daily_spending = expenses.groupby('date')['amount'].sum().reset_index()
        
        # Create a line chart
        fig2 = px.line(
            daily_spending,
            x='date',
            y='amount',
            title='Daily Spending',
            labels={'amount': 'Amount ($)', 'date': 'Date'}
        )
        st.plotly_chart(fig2, use_container_width=True)
        
        # Category trends over time
        st.subheader("Category Trends")
        
        # Group by date and category
        category_trends = expenses.groupby(['date', 'category'])['amount'].sum().reset_index()
        
        # Create a line chart for each category
        fig3 = px.line(
            category_trends,
            x='date',
            y='amount',
            color='category',
            title='Spending by Category Over Time',
            labels={'amount': 'Amount ($)', 'date': 'Date', 'category': 'Category'}
        )
        st.plotly_chart(fig3, use_container_width=True)
        
        # Top expenses
        st.subheader("Top Expenses")
        
        # Sort by amount (descending) and take top 10
        top_expenses = expenses.nlargest(10, 'amount')
        
        # Create a bar chart
        fig4 = px.bar(
            top_expenses,
            x='amount',
            y='category',
            orientation='h',
            title='Top 10 Expenses by Category',
            labels={'amount': 'Amount ($)', 'category': 'Category'}
        )
        st.plotly_chart(fig4, use_container_width=True)
    
    except Exception as e:
        st.error(f"Error generating spending analysis: {str(e)}")
