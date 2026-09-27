import pytest
from unittest.mock import patch, MagicMock
from app.config import settings
from app.utils import normalize_phone_number
from app.services.sms_service import SMSService, MockSMSProvider, AfricasTalkingLiveSMSProvider

def test_normalize_phone_number():
    assert normalize_phone_number("0712345678") == "+254712345678"
    assert normalize_phone_number("0112345678") == "+254112345678"
    assert normalize_phone_number("254712345678") == "+254712345678"
    assert normalize_phone_number("+254712345678") == "+254712345678"
    assert normalize_phone_number("  0712 345-678  ") == "+254712345678"

def test_mock_sms_mode(monkeypatch):
    monkeypatch.setattr(settings, "AT_SMS_MODE", "mock")
    SMSService.clear_logs()

    res = SMSService.send_sms("0712345678", "Test Mock SMS", notification_type="test")
    assert res.success is True
    assert res.provider == "Mock Provider"
    assert res.recipient == "+254712345678"

    logs = SMSService.get_logs()
    assert len(logs) == 1
    assert logs[0]["provider"] == "Mock Provider"
    assert logs[0]["phone_number"] == "+254712345678"

def test_live_sms_missing_credentials(monkeypatch):
    monkeypatch.setattr(settings, "AT_SMS_MODE", "live")
    monkeypatch.setattr(settings, "AFRICASTALKING_USERNAME", None)
    monkeypatch.setattr(settings, "AFRICASTALKING_API_KEY", None)

    res = SMSService.send_sms("0712345678", "Test Live SMS")
    assert res.success is False
    assert res.provider == "Africa's Talking Live"
    assert "Missing Africa's Talking Live credentials" in res.error

def test_live_sms_rejects_sandbox_username(monkeypatch):
    monkeypatch.setattr(settings, "AT_SMS_MODE", "live")
    monkeypatch.setattr(settings, "AFRICASTALKING_USERNAME", "sandbox")
    monkeypatch.setattr(settings, "AFRICASTALKING_API_KEY", "some_key")

    res = SMSService.send_sms("0712345678", "Test Live SMS")
    assert res.success is False
    assert "Live Africa's Talking username" in res.error

@patch("africastalking.SMS")
@patch("africastalking.initialize")
def test_live_sms_with_sender_id(mock_init, mock_sms, monkeypatch):
    monkeypatch.setattr(settings, "AT_SMS_MODE", "live")
    monkeypatch.setattr(settings, "AFRICASTALKING_USERNAME", "live_user")
    monkeypatch.setattr(settings, "AFRICASTALKING_API_KEY", "live_api_key")
    monkeypatch.setattr(settings, "AFRICASTALKING_SENDER_ID", "MYBRAND")

    mock_sms.send.return_value = {
        "SMSMessageData": {
            "Message": "Sent to 1/1 Total Cost: KES 0.8000",
            "Recipients": [
                {
                    "cost": "KES 0.8000",
                    "messageId": "ATXid_12345",
                    "number": "+254712345678",
                    "status": "Success",
                    "statusCode": 101
                }
            ]
        }
    }

    res = AfricasTalkingLiveSMSProvider.send("+254712345678", "Hello Live")
    assert res.success is True
    assert res.provider == "Africa's Talking Live"
    assert res.provider_message_id == "ATXid_12345"
    assert res.status == "Success"
    assert res.cost == "KES 0.8000"

    mock_sms.send.assert_called_once_with(
        message="Hello Live",
        recipients=["+254712345678"],
        sender_id="MYBRAND"
    )

@patch("africastalking.SMS")
@patch("africastalking.initialize")
def test_live_sms_without_sender_id_omitted(mock_init, mock_sms, monkeypatch):
    monkeypatch.setattr(settings, "AT_SMS_MODE", "live")
    monkeypatch.setattr(settings, "AFRICASTALKING_USERNAME", "live_user")
    monkeypatch.setattr(settings, "AFRICASTALKING_API_KEY", "live_api_key")
    monkeypatch.setattr(settings, "AFRICASTALKING_SENDER_ID", None)

    mock_sms.send.return_value = {
        "SMSMessageData": {
            "Recipients": [
                {
                    "cost": "KES 0.8000",
                    "messageId": "ATXid_67890",
                    "number": "+254712345678",
                    "status": "Success",
                    "statusCode": 101
                }
            ]
        }
    }

    res = AfricasTalkingLiveSMSProvider.send("+254712345678", "Hello Live No Sender")
    assert res.success is True
    mock_sms.send.assert_called_once_with(
        message="Hello Live No Sender",
        recipients=["+254712345678"]
    )

@patch("africastalking.SMS")
@patch("africastalking.initialize")
def test_live_sms_provider_error_handling(mock_init, mock_sms, monkeypatch):
    monkeypatch.setattr(settings, "AT_SMS_MODE", "live")
    monkeypatch.setattr(settings, "AFRICASTALKING_USERNAME", "live_user")
    monkeypatch.setattr(settings, "AFRICASTALKING_API_KEY", "live_api_key")
    monkeypatch.setattr(settings, "AFRICASTALKING_SENDER_ID", None)

    mock_sms.send.side_effect = Exception("Invalid SenderId or insufficient balance")

    res = AfricasTalkingLiveSMSProvider.send("+254712345678", "Hello Fail")
    assert res.success is False
    assert "Invalid SenderId or insufficient balance" in res.error
