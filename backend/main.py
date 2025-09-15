from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
import uvicorn

from database import get_db, engine
from models import Base
from routers import auth, families, donors, businesses, admin, ai, geospatial
from config import settings
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create database tables (with error handling)
try:
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")
except Exception as e:
    logger.error(f"Error creating database tables: {e}")
    # Don't crash the app if database is not available yet

app = FastAPI(
    title="Financial Platform API",
    description="A comprehensive financial platform for families, donors, and businesses",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(families.router, prefix="/api/families", tags=["Families"])
app.include_router(donors.router, prefix="/api/donors", tags=["Donors"])
app.include_router(businesses.router, prefix="/api/businesses", tags=["Businesses"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])
app.include_router(ai.router, prefix="/api/ai", tags=["AI Assistant"])
app.include_router(geospatial.router, prefix="/api/geospatial", tags=["Geospatial"])

@app.get("/")
async def root():
    return {"message": "Financial Platform API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    """Health check endpoint that doesn't require database"""
    return {"status": "healthy", "message": "Financial Platform API is running"}

@app.get("/health/db")
async def health_check_db():
    """Database health check"""
    try:
        from database import get_db
        db = next(get_db())
        db.execute("SELECT 1")
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "database": "disconnected", "error": str(e)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

