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
        # FastAPI endpoint expects OAuth2PasswordRequestForm-style form data
        response = requests.post(
            f"{API_BASE_URL}/auth/login/access-token",
            data={
                "username": email,
                "password": password,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            
            if token:
                # Fetch current user profile from backend instead of decoding JWT on frontend
                me_resp = requests.get(
                    f"{API_BASE_URL}/users/me",
                    headers={"Authorization": f"Bearer {token}"}
                )
                if me_resp.status_code == 200:
                    user = me_resp.json()
                    # Update session state
                    st.session_state.state.token = token
                    st.session_state.state.user = user
                    st.session_state.state.is_authenticated = True
                    st.session_state.state.is_admin = bool(user.get("is_superuser") or user.get("is_admin"))
                    st.experimental_rerun()
                else:
                    st.error("Login succeeded but failed to load user profile.")
            else:
                st.error("Invalid response from server")
        else:
            error_msg = response.json().get("detail", "Login failed")
            st.error(f"Login failed: {error_msg}")
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

def register_user(email: str, username: str, password: str):
    """Register a new user with the backend."""
    try:
        response = requests.post(
            f"{API_BASE_URL}/auth/register",
            json={
                "email": email,
                "username": username,
                "password": password
            }
        )
        
        if response.status_code == 200:
            st.success("Registration successful! Please log in.")
        else:
            error_msg = response.json().get("detail", "Registration failed")
            st.error(f"Registration failed: {error_msg}")
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

def get_auth_headers():
    """Get headers with authentication token."""
    token = st.session_state.state.token
    return {"Authorization": f"Bearer {token}"}
