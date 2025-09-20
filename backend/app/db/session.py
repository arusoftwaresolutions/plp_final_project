import asyncio
import logging
import os
from typing import AsyncGenerator, Optional

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.exc import OperationalError, SQLAlchemyError

from backend.app.core.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

async def wait_for_db(db_url: str, max_retries: int = 10, delay: int = 5) -> bool:
    """Wait for database to become available."""
    from sqlalchemy import text
    from sqlalchemy.ext.asyncio import create_async_engine
    from urllib.parse import urlparse, parse_qs
    import ssl
    
    # Parse the URL to check for SSL parameters
    parsed = urlparse(db_url)
    query_params = parse_qs(parsed.query)
    
    # Configure SSL and connection parameters
    connect_args = {}
    
    # Only configure SSL if explicitly requested or using Render
    if 'ssl=require' in db_url.lower() or 'render.com' in db_url or 'amazonaws.com' in db_url:
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        connect_args["ssl"] = ssl_context
    
    # Set connection timeout through server_settings
    connect_args["server_settings"] = {
        "application_name": "poverty_alleviation_platform",
        "statement_timeout": "30000"  # 30 seconds
    }
    
    for attempt in range(max_retries):
        try:
            # Create a new engine for the connection test
            temp_engine = create_async_engine(
                db_url,
                connect_args=connect_args,
                pool_pre_ping=True
            )
            
            # Test the connection
            async with temp_engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
                logger.info("✅ Database connection successful")
                await conn.close()
            
            # Clean up
            await temp_engine.dispose()
            return True
            
        except Exception as e:
            error_msg = str(e).split('\n')[0]  # Get first line of error message
            if attempt == max_retries - 1:
                logger.error(f"❌ Failed to connect to database after {max_retries} attempts")
                logger.error(f"Last error: {error_msg}")
                # Log full error details in debug mode
                logger.debug(f"Full error details: {str(e)}")
                # Log the connection details (with redacted password)
                parsed = urlparse(db_url)
                if parsed.password:
                    redacted_url = db_url.replace(f":{parsed.password}@", ":*****@")
                    logger.debug(f"Connection URL: {redacted_url}")
                return False
                
            logger.warning(f"⚠️ Database not ready, retrying in {delay} seconds... (Attempt {attempt + 1}/{max_retries})")
            logger.debug(f"Connection error: {error_msg}")
            
            # Add more detailed logging for common issues
            if "connection refused" in str(e).lower():
                logger.debug("  - Check if the database server is running and accessible")
                logger.debug(f"  - Host: {parsed.hostname}, Port: {parsed.port or 5432}")
            elif "password authentication failed" in str(e).lower():
                logger.debug("  - Check if the database credentials are correct")
            elif "does not exist" in str(e).lower():
                logger.debug("  - Check if the database exists and the user has access")
                
            await asyncio.sleep(delay)
    
    return False

def create_db_engine():
    """Create and return an async database engine with proper configuration."""
    try:
        db_url = settings.DATABASE
        
        # Parse the URL to check for SSL parameters
        from urllib.parse import urlparse, parse_qs, urlunparse
        parsed = urlparse(db_url)
        
        # Configure SSL and connection parameters
        connect_args = {}
        
        # Handle SSL for PostgreSQL on Render or AWS
        is_production = settings.ENVIRONMENT == "production"
        is_cloud_db = any(x in db_url.lower() for x in ['render.com', 'amazonaws.com', 'ssl=require'])
        
        if is_cloud_db or is_production:
            import ssl
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            connect_args['ssl'] = ssl_context
            
            # Clean up the URL by removing ssl parameters from the query string
            query = parse_qs(parsed.query)
            for ssl_param in ['ssl', 'sslmode']:
                if ssl_param in query:
                    query.pop(ssl_param)
            
            # Rebuild the URL with updated query parameters
            filtered_query = '&'.join(f"{k}={v[0]}" for k, v in query.items())
            parsed = parsed._replace(query=filtered_query)
            db_url = urlunparse(parsed)
            
        # Configure connection pool settings
        pool_settings = {
            'pool_pre_ping': True,  # Verify connections before using them
            'pool_recycle': 300,    # Recycle connections after 5 minutes
            'pool_size': 5,         # Number of connections to keep open
            'max_overflow': 10,     # Max number of connections to create beyond pool_size
            'pool_timeout': 30,     # Max seconds to wait for a connection
        }
        
        # Redact password in logs
        if parsed.password:
            redacted_netloc = f"{parsed.username}:*****@{parsed.hostname}"
            if parsed.port:
                redacted_netloc += f":{parsed.port}"
            logger.info(f"Connecting to database: {parsed.scheme}://{redacted_netloc}{parsed.path}")
        else:
            logger.info(f"Connecting to database: {db_url}")
            
        # Configure server settings for better monitoring and performance
        connect_args["server_settings"] = {
            "application_name": "poverty_alleviation_platform",
            "statement_timeout": "30000",  # 30 seconds
            "idle_in_transaction_session_timeout": "60000"  # 60 seconds
        }
        
        engine = create_async_engine(
            db_url,
            connect_args=connect_args,
            pool_pre_ping=True,  # Verify connections before using them
            pool_recycle=300,    # Recycle connections after 5 minutes
            pool_size=5,         # Number of connections to keep open
            max_overflow=10,     # Max number of connections to create beyond pool_size
            pool_timeout=30,     # Max seconds to wait for a connection
            echo=settings.DEBUG,
            # Add execution options for better debugging
            execution_options={
                "isolation_level": "AUTOCOMMIT"
            }
        )
        
        logger.info("✅ Database engine created successfully")
        return engine
    except Exception as e:
        logger.error(f"❌ Failed to create database engine: {str(e)}")
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
    """Get database session with automatic cleanup."""
    session = AsyncSessionLocal()
    try:
        yield session
        await session.commit()
    except SQLAlchemyError as e:
        await session.rollback()
        logger.error(f"Database error: {str(e)}")
        raise
    finally:
        await session.close()

# Import models to register them with SQLAlchemy
from .models import *  # noqa
