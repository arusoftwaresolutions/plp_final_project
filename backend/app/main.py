import os
from contextlib import asynccontextmanager
from typing import List, Optional

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

# Load environment variables first
load_dotenv()

# Then import local modules
try:
    from app.core.config import settings
    from app.api.api_v1.api import api_router
    from app.db.session import engine, Base
    from app.core.security import get_current_user
except ImportError as e:
    import sys
    print(f"Import error: {e}")
    print(f"Python path: {sys.path}")
    raise

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Insert initial data if needed
    # await init_db()
    
    yield
    
    # Clean up resources
    await engine.dispose()

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Poverty Alleviation Platform API",
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# Set up CORS
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)

# Health check endpoint with database connectivity check
@app.get("/health")
async def health_check():
    from app.core.config import settings
    
    # In development, we'll be more lenient with the health check
    if settings.DEBUG:
        return {
            "status": "healthy",
            "database": "development_mode",
            "details": {
                "mode": "development",
                "database_url": str(settings.DATABASE).split('@')[-1] if settings.DATABASE else "Not configured"
            }
        }
    
    # Production health check with database connection test
    db_status = "disconnected"
    error_info = None
    
    try:
        # Test database connection
        async with engine.connect() as conn:
            await conn.execute("SELECT 1")
            db_status = "connected"
    except Exception as e:
        error_info = {
            "type": str(type(e).__name__),
            "message": str(e),
            "database_url": str(settings.DATABASE).split('@')[-1] if settings.DATABASE else "Not configured"
        }
    
    if db_status == "connected":
        return {
            "status": "healthy",
            "database": "connected",
            "details": {
                "database_url": str(settings.DATABASE).split('@')[-1] if settings.DATABASE else "Not configured"
            }
        }
    else:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": error_info
        }

# Root endpoint with API information
@app.get("/")
async def root():
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": "production" if not settings.DEBUG else "development",
        "docs": "/docs",
        "redoc": "/redoc",
        "api_v1": "/api/v1"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8000")),
        reload=True,
        reload_dirs=["app"],
        log_level="info"
    )
