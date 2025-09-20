import requests
from typing import Optional, Dict, Any
import streamlit as st
from datetime import datetime, timedelta
import os

class APIClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.timeout = 10

    def _get_headers(self, headers: Optional[Dict] = None) -> Dict:
        """Get headers with authentication token if available."""
        default_headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        # Add auth token if available
        if hasattr(st.session_state, 'state') and hasattr(st.session_state.state, 'token'):
            default_headers["Authorization"] = f"Bearer {st.session_state.state.token}"
            
        if headers:
            default_headers.update(headers)
            
        return default_headers

    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """Handle API response and return JSON data."""
        try:
            response.raise_for_status()
            return response.json()
        except requests.exceptions.JSONDecodeError:
            return {"detail": "Invalid JSON response"}
        except requests.exceptions.HTTPError as e:
            return {"detail": str(e)}

    def get(self, endpoint: str, params: Optional[Dict] = None, headers: Optional[Dict] = None) -> Dict[str, Any]:
        """Make a GET request to the API."""
        try:
            response = requests.get(
                f"{self.base_url}/{endpoint.lstrip('/')}",
                params=params,
                headers=self._get_headers(headers),
                timeout=self.timeout
            )
            return self._handle_response(response)
        except requests.exceptions.RequestException as e:
            return {"detail": f"Request failed: {str(e)}"}

    def post(self, endpoint: str, data: Dict = None, json: Dict = None, headers: Optional[Dict] = None) -> Dict[str, Any]:
        """Make a POST request to the API."""
        try:
            response = requests.post(
                f"{self.base_url}/{endpoint.lstrip('/')}",
                json=json,
                data=data,
                headers=self._get_headers(headers),
                timeout=self.timeout
            )
            return self._handle_response(response)
        except requests.exceptions.RequestException as e:
            return {"detail": f"Request failed: {str(e)}"}

    def put(self, endpoint: str, data: Dict = None, json: Dict = None, headers: Optional[Dict] = None) -> Dict[str, Any]:
        """Make a PUT request to the API."""
        try:
            response = requests.put(
                f"{self.base_url}/{endpoint.lstrip('/')}",
                json=json,
                data=data,
                headers=self._get_headers(headers),
                timeout=self.timeout
            )
            return self._handle_response(response)
        except requests.exceptions.RequestException as e:
            return {"detail": f"Request failed: {str(e)}"}

    def delete(self, endpoint: str, headers: Optional[Dict] = None) -> Dict[str, Any]:
        """Make a DELETE request to the API."""
        try:
            response = requests.delete(
                f"{self.base_url}/{endpoint.lstrip('/')}",
                headers=self._get_headers(headers),
                timeout=self.timeout
            )
            return self._handle_response(response)
        except requests.exceptions.RequestException as e:
            return {"detail": f"Request failed: {str(e)}"}

# Initialize API client with base URL from environment variables
api_client = APIClient(os.getenv("API_BASE_URL", "http://localhost:8000/api/v1"))
