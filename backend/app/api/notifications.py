from fastapi import APIRouter
from typing import List, Dict, Any
from app.services.sms_service import SMSService
from app.schemas_sms import TestSMSRequest, SMSResult

router = APIRouter(prefix="/api/notifications", tags=["notifications"])

@router.get("/logs")
def get_sms_logs() -> List[Dict[str, Any]]:
    return SMSService.get_logs()

@router.post("/test", response_model=SMSResult)
def send_test_sms(payload: TestSMSRequest) -> SMSResult:
    result = SMSService.send_sms(
        phone_number=payload.phone_number,
        message=payload.message,
        notification_type="test"
    )
    return result

@router.delete("/logs")
def clear_sms_logs():
    SMSService.clear_logs()
    return {"message": "Logs cleared"}
