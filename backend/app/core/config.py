"""Application Configuration"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )
    
    # Database
    DATABASE_URL: str
    TEST_DATABASE_URL: str | None = None
    
    # Redis
    REDIS_URL: str
    
    # JWT
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Razorpay
    RAZORPAY_KEY_ID: str
    RAZORPAY_KEY_SECRET: str
    RAZORPAY_WEBHOOK_SECRET: str
    
    # SMS Provider
    SMS_PROVIDER: str = "twilio"
    TWILIO_ACCOUNT_SID: str | None = None
    TWILIO_AUTH_TOKEN: str | None = None
    TWILIO_PHONE_NUMBER: str | None = None
    
    # Email Provider
    EMAIL_PROVIDER: str = "sendgrid"
    SENDGRID_API_KEY: str | None = None
    SENDGRID_FROM_EMAIL: str | None = None
    
    # Google OAuth
    GOOGLE_OAUTH_CLIENT_ID: str | None = None
    GOOGLE_OAUTH_CLIENT_SECRET: str | None = None
    GOOGLE_OAUTH_OWNER_EMAILS: str | None = None  # Comma-separated list of owner emails
    
    # S3 Storage
    S3_BUCKET_NAME: str
    S3_ACCESS_KEY: str
    S3_SECRET_KEY: str
    S3_REGION: str = "us-east-1"
    S3_ENDPOINT_URL: str | None = None
    CDN_BASE_URL: str | None = None
    
    # Application
    FRONTEND_URL: str = "http://localhost:5173"
    BACKEND_URL: str = "http://localhost:8000"
    ENVIRONMENT: str = "development"
    
    # Monitoring
    SENTRY_DSN: str | None = None
    SENTRY_TRACES_SAMPLE_RATE: float = 0.1
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str | None = None
    
    # Rate Limiting
    RATE_LIMIT_AUTH_ATTEMPTS: int = 5
    RATE_LIMIT_AUTH_WINDOW_MINUTES: int = 15


settings = Settings()
