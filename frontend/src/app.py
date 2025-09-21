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

# Import components
try:
    from streamlit.components.v1 import html
except ImportError:
    from streamlit import components as st_components
    html = st_components.v1.html

# Add security headers and Web3 provider protection
st.markdown('''
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="description" content="SDG Finance Platform">
    <meta http-equiv="Content-Security-Policy" content="default-src 'self' https: 'unsafe-inline' 'unsafe-eval'; script-src 'self' https: 'unsafe-inline' 'unsafe-eval'; style-src 'self' https: 'unsafe-inline'; img-src 'self' https: data:; font-src 'self' https: data:;">
''', unsafe_allow_html=True)

# Show immediate content
st.markdown("""
    <div id="app-container" style="min-height: 100vh; background-color: #f8f9fa; display: block;">
        <div id="main-content" style="padding: 2rem; text-align: center; background-color: #ffffff; margin: 2rem auto; max-width: 800px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
            <h1 style="color: #2c3e50; margin-bottom: 1rem; font-size: 2.5rem;">SDG Finance Platform</h1>
            <p style="color: #666; font-size: 1.2rem;">Loading application...</p>
            <div id="loading-spinner" style="margin: 2rem 0;">
                <div style="border: 4px solid #f3f3f3; border-top: 4px solid #3498db; border-radius: 50%; width: 40px; height: 40px; animation: spin 2s linear infinite; margin: 0 auto;"></div>
            </div>
            <style>
                @keyframes spin {
                    0% { transform: rotate(0deg); }
                    100% { transform: rotate(360deg); }
                }
            </style>
        </div>
    </div>
""", unsafe_allow_html=True)

# Add Web3 provider protection JavaScript
web3_js = """
<script>
// Web3 provider protection
document.addEventListener('DOMContentLoaded', function() {
    (function() {
        try {
            const originalEthereum = window.ethereum;
            const ethereumProxy = new Proxy({}, {
                get: function(target, prop) {
                    if (originalEthereum && prop in originalEthereum) {
                        const value = originalEthereum[prop];
                        return typeof value === 'function' ? value.bind(originalEthereum) : value;
                    }
                    return undefined;
                },
                set: function(target, prop, value) {
                    if (originalEthereum) {
                        originalEthereum[prop] = value;
                    }
                    return true;
                }
            });

            Object.defineProperty(window, 'ethereum', {
                get: function() { return ethereumProxy; },
                set: function(value) { return false; },
                configurable: false,
                enumerable: true
            });

            console.log('Web3 provider protection initialized');
        } catch (e) {
            console.error('Web3 provider error:', e);
        }
    })();
});
</script>
"""

# Use components.html to inject the JavaScript
html(web3_js, height=0, width=0)

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
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
    # Check authentication
    if not st.session_state.get('authenticated', False):
        # Render login page using PAGES dictionary
        if 'Login' in PAGES:
            try:
                login_module = PAGES['Login']['module']
                if hasattr(login_module, 'show'):
                    if asyncio.iscoroutinefunction(login_module.show):
                        await login_module.show()
                    else:
                        login_module.show()
                else:
                    st.error("Auth module has no 'show' method")
            except Exception as e:
                st.error(f"Error in auth module: {str(e)}")
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
    try:
        # This is the main entry point for Streamlit
        asyncio.run(main())
    except Exception as e:
        # Display any unhandled exceptions
        st.error(f"An error occurred: {str(e)}")
        st.exception(e)  # This will show the full traceback in the app

def run_streamlit():
    """Run the Streamlit app with default settings."""
    import subprocess
    import sys
    file_path = str(Path(__file__).resolve())
    cmd = [sys.executable, "-m", "streamlit", "run", file_path]
    subprocess.run(cmd)

if __name__ == "__main__":
    try:
        import streamlit as st
        if hasattr(st, '_is_running_with_streamlit'):
            # If running in Streamlit, just run the main function
            import asyncio
            asyncio.run(main())
        else:
            # If not in Streamlit, show instructions and try to run directly
            print("\n" + "="*60)
            print("SDG Finance Platform - Streamlit Application")
            print("="*60)
            print("\nTo run this application, please use one of the following commands:")
            print("\nFor development:")
            print(f"    {sys.executable} -m streamlit run {Path(__file__).name}")
            print("\nFor production with specific settings:")
            print(f"    {sys.executable} -m streamlit run --server.port=8501 --server.address=0.0.0.0 {Path(__file__).name}")
            print("\n" + "="*60 + "\n")
            
            # Try to run with default settings
            try:
                run_streamlit()
            except Exception as e:
                print(f"Failed to start Streamlit: {str(e)}")
                print("\nPlease make sure Streamlit is installed and try running the command manually.")
    except ImportError:
        print("Error: Streamlit is not installed. Please install it with:")
        print(f"    {sys.executable} -m pip install streamlit")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        # Try to run with default settings as a fallback
        try:
            run_streamlit()
        except Exception as e:
            print(f"Failed to start Streamlit: {str(e)}")
