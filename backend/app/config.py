import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "Q-Less Queue API"
    APP_ENV: str = "development"
    DATABASE_URL: str = "sqlite:///./qless.db"
    AT_SMS_MODE: str = "mock"  # mock, sandbox, live
    AFRICASTALKING_USERNAME: str = "sandbox"
    AFRICASTALKING_API_KEY: str = "mock_key"
    AFRICASTALKING_SENDER_ID: str = "QLess"
    APPROACHING_THRESHOLD: int = 2
    CORS_ORIGINS: str = "*"

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
