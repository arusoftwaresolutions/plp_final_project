from datetime import datetime, timedelta
import random

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from utils import get_auth_headers, format_currency, format_date, API_BASE_URL

def generate_mock_users(count=50):
    """Generate mock user data for the admin panel."""
    first_names = ["John", "Jane", "Michael", "Emily", "David", "Sarah", "James", "Jennifer", "Robert", "Lisa",
                  "William", "Elizabeth", "Joseph", "Michelle", "Thomas", "Jessica", "Charles", "Amanda", "Christopher", "Melissa"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Miller", "Davis", "Garcia", "Rodriguez", "Wilson",
                 "Martinez", "Anderson", "Taylor", "Thomas", "Hernandez", "Moore", "Martin", "Jackson", "Thompson", "White"]
    
    users = []
    for i in range(count):
        first = random.choice(first_names)
        last = random.choice(last_names)
        email = f"{first.lower()}.{last.lower()}{random.randint(1, 100)}@example.com".replace("'", "")
        
        # Random registration date in the last 2 years
        reg_date = datetime.now() - timedelta(days=random.randint(1, 730))
        last_login = datetime.now() - timedelta(days=random.randint(0, 30))
        
        users.append({
            "id": i + 1,
            "name": f"{first} {last}",
            "email": email,
            "phone": f"+2557{random.randint(10, 99)}{random.randint(100000, 999999)}",
            "status": random.choices(["Active", "Inactive", "Suspended", "Pending"], weights=[0.7, 0.1, 0.1, 0.1])[0],
            "user_type": random.choices(["Borrower", "Lender", "Both"], weights=[0.6, 0.2, 0.2])[0],
            "registration_date": reg_date.strftime("%Y-%m-%d"),
            "last_login": last_login.strftime("%Y-%m-%d %H:%M"),
            "loans_taken": random.randint(0, 10),
            "loans_repaid": random.randint(0, 5),
            "active_loans": random.randint(0, 3),
            "total_loaned": round(random.uniform(0, 10000), 2),
            "total_repaid": round(random.uniform(0, 8000), 2),
            "credit_score": random.randint(300, 850)
        })
    
    return pd.DataFrame(users)

def generate_mock_loans(count=100):
    """Generate mock loan data for the admin panel."""
    purposes = [
        "Business Expansion", "Agriculture", "Education", "Medical Expenses", "Home Improvement",
        "Debt Consolidation", "Emergency", "Vehicle Purchase", "Wedding", "Other"
    ]
    
    statuses = ["Approved", "Pending", "Rejected", "Disbursed", "Completed", "Defaulted"]
    
    loans = []
    for i in range(count):
        amount = random.choice([500, 1000, 1500, 2000, 2500, 3000, 5000, 10000])
        term = random.choice([3, 6, 12, 18, 24, 36])
        interest_rate = round(random.uniform(5, 25), 1)
        
        # Calculate monthly payment using simple interest for demonstration
        monthly_interest = (interest_rate / 100) * amount / 12
        monthly_payment = (amount / term) + monthly_interest
        
        # Random dates
        app_date = datetime.now() - timedelta(days=random.randint(1, 365))
        status = random.choices(statuses, weights=[0.3, 0.2, 0.1, 0.2, 0.15, 0.05])[0]
        
        if status in ["Disbursed", "Completed", "Defaulted"]:
            disburse_date = app_date + timedelta(days=random.randint(1, 30))
            if status == "Completed":
                complete_date = disburse_date + timedelta(days=random.randint(30, term * 30))
            elif status == "Defaulted":
                complete_date = disburse_date + timedelta(days=random.randint(10, term * 15))
            else:
                complete_date = ""
        else:
            disburse_date = ""
            complete_date = ""
        
        loans.append({
            "id": f"LN{random.randint(10000, 99999)}",
            "borrower_id": random.randint(1, 50),
            "borrower_name": f"User {random.randint(1, 50)}",
            "purpose": random.choice(purposes),
            "amount": amount,
            "term_months": term,
            "interest_rate": interest_rate,
            "monthly_payment": round(monthly_payment, 2),
            "status": status,
            "application_date": app_date.strftime("%Y-%m-%d"),
            "disbursement_date": disburse_date.strftime("%Y-%m-%d") if disburse_date else "",
            "completion_date": complete_date.strftime("%Y-%m-%d") if complete_date else "",
            "amount_repaid": round(random.uniform(0, amount * 1.2), 2) if status != "Pending" else 0,
            "delinquent_days": random.randint(0, 90) if status == "Defaulted" else 0,
            "risk_score": random.randint(300, 850)
        })
    
    return pd.DataFrame(loans)

