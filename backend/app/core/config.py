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
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []
    
    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        # Handle string input (comma-separated)
        if isinstance(v, str) and not v.startswith("["):
            v = [i.strip() for i in v.split(",")]
        
        # Get frontend URL from environment
        frontend_url = os.getenv("FRONTEND_URL")
        
        # Default origins (for local development)
        default_origins = [
            "http://localhost:8501",
            "http://localhost:3000"
        ]
        
        # If we have explicit origins from config, use them
        if v and isinstance(v, list) and len(v) > 0:
            print(f"[Config] Using configured CORS origins: {v}", flush=True)
            return v
            
        # If FRONTEND_URL is set, use it as the primary origin
        if frontend_url:
            # Ensure it's a list and strip any trailing slashes
            frontend_url = frontend_url.rstrip('/')
            print(f"[Config] Using FRONTEND_URL for CORS: {frontend_url}", flush=True)
            return [frontend_url] + default_origins
            
        # If no FRONTEND_URL, use defaults
        print("[Config] Using default CORS origins (no custom configuration found)", flush=True)
        return default_origins
    
    # Railway provides these env vars
    RAILWAY_ENVIRONMENT: str = os.getenv("RAILWAY_ENVIRONMENT", "production").lower()
    RAILWAY_SERVICE_NAME: Optional[str] = os.getenv("RAILWAY_SERVICE_NAME")
    
    # Database connection settings - prioritize direct URL first
    DATABASE_URL: Optional[str] = os.getenv("DATABASE_URL")
    
    # Railway's internal database URL (if using Railway's managed PostgreSQL)
    RAILWAY_DATABASE_URL: Optional[str] = os.getenv("DATABASE_URL")
    
    # Fallback to individual components if DATABASE_URL not provided
    POSTGRES_SERVER: str = os.getenv("PGHOST") or os.getenv("POSTGRES_SERVER") or "db"
    POSTGRES_USER: str = os.getenv("PGUSER") or os.getenv("POSTGRES_USER") or "postgres"
    POSTGRES_PASSWORD: str = os.getenv("PGPASSWORD") or os.getenv("POSTGRES_PASSWORD") or ""
    POSTGRES_DB: str = os.getenv("PGDATABASE") or os.getenv("POSTGRES_DB") or "railway"
    POSTGRES_PORT: str = str(os.getenv("PGPORT") or os.getenv("POSTGRES_PORT") or "5432")
    
    # Force SSL in production
    POSTGRES_QUERY: str = "sslmode=require" if RAILWAY_ENVIRONMENT == "production" else ""
    
    # Additional debug info
    def __init__(self, **values):
        super().__init__(**values)
        print("\n[Config] Current database configuration:", flush=True)
        print(f"  DATABASE_URL: {self.DATABASE_URL}", flush=True)
        print(f"  RAILWAY_DATABASE_URL: {self.RAILWAY_DATABASE_URL}", flush=True)
        print(f"  POSTGRES_SERVER: {self.POSTGRES_SERVER}", flush=True)
        print(f"  POSTGRES_USER: {self.POSTGRES_USER}", flush=True)
        print(f"  POSTGRES_DB: {self.POSTGRES_DB}", flush=True)
        print(f"  POSTGRES_PORT: {self.POSTGRES_PORT}", flush=True)
        print(f"  RAILWAY_ENVIRONMENT: {self.RAILWAY_ENVIRONMENT}", flush=True)
    
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
        """Return the database URL with proper formatting and logging."""
        # 1. First try RAILWAY_DATABASE_URL (Railway's default)
        if self.RAILWAY_DATABASE_URL:
            url = self.RAILWAY_DATABASE_URL
            print(f"[Config] Using RAILWAY_DATABASE_URL: {url}", flush=True)
            return self._format_db_url(url)
            
        # 2. Try direct DATABASE_URL from environment
        env_db_url = os.getenv("DATABASE_URL")
        if env_db_url:
            print(f"[Config] Using DATABASE_URL from environment", flush=True)
            return self._format_db_url(env_db_url)
            
        # 3. Try DATABASE_URL from settings
        if hasattr(self, 'DATABASE_URL') and self.DATABASE_URL:
            print("[Config] Using DATABASE_URL from settings", flush=True)
            return self._format_db_url(self.DATABASE_URL)
            
        # 4. Build from individual components
        print("[Config] Building database URL from components", flush=True)
        user = self.POSTGRES_USER
        password = self.POSTGRES_PASSWORD
        host = self.POSTGRES_SERVER
        port = self.POSTGRES_PORT
        db = self.POSTGRES_DB
        query = self.POSTGRES_QUERY
        
        # Construct the URL
        credentials = f"{user}"
        if password:
            credentials = f"{user}:{password}"
            
        url = f"postgresql+asyncpg://{credentials}@{host}:{port}/{db}"
        if query:
            url = f"{url}?{query}"
            
        print(f"[Config] Final database URL: {url}", flush=True)
        return url
        
    def _format_db_url(self, url: str) -> str:
        """Format the database URL to use asyncpg driver and add SSL if needed."""
        if not url:
            return url
            
        # Convert postgres:// to postgresql+asyncpg://
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql+asyncpg://", 1)
        elif not (url.startswith("postgresql+asyncpg://") or url.startswith("postgresql://")):
            url = f"postgresql+asyncpg://{url}"
            
        # Add SSL if in production and not already specified
        if self.RAILWAY_ENVIRONMENT == "production" and "?sslmode=" not in url:
            url += "?sslmode=require"
            
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
