from fastapi import APIRouter
from typing import List, Dict, Any
from app.services.sms_service import SMSService

router = APIRouter(prefix="/api/notifications", tags=["notifications"])

@router.get("/logs")
def get_sms_logs() -> List[Dict[str, Any]]:
    return SMSService.get_logs()

@router.post("/test")
def send_test_sms(phone_number: str, message: str):
    success = SMSService.send_sms(phone_number, message, notification_type="test")
    return {"success": success, "phone_number": phone_number, "message": message}

@router.delete("/logs")
def clear_sms_logs():
    SMSService.clear_logs()
    return {"message": "Logs cleared"}