def generate_mock_transactions(count=500):
    """Generate mock transaction data for the admin panel."""
    types = ["Loan Disbursement", "Loan Repayment", "Deposit", "Withdrawal", "Fee", "Refund"]
    statuses = ["Completed", "Pending", "Failed", "Reversed"]
    
    transactions = []
    for i in range(count):
        amount = round(random.uniform(10, 5000), 2)
        fee = round(amount * random.uniform(0, 0.05), 2)
        
        # Random dates in the last year
        date = datetime.now() - timedelta(days=random.randint(1, 365), hours=random.randint(1, 24))
        
        transactions.append({
            "id": f"TXN{random.randint(100000, 999999)}",
            "user_id": random.randint(1, 50),
            "user_name": f"User {random.randint(1, 50)}",
            "type": random.choice(types),
            "amount": amount,
            "fee": fee,
            "net_amount": amount - fee if random.choice([True, False]) else amount + fee,
            "status": random.choices(statuses, weights=[0.8, 0.1, 0.05, 0.05])[0],
            "date": date.strftime("%Y-%m-%d %H:%M"),
            "description": f"{random.choice(types)} - {random.choice(['Completed', 'Processed', 'Initiated'])}",
            "reference": f"REF{random.randint(100000000, 999999999)}",
            "channel": random.choice(["Mobile App", "Web", "USSD", "Bank Transfer", "Agent"])
        })
    
    return pd.DataFrame(transactions)

