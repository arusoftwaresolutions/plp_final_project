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
    import time
    
    start_time = time.time()
    
    # Always return 200 OK for basic health check
    # Database connection will be checked but won't fail the health check
    response = {
        "status": "healthy",
        "timestamp": start_time,
        "details": {
            "mode": "development" if settings.DEBUG else "production",
            "database": {}
        }
    }
    
    # Try database connection but don't fail the health check if it fails
    try:
        async with engine.connect() as conn:
            start_db = time.time()
            await conn.execute("SELECT 1")
            db_time = time.time() - start_db
            
            response["details"]["database"] = {
                "status": "connected",
                "response_time_ms": f"{db_time*1000:.2f}",
                "url": str(settings.DATABASE).split('@')[-1] if settings.DATABASE else "Not configured"
            }
    except Exception as e:
        response["details"]["database"] = {
            "status": "disconnected",
            "error": str(e),
            "error_type": type(e).__name__,
            "url": str(settings.DATABASE).split('@')[-1] if settings.DATABASE else "Not configured"
        }
    
    response["response_time_ms"] = f"{(time.time() - start_time)*1000:.2f}"
    return response

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
