import asyncio
import os
import sys
import logging
import streamlit as st
from dotenv import load_dotenv
from typing import Dict, Any, Callable, Awaitable, Optional, List, Tuple
from streamlit_option_menu import option_menu
import base64
from pathlib import Path

# Set page config at the top
st.set_page_config(
    page_title="SDG Finance Platform",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern styling
def load_css():
    custom_css = """
    <style>
        /* Main container */
        .main {
            background-color: #f8f9fa;
        }
        
        /* Sidebar */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #2c3e50 0%, #1a2530 100%);
            color: white;
            padding: 1rem 0.5rem;
        }
        
        /* Sidebar header */
        [data-testid="stSidebarNav"]::before {
            content: "SDG Finance";
            display: block;
            font-size: 1.5rem;
            font-weight: 700;
            color: #fff;
            padding: 1rem 1rem 2rem 1rem;
            text-align: center;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            margin-bottom: 1rem;
        }
        
        /* Menu items */
        .st-bb {
            background-color: transparent !important;
        }
        
        .st-bb:hover {
            background-color: rgba(255, 255, 255, 0.1) !important;
        }
        
        /* Cards */
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
        
        /* Buttons */
        .stButton>button {
            border-radius: 20px;
            border: none;
            background: linear-gradient(90deg, #4b6cb7 0%, #182848 100%);
            color: white;
            font-weight: 500;
            padding: 0.5rem 1.5rem;
            transition: all 0.3s ease;
        }
        
        .stButton>button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        }
        
        /* Input fields */
        .stTextInput>div>div>input {
            border-radius: 8px;
            border: 1px solid #e0e0e0;
            padding: 0.5rem 1rem;
        }
        
        /* Tables */
        .stDataFrame {
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        }
        
        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {
            gap: 0.5rem;
        }
        
        .stTabs [data-baseweb="tab"] {
            border-radius: 8px 8px 0 0 !important;
            padding: 0.5rem 1.5rem;
            transition: all 0.3s ease;
        }
        
        .stTabs [aria-selected="true"] {
            background-color: #4b6cb7;
            color: white !important;
        }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Set auth token from environment variable if available
if 'AUTH_TOKEN' not in st.session_state and os.getenv('AUTH_TOKEN'):
    st.session_state.auth_token = os.getenv('AUTH_TOKEN')
    st.session_state.is_authenticated = True
    logger.info("Authenticated with token from environment")

# Add the src directory to the path for module imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Navigation configuration
MENU_ITEMS = [
    {"label": "Dashboard", "icon": "speedometer2", "module": "dashboard", "roles": ["user", "admin"]},
    {"label": "AI Recommendations", "icon": "robot", "module": "ai_recommendations", "roles": ["user", "admin"]},
    {"label": "Transactions", "icon": "cash-stack", "module": "transactions", "roles": ["user", "admin"]},
    {"label": "Crowdfunding", "icon": "people-fill", "module": "crowdfunding", "roles": ["user", "admin"]},
    {"label": "Micro Loans", "icon": "piggy-bank", "module": "microloans", "roles": ["user", "admin"]},
    {"label": "Poverty Map", "icon": "geo-alt", "module": "poverty_map", "roles": ["user", "admin"]},
    {"label": "My Profile", "icon": "person-circle", "module": "profile", "roles": ["user", "admin"]},
    {"label": "Admin Panel", "icon": "shield-lock", "module": "admin_panel", "roles": ["admin"]},
]

# Import page modules from the pages package with error handling
PAGE_MODULES = {}
try:
    from pages import (
        dashboard,
        ai_recommendations,
        transactions,
        crowdfunding,
        microloans,
        poverty_map,
        profile,
        admin_panel,
        auth
    )
    
    PAGE_MODULES = {
        "dashboard": dashboard,
        "ai_recommendations": ai_recommendations,
        "transactions": transactions,
        "crowdfunding": crowdfunding,
        "microloans": microloans,
        "poverty_map": poverty_map,
        "profile": profile,
        "admin_panel": admin_panel,
        "auth": auth
    }
    
except ImportError as e:
    logger.error(f"Failed to import page modules: {e}")
    st.error("Failed to load application modules. Please check the logs.")
    st.stop()

# Load environment variables
load_dotenv()

# Type aliases
PageFunc = Callable[[], Awaitable[None]]

# Set page config
try:
    st.set_page_config(
        page_title="Financial Inclusion App",
        page_icon="💰",
        layout="wide",
        initial_sidebar_state="collapsed",
        menu_items={
            'Get Help': 'https://github.com/yourusername/financial-inclusion-app',
            'Report a bug': 'https://github.com/yourusername/financial-inclusion-app/issues',
            'About': """
            # Financial Inclusion App
            
            Empowering communities through financial services.
            
            Version: 1.0.0  
            Last updated: 2023-11-15
            """
        }
    )
except Exception as e:
    logger.error(f"Failed to set page config: {e}")
    st.error("Failed to initialize the application. Please try refreshing the page.")
    st.stop()

# Custom CSS to hide Streamlit elements and add custom styles
st.markdown("""
    <style>
        /* Hide Streamlit default elements */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* Custom styles */
        .main {
            padding: 1rem 2rem;
        }
        
        .card {
            background: white;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            padding: 1.5rem;
            margin-bottom: 1.5rem;
        }
        
        .navbar {
            background: #2563eb;
            color: white;
            padding: 1rem 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 2rem;
            border-radius: 0 0 10px 10px;
        }
        
        .logo {
            font-size: 1.5rem;
            font-weight: bold;
        }
        
        .nav-links {
            display: flex;
            gap: 1.5rem;
        }
        
        .nav-link {
            color: white;
            text-decoration: none;
            font-weight: 500;
            padding: 0.5rem 1rem;
            border-radius: 5px;
            transition: background 0.3s;
        }
        
        .nav-link:hover {
            background: rgba(255, 255, 255, 0.1);
        }
        
        .nav-link.active {
            background: rgba(255, 255, 255, 0.2);
        }
    </style>
""", unsafe_allow_html=True)

# Import pages
from pages import (
    dashboard,
    ai_recommendations,
    transactions,
    crowdfunding,
    microloans,
    poverty_map,
    profile,
    admin_panel,
    auth
)

# Initialize session state with default values
def init_session_state():
    """Initialize the session state with default values."""
    defaults = {
        'authenticated': False,
        'is_admin': False,
        'current_user': None,
        'current_page': 'Dashboard',
        'initialized': True,
        'show_sidebar': False,
        'error': None,
        'success': None,
        'info': None,
        'warning': None,
        'page_title': 'Financial Inclusion App',
        'page_icon': '💰',
        'theme': 'light',
        'language': 'en',
        'timezone': 'UTC',
        'last_activity': None,
        'permissions': {},
        'settings': {
            'notifications': True,
            'analytics': False,
            'dark_mode': False,
            'compact_view': False
        },
        'navigation': {
            'previous_pages': [],
            'can_go_back': False
        },
        'data': {}
    }
    
    # Only set defaults if they don't exist
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

# Initialize the session state
init_session_state()

# Set default page if not set
if 'page' not in st.session_state:
    st.session_state.page = 'dashboard'
PAGES: Dict[str, Dict[str, Any]] = {
    "Dashboard": {
        "module": dashboard,
        "icon": "📊",
        "requires_auth": True,
        "category": "main",
        "order": 1
    },
    "AI Recommendations": {
        "module": ai_recommendations,
        "icon": "🤖",
        "requires_auth": True,
        "category": "tools",
        "order": 2
    },
    "Transactions": {
        "module": transactions,
        "icon": "💳",
        "requires_auth": True,
        "category": "finance",
        "order": 3
    },
    "Crowdfunding": {
        "module": crowdfunding,
        "icon": "🤝",
        "requires_auth": True,
        "category": "community",
        "order": 4
    },
    "Microloans": {
        "module": microloans,
        "icon": "📈",
        "requires_auth": True,
        "category": "finance",
        "order": 5
    },
    "Poverty Map": {
        "module": poverty_map,
        "icon": "🗺️",
        "requires_auth": True,
        "category": "community",
        "order": 6
    },
    "Profile": {
        "module": profile,
        "icon": "👤",
        "requires_auth": True,
        "category": "account",
        "order": 98
    },
    "Admin": {
        "module": admin_panel,
        "icon": "🔒",
        "requires_auth": True,
        "requires_admin": True,
        "category": "admin",
        "order": 99
    },
    "Login": {
        "module": auth,
        "icon": "🔑",
        "requires_auth": False,
        "category": "account",
        "order": 100
    }
}

# Group navigation items by category
NAV_CATEGORIES = {
    "main": {"name": "Main", "icon": "🏠"},
    "finance": {"name": "Finance", "icon": "💰"},
    "community": {"name": "Community", "icon": "🌍"},
    "tools": {"name": "Tools", "icon": "🛠️"},
    "account": {"name": "Account", "icon": "👤"},
    "admin": {"name": "Administration", "icon": "🔒"}
}

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.is_admin = False
    st.session_state.current_user = None
    st.session_state.current_page = "Dashboard"

def render_navbar():
    """Render the top navigation bar."""
    st.markdown("""
        <div class="navbar">
            <div class="logo">Financial Inclusion App</div>
            <div class="nav-links">
    """, unsafe_allow_html=True)
    
    # Only show navigation if user is authenticated
    if st.session_state.authenticated:
        for page_name in PAGES:
            # Skip admin panel if not admin
            if page_name == "Admin Panel" and not st.session_state.is_admin:
                continue
                
            active = "active" if st.session_state.current_page == page_name else ""
            st.markdown(
                f'<a href="?page={page_name}" class="nav-link {active}">{page_name}</a>',
                unsafe_allow_html=True
            )
        
        # Logout button
        if st.button("Logout", key="logout_btn"):
            st.session_state.authenticated = False
            st.session_state.is_admin = False
            st.session_state.current_user = None
            st.rerun()
    
    st.markdown("""
            </div>
        </div>
    """, unsafe_allow_html=True)

async def render_page(page_name: str) -> None:
    """Render the specified page."""
    if page_name not in PAGES:
        page_name = "Dashboard"
        st.session_state.current_page = "Dashboard"
    
    page_config = PAGES[page_name]
    
    # Check authentication
    if page_config["requires_auth"] and not st.session_state.authenticated:
        st.warning("Please log in to access this page.")
        st.session_state.current_page = "Login"
        st.rerun()
        return
    
    # Check admin access
    if page_config.get("requires_admin", False) and not st.session_state.is_admin:
        st.error("You don't have permission to access this page.")
        st.session_state.current_page = "Dashboard"
        st.rerun()
        return
    
    # Render the page
    try:
        await page_config["module"].show()
    except Exception as e:
        st.error(f"An error occurred while loading the page: {str(e)}")
        st.exception(e)  # Log full exception for debugging

async def main():
    """Main application function."""
    # Load CSS
    load_css()
    
    # Check authentication
    if not st.session_state.get('authenticated', False):
        # Render login page
        if 'auth' in PAGE_MODULES:
            if hasattr(PAGE_MODULES['auth'], 'show') and asyncio.iscoroutinefunction(PAGE_MODULES['auth'].show):
                await PAGE_MODULES['auth'].show()
            else:
                PAGE_MODULES['auth'].show()
        else:
            st.error("Authentication module not found")
        return
    
    # Get current page
    current_page = st.session_state.get('current_page', 'Dashboard')
    
    # Create main layout
    col1, col2 = st.columns([1, 4])
    
    # Render the sidebar in the first column
    with col1:
        render_sidebar()
    
    # Render the main content in the second column
    with col2:
        # Render the current page
        if current_page in PAGES:
            try:
                page_config = PAGES[current_page]
                # Check if module has an async show method
                if hasattr(page_config["module"], 'show') and asyncio.iscoroutinefunction(page_config["module"].show):
                    await page_config["module"].show()
                else:
                    page_config["module"].show()
            except Exception as e:
                st.error(f"Error loading page: {str(e)}")
                logger.error(f"Error in page {current_page}: {str(e)}")
        else:
            st.warning("Page not found. Redirecting to dashboard...")
            st.session_state.current_page = "Dashboard"
            st.rerun()
    
    # Add footer
    st.markdown("""
    <style>
        .footer {
            padding: 1rem 0;
            margin-top: 2rem;
            text-align: center;
            color: #666;
            font-size: 0.8rem;
            border-top: 1px solid #e0e0e0;
        }
        .stTextInput > div > div > input,
        .stTextArea > div > div > textarea,
        .stSelectbox > div > div > div,
        .stNumberInput > div > div > input,
        .stDateInput > div > div > input {
            border-radius: 0.375rem;
            border: 1px solid #d1d5db;
            padding: 0.5rem 0.75rem;
        }
        
        /* Table styling */
        .stDataFrame {
            border-radius: 0.5rem;
            overflow: hidden;
        }
        
        /* Hide Streamlit branding */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
    </style>
    <div class="footer">
        2023 SDG Finance Platform | Version 1.0.0 | 
        <a href="#" style="color: #4b6cb7; text-decoration: none;">Help</a> | 
        <a href="#" style="color: #4b6cb7; text-decoration: none;">Terms</a> | 
        <a href="#" style="color: #4b6cb7; text-decoration: none;">Privacy</a>
    </div>
    """, unsafe_allow_html=True)

def run():
    """Run the Streamlit app."""
    # This is the main entry point for Streamlit
    asyncio.run(main())

if __name__ == "__main__":
    # This is the simplest and most reliable way to run the app
    # Just import streamlit and run the app
    import streamlit as st
    
    # Check if we're already running in Streamlit
    if hasattr(st, '_is_running_with_streamlit'):
        # If yes, just run the main function
        import asyncio
        asyncio.run(main())
    else:
        # If not, print instructions
        print("Please run this application using Streamlit with the following command:")
        print("\n    streamlit run app.py\n")
        print("Or with custom options:")
        print("\n    streamlit run app.py --server.port=8501 --server.address=0.0.0.0\n")
