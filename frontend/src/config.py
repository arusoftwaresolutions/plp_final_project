"""Configuration settings for the Poverty Alleviation Platform.

This module defines all the configuration settings used throughout the application.
Environment variables take precedence over default values.
"""
import os
from typing import List, Optional
from pydantic import BaseSettings, PostgresDsn, validator, HttpUrl, AnyUrl
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    """Application settings.
    
    All settings can be overridden using environment variables with the same name in uppercase.
    """
    
    # Application settings
    APP_NAME: str = "Poverty Alleviation Platform"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    # API settings
    API_BASE_URL: HttpUrl = os.getenv("API_BASE_URL", "https://plp-final-project-bgex.onrender.com/api/v1")
    API_PREFIX: str = "/api/v1"
    API_TIMEOUT: int = int(os.getenv("API_TIMEOUT", "30"))  # seconds
    
    # Authentication
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
    
    # CORS settings
    CORS_ORIGINS: List[HttpUrl] = os.getenv(
        "CORS_ORIGINS", 
        "http://localhost:3000,http://localhost:8501"
    ).split(",")
    
    # Security
    SECURE_COOKIES: bool = os.getenv("SECURE_COOKIES", "True").lower() == "true"
    SESSION_COOKIE_NAME: str = os.getenv("SESSION_COOKIE_NAME", "poverty_alleviation_session")
    
    # Database (if needed for local development)
    DATABASE_URL: Optional[PostgresDsn] = os.getenv("DATABASE_URL")
    
    # Email settings
    SMTP_SERVER: Optional[str] = os.getenv("SMTP_SERVER")
    SMTP_PORT: Optional[int] = int(os.getenv("SMTP_PORT", "587")) if os.getenv("SMTP_PORT") else None
    SMTP_USERNAME: Optional[str] = os.getenv("SMTP_USERNAME")
    SMTP_PASSWORD: Optional[str] = os.getenv("SMTP_PASSWORD")
    EMAIL_FROM: Optional[str] = os.getenv("EMAIL_FROM", "noreply@poverty-alleviation.org")
    EMAIL_TEMPLATES_DIR: str = os.getenv("EMAIL_TEMPLATES_DIR", "email-templates")
    
    # Frontend URLs (for email templates, etc.)
    FRONTEND_URL: HttpUrl = os.getenv("FRONTEND_URL", "http://localhost:8501")
    
    # File upload settings
    MAX_UPLOAD_SIZE: int = int(os.getenv("MAX_UPLOAD_SIZE", "10485760"))  # 10MB default
    ALLOWED_FILE_TYPES: List[str] = os.getenv(
        "ALLOWED_FILE_TYPES", 
        "image/jpeg,image/png,application/pdf"
    ).split(",")
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = os.getenv(
        "LOG_FORMAT", 
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    class Config:
        case_sensitive = True
        env_file = ".env"
        env_file_encoding = "utf-8"
    
    @validator("CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v
    
    @validator("DATABASE_URL", pre=True)
    def assemble_db_connection(cls, v):
        if not v:
            return None
        if not v.startswith("postgres://"):
            return v
        # Convert postgres:// to postgresql:// for SQLAlchemy compatibility
        return "postgresql" + v[8:]
    
    # Feature flags
    ENABLE_ANALYTICS: bool = os.getenv("ENABLE_ANALYTICS", "False").lower() == "true"
    ENABLE_EMAIL_VERIFICATION: bool = os.getenv("ENABLE_EMAIL_VERIFICATION", "True").lower() == "true"
    
    # External services (if needed)
    MAPBOX_ACCESS_TOKEN: Optional[str] = os.getenv("MAPBOX_ACCESS_TOKEN")
    GOOGLE_ANALYTICS_ID: Optional[str] = os.getenv("GOOGLE_ANALYTICS_ID")
    
    # Validate database URL if provided
    @validator("DATABASE_URL", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: dict) -> Optional[str]:
        if isinstance(v, str):
            return v
        return None
    
    class Config:
        case_sensitive = True
        env_file = ".env"
        env_file_encoding = "utf-8"

# Create settings instance
settings = Settings()

# Export settings
__all__ = ["settings"]
