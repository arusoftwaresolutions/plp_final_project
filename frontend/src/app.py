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

# Custom CSS for the app
st.markdown("""
<style>
.main .block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}
.stButton>button {
    width: 100%;
}
.stTextInput>div>div>input {
    border-radius: 20px;
}
/* Hide the default Streamlit menu */
#MainMenu {visibility: hidden;}
header {visibility: hidden;}
footer {visibility: hidden;}
/* Style for auth forms */
.auth-form {
    max-width: 400px;
    margin: 0 auto;
    padding: 2rem;
    border-radius: 10px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    background-color: white;
}
</style>
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

# Lazy import pages to avoid startup crashes if a page has an import issue
import importlib

def safe_import(module_path: str):
    try:
        return importlib.import_module(module_path)
    except Exception as e:
        def _fallback_show():
            st.error(f"Failed to load page '{module_path}'.")
            st.exception(e)
        return type("_MissingPage", (), {"show": staticmethod(_fallback_show)})

dashboard = safe_import("pages.dashboard")
transactions = safe_import("pages.transactions")
loans = safe_import("pages.loans")
crowdfunding = safe_import("pages.crowdfunding")
insights = safe_import("pages.insights")
admin = safe_import("pages.admin")
auth = safe_import("pages.auth")
settings = safe_import("pages.settings")

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

# Initialize session variables
for var in ['show_create_campaign', 'show_organizations', 'show_learn_more', 'eligibility']:
    if var not in st.session_state:
        st.session_state[var] = None

# Check authentication state
is_authenticated = hasattr(st.session_state.state, 'is_authenticated') and st.session_state.state.is_authenticated

# Show sidebar only if user is authenticated
if is_authenticated:
    # Navigation menu
    with st.sidebar:
        st.image("assets/logo.png", width=200)
        st.title("Poverty Alleviation")
        
        # Show user info
        if hasattr(st.session_state.state, 'user') and st.session_state.state.user:
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
        if hasattr(st.session_state.state, 'is_admin') and st.session_state.state.is_admin:
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
        
        # Logout button at the bottom
        st.markdown("---")
        if st.button(" Logout", use_container_width=True, type="primary"):
            st.session_state.state = State()
            st.experimental_rerun()
        
        # Version info
        st.caption(f"v1.0.0 • {datetime.now().year} Poverty Alleviation Platform")
    
    # Main content area
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
    elif selected == "Admin" and hasattr(st.session_state.state, 'is_admin') and st.session_state.state.is_admin:
        admin.show()

if __name__ == "__main__":
    # Add a loading spinner while the app is initializing
    with st.spinner('Loading application...'):
        main()
