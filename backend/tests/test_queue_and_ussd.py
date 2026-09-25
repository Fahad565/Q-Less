import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import app.models  # Ensure all models are imported before metadata creation
from app.main import app
from app.db import Base, get_db
from app.models import TicketStatus, Ticket
from app.db_seed import seed_db
from app.services.sms_service import SMSService

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    seed_db(db)
    db.close()
    SMSService.clear_logs()
    yield
    Base.metadata.drop_all(bind=engine)

client = TestClient(app)

def test_health():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "healthy"

def test_ticket_creation_and_fifo():
    t1_res = client.post("/api/tickets", json={"customer_phone": "+254700000001", "service_id": 1})
    assert t1_res.status_code == 200
    t1_data = t1_res.json()
    assert t1_data["ticket_number"] == "C01"
    assert t1_data["position"] == 1
    assert t1_data["estimated_wait_minutes"] == 0

    t2_res = client.post("/api/tickets", json={"customer_phone": "+254700000002", "service_id": 1})
    assert t2_res.status_code == 200
    t2_data = t2_res.json()
    assert t2_data["ticket_number"] == "C02"
    assert t2_data["position"] == 2
    assert t2_data["estimated_wait_minutes"] == 5

    logs = client.get("/api/notifications/logs").json()
    # Find confirmation SMS for C01 and C02
    confirmations = [l for l in logs if l["type"] == "confirmation"]
    assert len(confirmations) >= 2
    assert "C01" in confirmations[0]["message"]
    assert "C02" in confirmations[1]["message"]

def test_duplicate_active_ticket_prevention():
    client.post("/api/tickets", json={"customer_phone": "+254700000001", "service_id": 1})
    res = client.post("/api/tickets", json={"customer_phone": "+254700000001", "service_id": 2})
    assert res.status_code == 400
    assert "already has an active ticket" in res.json()["detail"]

def test_ussd_flow():
    res = client.post("/api/ussd", data={"sessionId": "s1", "serviceCode": "*384#", "phoneNumber": "+254711111111", "text": ""})
    assert res.text.startswith("CON Welcome to Q-Less")

    res = client.post("/api/ussd", data={"sessionId": "s1", "serviceCode": "*384#", "phoneNumber": "+254711111111", "text": "1"})
    assert "CON Select Service:" in res.text
    assert "1. Customer Care" in res.text

    res = client.post("/api/ussd", data={"sessionId": "s1", "serviceCode": "*384#", "phoneNumber": "+254711111111", "text": "1*1"})
    assert "END Ticket Created!" in res.text
    assert "Ticket Number: C01" in res.text

    res = client.post("/api/ussd", data={"sessionId": "s2", "serviceCode": "*384#", "phoneNumber": "+254711111111", "text": "2"})
    assert "END Ticket C01 Status:" in res.text
    assert "WAITING" in res.text

def test_staff_call_next_and_counter_assignment():
    t1 = client.post("/api/tickets", json={"customer_phone": "+254700000001", "service_id": 1}).json()
    t2 = client.post("/api/tickets", json={"customer_phone": "+254700000002", "service_id": 1}).json()

    call_res = client.post("/api/queues/1/call-next?counter_id=1")
    assert call_res.status_code == 200
    called_t = call_res.json()
    assert called_t["id"] == t1["id"]
    assert called_t["status"] == "CALLED"
    assert called_t["counter_id"] == 1

    logs = client.get("/api/notifications/logs").json()
    counter_sms = [l for l in logs if l["type"] == "counter_assignment"]
    assert len(counter_sms) > 0
    assert "Counter 1" in counter_sms[0]["message"]

    comp_res = client.post(f"/api/tickets/{t1['id']}/complete")
    assert comp_res.status_code == 200
    assert comp_res.json()["status"] == "COMPLETED"
