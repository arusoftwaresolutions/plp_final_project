from pydantic import AnyHttpUrl, EmailStr, BaseSettings, validator
from typing import List, Optional, Union, Any
import os
from dotenv import load_dotenv
from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode

# Load .env only in local dev
_ENV = os.getenv("ENVIRONMENT", "production").lower()
if _ENV in ("dev", "development", "local"):
    load_dotenv(override=True)

class Settings(BaseSettings):
    # Project
    PROJECT_NAME: str = os.getenv("BACKEND_APP_NAME", "Poverty Alleviation Platform")
    VERSION: str = os.getenv("BACKEND_APP_VERSION", "1.0.0")
    DEBUG: bool = os.getenv("BACKEND_DEBUG", False)
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "production")
    API_V1_STR: str = "/api/v1"

    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 1440))

    # CORS
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            v = [i.strip() for i in v.split(",")]
        return v or ["http://localhost:8501", "http://localhost:3000"]

    # Railway environment
    RAILWAY_ENVIRONMENT: str = os.getenv("RAILWAY_ENVIRONMENT", "production").lower()
    RAILWAY_SERVICE_NAME: Optional[str] = os.getenv("RAILWAY_SERVICE_NAME")

    # Database URL
    DATABASE_URL: Optional[str] = os.getenv("DATABASE_URL") or os.getenv("RAILWAY_DATABASE_URL")

    POSTGRES_SERVER: str = os.getenv("PGHOST") or os.getenv("POSTGRES_HOSTNAME") or "db"
    POSTGRES_USER: str = os.getenv("PGUSER") or os.getenv("POSTGRES_USER") or "postgres"
    POSTGRES_PASSWORD: str = os.getenv("PGPASSWORD") or os.getenv("POSTGRES_PASSWORD") or ""
    POSTGRES_DB: str = os.getenv("PGDATABASE") or os.getenv("POSTGRES_DB") or "railway"
    POSTGRES_PORT: str = str(os.getenv("PGPORT") or os.getenv("POSTGRES_PORT") or "5432")

    @property
    def DATABASE(self) -> str:
        """Return the database URL formatted for asyncpg."""
        db_url = self.DATABASE_URL
        if db_url:
            # Normalize prefix
            if db_url.startswith("postgres://"):
                db_url = db_url.replace("postgres://", "postgresql+asyncpg://", 1)
            elif db_url.startswith("postgresql://"):
                db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)

            # Force SSL for Railway
            if self.RAILWAY_ENVIRONMENT == "production":
                parsed = urlparse(db_url)
                query = dict(parse_qsl(parsed.query))
                query["ssl"] = "require"
                db_url = urlunparse(parsed._replace(query=urlencode(query)))
            return db_url

        # Fallback (local dev)
        credentials = f"{self.POSTGRES_USER}"
        if self.POSTGRES_PASSWORD:
            credentials = f"{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
        db_url = f"postgresql+asyncpg://{credentials}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        if self.RAILWAY_ENVIRONMENT == "production":
            db_url += "?ssl=require"
        return db_url

    @property
    def SYNC_DATABASE_URL(self) -> str:
        return self.DATABASE.replace("postgresql+asyncpg://", "postgresql://")

    class Config:
        case_sensitive = True

settings = Settings()
