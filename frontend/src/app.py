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
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': None
    }
)

# Add global CSS to fix layout and reduce CSP issues
st.markdown("""
<style>
/* Global styles to fix layout issues */
* {
    box-sizing: border-box;
}

.main .block-container {
    max-width: 100%;
    padding-top: 0;
    padding-bottom: 0;
}

/* Fix for responsive columns */
.st-emotion-cache-1kyxreq {
    gap: 1rem !important;
}

.st-emotion-cache-1kyxreq > div {
    min-width: 0;
}

/* Ensure proper iframe sandboxing */
iframe {
    sandbox="allow-same-origin allow-scripts allow-forms allow-downloads";
}

/* Hide Streamlit elements that cause CSP issues */
[data-testid="stHeader"] {
    display: none !important;
}

[data-testid="stToolbar"] {
    display: none !important;
}

[data-testid="stSidebarNav"] {
    display: none !important;
}

/* Fix for main menu */
#MainMenu {
    visibility: hidden !important;
}

/* Ensure footer is always visible */
.footer {
    margin-top: 2rem !important;
    padding: 1rem !important;
}

/* Responsive design improvements */
@media (max-width: 768px) {
    .st-emotion-cache-1kyxreq {
        flex-direction: column !important;
    }

    .st-emotion-cache-1kyxreq > div:first-child {
        width: 100% !important;
        margin-bottom: 1rem;
    }

    .st-emotion-cache-1kyxreq > div:last-child {
        width: 100% !important;
    }
}
</style>
""", unsafe_allow_html=True)

# Import components
try:
    from streamlit.components.v1 import html
except ImportError:
    from streamlit import components as st_components
    html = st_components.v1.html

# Add security headers and Web3 provider protection
st.markdown('''
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <meta name="description" content="SDG Finance Platform">
        <meta http-equiv="Content-Security-Policy" content="default-src 'self' https: 'unsafe-inline' 'unsafe-eval'; script-src 'self' https: 'unsafe-inline' 'unsafe-eval'; style-src 'self' https: 'unsafe-inline'; img-src 'self' https: data:; font-src 'self' https: data:; frame-ancestors 'self';">
        <meta name="referrer" content="strict-origin-when-cross-origin">
    </head>
''', unsafe_allow_html=True)

# Configuration - matches your backend API
API_BASE_URL = os.getenv("API_BASE_URL", "https://plp-final-project-bgex.onrender.com")
API_PREFIX = os.getenv("API_PREFIX", "/api/v1").strip('/')
FULL_API_URL = f"{API_BASE_URL.rstrip('/')}/{API_PREFIX}"

# Web3 provider protection JavaScript
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
    handlers=[logging.StreamHandler(sys.stdout)]
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
    st.session_state.current_user = None
    st.session_state.current_page = "Dashboard"

