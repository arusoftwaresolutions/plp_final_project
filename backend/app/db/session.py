from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
import os
import ssl
from typing import Optional

from app.core.config import settings

# Create SSL context for secure connections
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE  # For now, disable cert verification

# Helper function to get engine with proper SSL settings
def create_db_engine():
    # Parse the database URL to check if it's a production environment
    is_production = settings.RAILWAY_ENVIRONMENT == "production"
    
    # Configure SSL based on environment
    connect_args = {
        "server_settings": {
            "application_name": "sdg_backend",
            "timezone": "UTC",
        }
    }
    
    # Only add SSL in production
    if is_production:
        connect_args["ssl"] = ssl_context
    
    # Create the engine with appropriate settings
    return create_async_engine(
        settings.DATABASE,
        echo=settings.DEBUG,
        pool_pre_ping=True,
        pool_recycle=300,  # Recycle connections after 5 minutes
        pool_size=5,       # Maintain up to 5 connections
        max_overflow=10,   # Allow up to 10 overflow connections
        connect_args=connect_args
    )

# Create the database engine
engine = create_db_engine()

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
