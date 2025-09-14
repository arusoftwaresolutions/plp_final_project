import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import os

# Configure page
st.set_page_config(
    page_title="Financial Platform",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Backend URL
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

class APIClient:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.token = None
    
    def set_token(self, token: str):
        self.token = token
    
    def _get_headers(self):
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers
    
    def login(self, email: str, password: str):
        response = requests.post(
            f"{self.base_url}/api/auth/login",
            json={"email": email, "password": password}
        )
        if response.status_code == 200:
            data = response.json()
            self.set_token(data["access_token"])
            return data
        return None
    
    def register(self, email: str, password: str, full_name: str, user_type: str):
        response = requests.post(
            f"{self.base_url}/api/auth/register",
            json={"email": email, "password": password, "full_name": full_name, "user_type": user_type}
        )
        return response.status_code == 200
    
    def get_user_info(self):
        response = requests.get(
            f"{self.base_url}/api/auth/me",
            headers=self._get_headers()
        )
        if response.status_code == 200:
            return response.json()
        return None
    
    def get_family_dashboard(self):
        response = requests.get(
            f"{self.base_url}/api/families/dashboard",
            headers=self._get_headers()
        )
        if response.status_code == 200:
            return response.json()
        return None
    
    def get_transactions(self):
        response = requests.get(
            f"{self.base_url}/api/families/transactions",
            headers=self._get_headers()
        )
        if response.status_code == 200:
            return response.json()
        return None
    
    def create_transaction(self, transaction_data):
        response = requests.post(
            f"{self.base_url}/api/families/transactions",
            json=transaction_data,
            headers=self._get_headers()
        )
        return response.status_code == 200
    
    def get_campaigns(self):
        response = requests.get(
            f"{self.base_url}/api/donors/campaigns",
            headers=self._get_headers()
        )
        if response.status_code == 200:
            return response.json()
        return None
    
    def make_donation(self, donation_data):
        response = requests.post(
            f"{self.base_url}/api/donors/donate",
            json=donation_data,
            headers=self._get_headers()
        )
        return response.status_code == 200
    
    def get_ai_recommendations(self):
        response = requests.get(
            f"{self.base_url}/api/ai/recommendations",
            headers=self._get_headers()
        )
        if response.status_code == 200:
            return response.json()
        return None
    
    def get_map_data(self):
        response = requests.get(
            f"{self.base_url}/api/geospatial/map"
        )
        if response.status_code == 200:
            return response.json()
        return None

# Initialize API client
api_client = APIClient(BACKEND_URL)

def login_page():
    st.title("🔐 Login to Financial Platform")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            submit_button = st.form_submit_button("Login")
            
            if submit_button:
                result = api_client.login(email, password)
                if result:
                    st.session_state.logged_in = True
                    st.session_state.user_info = api_client.get_user_info()
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid credentials")
        
        st.markdown("---")
        st.markdown("Don't have an account? Register below:")
        
        with st.form("register_form"):
            reg_email = st.text_input("Email", key="reg_email")
            reg_password = st.text_input("Password", type="password", key="reg_password")
            reg_name = st.text_input("Full Name", key="reg_name")
            reg_type = st.selectbox("User Type", ["family", "donor", "business", "admin"], key="reg_type")
            reg_submit = st.form_submit_button("Register")
            
            if reg_submit:
                success = api_client.register(reg_email, reg_password, reg_name, reg_type)
                if success:
                    st.success("Registration successful! Please login.")
                else:
                    st.error("Registration failed. Email might already exist.")

def family_dashboard():
    st.title("👨‍👩‍👧‍👦 Family Dashboard")
    
    # Get dashboard data
    dashboard_data = api_client.get_family_dashboard()
    if not dashboard_data:
        st.error("Failed to load dashboard data")
        return
    
    # Display key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Income", f"${dashboard_data['total_income']:,.2f}")
    
    with col2:
        st.metric("Total Expenses", f"${dashboard_data['total_expenses']:,.2f}")
    
    with col3:
        st.metric("Net Income", f"${dashboard_data['net_income']:,.2f}")
    
    with col4:
        st.metric("Transactions", dashboard_data['transaction_count'])
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Recent Transactions")
        transactions_df = pd.DataFrame(dashboard_data['recent_transactions'])
        if not transactions_df.empty:
            transactions_df['date'] = pd.to_datetime(transactions_df['date'])
            fig = px.bar(
                transactions_df, 
                x='date', 
                y='amount', 
                color='transaction_type',
                title="Recent Transactions"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No transactions yet")
    
    with col2:
        st.subheader("AI Recommendations")
        recommendations = dashboard_data['ai_recommendations']
        if recommendations:
            for rec in recommendations:
                priority_color = {"high": "red", "medium": "orange", "low": "green"}[rec['priority']]
                st.markdown(f"**{rec['title']}**")
                st.markdown(f"*{rec['description']}*")
                st.markdown(f"Priority: :{priority_color}[{rec['priority'].title()}]")
                st.markdown("---")
        else:
            st.info("No AI recommendations yet")

def add_transaction():
    st.title("➕ Add Transaction")
    
    with st.form("transaction_form"):
        amount = st.number_input("Amount", min_value=0.01, step=0.01)
        transaction_type = st.selectbox("Type", ["income", "expense"])
        category = st.text_input("Category")
        description = st.text_area("Description (optional)")
        
        submit_button = st.form_submit_button("Add Transaction")
        
        if submit_button:
            transaction_data = {
                "amount": amount,
                "transaction_type": transaction_type,
                "category": category,
                "description": description
            }
            
            success = api_client.create_transaction(transaction_data)
            if success:
                st.success("Transaction added successfully!")
                st.rerun()
            else:
                st.error("Failed to add transaction")

def donor_dashboard():
    st.title("💝 Donor Dashboard")
    
    # Get campaigns
    campaigns = api_client.get_campaigns()
    if not campaigns:
        st.error("Failed to load campaigns")
        return
    
    st.subheader("Available Campaigns")
    
    for campaign in campaigns:
        with st.container():
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"**{campaign['title']}**")
                st.markdown(campaign['description'])
                progress = campaign['current_amount'] / campaign['target_amount']
                st.progress(progress)
                st.markdown(f"${campaign['current_amount']:,.2f} of ${campaign['target_amount']:,.2f} raised")
            
            with col2:
                if st.button(f"Donate", key=f"donate_{campaign['id']}"):
                    st.session_state.selected_campaign = campaign
                    st.rerun()
    
    # Donation form
    if 'selected_campaign' in st.session_state:
        st.markdown("---")
        st.subheader(f"Donate to: {st.session_state.selected_campaign['title']}")
        
        with st.form("donation_form"):
            amount = st.number_input("Donation Amount", min_value=1.0, step=1.0)
            is_anonymous = st.checkbox("Anonymous donation")
            
            submit_button = st.form_submit_button("Make Donation")
            
            if submit_button:
                donation_data = {
                    "campaign_id": st.session_state.selected_campaign['id'],
                    "amount": amount,
                    "is_anonymous": is_anonymous
                }
                
                success = api_client.make_donation(donation_data)
                if success:
                    st.success("Donation successful!")
                    del st.session_state.selected_campaign
                    st.rerun()
                else:
                    st.error("Donation failed")

def business_dashboard():
    st.title("🏢 Business Dashboard")
    
    st.subheader("Loan Applications")
    
    # Mock loan applications for demo
    loan_applications = [
        {
            "id": "1",
            "amount": 25000,
            "purpose": "Equipment purchase for expansion",
            "status": "pending",
            "created_at": "2024-01-15"
        },
        {
            "id": "2", 
            "amount": 15000,
            "purpose": "Working capital",
            "status": "approved",
            "created_at": "2024-01-10"
        }
    ]
    
    for loan in loan_applications:
        with st.container():
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.markdown(f"**${loan['amount']:,.2f}** - {loan['purpose']}")
            
            with col2:
                status_color = {"pending": "orange", "approved": "green", "rejected": "red"}[loan['status']]
                st.markdown(f"Status: :{status_color}[{loan['status'].title()}]")
            
            with col3:
                st.markdown(f"Applied: {loan['created_at']}")
    
    st.markdown("---")
    
    # New loan application form
    st.subheader("Apply for New Loan")
    
    with st.form("loan_form"):
        amount = st.number_input("Loan Amount", min_value=1000, step=1000)
        purpose = st.text_area("Purpose of Loan")
        
        submit_button = st.form_submit_button("Submit Application")
        
        if submit_button:
            st.success("Loan application submitted successfully!")

def admin_dashboard():
    st.title("👨‍💼 Admin Dashboard")
    
    # Mock admin stats
    stats = {
        "total_families": 45,
        "total_campaigns": 12,
        "total_donations": 156,
        "total_loans": 8,
        "pending_loans": 3,
        "approved_loans": 5,
        "total_donated": 125000
    }
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Families", stats['total_families'])
    
    with col2:
        st.metric("Total Campaigns", stats['total_campaigns'])
    
    with col3:
        st.metric("Total Donations", stats['total_donations'])
    
    with col4:
        st.metric("Total Donated", f"${stats['total_donated']:,.2f}")
    
    st.markdown("---")
    
    # Loan applications to review
    st.subheader("Pending Loan Applications")
    
    pending_loans = [
        {
            "id": "3",
            "business": "Tech Startup LLC",
            "amount": 50000,
            "purpose": "Product development",
            "applied_date": "2024-01-20"
        }
    ]
    
    for loan in pending_loans:
        with st.container():
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.markdown(f"**{loan['business']}** - ${loan['amount']:,.2f}")
                st.markdown(loan['purpose'])
            
            with col2:
                st.markdown(f"Applied: {loan['applied_date']}")
            
            with col3:
                col_approve, col_reject = st.columns(2)
                with col_approve:
                    if st.button("Approve", key=f"approve_{loan['id']}"):
                        st.success("Loan approved!")
                with col_reject:
                    if st.button("Reject", key=f"reject_{loan['id']}"):
                        st.error("Loan rejected!")

def map_page():
    st.title("🗺️ Poverty Hotspots Map")
    
    # Get map data
    map_data = api_client.get_map_data()
    if not map_data:
        st.error("Failed to load map data")
        return
    
    st.markdown(f"**Hotspots:** {map_data['hotspots_count']} | **Families:** {map_data['families_count']}")
    
    # Display map HTML
    st.components.v1.html(map_data['map_html'], height=600)

def main():
    # Initialize session state
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    
    if not st.session_state.logged_in:
        login_page()
    else:
        user_info = st.session_state.get('user_info', {})
        user_type = user_info.get('user_type', '')
        
        # Sidebar navigation
        with st.sidebar:
            st.markdown(f"Welcome, {user_info.get('full_name', 'User')}!")
            st.markdown(f"Type: {user_type.title()}")
            
            if st.button("Logout"):
                st.session_state.logged_in = False
                st.session_state.user_info = None
                st.rerun()
            
            st.markdown("---")
            
            if user_type == "family":
                page = st.selectbox("Navigation", ["Dashboard", "Add Transaction", "AI Recommendations", "Map"])
            elif user_type == "donor":
                page = st.selectbox("Navigation", ["Dashboard", "Map"])
            elif user_type == "business":
                page = st.selectbox("Navigation", ["Dashboard", "Map"])
            elif user_type == "admin":
                page = st.selectbox("Navigation", ["Dashboard", "Map"])
            else:
                page = "Dashboard"
        
        # Main content
        if page == "Dashboard":
            if user_type == "family":
                family_dashboard()
            elif user_type == "donor":
                donor_dashboard()
            elif user_type == "business":
                business_dashboard()
            elif user_type == "admin":
                admin_dashboard()
        elif page == "Add Transaction" and user_type == "family":
            add_transaction()
        elif page == "AI Recommendations" and user_type == "family":
            st.title("🤖 AI Recommendations")
            recommendations = api_client.get_ai_recommendations()
            if recommendations:
                for rec in recommendations:
                    priority_color = {"high": "red", "medium": "orange", "low": "green"}[rec['priority']]
                    st.markdown(f"**{rec['title']}**")
                    st.markdown(f"*{rec['description']}*")
                    st.markdown(f"Priority: :{priority_color}[{rec['priority'].title()}]")
                    st.markdown("---")
            else:
                st.info("No AI recommendations available")
        elif page == "Map":
            map_page()

if __name__ == "__main__":
    main()
