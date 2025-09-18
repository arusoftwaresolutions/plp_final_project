"""
Main application file for Render deployment.
This is a thin wrapper that imports the FastAPI app from backend.app.main.
"""
import os
import sys
from pathlib import Path

# Add the project root to Python path
sys.path.append(str(Path(__file__).parent))

# Import the FastAPI app from the backend module
from backend.app.main import app

# This allows running with `python app.py` for local development
if __name__ == "__main__":
    import uvicorn
    
    # Get the port from environment variable with fallback
    port = int(os.getenv("PORT", 8000))
    
    # Get environment from environment variable with fallback
    env = os.getenv("ENVIRONMENT", "production").lower()
    
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=port,
        reload=env != "production"
    )
