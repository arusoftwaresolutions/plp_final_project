""
WSGI config for Poverty Alleviation Platform.
This file helps Render run your application.
"""

import os
from backend.app.main import app

# This allows Render to run your FastAPI application
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=port, log_level="info")
