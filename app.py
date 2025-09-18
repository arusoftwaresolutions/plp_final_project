"""
Main application file for Render deployment.
This is needed for Render's free tier to automatically detect and run your FastAPI app.
"""
import sys
from pathlib import Path

# Add the parent directory to Python path
sys.path.append(str(Path(__file__).parent))

def create_app():
    """Create and return the FastAPI application."""
    from backend.app.main import app
    return app

# Create the app instance
app = create_app()

# This allows running with `python app.py` for local development
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=10000, reload=True)
