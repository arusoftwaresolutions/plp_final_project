from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    database_url: str = "postgresql://postgres:postgres@localhost:5432/financial_platform"
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # AI Model settings
    ai_model_path: str = "models/budgeting_model.pkl"
    
    # Payment settings
    stripe_public_key: Optional[str] = None
    stripe_secret_key: Optional[str] = None
    
    class Config:
        env_file = ".env"

settings = Settings()
