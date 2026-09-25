from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.models import TicketStatus

class ServiceBase(BaseModel):
    name: str
    code_prefix: str = "Q"
    avg_service_minutes: int = 5

class ServiceResponse(ServiceBase):
    id: int
    queue_id: int

    class Config:
        from_attributes = True

class CounterBase(BaseModel):
    name: str
    is_active: bool = True

class CounterResponse(CounterBase):
    id: int
    queue_id: int

    class Config:
        from_attributes = True

class QueueBase(BaseModel):
    name: str
    location: str

class QueueResponse(QueueBase):
    id: int
    services: List[ServiceResponse] = []
    counters: List[CounterResponse] = []

    class Config:
        from_attributes = True

class TicketCreate(BaseModel):
    customer_phone: str
    service_id: int

class TicketResponse(BaseModel):
    id: int
    ticket_number: str
    customer_phone: str
    queue_id: int
    service_id: int
    counter_id: Optional[int] = None
    status: TicketStatus
    created_at: datetime
    called_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    position: Optional[int] = None
    estimated_wait_minutes: Optional[int] = None
    service_name: Optional[str] = None
    counter_name: Optional[str] = None

    class Config:
        from_attributes = True

class AssignCounterRequest(BaseModel):
    counter_id: int

class SMSLogResponse(BaseModel):
    id: str
    phone_number: str
    message: str
    type: str
    timestamp: datetime
