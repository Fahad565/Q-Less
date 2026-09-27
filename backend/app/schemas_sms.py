from typing import Optional
from pydantic import BaseModel, ConfigDict

class SMSResult(BaseModel):
    model_config = ConfigDict(extra="ignore")

    success: bool
    recipient: str
    provider: str
    provider_message_id: Optional[str] = None
    status: Optional[str] = None
    status_code: Optional[str] = None
    cost: Optional[str] = None
    error: Optional[str] = None

class TestSMSRequest(BaseModel):
    phone_number: str
    message: str
