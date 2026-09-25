import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, Enum, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.db import Base

class TicketStatus(str, enum.Enum):
    WAITING = "WAITING"
    CALLED = "CALLED"
    SERVING = "SERVING"
    COMPLETED = "COMPLETED"
    SKIPPED = "SKIPPED"
    CANCELLED = "CANCELLED"

class Queue(Base):
    __tablename__ = "queues"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    location = Column(String, nullable=False)

    services = relationship("Service", back_populates="queue", cascade="all, delete-orphan")
    counters = relationship("Counter", back_populates="queue", cascade="all, delete-orphan")
    tickets = relationship("Ticket", back_populates="queue", cascade="all, delete-orphan")

class Service(Base):
    __tablename__ = "services"

    id = Column(Integer, primary_key=True, index=True)
    queue_id = Column(Integer, ForeignKey("queues.id"), nullable=False)
    name = Column(String, nullable=False)
    code_prefix = Column(String, nullable=False, default="Q")
    avg_service_minutes = Column(Integer, nullable=False, default=5)

    queue = relationship("Queue", back_populates="services")
    tickets = relationship("Ticket", back_populates="service")

class Counter(Base):
    __tablename__ = "counters"

    id = Column(Integer, primary_key=True, index=True)
    queue_id = Column(Integer, ForeignKey("queues.id"), nullable=False)
    name = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)

    queue = relationship("Queue", back_populates="counters")
    tickets = relationship("Ticket", back_populates="counter")

class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)
    ticket_number = Column(String, index=True, nullable=False)
    customer_phone = Column(String, index=True, nullable=False)
    queue_id = Column(Integer, ForeignKey("queues.id"), nullable=False)
    service_id = Column(Integer, ForeignKey("services.id"), nullable=False)
    counter_id = Column(Integer, ForeignKey("counters.id"), nullable=True)
    status = Column(Enum(TicketStatus), default=TicketStatus.WAITING, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    called_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    approaching_notified_at = Column(DateTime, nullable=True)

    queue = relationship("Queue", back_populates="tickets")
    service = relationship("Service", back_populates="tickets")
    counter = relationship("Counter", back_populates="tickets")
    events = relationship("QueueEvent", back_populates="ticket", cascade="all, delete-orphan")

class QueueEvent(Base):
    __tablename__ = "queue_events"

    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, ForeignKey("tickets.id"), nullable=False)
    event_type = Column(String, nullable=False)
    description = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    ticket = relationship("Ticket", back_populates="events")
