import streamlit as st
from streamlit_option_menu import option_menu
import os
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime

# Load environment variables
load_dotenv()

# Set page config
st.set_page_config(
    page_title="Poverty Alleviation Platform",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add custom CSS
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stButton>button {
        width: 100%;
    }
    .stTextInput>div>div>input {
        padding: 10px;
    }
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    ::-webkit-scrollbar-track {
        background: #f1f1f1;
    }
    ::-webkit-scrollbar-thumb {
        background: #888;
        border-radius: 4px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #555;
    }
    /* Card styling */
    .card {
        background: white;
        border-radius: 10px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 1.5rem;
    }
    /* Custom tooltip */
    .tooltip {
        position: relative;
        display: inline-block;
        border-bottom: 1px dotted black;
    }
    .tooltip .tooltiptext {
        visibility: hidden;
        width: 200px;
        background-color: #555;
        color: #fff;
        text-align: center;
        border-radius: 6px;
        padding: 5px;
        position: absolute;
        z-index: 1;
        bottom: 125%;
        left: 50%;
        margin-left: -100px;
        opacity: 0;
        transition: opacity 0.3s;
    }
    .tooltip:hover .tooltiptext {
        visibility: visible;
        opacity: 1;
    }
    </style>
""", unsafe_allow_html=True)

# Import pages
from pages import (
    dashboard,
    transactions,
    loans,
    crowdfunding,
    insights,
    admin,
    auth,
    settings
)

# App state
class State:
    def __init__(self):
        self.token = None
        self.user = None
        self.is_authenticated = False
        self.is_admin = False

# Initialize session state
if 'state' not in st.session_state:
    st.session_state.state = State()

# Initialize other session state variables
if 'show_create_campaign' not in st.session_state:
    st.session_state.show_create_campaign = False
if 'show_organizations' not in st.session_state:
    st.session_state.show_organizations = False
if 'show_learn_more' not in st.session_state:
    st.session_state.show_learn_more = False
if 'eligibility' not in st.session_state:
    st.session_state.eligibility = None

def main():
    # Check authentication
    if not st.session_state.state.is_authenticated:
        auth.show_login_page()
        return

    # Sidebar navigation
    with st.sidebar:
        st.image("assets/logo.png", width=200)
        st.title("Poverty Alleviation")
        
        if st.session_state.state.is_authenticated:
            # Show user info
            st.markdown(f"### Welcome, {st.session_state.state.user.get('username', 'User')}")
            
            # Navigation menu
            menu_options = [
                "Dashboard",
                "Transactions",
                "Loans",
                "Crowdfunding",
                "Insights",
                "Settings"
            ]
            
            # Add admin menu if user is admin
            if st.session_state.state.get('is_admin', False):
                menu_options.append("Admin")
            
            selected = option_menu(
                menu_title=None,
                options=menu_options,
                icons=[
                    "house", "cash-coin", "bank", "people", "graph-up", "gear", "shield-lock"
                ][:len(menu_options)],
                default_index=0,
                styles={
                    "container": {"padding": "0!important", "background-color": "#f8f9fa"},
                    "nav-link": {"font-size": "14px", "text-align": "left", "margin": "5px 0", "border-radius": "5px"},
                    "nav-link-selected": {"background-color": "#0d6efd"},
                }
            )
            
            # Logout button
            if st.button("Logout", use_container_width=True, type="primary"):
                st.session_state.state = State()
                st.experimental_rerun()
                
            # Add some space at the bottom
            st.markdown("---")
            st.markdown("### Quick Actions")
            
            # Quick action buttons
            if st.button("💳 New Transaction", use_container_width=True):
                st.session_state.show_new_transaction = True
                
            if st.button("📝 Apply for Loan", use_container_width=True):
                st.session_state.show_loan_application = True
                
            if st.button("🎯 Create Campaign", use_container_width=True):
                st.session_state.show_create_campaign = True
            
            # Add footer
            st.markdown("---")
            st.caption(f"v1.0.0 • {datetime.now().year} © Poverty Alleviation Platform")
            
        else:
            st.write("Please log in to access the platform.")
            selected = "Login"
    
    # Display selected page
    if selected == "Dashboard":
        dashboard.show()
    elif selected == "Transactions":
        transactions.show()
    elif selected == "Loans":
        loans.show()
    elif selected == "Crowdfunding":
        crowdfunding.show()
    elif selected == "Insights":
        insights.show()
    elif selected == "Settings":
        settings.show()
    elif selected == "Admin" and st.session_state.state.is_admin:
        admin.show()

if __name__ == "__main__":
    # Add a loading spinner while the app is initializing
    with st.spinner('Loading application...'):
        main()
