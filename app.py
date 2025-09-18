"""
Main application file for Render deployment.
This is needed for Render's free tier to automatically detect and run your FastAPI app.
"""
import sys
from pathlib import Path

# Add the parent directory to Python path
sys.path.append(str(Path(__file__).parent))

# Now import your FastAPI app
from backend.app.main import app

# This allows running with `python app.py` for local development
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=10000, reload=True)