def show():
    """Show the admin panel."""
    # Check if user is admin
    if 'is_admin' not in st.session_state or not st.session_state.is_admin:
        st.warning("You don't have permission to access this page.")
        return
    
    st.title("Admin Dashboard")
    
    # Generate mock data
    users_df = generate_mock_users()
    loans_df = generate_mock_loans()
    transactions_df = generate_mock_transactions()
    
    # Create tabs for different sections
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Overview", "Users", "Loans", "Transactions", "Reports"])
    
    with tab1:  # Overview tab
        st.header("Platform Overview")
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Users", len(users_df))
        
        with col2:
            active_loans = len(loans_df[loans_df["status"].isin(["Approved", "Disbursed"])])
            st.metric("Active Loans", active_loans)
        
        with col3:
            total_volume = loans_df["amount"].sum()
            st.metric("Total Loan Volume", f"${total_volume:,.2f}")
        
        with col4:
            repayment_rate = (loans_df[loans_df["status"] == "Completed"].shape[0] / 
                            loans_df[loans_df["status"].isin(["Completed", "Defaulted"])].shape[0] * 100 
                            if loans_df[loans_df["status"].isin(["Completed", "Defaulted"])].shape[0] > 0 else 0)
            st.metric("Repayment Rate", f"{repayment_rate:.1f}%")
        
        # Row 1: Charts
        col1, col2 = st.columns(2)
        
        with col1:
            # User growth chart
            st.subheader("User Growth")
            
            # Create date range for the last 12 months
            end_date = datetime.now()
            start_date = end_date - timedelta(days=365)
            
            # Generate monthly data
            dates = pd.date_range(start_date, end_date, freq='M')
            user_counts = [random.randint(5, 50) for _ in range(len(dates))]
            cumulative_users = np.cumsum(user_counts)
            
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=dates,
                y=cumulative_users,
                mode='lines+markers',
                name='Total Users',
                line=dict(color='#3b82f6', width=3)
            ))
            
            fig.add_trace(go.Bar(
                x=dates,
                y=user_counts,
                name='New Users',
                marker_color='#93c5fd',
                opacity=0.7
            ))
            
            fig.update_layout(
                xaxis_title="Date",
                yaxis_title="Number of Users",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                height=350,
                margin=dict(l=20, r=20, t=40, b=20)
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Loan status distribution
            st.subheader("Loan Status Distribution")
            
            status_counts = loans_df["status"].value_counts().reset_index()
            status_counts.columns = ["Status", "Count"]
            
            fig = px.pie(
                status_counts, 
                values="Count", 
                names="Status",
                color_discrete_sequence=px.colors.sequential.RdBu
            )
            
            fig.update_traces(
                textposition='inside',
                textinfo='percent+label',
                hovertemplate="%{label}: %{value} (%{percent})"
            )
            
            fig.update_layout(
                showlegend=False,
                height=350,
                margin=dict(l=20, r=20, t=40, b=20)
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        # Row 2: More charts
        col1, col2 = st.columns(2)
        
        with col1:
            # Loan volume by purpose
            st.subheader("Loan Volume by Purpose")
            
            purpose_volume = loans_df.groupby("purpose")["amount"].sum().reset_index()
            purpose_volume = purpose_volume.sort_values("amount", ascending=False)
            
            fig = px.bar(
                purpose_volume,
                x="amount",
                y="purpose",
                orientation='h',
                labels={"amount": "Total Amount ($)", "purpose": ""},
                color="amount",
                color_continuous_scale=px.colors.sequential.Blues
            )
            
            fig.update_layout(
                height=400,
                margin=dict(l=20, r=20, t=40, b=20),
                coloraxis_showscale=False
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Transaction volume over time
            st.subheader("Transaction Volume (30 Days)")
            
            # Generate last 30 days data
            dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
            transaction_counts = [random.randint(5, 50) for _ in range(30)]
            transaction_volume = [round(random.uniform(1000, 50000), 2) for _ in range(30)]
            
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                x=dates,
                y=transaction_counts,
                name='Number of Transactions',
                marker_color='#93c5fd',
                opacity=0.7
            ))
            
            fig.add_trace(go.Scatter(
                x=dates,
                y=transaction_volume,
                name='Transaction Volume ($)',
                yaxis='y2',
                line=dict(color='#3b82f6', width=3)
            ))
            
            fig.update_layout(
                yaxis=dict(
                    title="Number of Transactions",
                    titlefont=dict(color='#93c5fd'),
                    tickfont=dict(color='#93c5fd')
                ),
                yaxis2=dict(
                    title="Transaction Volume ($)",
                    titlefont=dict(color='#3b82f6'),
                    tickfont=dict(color='#3b82f6'),
                    anchor="free",
                    overlaying="y",
                    side="right",
                    position=1
                ),
                xaxis_title="Date",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                height=400,
                margin=dict(l=20, r=80, t=40, b=20)
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        # Recent activity
        st.subheader("Recent Activity")
        
        # Get recent transactions
        recent_transactions = transactions_df.sort_values("date", ascending=False).head(10)
        
        # Display as a table with some styling
        st.dataframe(
            recent_transactions[["date", "user_name", "type", "amount", "status"]],
            column_config={
                "date": "Date",
                "user_name": "User",
                "type": "Type",
                "amount": st.column_config.NumberColumn("Amount", format="$%.2f"),
                "status": "Status"
            },
            hide_index=True,
            use_container_width=True
        )
    
    with tab2:  # Users tab
        st.header("User Management")
        
        # Filters
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            status_filter = st.multiselect(
                "Status",
                options=users_df["status"].unique(),
                default=users_df["status"].unique()
            )
        
        with col2:
            user_type_filter = st.multiselect(
                "User Type",
                options=users_df["user_type"].unique(),
                default=users_df["user_type"].unique()
            )
        
        with col3:
            min_loans = st.number_input("Min Loans Taken", min_value=0, value=0)
        
        with col4:
            search_query = st.text_input("Search by name or email", "")
        
        # Apply filters
        filtered_users = users_df.copy()
        
        if status_filter:
            filtered_users = filtered_users[filtered_users["status"].isin(status_filter)]
        
        if user_type_filter:
            filtered_users = filtered_users[filtered_users["user_type"].isin(user_type_filter)]
        
        filtered_users = filtered_users[filtered_users["loans_taken"] >= min_loans]
        
        if search_query:
            search_query = search_query.lower()
            filtered_users = filtered_users[
                filtered_users["name"].str.lower().str.contains(search_query) |
                filtered_users["email"].str.lower().str.contains(search_query)
            ]
        
        # Display user table
        st.dataframe(
            filtered_users[["name", "email", "status", "user_type", "loans_taken", "loans_repaid", "active_loans", "credit_score"]],
            column_config={
                "name": "Name",
                "email": "Email",
                "status": "Status",
                "user_type": "User Type",
                "loans_taken": "Loans Taken",
                "loans_repaid": "Loans Repaid",
                "active_loans": "Active Loans",
                "credit_score": "Credit Score"
            },
            hide_index=True,
            use_container_width=True
        )
        
        # User details modal
        if st.button("Add New User"):
            st.session_state.show_add_user = True
        
        if st.session_state.get("show_add_user", False):
            with st.form("add_user_form"):
                st.subheader("Add New User")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    first_name = st.text_input("First Name*")
                    email = st.text_input("Email*")
                    phone = st.text_input("Phone")
                    user_type = st.selectbox("User Type*", ["Borrower", "Lender", "Both"])
                
                with col2:
                    last_name = st.text_input("Last Name*")
                    password = st.text_input("Password*", type="password")
                    status = st.selectbox("Status*", ["Active", "Inactive", "Suspended", "Pending"])
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.form_submit_button("Create User"):
                        if first_name and last_name and email and password:
                            # In a real app, this would create a new user in the database
                            st.success(f"User {first_name} {last_name} created successfully!")
                            st.session_state.show_add_user = False
                            st.rerun()
                        else:
                            st.error("Please fill in all required fields.")
                
                with col2:
                    if st.form_submit_button("Cancel"):
                        st.session_state.show_add_user = False
                        st.rerun()
    
    with tab3:  # Loans tab
        st.header("Loan Management")
        
        # Filters
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            status_filter = st.multiselect(
                "Loan Status",
                options=loans_df["status"].unique(),
                default=loans_df["status"].unique()
            )
        
        with col2:
            purpose_filter = st.multiselect(
                "Purpose",
                options=loans_df["purpose"].unique(),
                default=loans_df["purpose"].unique()
            )
        
        with col3:
            min_amount = st.number_input("Min Amount", min_value=0, value=0)
        
        with col4:
            max_amount = st.number_input("Max Amount", min_value=0, value=10000)
        
        # Apply filters
        filtered_loans = loans_df.copy()
        
        if status_filter:
            filtered_loans = filtered_loans[filtered_loans["status"].isin(status_filter)]
        
        if purpose_filter:
            filtered_loans = filtered_loans[filtered_loans["purpose"].isin(purpose_filter)]
        
        filtered_loans = filtered_loans[
            (filtered_loans["amount"] >= min_amount) & 
            (filtered_loans["amount"] <= max_amount)
        ]
        
        # Display loan table
        st.dataframe(
            filtered_loans[["id", "borrower_name", "purpose", "amount", "term_months", "interest_rate", "status", "application_date"]],
            column_config={
                "id": "Loan ID",
                "borrower_name": "Borrower",
                "purpose": "Purpose",
                "amount": st.column_config.NumberColumn("Amount", format="$%.2f"),
                "term_months": "Term (months)",
                "interest_rate": st.column_config.NumberColumn("Interest Rate", format="%.1f%%"),
                "status": "Status",
                "application_date": "Application Date"
            },
            hide_index=True,
            use_container_width=True
        )
        
        # Loan details modal
        if st.button("Create New Loan"):
            st.session_state.show_add_loan = True
        
        if st.session_state.get("show_add_loan", False):
            with st.form("add_loan_form"):
                st.subheader("Create New Loan")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    borrower_id = st.selectbox("Borrower*", options=users_df["name"].tolist())
                    amount = st.number_input("Loan Amount*", min_value=100, step=100)
                    term_months = st.selectbox("Term (months)*", [3, 6, 12, 18, 24, 36])
                
                with col2:
                    purpose = st.selectbox("Purpose*", loans_df["purpose"].unique())
                    interest_rate = st.number_input("Interest Rate (%)", min_value=0.0, max_value=100.0, value=12.0, step=0.5)
                    status = st.selectbox("Status*", ["Pending", "Approved", "Disbursed", "Rejected"])
                
                notes = st.text_area("Notes")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.form_submit_button("Create Loan"):
                        # In a real app, this would create a new loan in the database
                        st.success(f"Loan of ${amount:,.2f} created successfully!")
                        st.session_state.show_add_loan = False
                        st.rerun()
                
                with col2:
                    if st.form_submit_button("Cancel"):
                        st.session_state.show_add_loan = False
                        st.rerun()
    
    with tab4:  # Transactions tab
        st.header("Transaction Management")
        
        # Filters
        col1, col2, col3 = st.columns(3)
        
        with col1:
            type_filter = st.multiselect(
                "Transaction Type",
                options=transactions_df["type"].unique(),
                default=transactions_df["type"].unique()
            )
        
        with col2:
            status_filter = st.multiselect(
                "Status",
                options=transactions_df["status"].unique(),
                default=transactions_df["status"].unique()
            )
        
        with col3:
            date_range = st.date_input(
                "Date Range",
                value=[
                    datetime.now() - timedelta(days=30),
                    datetime.now()
                ],
                max_value=datetime.now()
            )
        
        # Apply filters
        filtered_transactions = transactions_df.copy()
        
        if type_filter:
            filtered_transactions = filtered_transactions[filtered_transactions["type"].isin(type_filter)]
        
        if status_filter:
            filtered_transactions = filtered_transactions[filtered_transactions["status"].isin(status_filter)]
        
        if len(date_range) == 2:
            start_date = pd.to_datetime(date_range[0])
            end_date = pd.to_datetime(date_range[1]) + timedelta(days=1)
            filtered_transactions = filtered_transactions[
                (pd.to_datetime(filtered_transactions["date"]) >= start_date) &
                (pd.to_datetime(filtered_transactions["date"]) <= end_date)
            ]
        
        # Display transaction table
        st.dataframe(
            filtered_transactions[["date", "user_name", "type", "amount", "fee", "net_amount", "status", "channel"]],
            column_config={
                "date": "Date",
                "user_name": "User",
                "type": "Type",
                "amount": st.column_config.NumberColumn("Amount", format="$%.2f"),
                "fee": st.column_config.NumberColumn("Fee", format="$%.2f"),
                "net_amount": st.column_config.NumberColumn("Net Amount", format="$%.2f"),
                "status": "Status",
                "channel": "Channel"
            },
            hide_index=True,
            use_container_width=True
        )
        
        # Transaction details modal
        if st.button("Create New Transaction"):
            st.session_state.show_add_transaction = True
        
        if st.session_state.get("show_add_transaction", False):
            with st.form("add_transaction_form"):
                st.subheader("Create New Transaction")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    user_id = st.selectbox("User*", options=users_df["name"].tolist())
                    amount = st.number_input("Amount*", min_value=0.01, step=0.01, format="%.2f")
                    transaction_type = st.selectbox("Type*", transactions_df["type"].unique())
                
                with col2:
                    fee = st.number_input("Fee", min_value=0.00, step=0.01, format="%.2f")
                    status = st.selectbox("Status*", ["Completed", "Pending", "Failed", "Reversed"])
                    channel = st.selectbox("Channel*", ["Web", "Mobile App", "USSD", "Bank Transfer", "Agent"])
                
                description = st.text_area("Description")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.form_submit_button("Create Transaction"):
                        # In a real app, this would create a new transaction in the database
                        st.success(f"Transaction of ${amount:,.2f} created successfully!")
                        st.session_state.show_add_transaction = False
                        st.rerun()
                
                with col2:
                    if st.form_submit_button("Cancel"):
                        st.session_state.show_add_transaction = False
                        st.rerun()
    
    with tab5:  # Reports tab
        st.header("Reports & Analytics")
        
        # Report type selection
        report_type = st.selectbox(
            "Select Report",
            ["Loan Performance", "User Activity", "Financial Summary", "Risk Analysis"]
        )
        
        # Date range selector
        col1, col2 = st.columns(2)
        
        with col1:
            start_date = st.date_input("Start Date", value=datetime.now() - timedelta(days=365))
        
        with col2:
            end_date = st.date_input("End Date", value=datetime.now())
        
        # Generate report button
        if st.button("Generate Report"):
            with st.spinner("Generating report..."):
                # In a real app, this would generate a report based on the selected criteria
                st.success("Report generated successfully!")
                
                # Display report based on type
                if report_type == "Loan Performance":
                    st.subheader("Loan Performance Report")
                    
                    # Loan status distribution
                    st.markdown("### Loan Status Distribution")
                    
                    status_counts = loans_df["status"].value_counts().reset_index()
                    status_counts.columns = ["Status", "Count"]
                    
                    fig = px.pie(
                        status_counts, 
                        values="Count", 
                        names="Status",
                        color_discrete_sequence=px.colors.sequential.RdBu
                    )
                    
                    fig.update_traces(
                        textposition='inside',
                        textinfo='percent+label',
                        hovertemplate="%{label}: %{value} (%{percent})"
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Loan volume by month
                    st.markdown("### Loan Volume by Month")
                    
                    loans_df["application_date"] = pd.to_datetime(loans_df["application_date"])
                    monthly_volume = loans_df.groupby(pd.Grouper(key="application_date", freq='M'))["amount"].sum().reset_index()
                    
                    fig = px.bar(
                        monthly_volume,
                        x="application_date",
                        y="amount",
                        labels={"application_date": "Month", "amount": "Total Loan Volume ($)"}
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Loan performance metrics
                    st.markdown("### Performance Metrics")
                    
                    total_loans = len(loans_df)
                    approved_loans = len(loans_df[loans_df["status"].isin(["Approved", "Disbursed", "Completed"])])
                    defaulted_loans = len(loans_df[loans_df["status"] == "Defaulted"])
                    completed_loans = len(loans_df[loans_df["status"] == "Completed"])
                    completed_or_defaulted = len(loans_df[loans_df["status"].isin(["Completed", "Defaulted"])])
                    repayment_rate = (completed_loans / completed_or_defaulted * 100) if completed_or_defaulted > 0 else 0
                    
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("Total Loans", total_loans)
                    
                    with col2:
                        st.metric("Approval Rate", f"{(approved_loans / total_loans * 100):.1f}%")
                    
                    with col3:
                        st.metric("Default Rate", f"{(defaulted_loans / total_loans * 100):.1f}%")
                    
                    with col4:
                        st.metric("Repayment Rate", f"{repayment_rate:.1f}%")
                    
                    # Export button
                    st.download_button(
                        label="Download Report as PDF",
                        data="This would be the PDF content in a real app.",
                        file_name=f"loan_performance_report_{datetime.now().strftime('%Y%m%d')}.pdf",
                        mime="application/pdf"
                    )
                
                elif report_type == "User Activity":
                    st.subheader("User Activity Report")
                    
                    # User growth
                    st.markdown("### User Growth")
                    
                    users_df["registration_date"] = pd.to_datetime(users_df["registration_date"])
                    monthly_users = users_df.groupby(pd.Grouper(key="registration_date", freq='M')).size().cumsum().reset_index()
                    monthly_users.columns = ["Month", "Total Users"]
                    
                    fig = px.line(
                        monthly_users,
                        x="Month",
                        y="Total Users",
                        labels={"Month": "", "Total Users": "Total Users"}
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # User activity metrics
                    st.markdown("### Activity Metrics")
                    
                    active_users = len(users_df[users_df["status"] == "Active"])
                    avg_loans_per_user = users_df["loans_taken"].mean()
                    avg_credit_score = users_df["credit_score"].mean()
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Total Users", len(users_df))
                    
                    with col2:
                        st.metric("Active Users", active_users)
                    
                    with col3:
                        st.metric("Avg Loans per User", f"{avg_loans_per_user:.1f}")
                    
                    # User type distribution
                    st.markdown("### User Type Distribution")
                    
                    user_type_counts = users_df["user_type"].value_counts().reset_index()
                    user_type_counts.columns = ["User Type", "Count"]
                    
                    fig = px.pie(
                        user_type_counts, 
                        values="Count", 
                        names="User Type",
                        color_discrete_sequence=px.colors.sequential.Blues
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Export button
                    st.download_button(
                        label="Download Report as PDF",
                        data="This would be the PDF content in a real app.",
                        file_name=f"user_activity_report_{datetime.now().strftime('%Y%m%d')}.pdf",
                        mime="application/pdf"
                    )
                
                elif report_type == "Financial Summary":
                    st.subheader("Financial Summary Report")
                    
                    # Revenue by month
                    st.markdown("### Revenue by Month")
                    
                    transactions_df["date"] = pd.to_datetime(transactions_df["date"])
                    revenue = transactions_df[transactions_df["type"].isin(["Loan Repayment", "Fee"])]
                    monthly_revenue = revenue.groupby(pd.Grouper(key="date", freq='M'))["amount"].sum().reset_index()
                    
                    fig = px.bar(
                        monthly_revenue,
                        x="date",
                        y="amount",
                        labels={"date": "Month", "amount": "Revenue ($)"}
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Financial metrics
                    st.markdown("### Financial Metrics")
                    
                    total_volume = loans_df["amount"].sum()
                    total_revenue = transactions_df[transactions_df["type"].isin(["Loan Repayment", "Fee"])]["amount"].sum()
                    avg_loan_size = loans_df["amount"].mean()
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Total Loan Volume", f"${total_volume:,.2f}")
                    
                    with col2:
                        st.metric("Total Revenue", f"${total_revenue:,.2f}")
                    
                    with col3:
                        st.metric("Average Loan Size", f"${avg_loan_size:,.2f}")
                    
                    # Revenue by type
                    st.markdown("### Revenue by Type")
                    
                    revenue_by_type = transactions_df[transactions_df["type"].isin(["Loan Repayment", "Fee"])]
                    revenue_by_type = revenue_by_type.groupby("type")["amount"].sum().reset_index()
                    
                    fig = px.pie(
                        revenue_by_type,
                        values="amount",
                        names="type",
                        color_discrete_sequence=px.colors.sequential.Greens
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Export button
                    st.download_button(
                        label="Download Report as PDF",
                        data="This would be the PDF content in a real app.",
                        file_name=f"financial_summary_report_{datetime.now().strftime('%Y%m%d')}.pdf",
                        mime="application/pdf"
                    )
                
                elif report_type == "Risk Analysis":
                    st.subheader("Risk Analysis Report")
                    
                    # Risk score distribution
                    st.markdown("### User Risk Score Distribution")
                    
                    fig = px.histogram(
                        users_df,
                        x="credit_score",
                        nbins=20,
                        labels={"credit_score": "Credit Score"}
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Risk metrics
                    st.markdown("### Risk Metrics")
                    
                    avg_risk_score = users_df["credit_score"].mean()
                    high_risk_users = len(users_df[users_df["credit_score"] < 580])
                    default_rate = (len(loans_df[loans_df["status"] == "Defaulted"]) / 
                                  len(loans_df[loans_df["status"].isin(["Completed", "Defaulted"])])) * 100 \
                                  if len(loans_df[loans_df["status"].isin(["Completed", "Defaulted"])]) > 0 else 0
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Average Credit Score", f"{avg_risk_score:.0f}")
                    
                    with col2:
                        st.metric("High-Risk Users", high_risk_users)
                    
                    with col3:
                        st.metric("Portfolio Default Rate", f"{default_rate:.1f}%")
                    
                    # Risk by loan purpose
                    st.markdown("### Default Rate by Loan Purpose")
                    
                    defaulted_loans = loans_df[loans_df["status"] == "Defaulted"]
                    completed_loans = loans_df[loans_df["status"] == "Completed"]
                    
                    default_rates = []
                    for purpose in loans_df["purpose"].unique():
                        total = len(loans_df[loans_df["purpose"] == purpose])
                        defaults = len(defaulted_loans[defaulted_loans["purpose"] == purpose])
                        completes = len(completed_loans[completed_loans["purpose"] == purpose])
                        rate = (defaults / (defaults + completes)) * 100 if (defaults + completes) > 0 else 0
                        default_rates.append({"Purpose": purpose, "Default Rate": rate, "Count": total})
                    
                    default_rates_df = pd.DataFrame(default_rates)
                    
                    fig = px.bar(
                        default_rates_df.sort_values("Default Rate", ascending=False),
                        x="Purpose",
                        y="Default Rate",
                        color="Count",
                        color_continuous_scale=px.colors.sequential.Reds,
                        labels={"Default Rate": "Default Rate (%)"}
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Export button
                    st.download_button(
                        label="Download Report as PDF",
                        data="This would be the PDF content in a real app.",
                        file_name=f"risk_analysis_report_{datetime.now().strftime('%Y%m%d')}.pdf",
                        mime="application/pdf"
                    )
    
    # Add custom styles
    st.markdown("""
        <style>
            /* Style the tab buttons */
            .stTabs [data-baseweb="tab-list"] {
                gap: 8px;
            }
            
            .stTabs [data-baseweb="tab"] {
                height: 50px;
                white-space: nowrap;
                padding: 0 16px;
                background-color: #f1f5f9;
                border-radius: 8px 8px 0 0;
                margin-right: 0 !important;
            }
            
            .stTabs [aria-selected="true"] {
                background-color: #3b82f6;
                color: white;
            }
            
            /* Style form elements */
            .stTextInput > div > div > input,
            .stTextArea > div > div > textarea,
            .stNumberInput > div > div > input,
            .stSelectbox > div > div > div {
                border-radius: 8px;
                padding: 0.5rem 0.75rem;
                border: 1px solid #e2e8f0;
            }
            
            .stButton > button {
                border-radius: 8px;
                padding: 0.5rem 1rem;
                font-weight: 500;
                transition: all 0.2s;
            }
            
            .stButton > button:hover {
                transform: translateY(-1px);
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
            }
            
            /* Style the dataframes */
            .stDataFrame {
                border-radius: 8px;
                overflow: hidden;
                box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
            }
            
            /* Style the metrics */
            .stMetric {
                background-color: #f8fafc;
                border-radius: 8px;
                padding: 1rem;
                border: 1px solid #e2e8f0;
            }
            
            .stMetricLabel {
                font-size: 0.9rem;
                color: #64748b;
            }
            
            .stMetricValue {
                font-size: 1.5rem;
                font-weight: 600;
                color: #1e293b;
            }
        </style>
    """, unsafe_allow_html=True)
