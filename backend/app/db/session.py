from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool
from typing import AsyncGenerator
import os
import ssl

from app.core.config import settings

# Create SSL context for secure connections
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE  # Disable certificate verification (use CERT_REQUIRED in production)

# Create async engine
engine = create_async_engine(
    settings.DATABASE,
    echo=settings.DEBUG,
    future=True,
    pool_pre_ping=True,
    pool_recycle=300,
    pool_size=5,       # Maintain up to 5 connections
    max_overflow=10,   # Allow up to 10 overflow connections
    connect_args={
        "ssl": ssl_context,  # Pass SSL context directly
        "server_settings": {
            "application_name": "poverty_alleviation_api",
            "timezone": "UTC",
        }
    }
)

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
