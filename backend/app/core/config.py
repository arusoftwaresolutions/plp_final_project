from pydantic import AnyHttpUrl, EmailStr, PostgresDsn, validator, Field, BaseSettings
from typing import List, Optional, Union
import os
from dotenv import load_dotenv

# Load .env only in development to avoid overriding production env on Railway
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
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 1440))  # 24 hours
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:8501",
        "http://localhost:3000",
    ]
    
    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    # Railway provides these env vars
    RAILWAY_ENVIRONMENT: str = os.getenv("RAILWAY_ENVIRONMENT", "")
    RAILWAY_SERVICE_NAME: Optional[str] = os.getenv("RAILWAY_SERVICE_NAME")
    
    # Database - use Railway's PG* env vars if available, fall back to POSTGRES_* or defaults
    POSTGRES_SERVER: str = os.getenv("PGHOST") or os.getenv("POSTGRES_SERVER", "db")
    POSTGRES_USER: str = os.getenv("PGUSER") or os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("PGPASSWORD") or os.getenv("POSTGRES_PASSWORD", "")
    POSTGRES_DB: str = os.getenv("PGDATABASE") or os.getenv("POSTGRES_DB", "railway")
    POSTGRES_PORT: str = os.getenv("PGPORT") or os.getenv("POSTGRES_PORT", "5432")
    POSTGRES_QUERY: str = os.getenv("POSTGRES_QUERY", "sslmode=require")
    
    # Allow direct DATABASE_URL override from env
    DATABASE_URL: Optional[str] = os.getenv("DATABASE_URL")
    
    @validator("DATABASE_URL", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: dict) -> str:
        # Build connection parameters
        params = {
            "host": values.get("POSTGRES_SERVER", "db"),
            "port": values.get("POSTGRES_PORT", "5432"),
            "user": values.get("POSTGRES_USER", "postgres"),
            "password": values.get("POSTGRES_PASSWORD", ""),
            "database": values.get("POSTGRES_DB", "railway"),
            "ssl": "require"  # Force SSL for all connections
        }
        
        # If DATABASE_URL is provided, parse it and update params
        if v:
            from urllib.parse import urlparse, parse_qs
            try:
                parsed = urlparse(v)
                if parsed.hostname:
                    params["host"] = parsed.hostname
                if parsed.port:
                    params["port"] = str(parsed.port)
                if parsed.username:
                    params["user"] = parsed.username
                if parsed.password:
                    params["password"] = parsed.password
                if parsed.path.lstrip('/'):
                    params["database"] = parsed.path.lstrip('/')
                if parsed.query:
                    query_params = parse_qs(parsed.query)
                    if 'sslmode' in query_params:
                        params["ssl"] = query_params['sslmode'][0]
            except Exception as e:
                print(f"[Config] Error parsing DATABASE_URL: {e}", flush=True)
        
        # Construct URL without query params first
        url = f"postgresql+asyncpg://{params['user']}:{params['password']}@{params['host']}:{params['port']}/{params['database']}"
        
        # Add SSL as a connection argument instead of query param
        # This prevents the 'sslmode' argument from being passed to asyncpg.connect()
        return url
    
    @property
    def SYNC_DATABASE_URL(self) -> str:
        """Return the sync database URL (for migrations)."""
        return self.DATABASE.replace("postgresql+asyncpg://", "postgresql://")
    
    @property
    def DATABASE(self) -> str:
        """Return the database URL."""
        if self.DATABASE_URL:
            return str(self.DATABASE_URL).replace("postgresql://", "postgresql+asyncpg://")
        return self.assemble_db_connection(None, {
            'POSTGRES_USER': self.POSTGRES_USER,
            'POSTGRES_PASSWORD': self.POSTGRES_PASSWORD,
            'POSTGRES_SERVER': self.POSTGRES_SERVER,
            'POSTGRES_DB': self.POSTGRES_DB
        })
    
    # Admin
    FIRST_SUPERUSER: str = os.getenv("FIRST_SUPERUSER", "admin")
    FIRST_SUPERUSER_EMAIL: EmailStr = os.getenv("FIRST_SUPERUSER_EMAIL", "admin@example.com")
    FIRST_SUPERUSER_PASSWORD: str = os.getenv("FIRST_SUPERUSER_PASSWORD", "admin123")
    
    # AI Settings
    AI_MODEL_PATH: str = os.getenv("AI_MODEL_PATH", "models/budget_recommender.joblib")
    
    class Config:
        case_sensitive = True

settings = Settings()
