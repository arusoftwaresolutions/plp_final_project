import streamlit as st
import requests
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000/api/v1")
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def show_login_page():
    """Display the login/registration form."""
    st.title("Welcome to Poverty Alleviation Platform")
    st.markdown("### Sign in to continue")
    
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login")
            
            if submit:
                if not email or not password:
                    st.error("Please fill in all fields")
                else:
                    login_user(email, password)
    
    with tab2:
        with st.form("register_form"):
            st.markdown("### Create a new account")
            email = st.text_input("Email", key="reg_email")
            username = st.text_input("Username", key="reg_username")
            password = st.text_input("Password", type="password", key="reg_password")
            confirm_password = st.text_input("Confirm Password", type="password", key="reg_confirm_password")
            submit = st.form_submit_button("Register")
            
            if submit:
                if not all([email, username, password, confirm_password]):
                    st.error("Please fill in all fields")
                elif password != confirm_password:
                    st.error("Passwords do not match")
                else:
                    register_user(email, username, password)

def login_user(email: str, password: str):
    """Authenticate user with the backend."""
    try:
        with st.spinner("Signing in..."):
            # FastAPI endpoint expects OAuth2PasswordRequestForm-style form data
            response = requests.post(
                f"{API_BASE_URL}/auth/login/access-token",
                data={
                    "username": email,
                    "password": password,
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=10  # Add timeout to prevent hanging
            )
            
            if response.status_code == 200:
                data = response.json()
                # Store the token and user data in session state
                st.session_state.state.token = data.get("access_token")
                st.session_state.state.user = data.get("user", {})
                st.session_state.state.is_authenticated = True
                st.session_state.state.is_admin = data.get("user", {}).get("is_admin", False)
                st.success("✅ Login successful!")
                st.experimental_rerun()
            else:
                try:
                    error_data = response.json()
                    error_msg = error_data.get("detail", "Login failed. Please check your credentials.")
                except ValueError:
                    error_msg = f"Login failed with status code: {response.status_code}"
                st.error(f"❌ {error_msg}")
    except requests.exceptions.Timeout:
        st.error("⏱️ Connection timeout. Please try again later.")
    except requests.exceptions.RequestException as e:
        st.error(f"🔌 Connection error: {str(e)}")
        st.info("ℹ️ Please check if the backend server is running and accessible.")

def register_user(email: str, username: str, password: str):
    """Register a new user with the backend."""
    try:
        with st.spinner("Creating your account..."):
            response = requests.post(
                f"{API_BASE_URL}/auth/register",
                json={
                    "email": email,
                    "username": username,
                    "password": password,
                    "is_active": True,
                    "is_superuser": False,
                    "is_verified": False
                },
                timeout=10
            )
            
            if response.status_code == 200 or response.status_code == 201:
                st.success("✅ Registration successful! Please log in.")
                return True
            else:
                try:
                    error_data = response.json()
                    error_msg = error_data.get("detail", "Registration failed. Please try again.")
                    if "email" in error_data.get("detail", {}):
                        error_msg = f"Email error: {error_data['detail']['email'][0]}"
                    elif "username" in error_data.get("detail", {}):
                        error_msg = f"Username error: {error_data['detail']['username'][0]}"
                except ValueError:
                    error_msg = f"Registration failed with status code: {response.status_code}"
                st.error(f"❌ {error_msg}")
                return False
                
    except requests.exceptions.Timeout:
        st.error("⏱️ Connection timeout. Please try again later.")
        return False
    except requests.exceptions.RequestException as e:
        st.error(f"🔌 Connection error: {str(e)}")
        st.info("ℹ️ Please check if the backend server is running and accessible.")
        return False

def get_auth_headers():
    """Get headers with authentication token."""
    token = st.session_state.state.token
    return {"Authorization": f"Bearer {token}"}
