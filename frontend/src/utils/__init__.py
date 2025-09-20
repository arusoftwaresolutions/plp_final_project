"""
Utility functions and helpers for the Poverty Alleviation Platform.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union
import json
import logging
import os
import re

# Import API client
from .api_client import APIClient, api_client
import uuid

from dateutil import parser

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def format_currency(amount: float, currency: str = 'USD') -> str:
    """Format a number as currency.
    
    Args:
        amount: The amount to format
        currency: The currency code (default: 'USD')
        
    Returns:
        Formatted currency string
    """
    try:
        # Basic currency formatting
        if currency.upper() == 'USD':
            return f"${amount:,.2f}"
        elif currency.upper() == 'EUR':
            return f"€{amount:,.2f}"
        elif currency.upper() == 'GBP':
            return f"£{amount:,.2f}"
        else:
            return f"{amount:,.2f} {currency.upper()}"
    except (ValueError, TypeError):
        return str(amount)

def format_date(date_str: str, format_str: str = "%B %d, %Y") -> str:
    """Format a date string.
    
    Args:
        date_str: The date string to format
        format_str: The format string (default: "%B %d, %Y")
        
    Returns:
        Formatted date string
    """
    try:
        if not date_str:
            return ""
        date_obj = parser.parse(date_str)
        return date_obj.strftime(format_str)
    except (ValueError, TypeError):
        return str(date_str)

def format_relative_time(date_str: str) -> str:
    """Format a date as a relative time string (e.g., "2 days ago").
    
    Args:
        date_str: The date string to format
        
    Returns:
        Relative time string
    """
    try:
        if not date_str:
            return ""
            
        date_obj = parser.parse(date_str)
        now = datetime.now(timezone.utc)
        
        if date_obj.tzinfo is None:
            date_obj = date_obj.replace(tzinfo=timezone.utc)
        
        diff = now - date_obj
        
        if diff.days > 365:
            years = diff.days // 365
            return f"{years} year{'s' if years > 1 else ''} ago"
        elif diff.days > 30:
            months = diff.days // 30
            return f"{months} month{'s' if months > 1 else ''} ago"
        elif diff.days > 0:
            return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours} hour{'s' if hours > 1 else ''} ago"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
        else:
            return "just now"
    except (ValueError, TypeError):
        return str(date_str)

def validate_email(email: str) -> bool:
    """Validate an email address.
    
    Args:
        email: The email address to validate
        
    Returns:
        bool: True if the email is valid, False otherwise
    """
    if not email:
        return False
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_phone(phone: str) -> bool:
    """Validate a phone number.
    
    Args:
        phone: The phone number to validate
        
    Returns:
        bool: True if the phone number is valid, False otherwise
    """
    if not phone:
        return False
    
    # Remove all non-digit characters
    digits = re.sub(r'\D', '', phone)
    
    # Check if it's a valid phone number (between 8-15 digits)
    return 8 <= len(digits) <= 15

def generate_id(prefix: str = "") -> str:
    """Generate a unique ID with an optional prefix.
    
    Args:
        prefix: Optional prefix for the ID
        
    Returns:
        A unique ID string
    """
    unique_id = str(uuid.uuid4())[:8]
    return f"{prefix}_{unique_id}" if prefix else unique_id

def sanitize_input(input_str: str) -> str:
    """Sanitize user input to prevent XSS attacks.
    
    Args:
        input_str: The input string to sanitize
        
    Returns:
        Sanitized string
    """
    if not input_str:
        return ""
    
    # Replace potentially dangerous characters
    sanitized = input_str.replace("<", "&lt;")
    sanitized = sanitized.replace(">", "&gt;")
    sanitized = sanitized.replace('"', "&quot;")
    sanitized = sanitized.replace("'", "&#x27;")
    
    return sanitized

def parse_json(json_str: str) -> Union[Dict, List, None]:
    """Safely parse a JSON string.
    
    Args:
        json_str: The JSON string to parse
        
    Returns:
        Parsed JSON object or None if invalid
    """
    try:
        return json.loads(json_str)
    except (json.JSONDecodeError, TypeError):
        return None

def get_env_variable(name: str, default: Any = None) -> str:
    """Get an environment variable or return a default value.
    
    Args:
        name: The name of the environment variable
        default: The default value to return if the variable is not set
        
    Returns:
        The value of the environment variable or the default value
    """
    return os.environ.get(name, default)

def log_error(error: Exception, context: str = "") -> None:
    """Log an error with context.
    
    Args:
        error: The exception that was raised
        context: Additional context about where the error occurred
    """
    error_msg = f"Error: {str(error)}"
    if context:
        error_msg = f"{context} - {error_msg}"
    logger.error(error_msg, exc_info=True)

def format_error_message(error: Exception) -> str:
    """Format an error message for display to the user.
    
    Args:
        error: The exception that was raised
        
    Returns:
        A user-friendly error message
    """
    error_msg = str(error)
    
    # Customize common error messages
    if "connection" in error_msg.lower():
        return "Unable to connect to the server. Please check your internet connection and try again."
    elif "timeout" in error_msg.lower():
        return "The request timed out. Please try again in a moment."
    elif "404" in error_msg:
        return "The requested resource was not found."
    elif "403" in error_msg:
        return "You don't have permission to access this resource."
    elif "401" in error_msg:
        return "Please log in to access this resource."
    
    # Default error message
    return f"An error occurred: {error_msg}"
