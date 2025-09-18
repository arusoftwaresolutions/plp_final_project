from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
import logging
import os
from typing import AsyncGenerator, Optional

from app.core.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_database_url() -> str:
    """Get the database URL, handling Railway's masking of sensitive information."""
    # Get the URL from settings
    db_url = settings.DATABASE
    
    # If the URL is masked (contains '*****'), try to construct it from individual components
    if '*****' in db_url:
        logger.warning("Detected masked database URL, trying to construct from environment variables")
        
        # Get individual components from environment variables
        db_host = os.getenv("PGHOST")
        db_port = os.getenv("PGPORT")
        db_user = os.getenv("PGUSER")
        db_password = os.getenv("PGPASSWORD")
        db_name = os.getenv("PGDATABASE")
        
        if all([db_host, db_port, db_user, db_password, db_name]):
            # Construct the URL from individual components
            db_url = f"postgresql+asyncpg://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
            
            # Add SSL if in production
            if settings.RAILWAY_ENVIRONMENT == "production":
                db_url += "?sslmode=require"
            
            logger.info("Successfully constructed database URL from environment variables")
            return db_url
        else:
            raise ValueError("Database URL is masked and required environment variables are missing")
    
    return db_url

def create_db_engine():
    """Create and return an async database engine with proper configuration."""
    try:
        db_url = get_database_url()
        
        # Redact password in logs
        if "@" in db_url:
            parts = db_url.split("@")
            redacted_url = f"{parts[0].split('://')[0]}://*****:*****@{'@'.join(parts[1:])}"
            logger.info(f"Connecting to database: {redacted_url}")
        else:
            logger.info(f"Connecting to database: {db_url}")

        engine = create_async_engine(
            db_url,
            echo=settings.DEBUG,
            pool_pre_ping=True,
            pool_recycle=300,
            pool_size=5,
            max_overflow=10,
            connect_args={"ssl": "require"} if settings.RAILWAY_ENVIRONMENT == "production" else {}
        )
        logger.info("Database engine created successfully")
        return engine
    except Exception as e:
        logger.error(f"Failed to create database engine: {str(e)}")
        logger.exception("Database engine creation failed with exception:")
        raise

# Create the database engine
engine = create_db_engine()

# Session factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Base class for models
Base = declarative_base()

# Dependency for DB session
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            raise e
        finally:
            await session.close()

# Import models to register them with SQLAlchemy
from .models import *  # noqa
