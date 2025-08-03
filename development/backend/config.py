"""
Application Configuration
"""

import os
from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field, validator


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "Cash Flow Forecasting Tool"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")
    DEBUG: bool = Field(default=True, env="DEBUG")
    
    # Server
    HOST: str = Field(default="0.0.0.0", env="HOST")
    PORT: int = Field(default=8000, env="PORT")
    
    # Security
    SECRET_KEY: str = Field(env="SECRET_KEY")
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_EXPIRE_DAYS: int = 7
    
    # CORS
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:3001"],
        env="CORS_ORIGINS"
    )
    ALLOWED_HOSTS: List[str] = Field(
        default=["localhost", "127.0.0.1"],
        env="ALLOWED_HOSTS"
    )
    
    # Database
    DATABASE_URL: str = Field(env="DATABASE_URL")
    DATABASE_POOL_SIZE: int = Field(default=10, env="DATABASE_POOL_SIZE")
    DATABASE_MAX_OVERFLOW: int = Field(default=20, env="DATABASE_MAX_OVERFLOW")
    
    # Redis Cache
    REDIS_URL: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    CACHE_TTL: int = Field(default=3600, env="CACHE_TTL")  # 1 hour
    
    # Logging
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = Field(default=100, env="RATE_LIMIT_REQUESTS")
    RATE_LIMIT_WINDOW: int = Field(default=60, env="RATE_LIMIT_WINDOW")  # seconds
    
    # External APIs
    PLAID_CLIENT_ID: str = Field(default="", env="PLAID_CLIENT_ID")
    PLAID_SECRET: str = Field(default="", env="PLAID_SECRET")
    PLAID_ENVIRONMENT: str = Field(default="sandbox", env="PLAID_ENVIRONMENT")
    
    QUICKBOOKS_CLIENT_ID: str = Field(default="", env="QUICKBOOKS_CLIENT_ID")
    QUICKBOOKS_CLIENT_SECRET: str = Field(default="", env="QUICKBOOKS_CLIENT_SECRET")
    
    XERO_CLIENT_ID: str = Field(default="", env="XERO_CLIENT_ID")
    XERO_CLIENT_SECRET: str = Field(default="", env="XERO_CLIENT_SECRET")
    
    # Email
    SMTP_HOST: str = Field(default="", env="SMTP_HOST")
    SMTP_PORT: int = Field(default=587, env="SMTP_PORT")
    SMTP_USERNAME: str = Field(default="", env="SMTP_USERNAME")
    SMTP_PASSWORD: str = Field(default="", env="SMTP_PASSWORD")
    SMTP_TLS: bool = Field(default=True, env="SMTP_TLS")
    
    # File Storage
    STORAGE_TYPE: str = Field(default="local", env="STORAGE_TYPE")  # local, s3, gcs
    STORAGE_BUCKET: str = Field(default="", env="STORAGE_BUCKET")
    STORAGE_REGION: str = Field(default="us-east-1", env="STORAGE_REGION")
    
    # ML/AI
    ML_MODEL_PATH: str = Field(default="models/", env="ML_MODEL_PATH")
    ML_BATCH_SIZE: int = Field(default=32, env="ML_BATCH_SIZE")
    ML_TRAINING_DATA_DAYS: int = Field(default=365, env="ML_TRAINING_DATA_DAYS")
    
    # Monitoring
    SENTRY_DSN: str = Field(default="", env="SENTRY_DSN")
    DATADOG_API_KEY: str = Field(default="", env="DATADOG_API_KEY")
    
    @validator("CORS_ORIGINS", pre=True)
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    @validator("ALLOWED_HOSTS", pre=True)
    def parse_allowed_hosts(cls, v):
        if isinstance(v, str):
            return [host.strip() for host in v.split(",")]
        return v
    
    @validator("SECRET_KEY")
    def validate_secret_key(cls, v):
        if not v or len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters long")
        return v
    
    @validator("DATABASE_URL")
    def validate_database_url(cls, v):
        if not v:
            raise ValueError("DATABASE_URL is required")
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()

# Feature flags
FEATURES = {
    "ai_forecasting": True,
    "real_time_sync": True,
    "multi_currency": True,
    "advanced_scenarios": True,
    "integrations": True,
    "mobile_app": True,
    "api_access": True,
    "custom_reports": True,
    "audit_logging": True,
    "sso_integration": False,  # Enterprise feature
    "white_labeling": False,   # Enterprise feature
}