def render_sidebar():
    """Render the sidebar navigation."""
    st.markdown("""
    <div style="padding: 1rem; background-color: #f8f9fa; border-radius: 10px; margin-bottom: 1rem;">
        <h3 style="color: #2c3e50; margin-bottom: 1rem; text-align: center;">🌍 SDG Finance Platform</h3>
        <p style="color: #666; font-size: 0.9rem; text-align: center; margin-bottom: 1rem;">Empowering communities through financial inclusion</p>
    </div>
    """, unsafe_allow_html=True)

    # Navigation menu using option_menu
    selected = option_menu(
        menu_title=None,
        options=["Dashboard", "AI Recommendations", "Transactions", "Crowdfunding", "Microloans", "Poverty Map", "Profile"],
        icons=["speedometer2", "robot", "cash-stack", "people-fill", "piggy-bank", "geo-alt", "person-circle"],
        menu_icon="cast",
        default_index=0,
        orientation="vertical",
        styles={
            "container": {"padding": "0!important", "background-color": "#f8f9fa"},
            "icon": {"color": "#4b6cb7", "font-size": "18px"},
            "nav-link": {
                "font-size": "16px",
                "text-align": "left",
                "margin": "0px",
                "border-radius": "8px",
                "color": "#2c3e50",
                "--hover-color": "#e3f2fd"
            },
            "nav-link-selected": {"background-color": "#4b6cb7", "color": "white"}
        }
    )

    # Update current page
    if selected and selected != st.session_state.get('current_page', 'Dashboard'):
        st.session_state.current_page = selected
        st.rerun()

    # User info section
    if st.session_state.get('authenticated', False):
        st.markdown("---")
        st.markdown(f"""
        <div style="text-align: center; padding: 1rem; background-color: white; border-radius: 8px; margin-top: 1rem;">
            <p style="margin: 0; color: #2c3e50; font-weight: bold;">
                👤 {st.session_state.get('current_user', {}).get('username', 'User')}
            </p>
            <p style="margin: 0; color: #666; font-size: 0.8rem;">
                {'Admin' if st.session_state.get('is_admin', False) else 'User'}
            </p>
        </div>
        """, unsafe_allow_html=True)

        if st.button("🚪 Logout", key="sidebar_logout", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.is_admin = False
            st.session_state.current_user = None
            st.success("Logged out successfully!")
            st.rerun()

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
    # Check authentication FIRST - before rendering anything else
    if not st.session_state.get('authenticated', False):
        # Show clean login page without sidebar
        st.markdown("""
        <div style="min-height: 100vh; display: flex; align-items: center; justify-content: center; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
            <div style="background: white; padding: 3rem; border-radius: 20px; box-shadow: 0 20px 40px rgba(0,0,0,0.1); max-width: 500px; width: 90%;">
                <div style="text-align: center; margin-bottom: 2rem;">
                    <h1 style="color: #2c3e50; margin-bottom: 0.5rem; font-size: 2.5rem;">🌍 SDG Finance Platform</h1>
                    <p style="color: #666; font-size: 1.1rem; margin: 0;">Empowering communities through financial inclusion</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Render login page
        if 'auth' in PAGE_MODULES:
            try:
                if hasattr(PAGE_MODULES['auth'], 'show'):
                    if asyncio.iscoroutinefunction(PAGE_MODULES['auth'].show):
                        await PAGE_MODULES['auth'].show()
                    else:
                        PAGE_MODULES['auth'].show()
                else:
                    st.error("Auth module has no 'show' method")
            except Exception as e:
                st.error(f"Error in auth module: {str(e)}")
                # Show fallback login form
                st.markdown("---")
                st.subheader("🔑 Simple Login (Fallback)")

                with st.form("fallback_login_form"):
                    username = st.text_input("Username", placeholder="Enter your username")
                    password = st.text_input("Password", type="password", placeholder="Enter your password")

                    col1, col2 = st.columns(2)
                    with col1:
                        login_button = st.form_submit_button("Login", use_container_width=True)
                    with col2:
                        st.form_submit_button("Forgot Password?", use_container_width=True)

                if login_button:
                    if username and password:
                        if username == "admin" and password == "password":
                            st.session_state.authenticated = True
                            st.session_state.is_admin = True
                            st.session_state.current_user = {"username": username}
                            st.success("Login successful! Redirecting...")
                            st.rerun()
                        elif username == "user" and password == "password":
                            st.session_state.authenticated = True
                            st.session_state.is_admin = False
                            st.session_state.current_user = {"username": username}
                            st.success("Login successful! Redirecting...")
                            st.rerun()
                        else:
                            st.error("Invalid username or password")
                    else:
                        st.error("Please enter both username and password")

                st.markdown("---")
                st.markdown("**Demo Accounts:**")
                st.markdown("- Username: `admin`, Password: `password` (Admin access)")
                st.markdown("- Username: `user`, Password: `password` (User access)")
        else:
            st.error("Authentication module not found")
        return

    # User is authenticated - show main application with sidebar
    st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(135deg, #4b6cb7 0%, #182848 100%);
        color: white;
        padding: 1rem 2rem;
        border-radius: 0 0 20px 20px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    }
    .main-header h1 {
        margin: 0;
        font-size: 2rem;
        font-weight: 600;
    }
    .main-header p {
        margin: 0.5rem 0 0 0;
        opacity: 0.9;
        font-size: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)

    # Header
    st.markdown(f"""
    <div class="main-header">
        <h1>🌍 SDG Finance Platform Dashboard</h1>
        <p>Welcome back, {st.session_state.current_user.get('username', 'User')}!</p>
    </div>
    """, unsafe_allow_html=True)

    # Get current page
    current_page = st.session_state.get('current_page', 'Dashboard')

    # Create main layout
    col1, col2 = st.columns([1, 3])

    # Render the sidebar in the first column
    with col1:
        render_sidebar()

    # Render the main content in the second column
    with col2:
        # Add some spacing
        st.markdown("<div style='margin-bottom: 1rem;'></div>", unsafe_allow_html=True)

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
                # Show fallback content
                st.markdown(f"## 📊 {current_page}")
                st.write(f"Welcome to the {current_page.lower()} page!")
                st.info("This page is currently under development.")
        else:
            st.warning("Page not found. Redirecting to dashboard...")
            st.session_state.current_page = "Dashboard"
            st.rerun()

    # Add footer
    st.markdown("""
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
