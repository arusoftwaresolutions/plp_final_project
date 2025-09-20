import streamlit as st
import requests
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

# Import from config
from config import settings

# API configuration
API_BASE_URL = settings.API_BASE_URL
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

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
            # Prepare the login data
            login_data = {
                "username": email,
                "password": password,
                "grant_type": "password",
                "scope": "",
                "client_id": "",
                "client_secret": ""
            }
            
            # Make the login request
            response = requests.post(
                f"{API_BASE_URL}/auth/login/access-token",
                data=login_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                access_token = data.get("access_token")
                token_type = data.get("token_type", "bearer")
                
                if not access_token:
                    st.error("❌ No access token received from server")
                    return False
                
                # Store the token
                st.session_state.state.token = access_token
                st.session_state.state.is_authenticated = True
                
                # Get user info
                user_response = requests.get(
                    f"{API_BASE_URL}/users/me",
                    headers={"Authorization": f"{token_type} {access_token}"},
                    timeout=10
                )
                
                if user_response.status_code == 200:
                    user_data = user_response.json()
                    st.session_state.state.user = user_data
                    st.session_state.state.is_admin = user_data.get("is_superuser", False)
                
                st.success("✅ Login successful!")
                st.experimental_rerun()
                return True
                
            else:
                try:
                    error_data = response.json()
                    error_msg = error_data.get("detail", "Login failed. Please check your credentials.")
                    if "detail" in error_data and isinstance(error_data["detail"], str):
                        error_msg = error_data["detail"]
                    elif "detail" in error_data and isinstance(error_data["detail"], dict):
                        error_msg = ", ".join([f"{k}: {v[0]}" for k, v in error_data["detail"].items()])
                except ValueError:
                    error_msg = f"Login failed with status code: {response.status_code}"
                
                st.error(f"❌ {error_msg}")
                return False
                
    except requests.exceptions.Timeout:
        st.error("⏱️ Connection timeout. Please try again later.")
        return False
    except requests.exceptions.RequestException as e:
        st.error(f"🔌 Connection error: {str(e)}")
        st.info(f"ℹ️ Please check if the backend server is running at {API_BASE_URL}")
        return False

def register_user(email: str, username: str, password: str):
    """Register a new user with the backend."""
    try:
        with st.spinner("Creating your account..."):
            # Prepare registration data
            registration_data = {
                "email": email,
                "username": username,
                "password": password,
                "full_name": username,  # Using username as full_name if not provided
                "is_active": True,
                "is_superuser": False,
                "is_verified": False
            }
            
            # Make the registration request
            response = requests.post(
                f"{API_BASE_URL}/auth/register",
                json=registration_data,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            # Handle successful registration
            if response.status_code in (200, 201):
                st.success("✅ Registration successful! Please log in.")
                return True
            
            # Handle registration errors
            try:
                error_data = response.json()
                error_msg = "Registration failed. Please check your information and try again."
                
                # Handle different error response formats
                if "detail" in error_data:
                    if isinstance(error_data["detail"], str):
                        error_msg = error_data["detail"]
                    elif isinstance(error_data["detail"], dict):
                        errors = []
                        for field, messages in error_data["detail"].items():
                            if isinstance(messages, list):
                                errors.append(f"{field}: {', '.join(messages)}")
                            else:
                                errors.append(f"{field}: {messages}")
                        error_msg = "; ".join(errors)
                
                st.error(f"❌ {error_msg}")
                
            except ValueError:
                st.error(f"❌ Registration failed with status code: {response.status_code}")
                
            return False
            
    except requests.exceptions.Timeout:
        st.error("⏱️ Connection timeout. Please try again later.")
        return False
        
    except requests.exceptions.RequestException as e:
        st.error(f"🔌 Connection error: {str(e)}")
        st.info(f"ℹ️ Please check if the backend server is running at {API_BASE_URL}")
        return False

def get_auth_headers():
    """Get headers with authentication token."""
    token = st.session_state.state.token
    return {"Authorization": f"Bearer {token}"}
