import streamlit as st
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from utils import (
    API_BASE_URL,
    FULL_API_URL,  # Add this line
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
                    # Store the login attempt in session state and trigger a rerun
                    st.session_state.login_attempt = {"email": email, "password": password}
                    st.rerun()
    
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
            # Create form data with the correct format for OAuth2
            form_data = {
                "username": email,  # Backend expects 'username' but we'll send the email here
                "password": password,
                "grant_type": "password"
            }
            
            st.write("Sending login request...")  # Debugging
            st.write("Form data:", form_data)  # Debugging
            
            # Make the login request with form data
            try:
                # Make the request directly with requests to have more control
                import requests
                from urllib.parse import urlencode
                
                # Prepare the request
                url = f"{FULL_API_URL}/auth/login/access-token"
                headers = {
                    "Content-Type": "application/x-www-form-urlencoded",
                    "accept": "application/json"
                }
                
                st.write(f"Sending POST to: {url}")  # Debugging
                st.write(f"Headers: {headers}")  # Debugging
                
                # Make the request
                response = requests.post(
                    url,
                    data=urlencode(form_data),
                    headers=headers,
                    timeout=30
                )
                
                st.write(f"Response status: {response.status_code}")  # Debugging
                st.write(f"Response headers: {response.headers}")  # Debugging
                
                # Parse the response
                try:
                    token_response = response.json()
                    st.write("Response JSON:", token_response)  # Debugging
                except ValueError:
                    st.write(f"Non-JSON response: {response.text}")  # Debugging
                    token_response = None
                
                st.write("Login response:", token_response)  # Debugging line
                
                if not token_response or 'access_token' not in token_response:
                    st.error("❌ Invalid email or password")
                    if token_response and 'detail' in token_response:
                        st.error(f"Error: {token_response['detail']}")
                    return
                    
            except Exception as e:
                st.error(f"❌ Login failed: {str(e)}")
                st.exception(e)  # Print full traceback for debugging
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
    # Check for pending login attempt
    if "login_attempt" in st.session_state:
        login_attempt = st.session_state.pop("login_attempt", None)
        if login_attempt:
            await login_user(login_attempt["email"], login_attempt["password"])
    
    # Show the login page
    show_login_page()
