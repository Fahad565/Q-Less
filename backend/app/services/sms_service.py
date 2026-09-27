import logging
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from app.config import settings
from app.utils import normalize_phone_number
from app.schemas_sms import SMSResult

logger = logging.getLogger("sms_service")

# In-memory storage for SMS logs for dashboard inspection & testing
SMS_LOGS: List[Dict[str, Any]] = []

class MockSMSProvider:
    @staticmethod
    def send(recipient: str, message: str) -> SMSResult:
        return SMSResult(
            success=True,
            recipient=recipient,
            provider="Mock Provider",
            provider_message_id=f"MOCK-{len(SMS_LOGS) + 1}",
            status="Success",
            status_code="100",
            cost="KSH 0.00",
            error=None
        )

class AfricasTalkingLiveSMSProvider:
    @staticmethod
    def send(recipient: str, message: str) -> SMSResult:
        username = settings.AFRICASTALKING_USERNAME
        api_key = settings.AFRICASTALKING_API_KEY
        sender_id = settings.AFRICASTALKING_SENDER_ID

        if not username or not api_key:
            err_msg = "Missing Africa's Talking Live credentials (AFRICASTALKING_USERNAME or AFRICASTALKING_API_KEY)"
            logger.error(err_msg)
            return SMSResult(
                success=False,
                recipient=recipient,
                provider="Africa's Talking Live",
                error=err_msg
            )

        if username.lower() == "sandbox":
            err_msg = "Live SMS mode requires a Live Africa's Talking username, not 'sandbox'"
            logger.error(err_msg)
            return SMSResult(
                success=False,
                recipient=recipient,
                provider="Africa's Talking Live",
                error=err_msg
            )

        try:
            import africastalking
            africastalking.initialize(username=username, api_key=api_key)
            sms = africastalking.SMS

            send_kwargs = {
                "message": message,
                "recipients": [recipient]
            }
            if sender_id:
                send_kwargs["sender_id"] = sender_id

            logger.info(f"[AT LIVE SMS] Sending SMS to {recipient} with sender_id={sender_id or 'None (omitted)'}")
            response = sms.send(**send_kwargs)
            logger.info(f"[AT LIVE SMS] Raw Response: {response}")

            # Parse Africa's Talking SMS response structure
            # Example response:
            # {'SMSMessageData': {'Message': 'Sent to 1/1 Total Cost: KES 0.8000', 'Recipients': [{'cost': 'KES 0.8000', 'messageId': 'ATXid_...', 'number': '+254712345678', 'status': 'Success', 'statusCode': 101}]}}
            sms_data = response.get("SMSMessageData", {}) if isinstance(response, dict) else {}
            recipients = sms_data.get("Recipients", [])

            if recipients and isinstance(recipients, list) and len(recipients) > 0:
                rec_info = recipients[0]
                status_code = str(rec_info.get("statusCode", ""))
                status = str(rec_info.get("status", ""))
                msg_id = rec_info.get("messageId")
                cost = rec_info.get("cost")

                # Africa's Talking status code 101 indicates 'Success' (Processed/Sent)
                is_success = status.lower() in ["success", "sent"] or status_code in ["101", "100"]

                return SMSResult(
                    success=is_success,
                    recipient=recipient,
                    provider="Africa's Talking Live",
                    provider_message_id=msg_id,
                    status=status or "Submitted",
                    status_code=status_code,
                    cost=cost,
                    error=None if is_success else f"Provider status: {status} (Code {status_code})"
                )

            # Fallback if Recipients array is missing or empty
            err_detail = sms_data.get("Message", str(response))
            return SMSResult(
                success=False,
                recipient=recipient,
                provider="Africa's Talking Live",
                error=f"No recipient summary in response: {err_detail}"
            )

        except Exception as e:
            err_str = str(e)
            logger.error(f"[AT LIVE SMS] Exception while sending SMS: {err_str}")
            return SMSResult(
                success=False,
                recipient=recipient,
                provider="Africa's Talking Live",
                error=f"Africa's Talking API Error: {err_str}"
            )

class SMSService:
    @staticmethod
    def send_sms(phone_number: str, message: str, notification_type: str = "general") -> SMSResult:
        """
        Sends an SMS via Mock Provider or Africa's Talking Live Provider.
        Normalizes recipient phone number and records logs with provider metadata.
        """
        mode = settings.AT_SMS_MODE.lower()
        normalized_recipient = normalize_phone_number(phone_number)

        if mode == "mock":
            result = MockSMSProvider.send(normalized_recipient, message)
        elif mode == "live":
            result = AfricasTalkingLiveSMSProvider.send(normalized_recipient, message)
        else:
            result = SMSResult(
                success=False,
                recipient=normalized_recipient,
                provider="Unknown",
                error=f"Unsupported AT_SMS_MODE: {mode}"
            )

        log_entry = {
            "id": str(len(SMS_LOGS) + 1),
            "phone_number": normalized_recipient,
            "message": message,
            "type": notification_type,
            "provider": result.provider,
            "status": result.status or ("Success" if result.success else "Failed"),
            "provider_message_id": result.provider_message_id,
            "cost": result.cost,
            "error": result.error,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        SMS_LOGS.append(log_entry)

        logger.info(
            f"[{result.provider.upper()}] To: {normalized_recipient} | "
            f"Success: {result.success} | Type: {notification_type} | Message: {message}"
        )

        return result

    @staticmethod
    def get_logs() -> List[Dict[str, Any]]:
        return SMS_LOGS

    @staticmethod
    def clear_logs():
        global SMS_LOGS
        SMS_LOGS = []
