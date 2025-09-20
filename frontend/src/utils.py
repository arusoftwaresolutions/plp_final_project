"""Utility functions for the Financial Inclusion App frontend."""

import os
import json
import aiohttp
from datetime import datetime
from typing import Any, Dict, Optional, Union, List, Tuple

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
    retry_on_auth_failure: bool = True,
    timeout: int = 30
) -> Optional[Union[Dict[str, Any], List[Any]]]:
    """Make an API request with proper error handling and token refresh.
    
    Args:
        method: HTTP method (GET, POST, PUT, DELETE)
        endpoint: API endpoint (without base URL)
        data: Request body (for POST/PUT)
        params: Query parameters
        form_data: Whether to send as form data
        retry_on_auth_failure: Whether to retry on 401 with token refresh
        timeout: Request timeout in seconds
        
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
    
    async with aiohttp.ClientSession() as session:
        try:
            # Prepare request data
            json_data = None
            form_data_obj = None
            
            if data is not None:
                if form_data:
                    form_data_obj = aiohttp.FormData()
                    for key, value in data.items():
                        form_data_obj.add_field(key, str(value))
                else:
                    json_data = data
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
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{FULL_API_URL}/auth/refresh-token",
                data=token_data,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    st.error(f"Failed to refresh token: {response.status} - {error_text}")
                    return None
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

async def handle_api_error(response: aiohttp.ClientResponse) -> str:
    """Extract error message from API response."""
    try:
        error_data = await response.json()
        if isinstance(error_data, dict):
            return error_data.get("detail", str(error_data))
        return str(error_data)
    except:
        error_text = await response.text()
        return f"Error {response.status}: {error_text}"
