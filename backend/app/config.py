from typing import Optional
from pydantic import field_validator, ConfigDict
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    model_config = ConfigDict(env_file=".env", extra="ignore")

    APP_NAME: str = "Q-Less Queue API"
    APP_ENV: str = "development"
    DATABASE_URL: str = "sqlite:///./qless.db"
    AT_SMS_MODE: str = "mock"  # mock or live
    AFRICASTALKING_USERNAME: Optional[str] = None
    AFRICASTALKING_API_KEY: Optional[str] = None
    AFRICASTALKING_SENDER_ID: Optional[str] = None
    APPROACHING_THRESHOLD: int = 2
    CORS_ORIGINS: str = "*"

    @field_validator("AT_SMS_MODE")
    @classmethod
    def validate_sms_mode(cls, v: str) -> str:
        v_lower = v.lower().strip() if v else "mock"
        if v_lower not in ["mock", "live"]:
            raise ValueError("AT_SMS_MODE must be either 'mock' or 'live'")
        return v_lower

    @field_validator("AFRICASTALKING_SENDER_ID")
    @classmethod
    def clean_sender_id(cls, v: Optional[str]) -> Optional[str]:
        if v is None or not v.strip():
            return None
        return v.strip()

settings = Settings()
