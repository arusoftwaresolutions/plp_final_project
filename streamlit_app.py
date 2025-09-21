"""
SDG Finance Platform - Streamlit Cloud Deployment
Main entry point for Streamlit Cloud deployment
"""

import os
import sys
from pathlib import Path

# Add the src directory to Python path
sys.path.append(str(Path(__file__).parent / "src"))

# Import and run the main app
from app import main

if __name__ == "__main__":
    main()
