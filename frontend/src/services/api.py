import os
import requests
from typing import Dict, List, Optional, Any
from datetime import datetime
import streamlit as st
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000/api/v1")

class APIError(Exception):
    """Custom exception for API errors."""
    def __init__(self, message: str, status_code: int = None):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

def get_auth_headers() -> Dict[str, str]:
    """Get authentication headers with JWT token."""
    if 'state' not in st.session_state or not st.session_state.state.is_authenticated:
        return {}
    return {"Authorization": f"Bearer {st.session_state.state.token}"}

def handle_response(response: requests.Response) -> Any:
    """Handle API response and raise appropriate exceptions."""
    if response.status_code == 401:
        st.session_state.state = type('', (), {'is_authenticated': False})()
        st.error("Session expired. Please log in again.")
        st.experimental_rerun()
        return None
    
    try:
        data = response.json()
    except ValueError:
        data = {}
    
    if not response.ok:
        error_msg = data.get('detail', response.text or 'An error occurred')
        raise APIError(error_msg, response.status_code)
    
    return data

def get_user_profile() -> Dict[str, Any]:
    """Get current user's profile data."""
    try:
        response = requests.get(
            f"{API_BASE_URL}/users/me",
            headers=get_auth_headers()
        )
        return handle_response(response)
    except Exception as e:
        raise APIError(f"Failed to fetch user profile: {str(e)}")

def get_recent_transactions(limit: int = 10) -> List[Dict]:
    """Get recent transactions for the current user."""
    try:
        response = requests.get(
            f"{API_BASE_URL}/transactions/recent?limit={limit}",
            headers=get_auth_headers()
        )
        return handle_response(response) or []
    except Exception as e:
        raise APIError(f"Failed to fetch transactions: {str(e)}")

def get_loan_status() -> Dict[str, Any]:
    """Get loan status for the current user."""
    try:
        response = requests.get(
            f"{API_BASE_URL}/loans/status",
            headers=get_auth_headers()
        )
        return handle_response(response) or {}
    except Exception as e:
        if "No active loans" in str(e):
            return {}
        raise APIError(f"Failed to fetch loan status: {str(e)}")

def get_budget_recommendations() -> Dict[str, Any]:
    """Get budget recommendations for the current user."""
    try:
        response = requests.get(
            f"{API_BASE_URL}/ai/budget-recommendations",
            headers=get_auth_headers()
        )
        return handle_response(response) or {}
    except Exception as e:
        raise APIError(f"Failed to fetch budget recommendations: {str(e)}")

def get_ai_insights() -> Dict[str, Any]:
    """Get AI-generated financial insights for the current user."""
    try:
        response = requests.get(
            f"{API_BASE_URL}/ai/insights",
            headers=get_auth_headers()
        )
        return handle_response(response) or {}
    except Exception as e:
        raise APIError(f"Failed to fetch AI insights: {str(e)}")

def apply_for_loan(amount: float, term_months: int, purpose: str) -> Dict[str, Any]:
    """Apply for a new loan."""
    try:
        response = requests.post(
            f"{API_BASE_URL}/loans/apply",
            json={
                "amount": amount,
                "term_months": term_months,
                "purpose": purpose
            },
            headers=get_auth_headers()
        )
        return handle_response(response)
    except Exception as e:
        raise APIError(f"Failed to apply for loan: {str(e)}")

def create_campaign(title: str, description: str, target_amount: float, 
                  end_date: str, category: str) -> Dict[str, Any]:
    """Create a new crowdfunding campaign."""
    try:
        response = requests.post(
            f"{API_BASE_URL}/campaigns",
            json={
                "title": title,
                "description": description,
                "target_amount": target_amount,
                "end_date": end_date,
                "category": category
            },
            headers=get_auth_headers()
        )
        return handle_response(response)
    except Exception as e:
        raise APIError(f"Failed to create campaign: {str(e)}")

def get_poverty_insights(area_id: Optional[int] = None) -> List[Dict]:
    """Get poverty insights for specific area or globally."""
    try:
        url = f"{API_BASE_URL}/insights/poverty"
        if area_id:
            url += f"?area_id={area_id}"
        
        response = requests.get(
            url,
            headers=get_auth_headers()
        )
        return handle_response(response) or []
    except Exception as e:
        raise APIError(f"Failed to fetch poverty insights: {str(e)}")
