import streamlit as st
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from utils import (
    API_BASE_URL,
    api_request,
    format_date,
    handle_api_error
)

def show_login_page():
    """Display the login/registration form."""
    st.title("Welcome to Financial Inclusion App")
    st.markdown("### Sign in to your account")
    
    # Check if already logged in
    if st.session_state.get("authenticated", False):
        st.success("You are already logged in!")
        if st.button("Go to Dashboard"):
            st.session_state.current_page = "Dashboard"
            st.experimental_rerun()
        return
    
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        with st.form("login_form"):
            email = st.text_input("Email", key="login_email")
            password = st.text_input("Password", type="password", key="login_password")
            submit = st.form_submit_button("Login")
            
            if submit:
                if not email or not password:
                    st.error("Please fill in all fields")
                else:
                    import asyncio
                    asyncio.run(login_user(email, password))
    
    with tab2:
        with st.form("register_form"):
            st.markdown("### Create a new account")
            
            col1, col2 = st.columns(2)
            with col1:
                first_name = st.text_input("First Name", key="reg_first_name")
            with col2:
                last_name = st.text_input("Last Name", key="reg_last_name")
                
            email = st.text_input("Email", key="reg_email")
            username = st.text_input("Username", key="reg_username")
            
            col1, col2 = st.columns(2)
            with col1:
                password = st.text_input("Password", type="password", key="reg_password")
            with col2:
                confirm_password = st.text_input("Confirm Password", type="password", key="reg_confirm_password")
            
            submit = st.form_submit_button("Register")
            
            if submit:
                if not all([first_name, last_name, email, username, password, confirm_password]):
                    st.error("Please fill in all required fields")
                elif password != confirm_password:
                    st.error("Passwords do not match")
                elif len(password) < 8:
                    st.error("Password must be at least 8 characters long")
                else:
                    user_data = {
                        "email": email,
                        "username": username,
                        "first_name": first_name,
                        "last_name": last_name,
                        "password": password
                    }
                    register_user(user_data)

async def login_user(email: str, password: str):
    """Authenticate user with the backend."""
    try:
        with st.spinner("Signing in..."):
            # First, get the access token
            token_data = {
                "username": email,
                "password": password,
                "grant_type": "password"
            }
            
            # Make the login request
            token_response = await api_request(
                "POST",
                "/auth/login/access-token",
                data=token_data,
                form_data=True,
                retry_on_auth_failure=False  # Don't retry on auth failure for login
            )
            
            st.write("Login response:", token_response)  # Debugging line
            
            if not token_response or 'access_token' not in token_response:
                st.error("❌ Invalid email or password")
                return
                
            # Store the tokens and basic user info
            st.session_state.authenticated = True
            st.session_state.current_user = {
                "email": email,
                "access_token": token_response.get("access_token"),
                "token_type": token_response.get("token_type", "bearer")
            }
            
            # Fetch user details
            user_response = await api_request("GET", "/users/me")
            if user_response:
                st.session_state.current_user.update({
                    "id": user_response.get("id"),
                    "username": user_response.get("username"),
                    "first_name": user_response.get("first_name"),
                    "last_name": user_response.get("last_name"),
                    "is_admin": user_response.get("is_superuser", False)
                })
                st.session_state.is_admin = user_response.get("is_superuser", False)
            
            st.success("✅ Successfully logged in!")
            st.experimental_rerun()
                
    except Exception as e:
        st.error(f"🔌 Error: {str(e)}")
        st.info("ℹ️ Please check your connection and try again.")

async def register_user(user_data: Dict[str, Any]):
    """Register a new user with the backend.
    
    Args:
        user_data: Dictionary containing user registration data
    """
    try:
        with st.spinner("Creating your account..."):
            # Prepare the registration data
            registration_data = {
                "email": user_data["email"],
                "username": user_data["username"],
                "password": user_data["password"],
                "full_name": f"{user_data['first_name']} {user_data['last_name']}",
                "first_name": user_data["first_name"],
                "last_name": user_data["last_name"]
            }
            
            # Make the registration request
            response = await api_request(
                "POST",
                "/auth/register",
                data=registration_data
            )
            
            if response:
                st.success("✅ Account created successfully! Please log in.")
                # Clear the registration form
                for key in ["reg_first_name", "reg_last_name", "reg_email", 
                           "reg_username", "reg_password", "reg_confirm_password"]:
                    if key in st.session_state:
                        del st.session_state[key]
                st.experimental_rerun()
                
    except Exception as e:
        st.error(f"❌ Error creating account: {str(e)}")

def get_auth_headers() -> Dict[str, str]:
    """Get headers with authentication token.
    
    Returns:
        Dictionary containing the authorization headers
    """
    headers = {"Content-Type": "application/json"}
    if 'current_user' in st.session_state and st.session_state.current_user:
        headers["Authorization"] = f"Bearer {st.session_state.current_user.get('access_token', '')}"
    return headers

async def show():
    """Show the login page."""
    show_login_page()
