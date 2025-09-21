"""
SDG Finance Platform - Streamlit Frontend
Main entry point for deployment
"""

import sys
import os

# Add the src directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Import the main app
from app import main

if __name__ == "__main__":
    main()
