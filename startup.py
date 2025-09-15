#!/usr/bin/env python3
"""
Startup script for Railway deployment
Handles database initialization and app startup
"""
import os
import time
import logging
from sqlalchemy import create_engine, text
from config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def wait_for_database(max_retries=30, delay=2):
    """Wait for database to be available"""
    logger.info("Waiting for database to be available...")
    
    for attempt in range(max_retries):
        try:
            engine = create_engine(settings.database_url)
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info("Database is available!")
            return True
        except Exception as e:
            logger.warning(f"Database not ready (attempt {attempt + 1}/{max_retries}): {e}")
            time.sleep(delay)
    
    logger.error("Database not available after maximum retries")
    return False

def initialize_database():
    """Initialize database tables"""
    try:
        from database import engine
        from models import Base
        
        logger.info("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully!")
        return True
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        return False

def main():
    """Main startup function"""
    logger.info("Starting Financial Platform...")
    
    # Wait for database
    if not wait_for_database():
        logger.error("Failed to connect to database. Exiting.")
        return 1
    
    # Initialize database
    if not initialize_database():
        logger.error("Failed to initialize database. Exiting.")
        return 1
    
    # Start the application
    logger.info("Starting FastAPI application...")
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8000)),
        log_level="info"
    )

if __name__ == "__main__":
    exit(main())
