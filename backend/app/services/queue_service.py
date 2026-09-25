from datetime import datetime
from typing import Tuple, Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models import Queue, Service, Ticket, Counter, QueueEvent, TicketStatus
from app.services.sms_service import SMSService
from app.config import settings

class QueueService:
    @staticmethod
    def get_active_ticket_for_phone(db: Session, phone_number: str) -> Optional[Ticket]:
        return db.query(Ticket).filter(
            Ticket.customer_phone == phone_number,
            Ticket.status.in_([TicketStatus.WAITING, TicketStatus.CALLED, TicketStatus.SERVING])
        ).first()

    @staticmethod
    def calculate_position_and_wait(db: Session, ticket: Ticket) -> Tuple[int, int]:
        if ticket.status != TicketStatus.WAITING:
            return 0, 0

        # Number of WAITING tickets ahead of this ticket in the same queue
        ahead_count = db.query(func.count(Ticket.id)).filter(
            Ticket.queue_id == ticket.queue_id,
            Ticket.status == TicketStatus.WAITING,
            Ticket.id < ticket.id
        ).scalar() or 0

        position = ahead_count + 1
        service = db.query(Service).filter(Service.id == ticket.service_id).first()
        avg_minutes = service.avg_service_minutes if service else 5

        # Estimated wait = people ahead * avg service time
        estimated_wait = ahead_count * avg_minutes
        return position, estimated_wait

    @staticmethod
    def create_ticket(db: Session, customer_phone: str, service_id: int) -> Ticket:
        # Prevent duplicate active tickets
        existing = QueueService.get_active_ticket_for_phone(db, customer_phone)
        if existing:
            raise ValueError(f"Customer already has an active ticket: {existing.ticket_number}")

        service = db.query(Service).filter(Service.id == service_id).first()
        if not service:
            raise ValueError(f"Service with ID {service_id} not found")

        # Generate ticket number (e.g., C101, A102)
        total_tickets_today = db.query(func.count(Ticket.id)).filter(
            Ticket.service_id == service_id
        ).scalar() or 0

        prefix = service.code_prefix or "Q"
        ticket_number = f"{prefix}{total_tickets_today + 1:02d}"

        ticket = Ticket(
            ticket_number=ticket_number,
            customer_phone=customer_phone,
            queue_id=service.queue_id,
            service_id=service.id,
            status=TicketStatus.WAITING,
            created_at=datetime.utcnow()
        )
        db.add(ticket)
        db.commit()
        db.refresh(ticket)

        # Log event
        event = QueueEvent(
            ticket_id=ticket.id,
            event_type="CREATED",
            description=f"Ticket {ticket.ticket_number} created for service {service.name}"
        )
        db.add(event)
        db.commit()

        # Calculate position & wait
        position, est_wait = QueueService.calculate_position_and_wait(db, ticket)

        # Trigger SMS confirmation
        sms_msg = (
            f"Q-Less: You are ticket {ticket.ticket_number}.\n"
            f"There are {position - 1} customers ahead of you.\n"
            f"Estimated wait: ~{est_wait} minutes."
        )
        SMSService.send_sms(customer_phone, sms_msg, notification_type="confirmation")

        # Check approaching threshold immediately if position is small
        QueueService.check_and_notify_approaching_tickets(db, ticket.queue_id)

        return ticket

    @staticmethod
    def check_and_notify_approaching_tickets(db: Session, queue_id: int):
        waiting_tickets = db.query(Ticket).filter(
            Ticket.queue_id == queue_id,
            Ticket.status == TicketStatus.WAITING
        ).order_by(Ticket.id.asc()).all()

        for idx, t in enumerate(waiting_tickets):
            pos = idx + 1
            if pos <= settings.APPROACHING_THRESHOLD and t.approaching_notified_at is None:
                sms_msg = (
                    f"Q-Less: Your turn is approaching for ticket {t.ticket_number}! "
                    f"You are number {pos} in line. Please head to the service area."
                )
                SMSService.send_sms(t.customer_phone, sms_msg, notification_type="approaching")
                t.approaching_notified_at = datetime.utcnow()
                db.commit()

    @staticmethod
    def call_next(db: Session, queue_id: int, counter_id: Optional[int] = None) -> Optional[Ticket]:
        # Next ticket in WAITING state for this queue
        next_ticket = db.query(Ticket).filter(
            Ticket.queue_id == queue_id,
            Ticket.status == TicketStatus.WAITING
        ).order_by(Ticket.id.asc()).first()

        if not next_ticket:
            return None

        next_ticket.status = TicketStatus.CALLED
        next_ticket.called_at = datetime.utcnow()
        if counter_id:
            next_ticket.counter_id = counter_id

        db.commit()
        db.refresh(next_ticket)

        counter = db.query(Counter).filter(Counter.id == counter_id).first() if counter_id else None
        counter_name = counter.name if counter else "assigned counter"

        # Event
        event = QueueEvent(
            ticket_id=next_ticket.id,
            event_type="CALLED",
            description=f"Ticket {next_ticket.ticket_number} called to {counter_name}"
        )
        db.add(event)
        db.commit()

        # Send SMS notification
        sms_msg = f"Q-Less: Ticket {next_ticket.ticket_number}, please proceed to {counter_name}."
        SMSService.send_sms(next_ticket.customer_phone, sms_msg, notification_type="counter_assignment")

        # Notify remaining approaching tickets
        QueueService.check_and_notify_approaching_tickets(db, queue_id)

        return next_ticket

    @staticmethod
    def assign_counter(db: Session, ticket_id: int, counter_id: int) -> Ticket:
        ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
        if not ticket:
            raise ValueError(f"Ticket {ticket_id} not found")

        ticket.counter_id = counter_id
        db.commit()
        db.refresh(ticket)

        counter = db.query(Counter).filter(Counter.id == counter_id).first()
        counter_name = counter.name if counter else f"Counter {counter_id}"

        event = QueueEvent(
            ticket_id=ticket.id,
            event_type="COUNTER_ASSIGNED",
            description=f"Assigned to {counter_name}"
        )
        db.add(event)
        db.commit()

        if ticket.status in [TicketStatus.CALLED, TicketStatus.SERVING]:
            sms_msg = f"Q-Less: Ticket {ticket.ticket_number}, please proceed to {counter_name}."
            SMSService.send_sms(ticket.customer_phone, sms_msg, notification_type="counter_assignment")

        return ticket

    @staticmethod
    def update_status(db: Session, ticket_id: int, new_status: TicketStatus) -> Ticket:
        ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
        if not ticket:
            raise ValueError(f"Ticket {ticket_id} not found")

        old_status = ticket.status
        ticket.status = new_status
        if new_status == TicketStatus.COMPLETED:
            ticket.completed_at = datetime.utcnow()

        db.commit()
        db.refresh(ticket)

        event = QueueEvent(
            ticket_id=ticket.id,
            event_type=new_status.value,
            description=f"Status changed from {old_status.value} to {new_status.value}"
        )
        db.add(event)
        db.commit()

        # Re-evaluate approaching notifications for remaining waiting tickets
        if old_status in [TicketStatus.WAITING, TicketStatus.CALLED, TicketStatus.SERVING]:
            QueueService.check_and_notify_approaching_tickets(db, ticket.queue_id)

        return ticket
