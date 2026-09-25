import logging
from datetime import datetime
from typing import List, Dict, Any
from app.config import settings

logger = logging.getLogger("sms_service")

# In-memory storage for mock SMS messages for local UI inspection & testing
MOCK_SMS_LOGS: List[Dict[str, Any]] = []

class SMSService:
    @staticmethod
    def send_sms(phone_number: str, message: str, notification_type: str = "general") -> bool:
        """
        Sends an SMS via Africa's Talking API or logs it in mock mode.
        """
        mode = settings.AT_SMS_MODE.lower()

        log_entry = {
            "id": str(len(MOCK_SMS_LOGS) + 1),
            "phone_number": phone_number,
            "message": message,
            "type": notification_type,
            "timestamp": datetime.utcnow().isoformat()
        }
        MOCK_SMS_LOGS.append(log_entry)

        logger.info(f"[{mode.upper()} SMS] To: {phone_number} | Type: {notification_type} | Message: {message}")

        if mode == "mock":
            return True

        if mode in ["sandbox", "live"]:
            try:
                import africastalking
                africastalking.initialize(
                    username=settings.AFRICASTALKING_USERNAME,
                    api_key=settings.AFRICASTALKING_API_KEY
                )
                sms = africastalking.SMS
                response = sms.send(
                    message=message,
                    recipients=[phone_number],
                    sender_id=settings.AFRICASTALKING_SENDER_ID if settings.AFRICASTALKING_SENDER_ID != "QLess" else None
                )
                logger.info(f"Africa's Talking SMS response: {response}")
                return True
            except Exception as e:
                logger.error(f"Failed to send SMS via Africa's Talking: {e}")
                return False

        return True

    @staticmethod
    def get_logs() -> List[Dict[str, Any]]:
        return MOCK_SMS_LOGS

    @staticmethod
    def clear_logs():
        global MOCK_SMS_LOGS
        MOCK_SMS_LOGS = []
