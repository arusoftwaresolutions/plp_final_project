from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
import logging
from typing import AsyncGenerator, Optional
import os

from app.core.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_db_engine():
    """Create and return an async database engine with proper configuration."""
    try:
        db_url = settings.DATABASE
        
        # Redact password in logs
        if "@" in db_url:
            parts = db_url.split("@")
            redacted_url = f"{parts[0].split('://')[0]}://*****:*****@{'@'.join(parts[1:])}"
            logger.info(f"Connecting to database: {redacted_url}")
        else:
            logger.info(f"Connecting to database: {db_url}")

        # Configure connection pool and timeouts
        engine = create_async_engine(
            db_url,
            echo=settings.DEBUG,
            pool_pre_ping=True,  # Verify connections before using them
            pool_recycle=300,    # Recycle connections after 5 minutes
            pool_size=5,         # Number of connections to keep open
            max_overflow=10,     # Max number of connections to create beyond pool_size
            pool_timeout=30,     # Max seconds to wait for a connection
            connect_args={"connect_timeout": 10}  # Connection timeout in seconds
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
