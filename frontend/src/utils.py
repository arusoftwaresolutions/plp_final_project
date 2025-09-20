"""Utility functions for the Financial Inclusion App frontend."""

import os
import json
from datetime import datetime
from typing import Any, Dict, Optional, Union, List

import requests
import streamlit as st
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API configuration
API_BASE_URL = os.getenv("API_BASE_URL", "https://plp-final-project-bgex.onrender.com").rstrip('/')
API_PREFIX = os.getenv("API_PREFIX", "/api/v1").strip('/')
FULL_API_URL = f"{API_BASE_URL}/{API_PREFIX}"

def get_auth_headers() -> Dict[str, str]:
    """Get the authentication headers with the JWT token.
    
    Returns:
        dict: Headers with Authorization token if user is authenticated.
    """
    headers = {"Content-Type": "application/json"}
    if 'current_user' in st.session_state and st.session_state.current_user:
        headers["Authorization"] = f"Bearer {st.session_state.current_user.get('access_token', '')}"
    return headers

async def api_request(
    method: str, 
    endpoint: str, 
    data: Optional[Dict[str, Any]] = None, 
    params: Optional[Dict[str, Any]] = None,
    form_data: bool = False,
    retry_on_auth_failure: bool = True
) -> Optional[Union[Dict[str, Any], List[Any]]]:
    """Make an API request with proper error handling and token refresh.
    
    Args:
        method: HTTP method (GET, POST, PUT, DELETE)
        endpoint: API endpoint (without base URL)
        data: Request body (for POST/PUT)
        params: Query parameters
        form_data: Whether to send as form data
        retry_on_auth_failure: Whether to retry on 401 with token refresh
        
    Returns:
        Response data as dict/list or None if request failed
    """
    # Construct URL using base URL and endpoint
    endpoint = endpoint.lstrip('/')
    if endpoint.startswith(API_PREFIX):
        url = f"{API_BASE_URL}/{endpoint}"
    else:
        url = f"{FULL_API_URL}/{endpoint}" if endpoint else FULL_API_URL
    headers = get_auth_headers()
    
    if form_data:
        headers.pop("Content-Type", None)  # Let requests set the correct content-type for form data
    
    try:
        kwargs = {
            "headers": headers,
            "params": params or {},
            "timeout": 30  # 30 seconds timeout
        }
        
        if data is not None:
            if form_data:
                kwargs["data"] = data
            else:
                kwargs["json"] = data
        
        method = method.upper()
        if method == "GET":
            response = requests.get(url, **kwargs)
        elif method == "POST":
            response = requests.post(url, **kwargs)
        elif method == "PUT":
            response = requests.put(url, **kwargs)
        elif method == "DELETE":
            response = requests.delete(url, **kwargs)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
        
        # Handle 401 Unauthorized with token refresh
        if response.status_code == 401 and retry_on_auth_failure and 'current_user' in st.session_state:
            # Try to refresh the token
            refresh_token = st.session_state.current_user.get('refresh_token')
            if refresh_token:
                refresh_response = await refresh_access_token(refresh_token)
                if refresh_response:
                    # Update the session with new tokens
                    st.session_state.current_user.update({
                        'access_token': refresh_response['access_token'],
                        'token_type': refresh_response.get('token_type', 'bearer')
                    })
                    # Retry the original request with new token
                    return await api_request(
                        method, endpoint, data, params, form_data, retry_on_auth_failure=False
                    )
        
        response.raise_for_status()
        
        # Return None for 204 No Content
        if response.status_code == 204:
            return None
            
        # Handle empty responses
        if not response.text.strip():
            return None
            
        return response.json()
        
    except requests.exceptions.RequestException as e:
        error_msg = str(e)
        try:
            if hasattr(e, 'response') and e.response is not None:
                error_detail = e.response.json().get("detail", {})
                if isinstance(error_detail, dict):
                    error_msg = ", ".join([f"{k}: {v}" for k, v in error_detail.items()]) or str(e)
                else:
                    error_msg = str(error_detail) or str(e)
                
                # Handle 401 Unauthorized
                if e.response.status_code == 401:
                    st.error("Your session has expired. Please log in again.")
                    st.session_state.authenticated = False
                    st.session_state.current_user = None
                    st.experimental_rerun()
                    
        except Exception as parse_error:
            st.error(f"Error parsing error response: {str(parse_error)}")
            
        st.error(f"API Error: {error_msg}")
        return None

async def refresh_access_token(refresh_token: str) -> Optional[Dict[str, Any]]:
    """Refresh the access token using the refresh token.
    
    Args:
        refresh_token: The refresh token
        
    Returns:
        New token data or None if refresh failed
    """
    try:
        token_data = {
            "refresh_token": refresh_token,
            "grant_type": "refresh_token"
        }
        
        response = requests.post(
            f"{FULL_API_URL}/auth/refresh-token",
            data=token_data,
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Failed to refresh token: {str(e)}")
        return None


def format_currency(amount: float) -> str:
    """Format a number as currency.
    
    Args:
        amount: The amount to format.
        
    Returns:
        Formatted currency string.
    """
    if amount is None:
        return "$0.00"
    try:
        return f"${float(amount):,.2f}"
    except (ValueError, TypeError):
        return "$0.00"

def format_date(date_str: str, format_str: str = "%b %d, %Y") -> str:
    """Format a date string for display.
    
    Args:
        date_str: Date string in ISO format or datetime object.
        format_str: Format string for output.
        
    Returns:
        Formatted date string.
    """
    if not date_str:
        return "-"
        
    try:
        if hasattr(date_str, 'strftime'):  # If it's a datetime object
            return date_str.strftime(format_str)
            
        if isinstance(date_str, str):
            # Try parsing ISO format first
            try:
                if 'T' in date_str:  # ISO format with time
                    dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                else:  # Just date
                    dt = datetime.strptime(date_str, "%Y-%m-%d")
                return dt.strftime(format_str)
            except ValueError:
                # Fallback to parsing with dateutil if ISO format fails
                try:
                    from dateutil import parser
                    dt = parser.parse(date_str)
                    return dt.strftime(format_str)
                except:
                    return str(date_str)
        return str(date_str)
    except Exception as e:
        return str(date_str)

def handle_api_error(response: requests.Response) -> str:
    """Extract error message from API response."""
    try:
        error_data = response.json()
        if isinstance(error_data, dict):
            return error_data.get("detail", str(error_data))
        return str(error_data)
    except:
        return f"Error {response.status_code}: {response.text}"
