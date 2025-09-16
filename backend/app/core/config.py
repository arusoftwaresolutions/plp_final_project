from pydantic import AnyHttpUrl, EmailStr, PostgresDsn, validator, Field, BaseSettings
from typing import List, Optional, Union
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings(BaseSettings):
    # Project
    PROJECT_NAME: str = os.getenv("BACKEND_APP_NAME", "Poverty Alleviation Platform")
    VERSION: str = os.getenv("BACKEND_APP_VERSION", "1.0.0")
    DEBUG: bool = os.getenv("BACKEND_DEBUG", False)
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
    
    # Database
    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER", "db")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "postgres")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "poverty_alleviation")
    DATABASE_URL: Optional[PostgresDsn] = None
    
    @validator("DATABASE_URL", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: dict) -> str:
        if isinstance(v, str):
            return v.replace("postgresql://", "postgresql+asyncpg://")
        return f"postgresql+asyncpg://{values.get('POSTGRES_USER')}:{values.get('POSTGRES_PASSWORD')}@{values.get('POSTGRES_SERVER')}/{values.get('POSTGRES_DB')}"
    
    @property
    def SYNC_DATABASE_URL(self) -> str:
        """Return the sync database URL (for migrations)."""
        return self.DATABASE.replace("postgresql+asyncpg://", "postgresql://")
    
    @property
    def DATABASE(self) -> str:
        """Return the database URL."""
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
