from pydantic import AnyHttpUrl, EmailStr, BaseSettings, validator
from typing import List, Optional, Union
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
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY environment variable must be set")
        
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))

    # CORS
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    @validator("BACKEND_CORS_ORIGINS", pre=True)
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
        db_name = os.getenv("PGDATABASE")
        
        if all([db_host, db_user, db_password, db_name]):
            DATABASE_URL = f"postgresql+asyncpg://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
        else:
            # Fallback to local development database
            DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/sdg"

    @property
    def DATABASE(self) -> str:
        """Return the asyncpg-compatible database URL."""
        db_url = self.DATABASE_URL
        
        # Normalize the URL if needed
        if db_url.startswith("postgres://"):
            db_url = db_url.replace("postgres://", "postgresql+asyncpg://", 1)
        elif not db_url.startswith("postgresql+asyncpg://"):
            db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)
        
        # Handle SSL for production
        if self.ENVIRONMENT == "production" and 'sslmode=' not in db_url:
            db_url += '?sslmode=require' if '?' not in db_url else '&sslmode=require'
        
        # Redact password in logs
        if '@' in db_url:
            parts = db_url.split('@')
            redacted_url = f"{parts[0].split('://')[0]}://*****:*****@{'@'.join(parts[1:])}"
            print(f"[Config] Using database URL: {redacted_url}", flush=True)
        else:
            print(f"[Config] Using database URL: {db_url}", flush=True)
        
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

    class Config:
        case_sensitive = True

settings = Settings()
