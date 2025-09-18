"""
Main application file for Render deployment.
This is needed for Render's free tier to automatically detect and run your FastAPI app.
"""

# This imports your actual FastAPI app
from backend.app.main import app

# This allows running with `python app.py` for local development
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=10000, reload=True)
