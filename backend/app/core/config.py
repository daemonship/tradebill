from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    # Application
    APP_NAME: str = "Tradebill API"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str = "postgresql://tradebill:tradebill_dev@localhost:5432/tradebill"

    # Security
    JWT_SECRET: str = "dev-secret-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # External APIs
    RESEND_API_KEY: Optional[str] = None
    R2_ENDPOINT_URL: Optional[str] = None
    R2_ACCESS_KEY_ID: Optional[str] = None
    R2_SECRET_ACCESS_KEY: Optional[str] = None
    R2_BUCKET_NAME: Optional[str] = None

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
