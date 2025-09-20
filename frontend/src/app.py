import asyncio
import os
import sys
import logging
import streamlit as st
from dotenv import load_dotenv
from typing import Dict, Any, Callable, Awaitable, Optional, List, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Add the src directory to the path for module imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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

# Navigation configuration
PAGES: Dict[str, Dict[str, Any]] = {
    "Dashboard": {
        "module": "dashboard",
        "icon": "📊",
        "requires_auth": True,
        "category": "main",
        "order": 1
    },
    "AI Recommendations": {
        "module": "ai_recommendations",
        "icon": "🤖",
        "requires_auth": True,
        "category": "tools",
        "order": 2
    },
    "Transactions": {
        "module": "transactions",
        "icon": "💳",
        "requires_auth": True,
        "category": "finance",
        "order": 3
    },
    "Crowdfunding": {
        "module": "crowdfunding",
        "icon": "🤝",
        "requires_auth": True,
        "category": "community",
        "order": 4
    },
    "Microloans": {
        "module": "microloans",
        "icon": "📈",
        "requires_auth": True,
        "category": "finance",
        "order": 5
    },
    "Poverty Map": {
        "module": "poverty_map",
        "icon": "🗺️",
        "requires_auth": True,
        "category": "community",
        "order": 6
    },
    "Profile": {
        "module": "profile",
        "icon": "👤",
        "requires_auth": True,
        "category": "account",
        "order": 98
    },
    "Admin Panel": {
        "module": "admin_panel",
        "icon": "🔒",
        "requires_auth": True,
        "requires_admin": True,
        "category": "admin",
        "order": 99,
        "hide_from_nav": False
    },
    "Login": {
        "module": "auth",
        "icon": "🔑",
        "requires_auth": False,
        "hide_from_nav": True,
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
            st.experimental_rerun()
    
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
        st.experimental_rerun()
        return
    
    # Check admin access
    if page_config.get("requires_admin", False) and not st.session_state.is_admin:
        st.error("You don't have permission to access this page.")
        st.session_state.current_page = "Dashboard"
        st.experimental_rerun()
        return
    
    # Render the page
    try:
        await page_config["module"].show()
    except Exception as e:
        st.error(f"An error occurred while loading the page: {str(e)}")
        st.exception(e)  # Log full exception for debugging

async def main():
    """Main application function."""
    # Get current page from query params or session state
    query_params = st.experimental_get_query_params()
    current_page = query_params.get("page", [st.session_state.current_page])[0]
    
    # Update session state
    st.session_state.current_page = current_page
    
    # Render navigation (except for login page)
    if current_page != "Login" or not st.session_state.authenticated:
        render_navbar()
    
    # Render the current page
    await render_page(current_page)
    
    # Add custom CSS
    st.markdown("""
        <style>
            /* Main content padding */
            .main .block-container {
                padding-top: 2rem;
                padding-bottom: 2rem;
            }
            
            /* Button styling */
            .stButton > button {
                border-radius: 0.5rem;
                padding: 0.5rem 1rem;
                font-weight: 500;
                transition: all 0.2s ease;
            }
            
            /* Card styling */
            .card {
                background: white;
                border-radius: 0.5rem;
                box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
                padding: 1.5rem;
                margin-bottom: 1.5rem;
            }
            
            /* Form styling */
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
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    asyncio.run(main())
