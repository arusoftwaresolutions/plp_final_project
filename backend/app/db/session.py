from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
import os
import ssl
import logging
from typing import Optional, Dict, Any, AsyncGenerator
from urllib.parse import urlparse

from app.core.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create SSL context for secure connections
def get_ssl_context():
    """Create and return an SSL context based on the environment."""
    ssl_context = ssl.create_default_context()
    if settings.RAILWAY_ENVIRONMENT == "production":
        # In production, verify the server certificate
        ssl_context.check_hostname = True
        ssl_context.verify_mode = ssl.CERT_REQUIRED
    else:
        # In development, be more lenient
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
    return ssl_context

def parse_db_url(db_url: str) -> Dict[str, Any]:
    """Parse database URL and return connection parameters."""
    parsed = urlparse(db_url)
    
    # Extract connection parameters
    params = {
        "username": parsed.username or "postgres",
        "password": parsed.password or "",
        "host": parsed.hostname or "localhost",
        "port": str(parsed.port or 5432),
        "database": parsed.path.lstrip("/") or "railway",
        "query": parsed.query,
    }
    
    logger.info(f"Database connection parameters: {', '.join(f'{k}: {v}' for k, v in params.items())}")
    return params

def create_db_engine():
    """Create and return an async database engine with proper configuration."""
    try:
        db_url = settings.DATABASE
        logger.info("Initializing database engine")
        
        # Configure connection arguments
        connect_args: Dict[str, Any] = {
            "server_settings": {
                "application_name": settings.RAILWAY_SERVICE_NAME or "sdg_backend",
                "timezone": "UTC",
            }
        }
        
        # Log the database URL (with redacted password for security)
        if "@" in db_url:
            redacted_url = db_url.split("@")[0].split("://")[0] + "://*****:*****@" + "@".join(db_url.split("@")[1:])
            logger.info(f"Connecting to database: {redacted_url}")
        
        # Create the engine with appropriate SSL settings
        engine = create_async_engine(
            db_url,
            echo=settings.DEBUG,
            pool_pre_ping=True,
            pool_recycle=300,  # Recycle connections after 5 minutes
            pool_size=5,       # Maintain up to 5 connections
            max_overflow=10,   # Allow up to 10 overflow connections
            connect_args=connect_args
        )
        
        logger.info("Database engine created successfully")
        return engine
        
    except Exception as e:
        logger.error(f"Failed to create database engine: {str(e)}")
        raise

# Create the database engine
try:
    engine = create_db_engine()
    logger.info("Database engine created successfully")
except Exception as e:
    logger.error(f"Failed to create database engine: {e}")
    raise

# Create session factory using async_sessionmaker
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Base class for models
Base = declarative_base()

# Dependency to get DB session
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency that provides a database session.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            raise e
        finally:
            await session.close()

# Import all models here to ensure they are registered with SQLAlchemy
# This must be done after Base is defined
from .models import *  # noqa
