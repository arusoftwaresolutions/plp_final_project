from pydantic import AnyHttpUrl, EmailStr, BaseSettings, validator
from typing import List, Optional, Union
import os
from dotenv import load_dotenv
from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode

# Load .env in dev mode only
_ENV = os.getenv("ENVIRONMENT", "production").lower()
if _ENV in ("dev", "development", "local"):
    load_dotenv(override=True)

# Debug print to confirm Railway variable injection
print("DEBUG: DATABASE_URL in os.environ =", os.getenv("DATABASE_URL"), flush=True)

class Settings(BaseSettings):
    # Project
    PROJECT_NAME: str = os.getenv("BACKEND_APP_NAME", "Poverty Alleviation Platform")
    VERSION: str = os.getenv("BACKEND_APP_VERSION", "1.0.0")
    DEBUG: bool = bool(os.getenv("BACKEND_DEBUG", False))
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
        if not v:
            return ["http://localhost:8501", "http://localhost:3000"]
        return v

    # Railway env
    RAILWAY_ENVIRONMENT: str = os.getenv("RAILWAY_ENVIRONMENT", "production").lower()
    RAILWAY_SERVICE_NAME: Optional[str] = os.getenv("RAILWAY_SERVICE_NAME")

    # Database Configuration
    # Prefer DATABASE_URL or RAILWAY_DATABASE_URL environment variable
    DATABASE_URL: Optional[str] = os.getenv("DATABASE_URL") or os.getenv("RAILWAY_DATABASE_URL")
    
    # Development defaults (only used if no DATABASE_URL is provided)
    DEV_DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/railway"

    @property
    def DATABASE(self) -> str:
        """Return the asyncpg-compatible database URL."""
        # Use DATABASE_URL if available and not masked by Railway
        if self.DATABASE_URL and '*****' not in self.DATABASE_URL:
            try:
                db_url = self.DATABASE_URL
                
                # Normalize the URL
                if db_url.startswith("postgres://"):
                    db_url = db_url.replace("postgres://", "postgresql+asyncpg://", 1)
                elif not db_url.startswith("postgresql+asyncpg://"):
                    db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)

                # Handle SSL for production
                if self.RAILWAY_ENVIRONMENT == "production" and 'ssl=' not in db_url and 'sslmode=' not in db_url:
                    db_url += '?ssl=require' if '?' not in db_url else '&ssl=require'

                # Redact password in logs
                if '@' in db_url:
                    parts = db_url.split('@')
                    redacted_url = f"{parts[0].split('://')[0]}://*****:*****@{'@'.join(parts[1:])}"
                    print(f"[Config] Using database URL: {redacted_url}", flush=True)
                else:
                    print(f"[Config] Using database URL: {db_url}", flush=True)
                
                return db_url
            except Exception as e:
                print(f"[Config] Error processing DATABASE_URL: {e}", flush=True)
        
        # Check for individual components if DATABASE_URL is masked or not available
        try:
            db_host = os.getenv("PGHOST") or "localhost"
            db_port = os.getenv("PGPORT") or "5432"
            db_user = os.getenv("PGUSER") or "postgres"
            db_password = os.getenv("PGPASSWORD") or "postgres"
            db_name = os.getenv("PGDATABASE") or "railway"
            
            db_url = f"postgresql+asyncpg://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
            
            # Handle SSL for production
            if self.RAILWAY_ENVIRONMENT == "production":
                db_url += '?ssl=require'
            
            print(f"[Config] Using database from individual components: postgresql+asyncpg://{db_user}:*****@{db_host}:{db_port}/{db_name}", flush=True)
            return db_url
            
        except Exception as e:
            print(f"[Config] Error creating database URL from components: {e}", flush=True)
            
        # Fallback to development database if all else fails
        print("[Config] WARNING: Using development database URL", flush=True)
        return self.DEV_DATABASE_URL

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
