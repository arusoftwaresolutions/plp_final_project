from pydantic import AnyHttpUrl, EmailStr, Field, field_validator, ConfigDict
from pydantic_settings import BaseSettings
from typing import List, Optional, Union, Any
import os
from dotenv import load_dotenv

# Load .env in dev mode
_ENV = os.getenv("ENVIRONMENT", "production").lower()
if _ENV in ("dev", "development", "local"):
    load_dotenv(override=True)

class Settings(BaseSettings):
    # Project
    PROJECT_NAME: str = os.getenv("BACKEND_APP_NAME", "Poverty Alleviation Platform")
    VERSION: str = os.getenv("BACKEND_APP_VERSION", "1.0.0")
    DEBUG: bool = os.getenv("ENVIRONMENT", "production").lower() == "development"
    ENVIRONMENT: str = _ENV
    API_V1_STR: str = "/api/v1"

    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "temporary-secret-key-for-build")
    if not SECRET_KEY or SECRET_KEY == "temporary-secret-key-for-build":
        if os.getenv("ENVIRONMENT") != "development":
            import secrets
            SECRET_KEY = secrets.token_urlsafe(32)
            print("WARNING: Using a temporary SECRET_KEY. Please set SECRET_KEY environment variable in production.")
        
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))

    # CORS
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    @field_validator("BACKEND_CORS_ORIGINS", mode='before')
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            v = [i.strip() for i in v.split(",")]
        if not v:
            return ["http://localhost:3000", "http://localhost:8501"]
        return v

    # Database Configuration
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    if not DATABASE_URL:
        # Construct from individual components if DATABASE_URL not provided
        db_host = os.getenv("PGHOST")
        db_port = os.getenv("PGPORT", "5432")
        db_user = os.getenv("PGUSER")
        db_password = os.getenv("PGPASSWORD")
        db_name = os.getenv("PGDATABASE", "poverty_alleviation")
        
        if all([db_host, db_user, db_password]):
            # Use asyncpg driver for async operations with SSL
            DATABASE_URL = f"postgresql+asyncpg://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
            # Add ssl=require if using Render or AWS
            if 'render.com' in db_host or 'amazonaws.com' in db_host:
                DATABASE_URL += "?ssl=require"
        else:
            # Fallback to local development database
            DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/poverty_alleviation"
    
    # Ensure the DATABASE_URL uses asyncpg and has proper SSL settings
    if DATABASE_URL.startswith("postgresql://") and "+asyncpg" not in DATABASE_URL:
        DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

    @property
    def DATABASE(self) -> str:
        """Return the asyncpg-compatible database URL with proper SSL settings."""
        db_url = self.DATABASE_URL
        
        # Parse the URL to handle SSL settings properly
        from urllib.parse import urlparse, urlunparse, parse_qs, urlencode
        parsed = urlparse(db_url)
        query = parse_qs(parsed.query)
        
        # Remove any existing ssl/sslmode parameters as we'll handle them in connect_args
        for key in ['ssl', 'sslmode']:
            if key in query:
                del query[key]
        
        # Add SSL for production environments if needed
        if self.ENVIRONMENT == "production" and 'render.com' in db_url:
            query['ssl'] = ['require']
        
        # Rebuild the URL with cleaned query parameters
        clean_query = urlencode(query, doseq=True) if query else ""
        db_url = urlunparse(parsed._replace(query=clean_query))
        
        # Ensure we're using the asyncpg driver
        if db_url.startswith("postgres://"):
            db_url = db_url.replace("postgres://", "postgresql+asyncpg://", 1)
        elif db_url.startswith("postgresql://") and "+asyncpg" not in db_url:
            db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)
        
        # Log the database URL (with redacted password)
        parsed = urlparse(db_url)
        if parsed.password:
            redacted_netloc = f"{parsed.username}:*****@{parsed.hostname}"
            if parsed.port:
                redacted_netloc += f":{parsed.port}"
            print(f"[Config] Using database: {parsed.scheme}://{redacted_netloc}{parsed.path}", flush=True)
        else:
            print(f"[Config] Using database: {db_url}", flush=True)
            
        return db_url

    @property
    def SYNC_DATABASE_URL(self) -> str:
        """Return sync DB URL (for migrations)."""
        return self.DATABASE.replace("postgresql+asyncpg://", "postgresql://")

    # Admin
    FIRST_SUPERUSER: str = os.getenv("FIRST_SUPERUSER", "admin")
    FIRST_SUPERUSER_EMAIL: EmailStr = os.getenv("FIRST_SUPERUSER_EMAIL", "admin@example.com")
    FIRST_SUPERUSER_PASSWORD: str = os.getenv("FIRST_SUPERUSER_PASSWORD", "admin123")

    # AI Settings
    AI_MODEL_PATH: str = os.getenv("AI_MODEL_PATH", "models/budget_recommender.joblib")

    model_config = ConfigDict(
        case_sensitive=True,
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
