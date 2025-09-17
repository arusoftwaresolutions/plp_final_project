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
    RAILWAY_ENVIRONMENT: str = os.getenv("RAILWAY_ENVIRONMENT", "production").lower()
    RAILWAY_SERVICE_NAME: Optional[str] = os.getenv("RAILWAY_SERVICE_NAME")
    
    # Database connection settings
    DATABASE_URL: Optional[str] = os.getenv("DATABASE_URL")
    
    # Fallback to individual components if DATABASE_URL not provided
    POSTGRES_SERVER: str = os.getenv("PGHOST") or os.getenv("POSTGRES_SERVER") or "db"
    POSTGRES_USER: str = os.getenv("PGUSER") or os.getenv("POSTGRES_USER") or "postgres"
    POSTGRES_PASSWORD: str = os.getenv("PGPASSWORD") or os.getenv("POSTGRES_PASSWORD") or ""
    POSTGRES_DB: str = os.getenv("PGDATABASE") or os.getenv("POSTGRES_DB") or "railway"
    POSTGRES_PORT: str = str(os.getenv("PGPORT") or os.getenv("POSTGRES_PORT") or "5432")
    
    # Force SSL in production
    POSTGRES_QUERY: str = "sslmode=require" if RAILWAY_ENVIRONMENT == "production" else ""
    
    @validator("DATABASE_URL", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: dict) -> str:
        # Debug print all values for troubleshooting
        print(f"[Config] Assembling DB URL. DATABASE_URL: {v}", flush=True)
        print(f"[Config] Available values: {values}", flush=True)
        
        # If DATABASE_URL is explicitly provided in environment, use it directly
        env_db_url = os.getenv("DATABASE_URL")
        if env_db_url:
            print(f"[Config] Using DATABASE_URL from environment", flush=True)
            v = env_db_url
        
        if v:
            print(f"[Config] Using DATABASE_URL: {v}", flush=True)
            # Convert postgres:// to postgresql+asyncpg://
            if v.startswith("postgres://"):
                v = v.replace("postgres://", "postgresql+asyncpg://", 1)
            # Ensure it uses asyncpg
            elif not (v.startswith("postgresql+asyncpg://") or v.startswith("postgresql://")):
                v = f"postgresql+asyncpg://{v}"
            return v
            
        # Otherwise build from components
        user = values.get("POSTGRES_USER") or os.getenv("POSTGRES_USER") or "postgres"
        password = values.get("POSTGRES_PASSWORD") or os.getenv("POSTGRES_PASSWORD") or ""
        host = values.get("POSTGRES_SERVER") or os.getenv("POSTGRES_SERVER") or "db"
        port = values.get("POSTGRES_PORT") or os.getenv("POSTGRES_PORT") or "5432"
        db = values.get("POSTGRES_DB") or os.getenv("POSTGRES_DB") or "railway"
        query = values.get("POSTGRES_QUERY") or os.getenv("POSTGRES_QUERY") or ""
        
        # Construct the URL with defaults
        url = f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{db}"
        if query:
            url = f"{url}?{query}"
        
        print(f"[Config] Constructed database URL from components: {url}", flush=True)
        return url
    
    @property
    def SYNC_DATABASE_URL(self) -> str:
        """Return the sync database URL (for migrations)."""
        return self.DATABASE.replace("postgresql+asyncpg://", "postgresql://")
    
    @property
    def DATABASE(self) -> str:
        """Return the database URL."""
        # Try to get DATABASE_URL from environment first
        env_db_url = os.getenv("DATABASE_URL")
        if env_db_url:
            if env_db_url.startswith("postgres://"):
                env_db_url = env_db_url.replace("postgres://", "postgresql+asyncpg://", 1)
            elif not (env_db_url.startswith("postgresql+asyncpg://") or env_db_url.startswith("postgresql://")):
                env_db_url = f"postgresql+asyncpg://{env_db_url}"
            return env_db_url
            
        # If we have a DATABASE_URL in settings, use it
        if hasattr(self, 'DATABASE_URL') and self.DATABASE_URL:
            return self.DATABASE_URL
            
        # Otherwise build from components
        user = os.getenv("POSTGRES_USER") or getattr(self, 'POSTGRES_USER', 'postgres')
        password = os.getenv("POSTGRES_PASSWORD") or getattr(self, 'POSTGRES_PASSWORD', '')
        host = os.getenv("POSTGRES_SERVER") or getattr(self, 'POSTGRES_SERVER', 'db')
        port = os.getenv("POSTGRES_PORT") or getattr(self, 'POSTGRES_PORT', '5432')
        db = os.getenv("POSTGRES_DB") or getattr(self, 'POSTGRES_DB', 'railway')
        query = os.getenv("POSTGRES_QUERY") or getattr(self, 'POSTGRES_QUERY', '')
        
        url = f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{db}"
        if query:
            url = f"{url}?{query}"
            
        print(f"[Config] Final database URL: {url}", flush=True)
        return url
    
    # Admin
    FIRST_SUPERUSER: str = os.getenv("FIRST_SUPERUSER", "admin")
    FIRST_SUPERUSER_EMAIL: EmailStr = os.getenv("FIRST_SUPERUSER_EMAIL", "admin@example.com")
    FIRST_SUPERUSER_PASSWORD: str = os.getenv("FIRST_SUPERUSER_PASSWORD", "admin123")
    
    # AI Settings
    AI_MODEL_PATH: str = os.getenv("AI_MODEL_PATH", "models/budget_recommender.joblib")
    
    class Config:
        case_sensitive = True

settings = Settings()
