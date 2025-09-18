from pydantic import AnyHttpUrl, EmailStr, PostgresDsn, validator, Field, BaseSettings
from typing import List, Optional, Union, Dict, Any
import os
from dotenv import load_dotenv

# Load .env only in development to avoid overriding production env on Railway
_ENV = os.getenv("ENVIRONMENT", "production").lower()
if _ENV in ("dev", "development", "local"):
    load_dotenv(override=True)

# Print all environment variables for debugging
print("\n[Config] Environment variables:", flush=True)
for key, value in sorted(os.environ.items()):
    if any(k in key.upper() for k in ['POSTGRES', 'DATABASE', 'PG', 'RAILWAY', 'ENV']):
        print(f"  {key}: {value}", flush=True)

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
    
    # Railway environment
    RAILWAY_ENVIRONMENT: str = os.getenv("RAILWAY_ENVIRONMENT", "production").lower()
    RAILWAY_SERVICE_NAME: Optional[str] = os.getenv("RAILWAY_SERVICE_NAME")
    
    # Database configuration
    # 1. First try DATABASE_URL (standard PostgreSQL URL)
    # 2. Then try RAILWAY_DATABASE_URL (Railway's default)
    # 3. Fall back to individual components
    DATABASE_URL: Optional[str] = None
    
    # Individual database components (for building URL if needed)
    POSTGRES_SERVER: str = os.getenv("PGHOST") or os.getenv("POSTGRES_HOSTNAME") or "db"
    POSTGRES_USER: str = os.getenv("PGUSER") or os.getenv("POSTGRES_USER") or "postgres"
    POSTGRES_PASSWORD: str = os.getenv("PGPASSWORD") or os.getenv("POSTGRES_PASSWORD") or ""
    POSTGRES_DB: str = os.getenv("PGDATABASE") or os.getenv("POSTGRES_DB") or "railway"
    POSTGRES_PORT: str = str(os.getenv("PGPORT") or os.getenv("POSTGRES_PORT") or "5432")
    
    # Force SSL in production
    POSTGRES_QUERY: str = "sslmode=require" if RAILWAY_ENVIRONMENT == "production" else ""
    
    def __init__(self, **data: Any):
        super().__init__(**data)
        
        # Debug print all database-related environment variables
        print("\n[Config] Environment Variables:", flush=True)
        for key, value in os.environ.items():
            if any(k in key.upper() for k in ['POSTGRES', 'DATABASE', 'PG', 'RAILWAY', 'ENV']):
                print(f"  {key}: {value}", flush=True)
        
        # Database Configuration
        print("\n[Config] Database Configuration:", flush=True)
        
        # 1. Check for direct DATABASE_URL
        if os.getenv("DATABASE_URL"):
            self.DATABASE_URL = os.getenv("DATABASE_URL")
            print(f"  Using DATABASE_URL from environment: {self.DATABASE_URL}", flush=True)
        # 2. Check for Railway's database URL
        elif os.getenv("RAILWAY_DATABASE_URL"):
            self.DATABASE_URL = os.getenv("RAILWAY_DATABASE_URL")
            print(f"  Using RAILWAY_DATABASE_URL: {self.DATABASE_URL}", flush=True)
        # 3. Fall back to individual components
        else:
            print("  No DATABASE_URL found, using individual components", flush=True)
            self.DATABASE_URL = (
                f"postgresql+asyncpg://{self.POSTGRES_USER}:"
                f"{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:"
                f"{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
            )
        
        # Ensure the URL uses the correct protocol
        if self.DATABASE_URL and self.DATABASE_URL.startswith("postgres://"):
            self.DATABASE_URL = self.DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)
        
        # Add SSL if in production
        if self.RAILWAY_ENVIRONMENT == "production" and "?" not in self.DATABASE_URL:
            self.DATABASE_URL += "?sslmode=require"
        
        # CORS Configuration
        frontend_url = os.getenv("FRONTEND_URL") or os.getenv("RAILWAY_STATIC_URL")
        if frontend_url:
            frontend_url = frontend_url.rstrip('/')
            if frontend_url not in [str(x) for x in self.BACKEND_CORS_ORIGINS]:
                self.BACKEND_CORS_ORIGINS.append(frontend_url)
        
        # Print final configuration
        print("\n[Config] Final Configuration:", flush=True)
        print(f"  DATABASE_URL: {self.DATABASE_URL}", flush=True)
        print(f"  POSTGRES_SERVER: {self.POSTGRES_SERVER}", flush=True)
        print(f"  POSTGRES_USER: {self.POSTGRES_USER}", flush=True)
        print(f"  POSTGRES_DB: {self.POSTGRES_DB}", flush=True)
        print(f"  POSTGRES_PORT: {self.POSTGRES_PORT}", flush=True)
        print(f"  RAILWAY_ENVIRONMENT: {self.RAILWAY_ENVIRONMENT}", flush=True)
        print(f"  FRONTEND_URL: {frontend_url}", flush=True)
        print(f"  BACKEND_CORS_ORIGINS: {self.BACKEND_CORS_ORIGINS}", flush=True)
    
    @validator("DATABASE_URL", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: dict) -> str:
        # This is now handled in __init__, but we keep this for backward compatibility
        if v:
            print(f"[Config] Using provided DATABASE_URL: {v}", flush=True)
            # Convert postgres:// to postgresql+asyncpg://
            if v.startswith("postgres://"):
                v = v.replace("postgres://", "postgresql+asyncpg://", 1)
            return v
        
        # If we get here, we'll build from components
        print("[Config] Building database URL from components", flush=True)
        
        user = values.get("POSTGRES_USER") or os.getenv("PGUSER") or "postgres"
        password = values.get("POSTGRES_PASSWORD") or os.getenv("PGPASSWORD") or ""
        host = values.get("POSTGRES_SERVER") or os.getenv("PGHOST") or "db"
        port = values.get("POSTGRES_PORT") or os.getenv("PGPORT") or "5432"
        db = values.get("POSTGRES_DB") or os.getenv("PGDATABASE") or "railway"
        
        # Build the URL
        url = f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{db}"
        
        # Add SSL if in production
        if os.getenv("RAILWAY_ENVIRONMENT") == "production":
            if "?" not in url:
                url += "?sslmode=require"
            elif "sslmode=" not in url:
                url += "&sslmode=require"
        
        print(f"[Config] Built database URL: {url}", flush=True)
        return url
    
    @property
    def SYNC_DATABASE_URL(self) -> str:
        """Return the sync database URL (for migrations)."""
        return self.DATABASE.replace("postgresql+asyncpg://", "postgresql://")
    
    @property
    def DATABASE(self) -> str:
        """Return the database URL with proper formatting and logging."""
        # If we already have a DATABASE_URL, use it
        if hasattr(self, 'DATABASE_URL') and self.DATABASE_URL:
            url = self.DATABASE_URL
            print(f"[Config] Using configured DATABASE_URL: {url}", flush=True)
            return url
            
        # Fall back to building from components
        print("[Config] Building database URL from components", flush=True)
        
        # Get values from environment or instance attributes
        user = os.getenv("PGUSER") or getattr(self, 'POSTGRES_USER', 'postgres')
        password = os.getenv("PGPASSWORD") or getattr(self, 'POSTGRES_PASSWORD', '')
        host = os.getenv("PGHOST") or getattr(self, 'POSTGRES_SERVER', 'db')
        port = os.getenv("PGPORT") or getattr(self, 'POSTGRES_PORT', '5432')
        db = os.getenv("PGDATABASE") or getattr(self, 'POSTGRES_DB', 'railway')
        
        # Build the URL
        credentials = f"{user}:{password}" if password else user
        url = f"postgresql+asyncpg://{credentials}@{host}:{port}/{db}"
        
        # Add SSL if in production
        if self.RAILWAY_ENVIRONMENT == "production":
            if "?" not in url:
                url += "?sslmode=require"
            elif "sslmode=" not in url:
                url += "&sslmode=require"
        
        print(f"[Config] Final database URL: {url}", flush=True)
        return url
        
    def _format_db_url(self, url: str) -> str:
        """Format the database URL to use asyncpg driver and add SSL if needed."""
        if not url:
            return url
            
        # Ensure we have the correct protocol
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql+asyncpg://", 1)
        elif not (url.startswith("postgresql+asyncpg://") or url.startswith("postgresql://")):
            url = f"postgresql+asyncpg://{url}"
        
        # Add SSL if in production and not already specified
        if self.RAILWAY_ENVIRONMENT == "production":
            if "?" not in url:
                url += "?sslmode=require"
            elif "sslmode=" not in url:
                url += "&sslmode=require"
        
        print(f"[Config] Formatted database URL: {url}", flush=True)
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
